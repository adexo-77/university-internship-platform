import { render, screen } from '@testing-library/react';
import React from 'react';
import { MemoryRouter, Navigate, Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { getHomePath } from '../../config/navigation';
import { AuthProvider } from '../../context/AuthContext';
import { useAuth } from '../../hooks/useAuth';
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

const mockCoordinatorUser: User = {
  id: 3,
  email: 'coordinator@example.com',
  full_name: 'Coordinator User',
  role: 'coordinator',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

function renderRoute(element: React.ReactNode, initialUser: User | null, initialPath = '/') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <AuthProvider initialUser={initialUser}>{element}</AuthProvider>
    </MemoryRouter>
  );
}

const RootRedirectTestHelper: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }
  return <Navigate to={getHomePath(user.role)} replace />;
};

describe('ProtectedRoute Guard', () => {
  it('redirects unauthenticated user to /login', () => {
    renderRoute(
      <Routes>
        <Route path="/login" element={<div>Login Page Form</div>} />
        <Route element={<ProtectedRoute />}>
          <Route path="/protected" element={<div>Secret Content</div>} />
        </Route>
      </Routes>,
      null,
      '/protected'
    );
    expect(screen.getByText('Login Page Form')).toBeInTheDocument();
    expect(screen.queryByText('Secret Content')).not.toBeInTheDocument();
  });

  it('allows authenticated user to view protected route', () => {
    renderRoute(
      <Routes>
        <Route path="/login" element={<div>Login Page Form</div>} />
        <Route element={<ProtectedRoute />}>
          <Route path="/protected" element={<div>Secret Content</div>} />
        </Route>
      </Routes>,
      mockStudentUser,
      '/protected'
    );
    expect(screen.getByText('Secret Content')).toBeInTheDocument();
  });
});

describe('RoleRoute Guard', () => {
  it('shows access-denied with allowed role names when unauthorized', () => {
    renderRoute(
      <Routes>
        <Route element={<RoleRoute allowedRoles={['admin']} />}>
          <Route path="/admin-panel" element={<div>Admin Exclusive Panel</div>} />
        </Route>
        <Route path="/account" element={<div>Account Page</div>} />
      </Routes>,
      mockStudentUser,
      '/admin-panel'
    );
    expect(screen.getByText("You don't have access to this page")).toBeInTheDocument();
    expect(screen.getByText('This page is only available to admin accounts.')).toBeInTheDocument();
    expect(screen.queryByText('Admin Exclusive Panel')).not.toBeInTheDocument();
  });

  it('lists multiple role names in the access-denied message', () => {
    renderRoute(
      <Routes>
        <Route element={<RoleRoute allowedRoles={['admin', 'instructor']} />}>
          <Route path="/restricted" element={<div>Restricted Content</div>} />
        </Route>
      </Routes>,
      mockStudentUser,
      '/restricted'
    );
    expect(
      screen.getByText('This page is only available to admin and instructor accounts.')
    ).toBeInTheDocument();
  });

  it('allows authorized role to access route', () => {
    renderRoute(
      <Routes>
        <Route element={<RoleRoute allowedRoles={['admin']} />}>
          <Route path="/admin-panel" element={<div>Admin Exclusive Panel</div>} />
        </Route>
      </Routes>,
      mockAdminUser,
      '/admin-panel'
    );
    expect(screen.getByText('Admin Exclusive Panel')).toBeInTheDocument();
  });

  it('allows coordinator role when included in allowedRoles', () => {
    renderRoute(
      <Routes>
        <Route element={<RoleRoute allowedRoles={['admin', 'coordinator']} />}>
          <Route path="/review-queue" element={<div>Review Queue Content</div>} />
        </Route>
      </Routes>,
      mockCoordinatorUser,
      '/review-queue'
    );
    expect(screen.getByText('Review Queue Content')).toBeInTheDocument();
  });

  it('blocks coordinator role when not in allowedRoles', () => {
    renderRoute(
      <Routes>
        <Route element={<RoleRoute allowedRoles={['admin']} />}>
          <Route path="/admin/users" element={<div>Admin Users Content</div>} />
        </Route>
        <Route path="/account" element={<div>Account Page</div>} />
      </Routes>,
      mockCoordinatorUser,
      '/admin/users'
    );
    expect(screen.getByText("You don't have access to this page")).toBeInTheDocument();
    expect(screen.queryByText('Admin Users Content')).not.toBeInTheDocument();
  });
});

describe('Root redirect', () => {
  it('redirects unauthenticated user from / to /login', () => {
    renderRoute(
      <Routes>
        <Route path="/" element={<RootRedirectTestHelper />} />
        <Route path="/login" element={<div>Login Page</div>} />
      </Routes>,
      null,
      '/'
    );
    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });

  it('redirects authenticated student from / to /dashboard', () => {
    renderRoute(
      <Routes>
        <Route path="/" element={<RootRedirectTestHelper />} />
        <Route path="/dashboard" element={<div>Dashboard Destination</div>} />
      </Routes>,
      mockStudentUser,
      '/'
    );
    expect(screen.getByText('Dashboard Destination')).toBeInTheDocument();
  });

  it('redirects authenticated coordinator from / to /dashboard', () => {
    renderRoute(
      <Routes>
        <Route path="/" element={<RootRedirectTestHelper />} />
        <Route path="/dashboard" element={<div>Dashboard Destination</div>} />
      </Routes>,
      mockCoordinatorUser,
      '/'
    );
    expect(screen.getByText('Dashboard Destination')).toBeInTheDocument();
  });
});
