import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { getAssignment, updateAssignment } from '../api/assignment';
import { AssignmentForm } from '../components/assignments/AssignmentForm';
import { AppShell } from '../components/layout/AppShell';
import { PageHeader } from '../components/ui/PageHeader';
import { usePageTitle } from '../hooks/usePageTitle';
import { Assignment, AssignmentCreatePayload } from '../types/assignment';

export const AssignmentEditPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [assignment, setAssignment] = useState<Assignment | null>(null);
  usePageTitle(assignment ? `Edit ${assignment.title}` : 'Edit assignment');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const numericId = Number(id);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        setLoading(true);
        const data = await getAssignment(numericId);
        if (mounted) setAssignment(data);
      } catch (err) {
        if (mounted) setError(err instanceof Error ? err.message : 'Failed to load assignment.');
      } finally {
        if (mounted) setLoading(false);
      }
    }
    if (!isNaN(numericId)) {
      load();
    }
    return () => {
      mounted = false;
    };
  }, [numericId]);

  const handleSubmit = async (data: AssignmentCreatePayload) => {
    await updateAssignment(numericId, data);
    navigate(`/assignments/${numericId}`);
  };

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto space-y-6">
        <PageHeader
          title="Edit assignment"
          description={assignment ? `Editing ${assignment.title}` : 'Update assignment parameters.'}
          actions={
            <Link
              to={`/assignments/${numericId}`}
              className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-3 py-1.5 text-xs bg-surface text-ink border-line hover:bg-chalk"
            >
              Cancel
            </Link>
          }
        />

        {loading ? (
          <div className="py-12 text-center text-pencil">Loading assignment...</div>
        ) : error ? (
          <div className="rounded-control border border-brick bg-brick-tint/20 p-4 text-sm text-brick">
            {error}
          </div>
        ) : assignment ? (
          <div className="rounded-control border border-line bg-surface p-6 shadow-subtle">
            <AssignmentForm
              initialData={assignment}
              onSubmit={handleSubmit}
              submitLabel="Save changes"
              isEditing={true}
            />
          </div>
        ) : null}
      </div>
    </AppShell>
  );
};
