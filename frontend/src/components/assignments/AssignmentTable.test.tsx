import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { Assignment } from '../../types/assignment';
import { AssignmentTable } from './AssignmentTable';

const mockAssignments: Assignment[] = [
  {
    id: 1,
    course_id: 10,
    title: 'Problem Set 1',
    description: 'Graph algorithms assignment',
    due_at: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
    max_points: 100,
    created_at: '2026-10-18T10:00:00Z',
    updated_at: '2026-10-18T10:00:00Z',
    submission_status: 'submitted',
    is_late: false,
    grade: null,
  },
  {
    id: 2,
    course_id: 10,
    title: 'Problem Set 2',
    description: 'Dynamic programming',
    due_at: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000).toISOString(),
    max_points: 50,
    created_at: '2026-10-18T10:00:00Z',
    updated_at: '2026-10-18T10:00:00Z',
    submission_status: 'not_submitted',
    is_late: null,
    grade: null,
  },
];

describe('AssignmentTable Component', () => {
  it('renders assignment list with titles, points, and status for student', () => {
    render(
      <MemoryRouter>
        <AssignmentTable assignments={mockAssignments} courseId={10} isStudent={true} />
      </MemoryRouter>
    );

    expect(screen.getByText('Problem Set 1')).toBeInTheDocument();
    expect(screen.getByText('Problem Set 2')).toBeInTheDocument();
    expect(screen.getByText('100 pts')).toBeInTheDocument();
    expect(screen.getByText('50 pts')).toBeInTheDocument();

    expect(screen.getByText('Submitted')).toBeInTheDocument();
    expect(screen.getByText('Not submitted')).toBeInTheDocument();
  });

  it('renders empty state when no assignments exist', () => {
    render(
      <MemoryRouter>
        <AssignmentTable assignments={[]} courseId={10} isOwner={true} />
      </MemoryRouter>
    );

    expect(screen.getByText('No assignments yet')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Create assignment' })).toBeInTheDocument();
  });
});
