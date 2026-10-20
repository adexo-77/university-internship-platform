import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as adminInternshipApi from '../api/admin_internship';
import { AuthProvider } from '../context/AuthContext';
import { AdminInternshipReviewsPage } from './AdminInternshipReviewsPage';
import { User } from '../types/auth';
import { Internship, InternshipListResponse } from '../types/internship';

vi.mock('../api/admin_internship', () => ({
  listAdminInternships: vi.fn(),
  reviewInternship: vi.fn(),
}));

const mockAdminUser: User = {
  id: 1,
  email: 'admin@brolf.edu',
  full_name: 'Platform Admin',
  role: 'admin',
  is_active: true,
  created_at: '2026-10-20T10:00:00Z',
  updated_at: '2026-10-20T10:00:00Z',
};

const mockInternship: Internship = {
  id: 101,
  organization_id: 10,
  organization_name: 'Acme Corp',
  title: 'Backend Engineering Intern',
  description: 'Work on distributed systems.',
  requirements: 'Go, PostgreSQL',
  location: 'Nairobi',
  work_mode: 'remote',
  duration_weeks: 12,
  application_deadline: '2026-11-20T12:00:00Z',
  status: 'pending_review',
  applicant_count: 0,
  created_at: '2026-10-20T10:00:00Z',
  updated_at: '2026-10-20T10:00:00Z',
};

const mockResponse: InternshipListResponse = {
  items: [mockInternship],
  total: 1,
  limit: 20,
  offset: 0,
};

describe('AdminInternshipReviewsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads pending review queue by default and displays table', async () => {
    vi.mocked(adminInternshipApi.listAdminInternships).mockResolvedValue(mockResponse);

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockAdminUser}>
          <AdminInternshipReviewsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(await screen.findByText('Backend Engineering Intern')).toBeInTheDocument();
    expect(adminInternshipApi.listAdminInternships).toHaveBeenCalledWith({
      status: 'pending_review',
    });
  });

  it('filters by status when selection changes', async () => {
    vi.mocked(adminInternshipApi.listAdminInternships).mockResolvedValue(mockResponse);

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockAdminUser}>
          <AdminInternshipReviewsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await screen.findByText('Backend Engineering Intern');

    const select = screen.getByLabelText(/status filter/i);
    fireEvent.change(select, { target: { value: 'open' } });

    await waitFor(() => {
      expect(adminInternshipApi.listAdminInternships).toHaveBeenCalledWith({ status: 'open' });
    });
  });

  it('opens review modal when clicking Review button', async () => {
    vi.mocked(adminInternshipApi.listAdminInternships).mockResolvedValue(mockResponse);

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockAdminUser}>
          <AdminInternshipReviewsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    const reviewBtn = await screen.findByRole('button', { name: /review/i });
    fireEvent.click(reviewBtn);

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /approve/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /reject/i })).toBeInTheDocument();
  });
});
