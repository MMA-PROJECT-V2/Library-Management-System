from django.test import TestCase
from notifications.models import Notification, NotificationTemplate
from notifications.serializers import (
    NotificationSerializer,
    NotificationTemplateSerializer,
    SendFromTemplateSerializer
)

class TestNotificationSerializer(TestCase):
    def test_valid_notification_serializer(self):
        data = {
            "user_id": 1,
            "type": "EMAIL",
            "subject": "Test Subject",
            "message": "Test Message",
            "status": "PENDING"
        }
        serializer = NotificationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
    def test_invalid_user_id(self):
        data = {
            "user_id": -1,
            "type": "EMAIL",
            "subject": "Test",
            "message": "Test"
        }
        serializer = NotificationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("user_id", serializer.errors)

    def test_invalid_type(self):
        data = {
            "user_id": 1,
            "type": "INVALID_TYPE",
            "subject": "Test",
            "message": "Test"
        }
        serializer = NotificationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("type", serializer.errors)

    def test_empty_message(self):
        data = {
            "user_id": 1,
            "type": "EMAIL",
            "subject": "Test",
            "message": ""
        }
        serializer = NotificationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("message", serializer.errors)


class TestNotificationTemplateSerializer(TestCase):
    def test_valid_template_serializer(self):
        data = {
            "name": "test_template",
            "type": "EMAIL",
            "subject_template": "Subject {{ name }}",
            "message_template": "Message {{ content }}",
            "description": "Test Description"
        }
        serializer = NotificationTemplateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_empty_name(self):
        data = {
            "name": "",
            "type": "EMAIL",
            "subject_template": "S",
            "message_template": "M"
        }
        serializer = NotificationTemplateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)


class TestSendFromTemplateSerializer(TestCase):
    def setUp(self):
        self.template = NotificationTemplate.objects.create(
            name="existing_template",
            type="EMAIL",
            subject_template="S",
            message_template="M"
        )

    def test_valid_send_serializer(self):
        data = {
            "template_id": self.template.id,
            "user_id": 1,
            "context": {"key": "value"}
        }
        serializer = SendFromTemplateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_nonexistent_template(self):
        data = {
            "template_id": 9999,
            "user_id": 1
        }
        serializer = SendFromTemplateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("template_id", serializer.errors)
