import React from 'react';
import { Link } from 'react-router-dom';
import { StudentSubmissionRosterItem } from '../../types/assignment';
import { Badge } from '../ui/Badge';
import { Column, DataTable } from '../ui/DataTable';
import { EmptyState } from '../ui/EmptyState';

export interface SubmissionsTableProps {
  roster: StudentSubmissionRosterItem[];
  assignmentId: number;
  maxPoints: number;
  isOwner?: boolean;
}

export const SubmissionsTable: React.FC<SubmissionsTableProps> = ({
  roster,
  assignmentId,
  maxPoints,
  isOwner = false,
}) => {
  const columns: Column<StudentSubmissionRosterItem>[] = [
    {
      key: 'student',
      header: 'Student',
      render: (item) => (
        <div>
          <span className="font-medium text-ink block">{item.student_name}</span>
          <span className="text-xs text-pencil">{item.student_email}</span>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (item) => {
        if (!item.submission) {
          return <Badge variant="neutral">Not submitted</Badge>;
        }
        return (
          <div className="flex items-center gap-1.5 flex-wrap">
            <Badge variant="success">Submitted</Badge>
            {item.submission.is_late && <Badge variant="attention">Late</Badge>}
          </div>
        );
      },
    },
    {
      key: 'grade',
      header: 'Grade',
      render: (item) => {
        if (!item.submission) return <span className="text-pencil text-sm">—</span>;
        if (item.submission.grade !== null && item.submission.grade !== undefined) {
          return (
            <span className="font-semibold text-ink text-sm">
              {item.submission.grade} / {maxPoints}
            </span>
          );
        }
        return <span className="text-pencil text-sm italic">Ungraded</span>;
      },
    },
  ];

  if (isOwner) {
    columns.push({
      key: 'actions',
      header: 'Actions',
      render: (item) => {
        if (!item.submission) {
          return <span className="text-pencil text-xs italic">Awaiting submission</span>;
        }
        return (
          <Link
            to={`/assignments/${assignmentId}/submissions/${item.submission.id}/grade`}
            className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-3 py-1 text-xs bg-surface text-ink border-line hover:bg-chalk"
          >
            {item.submission.grade !== null ? 'Regrade' : 'Grade'}
          </Link>
        );
      },
    });
  }

  if (roster.length === 0) {
    return (
      <EmptyState
        title="No enrolled students"
        description="There are currently no students enrolled in this course to submit work."
      />
    );
  }

  return (
    <DataTable columns={columns} data={roster} keyExtractor={(item) => String(item.student_id)} />
  );
};
