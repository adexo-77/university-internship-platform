import React from 'react';
import { Link } from 'react-router-dom';
import { EmptyState } from '../ui';
import { StudentCourseProgress } from '../../types/dashboard';
import { ProgressBar } from './ProgressBar';

export interface StudentCoursesSectionProps {
  courses: StudentCourseProgress[];
}

export const StudentCoursesSection: React.FC<StudentCoursesSectionProps> = ({ courses }) => {
  return (
    <section className="space-y-3">
      <h2 className="text-base font-semibold text-ink">Course progress</h2>
      {courses.length === 0 ? (
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
          {courses.map((course) => (
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
                {course.instructor_name && (
                  <p className="text-xs text-pencil">{course.instructor_name}</p>
                )}
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
                  {course.average_grade_percent !== null ? `${course.average_grade_percent}%` : '—'}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};
