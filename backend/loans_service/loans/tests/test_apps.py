"""
Unit tests for loans.apps module.
"""
import pytest
from django.apps import apps


class TestLoansConfig:
    """Tests for LoansConfig app configuration."""
    
    def test_app_name(self):
        """Test that app name is correctly configured."""
        app_config = apps.get_app_config('loans')
        assert app_config.name == 'loans'
    
    def test_app_is_installed(self):
        """Test that loans app is installed."""
        assert apps.is_installed('loans')
