"""
Loan Service RabbitMQ Consumer
Listens for loan requests (create, return, renew) and processes them.
"""

import json
import logging
import sys
import os
import requests
from typing import Optional, Dict, Any
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.db import transaction

# Add common directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

from rabbitmq_client import get_rabbitmq_client
from loans.serializers import LoanCreateSerializer
from loans.models import Loan, LoanHistory
from loans.events import (
    publish_loan_created,
    publish_loan_returned,
    publish_loan_renewed,
    publish_loan_overdue
)

logger = logging.getLogger(__name__)

# --- Service Clients (Replicated from views.py for standalone consumer usage) ---

class UserServiceClient:
    def __init__(self):
        self.base_url = os.getenv('USER_SERVICE_URL', 'http://localhost:8001')
        self.timeout = 10
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(f"{self.base_url}/api/users/{user_id}/", timeout=self.timeout)
            if response.status_code == 200:
                logger.info(f"✅ User {user_id} found")
                return response.json()
            else:
                logger.warning(f"❌ User {user_id} not found or error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ User Service connection error: {e}")
            return None

class BookServiceClient:
    def __init__(self):
        self.base_url = os.getenv('BOOK_SERVICE_URL', 'http://localhost:8002')
        self.timeout = 10
    
    def get_book(self, book_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(f"{self.base_url}/api/books/{book_id}/", timeout=self.timeout)
            if response.status_code == 200:
                logger.info(f"✅ Book {book_id} found")
                return response.json()
            else:
                logger.warning(f"❌ Book {book_id} not found or error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Book Service connection error: {e}")
            return None
    
    def decrement_stock(self, book_id: int) -> bool:
        # Note: Internal call, bypassing auth/permissions for simplicity since it's service-to-service
        # Ideally should use an internal API key
        try:
            url = f"{self.base_url}/api/books/{book_id}/borrow/"
            response = requests.post(url, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Failed to decrement stock: {e}")
            return False

    def increment_stock(self, book_id: int) -> bool:
        try:
            url = f"{self.base_url}/api/books/{book_id}/return/"
            response = requests.post(url, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Failed to increment stock: {e}")
            return False


class LoanConsumer:
    def __init__(self):
        self.rabbitmq = get_rabbitmq_client()
        self.user_client = UserServiceClient()
        self.book_client = BookServiceClient()
        
    def start(self):
        """Start listening for messages"""
        logger.info("💸 Loan Consumer started. Waiting for messages...")
        
        self.rabbitmq.consume(
            queue_name='loan_service_queue',
            routing_keys=['loan.create_request', 'loan.return_request', 'loan.renew_request'],
            callback=self.process_message
        )
        
    def process_message(self, ch, method, properties, body):
        try:
            message = json.loads(body)
            event_type = message.get('event_type')
            
            logger.info(f"📨 Received event: {event_type}")
            
            if event_type == 'loan_create_request':
                self.handle_create(message.get('data'))
            elif event_type == 'loan_return_request':
                self.handle_return(message.get('loan_id'), message.get('user_id'))
            elif event_type == 'loan_renew_request':
                self.handle_renew(message.get('loan_id'), message.get('user_id'))
                
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def handle_create(self, data):
        """Handle loan creation request"""
        try:
            serializer = LoanCreateSerializer(data=data)
            if not serializer.is_valid():
                logger.error(f"❌ Invalid loan data: {serializer.errors}")
                return

            user_id = serializer.validated_data['user_id']
            book_id = serializer.validated_data['book_id']
            notes = serializer.validated_data.get('notes', '')

            # 1. Verify User
            user_data = self.user_client.get_user(user_id)
            if not user_data or not user_data.get('is_active'):
                logger.error(f"❌ Cannot create loan: User {user_id} invalid or inactive")
                return

            # 2. Verify Book
            book_data = self.book_client.get_book(book_id)
            if not book_data or book_data.get('available_copies', 0) <= 0:
                logger.error(f"❌ Cannot create loan: Book {book_id} unavailable")
                return

            # 3. Check Limits
            active_count = Loan.objects.filter(user_id=user_id, status__in=['ACTIVE', 'RENEWED', 'OVERDUE']).count()
            if active_count >= 5:
                logger.error(f"❌ Cannot create loan: User {user_id} limit reached ({active_count})")
                return
            
            if Loan.objects.filter(user_id=user_id, book_id=book_id, status__in=['ACTIVE', 'RENEWED', 'OVERDUE']).exists():
                logger.error(f"❌ Cannot create loan: User {user_id} already has book {book_id}")
                return

            # 4. Create Loan & Transaction
            with transaction.atomic():
                loan_date = timezone.now().date()
                due_date = loan_date + timedelta(days=14)
                
                loan = Loan.objects.create(
                    user_id=user_id,
                    book_id=book_id,
                    loan_date=loan_date,
                    due_date=due_date,
                    notes=notes,
                    status='ACTIVE'
                )
                
                # 5. Decrement Stock
                if not self.book_client.decrement_stock(book_id):
                    raise Exception("Failed to decrement stock")
                
                # 6. Audit Log
                LoanHistory.objects.create(
                    loan_id=loan.id,
                    action='CREATED',
                    performed_by=user_id, # Assumed self-service or triggered by user
                    details=f"Emprunt créé (async) pour '{book_data.get('title')}'"
                )
                
                logger.info(f"✅ Loan created async: #{loan.id}")
                publish_loan_created(loan, book_data, user_data.get('email'))

        except Exception as e:
            logger.error(f"❌ Failed to create loan: {e}")

    def handle_return(self, loan_id, user_id):
        """Handle loan return request"""
        try:
            try:
                loan = Loan.objects.get(id=loan_id)
            except Loan.DoesNotExist:
                logger.error(f"❌ Loan {loan_id} not found for return")
                return

            if loan.status not in ['ACTIVE', 'OVERDUE', 'RENEWED']:
                logger.warning(f"⚠️ Loan {loan_id} already returned or invalid status")
                return

            with transaction.atomic():
                return_date = timezone.now().date()
                loan.return_date = return_date
                loan.status = 'RETURNED'
                
                days_overdue = 0
                fine_amount = 0
                if return_date > loan.due_date:
                    days_overdue = (return_date - loan.due_date).days
                    fine_amount = days_overdue * 50
                    loan.fine_amount = fine_amount
                
                loan.save()
                
                # Increment Stock
                if not self.book_client.increment_stock(loan.book_id):
                    raise Exception("Failed to increment stock")
                
                # Audit Log
                LoanHistory.objects.create(
                    loan_id=loan.id,
                    action='RETURNED',
                    performed_by=user_id,
                    details=f"Retour (async). Retard: {days_overdue} jours"
                )
                
                book_data = self.book_client.get_book(loan.book_id) or {}
                user_data = self.user_client.get_user(loan.user_id) or {}
                
                logger.info(f"✅ Loan returned async: #{loan.id}")
                publish_loan_returned(loan, book_data, user_data.get('email'), fine_amount, days_overdue)

        except Exception as e:
            logger.error(f"❌ Failed to return loan: {e}")

    def handle_renew(self, loan_id, user_id):
        """Handle loan renewal request"""
        try:
            try:
                loan = Loan.objects.get(id=loan_id)
            except Loan.DoesNotExist:
                logger.error(f"❌ Loan {loan_id} not found for renewal")
                return

            if loan.status not in ['ACTIVE', 'RENEWED']:
                logger.error(f"❌ Cannot renew loan {loan_id}: Invalid status {loan.status}")
                return
            
            if loan.is_overdue():
                logger.error(f"❌ Cannot renew loan {loan_id}: Overdue")
                return
            
            if loan.renewal_count >= loan.max_renewals:
                logger.error(f"❌ Cannot renew loan {loan_id}: Max renewals reached")
                return

            old_due_date = loan.due_date
            loan.due_date = loan.due_date + timedelta(days=14)
            loan.renewal_count += 1
            loan.status = 'RENEWED'
            loan.save()
            
            LoanHistory.objects.create(
                loan_id=loan.id,
                action='RENEWED',
                performed_by=user_id,
                details=f"Renouvellement (async) #{loan.renewal_count}"
            )
            
            book_data = self.book_client.get_book(loan.book_id) or {}
            user_data = self.user_client.get_user(loan.user_id) or {}
            
            logger.info(f"✅ Loan renewed async: #{loan.id}")
            publish_loan_renewed(loan, book_data, user_data.get('email'), old_due_date)

        except Exception as e:
            logger.error(f"❌ Failed to renew loan: {e}")
