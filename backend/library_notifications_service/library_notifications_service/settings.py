"""
Django settings for library_notifications_service project.
"""

from pathlib import Path
from datetime import timedelta

try:
    from decouple import config
except ImportError:
    import os
    def config(key, default=None, cast=None):
        value = os.getenv(key, default)
        if cast and value is not None:
            try:
                return cast(value)
            except Exception:
                return value
        return value

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# SECURITY SETTINGS
# ============================================

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# ============================================
# INSTALLED APPS
# ============================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'corsheaders',
    'rest_framework',
    'django_celery_beat',
    'django_celery_results',

    # Local apps
    'notifications',
]

# ============================================
# MIDDLEWARE
# ============================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'library_notifications_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'library_notifications_service.wsgi.application'

# ============================================
# DATABASE CONFIGURATION
# ============================================

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.mysql'),
        'NAME': config('DB_NAME', default='library_notifications_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# ============================================
# CORS CONFIGURATION
# ============================================

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = config(
        'CORS_ALLOWED_ORIGINS',
        default='http://localhost:3000',
        cast=lambda v: [s.strip() for s in v.split(',')]
    )

# ============================================
# REST FRAMEWORK CONFIGURATION
# ============================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'notifications.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# ============================================
# PASSWORD VALIDATORS
# ============================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================
# INTERNATIONALIZATION
# ============================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = config('TIME_ZONE', default='UTC')
USE_I18N = True
USE_TZ = True

# ============================================
# STATIC & MEDIA FILES
# ============================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# EMAIL CONFIGURATION
# ============================================

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@library.com')
EMAIL_TIMEOUT = 10

# ============================================
# CELERY CONFIGURATION
# ============================================

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60
CELERY_RESULT_EXPIRES = 3600
CELERY_TASK_ALWAYS_EAGER = True


CELERY_BEAT_SCHEDULE = {
    'process-pending-notifications': {
        'task': 'notifications.tasks.process_pending_notifications',
        'schedule': timedelta(minutes=5),
    },
    'cleanup-old-logs': {
        'task': 'notifications.tasks.cleanup_old_logs',
        'schedule': timedelta(days=1),
        'kwargs': {'days': 30}
    },
    'cleanup-old-notifications': {
        'task': 'notifications.tasks.cleanup_old_notifications',
        'schedule': timedelta(days=1),
        'kwargs': {'days': 90}
    },
}

# ============================================
# MICROSERVICES CONFIGURATION
# ============================================

SERVICES = {
    'USER_SERVICE': config('USER_SERVICE_URL', default='http://localhost:8001'),
    'BOOK_SERVICE': config('BOOK_SERVICE_URL', default='http://localhost:8002'),
    'LOAN_SERVICE': config('LOAN_SERVICE_URL', default='http://localhost:8003'),
    'NOTIFICATION_SERVICE': config('NOTIFICATION_SERVICE_URL', default='http://localhost:8004'),
}

# Backward compatibility aliases
USER_SERVICE_URL = SERVICES['USER_SERVICE']
BOOK_SERVICE_URL = SERVICES['BOOK_SERVICE']
LOAN_SERVICE_URL = SERVICES['LOAN_SERVICE']
NOTIFICATION_SERVICE_URL = SERVICES['NOTIFICATION_SERVICE']

USER_SERVICE_TIMEOUT = config('USER_SERVICE_TIMEOUT', default=5, cast=int)

# ============================================
# LOGGING CONFIGURATION
# ============================================

LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
        'simple': {'format': '{levelname} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'level': 'INFO', 'class': 'logging.StreamHandler', 'formatter': 'simple'},
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'notifications.log',
            'maxBytes': 1024 * 1024 * 15,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'notifications': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
        'celery': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
    },
}

# ============================================
# SECURITY SETTINGS FOR PRODUCTION
# ============================================

if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
