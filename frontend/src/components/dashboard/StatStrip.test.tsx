import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { Badge } from '../ui';
import { StatStrip } from './StatStrip';

describe('StatStrip', () => {
  it('renders stat items with labels and values', () => {
    render(
      <MemoryRouter>
        <StatStrip
          items={[
            { label: 'Active courses', value: 3 },
            {
              label: 'Pending reviews',
              value: 2,
              badge: <Badge variant="attention">Pending</Badge>,
            },
          ]}
        />
      </MemoryRouter>
    );

    expect(screen.getByText('Active courses')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('Pending reviews')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('Pending')).toBeInTheDocument();
  });

  it('renders linked items as router links', () => {
    render(
      <MemoryRouter>
        <StatStrip
          items={[
            { label: 'Users', value: 10, to: '/admin/users' },
            { label: 'Static', value: 5 },
          ]}
        />
      </MemoryRouter>
    );

    const userLink = screen.getByRole('link', { name: /users/i });
    expect(userLink).toHaveAttribute('href', '/admin/users');
    expect(screen.queryByRole('link', { name: /static/i })).not.toBeInTheDocument();
  });
});
