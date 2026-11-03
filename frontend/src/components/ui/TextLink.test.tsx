import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { TextLink } from './TextLink';

describe('TextLink Component', () => {
  it('renders router link when to is provided', () => {
    render(
      <MemoryRouter>
        <TextLink to="/courses">View courses</TextLink>
      </MemoryRouter>
    );
    const link = screen.getByRole('link', { name: 'View courses' });
    expect(link).toHaveAttribute('href', '/courses');
    expect(link).toHaveClass('text-petrol', 'underline');
  });

  it('renders anchor tag when href is provided', () => {
    render(
      <TextLink href="https://example.com" target="_blank">
        External Link
      </TextLink>
    );
    const link = screen.getByRole('link', { name: 'External Link' });
    expect(link).toHaveAttribute('href', 'https://example.com');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('renders subtle and danger variants', () => {
    const { rerender } = render(
      <MemoryRouter>
        <TextLink to="/cancel" variant="subtle">
          Cancel
        </TextLink>
      </MemoryRouter>
    );
    expect(screen.getByRole('link', { name: 'Cancel' })).toHaveClass('text-pencil');

    rerender(
      <MemoryRouter>
        <TextLink to="/delete" variant="danger">
          Delete
        </TextLink>
      </MemoryRouter>
    );
    expect(screen.getByRole('link', { name: 'Delete' })).toHaveClass('text-brick');
  });
});
