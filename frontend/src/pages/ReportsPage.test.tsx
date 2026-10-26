import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { AuthProvider } from '../context/AuthContext';
import { User } from '../types/auth';
import { ReportsPage } from './ReportsPage';

const mockAdmin: User = {
  id: 1,
  email: 'admin@university.edu',
  full_name: 'Administrator',
  role: 'admin',
  is_active: true,
  created_at: '2026-10-10T10:00:00Z',
  updated_at: '2026-10-10T10:00:00Z',
};

const mockCoordinator: User = {
  id: 2,
  email: 'coord@university.edu',
  full_name: 'Coordinator',
  role: 'coordinator',
  is_active: true,
  created_at: '2026-10-10T10:00:00Z',
  updated_at: '2026-10-10T10:00:00Z',
};

describe('ReportsPage', () => {
  it('renders both Applications and Users export cards for admin', () => {
    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockAdmin}>
          <ReportsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: 'Reports', level: 1 })).toBeInTheDocument();
    expect(screen.getByTestId('applications-report-card')).toBeInTheDocument();
    expect(screen.getByTestId('users-report-card')).toBeInTheDocument();

    const links = screen.getAllByRole('link', { name: 'Export CSV' });
    expect(links).toHaveLength(2);
    expect(links[0]).toHaveAttribute('href', '/api/admin/reports/applications.csv');
    expect(links[1]).toHaveAttribute('href', '/api/admin/reports/users.csv');
  });

  it('renders Applications card but hides Users card for coordinator', () => {
    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockCoordinator}>
          <ReportsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: 'Reports', level: 1 })).toBeInTheDocument();
    expect(screen.getByTestId('applications-report-card')).toBeInTheDocument();
    expect(screen.queryByTestId('users-report-card')).not.toBeInTheDocument();

    const links = screen.getAllByRole('link', { name: 'Export CSV' });
    expect(links).toHaveLength(1);
    expect(links[0]).toHaveAttribute('href', '/api/admin/reports/applications.csv');
  });
});
