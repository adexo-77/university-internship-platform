import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { AuthProvider } from '../../context/AuthContext';
import { User } from '../../types/auth';
import { ProtectedRoute } from './ProtectedRoute';
import { RoleRoute } from './RoleRoute';

const mockStudentUser: User = {
  id: 1,
  email: 'student@example.com',
  full_name: 'Student User',
  role: 'student',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

const mockAdminUser: User = {
  id: 2,
  email: 'admin@example.com',
  full_name: 'Admin User',
  role: 'admin',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

describe('ProtectedRoute Guard', () => {
  it('redirects unauthenticated user to /login', () => {
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <AuthProvider initialUser={null}>
          <Routes>
            <Route path="/login" element={<div>Login Page Form</div>} />
            <Route element={<ProtectedRoute />}>
              <Route path="/protected" element={<div>Secret Content</div>} />
            </Route>
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByText('Login Page Form')).toBeInTheDocument();
    expect(screen.queryByText('Secret Content')).not.toBeInTheDocument();
  });

  it('allows authenticated user to view protected route', () => {
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <AuthProvider initialUser={mockStudentUser}>
          <Routes>
            <Route path="/login" element={<div>Login Page Form</div>} />
            <Route element={<ProtectedRoute />}>
              <Route path="/protected" element={<div>Secret Content</div>} />
            </Route>
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByText('Secret Content')).toBeInTheDocument();
  });
});

describe('RoleRoute Guard', () => {
  it('shows access-denied with allowed role names when unauthorized', () => {
    render(
      <MemoryRouter initialEntries={['/admin-panel']}>
        <AuthProvider initialUser={mockStudentUser}>
          <Routes>
            <Route element={<RoleRoute allowedRoles={['admin']} />}>
              <Route path="/admin-panel" element={<div>Admin Exclusive Panel</div>} />
            </Route>
            <Route path="/account" element={<div>Account Page</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByText("You don't have access to this page")).toBeInTheDocument();
    expect(screen.getByText('This page is only available to admin accounts.')).toBeInTheDocument();
    expect(screen.queryByText('Admin Exclusive Panel')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Go to your account' })).toBeInTheDocument();
  });

  it('lists multiple role names in the access-denied message', () => {
    render(
      <MemoryRouter initialEntries={['/restricted']}>
        <AuthProvider initialUser={mockStudentUser}>
          <Routes>
            <Route element={<RoleRoute allowedRoles={['admin', 'instructor']} />}>
              <Route path="/restricted" element={<div>Restricted Content</div>} />
            </Route>
            <Route path="/account" element={<div>Account Page</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(
      screen.getByText('This page is only available to admin and instructor accounts.')
    ).toBeInTheDocument();
  });

  it('allows authorized role to access route', () => {
    render(
      <MemoryRouter initialEntries={['/admin-panel']}>
        <AuthProvider initialUser={mockAdminUser}>
          <Routes>
            <Route element={<RoleRoute allowedRoles={['admin']} />}>
              <Route path="/admin-panel" element={<div>Admin Exclusive Panel</div>} />
            </Route>
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByText('Admin Exclusive Panel')).toBeInTheDocument();
  });
});

describe('Root redirect', () => {
  it('redirects unauthenticated user from / to /login', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <AuthProvider initialUser={null}>
          <Routes>
            <Route path="/" element={<RootRedirectTestHelper />} />
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });

  it('redirects authenticated student from / to /dashboard', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <AuthProvider initialUser={mockStudentUser}>
          <Routes>
            <Route path="/" element={<RootRedirectTestHelper />} />
            <Route path="/dashboard" element={<div>Dashboard Destination</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByText('Dashboard Destination')).toBeInTheDocument();
  });
});

/* ---------- helpers ---------- */
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { getHomePath } from '../../config/navigation';

/**
 * Mirrors the RootRedirect logic from App.tsx so we can test it in isolation
 * without importing the full App router.
 */
const RootRedirectTestHelper: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  return <Navigate to={getHomePath(user.role)} replace />;
};
