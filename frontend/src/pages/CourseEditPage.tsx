import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getCourseById, updateCourse } from '../api/course';
import { CourseForm, CourseFormData } from '../components/courses/CourseForm';
import { AppShell } from '../components/layout/AppShell';
import { ErrorMessage } from '../ui/ErrorMessage';
import { PageHeader } from '../ui/PageHeader';
import { Course } from '../types/course';

export const CourseEditPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchCourse = async () => {
      if (!id) return;
      try {
        const data = await getCourseById(Number(id));
        if (isMounted) setCourse(data);
      } catch (err: unknown) {
        if (isMounted) {
          if (err instanceof Error) {
            setError(err.message);
          } else {
            setError('Failed to load course details.');
          }
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchCourse();

    return () => {
      isMounted = false;
    };
  }, [id]);

  const handleSubmit = async (data: CourseFormData) => {
    if (!id) return;
    setSubmitting(true);
    setError(null);
    try {
      await updateCourse(Number(id), {
        title: data.title,
        description: data.description,
        status: data.status,
      });
      navigate(`/courses/${id}`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to update course.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <PageHeader
          title="Edit course"
          description={course ? `Editing "${course.title}"` : 'Update course details and syllabus.'}
        />

        {error && <ErrorMessage message={error} />}

        {loading ? (
          <div className="py-12 text-center text-pencil">Loading course...</div>
        ) : course ? (
          <CourseForm
            initialData={course}
            onSubmit={handleSubmit}
            isSubmitting={submitting}
            isEdit={true}
            error={error}
            onCancel={() => navigate(`/courses/${id}`)}
          />
        ) : (
          <div className="text-pencil">Course not found.</div>
        )}
      </div>
    </AppShell>
  );
};
