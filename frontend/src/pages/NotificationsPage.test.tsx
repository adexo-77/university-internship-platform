import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as notifApi from '../api/notification';
import { NotificationsPage } from './NotificationsPage';
import { NotificationItemData } from '../types/notification';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const sampleNotifications: NotificationItemData[] = [
  {
    id: 11,
    user_id: 2,
    kind: 'application_decision',
    title: 'Application Accepted: Mobile Dev',
    message: 'Congratulations!',
    link_path: '/applications/55',
    read_at: null,
    created_at: new Date().toISOString(),
  },
  {
    id: 12,
    user_id: 2,
    kind: 'internship_approved',
    title: 'Internship Posting Approved',
    message: 'Your posting is now published in the catalog.',
    link_path: '/internships/99',
    read_at: new Date().toISOString(),
    created_at: new Date().toISOString(),
  },
];

describe('NotificationsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads notifications and renders them in the list', async () => {
    vi.spyOn(notifApi, 'fetchNotifications').mockResolvedValue({
      items: sampleNotifications,
      total: 2,
      unread_count: 1,
    });

    render(
      <MemoryRouter>
        <NotificationsPage />
      </MemoryRouter>
    );

    expect(screen.getByText('Loading notifications...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Application Accepted: Mobile Dev')).toBeInTheDocument();
      expect(screen.getByText('Internship Posting Approved')).toBeInTheDocument();
    });
  });

  it('marks an unread notification as read on click and navigates to link_path', async () => {
    vi.spyOn(notifApi, 'fetchNotifications').mockResolvedValue({
      items: sampleNotifications,
      total: 2,
      unread_count: 1,
    });
    const markReadSpy = vi
      .spyOn(notifApi, 'markNotificationAsRead')
      .mockResolvedValue({ ...sampleNotifications[0], read_at: new Date().toISOString() });

    render(
      <MemoryRouter>
        <NotificationsPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Application Accepted: Mobile Dev')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('notification-item-11'));

    await waitFor(() => {
      expect(markReadSpy).toHaveBeenCalledWith(11);
      expect(mockNavigate).toHaveBeenCalledWith('/applications/55');
    });
  });

  it('does not call mark read when clicking an already read notification', async () => {
    vi.spyOn(notifApi, 'fetchNotifications').mockResolvedValue({
      items: sampleNotifications,
      total: 2,
      unread_count: 1,
    });
    const markReadSpy = vi.spyOn(notifApi, 'markNotificationAsRead');

    render(
      <MemoryRouter>
        <NotificationsPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Internship Posting Approved')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('notification-item-12'));

    expect(markReadSpy).not.toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/internships/99');
  });

  it('marks all as read when button is clicked', async () => {
    const fetchSpy = vi.spyOn(notifApi, 'fetchNotifications').mockResolvedValue({
      items: sampleNotifications,
      total: 2,
      unread_count: 1,
    });
    const markAllSpy = vi
      .spyOn(notifApi, 'markAllNotificationsAsRead')
      .mockResolvedValue({ marked_read: 1 });

    render(
      <MemoryRouter>
        <NotificationsPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Mark all as read' })).not.toBeDisabled();
    });

    fireEvent.click(screen.getByRole('button', { name: 'Mark all as read' }));

    await waitFor(() => {
      expect(markAllSpy).toHaveBeenCalledTimes(1);
      expect(fetchSpy).toHaveBeenCalledTimes(2);
    });
  });

  it('renders empty state when there are no notifications', async () => {
    vi.spyOn(notifApi, 'fetchNotifications').mockResolvedValue({
      items: [],
      total: 0,
      unread_count: 0,
    });

    render(
      <MemoryRouter>
        <NotificationsPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('No notifications')).toBeInTheDocument();
      expect(
        screen.getByText("You're all caught up! No notifications to display.")
      ).toBeInTheDocument();
    });
  });
});
