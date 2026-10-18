import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import * as assignmentApi from '../../api/assignment';
import { Assignment } from '../../types/assignment';
import { CourseAssignmentsSection } from './CourseAssignmentsSection';

const mockAssignments: Assignment[] = [
  {
    id: 1,
    course_id: 10,
    title: 'Assignment 1',
    description: 'First assignment description',
    due_at: '2026-11-01T23:59:59Z',
    max_points: 100,
    created_at: '2026-10-18T10:00:00Z',
    updated_at: '2026-10-18T10:00:00Z',
  },
];

describe('CourseAssignmentsSection Component', () => {
  it('renders an enabled "New assignment" button for the owning instructor', async () => {
    vi.spyOn(assignmentApi, 'listCourseAssignments').mockResolvedValue(mockAssignments);

    render(
      <MemoryRouter>
        <CourseAssignmentsSection courseId={10} isOwner={true} />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.queryByText('Loading assignments...')).not.toBeInTheDocument();
    });

    const newAssignmentButton = screen.getByRole('button', { name: 'New assignment' });
    expect(newAssignmentButton).toBeInTheDocument();
    expect(newAssignmentButton).toBeEnabled();
    expect(newAssignmentButton).toHaveClass('bg-petrol');
    expect(newAssignmentButton).toHaveClass('text-surface');

    const link = newAssignmentButton.closest('a');
    expect(link).toHaveAttribute('href', '/courses/10/assignments/new');
  });

  it('does not render "New assignment" button when the user is not the course owner', async () => {
    vi.spyOn(assignmentApi, 'listCourseAssignments').mockResolvedValue(mockAssignments);

    render(
      <MemoryRouter>
        <CourseAssignmentsSection courseId={10} isOwner={false} isStudent={true} />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.queryByText('Loading assignments...')).not.toBeInTheDocument();
    });

    expect(screen.queryByRole('button', { name: 'New assignment' })).not.toBeInTheDocument();
  });
});
