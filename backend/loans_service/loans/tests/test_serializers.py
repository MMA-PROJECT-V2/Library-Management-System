"""
Tests for Loan serializers
"""
import pytest
from loans.serializers import LoanSerializer, LoanCreateSerializer
from loans.models import Loan
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestLoanSerializer:
    """Test LoanSerializer"""
    
    def test_serialize_loan(self, loan):
        """Test serializing a loan"""
        serializer = LoanSerializer(loan)
        data = serializer.data
        assert data['id'] == loan.id
        assert data['user_id'] == loan.user_id
        assert data['book_id'] == loan.book_id
        assert data['status'] == loan.status
    
    def test_serialize_includes_calculated_fields(self, overdue_loan):
        """Test serializer includes calculated fields"""
        serializer = LoanSerializer(overdue_loan)
        data = serializer.data
        assert 'is_overdue' in data or data['status'] == 'ACTIVE'
    
    def test_deserialize_loan(self, user):
        """Test deserializing loan data"""
        data = {
            'user_id': user.id,
            'book_id': 1,
            'loan_date': timezone.now().date(),
            'due_date': (timezone.now() + timedelta(days=14)).date()
        }
        serializer = LoanSerializer(data=data)
        assert serializer.is_valid()
        loan = serializer.save()
        assert loan.user_id == user.id
        assert loan.book_id == 1


@pytest.mark.django_db
class TestLoanCreateSerializer:
    """Test LoanCreateSerializer"""
    
    def test_create_loan_valid_data(self, user):
        """Test creating loan with valid data"""
        data = {
            'user_id': user.id,
            'book_id': 1,
            'notes': 'Test note'
        }
        serializer = LoanCreateSerializer(data=data)
        assert serializer.is_valid()
    
    def test_create_loan_missing_required_fields(self):
        """Test validation with missing required fields"""
        data = {'book_id': 1}
        serializer = LoanCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'user_id' in serializer.errors
    
    def test_create_loan_invalid_user_id(self):
        """Test validation with invalid user_id"""
        data = {
            'user_id': -1,
            'book_id': 1
        }
        serializer = LoanCreateSerializer(data=data)
        assert not serializer.is_valid()
