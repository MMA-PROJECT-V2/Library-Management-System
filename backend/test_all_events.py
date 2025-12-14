"""
Complete RabbitMQ Event Testing Script
Tests all event types: loans, books, and users
Run from backend directory: python test_all_events.py
"""

import sys
import os
import json
import logging
from datetime import datetime

# Setup path to import common modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'common'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from rabbitmq_client import get_rabbitmq_client
except ImportError:
    logger.error("❌ Could not import rabbitmq_client. Make sure you run this from 'backend/' directory.")
    sys.exit(1)

def test_user_events():
    """Test User Service events"""
    logger.info("\n👤 TESTING USER EVENTS...")
    client = get_rabbitmq_client()
    
    message = {
        'event_type': 'user_registered',
        'user_id': 999,
        'username': 'test_user',
        'email': 'test@example.com',
        'timestamp': datetime.now().isoformat()
    }
    
    if client.publish('user.registered', message):
        logger.info("✅ Published 'user.registered'")
    else:
        logger.error("❌ Failed to publish 'user.registered'")
        
    if client.publish('notification.email.user_registered', message):
        logger.info("✅ Published 'notification.email.user_registered'")
    else:
        logger.error("❌ Failed to publish notification")

def test_book_events():
    """Test Book Service events"""
    logger.info("\n📚 TESTING BOOK EVENTS...")
    client = get_rabbitmq_client()
    
    msg_create = {
        'event_type': 'book_created',
        'book_id': 101,
        'title': 'Test Book',
        'timestamp': datetime.now().isoformat()
    }
    
    if client.publish('book.created', msg_create):
        logger.info("✅ Published 'book.created'")
    else:
        logger.error("❌ Failed to publish 'book.created'")
        
    if client.publish('book.updated', {'event_type': 'book_updated', 'book_id': 101}):
        logger.info("✅ Published 'book.updated'")
        
    if client.publish('book.deleted', {'event_type': 'book_deleted', 'book_id': 101}):
        logger.info("✅ Published 'book.deleted'")

def test_loan_events():
    """Test Loan Service events"""
    logger.info("\n📖 TESTING LOAN EVENTS...")
    client = get_rabbitmq_client()
    
    loan_msg = {
        'event_type': 'loan_created',
        'loan_id': 555,
        'user_email': 'test@example.com',
        'loan_date': datetime.now().isoformat(),
        'due_date': datetime.now().isoformat(),
        'timestamp': datetime.now().isoformat()
    }
    
    if client.publish('loan.created', loan_msg):
        logger.info("✅ Published 'loan.created'")
    else:
        logger.error("❌ Failed to publish 'loan.created'")
        
    if client.publish('notification.email.loan_created', loan_msg):
        logger.info("✅ Published 'notification.email.loan_created'")

if __name__ == "__main__":
    print("="*50)
    print("🚀 RABBITMQ INTEGRATION TEST")
    print("="*50)
    
    try:
        test_user_events()
        test_book_events()
        test_loan_events()
        print("\n✅ All tests completed!")
    except KeyboardInterrupt:
        print("\n🛑 Aborted")
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
