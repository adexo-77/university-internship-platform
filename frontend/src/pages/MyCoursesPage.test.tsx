import { act, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../context/AuthContext';
import { User } from '../types/auth';
import { MyCoursesPage } from './MyCoursesPage';

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
  full_name: 'Instructor User',
  role: 'instructor',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

const mockFetch = (coursesData: unknown) =>
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.includes('/api/notifications/unread-count')) {
      return new Response(JSON.stringify({ unread_count: 0 }), { status: 200 });
    }
    return new Response(JSON.stringify(coursesData), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  });

describe('MyCoursesPage Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders student enrolled courses when logged in as student', async () => {
    mockFetch([
      {
        id: 10,
        instructor_id: 2,
        instructor_name: 'Prof. Gauss',
        title: 'Linear Algebra',
        description: 'Matrices and vectors.',
        status: 'published',
        created_at: '2026-10-18T00:00:00Z',
        updated_at: '2026-10-18T00:00:00Z',
        enrolled: true,
      },
    ]);

    await act(async () => {
      render(
        <MemoryRouter>
          <AuthProvider initialUser={mockStudent}>
            <MyCoursesPage />
          </AuthProvider>
        </MemoryRouter>
      );
    });

    expect(screen.getByText('Linear Algebra')).toBeInTheDocument();
    expect(screen.getByText('Prof. Gauss')).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'New course' })).not.toBeInTheDocument();
  });

  it('renders empty state for student when no courses are enrolled', async () => {
    mockFetch([]);

    await act(async () => {
      render(
        <MemoryRouter>
          <AuthProvider initialUser={mockStudent}>
            <MyCoursesPage />
          </AuthProvider>
        </MemoryRouter>
      );
    });

    expect(screen.getByText('No courses enrolled')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Browse courses' })).toBeInTheDocument();
  });

  it('renders instructor own courses with New Course action and enrolled count', async () => {
    mockFetch([
      {
        id: 20,
        instructor_id: 2,
        instructor_name: 'Instructor User',
        title: 'Operating Systems Design',
        status: 'published',
        enrolled_count: 15,
        created_at: '2026-10-18T00:00:00Z',
        updated_at: '2026-10-18T00:00:00Z',
      },
    ]);

    await act(async () => {
      render(
        <MemoryRouter>
          <AuthProvider initialUser={mockInstructor}>
            <MyCoursesPage />
          </AuthProvider>
        </MemoryRouter>
      );
    });

    expect(screen.getByText('Operating Systems Design')).toBeInTheDocument();
    expect(screen.getByText('15')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'New course' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Edit' })).toBeInTheDocument();
  });
});
