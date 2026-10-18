import { act, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useAuth } from '../hooks/useAuth';
import { User } from '../types/auth';
import { AuthProvider } from './AuthContext';

const mockUser: User = {
  id: 1,
  email: 'test@example.com',
  full_name: 'Test Student',
  role: 'student',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

const TestConsumer: React.FC = () => {
  const { user, isAuthenticated, login, logout, register } = useAuth();

  return (
    <div>
      <div data-testid="auth-status">{isAuthenticated ? 'authenticated' : 'unauthenticated'}</div>
      <div data-testid="user-name">{user?.full_name ?? 'none'}</div>
      <button
        onClick={() => void login({ email: 'test@example.com', password: 'Password123!' })}
        data-testid="login-btn"
      >
        Login
      </button>
      <button
        onClick={() =>
          void register({
            email: 'new@example.com',
            password: 'Password123!',
            full_name: 'New User',
            role: 'student',
          })
        }
        data-testid="register-btn"
      >
        Register
      </button>
      <button onClick={() => void logout()} data-testid="logout-btn">
        Logout
      </button>
    </div>
  );
};

describe('AuthProvider & useAuth', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('checks session on mount and sets user on success', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/auth/me')) {
        return Promise.resolve(
          new Response(JSON.stringify(mockUser), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          })
        );
      }
      return Promise.reject(new Error('Unknown url'));
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    // Initial loading indicator
    expect(screen.getByText('Checking platform session')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
    });
    expect(screen.getByTestId('user-name')).toHaveTextContent('Test Student');
  });

  it('sets user to null when /api/auth/me returns 401', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/auth/me')) {
        return Promise.resolve(
          new Response(JSON.stringify({ detail: 'Authentication required' }), {
            status: 401,
            headers: { 'Content-Type': 'application/json' },
          })
        );
      }
      return Promise.reject(new Error('Unknown url'));
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('unauthenticated');
    });
    expect(screen.getByTestId('user-name')).toHaveTextContent('none');
  });

  it('updates state on login, register, and logout', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(
      (input: RequestInfo | URL, init?: RequestInit) => {
        const url = typeof input === 'string' ? input : input.toString();

        if (url.includes('/api/auth/me')) {
          return Promise.resolve(
            new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 })
          );
        }

        if (url.includes('/api/auth/login')) {
          return Promise.resolve(
            new Response(JSON.stringify(mockUser), {
              status: 200,
              headers: { 'Content-Type': 'application/json' },
            })
          );
        }

        if (url.includes('/api/auth/register')) {
          const newUser = { ...mockUser, full_name: 'New User', email: 'new@example.com' };
          return Promise.resolve(
            new Response(JSON.stringify(newUser), {
              status: 201,
              headers: { 'Content-Type': 'application/json' },
            })
          );
        }

        if (url.includes('/api/auth/logout') && init?.method === 'POST') {
          return Promise.resolve(new Response(JSON.stringify({ message: 'ok' }), { status: 200 }));
        }

        return Promise.reject(new Error('Unknown'));
      }
    );

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('unauthenticated');
    });

    // Test Login
    await act(async () => {
      screen.getByTestId('login-btn').click();
    });
    expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
    expect(screen.getByTestId('user-name')).toHaveTextContent('Test Student');

    // Test Logout
    await act(async () => {
      screen.getByTestId('logout-btn').click();
    });
    expect(screen.getByTestId('auth-status')).toHaveTextContent('unauthenticated');
    expect(screen.getByTestId('user-name')).toHaveTextContent('none');

    // Test Register
    await act(async () => {
      screen.getByTestId('register-btn').click();
    });
    expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
    expect(screen.getByTestId('user-name')).toHaveTextContent('New User');
  });
});
