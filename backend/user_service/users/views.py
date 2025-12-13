from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import User, UserProfile
from .serializers import (
    UserSerializer, UserDetailSerializer, UserProfileSerializer,
    RegisterSerializer, LoginSerializer
)
from .events import publish_user_registered
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)



def send_notification_from_template(template_name, user_id, context, token=None):
    """Helper to send notifications using templates via Notification Service"""
    headers = {}
    if token:
        if token.lower().startswith('bearer '):
            headers['Authorization'] = token
        else:
            headers['Authorization'] = f"Bearer {token}"
            
    try:
        response = requests.post(
            f"{settings.SERVICES.get('NOTIFICATION_SERVICE', 'http://localhost:8004')}/api/notifications/send_from_template/",
            json={
                'template_id': get_template_id(template_name),
                'user_id': user_id,
                'context': context,
                'type': 'EMAIL'
            },
            headers=headers,
            timeout=5
        )
        if response.status_code != 201:
            logger.warning(f"Notification service returned {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        # Don't re-raise, notification failure shouldn't block registration
        pass


def get_template_id(template_name):
    """Map template names to IDs"""
    template_map = {
        'user_registered': 5,  # This is the 5th template
        'loan_created': 1,
        'loan_returned_ontime': 2,
        'loan_returned_late': 3,
        'loan_renewed': 4
    }
    return template_map.get(template_name, 1)


# ============================================
#    REGISTER VIEW
# ============================================

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    """
    User registration endpoint.
    
    CSRF exempt because:
    - This is a stateless API using JWT authentication
    - No session cookies are used
    - Client authenticates via Bearer tokens
    """
    permission_classes = [AllowAny]
    
    
    def post(self, request):
        """
        Register a new user and return JWT tokens.
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Publish event
        try:
            publish_user_registered(user)
        except Exception as e:
            logger.error(f"Failed to publish user_registered event: {e}")

        return Response({
            "message": "Inscription réussie.",
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_201_CREATED)


# ============================================
#    LOGIN VIEW
# ============================================

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """
    User login endpoint.
    
    CSRF exempt because:
    - This is a stateless API using JWT authentication
    - No session cookies are used
    - Returns JWT tokens for authentication
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Authenticate user and return JWT tokens."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Connexion réussie.",
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })


# ============================================
#    TOKEN VALIDATION VIEW (for microservices)
# ============================================

@method_decorator(csrf_exempt, name='dispatch')
class ValidateTokenView(APIView):
    """
    Validate JWT token and return user data.
    
    CSRF exempt because:
    - Called by other microservices (not web browsers)
    - Uses JWT for authentication
    - No session state maintained
    
    Other microservices call this to:
    1. Verify token validity
    2. Get real-time user data and permissions
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Validate token and return user data."""
        token = request.data.get('token')
        
        if not token:
            return Response({
                "valid": False,
                "error": "Token is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Decode and validate the token
            access_token = AccessToken(token)
            user_id = access_token.get('user_id')
            
            # Get user from database (real-time data)
            user = User.objects.get(id=user_id)
            
            if not user.is_active:
                return Response({
                    "valid": False,
                    "error": "User account is disabled"
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Return user with all permissions
            return Response({
                "valid": True,
                "user": UserDetailSerializer(user).data
            })
            
        except TokenError as e:
            return Response({
                "valid": False,
                "error": f"Invalid token: {str(e)}"
            }, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({
                "valid": False,
                "error": "User not found"
            }, status=status.HTTP_401_UNAUTHORIZED)


# ============================================
#    CHECK PERMISSION VIEW (for microservices)
# ============================================

@method_decorator(csrf_exempt, name='dispatch')
class CheckPermissionView(APIView):
    """
    Check if user has specific permission(s).
    
    CSRF exempt because:
    - Called by other microservices (not web browsers)
    - Uses JWT for authentication
    - No session state maintained
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Check user permissions based on JWT token."""
        token = request.data.get('token')
        permission = request.data.get('permission')
        permissions = request.data.get('permissions', [])
        
        if not token:
            return Response({
                "allowed": False,
                "error": "Token is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            access_token = AccessToken(token)
            user_id = access_token.get('user_id')
            user = User.objects.get(id=user_id, is_active=True)
            
            # Check single permission
            if permission:
                has_perm = user.has_permission(permission)
                return Response({
                    "allowed": has_perm,
                    "user_id": user.id,
                    "role": user.role
                })
            
            # Check multiple permissions (user must have ALL)
            if permissions:
                user_perms = set(user.get_all_permissions_list())
                has_all = set(permissions).issubset(user_perms)
                return Response({
                    "allowed": has_all,
                    "user_id": user.id,
                    "role": user.role,
                    "missing": list(set(permissions) - user_perms)
                })
            
            return Response({
                "allowed": False,
                "error": "No permission specified"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except (TokenError, User.DoesNotExist):
            return Response({
                "allowed": False,
                "error": "Invalid token or user"
            }, status=status.HTTP_401_UNAUTHORIZED)


# ============================================
#    ME VIEW (current user)
# ============================================

class MeView(APIView):
    """
    Get current authenticated user.
    
    No CSRF exemption needed - protected by JWT authentication.
    DRF handles CSRF for authenticated API views automatically.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current authenticated user with permissions."""
        return Response({
            "user": UserDetailSerializer(request.user).data
        })


# ============================================
#    USER PROFILE VIEW
# ============================================

class UserProfileView(APIView):
    """
    Get or update user profile.
    
    No CSRF exemption needed - protected by JWT authentication.
    DRF handles CSRF for authenticated API views automatically.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user profile."""
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return Response(UserProfileSerializer(profile).data)
    
    def put(self, request):
        """Update user profile."""
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# For backward compatibility, create function-based view wrappers
register = RegisterView.as_view()
login_view = LoginView.as_view()
validate_token = ValidateTokenView.as_view()
check_permission = CheckPermissionView.as_view()
me = MeView.as_view()
user_profile = UserProfileView.as_view()


# ============================================
#    GET USER BY ID (for microservices)
# ============================================

@method_decorator(csrf_exempt, name='dispatch')
class UserDetailByIDView(APIView):
    """
    Get user details by ID.
    Used by other microservices (e.g. Notification Service) to fetch user info.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            return Response({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone_number if hasattr(user, 'phone_number') else None,
                "is_active": user.is_active,
                "role": user.role
            })
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

get_user_by_id = UserDetailByIDView.as_view()