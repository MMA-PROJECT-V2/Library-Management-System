"""
Integration tests for Loan views and endpoints
"""
import pytest
from django.urls import reverse
from rest_framework import status
from loans.models import Loan
from datetime import timedelta
from django.utils import timezone


@pytest.mark.django_db
class TestLoanCreation:
    """Test loan creation endpoint"""
    
    url = '/api/loans/'
    
    def test_create_loan_success(self, authenticated_client, mock_all_services, user):
        """Test successful loan creation"""
        data = {
            'user_id': user.id,
            'book_id': 1,
            'notes': 'Test loan'
        }
        response = authenticated_client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'loan' in response.data
        assert response.data['loan']['user_id'] == user.id
        assert response.data['loan']['book_id'] == 1
        
        # Verify loan was created in database
        assert Loan.objects.filter(user_id=user.id, book_id=1).exists()
    
    def test_create_loan_notification_sent(self, authenticated_client, mock_all_services, user):
        """Test notification is sent on loan creation"""
        data = {'user_id': user.id, 'book_id': 1}
        response = authenticated_client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify notification was called
        mock_all_services['notification'].assert_called_once()
    
    def test_create_loan_unauthenticated(self, api_client):
        """Test loan creation without authentication"""
        data = {'user_id': 1, 'book_id': 1}
        response = api_client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_loan_invalid_book(self, authenticated_client, mock_book_service, user):
        """Test loan creation with invalid book"""
        mock_book_service.get_book.return_value = None
        data = {'user_id': user.id, 'book_id': 999}
        response = authenticated_client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoanReturn:
    """Test loan return endpoint"""
    
    def test_return_loan_success(self, authenticated_client, loan, mock_all_services):
        """Test successful loan return"""
        url = f'/api/loans/{loan.id}/return/'
        response = authenticated_client.put(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify loan was returned
        loan.refresh_from_db()
        assert loan.status == 'RETURNED'
        assert loan.return_date is not None
    
    def test_return_loan_with_fine(self, authenticated_client, overdue_loan, mock_all_services):
        """Test returning overdue loan with fine"""
        url = f'/api/loans/{overdue_loan.id}/return/'
        response = authenticated_client.put(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'fine' in response.data
        assert response.data['fine']['amount'] > 0
    
    def test_return_loan_notification(self, authenticated_client, loan, mock_all_services):
        """Test notification sent on return"""
        url = f'/api/loans/{loan.id}/return/'
        response = authenticated_client.put(url)
        assert response.status_code == status.HTTP_200_OK
        mock_all_services['notification'].assert_called()
    
    def test_return_nonexistent_loan(self, authenticated_client, mock_all_services):
        """Test returning non-existent loan"""
        url = '/api/loans/999/return/'
        response = authenticated_client.put(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestLoanRenewal:
    """Test loan renewal endpoint"""
    
    def test_renew_loan_success(self, authenticated_client, loan, mock_all_services):
        """Test successful loan renewal"""
        url = f'/api/loans/{loan.id}/renew/'
        old_due_date = loan.due_date
        response = authenticated_client.put(url)
        assert response.status_code == status.HTTP_200_OK
        
        loan.refresh_from_db()
        assert loan.renewal_count == 1
        assert loan.due_date == old_due_date + timedelta(days=14)
    
    def test_renew_loan_max_renewals(self, authenticated_client, loan, mock_all_services):
        """Test renewal when max renewals reached"""
        loan.renewal_count = 2
        loan.save()
        url = f'/api/loans/{loan.id}/renew/'
        response = authenticated_client.put(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_renew_overdue_loan(self, authenticated_client, overdue_loan, mock_all_services):
        """Test renewing overdue loan"""
        url = f'/api/loans/{overdue_loan.id}/renew/'
        response = authenticated_client.put(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_renew_loan_notification(self, authenticated_client, loan, mock_all_services):
        """Test notification sent on renewal"""
        url = f'/api/loans/{loan.id}/renew/'
        response = authenticated_client.put(url)
        mock_all_services['notification'].assert_called()


@pytest.mark.django_db
class TestLoanList:
    """Test loan listing endpoints"""
    
    url = '/api/loans/'
    
    def test_list_user_loans(self, authenticated_client, loan, user):
        """Test listing user's loans"""
        response = authenticated_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_list_loans_unauthenticated(self, api_client):
        """Test listing loans without authentication"""
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_filter_active_loans(self, authenticated_client, loan, returned_loan):
        """Test filtering active loans"""
        response = authenticated_client.get(f'{self.url}?status=ACTIVE')
        assert response.status_code == status.HTTP_200_OK
        for loan_data in response.data:
            assert loan_data['status'] == 'ACTIVE'
    
    def test_filter_overdue_loans(self, authenticated_client, overdue_loan):
        """Test filtering overdue loans"""
        response = authenticated_client.get(f'{self.url}?overdue=true')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestLoanStats:
    """Test loan statistics endpoint"""
    
    url = '/api/loans/stats/'
    
    def test_get_stats_librarian(self, librarian_client, loan, overdue_loan):
        """Test getting stats as librarian"""
        response = librarian_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert 'total_active' in response.data
        assert 'total_overdue' in response.data
    
    def test_get_stats_regular_user(self, authenticated_client):
        """Test stats endpoint forbidden for regular users"""
        response = authenticated_client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
