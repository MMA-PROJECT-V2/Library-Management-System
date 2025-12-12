from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.template import Template, Context, TemplateSyntaxError
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Notification, NotificationTemplate, NotificationLog
from .serializers import (
    NotificationSerializer,
    SendFromTemplateSerializer,
    NotificationLogSerializer,
)
from .tasks import send_notification_email, send_notification_sms
from .permissions import CanCreateNotification, CanViewNotifications, IsLibrarianOrAdmin

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_notification(request):
    """
    POST /notifications/
    Create a new notification and send it immediately.
    """
    data = request.data.copy()
    
    # Allow any authenticated service to create notifications
    # This is required for inter-service communication (Loans/Books services creating notifications)

    if 'status' not in data:
        data['status'] = 'PENDING'
    
    serializer = NotificationSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    notification = serializer.save()
    
    # Send immediately
    try:
        if notification.type == 'EMAIL':
            send_notification_email.delay(notification.id)
        elif notification.type == 'SMS':
             send_notification_sms.delay(notification.id)
        
        # Refresh to get updated status
        notification.refresh_from_db()
        
    except Exception as e:
        logger.error(f"Failed to send notification {notification.id}: {e}")
    
    return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Allow any authenticated service to use templates
def send_from_template(request):
    """
    POST /notifications/send_from_template/
    """
    serializer = SendFromTemplateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    
    template = get_object_or_404(NotificationTemplate, pk=data['template_id'])
    
    if not template.is_active:
        return Response({"detail": "Template is inactive"}, status=status.HTTP_400_BAD_REQUEST)
    
    ctx = data.get('context') or {}
    
    try:
        subject_template = Template(template.subject_template)
        message_template = Template(template.message_template)
        
        subject = subject_template.render(Context(ctx))
        message = message_template.render(Context(ctx))
        
        logger.info(f"Template '{template.name}' rendered. Message length: {len(message)} chars")
        logger.debug(f"Rendered message: {message[:200]}...")  # Log first 200 chars
    except (TemplateSyntaxError, Exception) as e:
        logger.error(f"Template rendering error: {e}")
        return Response({"detail": f"Template error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    notif = Notification.objects.create(
        user_id=data['user_id'],
        type=data.get('type', template.type),
        subject=subject,
        message=message,
        status='PENDING'
    )
    
    # Send immediately
    try:
        if notif.type == 'EMAIL':
            send_notification_email.delay(notif.id)
        elif notif.type == 'SMS':
            send_notification_sms.delay(notif.id)
            
        notif.refresh_from_db()
    except Exception as e:
        logger.error(f"Failed to send notification {notif.id}: {e}")
        
    return Response(NotificationSerializer(notif).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewNotifications])
def user_notifications(request):
    """
    GET /notifications/user_notifications/
    Fetch notifications for a specific user (or current user).
    """
    user_id = request.query_params.get('user_id')
    
    # Security check: Admins can see any, users can only see their own
    if user_id:
        if not request.user.is_superuser and str(request.user.id) != str(user_id):
             return Response(
                {"detail": "You don't have permission to view these notifications"},
                status=status.HTTP_403_FORBIDDEN
            )
        target_user_id = user_id
    else:
        # Default to current user
        target_user_id = request.user.id
        
    qs = Notification.objects.filter(user_id=target_user_id).order_by('-created_at')
    
    serializer = NotificationSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsLibrarianOrAdmin])
def stats(request):
    """
    GET /notifications/stats/
    """
    days = int(request.query_params.get('days', 30))
    date_from = timezone.now() - timedelta(days=days)
    
    qs = Notification.objects.filter(created_at__gte=date_from)
    
    status_counts = qs.values('status').annotate(count=Count('id'))
    type_counts = qs.values('type').annotate(count=Count('id'))
    
    total = qs.count()
    sent = qs.filter(status='SENT').count()
    failed = qs.filter(status='FAILED').count()
    pending = qs.filter(status='PENDING').count()
    
    success_rate = (sent / total * 100) if total > 0 else 0
    
    return Response({
        "period_days": days,
        "total_notifications": total,
        "by_status": {item['status']: item['count'] for item in status_counts},
        "by_type": {item['type']: item['count'] for item in type_counts},
        "success_rate": round(success_rate, 2),
        "counts": {
            "sent": sent,
            "failed": failed,
            "pending": pending
        }
    })


# ============================================
#    ADDITIONAL ENDPOINTS
# ============================================

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    GET /health/
    Health check endpoint
    """
    return Response({
        'status': 'healthy',
        'service': 'notifications',
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsLibrarianOrAdmin])
def list_all_notifications(request):
    """
    GET /api/all_notifications/
    List all notifications (admin only)
    """
    notifications = Notification.objects.all().order_by('-created_at')[:100]
    serializer = NotificationSerializer(notifications, many=True)
    return Response({
        'count': len(notifications),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_notifications_by_id(request, user_id):
    """
    GET /api/notifications/user/<user_id>/
    Get notifications for a specific user
    """
    # Users can only see their own notifications unless they're admin
    if str(user_id) != str(request.user.id):
        if not (request.user.has_permission('can_view_all_notifications') or request.user.is_superuser):
            return Response(
                {"detail": "You don't have permission to view other users' notifications"},
                status=status.HTTP_403_FORBIDDEN
            )
    
    notifications = Notification.objects.filter(user_id=user_id).order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response({
        'user_id': user_id,
        'count': len(notifications),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsLibrarianOrAdmin])
def get_pending_notifications(request):
    """
    GET /api/notifications/pending/
    Get all pending notifications (admin only)
    """
    notifications = Notification.objects.filter(status='PENDING').order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response({
        'count': len(notifications),
        'results': serializer.data
    })