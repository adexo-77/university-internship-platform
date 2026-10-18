import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { Submission } from '../../types/assignment';
import { SubmissionForm } from './SubmissionForm';

describe('SubmissionForm Component', () => {
  it('validates empty content and invalid link URL before submitting', async () => {
    const handleSubmit = vi.fn();
    render(<SubmissionForm maxPoints={100} onSubmit={handleSubmit} />);

    fireEvent.click(screen.getByRole('button', { name: 'Submit assignment' }));

    expect(screen.getByText('Submission content cannot be empty.')).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();

    // Invalid URL protocol
    fireEvent.change(screen.getByLabelText(/your work/i), {
      target: { value: 'Valid written response' },
    });
    fireEvent.change(screen.getByLabelText(/optional repository/i), {
      target: { value: 'ftp://files.example.com' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Submit assignment' }));
    expect(screen.getByText('Link must start with http:// or https://.')).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it('submits valid coursework response successfully', async () => {
    const handleSubmit = vi.fn().mockResolvedValue(undefined);
    render(<SubmissionForm maxPoints={100} onSubmit={handleSubmit} />);

    fireEvent.change(screen.getByLabelText(/your work/i), {
      target: { value: 'Here is my complete solution to problem set 1.' },
    });
    fireEvent.change(screen.getByLabelText(/optional repository/i), {
      target: { value: 'https://github.com/student/assignment-1' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Submit assignment' }));

    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith({
        content: 'Here is my complete solution to problem set 1.',
        link_url: 'https://github.com/student/assignment-1',
      });
    });
  });

  it('locks the form and displays grade when submission is graded', () => {
    const gradedSubmission: Submission = {
      id: 5,
      assignment_id: 1,
      student_id: 2,
      content: 'Graded student coursework',
      link_url: 'https://github.com/student/repo',
      is_late: false,
      submitted_at: '2026-10-18T10:00:00Z',
      updated_at: '2026-10-18T10:00:00Z',
      grade: 92,
      feedback: 'Great proofs and clean code structure.',
      graded_at: '2026-10-18T12:00:00Z',
      graded_by: 1,
    };

    render(<SubmissionForm submission={gradedSubmission} maxPoints={100} onSubmit={vi.fn()} />);

    // Locked notice
    expect(
      screen.getByText('This submission has been graded and is locked from further edits.')
    ).toBeInTheDocument();

    // Grade and feedback display
    expect(screen.getByText('92 / 100')).toBeInTheDocument();
    expect(screen.getByText('Great proofs and clean code structure.')).toBeInTheDocument();

    // Inputs disabled and submit button absent
    expect(screen.getByLabelText(/your work/i)).toBeDisabled();
    expect(screen.getByLabelText(/optional repository/i)).toBeDisabled();
    expect(screen.queryByRole('button', { name: /submit/i })).not.toBeInTheDocument();
  });
});
