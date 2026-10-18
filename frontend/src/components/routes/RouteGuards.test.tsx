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
  it('renders "You don\'t have access to this page" with way back when unauthorized', () => {
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

    expect(screen.getByText("You don't have access to this page.")).toBeInTheDocument();
    expect(screen.queryByText('Admin Exclusive Panel')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Return to account' })).toBeInTheDocument();
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
