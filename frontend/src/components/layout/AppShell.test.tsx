import { act, fireEvent, render, screen } from '@testing-library/react';
import { Activity, BookOpen } from 'lucide-react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../../context/AuthContext';
import { User } from '../../types/auth';
import { AppShell } from './AppShell';

const mockAdminUser: User = {
  id: 1,
  email: 'admin@example.com',
  full_name: 'Admin Boss',
  role: 'admin',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

const mockStudentUser: User = {
  id: 2,
  email: 'student@example.com',
  full_name: 'Jane Student',
  role: 'student',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

describe('AppShell Component', () => {
  it('renders navigation filtered for admin user (Account and System status)', () => {
    render(
      <MemoryRouter initialEntries={['/status']}>
        <AuthProvider initialUser={mockAdminUser}>
          <AppShell currentPath="/status">
            <div>Page test content</div>
          </AppShell>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByRole('link', { name: 'Account' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'System status' })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Profile' })).not.toBeInTheDocument();
    expect(screen.getByText('Page test content')).toBeInTheDocument();
    expect(screen.getAllByText('Admin Boss').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByRole('button', { name: 'Log out' }).length).toBeGreaterThanOrEqual(1);
  });

  it('filters out admin-only navigation for student role and shows Profile', () => {
    render(
      <MemoryRouter initialEntries={['/account']}>
        <AuthProvider initialUser={mockStudentUser}>
          <AppShell currentPath="/account">
            <div>Student account content</div>
          </AppShell>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByRole('link', { name: 'Profile' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Account' })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'System status' })).not.toBeInTheDocument();
    expect(screen.getAllByText('Jane Student').length).toBeGreaterThanOrEqual(1);
  });

  it('renders custom navigation items passed via navItems prop', () => {
    const customNavItems = [
      { path: '/account', label: 'Account', icon: Activity },
      { path: '/courses', label: 'Courses', icon: BookOpen },
    ];

    render(
      <MemoryRouter initialEntries={['/courses']}>
        <AuthProvider initialUser={mockStudentUser}>
          <AppShell navItems={customNavItems} currentPath="/courses">
            <div>Courses content</div>
          </AppShell>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByRole('link', { name: 'Account' })).toBeInTheDocument();
    const coursesLink = screen.getByRole('link', { name: 'Courses' });
    expect(coursesLink).toBeInTheDocument();
    expect(coursesLink).toHaveAttribute('aria-current', 'page');
  });

  it('toggles mobile menu open and closed', () => {
    render(
      <MemoryRouter initialEntries={['/account']}>
        <AuthProvider initialUser={mockStudentUser}>
          <AppShell currentPath="/account">
            <div>Content</div>
          </AppShell>
        </AuthProvider>
      </MemoryRouter>
    );

    const toggleButton = screen.getByRole('button', { name: 'Open menu' });
    expect(toggleButton).toHaveAttribute('aria-expanded', 'false');

    fireEvent.click(toggleButton);
    expect(screen.getByRole('button', { name: 'Close menu' })).toHaveAttribute(
      'aria-expanded',
      'true'
    );

    fireEvent.click(screen.getByRole('button', { name: 'Close menu' }));
    expect(screen.getByRole('button', { name: 'Open menu' })).toHaveAttribute(
      'aria-expanded',
      'false'
    );
  });

  it('calls logout when header Log out button is clicked', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ message: 'Logged out' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    render(
      <MemoryRouter initialEntries={['/account']}>
        <AuthProvider initialUser={mockStudentUser}>
          <AppShell currentPath="/account">
            <div>Content</div>
          </AppShell>
        </AuthProvider>
      </MemoryRouter>
    );

    const logoutBtns = screen.getAllByRole('button', { name: 'Log out' });
    await act(async () => {
      fireEvent.click(logoutBtns[0]);
    });

    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/auth/logout',
      expect.objectContaining({ method: 'POST' })
    );
  });
});
