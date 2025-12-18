from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.conf import settings
import logging
import requests

from .models import Notification, NotificationLog

logger = logging.getLogger(__name__)



from common.consul_client import ConsulClient

def get_user_email(user_id):
    """
    Fetch user email from the User Service API.
    
    This integrates with your microservices architecture by calling
    the User Service to get real-time user data using Consul for discovery.
    """
    try:
        # Resolve service URL via Consul
        consul = ConsulClient(host=settings.CONSUL_HOST, port=settings.CONSUL_PORT)
        user_service_url = consul.get_service_url('user-service')
        
        if not user_service_url:
            user_service_url = getattr(settings, 'USER_SERVICE_URL', 'http://localhost:8001')
            logger.warning(f"Consul resolution failed for user-service, using fallback: {user_service_url}")

        # Call User Service API
        response = requests.get(
            f"{user_service_url}/api/users/{user_id}/",
            timeout=getattr(settings, 'USER_SERVICE_TIMEOUT', 5)
        )
        
        if response.status_code == 200:
            user_data = response.json()
            email = user_data.get('email')
            
            if email:
                validate_email(email)
                logger.info(f"Fetched email for user {user_id}: {email}")
                return email
            else:
                raise ValueError(f"No email found for user {user_id}")
        elif response.status_code == 404:
            raise ValueError(f"User {user_id} not found in User Service")
        else:
            raise ValueError(f"User Service returned status {response.status_code}")
            
    except requests.RequestException as e:
        logger.error(f"Failed to fetch user {user_id} from User Service: {e}")
        raise ValueError(f"User Service unavailable: {e}")
    except ValidationError as e:
        logger.error(f"Invalid email for user {user_id}: {e}")
        raise


def get_user_phone(user_id):
    """
    Fetch user phone number from the User Service API.
    """
    try:
        # Resolve service URL via Consul
        consul = ConsulClient(host=settings.CONSUL_HOST, port=settings.CONSUL_PORT)
        user_service_url = consul.get_service_url('user-service')
        
        if not user_service_url:
            user_service_url = getattr(settings, 'USER_SERVICE_URL', 'http://localhost:8001')
            logger.warning(f"Consul resolution failed for user-service, using fallback: {user_service_url}")

        response = requests.get(
            f"{user_service_url}/api/users/{user_id}/",
            timeout=getattr(settings, 'USER_SERVICE_TIMEOUT', 5)
        )
        
        if response.status_code == 200:
            user_data = response.json()
            phone = user_data.get('phone')
            
            if phone:
                logger.info(f"Fetched phone for user {user_id}: {phone}")
                return phone
            else:
                raise ValueError(f"No phone found for user {user_id}")
        else:
            raise ValueError(f"User Service returned status {response.status_code}")
            
    except requests.RequestException as e:
        logger.error(f"Failed to fetch user phone from User Service: {e}")
        raise ValueError(f"User Service unavailable: {e}")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_email(self, notification_id):
    """
    Send email notification with proper error handling and retry logic.
    
    Args:
        notification_id: ID of the notification to send
    
    Retries:
        - 3 retries with exponential backoff (60s, 120s, 240s)
        - Marks as FAILED after max retries
    """
    notif = None
    try:
        notif = Notification.objects.get(pk=notification_id)
        
        # Validate notification is ready to send
        if notif.status == "SENT":
            logger.info(f"Notification {notification_id} already sent, skipping")
            return {"status": "already_sent"}
        
        # Get recipient email from User Service
        recipient_email = get_user_email(notif.user_id)
        
        # Log message details for debugging
        logger.info(f"Sending email for notification {notification_id}")
        logger.info(f"Subject: {notif.subject}")
        logger.info(f"Connecting to SMTP server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        logger.info(f"Message length: {len(notif.message)} characters")
        logger.debug(f"Full message:\n{notif.message}")
        
        # Send email
        send_mail(
            subject=notif.subject,
            message=notif.message,
            from_email=None,  # uses DEFAULT_FROM_EMAIL
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        # Update status
        notif.status = "SENT"
        notif.sent_at = timezone.now()
        notif.save(update_fields=["status", "sent_at"])
        
        # Log success
        NotificationLog.objects.create(
            notification=notif,
            status="SENT",
            detail=f"Email sent successfully to {recipient_email}"
        )
        
        logger.info(f"Successfully sent notification {notification_id}")
        return {"status": "sent", "notification_id": notification_id}
        
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return {"status": "not_found"}
        
    except (ValidationError, ValueError) as e:
        # Invalid email or user not found - don't retry
        logger.error(f"Invalid email/user for notification {notification_id}: {e}")
        if notif:
            notif.status = "FAILED"
            notif.save(update_fields=["status"])
            NotificationLog.objects.create(
                notification=notif,
                status="FAILED",
                detail=f"Invalid email or user: {e}"
            )
        return {"status": "invalid_email"}
        
    except Exception as exc:
        # Log failure
        logger.error(f"Failed to send notification {notification_id}: {exc}", exc_info=True)
        
        if notif:
            NotificationLog.objects.create(
                notification=notif,
                status="FAILED",
                detail=f"Attempt {self.request.retries + 1}: {str(exc)}"
            )
        
        # Retry with exponential backoff
        try:
            countdown = 60 * (2 ** self.request.retries)
            logger.info(f"Retrying notification {notification_id} in {countdown}s")
            raise self.retry(exc=exc, countdown=countdown)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for notification {notification_id}")
            if notif:
                notif.status = "FAILED"
                notif.save(update_fields=["status"])
                NotificationLog.objects.create(
                    notification=notif,
                    status="FAILED",
                    detail=f"Max retries exceeded. Last error: {str(exc)}"
                )
            return {"status": "max_retries_exceeded"}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_sms(self, notification_id):
    """
    Send SMS notification.
    
    TODO: Implement with your SMS provider (Twilio, AWS SNS, etc.)
    """
    notif = None
    try:
        notif = Notification.objects.get(pk=notification_id)
        
        if notif.status == "SENT":
            logger.info(f"SMS notification {notification_id} already sent")
            return {"status": "already_sent"}
        
        # Get recipient phone from User Service
        recipient_phone = get_user_phone(notif.user_id)
        
        # TODO: Implement actual SMS sending with Twilio
        logger.warning(f"SMS sending not implemented. Would send to {recipient_phone}")
        
        # Placeholder - mark as sent
        notif.status = "SENT"
        notif.sent_at = timezone.now()
        notif.save(update_fields=["status", "sent_at"])
        
        NotificationLog.objects.create(
            notification=notif,
            status="SENT",
            detail=f"SMS sent to {recipient_phone} (placeholder implementation)"
        )
        
        logger.info(f"Successfully sent SMS notification {notification_id}")
        return {"status": "sent", "notification_id": notification_id}
        
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return {"status": "not_found"}
        
    except (ValueError,) as e:
        # User not found or invalid phone - don't retry
        logger.error(f"Invalid phone/user for notification {notification_id}: {e}")
        if notif:
            notif.status = "FAILED"
            notif.save(update_fields=["status"])
            NotificationLog.objects.create(
                notification=notif,
                status="FAILED",
                detail=f"Invalid phone or user: {e}"
            )
        return {"status": "invalid_phone"}
        
    except Exception as exc:
        logger.error(f"Failed to send SMS {notification_id}: {exc}", exc_info=True)
        
        if notif:
            NotificationLog.objects.create(
                notification=notif,
                status="FAILED",
                detail=f"Attempt {self.request.retries + 1}: {str(exc)}"
            )
        
        try:
            countdown = 60 * (2 ** self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except self.MaxRetriesExceededError:
            if notif:
                notif.status = "FAILED"
                notif.save(update_fields=["status"])
            return {"status": "max_retries_exceeded"}


@shared_task
def process_pending_notifications():
    """
    Periodic task to process pending notifications.
    Scheduled via CELERY_BEAT_SCHEDULE in settings.
    """
    pending = Notification.objects.filter(status="PENDING").order_by("created_at")
    count = pending.count()
    
    if count == 0:
        logger.info("No pending notifications to process")
        return {"processed": 0}
    
    # Process in batches to avoid overwhelming the queue
    batch_size = 100
    processed = 0
    
    for notif in pending[:batch_size]:
        try:
            if notif.type == "EMAIL":
                send_notification_email.delay(notif.id)
            elif notif.type == "SMS":
                send_notification_sms.delay(notif.id)
            processed += 1
        except Exception as e:
            logger.error(f"Failed to queue notification {notif.id}: {e}")
    
    logger.info(f"Queued {processed} pending notifications out of {count} total")
    return {"queued": processed, "total_pending": count}


@shared_task
def cleanup_old_logs(days=30):
    """
    Clean up old notification logs to prevent database bloat.
    
    Args:
        days: Number of days to retain logs (default: 30)
    """
    from datetime import timedelta
    cutoff = timezone.now() - timedelta(days=days)
    
    deleted_count, _ = NotificationLog.objects.filter(
        created_at__lt=cutoff
    ).delete()
    
    logger.info(f"Deleted {deleted_count} notification logs older than {days} days")
    return {"deleted": deleted_count, "cutoff_days": days}


@shared_task
def cleanup_old_notifications(days=90):
    """
    Archive or delete old sent notifications.
    
    Args:
        days: Number of days to retain notifications (default: 90)
    """
    from datetime import timedelta
    cutoff = timezone.now() - timedelta(days=days)
    
    # Only delete SENT notifications that are old
    deleted_count, _ = Notification.objects.filter(
        status="SENT",
        created_at__lt=cutoff
    ).delete()
    
    logger.info(f"Deleted {deleted_count} old notifications older than {days} days")
    return {"deleted": deleted_count, "cutoff_days": days}


@shared_task
def retry_failed_notifications(max_age_hours=24):
    """
    Retry failed notifications that are recent.
    
    Args:
        max_age_hours: Only retry failures from the last N hours
    """
    from datetime import timedelta
    cutoff = timezone.now() - timedelta(hours=max_age_hours)
    
    failed = Notification.objects.filter(
        status="FAILED",
        created_at__gte=cutoff
    )
    
    count = failed.count()
    retried = 0
    
    for notif in failed:
        try:
            # Reset to pending
            notif.status = "PENDING"
            notif.save(update_fields=["status"])
            
            # Queue for sending
            if notif.type == "EMAIL":
                send_notification_email.delay(notif.id)
            elif notif.type == "SMS":
                send_notification_sms.delay(notif.id)
            
            retried += 1
        except Exception as e:
            logger.error(f"Failed to retry notification {notif.id}: {e}")
    
    logger.info(f"Retried {retried} out of {count} failed notifications")
    return {"retried": retried, "total_failed": count}