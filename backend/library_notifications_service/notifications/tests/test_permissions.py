from django.test import TestCase
from unittest.mock import MagicMock
from notifications.permissions import (
    IsAuthenticated, 
    CanCreateNotification, 
    CanViewNotifications, 
    CanManageNotifications, 
    CanManageTemplates, 
    IsLibrarianOrAdmin
)

class PermissionsTest(TestCase):
    def setUp(self):
        self.user = MagicMock()
        self.request = MagicMock()
        self.request.user = self.user
        self.view = MagicMock()

    def test_is_authenticated(self):
        perm = IsAuthenticated()
        
        self.user.is_authenticated = True
        self.assertTrue(perm.has_permission(self.request, self.view))
        
        self.user.is_authenticated = False
        self.assertFalse(perm.has_permission(self.request, self.view))
        
        self.request.user = None
        self.assertFalse(perm.has_permission(self.request, self.view))

    def test_can_create_notification(self):
        perm = CanCreateNotification()
        self.user.is_authenticated = True
        
        self.user.has_permission.return_value = True
        self.assertTrue(perm.has_permission(self.request, self.view))
        self.user.has_permission.assert_called_with('can_create_notification')
        
        self.user.has_permission.return_value = False
        self.assertFalse(perm.has_permission(self.request, self.view))

    def test_can_view_notifications(self):
        perm = CanViewNotifications()
        self.user.is_authenticated = True
        
        self.user.has_permission.return_value = True
        self.assertTrue(perm.has_permission(self.request, self.view))
        self.user.has_permission.assert_called_with('can_view_notifications')
        
        self.user.has_permission.return_value = False
        self.assertFalse(perm.has_permission(self.request, self.view))

    def test_can_manage_notifications(self):
        perm = CanManageNotifications()
        self.user.is_authenticated = True
        
        self.user.has_permission.return_value = True
        self.assertTrue(perm.has_permission(self.request, self.view))
        self.user.has_permission.assert_called_with('can_manage_notifications')

    def test_can_manage_templates(self):
        perm = CanManageTemplates()
        self.user.is_authenticated = True
        
        self.user.has_permission.return_value = True
        self.assertTrue(perm.has_permission(self.request, self.view))
        self.user.has_permission.assert_called_with('can_manage_templates')

    def test_is_librarian_or_admin(self):
        perm = IsLibrarianOrAdmin()
        self.user.is_authenticated = True
        
        # User is Librarian
        self.user.is_librarian.return_value = True
        self.user.is_admin.return_value = False
        self.assertTrue(perm.has_permission(self.request, self.view))
        
        # User is Admin
        self.user.is_librarian.return_value = False
        self.user.is_admin.return_value = True
        self.assertTrue(perm.has_permission(self.request, self.view))
        
        # User is neither
        self.user.is_librarian.return_value = False
        self.user.is_admin.return_value = False
        self.assertFalse(perm.has_permission(self.request, self.view))
