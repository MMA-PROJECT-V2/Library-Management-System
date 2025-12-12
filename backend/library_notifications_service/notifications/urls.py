from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health-check'),
    
    # Notification endpoints
    path('all_notifications/', views.list_all_notifications, name='list-all-notifications'),
    path('notifications/', views.create_notification, name='create-notification'),
    path('notifications/send_from_template/', views.send_from_template, name='send-from-template'),
    path('notifications/user/<int:user_id>/', views.get_user_notifications_by_id, name='user-notifications-by-id'),
    path('notifications/user_notifications/', views.user_notifications, name='user-notifications'),
    path('notifications/pending/', views.get_pending_notifications, name='pending-notifications'),
    path('notifications/stats/', views.stats, name='notification-stats'),
]