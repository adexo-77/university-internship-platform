import React from 'react';
import { Link } from 'react-router-dom';
import { DueBadge } from '../assignments/DueBadge';
import { ApplicationStatusBadge } from '../internships/ApplicationStatusBadge';
import { EmptyState, Notice } from '../ui';
import { ApplicationStatus } from '../../types/application';
import { StudentDashboardResponse } from '../../types/dashboard';
import { formatDate } from '../../lib/dates';
import { ProgressBar } from './ProgressBar';
import { StatStrip } from './StatStrip';

export interface StudentDashboardProps {
  data: StudentDashboardResponse;
}

export const StudentDashboard: React.FC<StudentDashboardProps> = ({ data }) => {
  const totalApplications = Object.values(data.applications.counts).reduce(
    (sum, count) => sum + count,
    0
  );

  const stats = [
    { label: 'Enrolled courses', value: data.courses.length, to: '/my-courses' },
    { label: 'Assignments due', value: data.due_next.length },
    { label: 'Recent grades', value: data.recent_grades.length },
    { label: 'Applications', value: totalApplications, to: '/my-applications' },
  ];

  return (
    <div className="space-y-6">
      {!data.profile_complete && (
        <Notice variant="attention" title="Incomplete profile">
          Your profile is missing university or department details.{' '}
          <Link
            to="/profile"
            className="underline font-medium text-ink hover:text-petrol transition-colors"
          >
            Complete your profile
          </Link>{' '}
          to apply for internships.
        </Notice>
      )}

      <StatStrip items={stats} />

      {/* Due Next Section */}
      <section className="space-y-3">
        <h2 className="text-base font-semibold text-ink">Due next</h2>
        {data.due_next.length === 0 ? (
          <EmptyState
            title="No upcoming assignments"
            description="You have no pending assignments due in your enrolled courses."
            action={
              <Link
                to="/my-courses"
                className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-4 py-2 text-sm leading-snug bg-surface text-ink border-line hover:bg-chalk"
              >
                View enrolled courses
              </Link>
            }
          />
        ) : (
          <div className="bg-surface border border-line rounded-control divide-y divide-line overflow-hidden">
            {data.due_next.map((item) => (
              <div
                key={item.assignment_id}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-chalk transition-colors"
              >
                <div className="space-y-0.5">
                  <Link
                    to={`/assignments/${item.assignment_id}`}
                    className="font-medium text-ink hover:text-petrol transition-colors"
                  >
                    {item.title}
                  </Link>
                  <p className="text-xs text-pencil">{item.course_title}</p>
                </div>
                <div className="flex items-center gap-3 self-start sm:self-auto">
                  <span className="text-xs text-pencil tabular-nums">{item.max_points} pts</span>
                  <DueBadge dueAt={item.due_at} />
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Course Progress Section */}
      <section className="space-y-3">
        <h2 className="text-base font-semibold text-ink">Course progress</h2>
        {data.courses.length === 0 ? (
          <EmptyState
            title="No courses enrolled"
            description="Explore the catalog to find and enroll in active courses."
            action={
              <Link
                to="/courses"
                className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-4 py-2 text-sm leading-snug bg-surface text-ink border-line hover:bg-chalk"
              >
                Browse courses
              </Link>
            }
          />
        ) : (
          <div className="bg-surface border border-line rounded-control divide-y divide-line overflow-hidden">
            {data.courses.map((course) => (
              <div
                key={course.course_id}
                className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-chalk transition-colors"
              >
                <div className="md:w-1/3 space-y-0.5">
                  <Link
                    to={`/courses/${course.course_id}`}
                    className="font-medium text-ink hover:text-petrol transition-colors"
                  >
                    {course.title}
                  </Link>
                  <p className="text-xs text-pencil">{course.instructor_name}</p>
                </div>
                <div className="md:w-1/3">
                  <div className="flex items-center justify-between text-xs text-pencil mb-1">
                    <span>
                      {course.assignments_submitted} of {course.assignments_total} submitted
                    </span>
                  </div>
                  <ProgressBar
                    percent={course.progress_percent}
                    label={`Progress for ${course.title}`}
                  />
                </div>
                <div className="md:w-1/4 text-right">
                  <span className="text-xs text-pencil">Average grade</span>
                  <p className="text-sm font-semibold text-ink tabular-nums">
                    {course.average_grade_percent !== null
                      ? `${course.average_grade_percent}%`
                      : '—'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Recent Grades Section */}
      <section className="space-y-3">
        <h2 className="text-base font-semibold text-ink">Recent grades</h2>
        {data.recent_grades.length === 0 ? (
          <EmptyState
            title="No graded assignments"
            description="Graded submissions will appear here once reviewed by your instructor."
          />
        ) : (
          <div className="bg-surface border border-line rounded-control divide-y divide-line overflow-hidden">
            {data.recent_grades.map((grade) => (
              <div
                key={grade.submission_id}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-chalk transition-colors"
              >
                <div className="space-y-0.5">
                  <Link
                    to={`/assignments/${grade.assignment_id}`}
                    className="font-medium text-ink hover:text-petrol transition-colors"
                  >
                    {grade.assignment_title}
                  </Link>
                  <p className="text-xs text-pencil">
                    {grade.course_title} &bull; Graded {formatDate(grade.graded_at)}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-sm font-semibold text-ink tabular-nums">
                    {grade.grade} / {grade.max_points}
                  </span>
                  <span className="text-xs text-pencil ml-1 tabular-nums">
                    ({Math.round((grade.grade / grade.max_points) * 100)}%)
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Internship Applications Section */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-ink">Internship applications</h2>
          {totalApplications > 0 && (
            <Link to="/my-applications" className="text-xs font-medium text-petrol hover:underline">
              View all
            </Link>
          )}
        </div>
        {data.applications.recent.length === 0 ? (
          <EmptyState
            title="No applications submitted"
            description="Explore open internship postings to submit an application."
            action={
              <Link
                to="/internships"
                className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-4 py-2 text-sm leading-snug bg-surface text-ink border-line hover:bg-chalk"
              >
                Browse internships
              </Link>
            }
          />
        ) : (
          <div className="bg-surface border border-line rounded-control divide-y divide-line overflow-hidden">
            {data.applications.recent.map((app) => (
              <div
                key={app.application_id}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-chalk transition-colors"
              >
                <div className="space-y-0.5">
                  <Link
                    to={`/applications/${app.application_id}`}
                    className="font-medium text-ink hover:text-petrol transition-colors"
                  >
                    {app.posting_title}
                  </Link>
                  <p className="text-xs text-pencil">
                    {app.organization_name} &bull; Applied {formatDate(app.applied_at)}
                  </p>
                </div>
                <div>
                  <ApplicationStatusBadge status={app.status as ApplicationStatus} />
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
