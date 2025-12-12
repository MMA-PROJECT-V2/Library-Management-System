from django.contrib import admin
from django.utils.html import format_html
from .models import Notification, NotificationTemplate, NotificationLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "user_id", 
        "type", 
        "subject_preview", 
        "status_badge", 
        "sent_at", 
        "created_at"
    )
    list_filter = ("type", "status", "created_at", "sent_at")
    search_fields = ("user_id", "subject", "message")
    readonly_fields = ("id", "created_at", "updated_at", "sent_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("id", "user_id", "type", "status")
        }),
        ("Content", {
            "fields": ("subject", "message")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at", "sent_at")
        }),
    )
    
    def subject_preview(self, obj):
        """Show truncated subject."""
        if len(obj.subject) > 50:
            return f"{obj.subject[:50]}..."
        return obj.subject
    subject_preview.short_description = "Subject"
    
    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            "PENDING": "orange",
            "SENT": "green",
            "FAILED": "red"
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.status
        )
    status_badge.short_description = "Status"
    
    actions = ["mark_as_pending", "mark_as_sent", "mark_as_failed"]
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status="PENDING")
        self.message_user(request, f"{updated} notifications marked as PENDING")
    mark_as_pending.short_description = "Mark as PENDING"
    
    def mark_as_sent(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status="SENT", sent_at=timezone.now())
        self.message_user(request, f"{updated} notifications marked as SENT")
    mark_as_sent.short_description = "Mark as SENT"
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status="FAILED")
        self.message_user(request, f"{updated} notifications marked as FAILED")
    mark_as_failed.short_description = "Mark as FAILED"


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "type",
        "is_active_badge",
        "created_at",
        "updated_at"
    )
    list_filter = ("type", "is_active", "created_at")
    search_fields = ("name", "description", "subject_template", "message_template")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("name",)
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("id", "name", "type", "is_active", "description")
        }),
        ("Templates", {
            "fields": ("subject_template", "message_template")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )
    
    def is_active_badge(self, obj):
        """Display active status with color coding."""
        if obj.is_active:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: gray; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    is_active_badge.short_description = "Status"
    
    actions = ["activate_templates", "deactivate_templates"]
    
    def activate_templates(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} templates activated")
    activate_templates.short_description = "Activate selected templates"
    
    def deactivate_templates(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} templates deactivated")
    deactivate_templates.short_description = "Deactivate selected templates"


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "notification_id",
        "notification_user",
        "status_badge",
        "detail_preview",
        "created_at"
    )
    list_filter = ("status", "created_at")
    search_fields = ("notification__id", "notification__user_id", "detail")
    readonly_fields = ("id", "notification", "status", "detail", "created_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    
    def notification_user(self, obj):
        """Show the user_id of the associated notification."""
        return obj.notification.user_id
    notification_user.short_description = "User ID"
    
    def detail_preview(self, obj):
        """Show truncated detail."""
        if len(obj.detail) > 50:
            return f"{obj.detail[:50]}..."
        return obj.detail
    detail_preview.short_description = "Detail"
    
    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            "PENDING": "orange",
            "SENT": "green",
            "FAILED": "red"
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.status
        )
    status_badge.short_description = "Status"
    
    def has_add_permission(self, request):
        """Disable manual creation of logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make logs read-only."""
        return False