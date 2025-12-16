"""
Unit tests for books.permissions module.

Tests for all permission classes: HasBookPermission, CanViewBooks, CanAddBook,
CanEditBook, CanDeleteBook, CanBorrowBook, IsLibrarianOrAdmin, IsMember.
"""
import pytest
from unittest.mock import Mock

from books.permissions import (
    HasBookPermission, CanViewBooks, CanAddBook, CanEditBook,
    CanDeleteBook, CanBorrowBook, IsLibrarianOrAdmin, IsMember
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
    
    def has_all_permissions(self, perms):
        return all(perm in self._permissions for perm in perms)
    
    def is_member(self):
        return self._role == 'MEMBER'
    
    def is_librarian(self):
        return self._role == 'LIBRARIAN'
    
    def is_admin(self):
        return self._role == 'ADMIN' or self._is_superuser


class TestHasBookPermission:
    """Tests for HasBookPermission class."""
    
    @pytest.fixture
    def permission(self):
        return HasBookPermission()
    
    @pytest.fixture
    def mock_view(self):
        view = Mock()
        view.required_permissions = []
        return view
    
    def test_unauthenticated_user_denied(self, permission, mock_view):
        """Test unauthenticated user is denied."""
        request = Mock()
        request.user = None
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_unauthenticated_user_explicit_denied(self, permission, mock_view):
        """Test user with is_authenticated=False is denied."""
        request = Mock()
        request.user = MockUser(authenticated=False)
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_admin_always_permitted(self, permission, mock_view):
        """Test admin user is always permitted."""
        request = Mock()
        request.user = MockUser(authenticated=True, role='ADMIN')
        mock_view.required_permissions = ['some_permission']
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_no_required_permissions(self, permission, mock_view):
        """Test authenticated user is permitted when no permissions required."""
        request = Mock()
        request.user = MockUser(authenticated=True)
        mock_view.required_permissions = []
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_user_with_all_required_permissions(self, permission, mock_view):
        """Test user with all required permissions is permitted."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=['perm1', 'perm2'])
        mock_view.required_permissions = ['perm1', 'perm2']
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_user_missing_permissions(self, permission, mock_view):
        """Test user missing required permissions is denied."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=['perm1'])
        mock_view.required_permissions = ['perm1', 'perm2']
        
        assert permission.has_permission(request, mock_view) is False


class TestCanViewBooks:
    """Tests for CanViewBooks permission class."""
    
    @pytest.fixture
    def permission(self):
        return CanViewBooks()
    
    @pytest.fixture
    def mock_view(self):
        return Mock()
    
    def test_granted_with_permission(self, permission, mock_view):
        """Test user with can_view_books permission is granted."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=['can_view_books'])
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_denied_without_permission(self, permission, mock_view):
        """Test user without can_view_books permission is denied."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=[])
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_denied_unauthenticated(self, permission, mock_view):
        """Test unauthenticated user is denied."""
        request = Mock()
        request.user = None
        
        assert permission.has_permission(request, mock_view) is False


class TestCanAddBook:
    """Tests for CanAddBook permission class."""
    
    @pytest.fixture
    def permission(self):
        return CanAddBook()
    
    @pytest.fixture
    def mock_view(self):
        return Mock()
    
    def test_granted_with_permission(self, permission, mock_view):
        """Test user with can_add_book permission is granted."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=['can_add_book'])
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_denied_without_permission(self, permission, mock_view):
        """Test user without can_add_book permission is denied."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=[])
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_denied_unauthenticated(self, permission, mock_view):
        """Test unauthenticated user is denied."""
        request = Mock()
        request.user = MockUser(authenticated=False)
        
        assert permission.has_permission(request, mock_view) is False


class TestCanEditBook:
    """Tests for CanEditBook permission class."""
    
    @pytest.fixture
    def permission(self):
        return CanEditBook()
    
    @pytest.fixture
    def mock_view(self):
        return Mock()
    
    def test_granted_with_permission(self, permission, mock_view):
        """Test user with can_edit_book permission is granted."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=['can_edit_book'])
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_denied_without_permission(self, permission, mock_view):
        """Test user without can_edit_book permission is denied."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=[])
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_denied_unauthenticated(self, permission, mock_view):
        """Test unauthenticated user is denied."""
        request = Mock()
        request.user = None
        
        assert permission.has_permission(request, mock_view) is False


class TestCanDeleteBook:
    """Tests for CanDeleteBook permission class."""
    
    @pytest.fixture
    def permission(self):
        return CanDeleteBook()
    
    @pytest.fixture
    def mock_view(self):
        return Mock()
    
    def test_granted_with_permission(self, permission, mock_view):
        """Test user with can_delete_book permission is granted."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=['can_delete_book'])
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_denied_without_permission(self, permission, mock_view):
        """Test user without can_delete_book permission is denied."""
        request = Mock()
        request.user = MockUser(authenticated=True, permissions=[])
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_denied_unauthenticated(self, permission, mock_view):
        """Test unauthenticated user is denied."""
        request = Mock()
        request.user = MockUser(authenticated=False)
        
        assert permission.has_permission(request, mock_view) is False


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


class TestIsMember:
    """Tests for IsMember permission class."""
    
    @pytest.fixture
    def permission(self):
        return IsMember()
    
    @pytest.fixture
    def mock_view(self):
        return Mock()
    
    def test_member_permitted(self, permission, mock_view):
        """Test member is permitted."""
        request = Mock()
        request.user = MockUser(authenticated=True, role='MEMBER')
        
        assert permission.has_permission(request, mock_view) is True
    
    def test_librarian_denied(self, permission, mock_view):
        """Test librarian is denied."""
        request = Mock()
        request.user = MockUser(authenticated=True, role='LIBRARIAN')
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_admin_denied(self, permission, mock_view):
        """Test admin is denied."""
        request = Mock()
        request.user = MockUser(authenticated=True, role='ADMIN')
        
        assert permission.has_permission(request, mock_view) is False
    
    def test_unauthenticated_denied(self, permission, mock_view):
        """Test unauthenticated user is denied."""
        request = Mock()
        request.user = MockUser(authenticated=False)
        
        assert permission.has_permission(request, mock_view) is False
