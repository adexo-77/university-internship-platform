import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { Submission } from '../../types/assignment';
import { GradeForm } from './GradeForm';

const mockSubmission: Submission = {
  id: 10,
  assignment_id: 1,
  student_id: 20,
  content: 'Algorithm implementation in Python',
  link_url: 'https://github.com/student/algo',
  is_late: false,
  submitted_at: '2026-10-18T10:00:00Z',
  updated_at: '2026-10-18T10:00:00Z',
  grade: null,
  feedback: null,
  graded_at: null,
  graded_by: null,
};

describe('GradeForm Component', () => {
  it('displays student submission content and artifact link', () => {
    render(<GradeForm submission={mockSubmission} maxPoints={100} onSubmit={vi.fn()} />);

    expect(screen.getByText('Algorithm implementation in Python')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'https://github.com/student/algo' })).toHaveAttribute(
      'href',
      'https://github.com/student/algo'
    );
  });

  it('validates required grade and score bounds', async () => {
    const handleSubmit = vi.fn();
    render(<GradeForm submission={mockSubmission} maxPoints={100} onSubmit={handleSubmit} />);

    // Empty grade
    fireEvent.click(screen.getByRole('button', { name: 'Save grade' }));
    expect(screen.getByText('Grade is required.')).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();

    // Grade > maxPoints (105 > 100)
    fireEvent.change(screen.getByLabelText(/grade/i), { target: { value: '105' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save grade' }));
    expect(screen.getByText('Grade must be a number between 0 and 100.')).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();

    // Negative grade (-5)
    fireEvent.change(screen.getByLabelText(/grade/i), { target: { value: '-5' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save grade' }));
    expect(screen.getByText('Grade must be a number between 0 and 100.')).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it('submits valid score and feedback successfully', async () => {
    const handleSubmit = vi.fn().mockResolvedValue(undefined);
    render(<GradeForm submission={mockSubmission} maxPoints={100} onSubmit={handleSubmit} />);

    fireEvent.change(screen.getByLabelText(/grade/i), { target: { value: '88' } });
    fireEvent.change(screen.getByLabelText(/feedback/i), {
      target: { value: 'Clean solution and well-documented edge cases.' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Save grade' }));

    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith({
        grade: 88,
        feedback: 'Clean solution and well-documented edge cases.',
      });
    });
  });
});
