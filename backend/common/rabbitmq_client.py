"""
RabbitMQ Client Utility for Library Management System
Handles connection, publishing, and consuming messages
"""

import pika
import json
import logging
from typing import Callable, Dict, Any
from decouple import config

logger = logging.getLogger(__name__)


class RabbitMQClient:
    """RabbitMQ Client for publishing and consuming messages"""
    
    def __init__(self):
        self.host = config('RABBITMQ_HOST', default='localhost')
        self.port = config('RABBITMQ_PORT', default=5672, cast=int)
        self.username = config('RABBITMQ_USER', default='guest')
        self.password = config('RABBITMQ_PASSWORD', default='guest')
        self.virtual_host = config('RABBITMQ_VHOST', default='/')
        
        self.connection = None
        self.channel = None
        
        # Exchange configuration
        self.exchange_name = 'library_events'
        self.exchange_type = 'topic'
    
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type=self.exchange_type,
                durable=True
            )
            
            logger.info(f"✅ Connected to RabbitMQ at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            return False
    
    def disconnect(self):
        """Close RabbitMQ connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("✅ Disconnected from RabbitMQ")
        except Exception as e:
            logger.error(f"❌ Error disconnecting from RabbitMQ: {e}")
    
    def publish(self, routing_key: str, message: Dict[Any, Any]):
        """
        Publish message to RabbitMQ exchange
        
        Args:
            routing_key: Routing key (e.g., 'notification.email.loan_created')
            message: Dictionary containing message data
        """
        if not self.channel:
            if not self.connect():
                logger.error("Cannot publish: Not connected to RabbitMQ")
                return False
        
        try:
            body = json.dumps(message, default=str)
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"📤 Published message to {routing_key}: {message.get('event_type', 'unknown')}")
            return True
            
        except (pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed, pika.exceptions.StreamLostError, Exception) as e:
            logger.warning(f"⚠️ Failed to publish message: {e}. Attempting reconnection...")
            
            # Force disconnect and reconnect
            self.disconnect()
            if self.connect():
                try:
                    self.channel.basic_publish(
                        exchange=self.exchange_name,
                        routing_key=routing_key,
                        body=body,
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            content_type='application/json'
                        )
                    )
                    logger.info(f"📤 Published message after reconnection to {routing_key}")
                    return True
                except Exception as retry_e:
                    logger.error(f"❌ Failed to publish message after retry: {retry_e}")
                    return False
            else:
                logger.error("❌ Failed to reconnect to RabbitMQ")
                return False
    
    def consume(self, queue_name: str, routing_keys: list, callback: Callable):
        """
        Start consuming messages from queue
        
        Args:
            queue_name: Name of the queue
            routing_keys: List of routing keys to bind (e.g., ['notification.email.*'])
            callback: Function to handle received messages
        """
        if not self.channel:
            if not self.connect():
                logger.error("Cannot consume: Not connected to RabbitMQ")
                return
        
        try:
            # Declare queue
            self.channel.queue_declare(queue=queue_name, durable=True)
            
            # Bind queue to exchange with routing keys
            for routing_key in routing_keys:
                self.channel.queue_bind(
                    exchange=self.exchange_name,
                    queue=queue_name,
                    routing_key=routing_key
                )
                logger.info(f"🔗 Bound queue '{queue_name}' to routing key '{routing_key}'")
            
            # Set QoS (Fair dispatch - don't send more than 1 message at a time)
            self.channel.basic_qos(prefetch_count=1)
            
            # Start consuming
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False  # Manual acknowledgment
            )
            
            logger.info(f"👂 Waiting for messages on queue '{queue_name}'...")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("🛑 Stopping consumer...")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"❌ Error in consumer: {e}")
    
    def stop_consuming(self):
        """Stop consuming messages"""
        if self.channel:
            self.channel.stop_consuming()
        self.disconnect()


# Singleton instance
_rabbitmq_client = None

def get_rabbitmq_client() -> RabbitMQClient:
    """Get or create RabbitMQ client singleton"""
    global _rabbitmq_client
    if _rabbitmq_client is None:
        _rabbitmq_client = RabbitMQClient()
    return _rabbitmq_client