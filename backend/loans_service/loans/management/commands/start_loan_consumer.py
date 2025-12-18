"""
Django management command to start the Loan Service RabbitMQ consumer
Usage: python manage.py start_loan_consumer
"""

from django.core.management.base import BaseCommand
from loans.consumer import LoanConsumer
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Starts the Loan Service RabbitMQ Consumer'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting Loan Service Consumer...'))
        try:
            consumer = LoanConsumer()
            consumer.start()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Consumer stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Consumer crashed: {e}'))
