import React from 'react';
import { SubmissionStatus } from '../../types/assignment';
import { Badge } from '../ui/Badge';

export interface SubmissionStatusBadgeProps {
  status?: SubmissionStatus | null;
  isLate?: boolean | null;
  grade?: number | null;
  maxPoints?: number | null;
}

export const SubmissionStatusBadge: React.FC<SubmissionStatusBadgeProps> = ({
  status,
  isLate,
  grade,
  maxPoints,
}) => {
  if (!status) {
    return null;
  }

  const renderStatus = () => {
    switch (status) {
      case 'graded':
        return (
          <Badge variant="success">
            Graded{grade !== null && grade !== undefined ? ` (${grade}/${maxPoints ?? 100})` : ''}
          </Badge>
        );
      case 'submitted':
        return <Badge variant="success">Submitted</Badge>;
      case 'not_submitted':
      default:
        return <Badge variant="neutral">Not submitted</Badge>;
    }
  };

  return (
    <span className="inline-flex items-center gap-1.5 flex-wrap">
      {renderStatus()}
      {isLate && <Badge variant="attention">Late</Badge>}
    </span>
  );
};
