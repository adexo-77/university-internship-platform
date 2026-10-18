import React, { useState } from 'react';
import { Course, CourseStatus } from '../../types/course';
import { Button } from '../ui/Button';
import { ErrorMessage } from '../ui/ErrorMessage';
import { Select } from '../ui/Select';
import { TextField } from '../ui/TextField';
import { Textarea } from '../ui/Textarea';

export interface CourseFormData {
  title: string;
  description?: string;
  status?: CourseStatus;
}

export interface CourseFormProps {
  initialData?: Partial<Course>;
  onSubmit: (data: CourseFormData) => Promise<void>;
  isSubmitting?: boolean;
  isEdit?: boolean;
  error?: string | null;
  onCancel?: () => void;
}

export const CourseForm: React.FC<CourseFormProps> = ({
  initialData,
  onSubmit,
  isSubmitting = false,
  isEdit = false,
  error = null,
  onCancel,
}) => {
  const [title, setTitle] = useState(initialData?.title ?? '');
  const [description, setDescription] = useState(initialData?.description ?? '');
  const [status, setStatus] = useState<CourseStatus>(initialData?.status ?? 'draft');
  const [fieldErrors, setFieldErrors] = useState<{ title?: string; description?: string }>({});

  const validate = (): boolean => {
    const errs: { title?: string; description?: string } = {};

    const trimmedTitle = title.trim();
    if (!trimmedTitle) {
      errs.title = 'Title is required.';
    } else if (trimmedTitle.length < 3) {
      errs.title = 'Title must be at least 3 characters.';
    } else if (trimmedTitle.length > 120) {
      errs.title = 'Title cannot exceed 120 characters.';
    }

    if (description && description.length > 2000) {
      errs.description = 'Description cannot exceed 2000 characters.';
    }

    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    await onSubmit({
      title: title.trim(),
      description: description.trim() || undefined,
      status,
    });
  };

  const isPublishedLocked = isEdit && initialData?.status === 'published';

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-6 max-w-xl">
      {error && (
        <ErrorMessage
          whatHappened={error}
          howToFix="Please check your input values and try again."
        />
      )}

      <TextField
        id="course-title"
        label="Course title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        error={fieldErrors.title}
        required
        placeholder="e.g. Distributed Systems"
        maxLength={120}
      />

      <Textarea
        id="course-description"
        label="Course description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        error={fieldErrors.description}
        placeholder="Provide an overview of the syllabus, prerequisites, and learning goals."
        rows={5}
        maxLength={2000}
      />

      {isPublishedLocked ? (
        <div className="text-sm text-pencil">
          <span className="font-medium text-ink">Status:</span> Published (published courses cannot
          be reverted to draft)
        </div>
      ) : (
        <Select
          id="course-status"
          label="Publication status"
          value={status}
          onChange={(e) => setStatus(e.target.value as CourseStatus)}
          options={[
            { value: 'draft', label: 'Draft' },
            { value: 'published', label: 'Published' },
          ]}
        />
      )}

      <div className="flex items-center gap-3 pt-2">
        <Button type="submit" variant="primary" disabled={isSubmitting}>
          {isSubmitting
            ? isEdit
              ? 'Saving...'
              : 'Creating...'
            : isEdit
              ? 'Save changes'
              : 'Create course'}
        </Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
};
