"""
Pytest configuration and shared fixtures for Notifications Service tests
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from notifications.models import Notification, NotificationTemplate, NotificationLog

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
        password='testpass123'
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
def admin_client(api_client, admin_user):
    """Return authenticated admin API client"""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return api_client


@pytest.fixture
def notification(db, user):
    """Create a sample notification"""
    return Notification.objects.create(
        user_id=user.id,
        type='EMAIL',
        subject='Test Notification',
        message='This is a test notification',
        status='PENDING'
    )


@pytest.fixture
def sent_notification(db, user):
    """Create a sent notification"""
    from django.utils import timezone
    return Notification.objects.create(
        user_id=user.id,
        type='EMAIL',
        subject='Sent Notification',
        message='This notification was sent',
        status='SENT',
        sent_at=timezone.now()
    )


@pytest.fixture
def notification_template(db):
    """Create a notification template"""
    return NotificationTemplate.objects.create(
        name='test_template',
        type='EMAIL',
        subject_template='Test Subject: {{ title }}',
        message_template='Hello {{ name }}, this is a test message about {{ title }}.',
        description='Test template',
        is_active=True
    )


@pytest.fixture
def mock_send_mail(mocker):
    """Mock Django send_mail function"""
    return mocker.patch('django.core.mail.send_mail')


@pytest.fixture
def mock_user_service(mocker):
    """Mock user service calls"""
    mock = mocker.patch('notifications.tasks.get_user_email')
    mock.return_value = 'test@example.com'
    return mock
