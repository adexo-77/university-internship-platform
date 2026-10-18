import React, { useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { createCourseAssignment } from '../api/assignment';
import { AssignmentForm } from '../components/assignments/AssignmentForm';
import { AppShell } from '../components/layout/AppShell';
import { PageHeader } from '../components/ui/PageHeader';
import { usePageTitle } from '../hooks/usePageTitle';
import { AssignmentCreatePayload } from '../types/assignment';

export const AssignmentCreatePage: React.FC = () => {
  usePageTitle('Create assignment');
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const numericCourseId = Number(courseId);

  const handleSubmit = async (data: AssignmentCreatePayload) => {
    if (isNaN(numericCourseId)) {
      setError('Invalid course ID.');
      return;
    }
    await createCourseAssignment(numericCourseId, data);
    navigate(`/courses/${numericCourseId}`);
  };

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto space-y-6">
        <PageHeader
          title="Create assignment"
          description="Add a new coursework assignment for students enrolled in this course."
          actions={
            <Link
              to={`/courses/${numericCourseId}`}
              className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-3 py-1.5 text-xs bg-surface text-ink border-line hover:bg-chalk"
            >
              Back to course
            </Link>
          }
        />

        {error && (
          <div className="rounded-control border border-brick bg-brick-tint/20 p-4 text-sm text-brick">
            {error}
          </div>
        )}

        <div className="rounded-control border border-line bg-surface p-6 shadow-subtle">
          <AssignmentForm onSubmit={handleSubmit} submitLabel="Create assignment" />
        </div>
      </div>
    </AppShell>
  );
};
