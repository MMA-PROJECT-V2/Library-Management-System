from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """Check if user is authenticated."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class CanCreateNotification(BasePermission):
    """Permission to create notifications (Librarians and Admins)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_create_notification')


class CanViewNotifications(BasePermission):
    """Permission to view notifications."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Users can view their own notifications
        # Librarians/Admins can view all
        return request.user.has_permission('can_view_notifications')


class CanManageNotifications(BasePermission):
    """Permission to manage (update/delete) notifications (Admins only)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_manage_notifications')


class CanManageTemplates(BasePermission):
    """Permission to manage templates (Librarians and Admins)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_manage_templates')


class IsLibrarianOrAdmin(BasePermission):
    """Check if user is a librarian or admin."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_librarian() or request.user.is_admin()