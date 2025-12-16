"""
Unit tests for views helper functions and service clients.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from loans.views import (
    send_notification_from_template, get_template_id,
    UserServiceClient, BookServiceClient, health_check
)


class TestHelperFunctions:
    """Tests for view helper functions."""
    
    def test_get_template_id_loan_created(self):
        """Test template ID for loan_created."""
        assert get_template_id('loan_created') == 1
    
    def test_get_template_id_loan_returned_ontime(self):
        """Test template ID for loan_returned_ontime."""
        assert get_template_id('loan_returned_ontime') == 2
    
    def test_get_template_id_loan_returned_late(self):
        """Test template ID for loan_returned_late."""
        assert get_template_id('loan_returned_late') == 3
    
    def test_get_template_id_loan_renewed(self):
        """Test template ID for loan_renewed."""
        assert get_template_id('loan_renewed') == 4
    
    def test_get_template_id_user_registered(self):
        """Test template ID for user_registered."""
        assert get_template_id('user_registered') == 5
    
    def test_get_template_id_unknown(self):
        """Test template ID for unknown template returns default."""
        assert get_template_id('unknown_template') == 1
    
    @patch('loans.views.requests.post')
    def test_send_notification_success(self, mock_post):
        """Test successful notification sending."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        result = send_notification_from_template(
            template_name='loan_created',
            user_id=1,
            context={'book_title': 'Test Book'},
            token='test_token'
        )
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('loans.views.requests.post')
    def test_send_notification_with_bearer_prefix(self, mock_post):
        """Test notification with Bearer prefix in token."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        result = send_notification_from_template(
            template_name='loan_created',
            user_id=1,
            context={},
            token='Bearer test_token'
        )
        
        assert result is True
    
    @patch('loans.views.requests.post')
    def test_send_notification_failure(self, mock_post):
        """Test notification failure."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal server error'
        mock_post.return_value = mock_response
        
        result = send_notification_from_template(
            template_name='loan_created',
            user_id=1,
            context={}
        )
        
        assert result is False
    
    @patch('loans.views.requests.post')
    def test_send_notification_exception(self, mock_post):
        """Test notification when exception occurs."""
        mock_post.side_effect = Exception('Connection error')
        
        result = send_notification_from_template(
            template_name='loan_created',
            user_id=1,
            context={}
        )
        
        assert result is False
    
    @patch('loans.views.requests.post')
    def test_send_notification_without_token(self, mock_post):
        """Test notification without token."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        result = send_notification_from_template(
            template_name='loan_created',
            user_id=1,
            context={}
        )
        
        assert result is True


class TestUserServiceClient:
    """Tests for UserServiceClient."""
    
    @pytest.fixture
    def client(self):
        return UserServiceClient()
    
    @patch('loans.views.requests.get')
    def test_get_user_success(self, mock_get, client):
        """Test successful user fetch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com'
        }
        mock_get.return_value = mock_response
        
        result = client.get_user(1)
        
        assert result is not None
        assert result['id'] == 1
        assert result['username'] == 'testuser'
    
    @patch('loans.views.requests.get')
    def test_get_user_not_found(self, mock_get, client):
        """Test user not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = client.get_user(999)
        
        assert result is None
    
    @patch('loans.views.requests.get')
    def test_get_user_error(self, mock_get, client):
        """Test user service error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal error'
        mock_get.return_value = mock_response
        
        result = client.get_user(1)
        
        assert result is None
    
    @patch('loans.views.requests.get')
    def test_get_user_timeout(self, mock_get, client):
        """Test timeout when fetching user."""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        result = client.get_user(1)
        
        assert result is None
    
    @patch('loans.views.requests.get')
    def test_get_user_connection_error(self, mock_get, client):
        """Test connection error when fetching user."""
        mock_get.side_effect = requests.exceptions.RequestException()
        
        result = client.get_user(1)
        
        assert result is None
    
    @patch('loans.views.requests.get')
    def test_is_user_active_true(self, mock_get, client):
        """Test user is active."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 1, 'is_active': True}
        mock_get.return_value = mock_response
        
        result = client.is_user_active(1)
        
        assert result is True
    
    @patch('loans.views.requests.get')
    def test_is_user_active_false(self, mock_get, client):
        """Test user is not active."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 1, 'is_active': False}
        mock_get.return_value = mock_response
        
        result = client.is_user_active(1)
        
        assert result is False
    
    @patch('loans.views.requests.get')
    def test_is_user_active_user_not_found(self, mock_get, client):
        """Test is_user_active for non-existent user."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = client.is_user_active(999)
        
        assert result is False
    
    @patch('loans.views.requests.get')
    def test_get_user_email(self, mock_get, client):
        """Test get user email."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 1, 'email': 'test@example.com'}
        mock_get.return_value = mock_response
        
        result = client.get_user_email(1)
        
        assert result == 'test@example.com'
    
    @patch('loans.views.requests.get')
    def test_get_user_email_not_found(self, mock_get, client):
        """Test get email for non-existent user."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = client.get_user_email(999)
        
        assert result is None


class TestBookServiceClient:
    """Tests for BookServiceClient."""
    
    @pytest.fixture
    def client(self):
        return BookServiceClient()
    
    @patch('loans.views.requests.get')
    def test_get_book_success(self, mock_get, client):
        """Test successful book fetch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 1,
            'title': 'Test Book',
            'author': 'Test Author',
            'available_copies': 5
        }
        mock_get.return_value = mock_response
        
        result = client.get_book(1)
        
        assert result is not None
        assert result['title'] == 'Test Book'
        assert result['available_copies'] == 5
    
    @patch('loans.views.requests.get')
    def test_get_book_not_found(self, mock_get, client):
        """Test book not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = client.get_book(999)
        
        assert result is None
    
    @patch('loans.views.requests.get')
    def test_get_book_error(self, mock_get, client):
        """Test book service error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = client.get_book(1)
        
        assert result is None
    
    @patch('loans.views.requests.get')
    def test_get_book_timeout(self, mock_get, client):
        """Test timeout when fetching book."""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        result = client.get_book(1)
        
        assert result is None
    
    @patch('loans.views.requests.get')
    def test_get_book_connection_error(self, mock_get, client):
        """Test connection error when fetching book."""
        mock_get.side_effect = requests.exceptions.RequestException()
        
        result = client.get_book(1)
        
        assert result is None
    
    @patch('loans.views.requests.get')
    def test_check_availability_true(self, mock_get, client):
        """Test book is available."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'available_copies': 5}
        mock_get.return_value = mock_response
        
        result = client.check_availability(1)
        
        assert result is True
    
    @patch('loans.views.requests.get')
    def test_check_availability_false(self, mock_get, client):
        """Test book is not available."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'available_copies': 0}
        mock_get.return_value = mock_response
        
        result = client.check_availability(1)
        
        assert result is False
    
    @patch('loans.views.requests.get')
    def test_check_availability_book_not_found(self, mock_get, client):
        """Test availability for non-existent book."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = client.check_availability(999)
        
        assert result is False
    
    @patch('loans.views.requests.get')
    def test_get_available_copies(self, mock_get, client):
        """Test get available copies."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'available_copies': 3}
        mock_get.return_value = mock_response
        
        result = client.get_available_copies(1)
        
        assert result == 3
    
    @patch('loans.views.requests.get')
    def test_get_available_copies_book_not_found(self, mock_get, client):
        """Test get available copies for non-existent book."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = client.get_available_copies(999)
        
        assert result == 0
    
    @patch('loans.views.requests.post')
    def test_decrement_stock_success(self, mock_post, client):
        """Test successful stock decrement."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = client.decrement_stock(1, token='test_token')
        
        assert result is True
    
    @patch('loans.views.requests.post')
    def test_decrement_stock_failure(self, mock_post, client):
        """Test failed stock decrement."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        result = client.decrement_stock(1)
        
        assert result is False
    
    @patch('loans.views.requests.post')
    def test_decrement_stock_exception(self, mock_post, client):
        """Test stock decrement with exception."""
        mock_post.side_effect = requests.exceptions.RequestException()
        
        result = client.decrement_stock(1)
        
        assert result is False
    
    @patch('loans.views.requests.post')
    def test_increment_stock_success(self, mock_post, client):
        """Test successful stock increment."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = client.increment_stock(1, token='test_token')
        
        assert result is True
    
    @patch('loans.views.requests.post')
    def test_increment_stock_failure(self, mock_post, client):
        """Test failed stock increment."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        result = client.increment_stock(1)
        
        assert result is False
    
    @patch('loans.views.requests.post')
    def test_increment_stock_exception(self, mock_post, client):
        """Test stock increment with exception."""
        mock_post.side_effect = requests.exceptions.RequestException()
        
        result = client.increment_stock(1)
        
        assert result is False


class TestHealthCheck:
    """Tests for health check endpoint."""
    
    def test_health_check(self, db):
        """Test health check returns healthy status."""
        from rest_framework.test import APIRequestFactory
        
        factory = APIRequestFactory()
        request = factory.get('/api/health/')
        
        response = health_check(request)
        
        assert response.status_code == 200
        assert response.data['status'] == 'healthy'
        assert response.data['service'] == 'loans'
        assert 'timestamp' in response.data
