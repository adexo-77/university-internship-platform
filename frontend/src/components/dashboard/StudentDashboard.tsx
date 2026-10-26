import React from 'react';
import { Link } from 'react-router-dom';
import { DueBadge } from '../assignments/DueBadge';
import { EmptyState, Notice } from '../ui';
import { StudentDashboardResponse } from '../../types/dashboard';
import { formatDate } from '../../lib/dates';
import { StatStrip } from './StatStrip';
import { StudentApplicationsSection } from './StudentApplicationsSection';
import { StudentCoursesSection } from './StudentCoursesSection';
import { StudentBadgesSection } from '../badges/StudentBadgesSection';

export interface StudentDashboardProps {
  data: StudentDashboardResponse;
}

export const StudentDashboard: React.FC<StudentDashboardProps> = ({ data }) => {
  const appCounts = data.applications.counts_by_status;
  const totalApplications = Object.values(appCounts).reduce((sum, count) => sum + count, 0);

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
                  <DueBadge dueAt={item.due_at} />
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Course Progress Section */}
      <StudentCoursesSection courses={data.courses} />

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
      <StudentApplicationsSection
        applications={data.applications}
        totalApplications={totalApplications}
      />

      {/* Achievement Badges Section */}
      <StudentBadgesSection />
    </div>
  );
};
