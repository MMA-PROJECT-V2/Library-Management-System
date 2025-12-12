"""
Unit tests for Notification models
"""
import pytest
from django.utils import timezone
from notifications.models import Notification, NotificationTemplate, NotificationLog


@pytest.mark.django_db
class TestNotificationModel:
    """Test Notification model"""
    
    def test_create_notification(self, user):
        """Test creating a notification"""
        notif = Notification.objects.create(
            user_id=user.id,
            type='EMAIL',
            subject='Test',
            message='Test message',
            status='PENDING'
        )
        assert notif.id is not None
        assert notif.status == 'PENDING'
        assert notif.sent_at is None
    
    def test_notification_str(self, notification):
        """Test string representation"""
        expected = f"Notification {notification.id} to user {notification.user_id} ({notification.status})"
        assert str(notification) == expected
    
    def test_notification_ordering(self, user):
        """Test notifications are ordered by created_at descending"""
        notif1 = Notification.objects.create(
            user_id=user.id,
            type='EMAIL',
            subject='First',
            message='First message'
        )
        notif2 = Notification.objects.create(
            user_id=user.id,
            type='EMAIL',
            subject='Second',
            message='Second message'
        )
        notifications = list(Notification.objects.all())
        assert notifications[0] == notif2
        assert notifications[1] == notif1
    
    def test_notification_type_choices(self, user):
        """Test notification type validation"""
        notif = Notification.objects.create(
            user_id=user.id,
            type='EMAIL',
            subject='Test',
            message='Test'
        )
        assert notif.type in ['EMAIL', 'SMS']
    
    def test_notification_status_choices(self, notification):
        """Test notification status choices"""
        assert notification.status in ['PENDING', 'SENT', 'FAILED']


@pytest.mark.django_db
class TestNotificationTemplateModel:
    """Test NotificationTemplate model"""
    
    def test_create_template(self):
        """Test creating a notification template"""
        template = NotificationTemplate.objects.create(
            name='welcome_email',
            type='EMAIL',
            subject_template='Welcome {{ name }}!',
            message_template='Hello {{ name }}, welcome to our service!',
            description='Welcome email template'
        )
        assert template.id is not None
        assert template.is_active is True
    
    def test_template_str(self, notification_template):
        """Test string representation"""
        expected = f"Template {notification_template.name} ({notification_template.type})"
        assert str(notification_template) == expected
    
    def test_template_unique_name(self, notification_template):
        """Test template name uniqueness"""
        with pytest.raises(Exception):  # IntegrityError
            NotificationTemplate.objects.create(
                name=notification_template.name,
                type='EMAIL',
                subject_template='Test',
                message_template='Test'
            )
    
    def test_template_deactivation(self, notification_template):
        """Test deactivating a template"""
        notification_template.is_active = False
        notification_template.save()
        assert notification_template.is_active is False


@pytest.mark.django_db
class TestNotificationLogModel:
    """Test NotificationLog model"""
    
    def test_create_log(self, notification):
        """Test creating a notification log"""
        log = NotificationLog.objects.create(
            notification=notification,
            status='SENT',
            detail='Email sent successfully'
        )
        assert log.id is not None
        assert log.notification == notification
    
    def test_log_str(self, notification):
        """Test string representation"""
        log = NotificationLog.objects.create(
            notification=notification,
            status='SENT',
            detail='Test'
        )
        expected = f"Log for notif {notification.id} - SENT"
        assert str(log) == expected
    
    def test_log_cascade_delete(self, notification):
        """Test logs are deleted when notification is deleted"""
        log = NotificationLog.objects.create(
            notification=notification,
            status='SENT',
            detail='Test'
        )
        notification_id = notification.id
        notification.delete()
        assert not NotificationLog.objects.filter(notification_id=notification_id).exists()
