import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AdminInternshipReviewModal } from './AdminInternshipReviewModal';
import { Internship } from '../../types/internship';

const pendingPosting: Internship = {
  id: 1,
  organization_id: 10,
  organization_name: 'Tech Innovators',
  title: 'Frontend Engineer Intern',
  description: 'Work on React apps.',
  requirements: 'TypeScript, Tailwind',
  location: 'Remote, US',
  work_mode: 'remote',
  duration_weeks: 10,
  application_deadline: '2026-12-01T00:00:00Z',
  status: 'pending_review',
  applicant_count: 0,
  created_at: '2026-10-15T12:00:00Z',
  updated_at: '2026-10-15T12:00:00Z',
};

describe('AdminInternshipReviewModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('approves a pending posting without requiring a note', async () => {
    const onReview = vi.fn().mockResolvedValue(undefined);
    render(
      <AdminInternshipReviewModal
        internship={pendingPosting}
        isOpen={true}
        onClose={vi.fn()}
        onReview={onReview}
        isSubmitting={false}
      />
    );

    expect(screen.getByText('Frontend Engineer Intern')).toBeInTheDocument();
    const approveBtn = screen.getByRole('button', { name: /approve/i });
    fireEvent.click(approveBtn);

    expect(onReview).toHaveBeenCalledWith('approved', undefined);
  });

  it('requires a review note when rejecting a pending posting', async () => {
    const onReview = vi.fn().mockResolvedValue(undefined);
    render(
      <AdminInternshipReviewModal
        internship={pendingPosting}
        isOpen={true}
        onClose={vi.fn()}
        onReview={onReview}
        isSubmitting={false}
      />
    );

    const rejectBtn = screen.getByRole('button', { name: /reject/i });
    fireEvent.click(rejectBtn);

    expect(
      await screen.findByText(/review note is required when rejecting a posting/i)
    ).toBeInTheDocument();
    expect(onReview).not.toHaveBeenCalled();

    const noteInput = screen.getByLabelText(/review note/i);
    fireEvent.change(noteInput, { target: { value: 'Incomplete requirements section.' } });
    fireEvent.click(rejectBtn);

    expect(onReview).toHaveBeenCalledWith('rejected', 'Incomplete requirements section.');
  });

  it('requires a takedown note and user confirmation for open postings', async () => {
    const openPosting: Internship = {
      ...pendingPosting,
      status: 'open',
    };
    const onReview = vi.fn().mockResolvedValue(undefined);
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);

    render(
      <AdminInternshipReviewModal
        internship={openPosting}
        isOpen={true}
        onClose={vi.fn()}
        onReview={onReview}
        isSubmitting={false}
      />
    );

    const takedownBtn = screen.getByRole('button', { name: /take down/i });
    fireEvent.click(takedownBtn);

    expect(
      await screen.findByText(/review note is required to take down an open posting/i)
    ).toBeInTheDocument();
    expect(onReview).not.toHaveBeenCalled();

    const noteInput = screen.getByLabelText(/takedown reason/i);
    fireEvent.change(noteInput, { target: { value: 'Company violated platform terms.' } });
    fireEvent.click(takedownBtn);

    expect(confirmSpy).toHaveBeenCalled();
    expect(onReview).toHaveBeenCalledWith('rejected', 'Company violated platform terms.');
  });

  it('renders existing review note for rejected postings', () => {
    const rejectedPosting: Internship = {
      ...pendingPosting,
      status: 'rejected',
      review_note: 'Prior feedback from administrator.',
    };

    render(
      <AdminInternshipReviewModal
        internship={rejectedPosting}
        isOpen={true}
        onClose={vi.fn()}
        onReview={vi.fn()}
        isSubmitting={false}
      />
    );

    expect(screen.getByText('Prior feedback from administrator.')).toBeInTheDocument();
  });
});
