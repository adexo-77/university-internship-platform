import React from 'react';
import { Internship } from '../../types/internship';
import { formatDate } from '../../lib/dates';
import { Button, Column, DataTable } from '../ui';
import { InternshipStatusBadge } from '../internships/InternshipStatusBadge';

export interface AdminInternshipReviewsTableProps {
  internships: Internship[];
  onSelect: (item: Internship) => void;
  emptyMessage?: string;
}

export const AdminInternshipReviewsTable: React.FC<AdminInternshipReviewsTableProps> = ({
  internships,
  onSelect,
  emptyMessage = 'No internship postings match this filter.',
}) => {
  const columns: Column<Internship>[] = [
    {
      key: 'title',
      header: 'Title',
      render: (item) => <span className="font-medium text-ink">{item.title}</span>,
    },
    {
      key: 'organization',
      header: 'Organization',
      render: (item) => (
        <span className="text-pencil">{item.organization_name ?? 'Organization'}</span>
      ),
    },
    {
      key: 'location',
      header: 'Location',
      render: (item) => <span className="text-ink">{item.location}</span>,
    },
    {
      key: 'created_at',
      header: 'Submitted date',
      render: (item) => (
        <span className="text-pencil text-sm font-mono">
          {item.created_at ? formatDate(item.created_at) : '—'}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (item) => <InternshipStatusBadge status={item.status} />,
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (item) => {
        if (item.status === 'open') {
          return (
            <Button type="button" variant="danger" size="sm" onClick={() => onSelect(item)}>
              Take down
            </Button>
          );
        }
        if (item.status === 'pending_review') {
          return (
            <Button type="button" variant="quiet" size="sm" onClick={() => onSelect(item)}>
              Review
            </Button>
          );
        }
        return <span className="text-pencil text-sm">—</span>;
      },
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={internships}
      keyExtractor={(item) => String(item.id)}
      emptyMessage={emptyMessage}
    />
  );
};
