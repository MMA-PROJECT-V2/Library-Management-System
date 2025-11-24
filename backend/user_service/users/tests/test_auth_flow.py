"""
Integration tests for authentication flow across services.
"""

import pytest


@pytest.mark.integration
class TestAuthenticationFlow:
    """Test JWT authentication works across all services."""
    
    def test_user_can_register_and_login(self, wait_for_services, test_user_credentials):
        """Test user registration and login flow."""
        import requests
        
        # Register (or login if exists)
        response = requests.post(
            "http://localhost:8001/api/users/register/",
            json=test_user_credentials
        )
        
        assert response.status_code in [200, 201, 400]
        
        # If already exists, login
        if response.status_code == 400:
            response = requests.post(
                "http://localhost:8001/api/users/login/",
                json={
                    "email": test_user_credentials["email"],
                    "password": test_user_credentials["password"]
                }
            )
            assert response.status_code == 200
        
        data = response.json()
        assert "access" in data
        assert "refresh" in data
    
    def test_token_works_across_services(self, auth_token, auth_headers):
        """Test JWT token is accepted by all services."""
        import requests
        
        services = [
            ("user-service", "http://localhost:8001/api/users/me/"),
            ("books-service", "http://localhost:8002/api/books/"),
            ("loans-service", "http://localhost:8003/api/loans/"),
        ]
        
        for service_name, url in services:
            try:
                response = requests.get(url, headers=auth_headers, timeout=5)
                # Should get 200 or 403, but not 401 (means token validated)
                assert response.status_code in [200, 403], \
                    f"{service_name} rejected valid token"
            except requests.RequestException:
                pytest.skip(f"{service_name} not available")
    
    def test_user_service_validates_token(self, user_service_client, auth_token):
        """Test user service validates tokens correctly."""
        result = user_service_client.validate_token(auth_token)
        
        assert result["valid"] is True
        assert "user" in result
        assert "permissions" in result["user"]


@pytest.mark.integration
class TestPermissionFlow:
    """Test permission checking across services."""
    
    def test_books_service_checks_permissions(
        self, books_service_client, user_service_client, auth_token
    ):
        """Test books service validates permissions via user service."""
        
        # Check if user has permission to view books
        perm_result = user_service_client.check_permission(
            auth_token, 
            "can_view_books"
        )
        
        # Try to list books
        books_response = books_service_client.list_books()
        
        # If user has permission, books should be accessible
        if perm_result.get("allowed"):
            assert books_response.status_code == 200
        else:
            assert books_response.status_code == 403