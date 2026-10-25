import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as adminUserApi from '../../api/admin_user';
import { AdminUserForm } from './AdminUserForm';

vi.mock('../../api/admin_user', () => ({
  createAdminUser: vi.fn(),
}));

describe('AdminUserForm Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders radio buttons, fields, and submit button', () => {
    render(<AdminUserForm />);

    expect(screen.getByLabelText(/instructor/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/administrator/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/coordinator/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/initial password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create user/i })).toBeInTheDocument();
  });

  it('validates required fields, invalid email, and short password', async () => {
    render(<AdminUserForm />);

    const submitBtn = screen.getByRole('button', { name: /create user/i });

    // Submit empty form
    fireEvent.click(submitBtn);
    expect(await screen.findByText(/full name is required/i)).toBeInTheDocument();
    expect(adminUserApi.createAdminUser).not.toHaveBeenCalled();

    // Invalid email format
    fireEvent.change(screen.getByLabelText(/full name/i), {
      target: { value: 'Dr. John Watson' },
    });
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'invalid-email' },
    });
    fireEvent.change(screen.getByLabelText(/initial password/i), {
      target: { value: 'short' },
    });
    fireEvent.click(submitBtn);

    expect(await screen.findByText(/please provide a valid email address/i)).toBeInTheDocument();
    expect(
      await screen.findByText(/password must be between 8 and 128 characters/i)
    ).toBeInTheDocument();
    expect(adminUserApi.createAdminUser).not.toHaveBeenCalled();
  });

  it('submits valid form and displays success notice', async () => {
    vi.mocked(adminUserApi.createAdminUser).mockResolvedValueOnce({
      id: 5,
      email: 'john.watson@brolf.edu',
      full_name: 'Dr. John Watson',
      role: 'instructor',
      is_active: true,
      created_at: '2026-10-20T12:00:00Z',
      updated_at: '2026-10-20T12:00:00Z',
    });

    render(<AdminUserForm />);

    fireEvent.change(screen.getByLabelText(/full name/i), {
      target: { value: 'Dr. John Watson' },
    });
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: '  John.Watson@brolf.edu  ' },
    });
    fireEvent.change(screen.getByLabelText(/initial password/i), {
      target: { value: 'SecurePassword123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: /create user/i }));

    await waitFor(() => {
      expect(adminUserApi.createAdminUser).toHaveBeenCalledWith({
        role: 'instructor',
        full_name: 'Dr. John Watson',
        email: 'john.watson@brolf.edu',
        password: 'SecurePassword123!',
      });
    });

    expect(await screen.findByText(/user created/i)).toBeInTheDocument();
    expect(
      await screen.findByText(
        /Account for Dr. John Watson \(john.watson@brolf.edu\) created successfully\./i
      )
    ).toBeInTheDocument();
  });

  it('allows selecting coordinator role and submits successfully', async () => {
    vi.mocked(adminUserApi.createAdminUser).mockResolvedValueOnce({
      id: 6,
      email: 'selamawit.tadesse@example.com',
      full_name: 'Ms. Selamawit Tadesse',
      role: 'coordinator',
      is_active: true,
      created_at: '2026-10-25T12:00:00Z',
      updated_at: '2026-10-25T12:00:00Z',
    });

    render(<AdminUserForm />);

    fireEvent.click(screen.getByLabelText(/coordinator/i));
    fireEvent.change(screen.getByLabelText(/full name/i), {
      target: { value: 'Ms. Selamawit Tadesse' },
    });
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'selamawit.tadesse@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/initial password/i), {
      target: { value: '12345678' },
    });

    fireEvent.click(screen.getByRole('button', { name: /create user/i }));

    await waitFor(() => {
      expect(adminUserApi.createAdminUser).toHaveBeenCalledWith({
        role: 'coordinator',
        full_name: 'Ms. Selamawit Tadesse',
        email: 'selamawit.tadesse@example.com',
        password: '12345678',
      });
    });

    expect(await screen.findByText(/user created/i)).toBeInTheDocument();
  });
});
