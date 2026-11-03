import React from 'react';
import { Application } from '../../types/application';
import { Column, DataTable } from '../ui/DataTable';
import { TextLink } from '../ui';
import { ApplicationStatusBadge } from './ApplicationStatusBadge';

export interface ApplicantsTableProps {
  applications: Application[];
  emptyMessage?: string;
}

export const ApplicantsTable: React.FC<ApplicantsTableProps> = ({
  applications,
  emptyMessage = 'No applications submitted yet.',
}) => {
  const columns: Column<Application>[] = [
    {
      key: 'name',
      header: 'Applicant name',
      render: (item) => (
        <span className="font-medium text-ink">{item.applicant?.full_name || 'Applicant'}</span>
      ),
    },
    {
      key: 'university',
      header: 'University',
      render: (item) => <span className="text-pencil">{item.applicant?.university || '—'}</span>,
    },
    {
      key: 'department',
      header: 'Department',
      render: (item) => <span className="text-pencil">{item.applicant?.department || '—'}</span>,
    },
    {
      key: 'year',
      header: 'Year',
      render: (item) => (
        <span className="text-ink">
          {item.applicant?.year_of_study ? `Year ${item.applicant.year_of_study}` : '—'}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (item) => <ApplicationStatusBadge status={item.status} />,
    },
    {
      key: 'action',
      header: 'Action',
      render: (item) => (
        <TextLink to={`/applications/${item.id}`} className="text-sm">
          Review
        </TextLink>
      ),
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={applications}
      keyExtractor={(item) => String(item.id)}
      emptyMessage={emptyMessage}
    />
  );
};
