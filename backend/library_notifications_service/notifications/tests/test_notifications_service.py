import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock, MagicMock, call
import json


# ============================================
# 🔧 FIXTURES
# ============================================

@pytest.fixture
def api_client():
    """Client API pour les tests"""
    return APIClient()


@pytest.fixture
@pytest.mark.django_db
def sample_user():
    """Utilisateur de test"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!'
    )


@pytest.fixture
@pytest.mark.django_db
def sample_user_2():
    """Deuxième utilisateur de test"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='testuser2',
        email='test2@example.com',
        password='TestPass123!'
    )


@pytest.fixture
@pytest.mark.django_db
def sample_notification(sample_user):
    """Notification de test"""
    from notifications.models import Notification
    return Notification.objects.create(
        user_id=sample_user.id,
        title='Test Notification',
        message='This is a test notification',
        notification_type='INFO',
        is_read=False
    )


@pytest.fixture
@pytest.mark.django_db
def multiple_notifications(sample_user):
    """Créer plusieurs notifications pour les tests"""
    from notifications.models import Notification
    notifications = []
    for i in range(5):
        notif = Notification.objects.create(
            user_id=sample_user.id,
            title=f'Notification {i}',
            message=f'Message {i}',
            notification_type='INFO',
            is_read=(i % 2 == 0)
        )
        notifications.append(notif)
    return notifications


@pytest.fixture
@pytest.mark.django_db
def authenticated_client(api_client, sample_user):
    """Client authentifié"""
    api_client.force_authenticate(user=sample_user)
    return api_client


# ============================================
# 📝 TESTS MODÈLE NOTIFICATION
# ============================================

@pytest.mark.django_db
class TestNotificationModel:
    """Tests du modèle Notification"""

    def test_create_notification_success(self, sample_user):
        """Test création notification réussie"""
        from notifications.models import Notification
        
        notif = Notification.objects.create(
            user_id=sample_user.id,
            title='New Notification',
            message='Test message',
            notification_type='INFO'
        )
        
        assert notif.user_id == sample_user.id
        assert notif.title == 'New Notification'
        assert notif.is_read is False
        assert notif.sent_at is not None

    def test_notification_string_representation(self, sample_notification):
        """Test méthode __str__"""
        expected = f"{sample_notification.title} - User {sample_notification.user_id}"
        assert str(sample_notification) == expected

    def test_notification_types_valid(self, sample_user):
        """Test types de notification valides"""
        from notifications.models import Notification
        
        valid_types = ['INFO', 'WARNING', 'ERROR', 'SUCCESS', 'REMINDER']
        
        for notif_type in valid_types:
            notif = Notification.objects.create(
                user_id=sample_user.id,
                title=f'Test {notif_type}',
                message='Message',
                notification_type=notif_type
            )
            assert notif.notification_type == notif_type

    def test_notification_default_is_read_false(self, sample_notification):
        """Test is_read par défaut False"""
        assert sample_notification.is_read is False

    def test_notification_mark_as_read(self, sample_notification):
        """Test marquer comme lu"""
        sample_notification.is_read = True
        sample_notification.read_at = timezone.now()
        sample_notification.save()
        
        assert sample_notification.is_read is True
        assert sample_notification.read_at is not None

    def test_notification_auto_timestamps(self, sample_notification):
        """Test timestamps automatiques"""
        assert sample_notification.sent_at is not None
        assert sample_notification.created_at is not None

    def test_notification_with_related_id(self, sample_user):
        """Test notification avec ID relié"""
        from notifications.models import Notification
        
        notif = Notification.objects.create(
            user_id=sample_user.id,
            title='Loan Due Soon',
            message='Your loan is due tomorrow',
            notification_type='REMINDER',
            related_object_type='LOAN',
            related_object_id=123
        )
        
        assert notif.related_object_type == 'LOAN'
        assert notif.related_object_id == 123

    def test_notification_with_null_related_fields(self, sample_user):
        """Test notification avec champs related NULL"""
        from notifications.models import Notification
        
        notif = Notification.objects.create(
            user_id=sample_user.id,
            title='General Notification',
            message='Test',
            notification_type='INFO',
            related_object_type=None,
            related_object_id=None
        )
        
        assert notif.related_object_type is None
        assert notif.related_object_id is None

    def test_notification_meta_ordering(self, sample_user):
        """Test l'ordre des notifications par défaut"""
        from notifications.models import Notification
        
        old = Notification.objects.create(
            user_id=sample_user.id,
            title='Old',
            message='Old',
            notification_type='INFO'
        )
        old.sent_at = timezone.now() - timedelta(days=1)
        old.save()
        
        new = Notification.objects.create(
            user_id=sample_user.id,
            title='New',
            message='New',
            notification_type='INFO'
        )
        
        notifications = Notification.objects.filter(user_id=sample_user.id)
        assert notifications.first().title == 'New'

    def test_notification_update_fields(self, sample_notification):
        """Test mise à jour des champs"""
        sample_notification.title = 'Updated Title'
        sample_notification.message = 'Updated Message'
        sample_notification.save()
        
        sample_notification.refresh_from_db()
        assert sample_notification.title == 'Updated Title'
        assert sample_notification.message == 'Updated Message'


# ============================================
# 🔧 TESTS SERIALIZER
# ============================================

@pytest.mark.django_db
class TestNotificationSerializer:
    """Tests du serializer Notification"""

    def test_serializer_with_valid_data(self, sample_user):
        """Test serializer avec données valides"""
        from notifications.serializers import NotificationSerializer
        
        data = {
            'user_id': sample_user.id,
            'title': 'Test Notification',
            'message': 'Test message',
            'notification_type': 'INFO'
        }
        
        serializer = NotificationSerializer(data=data)
        assert serializer.is_valid()
        notif = serializer.save()
        assert notif.title == 'Test Notification'

    def test_serializer_missing_required_fields(self):
        """Test serializer champs requis manquants"""
        from notifications.serializers import NotificationSerializer
        
        data = {'title': 'Test'}
        serializer = NotificationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'user_id' in serializer.errors or 'message' in serializer.errors

    def test_serializer_invalid_notification_type(self, sample_user):
        """Test serializer type invalide"""
        from notifications.serializers import NotificationSerializer
        
        data = {
            'user_id': sample_user.id,
            'title': 'Test',
            'message': 'Test',
            'notification_type': 'INVALID'
        }
        
        serializer = NotificationSerializer(data=data)
        assert not serializer.is_valid()

    def test_serializer_read_only_fields(self, sample_notification):
        """Test champs read-only du serializer"""
        from notifications.serializers import NotificationSerializer
        
        serializer = NotificationSerializer(sample_notification)
        data = serializer.data
        
        assert 'id' in data
        assert 'sent_at' in data
        assert 'created_at' in data

    def test_serializer_with_related_object(self, sample_user):
        """Test serializer avec objet lié"""
        from notifications.serializers import NotificationSerializer
        
        data = {
            'user_id': sample_user.id,
            'title': 'Loan Reminder',
            'message': 'Your book is due',
            'notification_type': 'REMINDER',
            'related_object_type': 'LOAN',
            'related_object_id': 456
        }
        
        serializer = NotificationSerializer(data=data)
        assert serializer.is_valid()
        notif = serializer.save()
        assert notif.related_object_type == 'LOAN'


# ============================================
# 📬 TESTS ENVOI NOTIFICATIONS
# ============================================

@pytest.mark.django_db
class TestSendNotification:
    """Tests envoi de notifications"""

    @patch('notifications.services.EmailService.send_email')
    def test_send_notification_success(self, mock_email, authenticated_client):
        """Test envoi notification réussi"""
        mock_email.return_value = {'success': True}
        
        response = authenticated_client.post('/api/notifications/send/', {
            'user_id': authenticated_client.handler._force_user.id,
            'title': 'Test Notification',
            'message': 'Test message',
            'notification_type': 'INFO'
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Test Notification'

    @patch('notifications.services.EmailService.send_email')
    def test_send_notification_with_email(self, mock_email, authenticated_client):
        """Test envoi notification avec email"""
        mock_email.return_value = {'success': True}
        
        response = authenticated_client.post('/api/notifications/send/', {
            'user_id': authenticated_client.handler._force_user.id,
            'title': 'Important',
            'message': 'Test',
            'notification_type': 'WARNING',
            'send_email': True
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert mock_email.called

    def test_send_notification_missing_fields(self, authenticated_client):
        """Test envoi notification champs manquants"""
        response = authenticated_client.post('/api/notifications/send/', {
            'title': 'Test'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_send_notification_invalid_type(self, authenticated_client):
        """Test envoi notification type invalide"""
        response = authenticated_client.post('/api/notifications/send/', {
            'user_id': authenticated_client.handler._force_user.id,
            'title': 'Test',
            'message': 'Test',
            'notification_type': 'INVALID_TYPE'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_send_notification_unauthorized(self, api_client):
        """Test envoi sans authentification"""
        response = api_client.post('/api/notifications/send/', {
            'user_id': 1,
            'title': 'Test',
            'message': 'Test',
            'notification_type': 'INFO'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_send_notification_with_related_object(self, authenticated_client):
        """Test envoi avec objet lié"""
        response = authenticated_client.post('/api/notifications/send/', {
            'user_id': authenticated_client.handler._force_user.id,
            'title': 'Loan Reminder',
            'message': 'Your book is due',
            'notification_type': 'REMINDER',
            'related_object_type': 'LOAN',
            'related_object_id': 456
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['related_object_type'] == 'LOAN'

    @patch('notifications.services.EmailService.send_email')
    def test_send_notification_email_multiple_types(self, mock_email, authenticated_client):
        """Test envoi email pour différents types"""
        mock_email.return_value = {'success': True}
        
        notification_types = ['INFO', 'WARNING', 'ERROR', 'SUCCESS', 'REMINDER']
        
        for notif_type in notification_types:
            response = authenticated_client.post('/api/notifications/send/', {
                'user_id': authenticated_client.handler._force_user.id,
                'title': f'Test {notif_type}',
                'message': 'Test',
                'notification_type': notif_type,
                'send_email': True
            })
            
            assert response.status_code == status.HTTP_201_CREATED


# ============================================
# 📋 TESTS LISTE NOTIFICATIONS
# ============================================

@pytest.mark.django_db
class TestNotificationsList:
    """Tests liste notifications"""

    def test_list_my_notifications(self, authenticated_client, sample_notification):
        """Test liste mes notifications"""
        response = authenticated_client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_list_unread_notifications_only(self, authenticated_client, sample_user):
        """Test filtrer notifications non lues"""
        from notifications.models import Notification
        
        Notification.objects.create(
            user_id=sample_user.id,
            title='Read Notification',
            message='Already read',
            notification_type='INFO',
            is_read=True,
            read_at=timezone.now()
        )
        
        Notification.objects.create(
            user_id=sample_user.id,
            title='Unread Notification',
            message='Not read yet',
            notification_type='INFO',
            is_read=False
        )
        
        response = authenticated_client.get('/api/notifications/?is_read=false')
        
        assert response.status_code == status.HTTP_200_OK
        for notif in response.data['results']:
            assert notif['is_read'] is False

    def test_list_read_notifications_only(self, authenticated_client, sample_user):
        """Test filtrer notifications lues"""
        from notifications.models import Notification
        
        for i in range(3):
            Notification.objects.create(
                user_id=sample_user.id,
                title=f'Read {i}',
                message='Message',
                notification_type='INFO',
                is_read=True,
                read_at=timezone.now()
            )
        
        response = authenticated_client.get('/api/notifications/?is_read=true')
        
        assert response.status_code == status.HTTP_200_OK
        for notif in response.data['results']:
            assert notif['is_read'] is True

    def test_list_notifications_by_type(self, authenticated_client, sample_user):
        """Test filtrer par type"""
        from notifications.models import Notification
        
        for notif_type in ['WARNING', 'ERROR', 'SUCCESS']:
            Notification.objects.create(
                user_id=sample_user.id,
                title=f'{notif_type} Notification',
                message='Message',
                notification_type=notif_type
            )
        
        response = authenticated_client.get('/api/notifications/?type=WARNING')
        
        assert response.status_code == status.HTTP_200_OK
        for notif in response.data['results']:
            assert notif['notification_type'] == 'WARNING'

    def test_list_notifications_pagination(self, authenticated_client, sample_user):
        """Test pagination"""
        from notifications.models import Notification
        
        for i in range(25):
            Notification.objects.create(
                user_id=sample_user.id,
                title=f'Notification {i}',
                message=f'Message {i}',
                notification_type='INFO'
            )
        
        response = authenticated_client.get('/api/notifications/?page=1')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'next' in response.data
        assert len(response.data['results']) <= 20

    def test_list_notifications_ordered_by_date(self, authenticated_client, sample_user):
        """Test ordre par date (plus récent en premier)"""
        from notifications.models import Notification
        
        old_notif = Notification.objects.create(
            user_id=sample_user.id,
            title='Old',
            message='Old message',
            notification_type='INFO'
        )
        old_notif.sent_at = timezone.now() - timedelta(days=5)
        old_notif.save()
        
        new_notif = Notification.objects.create(
            user_id=sample_user.id,
            title='New',
            message='New message',
            notification_type='INFO'
        )
        
        response = authenticated_client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['title'] == 'New'

    def test_list_notifications_empty(self, authenticated_client):
        """Test liste vide"""
        response = authenticated_client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0

    def test_list_notifications_different_users_isolated(self, authenticated_client, sample_user, sample_user_2):
        """Test isolation des notifications entre utilisateurs"""
        from notifications.models import Notification
        
        Notification.objects.create(
            user_id=sample_user.id,
            title='User1 Notification',
            message='For user 1',
            notification_type='INFO'
        )
        
        Notification.objects.create(
            user_id=sample_user_2.id,
            title='User2 Notification',
            message='For user 2',
            notification_type='INFO'
        )
        
        response = authenticated_client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'User1 Notification'

    def test_list_notifications_multiple_filters(self, authenticated_client, sample_user):
        """Test combinaison de filtres"""
        from notifications.models import Notification
        
        Notification.objects.create(
            user_id=sample_user.id,
            title='Warning Unread',
            message='Message',
            notification_type='WARNING',
            is_read=False
        )
        
        Notification.objects.create(
            user_id=sample_user.id,
            title='Warning Read',
            message='Message',
            notification_type='WARNING',
            is_read=True,
            read_at=timezone.now()
        )
        
        response = authenticated_client.get('/api/notifications/?type=WARNING&is_read=false')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Warning Unread'


# ============================================
# ✅ TESTS MARQUER COMME LU
# ============================================

@pytest.mark.django_db
class TestMarkAsRead:
    """Tests marquer notification comme lue"""

    def test_mark_notification_as_read(self, authenticated_client, sample_notification):
        """Test marquer comme lu"""
        response = authenticated_client.post(
            f'/api/notifications/{sample_notification.id}/mark-read/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        sample_notification.refresh_from_db()
        assert sample_notification.is_read is True
        assert sample_notification.read_at is not None

    def test_mark_all_as_read(self, authenticated_client, sample_user):
        """Test marquer toutes comme lues"""
        from notifications.models import Notification
        
        for i in range(10):
            Notification.objects.create(
                user_id=sample_user.id,
                title=f'Notification {i}',
                message='Message',
                notification_type='INFO',
                is_read=False
            )
        
        response = authenticated_client.post('/api/notifications/mark-all-read/')
        
        assert response.status_code == status.HTTP_200_OK
        
        unread_count = Notification.objects.filter(
            user_id=sample_user.id,
            is_read=False
        ).count()
        assert unread_count == 0

    def test_mark_already_read_notification(self, authenticated_client, sample_notification):
        """Test marquer notification déjà lue"""
        sample_notification.is_read = True
        sample_notification.read_at = timezone.now()
        sample_notification.save()
        
        response = authenticated_client.post(
            f'/api/notifications/{sample_notification.id}/mark-read/'
        )
        
        assert response.status_code == status.HTTP_200_OK

    def test_mark_other_user_notification(self, api_client, sample_notification):
        """Test marquer notification autre utilisateur"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        
        api_client.force_authenticate(user=other_user)
        
        response = api_client.post(
            f'/api/notifications/{sample_notification.id}/mark-read/'
        )
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_mark_nonexistent_notification_as_read(self, authenticated_client):
        """Test marquer notification inexistante comme lue"""
        response = authenticated_client.post('/api/notifications/99999/mark-read/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_mark_all_read_with_no_notifications(self, authenticated_client):
        """Test marquer tout comme lu sans notifications"""
        response = authenticated_client.post('/api/notifications/mark-all-read/')
        
        assert response.status_code == status.HTTP_200_OK


# ============================================
# 🗑️ TESTS SUPPRESSION NOTIFICATIONS
# ============================================

@pytest.mark.django_db
class TestDeleteNotification:
    """Tests suppression notifications"""

    def test_delete_notification_success(self, authenticated_client, sample_notification):
        """Test suppression réussie"""
        notif_id = sample_notification.id
        
        response = authenticated_client.delete(f'/api/notifications/{notif_id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        from notifications.models import Notification
        assert not Notification.objects.filter(id=notif_id).exists()

    def test_delete_nonexistent_notification(self, authenticated_client):
        """Test suppression notification inexistante"""
        response = authenticated_client.delete('/api/notifications/999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_other_user_notification(self, api_client, sample_notification):
        """Test suppression notification autre utilisateur"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        
        api_client.force_authenticate(user=other_user)
        
        response = api_client.delete(f'/api/notifications/{sample_notification.id}/')
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_delete_all_read_notifications(self, authenticated_client, sample_user):
        """Test suppression toutes notifications lues"""
        from notifications.models import Notification
        
        for i in range(5):
            Notification.objects.create(
                user_id=sample_user.id,
                title=f'Read {i}',
                message='Message',
                notification_type='INFO',
                is_read=True,
                read_at=timezone.now()
            )
        
        unread = Notification.objects.create(
            user_id=sample_user.id,
            title='Unread',
            message='Message',
            notification_type='INFO',
            is_read=False
        )
        
        response = authenticated_client.delete('/api/notifications/delete-read/')
        
        assert response.status_code == status.HTTP_200_OK
        
        remaining = Notification.objects.filter(user_id=sample_user.id)
        assert remaining.count() == 1
        assert remaining.first().id == unread.id

    def test_delete_read_notifications_with_none(self, authenticated_client, sample_user):
        """Test suppression notifications lues quand aucune"""
        from notifications.models import Notification
        
        Notification.objects.create(
            user_id=sample_user.id,
            title='Unread',
            message='Message',
            notification_type='INFO',
            is_read=False
        )
        
        response = authenticated_client.delete('/api/notifications/delete-read/')
        
        assert response.status_code == status.HTTP_200_OK
        
        remaining = Notification.objects.filter(user_id=sample_user.id)
        assert remaining.count() == 1


# ============================================
# 🔔 TESTS NOTIFICATIONS AUTOMATIQUES
# ============================================

@pytest.mark.django_db
class TestAutomaticNotifications:
    """Tests notifications automatiques"""

    @patch('notifications.tasks.send_overdue_reminders')
    def test_send_overdue_loan_notifications(self, mock_task, sample_user):
        """Test notifications emprunts en retard"""
        from notifications.services import NotificationService
        
        loan_data = {
            'id': 1,
            'user_id': sample_user.id,
            'book_title': 'Test Book',
            'due_date': timezone.now() - timedelta(days=3),
            'days_overdue': 3
        }
        
        NotificationService.send_overdue_reminder(loan_data)
        
        from notifications.models import Notification
        notif = Notification.objects.filter(
            user_id=sample_user.id,
            notification_type='WARNING'
        ).first()
        
        assert notif is not None
        assert 'overdue' in notif.message.lower() or 'retard' in notif.message.lower()

    def test_send_loan_due_soon_notification(self, sample_user):
        """Test notifications échéance proche"""
        from notifications.services import NotificationService
        
        loan_data = {
            'id': 1,
            'user_id': sample_user.id,
            'book_title': 'Test Book',
            'due_date': timezone.now() + timedelta(days=2)
        }
        
        NotificationService.send_due_soon_reminder(loan_data)
        
        from notifications.models import Notification
        notif = Notification.objects.filter(
            user_id=sample_user.id,
            notification_type='REMINDER'
        ).first()
        
        assert notif is not None

    def test_send_book_available_notification(self, sample_user):
        """Test notification livre disponible"""
        from notifications.services import NotificationService
        
        book_data = {
            'id': 1,
            'title': 'Test Book',
            'author': 'Test Author'
        }
        
        NotificationService.send_book_available(sample_user.id, book_data)
        
        from notifications.models import Notification
        notif = Notification.objects.filter(
            user_id=sample_user.id,
            notification_type='SUCCESS'
        ).first()
        
        assert notif is not None
        assert book_data['title'] in notif.message

    def test_send_reservation_confirmed_notification(self, sample_user):
        """Test notification réservation confirmée"""
        from notifications.services import NotificationService
        
        reservation_data = {
            'id': 1,
            'book_title': 'Reserved Book',
            'pickup_date': timezone.now() + timedelta(days=1)
        }
        
        NotificationService.send_reservation_confirmed(sample_user.id, reservation_data)
        
        from notifications.models import Notification
        notif = Notification.objects.filter(
            user_id=sample_user.id,
            notification_type='SUCCESS'
        ).first()
        
        assert notif is not None

    @patch('notifications.services.EmailService.send_email')
    def test_automatic_notification_with_email(self, mock_email, sample_user):
        """Test notification automatique avec email"""
        from notifications.services import NotificationService
        
        mock_email.return_value = {'success': True}
        
        loan_data = {
            'id': 1,
            'user_id': sample_user.id,
            'book_title': 'Test Book',
            'due_date': timezone.now() + timedelta(days=1)
        }
        
        NotificationService.send_due_soon_reminder(loan_data, send_email=True)
        
        assert mock_email.called


# ============================================
# 📊 TESTS STATISTIQUES NOTIFICATIONS
# ============================================

@pytest.mark.django_db
class TestNotificationStatistics:
    """Tests statistiques notifications"""

    def test_get_unread_count(self, authenticated_client, sample_user):
        """Test nombre notifications non lues"""
        from notifications.models import Notification
        
        for i in range(7):
            Notification.objects.create(
                user_id=sample_user.id,
                title=f'Unread {i}',
                message='Message',
                notification_type='INFO',
                is_read=False
                )
        
        for i in range(3):
            Notification.objects.create(
                user_id=sample_user.id,
                title=f'Read {i}',
                message='Message',
                notification_type='INFO',
                is_read=True,
                read_at=timezone.now()
            )
        
        response = authenticated_client.get('/api/notifications/unread-count/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['unread_count'] == 7

    def test_get_unread_count_zero(self, authenticated_client, sample_user):
        """Test compteur notifications non lues à zéro"""
        from notifications.models import Notification
        
        for i in range(5):
            Notification.objects.create(
                user_id=sample_user.id,
                title=f'Read {i}',
                message='Message',
                notification_type='INFO',
                is_read=True,
                read_at=timezone.now()
            )
        
        response = authenticated_client.get('/api/notifications/unread-count/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['unread_count'] == 0

    def test_get_notification_summary(self, authenticated_client, sample_user):
        """Test résumé notifications"""
        from notifications.models import Notification
        
        notification_types = {
            'INFO': 5,
            'WARNING': 3,
            'ERROR': 2,
            'SUCCESS': 4,
            'REMINDER': 1
        }
        
        for notif_type, count in notification_types.items():
            for i in range(count):
                Notification.objects.create(
                    user_id=sample_user.id,
                    title=f'{notif_type} {i}',
                    message='Message',
                    notification_type=notif_type
                )
        
        response = authenticated_client.get('/api/notifications/summary/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total' in response.data
        assert response.data['total'] == 15
        assert 'by_type' in response.data

    def test_get_summary_empty(self, authenticated_client):
        """Test résumé sans notifications"""
        response = authenticated_client.get('/api/notifications/summary/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total'] == 0


# ============================================
# ⚠️ TESTS CAS LIMITES
# ============================================

@pytest.mark.django_db
class TestNotificationEdgeCases:
    """Tests cas limites"""

    def test_create_notification_very_long_title(self, sample_user):
        """Test notification titre très long"""
        from notifications.models import Notification
        
        with pytest.raises(Exception):
            Notification.objects.create(
                user_id=sample_user.id,
                title='A' * 500,
                message='Message',
                notification_type='INFO'
            )

    def test_create_notification_empty_message(self, sample_user):
        """Test notification message vide"""
        from notifications.models import Notification
        
        with pytest.raises(Exception):
            Notification.objects.create(
                user_id=sample_user.id,
                title='Title',
                message='',
                notification_type='INFO'
            )

    def test_xss_in_notification_message(self, authenticated_client):
        """Test tentative XSS dans message"""
        response = authenticated_client.post('/api/notifications/send/', {
            'user_id': authenticated_client.handler._force_user.id,
            'title': 'Test',
            'message': '<script>alert("XSS")</script>',
            'notification_type': 'INFO'
        })
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_sql_injection_in_title(self, authenticated_client):
        """Test tentative SQL injection dans titre"""
        response = authenticated_client.post('/api/notifications/send/', {
            'user_id': authenticated_client.handler._force_user.id,
            'title': "'; DROP TABLE notifications; --",
            'message': 'Test',
            'notification_type': 'INFO'
        })
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_notification_for_nonexistent_user(self, authenticated_client):
        """Test notification pour utilisateur inexistant"""
        response = authenticated_client.post('/api/notifications/send/', {
            'user_id': 99999,
            'title': 'Test',
            'message': 'Test',
            'notification_type': 'INFO'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('notifications.services.EmailService.send_email')
    def test_email_service_failure_doesnt_block_notification(self, mock_email, authenticated_client):
        """Test échec email n'empêche pas notification"""
        mock_email.side_effect = Exception("Email service down")
        
        response = authenticated_client.post('/api/notifications/send/', {
            'user_id': authenticated_client.handler._force_user.id,
            'title': 'Test',
            'message': 'Test',
            'notification_type': 'INFO',
            'send_email': True
        })
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_unicode_characters_in_notification(self, authenticated_client):
        """Test caractères unicode dans notification"""
        response = authenticated_client.post('/api/notifications/send/', {
            'user_id': authenticated_client.handler._force_user.id,
            'title': 'Test émojis 🎉📚',
            'message': 'Message avec accents: éàèù 中文',
            'notification_type': 'INFO'
        })
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_very_long_message(self, authenticated_client):
        """Test message très long"""
        long_message = 'A' * 1000
        
        response = authenticated_client.post('/api/notifications/send/', {
            'user_id': authenticated_client.handler._force_user.id,
            'title': 'Long Message Test',
            'message': long_message,
            'notification_type': 'INFO'
        })
        
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_concurrent_mark_as_read(self, authenticated_client, sample_notification):
        """Test marquage concurrent comme lu"""
        response1 = authenticated_client.post(
            f'/api/notifications/{sample_notification.id}/mark-read/'
        )
        response2 = authenticated_client.post(
            f'/api/notifications/{sample_notification.id}/mark-read/'
        )
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK

    def test_notification_with_negative_user_id(self, authenticated_client):
        """Test notification avec user_id négatif"""
        response = authenticated_client.post('/api/notifications/send/', {
            'user_id': -1,
            'title': 'Test',
            'message': 'Test',
            'notification_type': 'INFO'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================
# 🔐 TESTS PERMISSIONS ET SÉCURITÉ
# ============================================

@pytest.mark.django_db
class TestNotificationSecurity:
    """Tests sécurité et permissions"""

    def test_unauthorized_access_to_list(self, api_client):
        """Test accès non autorisé à la liste"""
        response = api_client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthorized_delete(self, api_client, sample_notification):
        """Test suppression non autorisée"""
        response = api_client.delete(f'/api/notifications/{sample_notification.id}/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthorized_mark_as_read(self, api_client, sample_notification):
        """Test marquage non autorisé"""
        response = api_client.post(
            f'/api/notifications/{sample_notification.id}/mark-read/'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_cannot_access_others_notifications(self, api_client, sample_user, sample_user_2, sample_notification):
        """Test utilisateur ne peut pas accéder aux notifications d'autrui"""
        api_client.force_authenticate(user=sample_user_2)
        
        response = api_client.get(f'/api/notifications/{sample_notification.id}/')
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_user_cannot_delete_others_notifications(self, api_client, sample_user, sample_user_2, sample_notification):
        """Test utilisateur ne peut pas supprimer notifications d'autrui"""
        api_client.force_authenticate(user=sample_user_2)
        
        response = api_client.delete(f'/api/notifications/{sample_notification.id}/')
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


# ============================================
# 🧪 TESTS FILTRES AVANCÉS
# ============================================

@pytest.mark.django_db
class TestNotificationFilters:
    """Tests filtres avancés"""

    def test_filter_by_date_range(self, authenticated_client, sample_user):
        """Test filtre par plage de dates"""
        from notifications.models import Notification
        
        old = Notification.objects.create(
            user_id=sample_user.id,
            title='Old',
            message='Old',
            notification_type='INFO'
        )
        old.sent_at = timezone.now() - timedelta(days=10)
        old.save()
        
        recent = Notification.objects.create(
            user_id=sample_user.id,
            title='Recent',
            message='Recent',
            notification_type='INFO'
        )
        
        date_filter = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        response = authenticated_client.get(f'/api/notifications/?date_from={date_filter}')
        
        assert response.status_code == status.HTTP_200_OK

    def test_filter_by_related_object_type(self, authenticated_client, sample_user):
        """Test filtre par type d'objet lié"""
        from notifications.models import Notification
        
        Notification.objects.create(
            user_id=sample_user.id,
            title='Loan Notification',
            message='Test',
            notification_type='REMINDER',
            related_object_type='LOAN',
            related_object_id=1
        )
        
        Notification.objects.create(
            user_id=sample_user.id,
            title='Book Notification',
            message='Test',
            notification_type='INFO',
            related_object_type='BOOK',
            related_object_id=2
        )
        
        response = authenticated_client.get('/api/notifications/?related_type=LOAN')
        
        assert response.status_code == status.HTTP_200_OK
        if response.data['results']:
            for notif in response.data['results']:
                assert notif['related_object_type'] == 'LOAN'

    def test_ordering_by_different_fields(self, authenticated_client, sample_user):
        """Test tri par différents champs"""
        from notifications.models import Notification
        
        for i in range(5):
            Notification.objects.create(
                user_id=sample_user.id,
                title=f'Notification {i}',
                message='Message',
                notification_type='INFO'
            )
        
        response = authenticated_client.get('/api/notifications/?ordering=-sent_at')
        
        assert response.status_code == status.HTTP_200_OK


# ============================================
# 🔄 TESTS INTÉGRATION SERVICES
# ============================================

@pytest.mark.django_db
class TestNotificationServiceIntegration:
    """Tests intégration avec autres services"""

    @patch('notifications.services.UserService.get_user_email')
    @patch('notifications.services.EmailService.send_email')
    def test_send_notification_with_user_lookup(self, mock_email, mock_user_service, authenticated_client):
        """Test envoi avec recherche utilisateur"""
        mock_user_service.return_value = 'user@example.com'
        mock_email.return_value = {'success': True}
        
        response = authenticated_client.post('/api/notifications/send/', {
            'user_id': authenticated_client.handler._force_user.id,
            'title': 'Test',
            'message': 'Test',
            'notification_type': 'INFO',
            'send_email': True
        })
        
        assert response.status_code == status.HTTP_201_CREATED

    @patch('notifications.services.LoanService.get_overdue_loans')
    def test_batch_notification_for_overdue_loans(self, mock_loan_service, sample_user):
        """Test envoi batch pour emprunts en retard"""
        from notifications.services import NotificationService
        
        mock_loan_service.return_value = [
            {
                'id': 1,
                'user_id': sample_user.id,
                'book_title': 'Book 1',
                'due_date': timezone.now() - timedelta(days=1),
                'days_overdue': 1
            },
            {
                'id': 2,
                'user_id': sample_user.id,
                'book_title': 'Book 2',
                'due_date': timezone.now() - timedelta(days=2),
                'days_overdue': 2
            }
        ]
        
        NotificationService.send_batch_overdue_reminders()
        
        from notifications.models import Notification
        notifications = Notification.objects.filter(
            user_id=sample_user.id,
            notification_type='WARNING'
        )
        
        assert notifications.count() >= 2


# ============================================
# 📱 TESTS PERFORMANCE
# ============================================

@pytest.mark.django_db
class TestNotificationPerformance:
    """Tests performance"""

    def test_bulk_notification_creation(self, sample_user):
        """Test création en masse de notifications"""
        from notifications.models import Notification
        
        notifications = [
            Notification(
                user_id=sample_user.id,
                title=f'Notification {i}',
                message=f'Message {i}',
                notification_type='INFO'
            )
            for i in range(100)
        ]
        
        Notification.objects.bulk_create(notifications)
        
        count = Notification.objects.filter(user_id=sample_user.id).count()
        assert count == 100

    def test_pagination_performance(self, authenticated_client, sample_user):
        """Test performance pagination"""
        from notifications.models import Notification
        
        for i in range(50):
            Notification.objects.create(
                user_id=sample_user.id,
                title=f'Notification {i}',
                message='Message',
                notification_type='INFO'
            )
        
        response = authenticated_client.get('/api/notifications/?page=2')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data