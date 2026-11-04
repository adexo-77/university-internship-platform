import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { deleteAssignment, getAssignment, updateAssignment } from '../api/assignment';
import { AssignmentForm } from '../components/assignments/AssignmentForm';
import { AppShell } from '../components/layout/AppShell';
import { BackLink, Button, ConfirmModal, ErrorMessage, PageHeader } from '../components/ui';
import { usePageTitle } from '../hooks/usePageTitle';
import { Assignment, AssignmentCreatePayload } from '../types/assignment';

export const AssignmentEditPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [assignment, setAssignment] = useState<Assignment | null>(null);
  usePageTitle(assignment ? `Edit ${assignment.title}` : 'Edit assignment');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

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

  const handleDelete = async () => {
    if (!assignment) return;
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await deleteAssignment(numericId);
      navigate(`/courses/${assignment.course_id}`);
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : 'Failed to delete assignment.');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto space-y-6">
        <BackLink />
        <PageHeader
          title="Edit assignment"
          description={assignment ? `Editing ${assignment.title}` : 'Update assignment parameters.'}
          actions={
            <div className="flex items-center gap-3">
              {assignment?.course_id && (
                <Link
                  to={`/courses/${assignment.course_id}`}
                  className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-3 py-1.5 text-xs bg-surface text-ink border-line hover:bg-chalk"
                >
                  Back to course
                </Link>
              )}
              <Link
                to={`/assignments/${numericId}`}
                className="inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-control border px-3 py-1.5 text-xs bg-surface text-ink border-line hover:bg-chalk"
              >
                Cancel
              </Link>
            </div>
          }
        />

        {deleteError && (
          <ErrorMessage whatHappened="Could not delete assignment." howToFix={deleteError} />
        )}

        {loading ? (
          <div className="py-12 text-center text-pencil">Loading assignment...</div>
        ) : error ? (
          <div className="rounded-control border border-brick bg-surface p-4 text-sm text-brick">
            {error}
          </div>
        ) : assignment ? (
          <div className="space-y-6">
            <div className="rounded-control border border-line bg-surface p-6 shadow-subtle">
              <AssignmentForm
                initialData={assignment}
                onSubmit={handleSubmit}
                submitLabel="Save changes"
                isEditing={true}
              />
            </div>

            <div className="rounded-control border border-line bg-surface p-6 space-y-3">
              <h3 className="text-sm font-semibold text-ink">Danger zone</h3>
              <p className="text-xs text-pencil">
                Delete this assignment permanently. Assignments with existing student submissions
                cannot be deleted.
              </p>
              <Button
                type="button"
                variant="danger"
                size="sm"
                onClick={() => setIsDeleteOpen(true)}
              >
                Delete assignment
              </Button>
            </div>

            <ConfirmModal
              isOpen={isDeleteOpen}
              title="Delete assignment"
              message={`Are you sure you want to delete "${assignment.title}"? This action cannot be undone.`}
              confirmLabel="Delete assignment"
              confirmVariant="danger"
              isSubmitting={isDeleting}
              error={deleteError}
              onClose={() => {
                if (!isDeleting) setIsDeleteOpen(false);
              }}
              onConfirm={handleDelete}
            />
          </div>
        ) : null}
      </div>
    </AppShell>
  );
};
