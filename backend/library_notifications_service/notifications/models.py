from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        ("EMAIL", "Email"),
        ("SMS", "SMS"),
    ]
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SENT", "Sent"),
        ("FAILED", "Failed"),
    ]
    
    user_id = models.IntegerField(db_index=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, db_index=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default="PENDING",
        db_index=True
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user_id", "status"]),
            models.Index(fields=["type", "status"]),
            models.Index(fields=["created_at", "status"]),
        ]

    def __str__(self):
        return f"Notification {self.id} to user {self.user_id} ({self.status})"


class NotificationTemplate(models.Model):
    """
    Templates used to create notifications.
    Uses Django template syntax for rendering with context.
    """
    name = models.CharField(max_length=150, unique=True, db_index=True)
    type = models.CharField(max_length=10, choices=Notification.TYPE_CHOICES)
    subject_template = models.CharField(max_length=255)
    message_template = models.TextField()
    description = models.TextField(blank=True, help_text="Template description for reference")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_templates"
        ordering = ["name"]

    def __str__(self):
        return f"Template {self.name} ({self.type})"


class NotificationLog(models.Model):
    """
    Log entries for attempts to deliver notifications.
    """
    notification = models.ForeignKey(
        Notification, 
        on_delete=models.CASCADE, 
        related_name="logs"
    )
    status = models.CharField(max_length=20, choices=Notification.STATUS_CHOICES)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "notification_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Log for notif {self.notification_id} - {self.status}"