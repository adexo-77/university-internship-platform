import { act, fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../context/AuthContext';
import { User } from '../../types/auth';
import { AppShell } from './AppShell';

vi.mock('../../api/notification', () => ({
  fetchUnreadCount: vi.fn().mockResolvedValue({ unread_count: 0 }),
}));

const mockStudentUser: User = {
  id: 10,
  email: 'student@example.com',
  full_name: 'Student Mobile',
  role: 'student',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

describe('AppShell Mobile Drawer', () => {
  it('locks body scroll when opened and restores it on close', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/courses']}>
          <AuthProvider initialUser={mockStudentUser}>
            <AppShell currentPath="/courses">
              <div>Mobile content</div>
            </AppShell>
          </AuthProvider>
        </MemoryRouter>
      );
    });

    expect(document.body.style.overflow).toBe('');

    const openButton = screen.getByRole('button', { name: 'Open menu' });
    await act(async () => {
      fireEvent.click(openButton);
    });
    expect(document.body.style.overflow).toBe('hidden');

    const overlay = screen.getByRole('presentation', { hidden: true });
    await act(async () => {
      fireEvent.click(overlay);
    });
    expect(document.body.style.overflow).toBe('');
  });

  it('closes mobile drawer when Escape key is pressed', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/courses']}>
          <AuthProvider initialUser={mockStudentUser}>
            <AppShell currentPath="/courses">
              <div>Content</div>
            </AppShell>
          </AuthProvider>
        </MemoryRouter>
      );
    });

    const openButton = screen.getByRole('button', { name: 'Open menu' });
    await act(async () => {
      fireEvent.click(openButton);
    });
    expect(screen.getByLabelText('Navigation drawer')).toHaveClass('translate-x-0');

    await act(async () => {
      fireEvent.keyDown(window, { key: 'Escape' });
    });
    expect(screen.getByLabelText('Navigation drawer')).toHaveClass('-translate-x-full');
  });

  it('traps focus inside mobile drawer on Tab and Shift+Tab', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/courses']}>
          <AuthProvider initialUser={mockStudentUser}>
            <AppShell currentPath="/courses">
              <div>Content</div>
            </AppShell>
          </AuthProvider>
        </MemoryRouter>
      );
    });

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Open menu' }));
    });

    const drawer = screen.getByLabelText('Navigation drawer');
    const focusables = drawer.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    expect(focusables.length).toBeGreaterThan(1);

    const first = focusables[0];
    const last = focusables[focusables.length - 1];

    await act(async () => {
      last.focus();
    });
    expect(document.activeElement).toBe(last);

    // Tab on last element wraps to first
    await act(async () => {
      fireEvent.keyDown(window, { key: 'Tab', shiftKey: false });
    });
    expect(document.activeElement).toBe(first);

    // Shift+Tab on first element wraps to last
    await act(async () => {
      fireEvent.keyDown(window, { key: 'Tab', shiftKey: true });
    });
    expect(document.activeElement).toBe(last);
  });

  it('closes drawer when explicit close button in drawer header is clicked', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/courses']}>
          <AuthProvider initialUser={mockStudentUser}>
            <AppShell currentPath="/courses">
              <div>Content</div>
            </AppShell>
          </AuthProvider>
        </MemoryRouter>
      );
    });

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Open menu' }));
    });
    const closeDrawerBtn = screen.getByRole('button', { name: 'Close menu drawer' });
    expect(closeDrawerBtn).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(closeDrawerBtn);
    });
    expect(screen.getByLabelText('Navigation drawer')).toHaveClass('-translate-x-full');
  });
});
