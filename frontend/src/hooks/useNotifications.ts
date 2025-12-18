import { useEffect, useCallback, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { notificationsService } from '@/services/notifications.service';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import type { Notification } from '@/types/notification.types';

const POLLING_INTERVAL = 30000; // 30 seconds

export const useNotifications = () => {
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [lastNotificationCount, setLastNotificationCount] = useState(0);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['notifications', user?.id],
    queryFn: async () => {
      const response = await notificationsService.getUserNotifications(user?.id);
      return response.data;
    },
    enabled: isAuthenticated && !!user?.id,
    refetchInterval: POLLING_INTERVAL,
    staleTime: POLLING_INTERVAL - 5000,
  });

  const notifications = data || [];
  const unreadCount = notifications.filter(n => n.status === 'PENDING').length;

  // Check for new notifications and show toast
  useEffect(() => {
    if (notifications.length > lastNotificationCount && lastNotificationCount > 0) {
      const newNotifications = notifications.slice(0, notifications.length - lastNotificationCount);
      newNotifications.forEach((notification: Notification) => {
        toast({
          title: notification.subject,
          description: notification.message.substring(0, 100) + (notification.message.length > 100 ? '...' : ''),
        });
      });
    }
    setLastNotificationCount(notifications.length);
  }, [notifications.length, lastNotificationCount, toast]);

  // Check for due date reminders
  const checkDueDateReminders = useCallback(() => {
    const dueDateNotifications = notifications.filter(
      n => n.subject.toLowerCase().includes('rappel') || n.subject.toLowerCase().includes('reminder')
    );
    
    if (dueDateNotifications.length > 0) {
      dueDateNotifications.forEach((notification: Notification) => {
        if (notification.status === 'PENDING') {
          toast({
            title: "📚 Due Date Reminder",
            description: notification.message,
            variant: "default",
          });
        }
      });
    }
  }, [notifications, toast]);

  useEffect(() => {
    if (isAuthenticated) {
      checkDueDateReminders();
    }
  }, [isAuthenticated, checkDueDateReminders]);

  const invalidateNotifications = () => {
    queryClient.invalidateQueries({ queryKey: ['notifications'] });
  };

  return {
    notifications,
    unreadCount,
    isLoading,
    error,
    refetch,
    invalidateNotifications,
  };
};

export const useNotificationStats = (days: number = 30) => {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['notification-stats', days],
    queryFn: async () => {
      const response = await notificationsService.getStats(days);
      return response.data;
    },
    enabled: isAuthenticated,
  });
};
