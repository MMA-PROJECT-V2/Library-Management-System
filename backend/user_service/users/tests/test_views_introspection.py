"""
Tests for user introspection views: me, user_profile.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from datetime import date


# ============================================
#    ME ENDPOINT TESTS
# ============================================

@pytest.mark.django_db
class TestMeView:
    """Test /me/ endpoint (get current user)."""
    
    def test_me_authenticated(self, authenticated_member_client, member_user):
        """Test getting current user when authenticated."""
        url = reverse('me')
        response = authenticated_member_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert response.data['user']['id'] == member_user.id
        assert response.data['user']['email'] == member_user.email
        assert 'permissions' in response.data['user']
        assert 'groups' in response.data['user']
    
    def test_me_unauthenticated(self, api_client):
        """Test /me/ endpoint requires authentication."""
        url = reverse('me')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_me_returns_detailed_user_data(self, authenticated_member_client, member_user, member_group):
        """Test /me/ returns detailed user information."""
        url = reverse('me')
        response = authenticated_member_client.get(url)
        
        user_data = response.data['user']
        
        # Check all expected fields
        assert 'id' in user_data
        assert 'email' in user_data
        assert 'username' in user_data
        assert 'first_name' in user_data
        assert 'last_name' in user_data
        assert 'role' in user_data
        assert 'is_active' in user_data
        assert 'is_staff' in user_data
        assert 'is_superuser' in user_data
        assert 'permissions' in user_data
        assert 'groups' in user_data
        assert 'max_loans' in user_data
        assert 'date_joined' in user_data
        
        # Check permissions are included
        assert isinstance(user_data['permissions'], list)
        assert 'can_view_books' in user_data['permissions']
        
        # Check groups are included
        assert isinstance(user_data['groups'], list)
        assert 'MEMBER' in user_data['groups']
    
    def test_me_different_roles(self, authenticated_librarian_client, authenticated_admin_client):
        """Test /me/ works for different user roles."""
        url = reverse('me')
        
        # Librarian
        response = authenticated_librarian_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['role'] == 'LIBRARIAN'
        
        # Admin
        response = authenticated_admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['role'] == 'ADMIN'


# ============================================
#    USER PROFILE ENDPOINT TESTS
# ============================================

@pytest.mark.django_db
class TestUserProfileView:
    """Test /profile/ endpoint."""
    
    def test_get_profile_authenticated(self, authenticated_member_client, member_user):
        """Test getting user profile when authenticated."""
        url = reverse('user_profile')
        response = authenticated_member_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert response.data['user']['id'] == member_user.id
        assert 'bio' in response.data
        assert 'address' in response.data
        assert 'avatar_url' in response.data
        assert 'birth_date' in response.data
    
    def test_get_profile_unauthenticated(self, api_client):
        """Test /profile/ endpoint requires authentication."""
        url = reverse('user_profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_profile_creates_if_not_exists(self, authenticated_member_client, member_user):
        """Test profile is created automatically if it doesn't exist."""
        # Ensure profile doesn't exist
        from users.models import UserProfile
        UserProfile.objects.filter(user=member_user).delete()
        
        url = reverse('user_profile')
        response = authenticated_member_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Profile should be created
        assert UserProfile.objects.filter(user=member_user).exists()
    
    def test_update_profile(self, authenticated_member_client, member_user):
        """Test updating user profile."""
        url = reverse('user_profile')
        data = {
            'bio': 'Updated bio',
            'address': '123 New Street',
            'avatar_url': 'https://example.com/new-avatar.jpg',
            'birth_date': '1990-05-15'
        }
        
        response = authenticated_member_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['bio'] == 'Updated bio'
        assert response.data['address'] == '123 New Street'
        assert response.data['avatar_url'] == 'https://example.com/new-avatar.jpg'
        assert response.data['birth_date'] == '1990-05-15'
        
        # Verify in database
        from users.models import UserProfile
        profile = UserProfile.objects.get(user=member_user)
        assert profile.bio == 'Updated bio'
        assert profile.address == '123 New Street'
    
    def test_update_profile_partial(self, authenticated_member_client, member_user):
        """Test partial update of user profile."""
        # Create profile with initial data
        from users.models import UserProfile
        profile = UserProfile.objects.create(
            user=member_user,
            bio='Initial bio',
            address='Initial address'
        )
        
        url = reverse('user_profile')
        data = {
            'bio': 'Updated bio only'
        }
        
        response = authenticated_member_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['bio'] == 'Updated bio only'
        # Address should remain unchanged
        assert response.data['address'] == 'Initial address'
    
    def test_update_profile_invalid_data(self, authenticated_member_client):
        """Test updating profile with invalid data fails."""
        url = reverse('user_profile')
        data = {
            'birth_date': 'invalid-date'
        }
        
        response = authenticated_member_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_profile_belongs_to_authenticated_user(self, authenticated_member_client, member_user, librarian_user):
        """Test user can only access their own profile."""
        # Create profile for librarian
        from users.models import UserProfile
        librarian_profile = UserProfile.objects.create(
            user=librarian_user,
            bio='Librarian bio'
        )
        
        # Member tries to access their own profile
        url = reverse('user_profile')
        response = authenticated_member_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['id'] == member_user.id
        # Should not see librarian's profile
        assert response.data['bio'] != 'Librarian bio'
    
    def test_profile_empty_fields(self, authenticated_member_client, member_user):
        """Test profile with empty/null fields."""
        from users.models import UserProfile
        profile = UserProfile.objects.create(user=member_user)
        
        url = reverse('user_profile')
        response = authenticated_member_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['bio'] is None or response.data['bio'] == ''
        assert response.data['address'] is None or response.data['address'] == ''
        assert response.data['avatar_url'] is None or response.data['avatar_url'] == ''
        assert response.data['birth_date'] is None
    
    def test_update_profile_clear_fields(self, authenticated_member_client, member_user):
        """Test clearing profile fields."""
        from users.models import UserProfile
        profile = UserProfile.objects.create(
            user=member_user,
            bio='Some bio',
            address='Some address'
        )
        
        url = reverse('user_profile')
        data = {
            'bio': '',
            'address': ''
        }
        
        response = authenticated_member_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        # Fields can be cleared
        assert response.data['bio'] == '' or response.data['bio'] is None

