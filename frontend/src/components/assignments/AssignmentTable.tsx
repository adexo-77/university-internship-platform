import React from 'react';
import { Link } from 'react-router-dom';
import { Assignment } from '../../types/assignment';
import { Column, DataTable } from '../ui/DataTable';
import { EmptyState } from '../ui/EmptyState';
import { DueBadge } from './DueBadge';
import { SubmissionStatusBadge } from './SubmissionStatusBadge';

export interface AssignmentTableProps {
  assignments: Assignment[];
  courseId: number;
  isOwner?: boolean;
  isAdmin?: boolean;
  isStudent?: boolean;
}

export const AssignmentTable: React.FC<AssignmentTableProps> = ({
  assignments,
  courseId,
  isOwner,
  isAdmin,
  isStudent,
}) => {
  const columns: Column<Assignment>[] = [
    {
      key: 'title',
      header: 'Title',
      render: (item) => (
        <div>
          <Link
            to={`/assignments/${item.id}`}
            className="font-medium text-ink hover:text-navy underline-offset-2 hover:underline"
          >
            {item.title}
          </Link>
          {item.description && (
            <p className="text-xs text-pencil truncate max-w-xs">{item.description}</p>
          )}
        </div>
      ),
    },
    {
      key: 'due_at',
      header: 'Due date',
      render: (item) => <DueBadge dueAt={item.due_at} />,
    },
    {
      key: 'max_points',
      header: 'Points',
      render: (item) => (
        <span className="text-sm text-pencil font-medium">{item.max_points} pts</span>
      ),
    },
  ];

  if (isStudent) {
    columns.push({
      key: 'submission_status',
      header: 'Your status',
      render: (item) => (
        <SubmissionStatusBadge
          status={item.submission_status}
          isLate={item.is_late}
          grade={item.grade}
          maxPoints={item.max_points}
        />
      ),
    });
  }

  columns.push({
    key: 'actions',
    header: 'Actions',
    render: (item) => (
      <div className="flex items-center justify-end gap-2">
        <Link
          to={`/assignments/${item.id}`}
          className="text-xs text-navy hover:underline font-medium"
        >
          View
        </Link>
        {(isOwner || isAdmin) && (
          <Link
            to={`/assignments/${item.id}/edit`}
            className="text-xs text-pencil hover:text-ink hover:underline font-medium"
          >
            Edit
          </Link>
        )}
      </div>
    ),
  });

  if (assignments.length === 0) {
    return (
      <EmptyState
        title="No assignments yet"
        description={
          isOwner
            ? 'Get started by creating your first course assignment.'
            : 'No assignments have been assigned for this course yet.'
        }
        action={
          isOwner ? (
            <Link
              to={`/courses/${courseId}/assignments/new`}
              className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control px-4 py-2 text-sm bg-navy text-surface hover:bg-navy-dark"
            >
              Create assignment
            </Link>
          ) : undefined
        }
      />
    );
  }

  return (
    <DataTable
      columns={columns}
      data={assignments}
      keyExtractor={(item) => String(item.id)}
    />
  );
};
