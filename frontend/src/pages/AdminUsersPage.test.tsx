import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as adminUserApi from '../api/admin_user';
import { AuthProvider } from '../context/AuthContext';
import { AdminUsersPage } from './AdminUsersPage';
import { AdminUser } from '../types/admin';
import { User } from '../types/auth';

vi.mock('../api/admin_user', () => ({
  listAdminUsers: vi.fn(),
  updateAdminUserStatus: vi.fn(),
  resetAdminUserPassword: vi.fn(),
}));

const mockAdminAuthUser: User = {
  id: 99,
  email: 'chief.admin@university.edu',
  full_name: 'Chief Admin',
  role: 'admin',
  is_active: true,
  created_at: '2026-10-10T10:00:00Z',
  updated_at: '2026-10-10T10:00:00Z',
};

const mockAdminUsers: AdminUser[] = [
  {
    id: 1,
    email: 'alice@brolf.edu',
    full_name: 'Alice Instructor',
    role: 'instructor',
    is_active: true,
    created_at: '2026-10-12T10:00:00Z',
    updated_at: '2026-10-12T10:00:00Z',
  },
  {
    id: 2,
    email: 'bob@brolf.edu',
    full_name: 'Bob Student',
    role: 'student',
    is_active: false,
    created_at: '2026-10-14T10:00:00Z',
    updated_at: '2026-10-14T10:00:00Z',
  },
];

describe('AdminUsersPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders search input, role filter, users table, and "New user" button', async () => {
    vi.mocked(adminUserApi.listAdminUsers).mockResolvedValue({
      items: mockAdminUsers,
      total: 2,
      limit: 10,
      offset: 0,
    });

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockAdminAuthUser}>
          <AdminUsersPage />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByLabelText(/search users/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/role filter/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /new user/i })).toBeInTheDocument();

    expect(await screen.findByText('Alice Instructor')).toBeInTheDocument();
    expect(screen.getByText('Bob Student')).toBeInTheDocument();
  });

  it('filters users when search query and role filter change', async () => {
    vi.mocked(adminUserApi.listAdminUsers).mockResolvedValue({
      items: [mockAdminUsers[0]],
      total: 1,
      limit: 10,
      offset: 0,
    });

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockAdminAuthUser}>
          <AdminUsersPage />
        </AuthProvider>
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/search users/i), {
      target: { value: 'alice' },
    });

    await waitFor(() => {
      expect(adminUserApi.listAdminUsers).toHaveBeenCalledWith(
        expect.objectContaining({ q: 'alice' })
      );
    });

    fireEvent.change(screen.getByLabelText(/role filter/i), {
      target: { value: 'instructor' },
    });

    await waitFor(() => {
      expect(adminUserApi.listAdminUsers).toHaveBeenCalledWith(
        expect.objectContaining({ role: 'instructor' })
      );
    });
  });
});
