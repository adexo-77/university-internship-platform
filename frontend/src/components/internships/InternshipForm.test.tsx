import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { InternshipForm } from './InternshipForm';

describe('InternshipForm Component', () => {
  it('validates required fields on submit', () => {
    const handleSubmit = vi.fn();
    render(<InternshipForm onSubmit={handleSubmit} />);

    fireEvent.click(screen.getByRole('button', { name: 'Create internship' }));

    expect(screen.getByText('Title is required.')).toBeInTheDocument();
    expect(screen.getByText('Location is required.')).toBeInTheDocument();
    expect(screen.getByText('Application deadline is required.')).toBeInTheDocument();
    expect(screen.getByText('Description is required.')).toBeInTheDocument();
    expect(screen.getByText('Requirements are required.')).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it('validates future deadline for new postings', () => {
    const handleSubmit = vi.fn();
    render(<InternshipForm onSubmit={handleSubmit} />);

    fireEvent.change(screen.getByLabelText(/^title/i), {
      target: { value: 'Data Engineer Intern' },
    });
    fireEvent.change(screen.getByLabelText(/location/i), {
      target: { value: 'Nairobi' },
    });
    fireEvent.change(screen.getByLabelText(/description/i), {
      target: { value: 'ETL pipelines and SQL models.' },
    });
    fireEvent.change(screen.getByLabelText(/requirements/i), {
      target: { value: 'Python and Postgres.' },
    });
    // Set a past deadline
    fireEvent.change(screen.getByLabelText(/application deadline/i), {
      target: { value: '2020-01-01T12:00' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create internship' }));
    expect(screen.getByText('Application deadline must be set in the future.')).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it('submits valid data when all inputs are correct', () => {
    const handleSubmit = vi.fn();
    render(<InternshipForm onSubmit={handleSubmit} />);

    fireEvent.change(screen.getByLabelText(/^title/i), {
      target: { value: 'Cloud Architecture Intern' },
    });
    fireEvent.change(screen.getByLabelText(/location/i), {
      target: { value: 'Remote' },
    });
    fireEvent.change(screen.getByLabelText(/work mode/i), {
      target: { value: 'remote' },
    });
    fireEvent.change(screen.getByLabelText(/duration/i), {
      target: { value: '12' },
    });
    fireEvent.change(screen.getByLabelText(/application deadline/i), {
      target: { value: '2028-12-31T23:59' },
    });
    fireEvent.change(screen.getByLabelText(/description/i), {
      target: { value: 'Manage Kubernetes infrastructure.' },
    });
    fireEvent.change(screen.getByLabelText(/requirements/i), {
      target: { value: 'Docker, Linux, Terraform.' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create internship' }));
    expect(handleSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Cloud Architecture Intern',
        location: 'Remote',
        work_mode: 'remote',
        duration_weeks: 12,
        description: 'Manage Kubernetes infrastructure.',
        requirements: 'Docker, Linux, Terraform.',
      })
    );
  });

  it('sets max date input attribute and shows helper text with latest allowed deadline', () => {
    render(<InternshipForm onSubmit={vi.fn()} />);

    const input = screen.getByLabelText(/application deadline/i);
    expect(input).toHaveAttribute('max');
    expect(screen.getByText(/Latest allowed deadline:/i)).toBeInTheDocument();
  });

  it('calculates latest allowed deadline from reviewed_at for open postings', () => {
    const initialData = {
      id: 1,
      title: 'Open Posting',
      status: 'open' as const,
      reviewed_at: '2026-10-14T00:00:00Z',
      application_deadline: '2026-11-01T00:00:00Z',
    };
    render(<InternshipForm initialData={initialData} onSubmit={vi.fn()} isEdit={true} />);

    const input = screen.getByLabelText(/application deadline/i);
    expect(input.getAttribute('max')).toContain('2027-01-12');
    expect(screen.getByText('Latest allowed deadline: 12 Jan 2027')).toBeInTheDocument();
  });

  it('displays the server message when rejected', () => {
    render(
      <InternshipForm
        onSubmit={vi.fn()}
        error="Application deadline cannot be later than 12 Jan 2027"
      />
    );

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(
      screen.getByText('Application deadline cannot be later than 12 Jan 2027')
    ).toBeInTheDocument();
  });
});
