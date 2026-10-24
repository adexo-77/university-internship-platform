import React, { useEffect, useState } from 'react';
import {
  createCourseResource,
  deleteCourseResource,
  getCourseResources,
  updateCourseResource,
} from '../../api/course_resource';
import { CourseResource } from '../../types/course';
import { Button, ConfirmModal, EmptyState, ErrorMessage } from '../ui';
import { CourseResourceFormModal } from './CourseResourceFormModal';

export interface CourseResourcesSectionProps {
  courseId: number;
  isOwner?: boolean;
}

export const CourseResourcesSection: React.FC<CourseResourcesSectionProps> = ({
  courseId,
  isOwner = false,
}) => {
  const [resources, setResources] = useState<CourseResource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [formModalOpen, setFormModalOpen] = useState(false);
  const [editingResource, setEditingResource] = useState<CourseResource | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deletingResource, setDeletingResource] = useState<CourseResource | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const data = await getCourseResources(courseId);
        if (mounted) setResources(data);
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to load course resources.');
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, [courseId]);

  const handleOpenAddModal = () => {
    setEditingResource(null);
    setFormModalOpen(true);
  };

  const handleOpenEditModal = (resource: CourseResource) => {
    setEditingResource(resource);
    setFormModalOpen(true);
  };

  const handleFormSubmit = async (data: {
    title: string;
    url: string;
    description?: string | null;
  }) => {
    setIsSubmitting(true);
    try {
      if (editingResource) {
        const updated = await updateCourseResource(editingResource.id, data);
        setResources((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
      } else {
        const created = await createCourseResource(courseId, data);
        setResources((prev) => [...prev, created]);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenDeleteModal = (resource: CourseResource) => {
    setDeletingResource(resource);
    setDeleteError(null);
    setDeleteModalOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!deletingResource) return;
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await deleteCourseResource(deletingResource.id);
      setResources((prev) => prev.filter((r) => r.id !== deletingResource.id));
      setDeleteModalOpen(false);
      setDeletingResource(null);
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : 'Failed to delete resource.');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <section className="space-y-4 pt-4 border-t border-line" aria-label="Course resources">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-ink">
            Learning resources ({resources.length})
          </h2>
          <p className="text-sm text-pencil">
            Reference links, documentation, and external materials for this course.
          </p>
        </div>
        {isOwner && (
          <Button size="sm" onClick={handleOpenAddModal}>
            Add resource
          </Button>
        )}
      </div>

      {loading ? (
        <div className="py-8 text-center text-sm text-pencil">Loading resources...</div>
      ) : error ? (
        <ErrorMessage whatHappened={error} howToFix="Please refresh the page to retry." />
      ) : resources.length === 0 ? (
        <EmptyState
          title="No learning resources yet"
          description={
            isOwner
              ? 'Add links to syllabus materials, tutorials, or documentation to help your students.'
              : 'The course instructor has not added any learning resources yet.'
          }
          action={
            isOwner ? (
              <Button size="sm" onClick={handleOpenAddModal}>
                Add resource
              </Button>
            ) : undefined
          }
        />
      ) : (
        <ul className="divide-y divide-line rounded-control border border-line bg-surface">
          {resources.map((item) => (
            <li
              key={item.id}
              className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            >
              <div className="space-y-1 min-w-0 flex-1">
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium text-petrol hover:underline text-base inline-flex items-center gap-1.5 break-words"
                >
                  <span>{item.title}</span>
                  <span className="text-xs text-pencil font-normal" aria-hidden="true">
                    ↗
                  </span>
                </a>
                <p className="text-xs text-pencil truncate">{item.url}</p>
                {item.description && (
                  <p className="text-sm text-ink whitespace-pre-wrap mt-1">{item.description}</p>
                )}
              </div>

              {isOwner && (
                <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => handleOpenEditModal(item)}
                  >
                    Edit
                  </Button>
                  <Button
                    type="button"
                    variant="danger"
                    size="sm"
                    onClick={() => handleOpenDeleteModal(item)}
                  >
                    Delete
                  </Button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}

      <CourseResourceFormModal
        isOpen={formModalOpen}
        initialData={editingResource}
        onClose={() => setFormModalOpen(false)}
        onSubmit={handleFormSubmit}
        isSubmitting={isSubmitting}
      />

      <ConfirmModal
        isOpen={deleteModalOpen}
        title="Delete learning resource"
        message={`Are you sure you want to delete "${deletingResource?.title ?? 'this resource'}"? This action cannot be undone.`}
        confirmLabel="Delete resource"
        confirmVariant="danger"
        onClose={() => {
          setDeleteModalOpen(false);
          setDeletingResource(null);
        }}
        onConfirm={handleConfirmDelete}
        isSubmitting={isDeleting}
        error={deleteError}
      />
    </section>
  );
};
