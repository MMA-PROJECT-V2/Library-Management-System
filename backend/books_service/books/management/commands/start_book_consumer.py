"""
Django management command to start the Books Service RabbitMQ consumer
Usage: python manage.py start_book_consumer
"""

from django.core.management.base import BaseCommand
from books.consumer import BookConsumer
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Starts the Books Service RabbitMQ Consumer'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting Books Service Consumer...'))
        try:
            consumer = BookConsumer()
            consumer.start()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Consumer stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Consumer crashed: {e}'))
