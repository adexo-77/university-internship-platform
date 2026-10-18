import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../context/AuthContext';
import { User } from '../types/auth';
import { ProfilePage } from './ProfilePage';

const mockStudentUser: User = {
  id: 10,
  email: 'student@example.edu',
  full_name: 'Jane Student',
  role: 'student',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

const mockOrgUser: User = {
  id: 20,
  email: 'rep@acme.com',
  full_name: 'Acme Representative',
  role: 'organization',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

describe('ProfilePage Routing and Delegation', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders student profile form when user role is student', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/students/me')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: 1,
              user_id: 10,
              university: 'Stanford University',
              department: 'Computer Science',
              year_of_study: 3,
              bio: 'Passionate about systems.',
              skills: ['Python'],
              updated_at: '2026-10-18T00:00:00Z',
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } }
          )
        );
      }
      return Promise.reject(new Error(`Unknown url: ${url}`));
    });

    render(
      <MemoryRouter initialEntries={['/profile']}>
        <AuthProvider initialUser={mockStudentUser}>
          <ProfilePage />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(await screen.findByLabelText('University')).toBeInTheDocument();
    expect(screen.queryByLabelText(/organization name/i)).not.toBeInTheDocument();
  });

  it('renders organization profile form when user role is organization', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/organizations/me')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: 2,
              user_id: 20,
              organization_name: 'Acme Robotics',
              industry: 'Hardware & AI',
              location: 'Boston, MA',
              website: 'https://acme.org',
              description: 'Innovating robotics.',
              updated_at: '2026-10-18T00:00:00Z',
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } }
          )
        );
      }
      return Promise.reject(new Error(`Unknown url: ${url}`));
    });

    render(
      <MemoryRouter initialEntries={['/profile']}>
        <AuthProvider initialUser={mockOrgUser}>
          <ProfilePage />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(await screen.findByLabelText(/organization name/i)).toBeInTheDocument();
    expect(screen.queryByLabelText('University')).not.toBeInTheDocument();
  });
});
