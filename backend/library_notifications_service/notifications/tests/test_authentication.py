from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import AuthenticationFailed
from unittest.mock import patch, MagicMock
from notifications.authentication import JWTAuthentication, RemoteUser

class AuthenticationTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.auth = JWTAuthentication()

    def test_authenticate_no_header(self):
        request = self.factory.get('/')
        user_auth = self.auth.authenticate(request)
        self.assertIsNone(user_auth)

    def test_authenticate_invalid_header_format(self):
        request = self.factory.get('/', HTTP_AUTHORIZATION='InvalidFormat')
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_authenticate_invalid_prefix(self):
        request = self.factory.get('/', HTTP_AUTHORIZATION='Token 12345')
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    @patch('notifications.authentication.requests.post')
    def test_authenticate_success(self, mock_post):
        # Mock successful validation
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'valid': True,
            'user': {
                'id': 1,
                'email': 'test@example.com',
                'role': 'MEMBER',
                'permissions': []
            }
        }
        mock_post.return_value = mock_response

        request = self.factory.get('/', HTTP_AUTHORIZATION='Bearer validtoken')
        user, token = self.auth.authenticate(request)
        
        self.assertIsInstance(user, RemoteUser)
        self.assertEqual(user.email, 'test@example.com')
        self.assertIsNone(token)

    @patch('notifications.authentication.requests.post')
    def test_authenticate_invalid_token(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'valid': False, 'error': 'Invalid'}
        mock_post.return_value = mock_response

        request = self.factory.get('/', HTTP_AUTHORIZATION='Bearer invalidtoken')
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    @patch('notifications.authentication.requests.post')
    def test_authenticate_service_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        request = self.factory.get('/', HTTP_AUTHORIZATION='Bearer token')
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)


class RemoteUserTest(TestCase):
    def setUp(self):
        self.user_data = {
            'id': 1,
            'email': 'user@example.com',
            'role': 'LIBRARIAN',
            'permissions': ['can_view_notifications']
        }
        self.user = RemoteUser(self.user_data)

    def test_properties(self):
        self.assertTrue(self.user.is_authenticated)
        self.assertFalse(self.user.is_anonymous)
        self.assertEqual(str(self.user), "user@example.com (LIBRARIAN)")

    def test_roles(self):
        self.assertTrue(self.user.is_librarian())
        self.assertFalse(self.user.is_member())
        self.assertFalse(self.user.is_admin())

    def test_permissions(self):
        self.assertTrue(self.user.has_permission('can_view_notifications'))
        self.assertFalse(self.user.has_permission('can_delete'))
        self.assertTrue(self.user.has_any_permission(['can_delete', 'can_view_notifications']))
        self.assertFalse(self.user.has_all_permissions(['can_delete', 'can_view_notifications']))
