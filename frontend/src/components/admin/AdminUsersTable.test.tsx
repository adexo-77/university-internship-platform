import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { AdminUser } from '../../types/admin';
import { AdminUsersTable } from './AdminUsersTable';

const mockUsers: AdminUser[] = [
  {
    id: 1,
    email: 'admin@example.edu',
    full_name: 'Super Admin',
    role: 'admin',
    is_active: true,
    created_at: '2026-10-15T10:00:00Z',
    updated_at: '2026-10-15T10:00:00Z',
  },
  {
    id: 2,
    email: 'instructor@example.edu',
    full_name: 'Dr. Jane Instructor',
    role: 'instructor',
    is_active: false,
    created_at: '2026-10-16T10:00:00Z',
    updated_at: '2026-10-16T10:00:00Z',
  },
];

describe('AdminUsersTable Component', () => {
  it('renders user details, roles, statuses, and created dates', () => {
    render(
      <AdminUsersTable users={mockUsers} onToggleStatus={vi.fn()} onResetPassword={vi.fn()} />
    );

    expect(screen.getByText('Super Admin')).toBeInTheDocument();
    expect(screen.getByText('admin@example.edu')).toBeInTheDocument();
    expect(screen.getByText('admin')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();

    expect(screen.getByText('Dr. Jane Instructor')).toBeInTheDocument();
    expect(screen.getByText('instructor@example.edu')).toBeInTheDocument();
    expect(screen.getByText('instructor')).toBeInTheDocument();
    expect(screen.getByText('Inactive')).toBeInTheDocument();
  });

  it('triggers onToggleStatus and onResetPassword when row action buttons are clicked', () => {
    const handleToggle = vi.fn();
    const handleReset = vi.fn();

    render(
      <AdminUsersTable
        users={mockUsers}
        onToggleStatus={handleToggle}
        onResetPassword={handleReset}
      />
    );

    const deactivateBtn = screen.getByRole('button', { name: 'Deactivate' });
    fireEvent.click(deactivateBtn);
    expect(handleToggle).toHaveBeenCalledWith(mockUsers[0]);

    const activateBtn = screen.getByRole('button', { name: 'Activate' });
    fireEvent.click(activateBtn);
    expect(handleToggle).toHaveBeenCalledWith(mockUsers[1]);

    const resetButtons = screen.getAllByRole('button', { name: 'Reset password' });
    fireEvent.click(resetButtons[0]);
    expect(handleReset).toHaveBeenCalledWith(mockUsers[0]);
  });
});
