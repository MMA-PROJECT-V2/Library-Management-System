from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
    verbose_name = "Notifications Service"
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        """
        # Import signals if you have any
        # from . import signals
        pass
    