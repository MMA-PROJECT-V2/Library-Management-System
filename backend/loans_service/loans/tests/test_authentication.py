"""
Unit tests for loans.authentication module.

Tests for JWTAuthentication and RemoteUser classes.
"""
import pytest
from unittest.mock import Mock, patch
import requests

from loans.authentication import JWTAuthentication, RemoteUser
from rest_framework.exceptions import AuthenticationFailed


class TestRemoteUser:
    """Tests for RemoteUser class."""
    
    @pytest.fixture
    def user_data(self):
        return {
            'id': 1,
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'MEMBER',
            'permissions': ['can_view_loans', 'can_borrow_book'],
            'groups': ['members'],
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
        }
    
    def test_remote_user_initialization(self, user_data):
        """Test that RemoteUser correctly initializes all properties."""
        user = RemoteUser(user_data)
        
        assert user.id == 1
        assert user.email == 'test@example.com'
        assert user.username == 'testuser'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.role == 'MEMBER'
        assert user.permissions == ['can_view_loans', 'can_borrow_book']
        assert user.groups == ['members']
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
    
    def test_remote_user_defaults(self):
        """Test default values when user_data is minimal."""
        user = RemoteUser({'id': 1, 'email': 'minimal@example.com'})
        
        assert user.id == 1
        assert user.email == 'minimal@example.com'
        assert user.username == 'minimal@example.com'  # Falls back to email
        assert user.first_name == ''
        assert user.last_name == ''
        assert user.role == 'MEMBER'
        assert user.permissions == []
        assert user.groups == []
    
    def test_is_authenticated_always_true(self, user_data):
        """Test that is_authenticated property returns True."""
        user = RemoteUser(user_data)
        assert user.is_authenticated is True
    
    def test_is_anonymous_always_false(self, user_data):
        """Test that is_anonymous property returns False."""
        user = RemoteUser(user_data)
        assert user.is_anonymous is False
    
    def test_has_permission_granted(self, user_data):
        """Test has_permission returns True when user has the permission."""
        user = RemoteUser(user_data)
        assert user.has_permission('can_view_loans') is True
        assert user.has_permission('can_borrow_book') is True
    
    def test_has_permission_denied(self, user_data):
        """Test has_permission returns False when user lacks the permission."""
        user = RemoteUser(user_data)
        assert user.has_permission('can_manage_loans') is False
    
    def test_has_any_permission_granted(self, user_data):
        """Test has_any_permission returns True if any permission matches."""
        user = RemoteUser(user_data)
        assert user.has_any_permission(['can_view_loans', 'can_manage_loans']) is True
    
    def test_has_any_permission_denied(self, user_data):
        """Test has_any_permission returns False if no permission matches."""
        user = RemoteUser(user_data)
        assert user.has_any_permission(['can_manage_loans', 'can_view_all_loans']) is False
    
    def test_has_all_permissions_granted(self, user_data):
        """Test has_all_permissions returns True if all permissions match."""
        user = RemoteUser(user_data)
        assert user.has_all_permissions(['can_view_loans', 'can_borrow_book']) is True
    
    def test_has_all_permissions_denied(self, user_data):
        """Test has_all_permissions returns False if any permission is missing."""
        user = RemoteUser(user_data)
        assert user.has_all_permissions(['can_view_loans', 'can_manage_loans']) is False
    
    def test_is_member_true(self, user_data):
        """Test is_member returns True for MEMBER role."""
        user = RemoteUser(user_data)
        assert user.is_member() is True
    
    def test_is_member_false(self, user_data):
        """Test is_member returns False for non-MEMBER role."""
        user_data['role'] = 'LIBRARIAN'
        user = RemoteUser(user_data)
        assert user.is_member() is False
    
    def test_is_librarian_true(self, user_data):
        """Test is_librarian returns True for LIBRARIAN role."""
        user_data['role'] = 'LIBRARIAN'
        user = RemoteUser(user_data)
        assert user.is_librarian() is True
    
    def test_is_librarian_false(self, user_data):
        """Test is_librarian returns False for non-LIBRARIAN role."""
        user = RemoteUser(user_data)
        assert user.is_librarian() is False
    
    def test_is_admin_true_by_role(self, user_data):
        """Test is_admin returns True for ADMIN role."""
        user_data['role'] = 'ADMIN'
        user = RemoteUser(user_data)
        assert user.is_admin() is True
    
    def test_is_admin_true_by_superuser(self, user_data):
        """Test is_admin returns True for superuser."""
        user_data['is_superuser'] = True
        user = RemoteUser(user_data)
        assert user.is_admin() is True
    
    def test_is_admin_false(self, user_data):
        """Test is_admin returns False for regular users."""
        user = RemoteUser(user_data)
        assert user.is_admin() is False
    
    def test_str_representation(self, user_data):
        """Test string representation of RemoteUser."""
        user = RemoteUser(user_data)
        assert str(user) == 'test@example.com (MEMBER)'
    
    def test_repr_representation(self, user_data):
        """Test repr representation of RemoteUser."""
        user = RemoteUser(user_data)
        assert repr(user) == '<RemoteUser: test@example.com>'


class TestJWTAuthentication:
    """Tests for JWTAuthentication class."""
    
    @pytest.fixture
    def jwt_auth(self):
        return JWTAuthentication()
    
    @pytest.fixture
    def mock_request(self):
        return Mock()
    
    def test_authenticate_no_header(self, jwt_auth, mock_request):
        """Test returns None when no Authorization header."""
        mock_request.headers = {}
        result = jwt_auth.authenticate(mock_request)
        assert result is None
    
    def test_authenticate_invalid_format_single_part(self, jwt_auth, mock_request):
        """Test raises AuthenticationFailed for single-part header."""
        mock_request.headers = {'Authorization': 'invalidtoken'}
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            jwt_auth.authenticate(mock_request)
        assert 'Invalid Authorization header format' in str(exc_info.value)
    
    def test_authenticate_invalid_format_not_bearer(self, jwt_auth, mock_request):
        """Test raises AuthenticationFailed when not Bearer prefix."""
        mock_request.headers = {'Authorization': 'Basic sometoken'}
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            jwt_auth.authenticate(mock_request)
        assert 'Invalid Authorization header format' in str(exc_info.value)
    
    @patch('loans.authentication.requests.post')
    def test_authenticate_success(self, mock_post, jwt_auth, mock_request):
        """Test successful authentication with valid token."""
        mock_request.headers = {'Authorization': 'Bearer valid_token'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'valid': True,
            'user': {
                'id': 1,
                'email': 'test@example.com',
                'role': 'MEMBER',
                'permissions': []
            }
        }
        mock_post.return_value = mock_response
        
        user, auth = jwt_auth.authenticate(mock_request)
        
        assert isinstance(user, RemoteUser)
        assert user.email == 'test@example.com'
        assert auth is None
    
    @patch('loans.authentication.requests.post')
    def test_authenticate_invalid_token(self, mock_post, jwt_auth, mock_request):
        """Test raises AuthenticationFailed for invalid token."""
        mock_request.headers = {'Authorization': 'Bearer invalid_token'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'valid': False,
            'error': 'Token expired'
        }
        mock_post.return_value = mock_response
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            jwt_auth.authenticate(mock_request)
        assert 'Token expired' in str(exc_info.value)
    
    @patch('loans.authentication.requests.post')
    def test_authenticate_validation_failed(self, mock_post, jwt_auth, mock_request):
        """Test raises AuthenticationFailed when validation returns non-200."""
        mock_request.headers = {'Authorization': 'Bearer some_token'}
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_post.return_value = mock_response
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            jwt_auth.authenticate(mock_request)
        assert 'Token validation failed' in str(exc_info.value)
    
    @patch('loans.authentication.requests.post')
    def test_authenticate_timeout(self, mock_post, jwt_auth, mock_request):
        """Test raises AuthenticationFailed on timeout."""
        mock_request.headers = {'Authorization': 'Bearer valid_token'}
        mock_post.side_effect = requests.Timeout()
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            jwt_auth.authenticate(mock_request)
        assert 'User service timeout' in str(exc_info.value)
    
    @patch('loans.authentication.requests.post')
    def test_authenticate_connection_error(self, mock_post, jwt_auth, mock_request):
        """Test raises AuthenticationFailed on connection error."""
        mock_request.headers = {'Authorization': 'Bearer valid_token'}
        mock_post.side_effect = requests.ConnectionError()
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            jwt_auth.authenticate(mock_request)
        assert 'Cannot connect to user service' in str(exc_info.value)
