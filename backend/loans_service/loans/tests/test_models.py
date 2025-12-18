"""
Unit tests for Loan model
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from loans.models import Loan


@pytest.mark.django_db
class TestLoanModel:
    """Test Loan model functionality"""
    
    def test_create_loan(self, user):
        """Test creating a loan"""
        loan = Loan.objects.create(
            user_id=user.id,
            book_id=1,
            loan_date=timezone.now().date(),
            due_date=(timezone.now() + timedelta(days=14)).date()
        )
        assert loan.id is not None
        assert loan.status == 'ACTIVE'
        assert loan.renewal_count == 0
        assert loan.return_date is None
    
    def test_loan_str_representation(self, loan):
        """Test string representation"""
        expected = f"Loan #{loan.id} - User {loan.user_id} - Book {loan.book_id} [{loan.status}]"
        assert str(loan) == expected
    
    def test_is_overdue_false(self, loan):
        """Test is_overdue when loan is not overdue"""
        assert loan.is_overdue() is False
    
    def test_is_overdue_true(self, overdue_loan):
        """Test is_overdue when loan is overdue"""
        assert overdue_loan.is_overdue() is True
    
    def test_is_overdue_returned_loan(self, returned_loan):
        """Test is_overdue for returned loan"""
        assert returned_loan.is_overdue() is False
    
    def test_calculate_fine_no_overdue(self, loan):
        """Test fine calculation for on-time loan"""
        fine = loan.calculate_fine()
        assert fine == 0
    
    def test_calculate_fine_overdue(self, overdue_loan):
        """Test fine calculation for overdue loan"""
        days_overdue = (timezone.now().date() - overdue_loan.due_date).days
        expected_fine = days_overdue * 50  # 50 DZD per day
        assert overdue_loan.calculate_fine() == expected_fine
    
    def test_calculate_fine_returned_loan(self, returned_loan):
        """Test fine calculation for returned loan"""
        assert returned_loan.calculate_fine() == 0
    
    def test_can_renew_true(self, loan):
        """Test can_renew when renewal is allowed"""
        assert loan.can_renew() is True
    
    def test_can_renew_max_renewals(self, loan):
        """Test can_renew when max renewals reached"""
        loan.renewal_count = 2
        loan.save()
        assert loan.can_renew() is False
    
    def test_can_renew_overdue(self, overdue_loan):
        """Test can_renew for overdue loan"""
        assert overdue_loan.can_renew() is False
    
    def test_can_renew_returned(self, returned_loan):
        """Test can_renew for returned loan"""
        assert returned_loan.can_renew() is False
    
    def test_renew_loan_success(self, loan):
        """Test successful loan renewal"""
        old_due_date = loan.due_date
        result = loan.renew()
        assert result is True
        assert loan.renewal_count == 1
        assert loan.due_date == old_due_date + timedelta(days=14)
    
    def test_renew_loan_max_renewals(self, loan):
        """Test renewal when max renewals reached"""
        loan.renewal_count = 2
        loan.save()
        result = loan.renew()
        assert result is False
        assert loan.renewal_count == 2
    
    def test_renew_loan_overdue(self, overdue_loan):
        """Test renewal of overdue loan"""
        result = overdue_loan.renew()
        assert result is False
    
    def test_return_loan(self, loan):
        """Test returning a loan"""
        loan.return_loan()
        assert loan.status == 'RETURNED'
        assert loan.return_date == timezone.now().date()
    
    def test_return_already_returned_loan(self, returned_loan):
        """Test returning an already returned loan"""
        old_return_date = returned_loan.return_date
        returned_loan.return_loan()
        assert returned_loan.return_date == old_return_date
    
    def test_loan_ordering(self, user):
        """Test loans are ordered by loan_date descending"""
        loan1 = Loan.objects.create(
            user_id=user.id,
            book_id=1,
            loan_date=(timezone.now() - timedelta(days=2)).date(),
            due_date=timezone.now().date()
        )
        loan2 = Loan.objects.create(
            user_id=user.id,
            book_id=2,
            loan_date=timezone.now().date(),
            due_date=(timezone.now() + timedelta(days=14)).date()
        )
        loans = list(Loan.objects.all())
        assert loans[0] == loan2
        assert loans[1] == loan1
