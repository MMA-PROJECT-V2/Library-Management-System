"""
Books Service RabbitMQ Consumer
Listens for book.{create,update,delete}_request and updates database
"""

import json
import logging
import sys
import os
from django.conf import settings

# Add common directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

from rabbitmq_client import get_rabbitmq_client
from books.serializers import BookSerializer
from books.models import Book
from books.events import (
    publish_book_created,
    publish_book_updated,
    publish_book_deleted
)

logger = logging.getLogger(__name__)

class BookConsumer:
    def __init__(self):
        self.rabbitmq = get_rabbitmq_client()
        
    def start(self):
        """Start listening for messages"""
        logger.info("📚 Book Consumer started. Waiting for messages...")
        
        # Listen for book operations
        self.rabbitmq.consume(
            queue_name='book_service_queue',
            routing_keys=['book.create_request', 'book.update_request', 'book.delete_request'],
            callback=self.process_message
        )
        
    def process_message(self, ch, method, properties, body):
        """Process incoming RabbitMQ message"""
        try:
            message = json.loads(body)
            routing_key = method.routing_key
            
            print(f"\n📥 [BookService] Received message on key: {routing_key}")
            print(f"📦 [BookService] Payload: {json.dumps(message, indent=2)}")
            
            # Determine action based on routing key or event_type
            if routing_key == 'book.create_request' or message.get('event_type') == 'book_create_request':
                # Handle both direct data (from frontend) and wrapped data (from internal events)
                data = message.get('data', message)
                print(f"🔄 [BookService] Processing CREATE request...")
                self.handle_create(data)
                
            elif routing_key == 'book.update_request' or message.get('event_type') == 'book_update_request':
                print(f"🔄 [BookService] Processing UPDATE request...")
                self.handle_update(message.get('book_id'), message.get('data'))
                
            elif routing_key == 'book.delete_request' or message.get('event_type') == 'book_delete_request':
                print(f"🔄 [BookService] Processing DELETE request...")
                self.handle_delete(message.get('book_id'))
            
            else:
                print(f"⚠️ [BookService] Unknown routing key/event type: {routing_key}")

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print("✅ [BookService] Message acknowledged")
            
        except Exception as e:
            print(f"❌ [BookService] Error processing message: {e}")
            logger.error(f"Error processing message: {e}")
            # Still acknowledge to prevent infinite loops for bad messages, 
            # ideally should dead-letter
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def handle_create(self, data):
        """Handle book creation"""
        try:
            serializer = BookSerializer(data=data)
            if serializer.is_valid():
                book = serializer.save()
                logger.info(f"✅ Book created async: {book.title}")
                publish_book_created(book)
            else:
                logger.error(f"❌ Validation failed for book creation: {serializer.errors}")
        except Exception as e:
            logger.error(f"❌ Failed to create book: {e}")

    def handle_update(self, book_id, data):
        """Handle book update"""
        try:
            try:
                book = Book.objects.get(id=book_id)
            except Book.DoesNotExist:
                logger.error(f"❌ Book not found for update: {book_id}")
                return

            serializer = BookSerializer(book, data=data, partial=True)
            if serializer.is_valid():
                book = serializer.save()
                logger.info(f"✅ Book updated async: {book.title}")
                publish_book_updated(book)
            else:
                logger.error(f"❌ Validation failed for book update: {serializer.errors}")
        except Exception as e:
            logger.error(f"❌ Failed to update book: {e}")

    def handle_delete(self, book_id):
        """Handle book deletion"""
        try:
            try:
                book = Book.objects.get(id=book_id)
                book_title = book.title
                book.delete()
                logger.info(f"✅ Book deleted async: {book_title}")
                publish_book_deleted(book_id, book_title)
            except Book.DoesNotExist:
                logger.warning(f"⚠️ Book not found for deletion: {book_id}")
        except Exception as e:
            logger.error(f"❌ Failed to delete book: {e}")
