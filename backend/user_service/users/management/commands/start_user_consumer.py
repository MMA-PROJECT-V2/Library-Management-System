"""
Django management command to start the User Service RabbitMQ consumer
Usage: python manage.py start_user_consumer
"""

from django.core.management.base import BaseCommand
from users.consumer import UserConsumer
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Starts the User Service RabbitMQ Consumer'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting User Service Consumer...'))
        try:
            consumer = UserConsumer()
            consumer.start()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Consumer stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Consumer crashed: {e}'))
