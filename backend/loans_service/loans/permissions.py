from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """Check if user is authenticated."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class CanBorrowBook(BasePermission):
    """Permission to borrow books (members)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_borrow_book')


class CanViewLoans(BasePermission):
    """Permission to view own loans."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_view_loans')


class CanViewAllLoans(BasePermission):
    """Permission to view all loans (librarians and admins)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_view_all_loans')


class CanManageLoans(BasePermission):
    """Permission to manage loans (librarians and admins)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_manage_loans')


class IsLibrarianOrAdmin(BasePermission):
    """Check if user is a librarian or admin."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.is_librarian() or request.user.is_admin()