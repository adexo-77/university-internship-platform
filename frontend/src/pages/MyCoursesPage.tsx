import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getInstructorCourses, getStudentCourses } from '../api/course';
import { CourseTable } from '../components/courses/CourseTable';
import { AppShell } from '../components/layout/AppShell';
import { Button } from '../ui/Button';
import { EmptyState } from '../ui/EmptyState';
import { ErrorMessage } from '../ui/ErrorMessage';
import { PageHeader } from '../ui/PageHeader';
import { useAuth } from '../hooks/useAuth';
import { Course } from '../types/course';

export const MyCoursesPage: React.FC = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isInstructor = user?.role === 'instructor';
  const isStudent = user?.role === 'student';

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    const loadCourses = async () => {
      try {
        if (isInstructor) {
          const data = await getInstructorCourses();
          if (isMounted) setCourses(data);
        } else if (isStudent) {
          const data = await getStudentCourses();
          if (isMounted) setCourses(data);
        }
      } catch (err: unknown) {
        if (isMounted) {
          if (err instanceof Error) {
            setError(err.message);
          } else {
            setError('Failed to load courses.');
          }
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadCourses();

    return () => {
      isMounted = false;
    };
  }, [isInstructor, isStudent]);

  return (
    <AppShell>
      <div className="space-y-6">
        <PageHeader
          title="My courses"
          description={
            isInstructor
              ? 'Manage courses you instruct and track student enrollment.'
              : 'View learning courses you are currently enrolled in.'
          }
          actions={
            isInstructor ? (
              <Button as={Link} to="/courses/new" variant="primary">
                New course
              </Button>
            ) : undefined
          }
        />

        {error && <ErrorMessage message={error} />}

        {loading ? (
          <div className="py-12 text-center text-pencil">Loading your courses...</div>
        ) : courses.length === 0 ? (
          <EmptyState
            title={isInstructor ? 'No courses created' : 'No courses enrolled'}
            description={
              isInstructor
                ? "You haven't created any courses yet. Create your first course to begin teaching."
                : "You aren't enrolled in any courses yet. Browse the course catalogue to find courses."
            }
            action={
              isInstructor
                ? {
                    label: 'Create course',
                    href: '/courses/new',
                  }
                : {
                    label: 'Browse courses',
                    href: '/courses',
                  }
            }
          />
        ) : (
          <CourseTable
            courses={courses}
            showStatus={isInstructor}
            showEnrolledCount={isInstructor}
            actionRenderer={
              isInstructor
                ? (item) => (
                    <Link
                      to={`/courses/${item.id}/edit`}
                      className="text-sm font-medium text-brand hover:underline"
                    >
                      Edit
                    </Link>
                  )
                : undefined
            }
          />
        )}
      </div>
    </AppShell>
  );
};
