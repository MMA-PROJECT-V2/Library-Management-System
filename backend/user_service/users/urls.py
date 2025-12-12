from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    register, login_view, me, user_profile,
    validate_token, check_permission, get_user_by_id
)

urlpatterns = [
    # ============================================
    #    AUTH ENDPOINTS
    # ============================================
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    
    # JWT Token endpoints (SimpleJWT)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ============================================
    #    TOKEN INTROSPECTION (for other microservices)
    # ============================================
    path('validate/', validate_token, name='validate_token'),
    path('check-permission/', check_permission, name='check_permission'),
    
    # ============================================
    #    USER ENDPOINTS
    # ============================================
    path('me/', me, name='me'),
    path('profile/', user_profile, name='user_profile'),
    
    # Internal usage
    path('<int:user_id>/', get_user_by_id, name='get_user_by_id'),
]