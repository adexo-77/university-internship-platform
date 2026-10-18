import React from 'react';
import { formatLocalDateTime, isDueSoon, isPastDue } from '../../lib/dates';
import { Badge } from '../ui/Badge';

export interface DueBadgeProps {
  dueAt: string;
  className?: string;
  showTime?: boolean;
}

export const DueBadge: React.FC<DueBadgeProps> = ({ dueAt, className = '', showTime = true }) => {
  const formattedTime = formatLocalDateTime(dueAt);
  const dueSoon = isDueSoon(dueAt);
  const pastDue = isPastDue(dueAt);

  return (
    <span className={`inline-flex items-center gap-2 flex-wrap ${className}`}>
      {showTime && <span className="text-sm text-ink">{formattedTime}</span>}
      {dueSoon && <Badge variant="attention">Due soon</Badge>}
      {pastDue && <Badge variant="error">Past due</Badge>}
    </span>
  );
};
