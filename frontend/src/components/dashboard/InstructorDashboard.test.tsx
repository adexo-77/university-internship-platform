import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { InstructorDashboardResponse } from '../../types/dashboard';
import { InstructorDashboard } from './InstructorDashboard';

const mockData: InstructorDashboardResponse = {
  courses: [
    {
      course_id: '1',
      title: 'Operating Systems',
      status: 'published',
      enrolled_count: 25,
      assignments_count: 3,
      awaiting_grading_count: 2,
      average_grade_percent: 88.5,
    },
  ],
  needs_grading: [
    {
      submission_id: '501',
      assignment_id: '101',
      assignment_title: 'Kernel Lab',
      course_id: '1',
      course_title: 'Operating Systems',
      student_name: 'Alice Student',
      submitted_at: '2026-10-20T14:30:00Z',
      is_late: true,
    },
  ],
};

describe('InstructorDashboard', () => {
  it('renders courses, pending counts, and needs grading items', () => {
    render(
      <MemoryRouter>
        <InstructorDashboard data={mockData} />
      </MemoryRouter>
    );

    expect(screen.getByText('Operating Systems')).toBeInTheDocument();
    expect(screen.getAllByText('25').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('2 pending')).toBeInTheDocument();
    expect(screen.getByText('Avg. grade: 88.5%')).toBeInTheDocument();
    expect(screen.getByText('Alice Student')).toBeInTheDocument();
    expect(screen.getByText('Kernel Lab • Operating Systems')).toBeInTheDocument();
    expect(screen.getByText('Late')).toBeInTheDocument();
  });

  it('renders empty states when there are no courses or pending submissions', () => {
    render(
      <MemoryRouter>
        <InstructorDashboard data={{ courses: [], needs_grading: [] }} />
      </MemoryRouter>
    );

    expect(screen.getByText('No courses found')).toBeInTheDocument();
    expect(screen.getByText('All caught up')).toBeInTheDocument();
  });
});
