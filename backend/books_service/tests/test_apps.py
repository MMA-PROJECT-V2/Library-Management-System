"""
Unit tests for books.apps module.
"""
import pytest
from django.apps import apps


class TestBooksConfig:
    """Tests for BooksConfig app configuration."""
    
    def test_app_name(self):
        """Test that app name is correctly configured."""
        app_config = apps.get_app_config('books')
        assert app_config.name == 'books'
    
    def test_app_is_installed(self):
        """Test that books app is installed."""
        assert apps.is_installed('books')
