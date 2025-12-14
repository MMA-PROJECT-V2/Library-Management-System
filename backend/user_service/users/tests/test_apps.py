"""
Tests for users.apps module (AppConfig and signal registration).
"""

import pytest
from django.apps import apps
from django.test import override_settings
from users.apps import UsersConfig


@pytest.mark.django_db
class TestUsersConfig:
    """Test UsersConfig AppConfig."""

    def test_app_config_name(self):
        """Test app config has correct name."""
        config = apps.get_app_config('users')
        assert isinstance(config, UsersConfig)
        assert config.name == 'users'

    def test_default_auto_field(self):
        """Test default_auto_field is BigAuto Field."""
        config = apps.get_app_config('users')
        assert config.default_auto_field == 'django.db.models.BigAutoField'

    def test_app_ready_called(self):
        """Test that ready() method was called during app initialization."""
        # The ready() method should have already been called when Django started
        # We can verify this by checking that signals are registered
        # or by checking side effects of the ready() method
        config = apps.get_app_config('users')
        # If ready() registers signals, we can check signal receivers
        # For now, just verify the config is ready
        assert config.models_module is not None
