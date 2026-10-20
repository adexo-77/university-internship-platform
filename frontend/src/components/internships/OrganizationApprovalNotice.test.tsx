import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { OrganizationProfile } from '../../types/profile';
import { OrganizationApprovalNotice } from './OrganizationApprovalNotice';

const mockBaseProfile: OrganizationProfile = {
  id: 1,
  user_id: 1,
  organization_name: 'Acme Corp',
  industry: 'Software',
  location: 'Nairobi',
  website: 'https://acme.org',
  description: 'Building software',
  approval_status: 'approved',
  approval_note: null,
  updated_at: '2026-10-20T12:00:00Z',
};

describe('OrganizationApprovalNotice Component', () => {
  it('renders nothing when profile is approved or null', () => {
    const { container: c1 } = render(<OrganizationApprovalNotice profile={null} />);
    expect(c1).toBeEmptyDOMElement();

    const { container: c2 } = render(<OrganizationApprovalNotice profile={mockBaseProfile} />);
    expect(c2).toBeEmptyDOMElement();
  });

  it('renders awaiting approval notice when status is pending', () => {
    const pendingProfile: OrganizationProfile = {
      ...mockBaseProfile,
      approval_status: 'pending',
    };

    render(<OrganizationApprovalNotice profile={pendingProfile} />);

    expect(screen.getByText(/approval pending/i)).toBeInTheDocument();
    expect(
      screen.getByText(
        /Your organization is awaiting approval\. You can prepare drafts, but you cannot publish until an admin approves you\./i
      )
    ).toBeInTheDocument();
  });

  it('renders rejection notice with note when status is rejected', () => {
    const rejectedProfile: OrganizationProfile = {
      ...mockBaseProfile,
      approval_status: 'rejected',
      approval_note: 'Company registration number invalid.',
    };

    render(<OrganizationApprovalNotice profile={rejectedProfile} />);

    expect(screen.getByText(/application rejected/i)).toBeInTheDocument();
    expect(screen.getByText(/Company registration number invalid\./i)).toBeInTheDocument();
  });
});
