import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  fetchNotifications,
  markAllNotificationsAsRead,
  markNotificationAsRead,
} from '../api/notification';
import { NotificationList } from '../components/notifications/NotificationList';
import { ErrorMessage, PageHeader } from '../components/ui';
import { usePageTitle } from '../hooks/usePageTitle';
import { NotificationItemData } from '../types/notification';

const PAGE_SIZE = 20;

export const NotificationsPage: React.FC = () => {
  usePageTitle('Notifications');
  const navigate = useNavigate();

  const [notifications, setNotifications] = useState<NotificationItemData[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [unreadOnly, setUnreadOnly] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isMarkingAll, setIsMarkingAll] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadNotifications = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await fetchNotifications({
        unread_only: unreadOnly,
        limit: PAGE_SIZE,
        offset: (page - 1) * PAGE_SIZE,
      });
      setNotifications(res.items);
      setTotal(res.total);
      setUnreadCount(res.unread_count);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load notifications');
    } finally {
      setIsLoading(false);
    }
  }, [page, unreadOnly]);

  useEffect(() => {
    void loadNotifications();
  }, [loadNotifications]);

  const handleNotificationClick = async (item: NotificationItemData) => {
    if (item.read_at === null) {
      try {
        await markNotificationAsRead(item.id);
        setNotifications((prev) =>
          prev.map((n) => (n.id === item.id ? { ...n, read_at: new Date().toISOString() } : n))
        );
        setUnreadCount((prev) => Math.max(0, prev - 1));
      } catch {
        // Still proceed to navigate even if mark-read failed
      }
    }
    navigate(item.link_path);
  };

  const handleMarkAllAsRead = async () => {
    try {
      setIsMarkingAll(true);
      await markAllNotificationsAsRead();
      await loadNotifications();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to mark all as read');
    } finally {
      setIsMarkingAll(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Notifications"
        description="Stay updated on courses, submissions, applications, and account activity."
      />

      {error && (
        <ErrorMessage whatHappened={error} howToFix="Please try again or refresh the page." />
      )}

      <NotificationList
        notifications={notifications}
        unreadCount={unreadCount}
        total={total}
        page={page}
        pageSize={PAGE_SIZE}
        unreadOnly={unreadOnly}
        isLoading={isLoading}
        isMarkingAll={isMarkingAll}
        onPageChange={(newPage) => setPage(newPage)}
        onFilterChange={(newUnreadOnly) => {
          setUnreadOnly(newUnreadOnly);
          setPage(1);
        }}
        onNotificationClick={handleNotificationClick}
        onMarkAllAsRead={handleMarkAllAsRead}
      />
    </div>
  );
};
