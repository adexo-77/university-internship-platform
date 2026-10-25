import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { CoordinatorDashboardResponse } from '../../types/dashboard';
import { CoordinatorDashboard } from './CoordinatorDashboard';

const mockData: CoordinatorDashboardResponse = {
  organizations_pending_approval: 3,
  internships_pending_review: 4,
  open_internships: 12,
  applications_by_status: {
    submitted: 15,
    shortlisted: 5,
    accepted: 3,
    rejected: 4,
    withdrawn: 1,
  },
  reviews_completed: 8,
};

describe('CoordinatorDashboard', () => {
  it('renders stats strip, pending badges, and application status breakdown', () => {
    render(
      <MemoryRouter>
        <CoordinatorDashboard data={mockData} />
      </MemoryRouter>
    );

    expect(screen.getByText('3 pending')).toBeInTheDocument();
    expect(screen.getByText('4 pending')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();
    expect(screen.getByText('Completed by you')).toBeInTheDocument();
    expect(screen.getByText('Review work queues')).toBeInTheDocument();
    expect(screen.getByText('Platform applications overview (28 total)')).toBeInTheDocument();
  });
});
