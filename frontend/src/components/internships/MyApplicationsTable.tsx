import React from 'react';
import { Link } from 'react-router-dom';
import { Application } from '../../types/application';
import { formatDate } from '../../lib/dates';
import { Button } from '../ui/Button';
import { Column, DataTable } from '../ui/DataTable';
import { ApplicationStatusBadge } from './ApplicationStatusBadge';

export interface MyApplicationsTableProps {
  applications: Application[];
  onWithdraw?: (id: number) => void | Promise<void>;
  isWithdrawing?: number | null;
  emptyMessage?: string;
}

export const MyApplicationsTable: React.FC<MyApplicationsTableProps> = ({
  applications,
  onWithdraw,
  isWithdrawing = null,
  emptyMessage = 'You have not submitted any internship applications yet.',
}) => {
  const columns: Column<Application>[] = [
    {
      key: 'posting',
      header: 'Internship',
      render: (item) => (
        <Link
          to={`/internships/${item.posting_id}`}
          className="font-medium text-petrol hover:underline"
        >
          {item.posting_title || `Internship #${item.posting_id}`}
        </Link>
      ),
    },
    {
      key: 'organization',
      header: 'Organization',
      render: (item) => <span className="text-pencil">{item.organization_name || '—'}</span>,
    },
    {
      key: 'applied_at',
      header: 'Applied on',
      render: (item) => <span className="text-ink">{formatDate(item.created_at)}</span>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (item) => <ApplicationStatusBadge status={item.status} />,
    },
    {
      key: 'decision_message',
      header: 'Feedback / message',
      render: (item) => (
        <span className="text-sm text-pencil line-clamp-2">{item.decision_message || '—'}</span>
      ),
    },
  ];

  if (onWithdraw) {
    columns.push({
      key: 'action',
      header: 'Action',
      render: (item) => {
        const canWithdraw = item.status === 'submitted' || item.status === 'shortlisted';
        if (!canWithdraw) return null;
        return (
          <Button
            type="button"
            variant="quiet"
            disabled={isWithdrawing === item.id}
            onClick={() => onWithdraw(item.id)}
          >
            {isWithdrawing === item.id ? 'Withdrawing...' : 'Withdraw'}
          </Button>
        );
      },
    });
  }

  return (
    <DataTable
      columns={columns}
      data={applications}
      keyExtractor={(item) => String(item.id)}
      emptyMessage={emptyMessage}
    />
  );
};
