import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { OrganizationDashboardResponse } from '../../types/dashboard';
import { OrganizationDashboard } from './OrganizationDashboard';

const mockData: OrganizationDashboardResponse = {
  approval_status: 'pending',
  approval_note: null,
  posting_counts: {
    draft: 1,
    pending_review: 2,
    open: 3,
    closed: 0,
  },
  applications_awaiting_decision: 4,
  recent_applications: [
    {
      application_id: '701',
      posting_id: '801',
      posting_title: 'Software Engineer Intern',
      applicant_name: 'Bob Candidate',
      status: 'submitted',
      applied_at: '2026-10-20T16:00:00Z',
    },
  ],
};

describe('OrganizationDashboard', () => {
  it('renders pending approval banner, posting counts, and applications', () => {
    render(
      <MemoryRouter>
        <OrganizationDashboard data={mockData} />
      </MemoryRouter>
    );

    expect(screen.getByText('Approval pending')).toBeInTheDocument();
    expect(screen.getByText('Software Engineer Intern • Applied 20 Oct 2026')).toBeInTheDocument();
    expect(screen.getByText('Bob Candidate')).toBeInTheDocument();
    expect(screen.getByText('Action needed')).toBeInTheDocument();
  });

  it('renders rejection notice when approval status is rejected', () => {
    render(
      <MemoryRouter>
        <OrganizationDashboard
          data={{
            ...mockData,
            approval_status: 'rejected',
            approval_note: 'Incomplete business registration documents.',
          }}
        />
      </MemoryRouter>
    );

    expect(screen.getByText('Organization application rejected')).toBeInTheDocument();
    expect(screen.getByText('Incomplete business registration documents.')).toBeInTheDocument();
  });

  it('hides notice when organization is approved', () => {
    render(
      <MemoryRouter>
        <OrganizationDashboard data={{ ...mockData, approval_status: 'approved' }} />
      </MemoryRouter>
    );

    expect(screen.queryByText('Approval pending')).not.toBeInTheDocument();
    expect(screen.queryByText('Organization application rejected')).not.toBeInTheDocument();
  });

  it('renders empty state when there are no applications', () => {
    render(
      <MemoryRouter>
        <OrganizationDashboard data={{ ...mockData, recent_applications: [] }} />
      </MemoryRouter>
    );

    expect(screen.getByText('No applications received')).toBeInTheDocument();
  });
});
