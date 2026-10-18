import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { StudentSubmissionRosterItem } from '../../types/assignment';
import { SubmissionsTable } from './SubmissionsTable';

const mockRoster: StudentSubmissionRosterItem[] = [
  {
    student_id: 101,
    student_name: 'Alice Cooper',
    student_email: 'alice@uni.edu',
    submission: {
      id: 11,
      assignment_id: 1,
      student_id: 101,
      content: 'Alice answer',
      link_url: null,
      is_late: false,
      submitted_at: '2026-10-18T10:00:00Z',
      updated_at: '2026-10-18T10:00:00Z',
      grade: 95,
      feedback: 'Well done',
      graded_at: '2026-10-18T11:00:00Z',
      graded_by: 1,
    },
  },
  {
    student_id: 102,
    student_name: 'Bob Marley',
    student_email: 'bob@uni.edu',
    submission: {
      id: 12,
      assignment_id: 1,
      student_id: 102,
      content: 'Bob late answer',
      link_url: null,
      is_late: true,
      submitted_at: '2026-10-18T12:00:00Z',
      updated_at: '2026-10-18T12:00:00Z',
      grade: null,
      feedback: null,
      graded_at: null,
      graded_by: null,
    },
  },
  {
    student_id: 103,
    student_name: 'Charlie Brown',
    student_email: 'charlie@uni.edu',
    submission: null,
  },
];

describe('SubmissionsTable Component', () => {
  it('renders every enrolled student with status, late flag, and grades', () => {
    render(
      <MemoryRouter>
        <SubmissionsTable roster={mockRoster} assignmentId={1} maxPoints={100} isOwner={true} />
      </MemoryRouter>
    );

    // Student names
    expect(screen.getByText('Alice Cooper')).toBeInTheDocument();
    expect(screen.getByText('Bob Marley')).toBeInTheDocument();
    expect(screen.getByText('Charlie Brown')).toBeInTheDocument();

    // Alice: graded 95 / 100, Regrade link
    expect(screen.getByText('95 / 100')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Regrade' })).toBeInTheDocument();

    // Bob: late badge, ungraded, Grade link
    expect(screen.getByText('Late')).toBeInTheDocument();
    expect(screen.getByText('Ungraded')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Grade' })).toBeInTheDocument();

    // Charlie: not submitted, awaiting submission
    expect(screen.getByText('Not submitted')).toBeInTheDocument();
    expect(screen.getByText('Awaiting submission')).toBeInTheDocument();
  });

  it('renders empty state when no students are enrolled', () => {
    render(
      <MemoryRouter>
        <SubmissionsTable roster={[]} assignmentId={1} maxPoints={100} isOwner={true} />
      </MemoryRouter>
    );

    expect(screen.getByText('No enrolled students')).toBeInTheDocument();
  });
});
