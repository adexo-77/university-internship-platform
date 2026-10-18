import React from 'react';
import { formatDateTime } from '../../lib/dates';
import { Submission } from '../../types/assignment';
import { Badge } from '../ui/Badge';

export interface SubmissionStatusPanelProps {
  submission?: Submission | null;
  maxPoints: number;
}

export const SubmissionStatusPanel: React.FC<SubmissionStatusPanelProps> = ({
  submission,
  maxPoints,
}) => {
  const isGraded = submission?.grade !== null && submission?.grade !== undefined;

  return (
    <div
      data-testid="submission-status-panel"
      className="rounded-control border border-line bg-surface p-4 flex items-center justify-between flex-wrap gap-3"
    >
      <span className="text-xs font-semibold text-pencil">Submission status</span>
      <div className="flex items-center gap-2 flex-wrap">
        {!submission ? (
          <Badge variant="neutral">Not submitted</Badge>
        ) : isGraded ? (
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="success">Graded</Badge>
            <span className="text-sm font-bold text-ink">
              {submission.grade} / {maxPoints}
            </span>
            {submission.is_late && <Badge variant="attention">Late</Badge>}
          </div>
        ) : (
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-ink">
              Submitted on {formatDateTime(submission.submitted_at)}
            </span>
            {submission.is_late && <Badge variant="attention">Late</Badge>}
          </div>
        )}
      </div>
    </div>
  );
};
