import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { DueBadge } from './DueBadge';

describe('DueBadge Component', () => {
  it('renders formatted time and "Due soon" badge when due within 3 days', () => {
    const twoDaysFromNow = new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString();
    render(<DueBadge dueAt={twoDaysFromNow} />);

    expect(screen.getByText('Due soon')).toBeInTheDocument();
  });

  it('renders "Past due" badge when due in past', () => {
    const pastDate = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
    render(<DueBadge dueAt={pastDate} />);

    expect(screen.getByText('Past due')).toBeInTheDocument();
  });

  it('renders formatted time without badges when due far in future', () => {
    const farFuture = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();
    render(<DueBadge dueAt={farFuture} />);

    expect(screen.queryByText('Due soon')).not.toBeInTheDocument();
    expect(screen.queryByText('Past due')).not.toBeInTheDocument();
  });
});
