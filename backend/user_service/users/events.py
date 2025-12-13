"""
Event Publishers for User Service
Publishes events: user.registered
Place this file in: backend/user_service/users/events.py
"""

import logging
import sys
import os
import json

# Add common directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

from rabbitmq_client import get_rabbitmq_client

logger = logging.getLogger(__name__)


def publish_user_registered(user):
    """
    Publish user_registered event
    
    Args:
        user: User object
    """
    rabbitmq = get_rabbitmq_client()
    
    message = {
        'event_type': 'user_registered',
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'timestamp': user.date_joined.isoformat() if hasattr(user, 'date_joined') else None
    }
    
    # Publish to general user queue
    rabbitmq.publish('user.registered', message)
    
    # Publish to notification queue
    rabbitmq.publish('notification.email.user_registered', message)
    
    logger.info(f"📤 Published user_registered event for user {user.username} (#{user.id})")



