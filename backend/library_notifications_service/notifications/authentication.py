import requests
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication that validates tokens with the User Service.
    
    Usage in views:
        @permission_classes([IsAuthenticated, CanCreateNotification])
        def create_notification(request):
            user_id = request.user.id
            # Your logic here
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        
        Returns:
            tuple: (RemoteUser, None) if authentication succeeds
            None: if no authentication credentials were provided
            
        Raises:
            AuthenticationFailed: if authentication fails
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        # Parse "Bearer <token>" format
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise AuthenticationFailed('Invalid Authorization header format. Expected: Bearer <token>')
        
        token = parts[1]
        
        try:
            user_data = self.verify_token_with_user_service(token)
            user = RemoteUser(user_data)
            return (user, None)
        except requests.RequestException as e:
            logger.error(f'User service unavailable: {e}')
            raise AuthenticationFailed(f'User service unavailable: {str(e)}')
        except Exception as e:
            logger.error(f'Authentication failed: {e}')
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')
    
    def verify_token_with_user_service(self, token):
        """
        Call the User Service to validate the token.
        
        Args:
            token (str): JWT token to validate
            
        Returns:
            dict: User data including permissions
            
        Raises:
            AuthenticationFailed: If token is invalid
        """
        user_service_url = settings.USER_SERVICE_URL
        validate_url = f"{user_service_url}/api/users/validate/"
        
        try:
            response = requests.post(
                validate_url,
                json={'token': token},
                timeout=settings.USER_SERVICE_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('valid'):
                    user_data = data.get('user')
                    if not user_data:
                        raise AuthenticationFailed('No user data in response')
                    return user_data
                else:
                    raise AuthenticationFailed(data.get('error', 'Invalid token'))
            else:
                logger.error(f'Token validation failed with status {response.status_code}')
                raise AuthenticationFailed('Token validation failed')
                
        except requests.Timeout:
            logger.error('User service timeout')
            raise AuthenticationFailed('User service timeout')
        except requests.ConnectionError:
            logger.error('Cannot connect to user service')
            raise AuthenticationFailed('Cannot connect to user service')


class RemoteUser:
    """
    A user-like object that holds data from the remote User Service.
    
    This mimics Django's User model interface but doesn't require a database.
    All user data comes from the User Service via JWT validation.
    """
    
    def __init__(self, user_data):
        """
        Initialize RemoteUser from User Service data.
        
        Args:
            user_data (dict): User data from User Service including:
                - id: User ID
                - email: User email
                - username: Username
                - role: User role (MEMBER, LIBRARIAN, ADMIN)
                - permissions: List of permission codes
        """
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
        """
        Check if user has a specific permission.
        
        Args:
            permission_code (str): Permission code to check (e.g., 'can_create_notification')
            
        Returns:
            bool: True if user has the permission
        """
        return permission_code in self.permissions
    
    def has_any_permission(self, permission_codes):
        """
        Check if user has any of the given permissions.
        
        Args:
            permission_codes (list): List of permission codes
            
        Returns:
            bool: True if user has at least one permission
        """
        return any(perm in self.permissions for perm in permission_codes)
    
    def has_all_permissions(self, permission_codes):
        """
        Check if user has all of the given permissions.
        
        Args:
            permission_codes (list): List of permission codes
            
        Returns:
            bool: True if user has all permissions
        """
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