"""
User Service RabbitMQ Consumer
Listens for user.create events and creates users
"""

import json
import logging
import sys
import os
from django.conf import settings

# Add common directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

from rabbitmq_client import get_rabbitmq_client
from users.serializers import RegisterSerializer
from users.events import publish_user_registered

logger = logging.getLogger(__name__)

class UserConsumer:
    def __init__(self):
        self.rabbitmq = get_rabbitmq_client()
        
    def start(self):
        """Start listening for messages"""
        logger.info("🚀 User Consumer started. Waiting for messages...")
        
        # Listen for user creation requests
        self.rabbitmq.consume(
            queue_name='user_service_queue',
            routing_keys=['user.create'],
            callback=self.process_message
        )
        
    def process_message(self, ch, method, properties, body):
        """Process incoming RabbitMQ message"""
        try:
            message = json.loads(body)
            event_type = message.get('event_type')
            
            logger.info(f"📨 Received event: {event_type}")
            
            if event_type == 'user_create':
                self.handle_user_create(message.get('data'))
                
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            # Negative Acknowledge (requeue if transient, reject if malformed)
            # For now, we ack to avoid infinite looks on bad data
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def handle_user_create(self, user_data):
        """Handle user creation logic"""
        try:
            logger.info(f"👤 Creating user: {user_data.get('email')}")
            
            # Using serializer to validate and save (re-validation for safety)
            serializer = RegisterSerializer(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
                logger.info(f"✅ User created successfully: {user.username}")
                
                # Publish registered event (triggers notification)
                publish_user_registered(user)
            else:
                logger.error(f"❌ Validation failed for user creation: {serializer.errors}")
                
        except Exception as e:
            logger.error(f"❌ Failed to create user: {e}")
