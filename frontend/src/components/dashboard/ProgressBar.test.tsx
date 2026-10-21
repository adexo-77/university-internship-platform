import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ProgressBar } from './ProgressBar';

describe('ProgressBar', () => {
  it('renders percentage and sets aria attributes', () => {
    render(<ProgressBar percent={42} label="Course Progress" />);

    expect(screen.getByText('42%')).toBeInTheDocument();
    const progressbar = screen.getByRole('progressbar', { name: 'Course Progress' });
    expect(progressbar).toHaveAttribute('aria-valuenow', '42');
    expect(progressbar).toHaveAttribute('aria-valuemin', '0');
    expect(progressbar).toHaveAttribute('aria-valuemax', '100');
  });

  it('clamps percent between 0 and 100', () => {
    const { rerender } = render(<ProgressBar percent={-15} />);
    expect(screen.getByText('0%')).toBeInTheDocument();

    rerender(<ProgressBar percent={150} />);
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('can hide the percentage text', () => {
    render(<ProgressBar percent={75} showPercent={false} />);
    expect(screen.queryByText('75%')).not.toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '75');
  });
});
