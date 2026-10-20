import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { AdminOrganizationItem } from '../../types/admin';
import { AdminOrganizationsTable } from './AdminOrganizationsTable';

const mockOrganizations: AdminOrganizationItem[] = [
  {
    user_id: 101,
    organization_name: 'Acme Technologies',
    contact_name: 'John Recruiter',
    email: 'hr@acme.com',
    industry: 'Technology',
    location: 'Nairobi',
    approval_status: 'pending',
    approval_note: null,
    reviewed_at: null,
    reviewed_by: null,
  },
  {
    user_id: 102,
    organization_name: 'Global Finance Corp',
    contact_name: 'Sarah Banker',
    email: 'careers@globalfin.com',
    industry: 'Banking',
    location: 'Mombasa',
    approval_status: 'approved',
    approval_note: 'Verified license',
    reviewed_at: '2026-10-18T10:00:00Z',
    reviewed_by: 1,
  },
];

describe('AdminOrganizationsTable Component', () => {
  it('renders organization names, contacts, emails, and approval badges', () => {
    render(
      <AdminOrganizationsTable
        organizations={mockOrganizations}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />
    );

    expect(screen.getByText('Acme Technologies')).toBeInTheDocument();
    expect(screen.getByText('John Recruiter')).toBeInTheDocument();
    expect(screen.getByText('hr@acme.com')).toBeInTheDocument();
    expect(screen.getByText('pending')).toBeInTheDocument();

    expect(screen.getByText('Global Finance Corp')).toBeInTheDocument();
    expect(screen.getByText('Sarah Banker')).toBeInTheDocument();
    expect(screen.getByText('careers@globalfin.com')).toBeInTheDocument();
    expect(screen.getByText('approved')).toBeInTheDocument();
  });

  it('triggers onApprove and onReject when action buttons are clicked', () => {
    const handleApprove = vi.fn();
    const handleReject = vi.fn();

    render(
      <AdminOrganizationsTable
        organizations={mockOrganizations}
        onApprove={handleApprove}
        onReject={handleReject}
      />
    );

    const approveButtons = screen.getAllByRole('button', { name: 'Approve' });
    fireEvent.click(approveButtons[0]);
    expect(handleApprove).toHaveBeenCalledWith(mockOrganizations[0]);

    const rejectButtons = screen.getAllByRole('button', { name: 'Reject' });
    fireEvent.click(rejectButtons[0]);
    expect(handleReject).toHaveBeenCalledWith(mockOrganizations[0]);
  });
});
