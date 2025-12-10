# permissions.py
from rest_framework.permissions import BasePermission


class CanCreateNotification(BasePermission):
    """Permission to create notifications."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_create_notification')


class CanViewNotifications(BasePermission):
    """Permission to view notifications."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_view_notifications')


class CanManageNotifications(BasePermission):
    """Permission to manage (update/delete) notifications."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_permission('can_manage_notifications')


class CanManageTemplates(BasePermission):
    """Permission to manage templates."""
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


class IsMember(BasePermission):
    """Check if user is a member."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_member()