# notifications/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Notification, NotificationTemplate

User = get_user_model()


class NotificationModelTest(TestCase):
    def setUp(self):
        self.notification = Notification.objects.create(
            user_id=1,
            type='EMAIL',
            subject='Test Notification',
            message='This is a test notification.',
            status='PENDING'
        )

    def test_notification_creation(self):
        self.assertEqual(self.notification.subject, 'Test Notification')
        self.assertEqual(self.notification.message, 'This is a test notification.')
        self.assertEqual(self.notification.status, 'PENDING')
        self.assertEqual(str(self.notification), f"Notification {self.notification.id} to user 1 (PENDING)")


class NotificationAPITest(APITestCase):
    def setUp(self):
        # Create a test user for authentication
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Authenticate the client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.notification_data = {
            'user_id': 1,
            'type': 'EMAIL',
            'subject': 'Test Notification',
            'message': 'This is a test notification.',
        }
        
        self.notification = Notification.objects.create(**self.notification_data)

    def test_list_notifications(self):
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_notification(self):
        url = reverse('notification-list')
        data = {
            'user_id': 2,
            'type': 'SMS',
            'subject': 'New Notification',
            'message': 'Another test message.',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 2)

    def test_retrieve_notification(self):
        url = reverse('notification-detail', kwargs={'pk': self.notification.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subject'], 'Test Notification')

    def test_update_notification(self):
        url = reverse('notification-detail', kwargs={'pk': self.notification.id})
        data = {'subject': 'Updated Subject'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.subject, 'Updated Subject')

    def test_delete_notification(self):
        url = reverse('notification-detail', kwargs={'pk': self.notification.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Notification.objects.count(), 0)

    def test_user_notifications_endpoint(self):
        url = reverse('notification-user-notifications', kwargs={'user_id': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pending_notifications_endpoint(self):
        url = reverse('notification-pending')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stats_endpoint(self):
        url = reverse('notification-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_notifications', response.data)

    def test_health_endpoint(self):
        url = reverse('health_check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')


class NotificationTemplateAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.template_data = {
            'name': 'test_template',
            'type': 'EMAIL',
            'subject_template': 'Hello {{ user_name }}',
            'message_template': 'Your book {{ book_title }} is due on {{ due_date }}.',
        }
        
        self.template = NotificationTemplate.objects.create(**self.template_data)

    def test_list_templates(self):
        url = reverse('template-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_template(self):
        url = reverse('template-list')
        data = {
            'name': 'new_template',
            'type': 'SMS',
            'subject_template': 'Reminder: {{ book_title }}',
            'message_template': 'Please return {{ book_title }} by {{ due_date }}.',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NotificationTemplate.objects.count(), 2)

    def test_test_template_endpoint(self):
        url = reverse('template-test-template', kwargs={'pk': self.template.id})
        data = {
            'context': {
                'user_name': 'John',
                'book_title': 'Django Guide',
                'due_date': '2024-12-15'
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('subject', response.data)


class BulkOperationsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_bulk_create_notifications(self):
        url = reverse('notification-bulk-create')
        data = {
            'notifications': [
                {
                    'user_id': 1,
                    'type': 'EMAIL',
                    'subject': 'Bulk Test 1',
                    'message': 'Message 1'
                },
                {
                    'user_id': 2,
                    'type': 'SMS',
                    'subject': 'Bulk Test 2',
                    'message': 'Message 2'
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created'], 2)
        self.assertEqual(Notification.objects.count(), 2)


class ValidationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_invalid_user_id(self):
        url = reverse('notification-list')
        data = {
            'user_id': -1,
            'type': 'EMAIL',
            'subject': 'Test',
            'message': 'Test message'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_subject(self):
        url = reverse('notification-list')
        data = {
            'user_id': 1,
            'type': 'EMAIL',
            'subject': '',
            'message': 'Test message'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_type(self):
        url = reverse('notification-list')
        data = {
            'user_id': 1,
            'type': 'INVALID',
            'subject': 'Test',
            'message': 'Test message'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)