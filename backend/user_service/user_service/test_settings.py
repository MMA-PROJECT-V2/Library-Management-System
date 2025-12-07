"""
Django test settings for user_service.
Uses SQLite for faster tests, can be overridden with environment variables.
"""

from .settings import *
import os

# Override database for tests (use SQLite for speed, or MySQL if specified)
if os.environ.get('USE_MYSQL_FOR_TESTS', '').lower() == 'true':
    # Use MySQL if explicitly requested (e.g., in CI)
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.mysql'),
            'NAME': os.environ.get('DB_NAME', 'library_test'),
            'USER': os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'root'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'TEST': {
                'NAME': os.environ.get('DB_NAME', 'library_test'),
            }
        }
    }
else:
    # Default: Use SQLite for faster tests
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

# Disable migrations for faster tests (use if models are stable)
# PASSWORD_HASHERS = [
#     'django.contrib.auth.hashers.MD5PasswordHasher',  # Faster for tests
# ]

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
}

# Disable cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Test secret key
SECRET_KEY = 'test-secret-key-for-testing-only'

# Disable debug toolbar and other dev tools
DEBUG = False

# Email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Celery (if used) - use eager mode for tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

