from rest_framework import status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.template import Template, Context, TemplateSyntaxError
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Notification, NotificationTemplate, NotificationLog
from .serializers import (
    NotificationSerializer,
    NotificationTemplateSerializer,
    NotificationLogSerializer,
    SendFromTemplateSerializer,
)
from .tasks import send_notification_email, send_notification_sms
from .permissions import (
    CanCreateNotification,
    CanViewNotifications,
    CanManageNotifications,
    CanManageTemplates,
    IsLibrarianOrAdmin,
)

logger = logging.getLogger(__name__)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Notifications with template, stats, and bulk operations.
    
    Permissions:
        - List/Retrieve: CanViewNotifications
        - Create: CanCreateNotification
        - Update/Delete: CanManageNotifications
    
    Endpoints:
        - GET /notifications/ - List all notifications
        - POST /notifications/ - Create new notification
        - GET /notifications/{id}/ - Get specific notification
        - PUT /notifications/{id}/ - Update notification
        - DELETE /notifications/{id}/ - Delete notification
        - POST /notifications/{id}/retry/ - Retry failed notification
        - GET /notifications/user/{user_id}/ - Get user's notifications
        - GET /notifications/pending/ - Get pending notifications
        - GET /notifications/recent/ - Get recent notifications
        - GET /notifications/stats/ - Get statistics
        - POST /notifications/send_from_template/ - Create from template
        - POST /notifications/bulk_create/ - Create multiple notifications
    """
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer

    def get_permissions(self):
        """
        Instantiate and return the list of permissions for this view.
        """
        if self.action in ['list', 'retrieve', 'user_notifications', 'stats']:
            permission_classes = [IsAuthenticated, CanViewNotifications]
        elif self.action in ['create', 'send_from_template', 'bulk_create']:
            permission_classes = [IsAuthenticated, CanCreateNotification]
        elif self.action in ['update', 'partial_update', 'destroy', 'retry']:
            permission_classes = [IsAuthenticated, CanManageNotifications]
        elif self.action in ['pending', 'recent']:
            permission_classes = [IsAuthenticated, IsLibrarianOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Create a new notification and optionally queue it for sending.
        
        Query Parameters:
            - send_now (bool): If true, immediately queue for sending
        """
        data = request.data.copy()
        
        # Set default status if not provided
        if 'status' not in data:
            data['status'] = 'PENDING'
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()
        
        # Optionally queue for immediate sending
        send_now = request.query_params.get('send_now', 'false').lower() == 'true'
        if send_now and notification.status == 'PENDING':
            try:
                if notification.type == 'EMAIL':
                    send_notification_email.delay(notification.id)
                elif notification.type == 'SMS':
                    send_notification_sms.delay(notification.id)
                logger.info(f"Queued notification {notification.id} for immediate sending")
            except Exception as e:
                logger.error(f"Failed to queue notification {notification.id}: {e}")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Get a specific notification with optional logs.
        
        Query Parameters:
            - include_logs (bool): Include delivery logs
        """
        notification = get_object_or_404(self.queryset, pk=pk)
        
        # Check if user can view this notification
        if not request.user.is_admin() and notification.user_id != request.user.id:
            return Response(
                {"detail": "You don't have permission to view this notification"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(notification)
        data = serializer.data
        
        # Include logs if requested
        include_logs = request.query_params.get('include_logs', 'false').lower() == 'true'
        if include_logs:
            logs = NotificationLog.objects.filter(notification=notification).order_by('-created_at')
            data['logs'] = NotificationLogSerializer(logs, many=True).data
        
        return Response(data)

    @action(detail=False, methods=['get'], url_path=r'user/(?P<user_id>\d+)')
    def user_notifications(self, request, user_id=None):
        """
        Get all notifications for a specific user.
        
        URL: /api/notifications/user/123/
        
        Query Parameters:
            - status: Filter by status (PENDING, SENT, FAILED)
            - type: Filter by type (EMAIL, SMS)
        """
        # Check if user can view these notifications
        if not request.user.is_admin() and str(request.user.id) != str(user_id):
            return Response(
                {"detail": "You can only view your own notifications"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        qs = self.queryset.filter(user_id=user_id)
        
        # Optional filtering by status
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter.upper())
        
        # Optional filtering by type
        type_filter = request.query_params.get('type')
        if type_filter:
            qs = qs.filter(type=type_filter.upper())
        
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='pending')
    def pending(self, request):
        """
        Get all pending notifications.
        
        URL: /api/notifications/pending/
        
        Query Parameters:
            - type: Filter by type (EMAIL, SMS)
        """
        qs = self.queryset.filter(status='PENDING')
        
        # Optional filtering by type
        type_filter = request.query_params.get('type')
        if type_filter:
            qs = qs.filter(type=type_filter.upper())
        
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='send_from_template')
    def send_from_template(self, request):
        """
        Create a notification from a template with safe rendering.
        
        Body:
        {
            "template_id": 1,
            "user_id": 123,
            "context": {
                "user_name": "John",
                "book_title": "Django Guide",
                "due_date": "2024-12-15"
            },
            "type": "EMAIL"  // optional override
        }
        """
        serializer = SendFromTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        template = get_object_or_404(NotificationTemplate, pk=data['template_id'])
        
        # Check if template is active
        if not template.is_active:
            return Response(
                {"detail": "Template is inactive"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ctx = data.get('context') or {}
        
        # Render templates safely using Django template engine
        try:
            subject_template = Template(template.subject_template)
            message_template = Template(template.message_template)
            
            subject = subject_template.render(Context(ctx))
            message = message_template.render(Context(ctx))
            
        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error in template {template.id}: {e}")
            return Response(
                {"detail": f"Template syntax error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Template rendering error in template {template.id}: {e}")
            return Response(
                {"detail": f"Template rendering error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create notification
        notif = Notification.objects.create(
            user_id=data['user_id'],
            type=data.get('type', template.type),
            subject=subject,
            message=message,
            status='PENDING'
        )
        
        # Queue for sending
        try:
            if notif.type == 'EMAIL':
                send_notification_email.delay(notif.id)
            elif notif.type == 'SMS':
                send_notification_sms.delay(notif.id)
            logger.info(f"Created and queued notification {notif.id} from template {template.id}")
        except Exception as e:
            logger.error(f"Failed to queue notification {notif.id}: {e}")
        
        notif_ser = NotificationSerializer(notif)
        return Response(notif_ser.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='bulk_create')
    def bulk_create(self, request):
        """
        Create multiple notifications at once.
        
        Body:
        {
            "notifications": [
                {
                    "user_id": 1,
                    "type": "EMAIL",
                    "subject": "Test 1",
                    "message": "Message 1"
                },
                {
                    "user_id": 2,
                    "type": "SMS",
                    "subject": "Test 2",
                    "message": "Message 2"
                }
            ]
        }
        
        Maximum: 100 notifications per request
        """
        notifications_data = request.data.get('notifications', [])
        
        if not notifications_data or not isinstance(notifications_data, list):
            return Response(
                {"detail": "notifications list is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(notifications_data) > 100:
            return Response(
                {"detail": "Maximum 100 notifications per bulk request"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_notifications = []
        errors = []
        
        for idx, notif_data in enumerate(notifications_data):
            notif_data.setdefault('status', 'PENDING')
            serializer = NotificationSerializer(data=notif_data)
            
            if serializer.is_valid():
                notif = serializer.save()
                created_notifications.append(notif)
                
                # Queue for sending
                try:
                    if notif.type == 'EMAIL':
                        send_notification_email.delay(notif.id)
                    elif notif.type == 'SMS':
                        send_notification_sms.delay(notif.id)
                except Exception as e:
                    logger.error(f"Failed to queue notification {notif.id}: {e}")
            else:
                errors.append({"index": idx, "errors": serializer.errors})
        
        response_status = status.HTTP_201_CREATED
        if errors and not created_notifications:
            response_status = status.HTTP_400_BAD_REQUEST
        elif errors:
            response_status = status.HTTP_207_MULTI_STATUS
        
        return Response({
            "created": len(created_notifications),
            "failed": len(errors),
            "errors": errors,
            "notifications": NotificationSerializer(created_notifications, many=True).data
        }, status=response_status)

    @action(detail=True, methods=['post'], url_path='retry')
    def retry(self, request, pk=None):
        """
        Retry sending a failed notification.
        
        URL: /api/notifications/123/retry/
        """
        notification = get_object_or_404(self.queryset, pk=pk)
        
        if notification.status == 'SENT':
            return Response(
                {"detail": "Notification already sent"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset status to pending
        notification.status = 'PENDING'
        notification.save(update_fields=['status'])
        
        # Queue for sending
        try:
            if notification.type == 'EMAIL':
                send_notification_email.delay(notification.id)
            elif notification.type == 'SMS':
                send_notification_sms.delay(notification.id)
            
            logger.info(f"Queued notification {notification.id} for retry")
            
            return Response(
                {"detail": "Notification queued for retry"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Failed to queue notification {notification.id} for retry: {e}")
            return Response(
                {"detail": f"Failed to queue notification: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Return comprehensive statistics.
        
        URL: /api/notifications/stats/
        
        Query Parameters:
            - days: Number of days to include (default: 30)
        """
        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        qs = Notification.objects.filter(created_at__gte=date_from)
        
        # Counts by status
        status_counts = qs.values('status').annotate(count=Count('id'))
        
        # Counts by type
        type_counts = qs.values('type').annotate(count=Count('id'))
        
        # Success rate
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

    @action(detail=False, methods=['get'], url_path='recent')
    def recent(self, request):
        """
        Get most recent notifications across all users.
        
        URL: /api/notifications/recent/?limit=20
        
        Query Parameters:
            - limit: Number of results (max 100, default 10)
        """
        limit = min(int(request.query_params.get('limit', 10)), 100)
        qs = self.queryset[:limit]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification templates.
    
    Permissions: CanManageTemplates (Librarians and Admins)
    
    Endpoints:
        - GET /templates/ - List all templates
        - POST /templates/ - Create new template
        - GET /templates/{id}/ - Get specific template
        - PUT /templates/{id}/ - Update template
        - DELETE /templates/{id}/ - Delete template
        - POST /templates/{id}/test/ - Test template with context
    """
    queryset = NotificationTemplate.objects.all().order_by('-created_at')
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated, CanManageTemplates]
    
    def create(self, request, *args, **kwargs):
        """
        Create a new template with validation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate template syntax
        try:
            Template(serializer.validated_data['subject_template'])
            Template(serializer.validated_data['message_template'])
        except TemplateSyntaxError as e:
            raise ValidationError({"detail": f"Invalid template syntax: {str(e)}"})
        
        self.perform_create(serializer)
        logger.info(f"Created template: {serializer.data['name']}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Update a template with validation.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Validate template syntax if templates are being updated
        if 'subject_template' in serializer.validated_data:
            try:
                Template(serializer.validated_data['subject_template'])
            except TemplateSyntaxError as e:
                raise ValidationError({"detail": f"Invalid subject template syntax: {str(e)}"})
        
        if 'message_template' in serializer.validated_data:
            try:
                Template(serializer.validated_data['message_template'])
            except TemplateSyntaxError as e:
                raise ValidationError({"detail": f"Invalid message template syntax: {str(e)}"})
        
        self.perform_update(serializer)
        logger.info(f"Updated template: {instance.name}")
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='test')
    def test_template(self, request, pk=None):
        """
        Test a template with sample context.
        
        Body:
        {
            "context": {
                "user_name": "John",
                "book_title": "Test Book",
                "due_date": "2024-12-15"
            }
        }
        """
        template = get_object_or_404(self.queryset, pk=pk)
        context = request.data.get('context', {})
        
        try:
            subject_template = Template(template.subject_template)
            message_template = Template(template.message_template)
            
            subject = subject_template.render(Context(context))
            message = message_template.render(Context(context))
            
            return Response({
                "template_name": template.name,
                "template_type": template.type,
                "subject": subject,
                "message": message,
                "context_used": context
            })
        except TemplateSyntaxError as e:
            return Response(
                {"detail": f"Template syntax error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Template test failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )