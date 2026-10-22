import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../context/AuthContext';
import { RegisterPage } from './RegisterPage';

describe('RegisterPage Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('validates client fields including short password length', async () => {
    render(
      <MemoryRouter initialEntries={['/register']}>
        <AuthProvider initialUser={null}>
          <RegisterPage />
        </AuthProvider>
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText('Full name'), { target: { value: 'Jane Doe' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'jane@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'short' } });

    fireEvent.click(screen.getByRole('button', { name: 'Create account' }));

    expect(
      await screen.findByText('Password must be at least 8 characters long.')
    ).toBeInTheDocument();
  });

  it('shows required organization name field when Organization role is chosen and validates it', async () => {
    render(
      <MemoryRouter initialEntries={['/register']}>
        <AuthProvider initialUser={null}>
          <RegisterPage />
        </AuthProvider>
      </MemoryRouter>
    );

    // Initially role is student, organization name field is not present
    expect(screen.queryByLabelText('Organization name')).not.toBeInTheDocument();
    expect(screen.getByLabelText('Student')).toBeChecked();
    expect(screen.getByLabelText('Organization')).not.toBeChecked();

    // Select Organization role
    fireEvent.click(screen.getByLabelText('Organization'));
    expect(screen.getByLabelText('Organization')).toBeChecked();
    expect(screen.getByLabelText('Student')).not.toBeChecked();

    // Organization name field is now displayed
    expect(screen.getByLabelText('Organization name')).toBeInTheDocument();

    // Attempt submission without organization name
    fireEvent.change(screen.getByLabelText('Full name'), { target: { value: 'Jane Doe' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'jane@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'Password123!' } });

    fireEvent.click(screen.getByRole('button', { name: 'Create account' }));

    expect(await screen.findByText('Organization name is required.')).toBeInTheDocument();
  });

  it('submits valid organization registration with organization name and redirects to /account', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/auth/register')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: 1,
              email: 'jane@example.com',
              full_name: 'Jane Doe',
              role: 'organization',
              is_active: true,
              created_at: '2026-10-18T00:00:00Z',
              updated_at: '2026-10-18T00:00:00Z',
            }),
            {
              status: 201,
              headers: { 'Content-Type': 'application/json' },
            }
          )
        );
      }
      return Promise.reject(new Error('Unknown url'));
    });

    render(
      <MemoryRouter initialEntries={['/register']}>
        <AuthProvider initialUser={null}>
          <Routes>
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/account" element={<div>Account Destination</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText('Full name'), { target: { value: 'Jane Doe' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'jane@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'Password123!' } });
    fireEvent.click(screen.getByLabelText('Organization'));

    fireEvent.change(screen.getByLabelText('Organization name'), {
      target: { value: 'Acme Corp' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create account' }));

    await waitFor(() => {
      expect(screen.getByText('Account Destination')).toBeInTheDocument();
    });
  });

  it('displays plain error when email is already registered', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/auth/register')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              detail: 'An account with this email already exists',
              code: 'EMAIL_ALREADY_REGISTERED',
            }),
            {
              status: 409,
              headers: { 'Content-Type': 'application/json' },
            }
          )
        );
      }
      return Promise.reject(new Error('Unknown url'));
    });

    render(
      <MemoryRouter initialEntries={['/register']}>
        <AuthProvider initialUser={null}>
          <RegisterPage />
        </AuthProvider>
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText('Full name'), { target: { value: 'Jane Doe' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'exists@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'Password123!' } });

    fireEvent.click(screen.getByRole('button', { name: 'Create account' }));

    await waitFor(() => {
      expect(screen.getByText('An account with this email already exists')).toBeInTheDocument();
    });
  });

  it('displays rate limit cooldown notice and disables submit button on 429 response', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/auth/register')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              detail: 'Rate limit exceeded. Try again in 60 minutes.',
              code: 'RATE_LIMITED',
            }),
            {
              status: 429,
              headers: {
                'Content-Type': 'application/json',
                'Retry-After': '3600',
              },
            }
          )
        );
      }
      return Promise.reject(new Error('Unknown url'));
    });

    render(
      <MemoryRouter initialEntries={['/register']}>
        <AuthProvider initialUser={null}>
          <RegisterPage />
        </AuthProvider>
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText('Full name'), { target: { value: 'Jane Doe' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'jane@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'Password123!' } });

    const submitBtn = screen.getByRole('button', { name: 'Create account' });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(
        screen.getByText(/too many attempts\. try again in 60 minutes\./i)
      ).toBeInTheDocument();
    });
    expect(screen.getByRole('button', { name: 'Create account' })).toBeDisabled();
  });
});
