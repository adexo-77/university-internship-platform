import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createCourse } from '../api/course';
import { CourseForm, CourseFormData } from '../components/courses/CourseForm';
import { AppShell } from '../components/layout/AppShell';
import { PageHeader } from '../ui/PageHeader';

export const CourseCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: CourseFormData) => {
    setSubmitting(true);
    setError(null);
    try {
      const course = await createCourse({
        title: data.title,
        description: data.description,
        status: data.status,
      });
      navigate(`/courses/${course.id}`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to create course.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <PageHeader
          title="New course"
          description="Create a course syllabus and manage student enrollment."
        />

        <CourseForm
          onSubmit={handleSubmit}
          isSubmitting={submitting}
          error={error}
          onCancel={() => navigate('/my-courses')}
        />
      </div>
    </AppShell>
  );
};
