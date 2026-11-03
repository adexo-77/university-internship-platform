import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { IconButton } from './IconButton';

describe('IconButton Component', () => {
  it('renders button with accessible label and icon', () => {
    render(
      <IconButton aria-label="Toggle navigation" icon={<span data-testid="test-icon">Icon</span>} />
    );
    const button = screen.getByRole('button', { name: 'Toggle navigation' });
    expect(button).toBeInTheDocument();
    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
    expect(button).toHaveClass('min-h-[44px]');
  });

  it('renders disabled state correctly', () => {
    render(<IconButton aria-label="Disabled button" disabled icon={<span>Icon</span>} />);
    const button = screen.getByRole('button', { name: 'Disabled button' });
    expect(button).toBeDisabled();
    expect(button).toHaveClass('disabled:cursor-not-allowed');
  });
});
