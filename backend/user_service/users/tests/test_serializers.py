"""
Tests for serializers.
"""

import pytest
from django.contrib.auth import get_user_model
from users.serializers import (
    UserSerializer, UserDetailSerializer, RegisterSerializer,
    LoginSerializer, PermissionSerializer, GroupSerializer
)
from users.models import Permission, Group

User = get_user_model()


# ============================================
#    USER SERIALIZER TESTS
# ============================================

@pytest.mark.django_db
class TestUserSerializer:
    """Test UserSerializer."""
    
    def test_user_serialization(self, member_user):
        """Test serializing a user."""
        serializer = UserSerializer(member_user)
        data = serializer.data
        
        assert data['id'] == member_user.id
        assert data['email'] == member_user.email
        assert data['username'] == member_user.username
        assert data['role'] == member_user.role
        assert 'password' not in data  # Password should not be exposed


# ============================================
#    USER DETAIL SERIALIZER TESTS
# ============================================

@pytest.mark.django_db
class TestUserDetailSerializer:
    """Test UserDetailSerializer (includes permissions)."""
    
    def test_user_detail_serialization(self, member_user):
        """Test detailed user serialization includes permissions."""
        serializer = UserDetailSerializer(member_user)
        data = serializer.data
        
        assert data['id'] == member_user.id
        assert data['email'] == member_user.email
        assert 'permissions' in data
        assert 'groups' in data
        assert isinstance(data['permissions'], list)
        assert isinstance(data['groups'], list)
    
    def test_permissions_included(self, member_user, member_group):
        """Test permissions are correctly included."""
        serializer = UserDetailSerializer(member_user)
        data = serializer.data
        
        permissions = data['permissions']
        assert 'can_borrow_book' in permissions
        assert 'can_view_books' in permissions
    
    def test_groups_included(self, member_user, member_group):
        """Test groups are correctly included."""
        serializer = UserDetailSerializer(member_user)
        data = serializer.data
        
        groups = data['groups']
        assert 'MEMBER' in groups


# ============================================
#    REGISTER SERIALIZER TESTS
# ============================================

@pytest.mark.django_db
class TestRegisterSerializer:
    """Test RegisterSerializer."""
    
    def test_valid_registration_data(self, member_group):
        """Test serializer with valid registration data."""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        
        user = serializer.save()
        assert user.email == 'newuser@example.com'
        assert user.check_password('securepass123')
    
    def test_password_too_short(self):
        """Test validation fails for short password."""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'short',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
    
    def test_missing_required_fields(self):
        """Test validation fails for missing fields."""
        data = {
            'email': 'test@example.com'
            # Missing other required fields
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors
        assert 'password' in serializer.errors
    
    def test_auto_assign_to_group(self, member_group):
        """Test user is auto-assigned to group based on role."""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        
        # User should be in MEMBER group
        assert user.custom_groups.filter(name='MEMBER').exists()


# ============================================
#    LOGIN SERIALIZER TESTS
# ============================================

@pytest.mark.django_db
class TestLoginSerializer:
    """Test LoginSerializer."""
    
    def test_valid_login(self, member_user):
        """Test serializer with valid credentials."""
        data = {
            'email': 'member@library.com',
            'password': 'testpass123'
        }
        
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['user'] == member_user
    
    def test_invalid_password(self, member_user):
        """Test serializer with invalid password."""
        data = {
            'email': 'member@library.com',
            'password': 'wrongpassword'
        }
        
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
    
    def test_nonexistent_email(self):
        """Test serializer with nonexistent email."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
    
    def test_inactive_user(self, member_user):
        """Test serializer rejects inactive user."""
        member_user.is_active = False
        member_user.save()
        
        data = {
            'email': 'member@library.com',
            'password': 'testpass123'
        }
        
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()


# ============================================
#    PERMISSION SERIALIZER TESTS
# ============================================

@pytest.mark.django_db
class TestPermissionSerializer:
    """Test PermissionSerializer."""
    
    def test_permission_serialization(self):
        """Test serializing a permission."""
        perm = Permission.objects.create(
            code='test_perm',
            name='Test Permission',
            description='A test',
            category='SYSTEM'
        )
        
        serializer = PermissionSerializer(perm)
        data = serializer.data
        
        assert data['code'] == 'test_perm'
        assert data['name'] == 'Test Permission'
        assert data['category'] == 'SYSTEM'


# ============================================
#    GROUP SERIALIZER TESTS
# ============================================

@pytest.mark.django_db
class TestGroupSerializer:
    """Test GroupSerializer."""
    
    def test_group_serialization(self, member_group):
        """Test serializing a group."""
        serializer = GroupSerializer(member_group)
        data = serializer.data
        
        assert data['name'] == 'MEMBER'
        assert 'permissions' in data
        assert isinstance(data['permissions'], list)
    
    def test_group_with_permissions(self, member_group, permissions):
        """Test group serialization includes permissions."""
        serializer = GroupSerializer(member_group)
        data = serializer.data
        
        perm_codes = [p['code'] for p in data['permissions']]
        assert 'can_view_books' in perm_codes
        assert 'can_borrow_book' in perm_codes