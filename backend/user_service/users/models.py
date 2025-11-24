from django.db import models
from django.contrib.auth.models import AbstractBaseUser , PermissionsMixin , BaseUserManager

# Create your models here.

# ============================================
#    CUSTOM USER MANAGER
# ============================================

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(email, username, password, **extra_fields)


# ============================================
#    USER MODEL
# ============================================

class User(AbstractBaseUser , ):
    """
    Custom User model with roles and group-based permissions.
    """
    
    ROLE_CHOICES = [
        ('MEMBER', 'Member'),
        ('LIBRARIAN', 'Librarian'),
        ('ADMIN', 'Admin'),
    ]
    
    # Override email to make it unique and required
    email = models.EmailField(unique=True, max_length=255)
    
    # Additional fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBER')
    max_loans = models.IntegerField(default=5)
    
    # Link to custom groups (not Django's built-in groups)
    # Using string reference for forward declaration
    custom_groups = models.ManyToManyField(
        'Group',
        related_name='users',
        blank=True
    )
    
    # Direct permissions (in addition to group permissions)
    # Using string reference for forward declaration
    direct_permissions = models.ManyToManyField(
        'Permission',
        related_name='users_direct',
        blank=True,
        help_text="Permissions assigned directly to this user"
    )
    
    # Use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    objects = CustomUserManager()
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    # ========== Permission Methods ==========
    
    def get_all_permissions(self):
        """
        Get all permission codes for this user.
        Combines: group permissions + direct permissions
        """
        # Permission is defined later in this file, but accessible at runtime
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
        """
        Check if user has a specific permission.
        """
        # Admin has all permissions
        if self.role == 'ADMIN' or self.is_superuser:
            return True
        
        return permission_code in self.get_all_permissions()
    
    def has_any_permission(self, permission_codes):
        """
        Check if user has ANY of the given permissions.
        """
        if self.role == 'ADMIN' or self.is_superuser:
            return True
        
        user_permissions = set(self.get_all_permissions())
        return bool(user_permissions & set(permission_codes))
    
    def has_all_permissions(self, permission_codes):
        """
        Check if user has ALL of the given permissions.
        """
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
        return f"Profile of {self.user.username}"
    

# ============================================
#    PERMISSION MODEL
# ============================================

class Permission(models.Model):
    """
    Custom permissions for the library system.
    Each permission represents a specific action a user can perform.
    """
    
    # Permission categories
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
    """
    Groups are collections of permissions.
    Users belong to groups and inherit all permissions from their groups.
    """
    
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
