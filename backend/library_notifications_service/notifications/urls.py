# notifications/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from .views import NotificationViewSet, NotificationTemplateViewSet

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"templates", NotificationTemplateViewSet, basename="template")

@api_view(['GET'])
def health_check(request):
    """Health check endpoint for monitoring."""
    return Response({
        'status': 'healthy',
        'service': 'notifications',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('', include(router.urls)),
]