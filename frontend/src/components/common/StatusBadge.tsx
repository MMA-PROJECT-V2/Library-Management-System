import { cn } from '@/lib/utils';
import type { LoanStatus } from '@/types/loan.types';

interface StatusBadgeProps {
  status: LoanStatus;
  className?: string;
}

const statusConfig: Record<LoanStatus, { label: string; className: string }> = {
  ACTIVE: {
    label: 'Active',
    className: 'bg-info/10 text-info border-info/20',
  },
  RENEWED: {
    label: 'Renewed',
    className: 'bg-accent/10 text-accent border-accent/20',
  },
  RETURNED: {
    label: 'Returned',
    className: 'bg-success/10 text-success border-success/20',
  },
  OVERDUE: {
    label: 'Overdue',
    className: 'bg-destructive/10 text-destructive border-destructive/20',
  },
};

export const StatusBadge = ({ status, className }: StatusBadgeProps) => {
  const config = statusConfig[status];
  
  return (
    <span 
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        config.className,
        className
      )}
    >
      {config.label}
    </span>
  );
};
