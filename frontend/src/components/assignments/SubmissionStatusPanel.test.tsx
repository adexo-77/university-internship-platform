import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Submission } from '../../types/assignment';
import { SubmissionStatusPanel } from './SubmissionStatusPanel';

describe('SubmissionStatusPanel Component', () => {
  it('renders "Not submitted" badge when submission is absent', () => {
    render(<SubmissionStatusPanel submission={null} maxPoints={100} />);

    expect(screen.getByTestId('submission-status-panel')).toBeInTheDocument();
    expect(screen.getByText('Not submitted')).toBeInTheDocument();
    expect(screen.queryByText('Late')).not.toBeInTheDocument();
    expect(screen.queryByText('Graded')).not.toBeInTheDocument();
  });

  it('renders "Submitted on <date time>" without late badge when on-time', () => {
    const submission: Submission = {
      id: 1,
      assignment_id: 10,
      student_id: 20,
      content: 'Here is my work.',
      link_url: null,
      submitted_at: '2026-10-18T20:10:00Z',
      is_late: false,
      grade: null,
      feedback: null,
      graded_at: null,
      grader_id: null,
    };

    render(<SubmissionStatusPanel submission={submission} maxPoints={100} />);

    expect(screen.getByText(/Submitted on 18 Oct 2026/)).toBeInTheDocument();
    expect(screen.queryByText('Late')).not.toBeInTheDocument();
    expect(screen.queryByText('Graded')).not.toBeInTheDocument();
  });

  it('renders "Submitted on <date time>" with Late badge when submission is late', () => {
    const submission: Submission = {
      id: 2,
      assignment_id: 10,
      student_id: 20,
      content: 'Late work submission.',
      link_url: null,
      submitted_at: '2026-10-18T20:10:00Z',
      is_late: true,
      grade: null,
      feedback: null,
      graded_at: null,
      grader_id: null,
    };

    render(<SubmissionStatusPanel submission={submission} maxPoints={100} />);

    expect(screen.getByText(/Submitted on 18 Oct 2026/)).toBeInTheDocument();
    expect(screen.getByText('Late')).toBeInTheDocument();
    expect(screen.queryByText('Graded')).not.toBeInTheDocument();
  });

  it('renders "Graded" badge with points score when graded', () => {
    const submission: Submission = {
      id: 3,
      assignment_id: 10,
      student_id: 20,
      content: 'Graded work.',
      link_url: null,
      submitted_at: '2026-10-18T20:10:00Z',
      is_late: false,
      grade: 92,
      feedback: 'Great job!',
      graded_at: '2026-10-19T10:00:00Z',
      grader_id: 5,
    };

    render(<SubmissionStatusPanel submission={submission} maxPoints={100} />);

    expect(screen.getByText('Graded')).toBeInTheDocument();
    expect(screen.getByText('92 / 100')).toBeInTheDocument();
    expect(screen.queryByText('Late')).not.toBeInTheDocument();
  });

  it('renders "Graded" badge with score and Late badge when graded work was submitted late', () => {
    const submission: Submission = {
      id: 4,
      assignment_id: 10,
      student_id: 20,
      content: 'Graded late work.',
      link_url: null,
      submitted_at: '2026-10-18T20:10:00Z',
      is_late: true,
      grade: 78,
      feedback: 'Good work despite slight delay.',
      graded_at: '2026-10-19T10:00:00Z',
      grader_id: 5,
    };

    render(<SubmissionStatusPanel submission={submission} maxPoints={100} />);

    expect(screen.getByText('Graded')).toBeInTheDocument();
    expect(screen.getByText('78 / 100')).toBeInTheDocument();
    expect(screen.getByText('Late')).toBeInTheDocument();
  });
});
