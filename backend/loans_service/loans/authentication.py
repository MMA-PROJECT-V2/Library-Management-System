import requests
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class JWTAuthentication(BaseAuthentication):
    """
    JWT Authentication by validating token with User Service
    """
    
    def authenticate(self, request):
        """
        Authenticate the request by validating JWT token with user service.
        
        Returns:
            tuple: (user, None) if authentication successful
            None: if no authentication attempted
            
        Raises:
            AuthenticationFailed: if authentication fails
        """
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
        
        # Parse Authorization header
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise AuthenticationFailed('Invalid Authorization header format. Use: Bearer <token>')
        
        token = parts[1]
        
        try:
            user_data = self._validate_token_with_user_service(token)
            user = RemoteUser(user_data)
            return (user, None)
        except requests.Timeout:
            logger.error("User service timeout during token validation")
            raise AuthenticationFailed('User service timeout')
        except requests.ConnectionError:
            logger.error("Cannot connect to user service")
            raise AuthenticationFailed('Cannot connect to user service')
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')
    
    def _validate_token_with_user_service(self, token):
        """
        Validate token with user service.
        
        Args:
            token: JWT access token
            
        Returns:
            dict: User data including permissions
            
        Raises:
            AuthenticationFailed: if token is invalid
        """
        user_service_url = settings.SERVICES.get('USER_SERVICE', 'http://localhost:8001')
        validate_url = f"{user_service_url}/api/users/validate/"
        
        try:
            response = requests.post(
                validate_url,
                json={'token': token},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('valid'):
                    return data.get('user')
                else:
                    raise AuthenticationFailed(data.get('error', 'Invalid token'))
            else:
                logger.error(f"Token validation failed. Status: {response.status_code}, Body: {response.text}")
                raise AuthenticationFailed(f'Token validation failed: {response.status_code} - {response.text}')
                
        except requests.Timeout:
            raise AuthenticationFailed('User service timeout')
        except requests.ConnectionError:
            raise AuthenticationFailed('Cannot connect to user service')


class RemoteUser:
    """
    User-like object that holds data from the remote user service.
    Mimics Django's User model but doesn't require a database.
    """
    
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.email = user_data.get('email')
        self.username = user_data.get('username', user_data.get('email'))
        self.first_name = user_data.get('first_name', '')
        self.last_name = user_data.get('last_name', '')
        self.role = user_data.get('role', 'MEMBER')
        self.permissions = user_data.get('permissions', [])
        self.groups = user_data.get('groups', [])
        self.is_active = user_data.get('is_active', True)
        self.is_staff = user_data.get('is_staff', False)
        self.is_superuser = user_data.get('is_superuser', False)
        self._user_data = user_data
    
    @property
    def is_authenticated(self):
        """Always return True for authenticated users."""
        return True
    
    @property
    def is_anonymous(self):
        """Always return False for authenticated users."""
        return False
    
    def has_permission(self, permission_code):
        """Check if user has a specific permission."""
        return permission_code in self.permissions
    
    def has_any_permission(self, permission_codes):
        """Check if user has any of the given permissions."""
        return any(perm in self.permissions for perm in permission_codes)
    
    def has_all_permissions(self, permission_codes):
        """Check if user has all of the given permissions."""
        return all(perm in self.permissions for perm in permission_codes)
    
    def is_member(self):
        """Check if user is a member."""
        return self.role == 'MEMBER'
    
    def is_librarian(self):
        """Check if user is a librarian."""
        return self.role == 'LIBRARIAN'
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'ADMIN' or self.is_superuser
    
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    def __repr__(self):
        return f"<RemoteUser: {self.email}>"