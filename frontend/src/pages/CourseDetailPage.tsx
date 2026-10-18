import React, { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getCourseById, getCourseRoster, updateCourse } from '../api/course';
import { EnrollButton } from '../components/courses/EnrollButton';
import { StudentRosterTable } from '../components/courses/StudentRosterTable';
import { AppShell } from '../components/layout/AppShell';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { ErrorMessage } from '../ui/ErrorMessage';
import { Notice } from '../ui/Notice';
import { PageHeader } from '../ui/PageHeader';
import { useAuth } from '../hooks/useAuth';
import { Course, EnrolledStudent } from '../types/course';

export const CourseDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [course, setCourse] = useState<Course | null>(null);
  const [roster, setRoster] = useState<EnrolledStudent[]>([]);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const courseId = Number(id);

  const fetchCourseData = useCallback(async () => {
    if (!courseId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getCourseById(courseId);
      setCourse(data);

      const isOwner = user?.role === 'instructor' && data.instructor_id === user.id;
      const isAdmin = user?.role === 'admin';

      if (isOwner || isAdmin) {
        const students = await getCourseRoster(courseId);
        setRoster(students);
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to load course details.');
      }
    } finally {
      setLoading(false);
    }
  }, [courseId, user]);

  useEffect(() => {
    fetchCourseData();
  }, [fetchCourseData]);

  const handlePublish = async () => {
    if (!course) return;
    setPublishing(true);
    setError(null);
    try {
      const updated = await updateCourse(course.id, { status: 'published' });
      setCourse(updated);
      setNotice('Course published successfully.');
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to publish course.');
      }
    } finally {
      setPublishing(false);
    }
  };

  const isOwner = Boolean(
    user?.role === 'instructor' && course && course.instructor_id === user.id
  );
  const isAdmin = user?.role === 'admin';
  const isStudent = user?.role === 'student';

  return (
    <AppShell>
      <div className="space-y-8 max-w-4xl">
        {error && <ErrorMessage message={error} />}
        {notice && <Notice variant="success">{notice}</Notice>}

        {loading ? (
          <div className="py-12 text-center text-pencil">Loading course details...</div>
        ) : !course ? (
          <div className="py-12 text-center text-pencil">
            Course not found or you do not have permission to view it.
          </div>
        ) : (
          <>
            <PageHeader
              title={course.title}
              description={`Instructed by ${course.instructor_name || 'Staff'}`}
              actions={
                <div className="flex items-center gap-3">
                  {(isOwner || isAdmin) && (
                    <Button as={Link} to={`/courses/${course.id}/edit`} variant="outline" size="sm">
                      Edit course
                    </Button>
                  )}
                  {isOwner && course.status === 'draft' && (
                    <Button
                      type="button"
                      variant="primary"
                      size="sm"
                      onClick={handlePublish}
                      loading={publishing}
                    >
                      Publish course
                    </Button>
                  )}
                  {isStudent && (
                    <EnrollButton
                      courseId={course.id}
                      enrolled={course.enrolled ?? false}
                      onEnrollmentChange={(newEnrolled) => {
                        setCourse((prev) => (prev ? { ...prev, enrolled: newEnrolled } : null));
                        setNotice(
                          newEnrolled
                            ? 'You are now enrolled in this course.'
                            : 'You have unenrolled from this course.'
                        );
                      }}
                    />
                  )}
                </div>
              }
            />

            <div className="flex items-center gap-3">
              <Badge variant={course.status === 'published' ? 'success' : 'neutral'}>
                {course.status === 'published' ? 'Published' : 'Draft'}
              </Badge>
              {isStudent && course.enrolled && <Badge variant="info">Enrolled</Badge>}
            </div>

            <section className="space-y-2">
              <h2 className="text-lg font-semibold text-ink">Description</h2>
              <div className="rounded-control border border-line bg-surface p-6 text-ink whitespace-pre-wrap leading-relaxed">
                {course.description || 'No description provided.'}
              </div>
            </section>

            {(isOwner || isAdmin) && (
              <section className="space-y-4 pt-4 border-t border-line">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-ink">
                    Enrolled students ({roster.length})
                  </h2>
                </div>
                <StudentRosterTable students={roster} />
              </section>
            )}
          </>
        )}
      </div>
    </AppShell>
  );
};
