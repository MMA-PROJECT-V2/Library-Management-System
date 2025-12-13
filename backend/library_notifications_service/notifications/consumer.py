"""
Notification Service RabbitMQ Consumer
Listens for notification events and sends emails
"""

import os
import sys
import django
import json
import logging
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_notifications_service.settings')
django.setup()

# Add common directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

from rabbitmq_client import get_rabbitmq_client
from notifications.models import Notification, NotificationTemplate
from notifications.tasks import send_notification_email
from django.template import Template, Context

logger = logging.getLogger(__name__)


class NotificationConsumer:
    """Consumes notification events from RabbitMQ and creates notifications"""
    
    def __init__(self):
        self.rabbitmq = get_rabbitmq_client()
        
        # Template name mapping
        self.template_map = {
            'notification.email.loan_created': 'loan_created',
            'notification.email.loan_returned_ontime': 'loan_returned_ontime',
            'notification.email.loan_returned_late': 'loan_returned_late',
            'notification.email.loan_renewed': 'loan_renewed',
            'notification.email.loan_overdue': 'loan_overdue',
            'notification.email.user_registered': 'user_registered',
        }
    
    def process_message(self, ch, method, properties, body):
        """
        Process incoming message from RabbitMQ
        
        Args:
            ch: Channel
            method: Method with routing_key
            properties: Message properties
            body: Message body (JSON)
        """
        try:
            # Parse message
            message = json.loads(body)
            routing_key = method.routing_key
            
            logger.info(f"📬 Received message: {routing_key} - {message.get('event_type')}")
            
            # Get template name from routing key
            template_name = self.template_map.get(routing_key)
            
            if not template_name:
                logger.warning(f"⚠️ No template mapping for routing key: {routing_key}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Get template from database
            try:
                template = NotificationTemplate.objects.get(name=template_name, is_active=True)
            except NotificationTemplate.DoesNotExist:
                logger.error(f"❌ Template not found: {template_name}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Render template with message data
            subject = self.render_template(template.subject_template, message)
            body_text = self.render_template(template.message_template, message)
            
            # Create notification in database
            notification = Notification.objects.create(
                user_id=message.get('user_id'),
                type=template.type,
                subject=subject,
                message=body_text,
                status='PENDING'
            )
            
            logger.info(f"✅ Created notification #{notification.id} for user #{message.get('user_id')}")
            
            # Send immediately via Celery
            send_notification_email.delay(notification.id)
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"✅ Message acknowledged: {routing_key}")
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}", exc_info=True)
            # Requeue on error (will retry)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def render_template(self, template_str, context_data):
        """
        Render Django template with context
        
        Args:
            template_str: Template string
            context_data: Dictionary of context variables
        
        Returns:
            Rendered string
        """
        try:
            # Create a copy to avoid modifying the original message
            # This is critical because this function is called twice (subject and body)
            # and modifying dates in-place causes the second call to fail
            ctx = context_data.copy()
            
            # Format dates if present
            if 'loan_date' in ctx and isinstance(ctx['loan_date'], str):
                try:
                    ctx['loan_date'] = datetime.fromisoformat(ctx['loan_date']).strftime('%d/%m/%Y')
                except ValueError:
                    pass # Already formatted or invalid
            
            if 'due_date' in ctx and isinstance(ctx['due_date'], str):
                try:
                    ctx['due_date'] = datetime.fromisoformat(ctx['due_date']).strftime('%d/%m/%Y')
                except ValueError:
                    pass
            
            if 'return_date' in ctx and isinstance(ctx['return_date'], str):
                try:
                    ctx['return_date'] = datetime.fromisoformat(ctx['return_date']).strftime('%d/%m/%Y')
                except ValueError:
                    pass
            
            if 'old_due_date' in ctx and isinstance(ctx['old_due_date'], str):
                try:
                    ctx['old_due_date'] = datetime.fromisoformat(ctx['old_due_date']).strftime('%d/%m/%Y')
                except ValueError:
                    pass
            
            if 'new_due_date' in ctx and isinstance(ctx['new_due_date'], str):
                try:
                    ctx['new_due_date'] = datetime.fromisoformat(ctx['new_due_date']).strftime('%d/%m/%Y')
                except ValueError:
                    pass
            
            template = Template(template_str)
            context = Context(ctx)
            return template.render(context)
            
        except Exception as e:
            logger.error(f"❌ Template rendering error: {e}")
            return template_str
    
    def start(self):
        """Start consuming messages"""
        logger.info("🚀 Starting Notification Consumer...")
        
        # Define routing keys to listen to
        routing_keys = [
            'notification.email.*',  # All email notifications
        ]
        
        # Start consuming
        self.rabbitmq.consume(
            queue_name='notification_queue',
            routing_keys=routing_keys,
            callback=self.process_message
        )


def main():
    """Main entry point for consumer"""
    try:
        consumer = NotificationConsumer()
        consumer.start()
    except KeyboardInterrupt:
        logger.info("🛑 Consumer stopped by user")
    except Exception as e:
        logger.error(f"❌ Consumer error: {e}", exc_info=True)


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    main()