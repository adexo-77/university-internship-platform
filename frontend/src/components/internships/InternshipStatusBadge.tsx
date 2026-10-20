import React from 'react';
import { InternshipStatus } from '../../types/internship';
import { Badge } from '../ui/Badge';

export interface InternshipStatusBadgeProps {
  status: InternshipStatus;
}

export const InternshipStatusBadge: React.FC<InternshipStatusBadgeProps> = ({ status }) => {
  switch (status) {
    case 'open':
      return <Badge variant="success">Open</Badge>;
    case 'pending_review':
      return <Badge variant="attention">Pending review</Badge>;
    case 'rejected':
      return <Badge variant="error">Rejected</Badge>;
    case 'closed':
      return <Badge variant="neutral">Closed</Badge>;
    case 'draft':
    default:
      return <Badge variant="neutral">Draft</Badge>;
  }
};
