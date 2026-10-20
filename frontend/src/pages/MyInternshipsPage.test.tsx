import { render, screen } from '@testing-library/react';
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
  updateInternship: vi.fn(),
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

describe('MyInternshipsPage Organization Approval Notice and Publish Controls', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders approval notice and disables publish button when organization is pending', async () => {
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

    const publishBtn = await screen.findByRole('button', { name: /publish/i });
    expect(publishBtn).toBeDisabled();
    expect(publishBtn).toHaveAttribute(
      'title',
      'Your organization is awaiting approval. You can prepare drafts, but you cannot publish until an admin approves you.'
    );
  });

  it('enables publish button when organization is approved', async () => {
    const approvedProfile: OrganizationProfile = {
      ...pendingProfile,
      approval_status: 'approved',
    };
    vi.mocked(internshipApi.getOrganizationInternships).mockResolvedValue([mockDraftPosting]);
    vi.mocked(profileApi.getOrganizationProfile).mockResolvedValue(approvedProfile);

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockOrgUser}>
          <MyInternshipsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    const publishBtn = await screen.findByRole('button', { name: /publish/i });
    expect(publishBtn).not.toBeDisabled();
    expect(screen.queryByText(/Your organization is awaiting approval/i)).not.toBeInTheDocument();
  });
});
