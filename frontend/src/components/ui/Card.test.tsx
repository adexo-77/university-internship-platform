import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { Card } from './Card';

describe('Card Component', () => {
  it('renders static card container when not interactive', () => {
    render(<Card>Static Content</Card>);
    const card = screen.getByText('Static Content');
    expect(card).toBeInTheDocument();
    expect(card).not.toHaveClass('cursor-pointer');
  });

  it('renders clickable link card when to is provided', () => {
    render(
      <MemoryRouter>
        <Card to="/internships/1">Internship Card</Card>
      </MemoryRouter>
    );
    const link = screen.getByRole('link', { name: 'Internship Card' });
    expect(link).toHaveAttribute('href', '/internships/1');
    expect(link).toHaveClass('cursor-pointer', 'hover:border-petrol');
  });

  it('handles keyboard navigation and clicks when onClick is provided', () => {
    const handleClick = vi.fn();
    render(<Card onClick={handleClick}>Clickable Card</Card>);
    const card = screen.getByRole('button', { name: 'Clickable Card' });
    fireEvent.click(card);
    expect(handleClick).toHaveBeenCalledTimes(1);

    fireEvent.keyDown(card, { key: 'Enter' });
    expect(handleClick).toHaveBeenCalledTimes(2);
  });
});
