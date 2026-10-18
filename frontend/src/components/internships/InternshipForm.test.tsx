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
});
