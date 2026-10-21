import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { AdminInternshipReviewsTable } from './AdminInternshipReviewsTable';
import { Internship } from '../../types/internship';

const mockInternships: Internship[] = [
  {
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
  },
];

describe('AdminInternshipReviewsTable', () => {
  it('renders table headers and row details', () => {
    const onSelect = vi.fn();
    render(<AdminInternshipReviewsTable internships={mockInternships} onSelect={onSelect} />);

    expect(screen.getByText('Frontend Engineer Intern')).toBeInTheDocument();
    expect(screen.getByText('Tech Innovators')).toBeInTheDocument();
    expect(screen.getByText('Remote, US')).toBeInTheDocument();
    expect(screen.getByText(/pending review/i)).toBeInTheDocument();

    const reviewBtn = screen.getByRole('button', { name: /review/i });
    fireEvent.click(reviewBtn);
    expect(onSelect).toHaveBeenCalledWith(mockInternships[0]);
  });

  it('renders Take down action only on open rows and Review on pending rows', () => {
    const onSelect = vi.fn();
    const rows: Internship[] = [
      { ...mockInternships[0], id: 1, title: 'Open Role', status: 'open' },
      { ...mockInternships[0], id: 2, title: 'Pending Role', status: 'pending_review' },
      { ...mockInternships[0], id: 3, title: 'Rejected Role', status: 'rejected' },
      { ...mockInternships[0], id: 4, title: 'Closed Role', status: 'closed' },
    ];
    render(<AdminInternshipReviewsTable internships={rows} onSelect={onSelect} />);

    const takedownButtons = screen.getAllByRole('button', { name: /take down/i });
    expect(takedownButtons).toHaveLength(1);
    fireEvent.click(takedownButtons[0]);
    expect(onSelect).toHaveBeenCalledWith(rows[0]);

    const reviewButtons = screen.getAllByRole('button', { name: /review/i });
    expect(reviewButtons).toHaveLength(1);

    const allButtons = screen.getAllByRole('button');
    expect(allButtons).toHaveLength(2);
  });

  it('renders custom empty message when no postings match', () => {
    render(
      <AdminInternshipReviewsTable
        internships={[]}
        onSelect={vi.fn()}
        emptyMessage="No reviews in queue."
      />
    );

    expect(screen.getByText('No reviews in queue.')).toBeInTheDocument();
  });
});
