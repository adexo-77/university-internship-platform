import React from 'react';
import { Link } from 'react-router-dom';
import { Assignment } from '../../types/assignment';
import { Button, EmptyState, TextLink } from '../ui';
import { Column, DataTable } from '../ui/DataTable';
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
          <TextLink
            to={`/assignments/${item.id}`}
            className="font-medium text-ink hover:text-petrol"
          >
            {item.title}
          </TextLink>
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
        <TextLink to={`/assignments/${item.id}`} className="text-xs">
          View
        </TextLink>
        {(isOwner || isAdmin) && (
          <TextLink to={`/assignments/${item.id}/edit`} variant="subtle" className="text-xs">
            Edit
          </TextLink>
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
            <Link to={`/courses/${courseId}/assignments/new`}>
              <Button>Create assignment</Button>
            </Link>
          ) : undefined
        }
      />
    );
  }

  return (
    <DataTable columns={columns} data={assignments} keyExtractor={(item) => String(item.id)} />
  );
};
