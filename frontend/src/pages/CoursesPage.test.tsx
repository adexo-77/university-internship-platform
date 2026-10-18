import { act, fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../context/AuthContext';
import { User } from '../types/auth';
import { CoursesPage } from './CoursesPage';

const mockAdminUser: User = {
  id: 1,
  email: 'admin@test.edu',
  full_name: 'Admin User',
  role: 'admin',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

const mockStudentUser: User = {
  id: 2,
  email: 'student@test.edu',
  full_name: 'Jane Student',
  role: 'student',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

describe('CoursesPage Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders courses list and search form', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({
          items: [
            {
              id: 1,
              instructor_id: 10,
              instructor_name: 'Dr. Turing',
              title: 'Theory of Computation',
              description: 'Automata and computability.',
              status: 'published',
              created_at: '2026-10-18T00:00:00Z',
              updated_at: '2026-10-18T00:00:00Z',
              enrolled: false,
            },
          ],
          total: 1,
          limit: 10,
          offset: 0,
        }),
        {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }
      )
    );

    await act(async () => {
      render(
        <MemoryRouter>
          <AuthProvider initialUser={mockStudentUser}>
            <CoursesPage />
          </AuthProvider>
        </MemoryRouter>
      );
    });

    expect(screen.getByText('Theory of Computation')).toBeInTheDocument();
    expect(screen.getByText('Dr. Turing')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/search by course title/i)).toBeInTheDocument();
  });

  it('submits search query and requests filtered courses', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({
          items: [],
          total: 0,
          limit: 10,
          offset: 0,
        }),
        {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }
      )
    );

    await act(async () => {
      render(
        <MemoryRouter>
          <AuthProvider initialUser={mockStudentUser}>
            <CoursesPage />
          </AuthProvider>
        </MemoryRouter>
      );
    });

    const searchInput = screen.getByPlaceholderText(/search by course title/i);
    fireEvent.change(searchInput, { target: { value: 'Quantum' } });

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Search' }));
    });

    expect(fetchSpy).toHaveBeenCalledWith(expect.stringContaining('q=Quantum'), expect.anything());
    expect(screen.getByText('No courses found')).toBeInTheDocument();
  });

  it('shows status badge for admin users', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({
          items: [
            {
              id: 2,
              instructor_id: 10,
              instructor_name: 'Dr. Turing',
              title: 'Draft Course 101',
              status: 'draft',
              created_at: '2026-10-18T00:00:00Z',
              updated_at: '2026-10-18T00:00:00Z',
            },
          ],
          total: 1,
          limit: 10,
          offset: 0,
        }),
        {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }
      )
    );

    await act(async () => {
      render(
        <MemoryRouter>
          <AuthProvider initialUser={mockAdminUser}>
            <CoursesPage />
          </AuthProvider>
        </MemoryRouter>
      );
    });

    expect(screen.getByText('Draft Course 101')).toBeInTheDocument();
    expect(screen.getByText('Draft')).toBeInTheDocument();
  });
});
