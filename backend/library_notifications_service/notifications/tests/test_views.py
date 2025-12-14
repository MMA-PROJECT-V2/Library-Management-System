from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from notifications.models import NotificationTemplate, Notification
from unittest.mock import patch

User = get_user_model()

class NotificationAPITest(APITestCase):
    def setUp(self):
        # Patch User methods expected by permissions
        self.patcher_perm = patch.object(User, 'has_permission', create=True, return_value=True)
        self.patcher_lib = patch.object(User, 'is_librarian', create=True, return_value=False)
        self.patcher_admin = patch.object(User, 'is_admin', create=True, return_value=False)
        
        self.mock_has_perm = self.patcher_perm.start()
        self.mock_is_lib = self.patcher_lib.start()
        self.mock_is_admin = self.patcher_admin.start()
        
        self.addCleanup(self.patcher_perm.stop)
        self.addCleanup(self.patcher_lib.stop)
        self.addCleanup(self.patcher_admin.stop)

        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)
        
        self.template = NotificationTemplate.objects.create(
            name="borrow_confirm",
            type="EMAIL",
            subject_template="You borrowed {{ title }}",
            message_template="Hello, you borrowed {{ title }} on {{ date }}."
        )
        
        # Create a notification for this user
        self.notification = Notification.objects.create(
            user_id=self.user.id,
            type='EMAIL',
            subject='Test',
            message='Test message',
            status='PENDING'
        )

    def test_list_notifications(self):
        """Test listing notifications for the authenticated user"""
        url = reverse('user-notifications')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch('notifications.views.send_notification_email.delay')
    def test_create_notification(self, mock_email_task):
        """Test creating a notification via API"""
        url = reverse('create-notification')
        data = {
            'user_id': self.user.id,
            'type': 'EMAIL',
            'subject': 'New',
            'message': 'Message'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(mock_email_task.called)

    @patch('notifications.views.send_notification_email.delay')
    def test_send_from_template_creates_notification(self, mock_email_task):
        url = reverse('send-from-template')
        data = {
            "template_id": self.template.id, 
            "user_id": self.user.id, 
            "context": {"title": "Django for APIs", "date": "2025-12-09"}
        }
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(user_id=self.user.id, subject__icontains="Django for APIs").exists())
        self.assertTrue(mock_email_task.called)

    def test_stats_endpoint_admin_only(self):
        """Test that normal users cannot access stats"""
        # Default mocks are False
        self.mock_is_admin.return_value = False 
        self.mock_is_lib.return_value = False
        
        url = reverse('notification-stats')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_stats_endpoint_success(self):
        """Test stats endpoint for admin"""
        admin = User.objects.create_superuser(username='admin', password='password')
        self.client.force_authenticate(user=admin)
        
        # Configure mocks for this test
        self.mock_is_admin.return_value = True
        
        # create a couple notifications
        Notification.objects.create(user_id=1, type="EMAIL", subject="A", message="m", status="SENT")
        Notification.objects.create(user_id=2, type="SMS", subject="B", message="m", status="PENDING")
        
        url = reverse('notification-stats')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('by_status', resp.data)
        self.assertIn('by_type', resp.data)

    def test_health_check(self):
        url = reverse('health-check')
        # Logout to test public access
        self.client.logout()
        resp = self.client.get(url)
        
        if not hasattr(resp, 'data'):
             # If JsonResponse, parse content
             import json
             data = json.loads(resp.content)
             self.assertEqual(data['status'], 'healthy')
        else:
             self.assertEqual(resp.data['status'], 'healthy')
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- New Tests for Full Coverage ---

    @patch('notifications.views.send_notification_email.delay')
    def test_create_notification_exception(self, mock_delay):
        """Test exception handling during creation"""
        mock_delay.side_effect = Exception("Queue Error")
        
        data = {
            'user_id': self.user.id,
            'type': 'EMAIL',
            'subject': 'Test',
            'message': 'Test'
        }
        url = reverse('create-notification')
        resp = self.client.post(url, data, format='json')
        
        # Should still succeed (created) but log error for sending
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(subject='Test').exists())

    def test_send_from_template_inactive(self):
        """Test sending from inactive template"""
        self.template.is_active = False
        self.template.save()
        
        data = {
            'template_id': self.template.id,
            'user_id': self.user.id,
            'context': {'name': 'User'}
        }
        url = reverse('send-from-template')
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_from_template_render_error(self):
        """Test template rendering error"""
        self.template.subject_template = "{% if %}" # Invalid tag syntax
        self.template.save()
        
        data = {
            'template_id': self.template.id,
            'user_id': self.user.id,
            'context': {'name': 'User'}
        }
        url = reverse('send-from-template')
        
        # Patch the task just in case it succeeds, to avoid network call
        with patch('notifications.views.send_notification_email.delay') as mock_task:
            resp = self.client.post(url, data, format='json')
            
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_all_notifications_admin(self):
        """Test admin list all endpoint"""
        Notification.objects.create(user_id=99, type='EMAIL', subject='A', message='A')
        
        # As Admin
        self.mock_is_admin.return_value = True
        
        url = reverse('list-all-notifications')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # We expect at least the one we made + initial
        self.assertTrue(len(resp.data['results']) >= 2)

    def test_get_user_notifications_by_id_permission(self):
        """Test accessing another user's notifications"""
        other_user_id = self.user.id + 1
        
        # As regular user (is_admin=False default), try to see other's
        self.mock_is_admin.return_value = False
        self.mock_has_perm.return_value = False
        
        url = reverse('user-notifications-by-id', args=[other_user_id])
        resp = self.client.get(url)
        self.assertIn(resp.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        # As Admin (via has_permission check)
        # The view checks: user.has_permission('can_view_all_notifications')
        self.mock_has_perm.side_effect = lambda p: p == 'can_view_all_notifications'
        
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        self.mock_has_perm.side_effect = None
        self.mock_has_perm.return_value = True

    def test_get_pending_notifications(self):
        """Test pending notifications endpoint"""
        Notification.objects.create(user_id=1, type='EMAIL', status='PENDING', subject='Pending', message='M')
        
        # As Admin
        self.mock_is_admin.return_value = True
        
        url = reverse('pending-notifications')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        results = resp.data['results']
        for n in results:
            self.assertEqual(n['status'], 'PENDING')