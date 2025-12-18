"""
Event Publishers for Books Service
Publishes events: book.created, book.updated, book.deleted
Place this file in: backend/books_service/books/events.py
"""

import logging
import sys
import os
import json

# Add common directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

from rabbitmq_client import get_rabbitmq_client

logger = logging.getLogger(__name__)


def publish_book_created(book):
    """Publish book_created event"""
    rabbitmq = get_rabbitmq_client()
    
    message = {
        'event_type': 'book_created',
        'book_id': book.id,
        'title': book.title,
        'author': book.author,
        'isbn': book.isbn,
        'category': book.category,
        'available_copies': book.available_copies,
        'timestamp': book.created_at.isoformat() if hasattr(book, 'created_at') else None
    }
    
    rabbitmq.publish('book.created', message)
    logger.info(f"📤 Published book_created event for book '{book.title}' (#{book.id})")


def publish_book_updated(book):
    """Publish book_updated event"""
    rabbitmq = get_rabbitmq_client()
    
    message = {
        'event_type': 'book_updated',
        'book_id': book.id,
        'title': book.title,
        'author': book.author,
        'isbn': book.isbn,
        'category': book.category,
        'available_copies': book.available_copies,
        'timestamp': book.updated_at.isoformat() if hasattr(book, 'updated_at') else None
    }
    
    rabbitmq.publish('book.updated', message)
    logger.info(f"📤 Published book_updated event for book '{book.title}' (#{book.id})")


def publish_book_deleted(book_id, title):
    """Publish book_deleted event"""
    rabbitmq = get_rabbitmq_client()
    
    message = {
        'event_type': 'book_deleted',
        'book_id': book_id,
        'title': title
    }
    
    rabbitmq.publish('book.deleted', message)
    logger.info(f"📤 Published book_deleted event for book '{title}' (#{book_id})")



