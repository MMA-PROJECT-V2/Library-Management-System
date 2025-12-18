from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# ============================================
#    CUSTOM USER MANAGER
# ============================================

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with email."""
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


# ============================================
#    USER MODEL
# ============================================

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with roles and group-based permissions.
    Uses email as the primary identifier instead of username.
    """
    
    ROLE_CHOICES = [
        ('MEMBER', 'Member'),
        ('LIBRARIAN', 'Librarian'),
        ('ADMIN', 'Admin'),
    ]
    
    # Core fields
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(max_length=150, unique=True, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Additional fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBER')
    max_loans = models.IntegerField(default=5)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # Required for PermissionsMixin
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Link to custom groups
    custom_groups = models.ManyToManyField(
        'Group',
        related_name='users',
        blank=True
    )
    
    # Direct permissions (in addition to group permissions)
    direct_permissions = models.ManyToManyField(
        'Permission',
        related_name='users_direct',
        blank=True,
        help_text="Permissions assigned directly to this user"
    )
    
    # Use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No additional required fields for createsuperuser
    
    objects = CustomUserManager()
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
    
    def save(self, *args, **kwargs):
        """Auto-generate username from email if not provided."""
        if not self.username:
            self.username = self.email.split('@')[0]
            # Handle duplicates by appending a number
            base_username = self.username
            counter = 1
            while User.objects.filter(username=self.username).exclude(pk=self.pk).exists():
                self.username = f"{base_username}{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    # ========== Permission Methods ==========
    
    def get_all_permissions(self):
        """
        Get all permission codes for this user.
        Combines: group permissions + direct permissions
        """
        # Admin has ALL permissions
        if self.role == 'ADMIN' or self.is_superuser:
            return list(Permission.objects.values_list('code', flat=True))
        
        # Get permissions from all groups
        group_permissions = Permission.objects.filter(
            groups__users=self
        ).values_list('code', flat=True)
        
        # Get direct permissions
        direct_permissions = self.direct_permissions.values_list('code', flat=True)
        
        # Combine and remove duplicates
        all_permissions = set(group_permissions) | set(direct_permissions)
        
        return list(all_permissions)
    
    def get_all_permissions_list(self):
        """Alias for get_all_permissions() for consistency."""
        return self.get_all_permissions()
    
    def has_permission(self, permission_code):
        """Check if user has a specific permission."""
        if self.role == 'ADMIN' or self.is_superuser:
            return True
        return permission_code in self.get_all_permissions()
    
    def has_any_permission(self, permission_codes):
        """Check if user has ANY of the given permissions."""
        if self.role == 'ADMIN' or self.is_superuser:
            return True
        user_permissions = set(self.get_all_permissions())
        return bool(user_permissions & set(permission_codes))
    
    def has_all_permissions(self, permission_codes):
        """Check if user has ALL of the given permissions."""
        if self.role == 'ADMIN' or self.is_superuser:
            return True
        user_permissions = set(self.get_all_permissions())
        return set(permission_codes).issubset(user_permissions)
    
    def get_groups(self):
        """Get all groups this user belongs to."""
        return self.custom_groups.all()
    
    # ========== Role Methods ==========
    
    def is_member(self):
        return self.role == 'MEMBER'
    
    def is_librarian(self):
        return self.role == 'LIBRARIAN'
    
    def is_admin_user(self):
        return self.role == 'ADMIN'
    
    def can_borrow(self):
        return self.is_active and self.has_permission('can_borrow_book')


# ============================================
#    USER PROFILE MODEL
# ============================================

class UserProfile(models.Model):
    """Extended profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    avatar_url = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "user_profiles"

    def __str__(self):
        return f"Profile of {self.user.email}"


# ============================================
#    PERMISSION MODEL
# ============================================

class Permission(models.Model):
    """Custom permissions for the library system."""
    
    CATEGORY_CHOICES = [
        ('BOOKS', 'Book Management'),
        ('LOANS', 'Loan Management'),
        ('USERS', 'User Management'),
        ('REPORTS', 'Reports & Analytics'),
        ('SYSTEM', 'System Settings'),
    ]
    
    code = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Unique code like 'can_add_book'"
    )
    name = models.CharField(
        max_length=100,
        help_text="Human readable name like 'Can Add Book'"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of what this permission allows"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='SYSTEM'
    )
    
    class Meta:
        db_table = 'permissions'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


# ============================================
#    GROUP MODEL
# ============================================

class Group(models.Model):
    """Groups are collections of permissions."""
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(
        Permission,
        related_name='groups',
        blank=True
    )
    is_default = models.BooleanField(
        default=False,
        help_text="If true, new users are automatically added to this group"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'groups'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_permission_codes(self):
        """Return list of permission codes for this group"""
        return list(self.permissions.values_list('code', flat=True))