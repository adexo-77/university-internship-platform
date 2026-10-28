import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider } from '../context/AuthContext';
import { User } from '../types/auth';
import { InternshipsPage } from './InternshipsPage';

const mockStudentUser: User = {
  id: 2,
  email: 'student@test.edu',
  full_name: 'Jane Student',
  role: 'student',
  is_active: true,
  created_at: '2026-10-18T00:00:00Z',
  updated_at: '2026-10-18T00:00:00Z',
};

const mockInternships = [
  {
    id: 1,
    organization_id: 10,
    organization_name: 'Acme Corp',
    title: 'Frontend Engineer Intern',
    description: 'React, TypeScript, CSS.',
    requirements: 'Strong CS fundamentals.',
    location: 'Nairobi',
    work_mode: 'remote',
    duration_weeks: 12,
    application_deadline: '2026-11-30T00:00:00Z',
    status: 'open',
    created_at: '2026-10-18T00:00:00Z',
    updated_at: '2026-10-18T00:00:00Z',
    applied: false,
    application_status: null,
  },
  {
    id: 2,
    organization_id: 11,
    organization_name: 'Beta Labs',
    title: 'Systems Engineering Intern',
    description: 'C++ and distributed systems.',
    requirements: 'Operating systems.',
    location: 'Hybrid',
    work_mode: 'hybrid',
    duration_weeks: 16,
    application_deadline: '2026-12-15T00:00:00Z',
    status: 'open',
    created_at: '2026-10-18T00:00:00Z',
    updated_at: '2026-10-18T00:00:00Z',
    applied: true,
    application_status: 'submitted',
  },
];

describe('InternshipsPage Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  const renderComponent = (user: User = mockStudentUser) => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/auth/me')) {
        return new Response(JSON.stringify(user), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/api/internships/suggestions')) {
        return new Response(
          JSON.stringify({
            items: [],
            reason_code: null,
          }),
          {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          }
        );
      }
      return new Response(
        JSON.stringify({
          items: mockInternships,
          total: 2,
          limit: 10,
          offset: 0,
        }),
        {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    });

    return render(
      <MemoryRouter>
        <AuthProvider>
          <InternshipsPage />
        </AuthProvider>
      </MemoryRouter>
    );
  };

  it('renders catalogue table and filter controls', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Frontend Engineer Intern')).toBeInTheDocument();
      expect(screen.getByText('Systems Engineering Intern')).toBeInTheDocument();
      expect(screen.getByText('Acme Corp')).toBeInTheDocument();
      expect(screen.getByText('Beta Labs')).toBeInTheDocument();
    });

    expect(screen.getByLabelText(/search/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/work mode/i)).toBeInTheDocument();
  });

  it('filters catalogue with search query', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Frontend Engineer Intern')).toBeInTheDocument();
    });

    const searchInput = screen.getByLabelText(/search/i);
    fireEvent.change(searchInput, { target: { value: 'Frontend' } });
    fireEvent.click(screen.getByRole('button', { name: 'Search' }));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('q=Frontend'),
        expect.anything()
      );
    });
  });

  it('filters catalogue by work mode', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Frontend Engineer Intern')).toBeInTheDocument();
    });

    const select = screen.getByLabelText(/work mode/i);
    fireEvent.change(select, { target: { value: 'remote' } });

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('work_mode=remote'),
        expect.anything()
      );
    });
  });
});
