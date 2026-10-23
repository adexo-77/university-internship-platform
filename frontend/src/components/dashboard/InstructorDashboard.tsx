import React from 'react';
import { Link } from 'react-router-dom';
import { Badge, EmptyState } from '../ui';
import { InstructorDashboardResponse } from '../../types/dashboard';
import { formatDateTime } from '../../lib/dates';
import { StatStrip } from './StatStrip';

export interface InstructorDashboardProps {
  data: InstructorDashboardResponse;
}

export const InstructorDashboard: React.FC<InstructorDashboardProps> = ({ data }) => {
  const totalEnrolled = data.courses.reduce((sum, c) => sum + c.enrolled_count, 0);
  const totalAwaiting = data.courses.reduce(
    (sum, c) => sum + (c.submissions_awaiting_grading ?? c.awaiting_grading_count ?? 0),
    0
  );

  const stats = [
    { label: 'Active courses', value: data.courses.length, to: '/my-courses' },
    { label: 'Total students', value: totalEnrolled },
    {
      label: 'Needs grading',
      value: totalAwaiting,
      badge: totalAwaiting > 0 ? <Badge variant="attention">Pending</Badge> : undefined,
    },
  ];

  return (
    <div className="space-y-6">
      <StatStrip items={stats} />

      {/* Course Summary Section */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-ink">Course summary</h2>
          <Link to="/courses/new" className="text-xs font-medium text-petrol hover:underline">
            Create course
          </Link>
        </div>
        {data.courses.length === 0 ? (
          <EmptyState
            title="No courses found"
            description="Create a new course to start enrolling students and assigning coursework."
            action={
              <Link
                to="/courses/new"
                className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-4 py-2 text-sm leading-snug bg-surface text-ink border-line hover:bg-chalk"
              >
                Create course
              </Link>
            }
          />
        ) : (
          <div className="bg-surface border border-line rounded-control divide-y divide-line overflow-hidden">
            <div className="hidden sm:grid sm:grid-cols-12 px-4 py-2 bg-chalk text-xs font-medium text-pencil">
              <span className="col-span-5">Course</span>
              <span className="col-span-2 text-right">Enrolled</span>
              <span className="col-span-2 text-right">Assignments</span>
              <span className="col-span-3 text-right">Awaiting grading</span>
            </div>
            {data.courses.map((course) => (
              <div
                key={course.course_id}
                className="p-4 sm:grid sm:grid-cols-12 sm:items-center gap-2 hover:bg-chalk transition-colors"
              >
                <div className="col-span-5 space-y-0.5">
                  <div className="flex items-center gap-2">
                    <Link
                      to={`/courses/${course.course_id}`}
                      className="font-medium text-ink hover:text-petrol transition-colors"
                    >
                      {course.title}
                    </Link>
                    <Badge variant={course.status === 'published' ? 'success' : 'neutral'}>
                      {course.status}
                    </Badge>
                  </div>
                  {course.average_grade_percent !== null && (
                    <p className="text-xs text-pencil">
                      Avg. grade: {course.average_grade_percent}%
                    </p>
                  )}
                </div>
                <div className="col-span-2 sm:text-right text-xs text-pencil tabular-nums mt-1 sm:mt-0">
                  <span className="sm:hidden font-medium text-ink mr-1">Enrolled:</span>
                  {course.enrolled_count}
                </div>
                <div className="col-span-2 sm:text-right text-xs text-pencil tabular-nums">
                  <span className="sm:hidden font-medium text-ink mr-1">Assignments:</span>
                  {course.assignments_count}
                </div>
                <div className="col-span-3 sm:text-right mt-1 sm:mt-0">
                  {(course.submissions_awaiting_grading ?? course.awaiting_grading_count ?? 0) >
                  0 ? (
                    <Badge variant="attention">
                      {course.submissions_awaiting_grading ?? course.awaiting_grading_count} pending
                    </Badge>
                  ) : (
                    <span className="text-xs text-pencil">None</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Needs Grading List */}
      <section className="space-y-3">
        <h2 className="text-base font-semibold text-ink">Needs grading</h2>
        {data.needs_grading.length === 0 ? (
          <EmptyState
            title="All caught up"
            description="There are no submissions currently awaiting your review."
          />
        ) : (
          <div className="bg-surface border border-line rounded-control divide-y divide-line overflow-hidden">
            {data.needs_grading.map((item) => (
              <div
                key={item.submission_id}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-chalk transition-colors"
              >
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <Link
                      to={`/assignments/${item.assignment_id}/submissions/${item.submission_id}/grade`}
                      className="font-medium text-ink hover:text-petrol transition-colors"
                    >
                      {item.student_name}
                    </Link>
                    {(item.late ?? item.is_late) && <Badge variant="error">Late</Badge>}
                  </div>
                  <p className="text-xs text-pencil">
                    {item.assignment_title} &bull; {item.course_title}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-pencil tabular-nums">
                    Submitted {formatDateTime(item.submitted_at)}
                  </span>
                  <Link
                    to={`/assignments/${item.assignment_id}/submissions/${item.submission_id}/grade`}
                    className="text-xs font-medium text-petrol hover:underline"
                  >
                    Grade &rarr;
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
