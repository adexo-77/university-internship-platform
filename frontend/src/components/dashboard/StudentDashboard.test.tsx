import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { StudentDashboardResponse } from '../../types/dashboard';
import { StudentDashboard } from './StudentDashboard';

const mockData: StudentDashboardResponse = {
  due_next: [
    {
      assignment_id: 101,
      course_id: 1,
      course_title: 'Algorithms',
      title: 'Problem Set 1',
      due_at: '2026-11-01T12:00:00Z',
    },
  ],
  recent_grades: [
    {
      submission_id: 201,
      assignment_id: 100,
      assignment_title: 'Quiz 1',
      course_title: 'Algorithms',
      grade: 95,
      max_points: 100,
      graded_at: '2026-10-20T10:00:00Z',
    },
  ],
  courses: [
    {
      course_id: 1,
      title: 'Algorithms',
      instructor_name: 'Dr. Turing',
      assignments_total: 4,
      assignments_submitted: 2,
      progress_percent: 50,
      average_grade_percent: 95.0,
    },
  ],
  applications: {
    counts_by_status: { submitted: 1 },
    recent: [
      {
        id: 301,
        posting_id: 401,
        posting_title: 'Backend Intern',
        organization_name: 'Acme Corp',
        status: 'submitted',
        applied_at: '2026-10-19T09:00:00Z',
      },
    ],
  },
  profile_complete: false,
};

describe('StudentDashboard', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes('/api/internships/suggestions')) {
        return new Response(JSON.stringify({ items: [], reason_code: null }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/api/badges/my')) {
        return new Response(JSON.stringify([]), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/api/students/me/study-plan')) {
        return new Response(
          JSON.stringify({
            generated_at: '2026-11-07T08:00:00Z',
            window: { days: 7, start_date: '2026-11-07', end_date: '2026-11-13' },
            summary: {
              headline: 'Your schedule is clear.',
              sentences: ['No pending assignments.'],
              metrics: {
                enrolled_courses_count: 0,
                assignments_due_count: 0,
                total_scheduled_minutes: 0,
                overdue_assignments_count: 0,
              },
            },
            plan: [],
          }),
          {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          }
        );
      }
      return new Response(JSON.stringify({}), { status: 200 });
    });
  });

  it('renders student data and incomplete profile notice', async () => {
    render(
      <MemoryRouter>
        <StudentDashboard data={mockData} />
      </MemoryRouter>
    );

    expect(screen.getByText('Incomplete profile')).toBeInTheDocument();
    expect(screen.getByText('Problem Set 1')).toBeInTheDocument();
    expect(screen.getAllByText('Algorithms').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('50%')).toBeInTheDocument();
    expect(screen.getByText('95 / 100')).toBeInTheDocument();
    expect(screen.getByText('Backend Intern')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('No matching suggestions right now')).toBeInTheDocument();
      expect(screen.getByText('No badges available')).toBeInTheDocument();
    });
  });

  it('hides incomplete profile notice when profile is complete', async () => {
    render(
      <MemoryRouter>
        <StudentDashboard data={{ ...mockData, profile_complete: true }} />
      </MemoryRouter>
    );

    expect(screen.queryByText('Incomplete profile')).not.toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('No matching suggestions right now')).toBeInTheDocument();
      expect(screen.getByText('No badges available')).toBeInTheDocument();
    });
  });

  it('renders empty states when there is no data', async () => {
    const emptyData: StudentDashboardResponse = {
      due_next: [],
      recent_grades: [],
      courses: [],
      applications: { counts_by_status: {}, recent: [] },
      profile_complete: true,
    };

    render(
      <MemoryRouter>
        <StudentDashboard data={emptyData} />
      </MemoryRouter>
    );

    expect(screen.getByText('No upcoming assignments')).toBeInTheDocument();
    expect(screen.getByText('No courses enrolled')).toBeInTheDocument();
    expect(screen.getByText('No graded assignments')).toBeInTheDocument();
    expect(screen.getByText('No applications submitted')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('No matching suggestions right now')).toBeInTheDocument();
      expect(screen.getByText('No badges available')).toBeInTheDocument();
    });
  });
});
