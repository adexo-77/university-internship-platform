import React from 'react';
import { ApplicationStatus } from '../../types/application';
import { Badge } from '../ui/Badge';

export interface ApplicationStatusBadgeProps {
  status: ApplicationStatus;
}

export const ApplicationStatusBadge: React.FC<ApplicationStatusBadgeProps> = ({ status }) => {
  switch (status) {
    case 'accepted':
      return <Badge variant="success">Accepted</Badge>;
    case 'shortlisted':
      return <Badge variant="attention">Shortlisted</Badge>;
    case 'rejected':
      return <Badge variant="error">Rejected</Badge>;
    case 'withdrawn':
      return <Badge variant="neutral">Withdrawn</Badge>;
    case 'submitted':
    default:
      return <Badge variant="neutral">Submitted</Badge>;
  }
};
