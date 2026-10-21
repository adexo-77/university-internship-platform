import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { AdminDashboardResponse } from '../../types/dashboard';
import { AdminDashboard } from './AdminDashboard';

const mockData: AdminDashboardResponse = {
  users_by_role: {
    student: 50,
    instructor: 10,
    organization: 5,
    admin: 2,
  },
  active_users_count: 65,
  organizations_pending_approval: 3,
  internships_pending_review: 4,
  open_internships: 12,
  courses_by_status: {
    draft: 2,
    published: 8,
    archived: 1,
  },
  applications_by_status: {
    submitted: 15,
    shortlisted: 5,
    accepted: 3,
    rejected: 4,
    withdrawn: 1,
  },
};

describe('AdminDashboard', () => {
  it('renders summary strip, attention badges, and breakdowns', () => {
    render(
      <MemoryRouter>
        <AdminDashboard data={mockData} />
      </MemoryRouter>
    );

    expect(screen.getByText('65 active')).toBeInTheDocument();
    expect(screen.getByText('3 pending')).toBeInTheDocument();
    expect(screen.getByText('4 pending')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByText('Users by role')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
    expect(screen.getByText('Courses overview')).toBeInTheDocument();
    expect(screen.getByText('Platform applications overview (28 total)')).toBeInTheDocument();
  });
});
