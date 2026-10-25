import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { NotificationList } from './NotificationList';
import { NotificationItemData } from '../../types/notification';

const mockNotifications: NotificationItemData[] = [
  {
    id: 1,
    user_id: 10,
    kind: 'assignment_created',
    title: 'New Assignment: Lab 1',
    message: 'Assignment Lab 1 in Distributed Systems was posted.',
    link_path: '/assignments/101',
    read_at: null,
    created_at: new Date(Date.now() - 5 * 60_000).toISOString(),
  },
  {
    id: 2,
    user_id: 10,
    kind: 'submission_graded',
    title: 'Submission Graded: Midterm',
    message: 'Your submission scored 95/100.',
    link_path: '/assignments/102',
    read_at: new Date(Date.now() - 3600_000).toISOString(),
    created_at: new Date(Date.now() - 7200_000).toISOString(),
  },
];

describe('NotificationList Component', () => {
  it('renders notifications with relative time and visually distinct unread styling', () => {
    render(
      <NotificationList
        notifications={mockNotifications}
        unreadCount={1}
        total={2}
        page={1}
        pageSize={10}
        unreadOnly={false}
        isLoading={false}
        onPageChange={vi.fn()}
        onFilterChange={vi.fn()}
        onNotificationClick={vi.fn()}
        onMarkAllAsRead={vi.fn()}
      />
    );

    expect(screen.getByText('New Assignment: Lab 1')).toBeInTheDocument();
    expect(screen.getByText('Submission Graded: Midterm')).toBeInTheDocument();

    // First item is unread: should have unread dot
    const unreadDot = screen.getByTestId('unread-dot');
    expect(unreadDot).toBeInTheDocument();

    // Unread item container should have data-unread="true" and bg-petrol-tint
    const unreadItem = screen.getByTestId('notification-item-1');
    expect(unreadItem).toHaveAttribute('data-unread', 'true');
    expect(unreadItem).toHaveClass('bg-petrol-tint');

    // Read item should have data-unread="false"
    const readItem = screen.getByTestId('notification-item-2');
    expect(readItem).toHaveAttribute('data-unread', 'false');
  });

  it('calls onNotificationClick when an item is clicked', () => {
    const onNotificationClick = vi.fn();
    render(
      <NotificationList
        notifications={mockNotifications}
        unreadCount={1}
        total={2}
        page={1}
        pageSize={10}
        unreadOnly={false}
        isLoading={false}
        onPageChange={vi.fn()}
        onFilterChange={vi.fn()}
        onNotificationClick={onNotificationClick}
        onMarkAllAsRead={vi.fn()}
      />
    );

    fireEvent.click(screen.getByTestId('notification-item-1'));
    expect(onNotificationClick).toHaveBeenCalledWith(mockNotifications[0]);
  });

  it('renders empty state when there are no notifications', () => {
    render(
      <NotificationList
        notifications={[]}
        unreadCount={0}
        total={0}
        page={1}
        pageSize={10}
        unreadOnly={false}
        isLoading={false}
        onPageChange={vi.fn()}
        onFilterChange={vi.fn()}
        onNotificationClick={vi.fn()}
        onMarkAllAsRead={vi.fn()}
      />
    );

    expect(screen.getByText('No notifications')).toBeInTheDocument();
    expect(
      screen.getByText("You're all caught up! No notifications to display.")
    ).toBeInTheDocument();
  });

  it('triggers onMarkAllAsRead when Mark all as read button is clicked', () => {
    const onMarkAll = vi.fn();
    render(
      <NotificationList
        notifications={mockNotifications}
        unreadCount={1}
        total={2}
        page={1}
        pageSize={10}
        unreadOnly={false}
        isLoading={false}
        onPageChange={vi.fn()}
        onFilterChange={vi.fn()}
        onNotificationClick={vi.fn()}
        onMarkAllAsRead={onMarkAll}
      />
    );

    const markAllButton = screen.getByRole('button', { name: 'Mark all as read' });
    expect(markAllButton).not.toBeDisabled();
    fireEvent.click(markAllButton);
    expect(onMarkAll).toHaveBeenCalledTimes(1);
  });

  it('renders pagination controls and handles page changes', () => {
    const onPageChange = vi.fn();
    render(
      <NotificationList
        notifications={mockNotifications}
        unreadCount={0}
        total={25}
        page={1}
        pageSize={10}
        unreadOnly={false}
        isLoading={false}
        onPageChange={onPageChange}
        onFilterChange={vi.fn()}
        onNotificationClick={vi.fn()}
        onMarkAllAsRead={vi.fn()}
      />
    );

    expect(screen.getByText('Page 1 of 3')).toBeInTheDocument();
    const prevButton = screen.getByRole('button', { name: 'Previous' });
    const nextButton = screen.getByRole('button', { name: 'Next' });

    expect(prevButton).toBeDisabled();
    expect(nextButton).not.toBeDisabled();

    fireEvent.click(nextButton);
    expect(onPageChange).toHaveBeenCalledWith(2);
  });
});
