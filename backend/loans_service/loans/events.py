"""
Event Publishers for Loans Service
Publishes events to RabbitMQ when loans are created, returned, renewed, etc.
"""

import logging
import sys
import os

# Add common directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

from rabbitmq_client import get_rabbitmq_client

logger = logging.getLogger(__name__)


def publish_loan_created(loan, book_data, user_email):
    """
    Publish loan_created event
    
    Args:
        loan: Loan object
        book_data: Book information dict
        user_email: User's email address
    """
    rabbitmq = get_rabbitmq_client()
    
    message = {
        'event_type': 'loan_created',
        'loan_id': loan.id,
        'user_id': loan.user_id,
        'user_email': user_email,
        'book_id': loan.book_id,
        'book_title': book_data.get('title'),
        'book_author': book_data.get('author'),
        'book_isbn': book_data.get('isbn'),
        'book_category': book_data.get('category'),
        'loan_date': loan.loan_date.isoformat(),
        'due_date': loan.due_date.isoformat(),
        'timestamp': loan.created_at.isoformat()
    }
    
    # Publish to both general loan queue and notification queue
    rabbitmq.publish('loan.created', message)
    rabbitmq.publish('notification.email.loan_created', message)
    
    logger.info(f"📤 Published loan_created event for loan #{loan.id}")


def publish_loan_returned(loan, book_data, user_email, fine_amount=0, days_overdue=0):
    """
    Publish loan_returned event
    
    Args:
        loan: Loan object
        book_data: Book information dict
        user_email: User's email address
        fine_amount: Fine amount if overdue
        days_overdue: Number of days overdue
    """
    rabbitmq = get_rabbitmq_client()
    
    message = {
        'event_type': 'loan_returned',
        'loan_id': loan.id,
        'user_id': loan.user_id,
        'user_email': user_email,
        'book_id': loan.book_id,
        'book_title': book_data.get('title'),
        'return_date': loan.return_date.isoformat(),
        'due_date': loan.due_date.isoformat(),
        'fine_amount': float(fine_amount),
        'days_overdue': days_overdue,
        'on_time': days_overdue == 0,
        'timestamp': loan.updated_at.isoformat()
    }
    
    # Publish to general loan queue
    rabbitmq.publish('loan.returned', message)
    
    # Publish to appropriate notification queue based on whether it's on time or late
    if days_overdue > 0:
        rabbitmq.publish('notification.email.loan_returned_late', message)
    else:
        rabbitmq.publish('notification.email.loan_returned_ontime', message)
    
    logger.info(f"📤 Published loan_returned event for loan #{loan.id} (overdue: {days_overdue} days)")


def publish_loan_renewed(loan, book_data, user_email, old_due_date):
    """
    Publish loan_renewed event
    
    Args:
        loan: Loan object
        book_data: Book information dict
        user_email: User's email address
        old_due_date: Previous due date
    """
    rabbitmq = get_rabbitmq_client()
    
    renewal_message = ''
    if loan.renewal_count < 2:
        renewal_message = f'Vous pouvez encore renouveler cet emprunt {2 - loan.renewal_count} fois.'
    else:
        renewal_message = 'Attention : Vous avez atteint le nombre maximum de renouvellements (2).'
    
    message = {
        'event_type': 'loan_renewed',
        'loan_id': loan.id,
        'user_id': loan.user_id,
        'user_email': user_email,
        'book_id': loan.book_id,
        'book_title': book_data.get('title'),
        'old_due_date': old_due_date.isoformat(),
        'new_due_date': loan.due_date.isoformat(),
        'renewal_count': loan.renewal_count,
        'max_renewals': loan.max_renewals,
        'renewal_message': renewal_message,
        'timestamp': loan.updated_at.isoformat()
    }
    
    rabbitmq.publish('loan.renewed', message)
    rabbitmq.publish('notification.email.loan_renewed', message)
    
    logger.info(f"📤 Published loan_renewed event for loan #{loan.id} (renewal #{loan.renewal_count})")


def publish_loan_overdue(loan, book_data, user_email, days_overdue, fine_amount):
    """
    Publish loan_overdue event (for periodic checks)
    
    Args:
        loan: Loan object
        book_data: Book information dict
        user_email: User's email address
        days_overdue: Number of days overdue
        fine_amount: Current fine amount
    """
    rabbitmq = get_rabbitmq_client()
    
    message = {
        'event_type': 'loan_overdue',
        'loan_id': loan.id,
        'user_id': loan.user_id,
        'user_email': user_email,
        'book_id': loan.book_id,
        'book_title': book_data.get('title'),
        'due_date': loan.due_date.isoformat(),
        'days_overdue': days_overdue,
        'fine_amount': float(fine_amount),
        'timestamp': loan.updated_at.isoformat()
    }
    
    rabbitmq.publish('loan.overdue', message)
    rabbitmq.publish('notification.email.loan_overdue', message)
    
    logger.info(f"📤 Published loan_overdue event for loan #{loan.id} ({days_overdue} days overdue)")
    