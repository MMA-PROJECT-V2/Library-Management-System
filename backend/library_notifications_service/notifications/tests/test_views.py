from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from notifications.models import NotificationTemplate, Notification

class NotificationAPITest(APITestCase):
    def setUp(self):
        self.template = NotificationTemplate.objects.create(
            name="borrow_confirm",
            type="EMAIL",
            subject_template="You borrowed {title}",
            message_template="Hello, you borrowed {title} on {date}."
        )

    def test_send_from_template_creates_notification(self):
        url = reverse('notifications-send_from_template')
        data = {"template_id": self.template.id, "user_id": 10, "context": {"title": "Django for APIs", "date": "2025-12-09"}}
        resp = self.client.post('/api/notifications/send_from_template/', data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(user_id=10, subject__icontains="Django for APIs").exists())

    def test_stats_endpoint(self):
        # create a couple notifications
        Notification.objects.create(user_id=1, type="EMAIL", subject="A", message="m", status="SENT")
        Notification.objects.create(user_id=2, type="SMS", subject="B", message="m", status="PENDING")
        resp = self.client.get('/api/notifications/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('by_status', resp.data)
        self.assertIn('by_type', resp.data)