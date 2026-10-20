import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { AdminUser } from '../../types/admin';
import { AdminUserStatusModal } from './AdminUserStatusModal';

const activeUser: AdminUser = {
  id: 1,
  email: 'active@test.com',
  full_name: 'Alice Active',
  role: 'instructor',
  is_active: true,
  created_at: '2026-10-15T10:00:00Z',
  updated_at: '2026-10-15T10:00:00Z',
};

const inactiveUser: AdminUser = {
  id: 2,
  email: 'inactive@test.com',
  full_name: 'Bob Inactive',
  role: 'student',
  is_active: false,
  created_at: '2026-10-15T10:00:00Z',
  updated_at: '2026-10-15T10:00:00Z',
};

describe('AdminUserStatusModal Component', () => {
  it('renders deactivation confirmation message and triggers onConfirm', async () => {
    const handleConfirm = vi.fn().mockResolvedValue(undefined);
    const handleClose = vi.fn();

    render(
      <AdminUserStatusModal
        user={activeUser}
        isOpen={true}
        onClose={handleClose}
        onConfirm={handleConfirm}
        isSubmitting={false}
      />
    );

    expect(screen.getByText(/deactivate user account/i)).toBeInTheDocument();
    expect(
      screen.getByText(
        /Are you sure you want to deactivate Alice Active\? This will invalidate all active sessions and prevent the user from signing in\./i
      )
    ).toBeInTheDocument();

    const deactBtn = screen.getByRole('button', { name: 'Deactivate user' });
    fireEvent.click(deactBtn);
    expect(handleConfirm).toHaveBeenCalled();

    const cancelBtn = screen.getByRole('button', { name: 'Cancel' });
    fireEvent.click(cancelBtn);
    expect(handleClose).toHaveBeenCalled();
  });

  it('renders reactivation confirmation message for inactive user', () => {
    render(
      <AdminUserStatusModal
        user={inactiveUser}
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        isSubmitting={false}
      />
    );

    expect(screen.getByText(/activate user account/i)).toBeInTheDocument();
    expect(
      screen.getByText(
        /Are you sure you want to reactivate Bob Inactive\? The user will be permitted to sign in again\./i
      )
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Activate user' })).toBeInTheDocument();
  });
});
