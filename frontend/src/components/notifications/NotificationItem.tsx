import React from 'react';
import { formatRelativeTime } from '../../lib/dates';
import { cn } from '../../lib/cn';
import { NotificationItemData } from '../../types/notification';

export interface NotificationItemProps {
  notification: NotificationItemData;
  onClick: (notification: NotificationItemData) => void;
}

export const NotificationItem: React.FC<NotificationItemProps> = ({ notification, onClick }) => {
  const isUnread = notification.read_at === null;

  return (
    <div
      role="button"
      tabIndex={0}
      data-testid={`notification-item-${notification.id}`}
      data-unread={isUnread}
      onClick={() => onClick(notification)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick(notification);
        }
      }}
      className={cn(
        'group flex flex-col gap-1 p-4 border-b border-line text-left transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-petrol',
        isUnread
          ? 'bg-petrol-tint border-petrol hover:bg-petrol-tint'
          : 'bg-surface hover:bg-chalk text-pencil'
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          {isUnread && (
            <span
              data-testid="unread-dot"
              className="h-2 w-2 rounded-full bg-petrol shrink-0"
              aria-label="Unread"
            />
          )}
          <span
            className={cn(
              'text-base leading-snug truncate',
              isUnread ? 'font-semibold text-ink' : 'font-medium text-ink'
            )}
          >
            {notification.title}
          </span>
        </div>
        <span className="text-xs text-pencil shrink-0">
          {formatRelativeTime(notification.created_at)}
        </span>
      </div>

      <p className="text-sm text-pencil line-clamp-2 mt-0.5">{notification.message}</p>
    </div>
  );
};
