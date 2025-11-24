"""
Comprehensive tests for User, UserProfile, Permission, and Group models.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from users.models import UserProfile, Permission, Group

User = get_user_model()


# ============================================
#    USER MODEL TESTS
# ============================================

@pytest.mark.django_db
class TestUserModel:
    """Test User model functionality."""
    
    def test_create_user(self):
        """Test creating a basic user."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        assert user.email == 'test@example.com'
        assert user.username == 'testuser'
        assert user.check_password('testpass123')
        assert user.role == 'MEMBER'  # Default role
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.role == 'ADMIN'
    
    def test_user_email_unique(self):
        """Test email must be unique."""
        User.objects.create_user(
            email='duplicate@example.com',
            username='user1',
            password='pass123',
            first_name='User',
            last_name='One'
        )
        
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email='duplicate@example.com',
                username='user2',
                password='pass123',
                first_name='User',
                last_name='Two'
            )
    
    def test_user_str_representation(self, member_user):
        """Test user string representation."""
        assert str(member_user) == f"{member_user.username} (Member)"
    
    def test_user_role_choices(self):
        """Test user role choices."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='pass123',
            first_name='Test',
            last_name='User',
            role='LIBRARIAN'
        )
        
        assert user.role == 'LIBRARIAN'
        assert user.get_role_display() == 'Librarian'
    
    def test_is_member(self, member_user):
        """Test is_member method."""
        assert member_user.is_member() is True
        assert member_user.is_librarian() is False
        assert member_user.is_admin_user() is False
    
    def test_is_librarian(self, librarian_user):
        """Test is_librarian method."""
        assert librarian_user.is_librarian() is True
        assert librarian_user.is_member() is False
        assert librarian_user.is_admin_user() is False
    
    def test_is_admin_user(self, admin_user):
        """Test is_admin_user method."""
        assert admin_user.is_admin_user() is True
        assert admin_user.is_member() is False
        assert admin_user.is_librarian() is False
    
    def test_can_borrow(self, member_user, permissions):
        """Test can_borrow method."""
        # User should have can_borrow_book permission from member_group
        assert member_user.can_borrow() is True
        
        # Deactivate user
        member_user.is_active = False
        member_user.save()
        assert member_user.can_borrow() is False


# ============================================
#    USER PERMISSIONS TESTS
# ============================================

@pytest.mark.django_db
class TestUserPermissions:
    """Test user permission methods."""
    
    def test_get_all_permissions_from_group(self, member_user, member_group, permissions):
        """Test user gets permissions from group."""
        perms = member_user.get_all_permissions()
        
        assert 'can_view_books' in perms
        assert 'can_borrow_book' in perms
        assert 'can_return_book' in perms
        assert 'can_view_loans' in perms
    
    def test_get_all_permissions_list(self, member_user, member_group):
        """Test get_all_permissions_list method."""
        perms = member_user.get_all_permissions_list()
        
        assert isinstance(perms, list)
        assert len(perms) > 0
    
    def test_has_permission(self, member_user, member_group):
        """Test has_permission method."""
        assert member_user.has_permission('can_view_books') is True
        assert member_user.has_permission('can_borrow_book') is True
        assert member_user.has_permission('can_add_book') is False  # Not in member group
    
    def test_admin_has_all_permissions(self, admin_user, permissions):
        """Test admin has all permissions."""
        # Admin should have all permissions
        all_perms = Permission.objects.values_list('code', flat=True)
        
        for perm_code in all_perms:
            assert admin_user.has_permission(perm_code) is True
    
    def test_has_any_permission(self, member_user, member_group):
        """Test has_any_permission method."""
        # User has can_view_books but not can_add_book
        assert member_user.has_any_permission(['can_view_books', 'can_add_book']) is True
        assert member_user.has_any_permission(['can_add_book', 'can_delete_book']) is False
    
    def test_has_all_permissions(self, member_user, member_group):
        """Test has_all_permissions method."""
        # User has all these permissions
        assert member_user.has_all_permissions(['can_view_books', 'can_borrow_book']) is True
        
        # User doesn't have all these permissions
        assert member_user.has_all_permissions(['can_view_books', 'can_add_book']) is False
    
    def test_direct_permissions(self, member_user, permissions):
        """Test direct permissions assignment."""
        # Add direct permission
        member_user.direct_permissions.add(permissions['can_add_book'])
        
        assert member_user.has_permission('can_add_book') is True
        assert 'can_add_book' in member_user.get_all_permissions()
    
    def test_get_groups(self, member_user, member_group):
        """Test get_groups method."""
        groups = member_user.get_groups()
        
        assert member_group in groups
        assert groups.count() == 1


# ============================================
#    USER PROFILE MODEL TESTS
# ============================================

@pytest.mark.django_db
class TestUserProfile:
    """Test UserProfile model."""
    
    def test_create_profile(self, member_user):
        """Test creating a user profile."""
        profile = UserProfile.objects.create(
            user=member_user,
            bio='Test bio',
            address='123 Test St',
            avatar_url='https://example.com/avatar.jpg',
            birth_date='1990-01-01'
        )
        
        assert profile.user == member_user
        assert profile.bio == 'Test bio'
        assert profile.address == '123 Test St'
    
    def test_profile_one_to_one_relationship(self, member_user):
        """Test profile has one-to-one relationship with user."""
        profile1 = UserProfile.objects.create(user=member_user)
        
        # Try to create another profile for same user
        with pytest.raises(IntegrityError):
            UserProfile.objects.create(user=member_user)
    
    def test_profile_str_representation(self, member_user):
        """Test profile string representation."""
        profile = UserProfile.objects.create(user=member_user)
        assert str(profile) == f"Profile of {member_user.username}"
    
    def test_profile_optional_fields(self, member_user):
        """Test profile optional fields can be null."""
        profile = UserProfile.objects.create(user=member_user)
        
        assert profile.bio is None or profile.bio == ''
        assert profile.address is None or profile.address == ''
        assert profile.avatar_url is None or profile.avatar_url == ''
        assert profile.birth_date is None


# ============================================
#    PERMISSION MODEL TESTS
# ============================================

@pytest.mark.django_db
class TestPermission:
    """Test Permission model."""
    
    def test_create_permission(self):
        """Test creating a permission."""
        perm = Permission.objects.create(
            code='test_permission',
            name='Test Permission',
            description='A test permission',
            category='SYSTEM'
        )
        
        assert perm.code == 'test_permission'
        assert perm.name == 'Test Permission'
        assert perm.category == 'SYSTEM'
    
    def test_permission_code_unique(self):
        """Test permission code must be unique."""
        Permission.objects.create(
            code='unique_perm',
            name='Unique Permission',
            category='SYSTEM'
        )
        
        with pytest.raises(IntegrityError):
            Permission.objects.create(
                code='unique_perm',
                name='Another Permission',
                category='SYSTEM'
            )
    
    def test_permission_str_representation(self):
        """Test permission string representation."""
        perm = Permission.objects.create(
            code='test_perm',
            name='Test Permission',
            category='SYSTEM'
        )
        
        assert str(perm) == 'Test Permission (test_perm)'
    
    def test_permission_category_choices(self):
        """Test permission category choices."""
        categories = ['BOOKS', 'LOANS', 'USERS', 'REPORTS', 'SYSTEM']
        
        for category in categories:
            perm = Permission.objects.create(
                code=f'test_{category.lower()}',
                name=f'Test {category}',
                category=category
            )
            assert perm.category == category


# ============================================
#    GROUP MODEL TESTS
# ============================================

@pytest.mark.django_db
class TestGroup:
    """Test Group model."""
    
    def test_create_group(self, permissions):
        """Test creating a group."""
        group = Group.objects.create(
            name='Test Group',
            description='A test group',
            is_default=False
        )
        
        group.permissions.set([
            permissions['can_view_books'],
            permissions['can_borrow_book']
        ])
        
        assert group.name == 'Test Group'
        assert group.permissions.count() == 2
    
    def test_group_name_unique(self):
        """Test group name must be unique."""
        Group.objects.create(name='Unique Group')
        
        with pytest.raises(IntegrityError):
            Group.objects.create(name='Unique Group')
    
    def test_group_str_representation(self):
        """Test group string representation."""
        group = Group.objects.create(name='Test Group')
        assert str(group) == 'Test Group'
    
    def test_get_permission_codes(self, permissions):
        """Test get_permission_codes method."""
        group = Group.objects.create(name='Test Group')
        group.permissions.set([
            permissions['can_view_books'],
            permissions['can_borrow_book']
        ])
        
        codes = group.get_permission_codes()
        
        assert 'can_view_books' in codes
        assert 'can_borrow_book' in codes
        assert len(codes) == 2
    
    def test_group_users_relationship(self, member_user, member_group):
        """Test group-users many-to-many relationship."""
        assert member_user in member_group.users.all()
        assert member_group in member_user.custom_groups.all()
    
    def test_is_default_flag(self):
        """Test is_default flag."""
        default_group = Group.objects.create(name='Default', is_default=True)
        normal_group = Group.objects.create(name='Normal', is_default=False)
        
        assert default_group.is_default is True
        assert normal_group.is_default is False

