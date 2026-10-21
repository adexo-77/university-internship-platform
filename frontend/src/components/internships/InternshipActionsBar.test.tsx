import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { InternshipActionsBar } from './InternshipActionsBar';
import { Internship } from '../../types/internship';

const basePosting: Internship = {
  id: 42,
  organization_id: 10,
  organization_name: 'Acme Corp',
  title: 'Platform Engineer Intern',
  description: 'Design distributed platforms.',
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

describe('InternshipActionsBar', () => {
  it('renders Edit and Submit for review when owner and status is draft or rejected', () => {
    const onSubmit = vi.fn();
    render(
      <MemoryRouter>
        <InternshipActionsBar
          internship={basePosting}
          isOwner={true}
          onSubmitForReview={onSubmit}
          onWithdrawToDraft={vi.fn()}
          onClose={vi.fn()}
        />
      </MemoryRouter>
    );

    const submitBtn = screen.getByRole('button', { name: /submit for review/i });
    expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument();
    fireEvent.click(submitBtn);
    expect(onSubmit).toHaveBeenCalledTimes(1);
  });

  it('renders Withdraw to draft when owner and status is pending_review', () => {
    const onWithdraw = vi.fn();
    render(
      <MemoryRouter>
        <InternshipActionsBar
          internship={{ ...basePosting, status: 'pending_review' }}
          isOwner={true}
          onSubmitForReview={vi.fn()}
          onWithdrawToDraft={onWithdraw}
          onClose={vi.fn()}
        />
      </MemoryRouter>
    );

    const withdrawBtn = screen.getByRole('button', { name: /withdraw to draft/i });
    fireEvent.click(withdrawBtn);
    expect(onWithdraw).toHaveBeenCalledTimes(1);
  });

  it('renders Extend deadline and Close when owner and status is open', () => {
    const onClose = vi.fn();
    render(
      <MemoryRouter>
        <InternshipActionsBar
          internship={{ ...basePosting, status: 'open' }}
          isOwner={true}
          onSubmitForReview={vi.fn()}
          onWithdrawToDraft={vi.fn()}
          onClose={onClose}
        />
      </MemoryRouter>
    );

    expect(screen.getByRole('button', { name: /extend deadline/i })).toBeInTheDocument();
    const closeBtn = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeBtn);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('renders Take down button for admin only when posting is open', () => {
    const onTakeDown = vi.fn();
    const { rerender } = render(
      <MemoryRouter>
        <InternshipActionsBar
          internship={{ ...basePosting, status: 'open' }}
          isOwner={false}
          isAdmin={true}
          onSubmitForReview={vi.fn()}
          onWithdrawToDraft={vi.fn()}
          onClose={vi.fn()}
          onTakeDown={onTakeDown}
        />
      </MemoryRouter>
    );

    const takedownBtn = screen.getByRole('button', { name: /take down/i });
    expect(takedownBtn).toBeInTheDocument();
    fireEvent.click(takedownBtn);
    expect(onTakeDown).toHaveBeenCalledTimes(1);

    // Non-admin does not see Take down button
    rerender(
      <MemoryRouter>
        <InternshipActionsBar
          internship={{ ...basePosting, status: 'open' }}
          isOwner={false}
          isAdmin={false}
          onSubmitForReview={vi.fn()}
          onWithdrawToDraft={vi.fn()}
          onClose={vi.fn()}
          onTakeDown={onTakeDown}
        />
      </MemoryRouter>
    );
    expect(screen.queryByRole('button', { name: /take down/i })).not.toBeInTheDocument();
  });

  it('does not render Take down button when admin views non-open posting', () => {
    render(
      <MemoryRouter>
        <InternshipActionsBar
          internship={{ ...basePosting, status: 'pending_review' }}
          isOwner={false}
          isAdmin={true}
          onSubmitForReview={vi.fn()}
          onWithdrawToDraft={vi.fn()}
          onClose={vi.fn()}
        />
      </MemoryRouter>
    );

    expect(screen.queryByRole('button', { name: /take down/i })).not.toBeInTheDocument();
  });
});
