import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as notifApi from '../../api/notification';
import { NotificationBell } from './NotificationBell';

describe('NotificationBell Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(notifApi, 'fetchUnreadCount').mockResolvedValue({ unread_count: 0 });
  });

  it('renders bell link pointing to /notifications with base label when count is 0', () => {
    render(
      <MemoryRouter>
        <NotificationBell count={0} />
      </MemoryRouter>
    );

    const link = screen.getByRole('link', { name: 'Notifications' });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', '/notifications');

    // Badge should not be present
    expect(screen.queryByTestId('unread-badge')).not.toBeInTheDocument();
  });

  it('renders unread count badge in petrol with accessible label when count > 0', () => {
    render(
      <MemoryRouter>
        <NotificationBell count={4} />
      </MemoryRouter>
    );

    const link = screen.getByRole('link', { name: 'Notifications (4 unread)' });
    expect(link).toBeInTheDocument();

    const badge = screen.getByTestId('unread-badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent('4');
    expect(badge).toHaveClass('bg-petrol');
    expect(badge).toHaveClass('text-surface');
  });

  it('caps badge display at 99+ when count exceeds 99', () => {
    render(
      <MemoryRouter>
        <NotificationBell count={150} />
      </MemoryRouter>
    );

    const link = screen.getByRole('link', { name: 'Notifications (150 unread)' });
    expect(link).toBeInTheDocument();

    const badge = screen.getByTestId('unread-badge');
    expect(badge).toHaveTextContent('99+');
  });
});
