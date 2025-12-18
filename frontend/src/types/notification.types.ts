export type NotificationType = 'EMAIL' | 'SMS';
export type NotificationStatus = 'PENDING' | 'SENT' | 'FAILED';

export interface Notification {
  id: number;
  user_id: number;
  type: NotificationType;
  subject: string;
  message: string;
  status: NotificationStatus;
  sent_at: string | null;
  created_at: string;
}

export interface NotificationStats {
  period_days: number;
  total_notifications: number;
  by_status: {
    SENT: number;
    PENDING: number;
    FAILED: number;
  };
  by_type: {
    EMAIL: number;
    SMS: number;
  };
  success_rate: number;
  counts: {
    sent: number;
    failed: number;
    pending: number;
  };
}
