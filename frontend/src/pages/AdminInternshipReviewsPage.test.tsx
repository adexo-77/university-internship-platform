import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
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

  it('offers Pending review, Open, Rejected, Closed and All filter options with Pending review as default', async () => {
    vi.mocked(adminInternshipApi.listAdminInternships).mockResolvedValue(mockResponse);

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockAdminUser}>
          <AdminInternshipReviewsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    const select = (await screen.findByLabelText(/status filter/i)) as HTMLSelectElement;
    expect(select.value).toBe('pending_review');

    const options = Array.from(select.options).map((o) => o.text);
    expect(options).toEqual(['Pending review', 'Open', 'Rejected', 'Closed', 'All']);
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

  it('updates the row status in-place after takedown action without page reload', async () => {
    const openInternship: Internship = {
      ...mockInternship,
      id: 202,
      title: 'DevOps Engineer Intern',
      status: 'open',
    };
    vi.mocked(adminInternshipApi.listAdminInternships).mockResolvedValue({
      items: [openInternship],
      total: 1,
      limit: 20,
      offset: 0,
    });
    vi.mocked(adminInternshipApi.reviewInternship).mockResolvedValue({
      ...openInternship,
      status: 'rejected',
      review_note: 'Terms violation',
    });
    vi.spyOn(window, 'confirm').mockReturnValue(true);

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockAdminUser}>
          <AdminInternshipReviewsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    const takedownBtn = await screen.findByRole('button', { name: /take down/i });
    expect(screen.getByText('DevOps Engineer Intern')).toBeInTheDocument();
    fireEvent.click(takedownBtn);

    const noteInput = screen.getByLabelText(/takedown reason/i);
    fireEvent.change(noteInput, { target: { value: 'Terms violation' } });

    const dialog = screen.getByRole('dialog');
    const modalTakedownBtn = within(dialog).getByRole('button', { name: /take down/i });
    fireEvent.click(modalTakedownBtn);

    await waitFor(() => {
      expect(adminInternshipApi.reviewInternship).toHaveBeenCalledWith(202, {
        decision: 'rejected',
        review_note: 'Terms violation',
      });
    });

    await waitFor(() => {
      expect(screen.getAllByText('Rejected').length).toBeGreaterThanOrEqual(2);
    });
    expect(screen.queryByRole('button', { name: /take down/i })).not.toBeInTheDocument();
  });
});
