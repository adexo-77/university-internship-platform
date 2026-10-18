import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ApplyForm } from './ApplyForm';

describe('ApplyForm Component', () => {
  it('blocks submit and shows error when cover letter is empty', () => {
    const handleSubmit = vi.fn();
    render(<ApplyForm onSubmit={handleSubmit} />);

    fireEvent.click(screen.getByRole('button', { name: 'Submit application' }));

    expect(screen.getByText('Cover letter is required.')).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it('submits valid trimmed cover letter', () => {
    const handleSubmit = vi.fn();
    render(<ApplyForm onSubmit={handleSubmit} />);

    fireEvent.change(screen.getByLabelText(/cover letter/i), {
      target: { value: '  I am very interested in this engineering role.  ' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Submit application' }));

    expect(handleSubmit).toHaveBeenCalledWith('I am very interested in this engineering role.');
  });

  it('displays error message from props', () => {
    render(<ApplyForm onSubmit={vi.fn()} error="You have already applied to this internship" />);

    expect(screen.getByText('You have already applied to this internship')).toBeInTheDocument();
  });
});
