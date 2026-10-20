import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as internshipApi from '../api/internship';
import * as profileApi from '../api/profile';
import { AuthProvider } from '../context/AuthContext';
import { MyInternshipsPage } from './MyInternshipsPage';
import { User } from '../types/auth';
import { Internship } from '../types/internship';
import { OrganizationProfile } from '../types/profile';

vi.mock('../api/internship', () => ({
  getOrganizationInternships: vi.fn(),
  submitInternship: vi.fn(),
  withdrawInternship: vi.fn(),
  closeInternship: vi.fn(),
}));

vi.mock('../api/profile', () => ({
  getOrganizationProfile: vi.fn(),
}));

const mockOrgUser: User = {
  id: 10,
  email: 'org@test.com',
  full_name: 'Acme Recruiter',
  role: 'organization',
  is_active: true,
  created_at: '2026-10-20T10:00:00Z',
  updated_at: '2026-10-20T10:00:00Z',
};

const mockDraftPosting: Internship = {
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
  status: 'draft',
  applicant_count: 0,
  created_at: '2026-10-20T10:00:00Z',
  updated_at: '2026-10-20T10:00:00Z',
};

const pendingProfile: OrganizationProfile = {
  id: 1,
  user_id: 10,
  organization_name: 'Acme Corp',
  industry: 'Tech',
  location: 'Nairobi',
  website: 'https://acme.org',
  description: 'Tech firm',
  approval_status: 'pending',
  approval_note: null,
  updated_at: '2026-10-20T10:00:00Z',
};

const approvedProfile: OrganizationProfile = {
  ...pendingProfile,
  approval_status: 'approved',
};

describe('MyInternshipsPage Organization Approval Notice and Review Controls', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders approval notice and disables submit for review button when organization is pending', async () => {
    vi.mocked(internshipApi.getOrganizationInternships).mockResolvedValue([mockDraftPosting]);
    vi.mocked(profileApi.getOrganizationProfile).mockResolvedValue(pendingProfile);

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockOrgUser}>
          <MyInternshipsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(
      await screen.findByText(
        /Your organization is awaiting approval\. You can prepare drafts, but you cannot publish until an admin approves you\./i
      )
    ).toBeInTheDocument();

    const submitBtn = await screen.findByRole('button', { name: /submit for review/i });
    expect(submitBtn).toBeDisabled();
    expect(submitBtn).toHaveAttribute(
      'title',
      'Your organization must be approved before you can submit internships for review.'
    );
  });

  it('enables submit for review button when organization is approved and calls api', async () => {
    vi.mocked(internshipApi.getOrganizationInternships).mockResolvedValue([mockDraftPosting]);
    vi.mocked(profileApi.getOrganizationProfile).mockResolvedValue(approvedProfile);
    vi.mocked(internshipApi.submitInternship).mockResolvedValue({
      ...mockDraftPosting,
      status: 'pending_review',
    });

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockOrgUser}>
          <MyInternshipsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    const submitBtn = await screen.findByRole('button', { name: /submit for review/i });
    expect(submitBtn).not.toBeDisabled();
    expect(screen.queryByText(/Your organization is awaiting approval/i)).not.toBeInTheDocument();

    fireEvent.click(submitBtn);
    expect(internshipApi.submitInternship).toHaveBeenCalledWith(101);
  });

  it('renders withdraw to draft button for pending_review posting and calls withdraw api', async () => {
    const pendingPosting: Internship = {
      ...mockDraftPosting,
      status: 'pending_review',
    };
    vi.mocked(internshipApi.getOrganizationInternships).mockResolvedValue([pendingPosting]);
    vi.mocked(profileApi.getOrganizationProfile).mockResolvedValue(approvedProfile);
    vi.mocked(internshipApi.withdrawInternship).mockResolvedValue({
      ...mockDraftPosting,
      status: 'draft',
    });

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockOrgUser}>
          <MyInternshipsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    const withdrawBtn = await screen.findByRole('button', { name: /withdraw to draft/i });
    fireEvent.click(withdrawBtn);
    expect(internshipApi.withdrawInternship).toHaveBeenCalledWith(101);
  });

  it('renders rejection notice with admin review note and edit link for rejected postings', async () => {
    const rejectedPosting: Internship = {
      ...mockDraftPosting,
      status: 'rejected',
      review_note: 'Please include more details on mentorship structure.',
    };
    vi.mocked(internshipApi.getOrganizationInternships).mockResolvedValue([rejectedPosting]);
    vi.mocked(profileApi.getOrganizationProfile).mockResolvedValue(approvedProfile);

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockOrgUser}>
          <MyInternshipsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(
      await screen.findByText(/Please include more details on mentorship structure\./i)
    ).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /edit posting/i })).toHaveAttribute(
      'href',
      '/internships/101/edit'
    );
  });
});
