"""
Tests for service client integrations
"""
import pytest
from loans.views import UserServiceClient, BookServiceClient
from unittest.mock import Mock, patch
import requests


class TestUserServiceClient:
    """Test User Service client"""
    
    @patch('requests.get')
    def test_get_user_success(self, mock_get):
        """Test successful user retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com'
        }
        mock_get.return_value = mock_response
        
        client = UserServiceClient()
        user = client.get_user(1)
        assert user['id'] == 1
        assert user['username'] == 'testuser'
    
    @patch('requests.get')
    def test_get_user_not_found(self, mock_get):
        """Test user not found"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        client = UserServiceClient()
        user = client.get_user(999)
        assert user is None
    
    @patch('requests.get')
    def test_get_user_service_error(self, mock_get):
        """Test handling service errors"""
        mock_get.side_effect = requests.RequestException("Service unavailable")
        
        client = UserServiceClient()
        user = client.get_user(1)
        assert user is None


class TestBookServiceClient:
    """Test Book Service client"""
    
    @patch('requests.get')
    def test_get_book_success(self, mock_get):
        """Test successful book retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 1,
            'title': 'Test Book',
            'author': 'Test Author'
        }
        mock_get.return_value = mock_response
        
        client = BookServiceClient()
        book = client.get_book(1)
        assert book['id'] == 1
        assert book['title'] == 'Test Book'
    
    @patch('requests.post')
    def test_borrow_book_success(self, mock_post):
        """Test successful book borrowing"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        client = BookServiceClient()
        result = client.borrow_book(1, 'token123')
        assert result is True
    
    @patch('requests.post')
    def test_borrow_book_out_of_stock(self, mock_post):
        """Test borrowing when book is out of stock"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        client = BookServiceClient()
        result = client.borrow_book(1, 'token123')
        assert result is False
