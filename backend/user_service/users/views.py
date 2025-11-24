from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User, UserProfile
from .serializers import (
    UserSerializer, UserDetailSerializer, UserProfileSerializer,
    RegisterSerializer, LoginSerializer
)


# ============================================
#    REGISTER
# ============================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    
    # Generate tokens for the new user
    refresh = RefreshToken.for_user(user)
    
    return Response({
        "message": "Inscription réussie.",
        "user": UserSerializer(user).data,
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }, status=status.HTTP_201_CREATED)


# ============================================
#    LOGIN
# ============================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data["user"]  # Fixed: was validate_data
    refresh = RefreshToken.for_user(user)
    
    return Response({
        "message": "Connexion réussie.",
        "user": UserSerializer(user).data,
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    })


# ============================================
#    TOKEN VALIDATION (INTROSPECTION ENDPOINT)
#    This is the KEY endpoint for microservices
# ============================================

@api_view(['POST'])
@permission_classes([AllowAny])  # Other services call this
def validate_token(request):
    """
    Validate JWT token and return user data with permissions.
    
    Other microservices call this endpoint to:
    1. Verify the token is valid
    2. Get real-time user data and permissions
    
    Request body: {"token": "eyJ..."}
    """
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
#    CHECK PERMISSION ENDPOINT
#    Quick permission check for services
# ============================================

@api_view(['POST'])
@permission_classes([AllowAny])
def check_permission(request):
    """
    Check if a user has specific permission(s).
    
    Request body: {
        "token": "eyJ...",
        "permission": "can_add_book"  # or
        "permissions": ["can_add_book", "can_edit_book"]
    }
    """
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
#    GET CURRENT USER (ME)
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Get current authenticated user with permissions."""
    return Response({
        "user": UserDetailSerializer(request.user).data
    })


# ============================================
#    USER PROFILE
# ============================================

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        return Response(UserProfileSerializer(profile).data)
    
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)