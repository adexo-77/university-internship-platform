import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { InternshipStatusBadge } from './InternshipStatusBadge';
import { InternshipStatus } from '../../types/internship';

describe('InternshipStatusBadge', () => {
  const statuses: { status: InternshipStatus; label: string }[] = [
    { status: 'draft', label: 'draft' },
    { status: 'pending_review', label: 'pending review' },
    { status: 'open', label: 'open' },
    { status: 'rejected', label: 'rejected' },
    { status: 'closed', label: 'closed' },
  ];

  statuses.forEach(({ status, label }) => {
    it(`renders correct label for status: ${status}`, () => {
      render(<InternshipStatusBadge status={status} />);
      expect(screen.getByText(new RegExp(label, 'i'))).toBeInTheDocument();
    });
  });
});
