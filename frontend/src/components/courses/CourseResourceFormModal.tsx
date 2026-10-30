import React, { useEffect, useState } from 'react';
import { CourseResource } from '../../types/course';
import { Button, ErrorMessage, TextField, Textarea } from '../ui';

export interface CourseResourceFormModalProps {
  isOpen: boolean;
  initialData?: CourseResource | null;
  onClose: () => void;
  onSubmit: (data: { title: string; url: string; description?: string | null }) => Promise<void>;
  isSubmitting?: boolean;
}

export const CourseResourceFormModal: React.FC<CourseResourceFormModalProps> = ({
  isOpen,
  initialData,
  onClose,
  onSubmit,
  isSubmitting = false,
}) => {
  const [title, setTitle] = useState('');
  const [url, setUrl] = useState('');
  const [description, setDescription] = useState('');
  const [errors, setErrors] = useState<{ title?: string; url?: string; description?: string }>({});
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setTitle(initialData.title);
      setUrl(initialData.url);
      setDescription(initialData.description ?? '');
    } else {
      setTitle('');
      setUrl('');
      setDescription('');
    }
    setErrors({});
    setSubmitError(null);
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const validate = (): boolean => {
    const nextErrors: { title?: string; url?: string; description?: string } = {};
    const trimmedTitle = title.trim();
    const trimmedUrl = url.trim();

    if (!trimmedTitle) {
      nextErrors.title = 'Title is required.';
    } else if (trimmedTitle.length > 120) {
      nextErrors.title = 'Title cannot exceed 120 characters.';
    }

    if (!trimmedUrl) {
      nextErrors.url = 'URL is required.';
    } else if (trimmedUrl.length > 500) {
      nextErrors.url = 'URL cannot exceed 500 characters.';
    } else {
      const lower = trimmedUrl.toLowerCase();
      if (lower.startsWith('javascript:') || lower.startsWith('data:')) {
        nextErrors.url = 'Dangerous URL schemes like javascript: or data: are not allowed.';
      } else if (!lower.startsWith('http://') && !lower.startsWith('https://')) {
        nextErrors.url = 'URL must start with http:// or https://';
      } else {
        try {
          const parsed = new URL(trimmedUrl);
          if (!parsed.hostname) {
            nextErrors.url = 'URL must contain a valid hostname.';
          }
        } catch {
          nextErrors.url = 'Please enter a valid URL.';
        }
      }
    }

    if (description.length > 500) {
      nextErrors.description = 'Description cannot exceed 500 characters.';
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    if (!validate()) return;

    try {
      await onSubmit({
        title: title.trim(),
        url: url.trim(),
        description: description.trim() || null,
      });
      onClose();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to save resource.');
    }
  };

  const isEditing = Boolean(initialData);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="resource-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4"
    >
      <div className="w-full max-w-lg rounded-control border border-line bg-surface p-6 shadow-card space-y-4">
        <div>
          <h3 id="resource-modal-title" className="text-lg font-semibold text-ink">
            {isEditing ? 'Edit learning resource' : 'Add learning resource'}
          </h3>
          <p className="text-sm text-pencil mt-1">
            Provide a title, an HTTP/HTTPS link, and an optional description.
          </p>
        </div>

        {submitError && (
          <ErrorMessage
            whatHappened={submitError}
            howToFix="Please correct any issues and retry."
          />
        )}

        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <TextField
            id="resource-title"
            label="Resource title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            error={errors.title}
            placeholder="e.g., PostgreSQL Documentation"
            disabled={isSubmitting}
            required
          />

          <TextField
            id="resource-url"
            label="Resource URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            error={errors.url}
            placeholder="https://www.postgresql.org/docs/"
            disabled={isSubmitting}
            required
          />

          <Textarea
            id="resource-description"
            label="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            error={errors.description}
            placeholder="Short description of this reference material..."
            disabled={isSubmitting}
            rows={3}
          />

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="quiet" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : isEditing ? 'Save changes' : 'Add resource'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
