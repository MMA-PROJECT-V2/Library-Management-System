"""
Comprehensive unit tests for serializers.
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from loans.models import Loan, LoanHistory
from loans.serializers import LoanSerializer, LoanCreateSerializer, LoanHistorySerializer


@pytest.fixture
def active_loan(db):
    """Create an active loan."""
    return Loan.objects.create(
        user_id=1,
        book_id=1,
        loan_date=timezone.now().date(),
        due_date=(timezone.now() + timedelta(days=14)).date(),
        status='ACTIVE'
    )


@pytest.fixture
def overdue_loan(db):
    """Create an overdue loan."""
    return Loan.objects.create(
        user_id=1,
        book_id=2,
        loan_date=(timezone.now() - timedelta(days=20)).date(),
        due_date=(timezone.now() - timedelta(days=6)).date(),
        status='ACTIVE'
    )


@pytest.fixture
def returned_loan(db):
    """Create a returned loan."""
    return Loan.objects.create(
        user_id=1,
        book_id=3,
        loan_date=(timezone.now() - timedelta(days=10)).date(),
        due_date=(timezone.now() + timedelta(days=4)).date(),
        return_date=timezone.now().date(),
        status='RETURNED'
    )


class TestLoanSerializer:
    """Tests for LoanSerializer."""
    
    def test_serializer_contains_expected_fields(self, active_loan):
        """Test serializer returns all expected fields."""
        serializer = LoanSerializer(active_loan)
        data = serializer.data
        
        expected_fields = [
            'id', 'user_id', 'book_id', 'loan_date', 'due_date',
            'return_date', 'status', 'fine_amount', 'fine_paid',
            'renewal_count', 'max_renewals', 'notes', 'is_overdue',
            'days_until_due', 'can_renew', 'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            assert field in data
    
    def test_is_overdue_computed_field(self, active_loan, overdue_loan):
        """Test is_overdue computed field."""
        active_serializer = LoanSerializer(active_loan)
        overdue_serializer = LoanSerializer(overdue_loan)
        
        assert active_serializer.data['is_overdue'] is False
        assert overdue_serializer.data['is_overdue'] is True
    
    def test_days_until_due_computed_field(self, active_loan):
        """Test days_until_due computed field."""
        serializer = LoanSerializer(active_loan)
        expected_days = (active_loan.due_date - timezone.now().date()).days
        
        assert serializer.data['days_until_due'] == expected_days
    
    def test_days_until_due_for_returned_loan(self, returned_loan):
        """Test days_until_due is 0 for returned loan."""
        serializer = LoanSerializer(returned_loan)
        assert serializer.data['days_until_due'] == 0
    
    def test_can_renew_computed_field(self, active_loan, overdue_loan):
        """Test can_renew computed field."""
        active_serializer = LoanSerializer(active_loan)
        overdue_serializer = LoanSerializer(overdue_loan)
        
        assert active_serializer.data['can_renew'] is True
        assert overdue_serializer.data['can_renew'] is False
    
    def test_serializer_many(self, active_loan, overdue_loan):
        """Test serializing multiple loans."""
        loans = Loan.objects.all()
        serializer = LoanSerializer(loans, many=True)
        
        assert len(serializer.data) == 2


class TestLoanCreateSerializer:
    """Tests for LoanCreateSerializer."""
    
    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'user_id': 1,
            'book_id': 1,
            'notes': 'Test loan'
        }
        serializer = LoanCreateSerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['user_id'] == 1
        assert serializer.validated_data['book_id'] == 1
        assert serializer.validated_data['notes'] == 'Test loan'
    
    def test_minimal_valid_data(self):
        """Test serializer with minimal required data."""
        data = {'user_id': 1, 'book_id': 1}
        serializer = LoanCreateSerializer(data=data)
        
        assert serializer.is_valid()
    
    def test_missing_user_id(self):
        """Test serializer fails without user_id."""
        data = {'book_id': 1}
        serializer = LoanCreateSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'user_id' in serializer.errors
    
    def test_missing_book_id(self):
        """Test serializer fails without book_id."""
        data = {'user_id': 1}
        serializer = LoanCreateSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'book_id' in serializer.errors
    
    def test_invalid_user_id_zero(self):
        """Test serializer fails with user_id = 0."""
        data = {'user_id': 0, 'book_id': 1}
        serializer = LoanCreateSerializer(data=data)
        
        assert not serializer.is_valid()
    
    def test_invalid_user_id_negative(self):
        """Test serializer fails with negative user_id."""
        data = {'user_id': -1, 'book_id': 1}
        serializer = LoanCreateSerializer(data=data)
        
        assert not serializer.is_valid()
    
    def test_invalid_book_id_zero(self):
        """Test serializer fails with book_id = 0."""
        data = {'user_id': 1, 'book_id': 0}
        serializer = LoanCreateSerializer(data=data)
        
        assert not serializer.is_valid()
    
    def test_invalid_book_id_negative(self):
        """Test serializer fails with negative book_id."""
        data = {'user_id': 1, 'book_id': -1}
        serializer = LoanCreateSerializer(data=data)
        
        assert not serializer.is_valid()
    
    def test_notes_optional(self):
        """Test notes field is optional."""
        data = {'user_id': 1, 'book_id': 1}
        serializer = LoanCreateSerializer(data=data)
        
        assert serializer.is_valid()
    
    def test_notes_max_length(self):
        """Test notes field max length."""
        data = {
            'user_id': 1,
            'book_id': 1,
            'notes': 'x' * 501  # Exceeds max_length of 500
        }
        serializer = LoanCreateSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'notes' in serializer.errors


class TestLoanHistorySerializer:
    """Tests for LoanHistorySerializer."""
    
    def test_serializer_contains_expected_fields(self, db):
        """Test serializer returns all expected fields."""
        history = LoanHistory.objects.create(
            loan_id=1,
            action='CREATED',
            performed_by=1,
            details='Loan created'
        )
        serializer = LoanHistorySerializer(history)
        data = serializer.data
        
        expected_fields = [
            'id', 'loan_id', 'action', 'action_display',
            'performed_by', 'details', 'created_at'
        ]
        
        for field in expected_fields:
            assert field in data
    
    def test_action_display_field(self, db):
        """Test action_display shows readable action name."""
        history = LoanHistory.objects.create(
            loan_id=1,
            action='RENEWED'
        )
        serializer = LoanHistorySerializer(history)
        
        # Should show French display value
        assert serializer.data['action_display'] == 'Renouvelé'
    
    def test_read_only_fields(self, db):
        """Test that read-only fields are handled correctly."""
        history = LoanHistory.objects.create(loan_id=1, action='CREATED')
        
        serializer = LoanHistorySerializer(history)
        # Just verify serializer works and returns data
        assert 'id' in serializer.data
        assert serializer.data['action'] == 'CREATED'
