from django.urls import path
from .views import register, login_view, Me, UserProfileView


urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('me/', Me, name='me'),
    path('profile/', UserProfileView, name='user-profile'),
]