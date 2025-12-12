"""
Tests for fine calculations and overdue logic
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from loans.models import Loan


@pytest.mark.django_db
class TestFineCalculations:
    """Test fine calculation logic"""
    
    def test_no_fine_on_time_return(self, user):
        """Test no fine for on-time return"""
        loan = Loan.objects.create(
            user_id=user.id,
            book_id=1,
            loan_date=timezone.now().date(),
            due_date=(timezone.now() + timedelta(days=5)).date()
        )
        assert loan.calculate_fine() == 0
    
    def test_fine_one_day_overdue(self, user):
        """Test fine for 1 day overdue"""
        loan = Loan.objects.create(
            user_id=user.id,
            book_id=1,
            loan_date=(timezone.now() - timedelta(days=15)).date(),
            due_date=(timezone.now() - timedelta(days=1)).date()
        )
        assert loan.calculate_fine() == 50  # 1 day * 50 DZD
    
    def test_fine_multiple_days_overdue(self, user):
        """Test fine for multiple days overdue"""
        days_overdue = 10
        loan = Loan.objects.create(
            user_id=user.id,
            book_id=1,
            loan_date=(timezone.now() - timedelta(days=24)).date(),
            due_date=(timezone.now() - timedelta(days=days_overdue)).date()
        )
        expected_fine = days_overdue * 50
        assert loan.calculate_fine() == expected_fine
    
    def test_no_fine_after_return(self, user):
        """Test no fine calculated after return"""
        loan = Loan.objects.create(
            user_id=user.id,
            book_id=1,
            loan_date=(timezone.now() - timedelta(days=20)).date(),
            due_date=(timezone.now() - timedelta(days=6)).date(),
            return_date=timezone.now().date(),
            status='RETURNED'
        )
        assert loan.calculate_fine() == 0
    
    def test_fine_calculation_edge_case_same_day(self, user):
        """Test fine calculation on due date"""
        loan = Loan.objects.create(
            user_id=user.id,
            book_id=1,
            loan_date=(timezone.now() - timedelta(days=14)).date(),
            due_date=timezone.now().date()
        )
        assert loan.calculate_fine() == 0


@pytest.mark.django_db
class TestOverdueDetection:
    """Test overdue loan detection"""
    
    def test_is_overdue_future_due_date(self, user):
        """Test loan with future due date is not overdue"""
        loan = Loan.objects.create(
            user_id=user.id,
            book_id=1,
            loan_date=timezone.now().date(),
            due_date=(timezone.now() + timedelta(days=7)).date()
        )
        assert loan.is_overdue() is False
    
    def test_is_overdue_past_due_date(self, user):
        """Test loan with past due date is overdue"""
        loan = Loan.objects.create(
            user_id=user.id,
            book_id=1,
            loan_date=(timezone.now() - timedelta(days=20)).date(),
            due_date=(timezone.now() - timedelta(days=5)).date()
        )
        assert loan.is_overdue() is True
    
    def test_is_overdue_today_due_date(self, user):
        """Test loan due today is not overdue"""
        loan = Loan.objects.create(
            user_id=user.id,
            book_id=1,
            loan_date=(timezone.now() - timedelta(days=14)).date(),
            due_date=timezone.now().date()
        )
        assert loan.is_overdue() is False
    
    def test_returned_loan_not_overdue(self, user):
        """Test returned loan is not considered overdue"""
        loan = Loan.objects.create(
            user_id=user.id,
            book_id=1,
            loan_date=(timezone.now() - timedelta(days=20)).date(),
            due_date=(timezone.now() - timedelta(days=5)).date(),
            return_date=timezone.now().date(),
            status='RETURNED'
        )
        assert loan.is_overdue() is False
