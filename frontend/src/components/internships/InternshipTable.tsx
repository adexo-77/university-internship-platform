import React from 'react';
import { Link } from 'react-router-dom';
import { Internship } from '../../types/internship';
import { ApplicationStatus } from '../../types/application';
import { Column, DataTable } from '../ui/DataTable';
import { DueBadge } from '../assignments/DueBadge';
import { InternshipStatusBadge } from './InternshipStatusBadge';
import { ApplicationStatusBadge } from './ApplicationStatusBadge';

export interface InternshipTableProps {
  internships: Internship[];
  showStatus?: boolean;
  showOrganization?: boolean;
  showApplicantCount?: boolean;
  showApplicationStatus?: boolean;
  emptyMessage?: string;
  actionRenderer?: (internship: Internship) => React.ReactNode;
}

export const InternshipTable: React.FC<InternshipTableProps> = ({
  internships,
  showStatus = false,
  showOrganization = true,
  showApplicantCount = false,
  showApplicationStatus = false,
  emptyMessage = 'No internships found.',
  actionRenderer,
}) => {
  const columns: Column<Internship>[] = [
    {
      key: 'title',
      header: 'Title',
      render: (item) => (
        <Link to={`/internships/${item.id}`} className="font-medium text-petrol hover:underline">
          {item.title}
        </Link>
      ),
    },
  ];

  if (showOrganization) {
    columns.push({
      key: 'organization',
      header: 'Organization',
      render: (item) => <span className="text-pencil">{item.organization_name || '—'}</span>,
    });
  }

  columns.push(
    {
      key: 'location',
      header: 'Location',
      render: (item) => <span className="text-ink">{item.location}</span>,
    },
    {
      key: 'work_mode',
      header: 'Work mode',
      render: (item) => <span className="capitalize text-ink">{item.work_mode}</span>,
    },
    {
      key: 'deadline',
      header: 'Application deadline',
      render: (item) => <DueBadge dueAt={item.application_deadline} />,
    }
  );

  if (showApplicantCount) {
    columns.push({
      key: 'applicant_count',
      header: 'Applicants',
      isNumeric: true,
      render: (item) => <span className="text-ink tabular-nums">{item.applicant_count ?? 0}</span>,
    });
  }

  if (showStatus) {
    columns.push({
      key: 'status',
      header: 'Status',
      render: (item) => <InternshipStatusBadge status={item.status} />,
    });
  }

  if (showApplicationStatus) {
    columns.push({
      key: 'application_status',
      header: 'My application',
      render: (item) =>
        item.application_status ? (
          <ApplicationStatusBadge status={item.application_status as ApplicationStatus} />
        ) : (
          <span className="text-pencil">Not applied</span>
        ),
    });
  }

  if (actionRenderer) {
    columns.push({
      key: 'actions',
      header: 'Actions',
      render: (item) => actionRenderer(item),
    });
  }

  return (
    <DataTable
      columns={columns}
      data={internships}
      keyExtractor={(item) => String(item.id)}
      emptyMessage={emptyMessage}
    />
  );
};
