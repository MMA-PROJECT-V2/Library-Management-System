import os
import sys
import django

# Ensure Django settings are configured for tests within books_service
PROJECT_ROOT = os.path.dirname(__file__)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'books_service.settings')

# Configure Django for pytest
django.setup()