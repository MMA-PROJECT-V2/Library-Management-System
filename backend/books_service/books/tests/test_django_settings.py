import pytest
import os
from django.conf import settings


@pytest.mark.django_db
class TestDjangoSettings:
    """Test Django settings configuration."""
    
    def test_secret_key_configured(self):
        """Verify SECRET_KEY is set."""
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) > 0
    
    def test_debug_setting(self):
        """Verify DEBUG setting."""
        assert isinstance(settings.DEBUG, bool)
    
    def test_databases_configured(self):
        """Verify database configuration."""
        assert 'default' in settings.DATABASES
        db_config = settings.DATABASES['default']
        assert 'ENGINE' in db_config
        assert 'NAME' in db_config
    
    def test_installed_apps(self):
        """Verify required apps are installed."""
        required_apps = ['django.contrib.admin', 'rest_framework', 'books', 'corsheaders']
        for app in required_apps:
            assert app in settings.INSTALLED_APPS, f"{app} not in INSTALLED_APPS"
    
    def test_allowed_hosts(self):
        """Verify ALLOWED_HOSTS is configured."""
        assert hasattr(settings, 'ALLOWED_HOSTS')
        assert isinstance(settings.ALLOWED_HOSTS, (list, tuple))
    
    def test_middleware_configured(self):
        """Verify middleware is set."""
        assert hasattr(settings, 'MIDDLEWARE')
        assert len(settings.MIDDLEWARE) > 0
    
    def test_rest_framework_config(self):
        """Verify REST Framework settings."""
        assert hasattr(settings, 'REST_FRAMEWORK')
        assert isinstance(settings.REST_FRAMEWORK, dict)
    
    def test_cors_allowed_origins(self):
        """Verify CORS configuration."""
        assert hasattr(settings, 'CORS_ALLOWED_ORIGINS')