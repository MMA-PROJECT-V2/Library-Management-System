"""
Unit tests for loans.permissions module.

Tests for all permission classes: IsAuthenticated, CanBorrowBook, CanViewLoans,
CanViewAllLoans, CanManageLoans, IsLibrarianOrAdmin.
"""
import pytest
from unittest.mock import Mock

from loans.permissions import (
    IsAuthenticated, CanBorrowBook, CanViewLoans,
    CanViewAllLoans, CanManageLoans, IsLibrarianOrAdmin
)


class MockUser:
    """Mock user for testing permissions."""
    
    def __init__(self, authenticated=True, permissions=None, role='MEMBER', is_superuser=False):
        self._is_authenticated = authenticated
        self._permissions = permissions or []
        self._role = role
        self._is_superuser = is_superuser
    
    @property
    def is_authenticated(self):
        return self._is_authenticated
    
    def has_permission(self, perm):
        return perm in self._permissions
    
    def is_member(self):
        return self._role == 'MEMBER'
    
    def is_librarian(self):
        return self._role == 'LIBRARIAN'
    
    def is_admin(self):
        return self._role == 'ADMIN' or self._is_superuser


class TestIsAuthenticated:
    """Tests for IsAuthenticated permission class."""
    
    @pytest.fixture
    def permission(self):
        return IsAuthenticated()
    
    @pytest.fixture
    def mock_view(self):
        return Mock()
    
    def test_authenticated_user_permitted(self, permission, mock_view):
        """Test authenticated user is permitted."""
        request = Mock()
        request.user = MockUser(authenticated=True)
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_unauthenticated_user_denied(self, permission, mock_view):
        """Test unauthenticated user is denied."""
        request = Mock()
        request.user = MockUser(authenticated=False)
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_no_user_denied(self, permission, mock_view):
        """Test no user is denied."""
        class MockRequest:
            user = None
        request = MockRequest()
        
        # When user is None, permission returns None (falsy) not False
        assert not permission.has_permission(request, mock_view)


class TestCanBorrowBook:
    """Tests for CanBorrowBook permission class."""
    
    @pytest.fixture
    def permission(self):
        return CanBorrowBook()
    
    @pytest.fixture
    def mock_view(self):
        return Mock()
    
    def test_granted_with_permission(self, permission, mock_view):
        """Test user with can_borrow_book permission is granted."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=['can_borrow_book'])
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_denied_without_permission(self, permission, mock_view):
        """Test user without can_borrow_book permission is denied."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=[])
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_denied_unauthenticated(self, permission, mock_view):
        """Test unauthenticated user is denied."""
        request = Mock()
        request.user = None
        
        assert permission.has_permission(request, mock_view) is False


class TestCanViewLoans:
    """Tests for CanViewLoans permission class."""
    
    @pytest.fixture
    def permission(self):
        return CanViewLoans()
    
    @pytest.fixture
    def mock_view(self):
        return Mock()
    
    def test_granted_with_permission(self, permission, mock_view):
        """Test user with can_view_loans permission is granted."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=['can_view_loans'])
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_denied_without_permission(self, permission, mock_view):
        """Test user without can_view_loans permission is denied."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=[])
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_denied_unauthenticated(self, permission, mock_view):
        """Test unauthenticated user is denied."""
        request = Mock()
        request.user = MockUser(authenticated=False)
        
        assert permission.has_permission(request, mock_view) is False


class TestCanViewAllLoans:
    """Tests for CanViewAllLoans permission class."""
    
    @pytest.fixture
    def permission(self):
        return CanViewAllLoans()
    
    @pytest.fixture
    def mock_view(self):
        return Mock()
    
    def test_granted_with_permission(self, permission, mock_view):
        """Test user with can_view_all_loans permission is granted."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=['can_view_all_loans'])
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_denied_without_permission(self, permission, mock_view):
        """Test user without can_view_all_loans permission is denied."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=['can_view_loans'])
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_denied_unauthenticated(self, permission, mock_view):
        """Test unauthenticated user is denied."""
        request = Mock()
        request.user = None
        
        assert permission.has_permission(request, mock_view) is False


class TestCanManageLoans:
    """Tests for CanManageLoans permission class."""
    
    @pytest.fixture
    def permission(self):
        return CanManageLoans()
    
    @pytest.fixture
    def mock_view(self):
        return Mock()
    
    def test_granted_with_permission(self, permission, mock_view):
        """Test user with can_manage_loans permission is granted."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=['can_manage_loans'])
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_denied_without_permission(self, permission, mock_view):
        """Test user without can_manage_loans permission is denied."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=['can_view_loans'])
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_denied_unauthenticated(self, permission, mock_view):
        """Test unauthenticated user is denied."""
        request = Mock()
        request.user = MockUser(authenticated=False)
        
        assert permission.has_permission(request, mock_view) is False


class TestIsLibrarianOrAdmin:
    """Tests for IsLibrarianOrAdmin permission class."""
    
    @pytest.fixture
    def permission(self):
        return IsLibrarianOrAdmin()
    
    @pytest.fixture
    def mock_view(self):
        return Mock()
    
    def test_librarian_permitted(self, permission, mock_view):
        """Test librarian is permitted."""
        request = Mock()
        request.user = MockUser(authenticated=True, role='LIBRARIAN')
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_admin_permitted(self, permission, mock_view):
        """Test admin is permitted."""
        request = Mock()
        request.user = MockUser(authenticated=True, role='ADMIN')
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_superuser_permitted(self, permission, mock_view):
        """Test superuser is permitted."""
        request = Mock()
        request.user = MockUser(authenticated=True, role='MEMBER', is_superuser=True)
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_member_denied(self, permission, mock_view):
        """Test member is denied."""
        request = Mock()
        request.user = MockUser(authenticated=True, role='MEMBER')
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_unauthenticated_denied(self, permission, mock_view):
        """Test unauthenticated user is denied."""
        request = Mock()
        request.user = None
        
        assert permission.has_permission(request, mock_view) is False
