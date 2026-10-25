import React from 'react';
import { Link } from 'react-router-dom';
import { Bell } from 'lucide-react';
import { useUnreadCount } from '../../hooks/useUnreadCount';
import { cn } from '../../lib/cn';

export interface NotificationBellProps {
  count?: number;
  className?: string;
  pollIntervalMs?: number;
}

export const NotificationBell: React.FC<NotificationBellProps> = ({
  count,
  className,
  pollIntervalMs,
}) => {
  const { unreadCount: polledCount } = useUnreadCount({
    enabled: count === undefined,
    pollIntervalMs,
  });

  const unreadCount = count !== undefined ? count : polledCount;
  const label = unreadCount > 0 ? `Notifications (${unreadCount} unread)` : 'Notifications';

  return (
    <Link
      to="/notifications"
      aria-label={label}
      title={label}
      className={cn(
        'relative inline-flex items-center justify-center rounded-control p-2 text-pencil hover:bg-chalk hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol transition-colors',
        className
      )}
    >
      <Bell className="h-5 w-5 shrink-0" aria-hidden="true" />
      {unreadCount > 0 && (
        <span
          data-testid="unread-badge"
          className="absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-petrol px-1 text-[10px] font-bold leading-none text-surface"
        >
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
    </Link>
  );
};
