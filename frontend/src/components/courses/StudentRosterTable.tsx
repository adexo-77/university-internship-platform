import React from 'react';
import { EnrolledStudent } from '../../types/course';
import { Column, DataTable } from '../ui/DataTable';

export interface StudentRosterTableProps {
  students: EnrolledStudent[];
  emptyMessage?: string;
}

export const StudentRosterTable: React.FC<StudentRosterTableProps> = ({
  students,
  emptyMessage = 'No students enrolled yet.',
}) => {
  const columns: Column<EnrolledStudent>[] = [
    {
      key: 'name',
      header: 'Student name',
      render: (item) => <span className="font-medium text-ink">{item.name}</span>,
    },
    {
      key: 'email',
      header: 'Email address',
      render: (item) => <span className="text-pencil">{item.email}</span>,
    },
    {
      key: 'enrolled_at',
      header: 'Enrolled date',
      render: (item) => {
        const date = new Date(item.enrolled_at);
        return (
          <span className="text-pencil tabular-nums">
            {Number.isNaN(date.getTime()) ? item.enrolled_at : date.toLocaleDateString()}
          </span>
        );
      },
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={students}
      keyExtractor={(item) => String(item.student_id)}
      emptyMessage={emptyMessage}
    />
  );
};
