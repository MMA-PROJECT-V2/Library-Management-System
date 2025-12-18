import os
import pytest
from django.conf import settings

class TestSettings:
    def test_debug_mode(self):
        # Test DEBUG setting
        assert hasattr(settings, 'DEBUG')
    
    def test_database_config(self):
        # Test database configuration
        assert 'default' in settings.DATABASES
        assert settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql'
    
    def test_installed_apps(self):
        # Test required apps are installed
        assert 'rest_framework' in settings.INSTALLED_APPS
        assert 'books' in settings.INSTALLED_APPS
        assert 'corsheaders' in settings.INSTALLED_APPS
    
    def test_secret_key_exists(self):
        # Test SECRET_KEY is set
        assert len(settings.SECRET_KEY) > 0
    
    def test_allowed_hosts(self):
        # Test ALLOWED_HOSTS
        assert hasattr(settings, 'ALLOWED_HOSTS')
        assert isinstance(settings.ALLOWED_HOSTS, list)