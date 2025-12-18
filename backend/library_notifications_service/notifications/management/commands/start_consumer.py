"""
Django management command to start the RabbitMQ consumer
Usage: python manage.py start_consumer
"""

from django.core.management.base import BaseCommand
from notifications.consumer import NotificationConsumer
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start RabbitMQ consumer for notification service'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting RabbitMQ consumer...'))
        
        try:
            consumer = NotificationConsumer()
            consumer.start()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nConsumer stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Consumer error: {e}'))
            raise