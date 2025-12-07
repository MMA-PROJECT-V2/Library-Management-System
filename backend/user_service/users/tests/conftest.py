"""
Pytest configuration and fixtures for user service tests.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Group, Permission, UserProfile

User = get_user_model()


# ============================================
#    PERMISSION FIXTURES
# ============================================

@pytest.fixture
def permissions(db):
    """Create all default permissions."""
    perms = {
        'can_view_books': Permission.objects.create(
            code='can_view_books',
            name='Can View Books',
            category='BOOKS'
        ),
        'can_add_book': Permission.objects.create(
            code='can_add_book',
            name='Can Add Book',
            category='BOOKS'
        ),
        'can_edit_book': Permission.objects.create(
            code='can_edit_book',
            name='Can Edit Book',
            category='BOOKS'
        ),
        'can_delete_book': Permission.objects.create(
            code='can_delete_book',
            name='Can Delete Book',
            category='BOOKS'
        ),
        'can_borrow_book': Permission.objects.create(
            code='can_borrow_book',
            name='Can Borrow Book',
            category='LOANS'
        ),
        'can_return_book': Permission.objects.create(
            code='can_return_book',
            name='Can Return Book',
            category='LOANS'
        ),
        'can_view_loans': Permission.objects.create(
            code='can_view_loans',
            name='Can View Loans',
            category='LOANS'
        ),
        'can_view_all_loans': Permission.objects.create(
            code='can_view_all_loans',
            name='Can View All Loans',
            category='LOANS'
        ),
        'can_manage_loans': Permission.objects.create(
            code='can_manage_loans',
            name='Can Manage Loans',
            category='LOANS'
        ),
    }
    return perms


# ============================================
#    GROUP FIXTURES
# ============================================

@pytest.fixture
def member_group(db, permissions):
    """Create MEMBER group with appropriate permissions."""
    group = Group.objects.create(
        name='MEMBER',
        description='Library members',
        is_default=True
    )
    group.permissions.set([
        permissions['can_view_books'],
        permissions['can_borrow_book'],
        permissions['can_return_book'],
        permissions['can_view_loans'],
    ])
    return group


@pytest.fixture
def librarian_group(db, permissions):
    """Create LIBRARIAN group with appropriate permissions."""
    group = Group.objects.create(
        name='LIBRARIAN',
        description='Library staff'
    )
    group.permissions.set([
        permissions['can_view_books'],
        permissions['can_add_book'],
        permissions['can_edit_book'],
        permissions['can_delete_book'],
        permissions['can_view_all_loans'],
        permissions['can_manage_loans'],
    ])
    return group


@pytest.fixture
def admin_group(db, permissions):
    """Create ADMIN group with all permissions."""
    group = Group.objects.create(
        name='ADMIN',
        description='System administrators'
    )
    group.permissions.set(Permission.objects.all())
    return group


# ============================================
#    USER FIXTURES
# ============================================

@pytest.fixture
def member_user(db, member_group):
    """Create a member user."""
    user = User.objects.create_user(
        email='member@library.com',
        password='testpass123',
        role='MEMBER',
        first_name='Member',
        last_name='User'
    )
    user.custom_groups.add(member_group)
    return user


@pytest.fixture
def librarian_user(db, librarian_group):
    """Create a librarian user."""
    user = User.objects.create_user(
        email='librarian@library.com',
        password='testpass123',
        role='LIBRARIAN',
        first_name='Librarian',
        last_name='User'
    )
    user.custom_groups.add(librarian_group)
    return user


@pytest.fixture
def admin_user(db, admin_group):
    """Create an admin user."""
    user = User.objects.create_superuser(
        email='admin@library.com',
        password='testpass123',
        first_name='Admin',
        last_name='User'
    )
    user.custom_groups.add(admin_group)
    return user


# ============================================
#    TOKEN FIXTURES
# ============================================

@pytest.fixture
def member_token(member_user):
    """Generate JWT token for member user."""
    refresh = RefreshToken.for_user(member_user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }


@pytest.fixture
def librarian_token(librarian_user):
    """Generate JWT token for librarian user."""
    refresh = RefreshToken.for_user(librarian_user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }


@pytest.fixture
def admin_token(admin_user):
    """Generate JWT token for admin user."""
    refresh = RefreshToken.for_user(admin_user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }


# ============================================
#    API CLIENT FIXTURES
# ============================================

@pytest.fixture
def api_client():
    """Return a DRF API client."""
    return APIClient()


@pytest.fixture
def authenticated_member_client(api_client, member_token):
    """Return API client authenticated as member."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {member_token['access']}")
    return api_client


@pytest.fixture
def authenticated_librarian_client(api_client, librarian_token):
    """Return API client authenticated as librarian."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {librarian_token['access']}")
    return api_client


@pytest.fixture
def authenticated_admin_client(api_client, admin_token):
    """Return API client authenticated as admin."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token['access']}")
    return api_client


# ============================================
#    HELPER FIXTURES
# ============================================

@pytest.fixture
def user_factory(db):
    """Factory to create users with custom attributes."""
    def create_user(**kwargs):
        defaults = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'role': 'MEMBER'
        }
        defaults.update(kwargs)
        password = defaults.pop('password')
        user = User.objects.create_user(password=password, **defaults)
        return user
    return create_user