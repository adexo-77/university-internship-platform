import React from 'react';
import { Link } from 'react-router-dom';
import { Course } from '../../types/course';
import { Badge } from '../ui/Badge';
import { Column, DataTable } from '../ui/DataTable';

export interface CourseTableProps {
  courses: Course[];
  showStatus?: boolean;
  showEnrolledCount?: boolean;
  showEnrolledBadge?: boolean;
  emptyMessage?: string;
  actionRenderer?: (course: Course) => React.ReactNode;
}

export const CourseTable: React.FC<CourseTableProps> = ({
  courses,
  showStatus = false,
  showEnrolledCount = false,
  showEnrolledBadge = false,
  emptyMessage = 'No courses found.',
  actionRenderer,
}) => {
  const columns: Column<Course>[] = [
    {
      key: 'title',
      header: 'Course title',
      render: (item) => (
        <Link to={`/courses/${item.id}`} className="font-medium text-brand hover:underline">
          {item.title}
        </Link>
      ),
    },
    {
      key: 'instructor',
      header: 'Instructor',
      render: (item) => <span className="text-pencil">{item.instructor_name || '—'}</span>,
    },
  ];

  if (showEnrolledCount) {
    columns.push({
      key: 'enrolled_count',
      header: 'Enrolled students',
      isNumeric: true,
      render: (item) => <span className="text-ink tabular-nums">{item.enrolled_count ?? 0}</span>,
    });
  }

  if (showStatus) {
    columns.push({
      key: 'status',
      header: 'Status',
      render: (item) => (
        <Badge variant={item.status === 'published' ? 'success' : 'neutral'}>
          {item.status === 'published' ? 'Published' : 'Draft'}
        </Badge>
      ),
    });
  }

  if (showEnrolledBadge) {
    columns.push({
      key: 'enrolled',
      header: 'Enrollment',
      render: (item) => (item.enrolled ? <Badge variant="success">Enrolled</Badge> : null),
    });
  }

  if (actionRenderer) {
    columns.push({
      key: 'actions',
      header: 'Actions',
      render: actionRenderer,
    });
  }

  return (
    <DataTable
      columns={columns}
      data={courses}
      keyExtractor={(item) => String(item.id)}
      emptyMessage={emptyMessage}
    />
  );
};
