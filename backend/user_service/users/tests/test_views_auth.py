"""
Tests for authentication views: register, login, validate_token, check_permission.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


# ============================================
#    REGISTER ENDPOINT TESTS
# ============================================

@pytest.mark.django_db
class TestRegisterView:
    """Test user registration endpoint."""
    
    def test_register_success(self, api_client, member_group):
        """Test successful user registration."""
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'message' in response.data
        assert 'user' in response.data
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == 'newuser@example.com'
    
    def test_register_duplicate_email(self, api_client, member_user, member_group):
        """Test registration with duplicate email fails."""
        url = reverse('register')
        data = {
            'email': member_user.email,
            'username': 'different_user',
            'password': 'pass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_missing_fields(self, api_client):
        """Test registration with missing required fields."""
        url = reverse('register')
        data = {
            'email': 'test@example.com'
            # Missing other required fields
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_weak_password(self, api_client):
        """Test registration with weak password fails."""
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'short',  # Too short
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_register_returns_tokens(self, api_client, member_group):
        """Test registration returns valid JWT tokens."""
        url = reverse('register')
        data = {
            'email': 'tokenuser@example.com',
            'username': 'tokenuser',
            'password': 'securepass123',
            'first_name': 'Token',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        
        # Verify tokens are valid
        try:
            AccessToken(access_token)
            RefreshToken(refresh_token)
        except TokenError:
            pytest.fail("Invalid tokens returned from registration")


# ============================================
#    LOGIN ENDPOINT TESTS
# ============================================

@pytest.mark.django_db
class TestLoginView:
    """Test user login endpoint."""
    
    def test_login_success(self, api_client, member_user):
        """Test successful login."""
        url = reverse('login')
        data = {
            'email': member_user.email,
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert 'user' in response.data
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == member_user.email
    
    def test_login_invalid_credentials(self, api_client, member_user):
        """Test login with invalid password fails."""
        url = reverse('login')
        data = {
            'email': member_user.email,
            'password': 'wrongpassword'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data
    
    def test_login_nonexistent_user(self, api_client):
        """Test login with nonexistent email fails."""
        url = reverse('login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'anypassword'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_inactive_user(self, api_client, member_user):
        """Test login with inactive user fails."""
        member_user.is_active = False
        member_user.save()
        
        url = reverse('login')
        data = {
            'email': member_user.email,
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_returns_valid_tokens(self, api_client, member_user):
        """Test login returns valid JWT tokens."""
        url = reverse('login')
        data = {
            'email': member_user.email,
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        
        # Verify tokens are valid
        try:
            AccessToken(access_token)
            RefreshToken(refresh_token)
        except TokenError:
            pytest.fail("Invalid tokens returned from login")


# ============================================
#    VALIDATE TOKEN ENDPOINT TESTS
# ============================================

@pytest.mark.django_db
class TestValidateTokenView:
    """Test token validation endpoint (for microservices)."""
    
    def test_validate_valid_token(self, api_client, member_user, member_token):
        """Test validating a valid token."""
        url = reverse('validate_token')
        data = {
            'token': member_token['access']
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['valid'] is True
        assert 'user' in response.data
        assert response.data['user']['id'] == member_user.id
        assert 'permissions' in response.data['user']
        assert 'groups' in response.data['user']
    
    def test_validate_missing_token(self, api_client):
        """Test validation without token fails."""
        url = reverse('validate_token')
        data = {}
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['valid'] is False
        assert 'error' in response.data
    
    def test_validate_invalid_token(self, api_client):
        """Test validation with invalid token fails."""
        url = reverse('validate_token')
        data = {
            'token': 'invalid.token.here'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['valid'] is False
        assert 'error' in response.data
    
    def test_validate_token_inactive_user(self, api_client, member_user):
        """Test validation with token for inactive user fails."""
        # Create token for user
        refresh = RefreshToken.for_user(member_user)
        access_token = str(refresh.access_token)
        
        # Deactivate user
        member_user.is_active = False
        member_user.save()
        
        url = reverse('validate_token')
        data = {
            'token': access_token
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['valid'] is False
        assert 'error' in response.data
    
    def test_validate_token_returns_user_data(self, api_client, member_user, member_token):
        """Test validation returns complete user data."""
        url = reverse('validate_token')
        data = {
            'token': member_token['access']
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        user_data = response.data['user']
        assert user_data['email'] == member_user.email
        assert user_data['role'] == member_user.role
        assert isinstance(user_data['permissions'], list)
        assert isinstance(user_data['groups'], list)


# ============================================
#    CHECK PERMISSION ENDPOINT TESTS
# ============================================

@pytest.mark.django_db
class TestCheckPermissionView:
    """Test permission checking endpoint (for microservices)."""
    
    def test_check_single_permission_allowed(self, api_client, member_user, member_token, member_group):
        """Test checking a permission the user has."""
        url = reverse('check_permission')
        data = {
            'token': member_token['access'],
            'permission': 'can_view_books'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['allowed'] is True
        assert response.data['user_id'] == member_user.id
        assert response.data['role'] == member_user.role
    
    def test_check_single_permission_denied(self, api_client, member_user, member_token):
        """Test checking a permission the user doesn't have."""
        url = reverse('check_permission')
        data = {
            'token': member_token['access'],
            'permission': 'can_add_book'  # Member doesn't have this
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['allowed'] is False
    
    def test_check_multiple_permissions_all_allowed(self, api_client, member_user, member_token, member_group):
        """Test checking multiple permissions user has all of."""
        url = reverse('check_permission')
        data = {
            'token': member_token['access'],
            'permissions': ['can_view_books', 'can_borrow_book']
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['allowed'] is True
    
    def test_check_multiple_permissions_some_missing(self, api_client, member_user, member_token, member_group):
        """Test checking multiple permissions where user lacks some."""
        url = reverse('check_permission')
        data = {
            'token': member_token['access'],
            'permissions': ['can_view_books', 'can_add_book']  # User has first, not second
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['allowed'] is False
        assert 'missing' in response.data
        assert 'can_add_book' in response.data['missing']
    
    def test_check_permission_missing_token(self, api_client):
        """Test permission check without token fails."""
        url = reverse('check_permission')
        data = {
            'permission': 'can_view_books'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['allowed'] is False
    
    def test_check_permission_no_permission_specified(self, api_client, member_token):
        """Test permission check without permission specified fails."""
        url = reverse('check_permission')
        data = {
            'token': member_token['access']
            # No permission or permissions
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['allowed'] is False
    
    def test_check_permission_invalid_token(self, api_client):
        """Test permission check with invalid token fails."""
        url = reverse('check_permission')
        data = {
            'token': 'invalid.token',
            'permission': 'can_view_books'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['allowed'] is False
    
    def test_admin_has_all_permissions(self, api_client, admin_user, admin_token, permissions):
        """Test admin user has all permissions."""
        url = reverse('check_permission')
        
        # Check various permissions
        for perm_code in ['can_view_books', 'can_add_book', 'can_delete_book', 'can_manage_loans']:
            data = {
                'token': admin_token['access'],
                'permission': perm_code
            }
            
            response = api_client.post(url, data, format='json')
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['allowed'] is True, f"Admin should have {perm_code}"