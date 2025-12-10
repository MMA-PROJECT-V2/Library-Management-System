from rest_framework.permissions import BasePermission


class HasBookPermission(BasePermission):

    def has_permission(self, request, view):
        """
        Check if user has required permissions for this view.
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin has all permissions
        if hasattr(request.user, 'is_admin') and request.user.is_admin():
            return True
        
        # Get required permissions from view
        required_permissions = getattr(view, 'required_permissions', [])
        
        if not required_permissions:
            # No specific permissions required, just authentication
            return True
        
        # Check if user has all required permissions
        if hasattr(request.user, 'has_all_permissions'):
            return request.user.has_all_permissions(required_permissions)
        
        # Fallback: check individual permissions
        return all(
            hasattr(request.user, 'has_permission') and 
            request.user.has_permission(perm) 
            for perm in required_permissions
        )
    


class CanViewBooks(BasePermission):
    """Permission to view books (all users)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_view_books')

class CanAddBook(BasePermission):
    """Permission to add books (librarian, admin)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_add_book')

class CanEditBook(BasePermission):
    """Permission to edit books (librarian, admin)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_edit_book')
    

class CanDeleteBook(BasePermission):
    """Permission to delete books (librarian, admin)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_delete_book')


class CanBorrowBook(BasePermission):
    """Permission to borrow books (members)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_borrow_book')


class IsLibrarianOrAdmin(BasePermission):
    """Check if user is a librarian or admin."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if hasattr(request.user, 'is_librarian') and request.user.is_librarian():
            return True
        
        if hasattr(request.user, 'is_admin') and request.user.is_admin():
            return True
        
        return False


class IsMember(BasePermission):
    """Check if user is a member (can borrow books)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'is_member') and request.user.is_member()    