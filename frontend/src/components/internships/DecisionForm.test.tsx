import { act, fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { DecisionForm } from './DecisionForm';

describe('DecisionForm Component', () => {
  it('renders Shortlist, Accept, and Reject for submitted application', () => {
    render(<DecisionForm currentStatus="submitted" onSubmit={vi.fn()} />);

    expect(screen.getByRole('button', { name: 'Shortlist' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Accept' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reject' })).toBeInTheDocument();
  });

  it('renders only Accept and Reject for shortlisted application', () => {
    render(<DecisionForm currentStatus="shortlisted" onSubmit={vi.fn()} />);

    expect(screen.queryByRole('button', { name: 'Shortlist' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Accept' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reject' })).toBeInTheDocument();
  });

  it('renders nothing when decision is final', () => {
    const { container: c1 } = render(<DecisionForm currentStatus="accepted" onSubmit={vi.fn()} />);
    expect(c1).toBeEmptyDOMElement();

    const { container: c2 } = render(<DecisionForm currentStatus="rejected" onSubmit={vi.fn()} />);
    expect(c2).toBeEmptyDOMElement();

    const { container: c3 } = render(<DecisionForm currentStatus="withdrawn" onSubmit={vi.fn()} />);
    expect(c3).toBeEmptyDOMElement();
  });

  it('submits decision action with optional message', async () => {
    const handleSubmit = vi.fn().mockResolvedValue(undefined);
    render(<DecisionForm currentStatus="submitted" onSubmit={handleSubmit} />);

    await act(async () => {
      fireEvent.change(screen.getByLabelText(/decision message/i), {
        target: { value: 'Congratulations! You demonstrated strong system design skills.' },
      });
      fireEvent.click(screen.getByRole('button', { name: 'Accept' }));
    });

    expect(handleSubmit).toHaveBeenCalledWith(
      'accepted',
      'Congratulations! You demonstrated strong system design skills.'
    );
  });
});
