import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../context/AuthContext';
import { User } from '../types/auth';
import { DashboardPage } from './DashboardPage';

const mockStudent: User = {
  id: 1,
  email: 'student@test.edu',
  full_name: 'Student User',
  role: 'student',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

const mockInstructor: User = {
  id: 2,
  email: 'instructor@test.edu',
  full_name: 'Dr. Instructor',
  role: 'instructor',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

const mockCoordinator: User = {
  id: 3,
  email: 'coord@test.edu',
  full_name: 'Coordinator User',
  role: 'coordinator',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

const mockDashboardFetch = (dashboardData: unknown, failFirst = false) => {
  let failed = false;
  return vi.spyOn(globalThis, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.includes('/api/notifications/unread-count')) {
      return new Response(JSON.stringify({ unread_count: 0 }), { status: 200 });
    }
    if (failFirst && !failed) {
      failed = true;
      throw new Error('Network disconnected');
    }
    return new Response(JSON.stringify(dashboardData), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  });
};

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders student dashboard on success', async () => {
    mockDashboardFetch({
      due_next: [],
      recent_grades: [],
      courses: [],
      applications: { counts_by_status: {}, recent: [] },
      profile_complete: true,
    });

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockStudent}>
          <DashboardPage />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Dashboard' })).toBeInTheDocument();
      expect(screen.getByText('No upcoming assignments')).toBeInTheDocument();
    });
  });

  it('renders instructor dashboard on success', async () => {
    mockDashboardFetch({
      courses: [],
      needs_grading: [],
    });

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockInstructor}>
          <DashboardPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('No courses found')).toBeInTheDocument();
      expect(screen.getByText('All caught up')).toBeInTheDocument();
    });
  });

  it('renders coordinator dashboard on success', async () => {
    mockDashboardFetch({
      organizations_pending_approval: 1,
      internships_pending_review: 2,
      open_internships: 3,
      applications_by_status: { submitted: 4, accepted: 1 },
      reviews_completed: 5,
    });

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockCoordinator}>
          <DashboardPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Review work queues')).toBeInTheDocument();
      expect(screen.getByText('Completed by you')).toBeInTheDocument();
    });
  });

  it('renders error state and retries on button click', async () => {
    const fetchMock = mockDashboardFetch(
      {
        due_next: [],
        recent_grades: [],
        courses: [],
        applications: { counts_by_status: {}, recent: [] },
        profile_complete: true,
      },
      true
    );

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockStudent}>
          <DashboardPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Network disconnected')).toBeInTheDocument();
    });

    const retryBtn = screen.getByRole('button', { name: 'Retry' });
    fireEvent.click(retryBtn);

    await waitFor(() => {
      expect(screen.getByText('No upcoming assignments')).toBeInTheDocument();
    });

    expect(fetchMock).toHaveBeenCalled();
  });
});
