"""
Pytest configuration and shared fixtures for Loans Service tests
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from loans.models import Loan
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()


@pytest.fixture
def api_client():
    """Return API client for making requests"""
    return APIClient()


@pytest.fixture
def user(db):
    """Create a regular user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def librarian(db):
    """Create a librarian user (staff)"""
    return User.objects.create_user(
        username='librarian',
        email='librarian@example.com',
        password='libpass123',
        first_name='Lib',
        last_name='Rarian',
        is_staff=True
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Return authenticated API client"""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return api_client


@pytest.fixture
def librarian_client(api_client, librarian):
    """Return authenticated librarian API client"""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(librarian)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return api_client


@pytest.fixture
def loan(db, user):
    """Create a sample loan"""
    return Loan.objects.create(
        user_id=user.id,
        book_id=1,
        loan_date=timezone.now().date(),
        due_date=(timezone.now() + timedelta(days=14)).date(),
        status='ACTIVE'
    )


@pytest.fixture
def overdue_loan(db, user):
    """Create an overdue loan"""
    return Loan.objects.create(
        user_id=user.id,
        book_id=2,
        loan_date=(timezone.now() - timedelta(days=20)).date(),
        due_date=(timezone.now() - timedelta(days=6)).date(),
        status='ACTIVE'
    )


@pytest.fixture
def returned_loan(db, user):
    """Create a returned loan"""
    return Loan.objects.create(
        user_id=user.id,
        book_id=3,
        loan_date=(timezone.now() - timedelta(days=10)).date(),
        due_date=(timezone.now() + timedelta(days=4)).date(),
        return_date=timezone.now().date(),
        status='RETURNED'
    )


@pytest.fixture
def mock_user_service(mocker):
    """Mock User Service client"""
    mock = mocker.patch('loans.views.UserServiceClient')
    instance = mock.return_value
    instance.get_user.return_value = {
        'id': 1,
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
    instance.get_user_email.return_value = 'test@example.com'
    instance.validate_user.return_value = True
    return instance


@pytest.fixture
def mock_book_service(mocker):
    """Mock Book Service client"""
    mock = mocker.patch('loans.views.BookServiceClient')
    instance = mock.return_value
    instance.get_book.return_value = {
        'id': 1,
        'title': 'Test Book',
        'author': 'Test Author',
        'isbn': '1234567890',
        'category': 'FICTION',
        'available_copies': 5
    }
    instance.borrow_book.return_value = True
    instance.return_book.return_value = True
    return instance


@pytest.fixture
def mock_notification_service(mocker):
    """Mock notification sending"""
    return mocker.patch('loans.views.send_notification_from_template', return_value=True)


@pytest.fixture
def mock_all_services(mock_user_service, mock_book_service, mock_notification_service):
    """Mock all external services"""
    return {
        'user': mock_user_service,
        'book': mock_book_service,
        'notification': mock_notification_service
    }
