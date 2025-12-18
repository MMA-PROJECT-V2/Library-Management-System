"""
RabbitMQ Client Utility for Library Management System
Handles connection, publishing, and consuming messages
"""

import pika
import json
import logging
import os
import sys
from typing import Callable, Dict, Any
from decouple import config

logger = logging.getLogger(__name__)


class RabbitMQClient:
    """RabbitMQ Client for publishing and consuming messages"""

    def __init__(self):
        # Try to discover RabbitMQ from Consul
        rabbitmq_host = None
        rabbitmq_port = None

        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)

            from common.consul_utils import get_service

            rabbitmq_url = get_service("rabbitmq")
            if rabbitmq_url:
                # Remove protocol if present
                if "://" in rabbitmq_url:
                    rabbitmq_url = rabbitmq_url.split("://")[1]
                
                if ":" in rabbitmq_url:
                    rabbitmq_host, port_str = rabbitmq_url.split(":")
                    rabbitmq_port = int(port_str)
                else:
                    rabbitmq_host = rabbitmq_url
                    rabbitmq_port = 5672

                logger.info(f"✅ Discovered RabbitMQ from Consul: {rabbitmq_host}:{rabbitmq_port}")

        except Exception as e:
            logger.warning(f"Could not discover RabbitMQ from Consul: {e}")

        # Fallbacks
        self.host = rabbitmq_host or config("RABBITMQ_HOST", default="localhost")
        self.port = rabbitmq_port or config("RABBITMQ_PORT", default=5672, cast=int)

        self.username = config("RABBITMQ_USER", default="guest")
        self.password = config("RABBITMQ_PASSWORD", default="guest")
        self.virtual_host = config("RABBITMQ_VHOST", default="/")

        self.connection = None
        self.channel = None

        self.exchange_name = "library_events"
        self.exchange_type = "topic"

    def connect(self) -> bool:
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )

            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type=self.exchange_type,
                durable=True,
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

    def publish(self, routing_key: str, message: Dict[Any, Any]) -> bool:
        """Publish message to RabbitMQ exchange"""
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
                    delivery_mode=2,
                    content_type="application/json",
                ),
            )

            logger.info(f"📤 Published message to {routing_key}")
            return True

        except Exception as e:
            logger.warning(f"⚠️ Publish failed: {e}. Retrying...")
            self.disconnect()

            if self.connect():
                try:
                    self.channel.basic_publish(
                        exchange=self.exchange_name,
                        routing_key=routing_key,
                        body=body,
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            content_type="application/json",
                        ),
                    )
                    logger.info("📤 Published message after reconnect")
                    return True
                except Exception as retry_e:
                    logger.error(f"❌ Retry failed: {retry_e}")

            return False

    def consume(self, queue_name: str, routing_keys: list, callback: Callable):
        """Consume messages from queue"""
        if not self.channel:
            if not self.connect():
                logger.error("Cannot consume: Not connected to RabbitMQ")
                return

        try:
            self.channel.queue_declare(queue=queue_name, durable=True)

            for routing_key in routing_keys:
                self.channel.queue_bind(
                    exchange=self.exchange_name,
                    queue=queue_name,
                    routing_key=routing_key,
                )

            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False,
            )

            logger.info(f"👂 Consuming from queue '{queue_name}'")
            self.channel.start_consuming()

        except KeyboardInterrupt:
            logger.info("🛑 Consumer stopped")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"❌ Consumer error: {e}")

    def stop_consuming(self):
        if self.channel:
            self.channel.stop_consuming()
        self.disconnect()


# Singleton
_rabbitmq_client = None


def get_rabbitmq_client() -> RabbitMQClient:
    global _rabbitmq_client
    if _rabbitmq_client is None:
        _rabbitmq_client = RabbitMQClient()
    return _rabbitmq_client
