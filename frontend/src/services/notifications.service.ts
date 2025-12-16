import api, { NOTIFICATIONS_SERVICE_URL } from './api';
import type { Notification, NotificationStats } from '@/types/notification.types';

export const notificationsService = {
  getUserNotifications: (userId?: number) => 
    api.get<Notification[]>(`${NOTIFICATIONS_SERVICE_URL}/notifications/user_notifications/`, {
      params: userId ? { user_id: userId } : {}
    }),
  
  getStats: (days?: number) => 
    api.get<NotificationStats>(`${NOTIFICATIONS_SERVICE_URL}/notifications/stats/`, {
      params: { days: days || 30 }
    }),
  
  healthCheck: () => 
    api.get<{ status: string; service: string; timestamp: string }>(`${NOTIFICATIONS_SERVICE_URL}/health/`),
};
