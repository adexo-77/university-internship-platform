import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Brand } from './Brand';

describe('Brand Component', () => {
  it('renders uppercase wordmark and default tagline', () => {
    render(<Brand />);
    expect(screen.getByText('UNIVERSITY')).toBeInTheDocument();
    expect(screen.getByText('Learning & Internship Platform')).toBeInTheDocument();
  });

  it('renders with custom tagline', () => {
    render(<Brand tagline="Custom Tagline Here" />);
    expect(screen.getByText('UNIVERSITY')).toBeInTheDocument();
    expect(screen.getByText('Custom Tagline Here')).toBeInTheDocument();
  });

  it('renders size variants without errors', () => {
    const { rerender } = render(<Brand size="sm" />);
    expect(screen.getByText('UNIVERSITY')).toHaveClass('text-sm');

    rerender(<Brand size="lg" />);
    expect(screen.getByText('UNIVERSITY')).toHaveClass('text-xl');
  });
});
