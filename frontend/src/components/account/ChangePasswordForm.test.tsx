import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as authApi from '../../api/auth';
import { ChangePasswordForm } from './ChangePasswordForm';

vi.mock('../../api/auth', async (importOriginal) => {
  const actual = await importOriginal<typeof authApi>();
  return {
    ...actual,
    changePassword: vi.fn(),
  };
});

describe('ChangePasswordForm Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all password inputs and submit button', () => {
    render(<ChangePasswordForm />);

    expect(screen.getByLabelText(/current password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^new password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm new password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /update password/i })).toBeInTheDocument();
  });

  it('validates client-side rules before calling API', async () => {
    render(<ChangePasswordForm />);

    const submitBtn = screen.getByRole('button', { name: /update password/i });

    // Submit empty
    fireEvent.click(submitBtn);
    expect(await screen.findByText(/current password is required/i)).toBeInTheDocument();
    expect(authApi.changePassword).not.toHaveBeenCalled();

    // Short password
    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'OldPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/^new password/i), {
      target: { value: 'short' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'short' },
    });
    fireEvent.click(submitBtn);

    expect(
      await screen.findByText(/new password must be between 8 and 128 characters/i)
    ).toBeInTheDocument();
    expect(authApi.changePassword).not.toHaveBeenCalled();

    // Passwords do not match
    fireEvent.change(screen.getByLabelText(/^new password/i), {
      target: { value: 'NewSecretPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'DifferentPass123!' },
    });
    fireEvent.click(submitBtn);

    expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();

    // Same as current password
    fireEvent.change(screen.getByLabelText(/^new password/i), {
      target: { value: 'OldPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'OldPassword123!' },
    });
    fireEvent.click(submitBtn);

    expect(
      await screen.findByText(/new password must be different from current password/i)
    ).toBeInTheDocument();
  });

  it('submits valid payload and displays success message', async () => {
    vi.mocked(authApi.changePassword).mockResolvedValueOnce();

    render(<ChangePasswordForm />);

    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'OldPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/^new password/i), {
      target: { value: 'NewSecretPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'NewSecretPassword123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: /update password/i }));

    await waitFor(() => {
      expect(authApi.changePassword).toHaveBeenCalledWith({
        current_password: 'OldPassword123!',
        new_password: 'NewSecretPassword123!',
      });
    });

    expect(await screen.findByText(/password changed successfully/i)).toBeInTheDocument();
  });

  it('displays API error when changePassword fails', async () => {
    vi.mocked(authApi.changePassword).mockRejectedValueOnce(new Error('Invalid email or password'));

    render(<ChangePasswordForm />);

    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'WrongPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/^new password/i), {
      target: { value: 'NewSecretPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'NewSecretPassword123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: /update password/i }));

    expect(await screen.findByText(/invalid email or password/i)).toBeInTheDocument();
  });

  it('displays rate limit cooldown notice and disables submit button on 429 error', async () => {
    vi.mocked(authApi.changePassword).mockRejectedValueOnce(
      new authApi.AuthApiError('Rate limited', 429, 'RATE_LIMITED', 900)
    );

    render(<ChangePasswordForm />);

    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'OldPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/^new password/i), {
      target: { value: 'NewSecretPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'NewSecretPassword123!' },
    });

    const submitBtn = screen.getByRole('button', { name: /update password/i });
    fireEvent.click(submitBtn);

    expect(
      await screen.findByText(/too many attempts\. try again in 15 minutes\./i)
    ).toBeInTheDocument();
    expect(submitBtn).toBeDisabled();
  });
});
