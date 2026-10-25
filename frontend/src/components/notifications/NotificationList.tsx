import React from 'react';
import { Button, EmptyState } from '../ui';
import { NotificationItem } from './NotificationItem';
import { NotificationItemData } from '../../types/notification';

export interface NotificationListProps {
  notifications: NotificationItemData[];
  unreadCount: number;
  total: number;
  page: number;
  pageSize: number;
  unreadOnly: boolean;
  isLoading: boolean;
  isMarkingAll?: boolean;
  onPageChange: (newPage: number) => void;
  onFilterChange: (unreadOnly: boolean) => void;
  onNotificationClick: (notification: NotificationItemData) => void;
  onMarkAllAsRead: () => void;
}

export const NotificationList: React.FC<NotificationListProps> = ({
  notifications,
  unreadCount,
  total,
  page,
  pageSize,
  unreadOnly,
  isLoading,
  isMarkingAll = false,
  onPageChange,
  onFilterChange,
  onNotificationClick,
  onMarkAllAsRead,
}) => {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-4">
      {/* Controls Bar: Filters and Mark All Read */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-3">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => onFilterChange(false)}
            className={`rounded-control px-3 py-1.5 text-sm font-medium transition-colors ${
              !unreadOnly ? 'bg-petrol text-surface' : 'text-pencil hover:bg-chalk hover:text-ink'
            }`}
          >
            All
          </button>
          <button
            type="button"
            onClick={() => onFilterChange(true)}
            className={`rounded-control px-3 py-1.5 text-sm font-medium transition-colors ${
              unreadOnly ? 'bg-petrol text-surface' : 'text-pencil hover:bg-chalk hover:text-ink'
            }`}
          >
            Unread only {unreadCount > 0 && `(${unreadCount})`}
          </button>
        </div>

        <Button
          variant="secondary"
          size="sm"
          onClick={onMarkAllAsRead}
          disabled={unreadCount === 0 || isMarkingAll}
        >
          {isMarkingAll ? 'Marking...' : 'Mark all as read'}
        </Button>
      </div>

      {/* Content Area */}
      {isLoading ? (
        <div className="rounded-control border border-line bg-surface p-8 text-center text-pencil">
          Loading notifications...
        </div>
      ) : notifications.length === 0 ? (
        <EmptyState
          title="No notifications"
          description={
            unreadOnly
              ? 'You have no unread notifications.'
              : "You're all caught up! No notifications to display."
          }
        />
      ) : (
        <div className="rounded-control border border-line overflow-hidden bg-surface divide-y divide-line">
          {notifications.map((item) => (
            <NotificationItem key={item.id} notification={item} onClick={onNotificationClick} />
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2 text-sm text-pencil">
          <span>
            Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} of {total}
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
            >
              Previous
            </Button>
            <span className="px-2">
              Page {page} of {totalPages}
            </span>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
