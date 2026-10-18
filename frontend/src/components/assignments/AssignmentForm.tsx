import React, { useState } from 'react';
import { Assignment, AssignmentCreatePayload } from '../../types/assignment';
import { Button } from '../ui/Button';
import { ErrorMessage } from '../ui/ErrorMessage';
import { TextField } from '../ui/TextField';
import { Textarea } from '../ui/Textarea';

export interface AssignmentFormProps {
  initialData?: Assignment;
  onSubmit: (data: AssignmentCreatePayload) => Promise<void>;
  submitLabel?: string;
  isEditing?: boolean;
}

export const AssignmentForm: React.FC<AssignmentFormProps> = ({
  initialData,
  onSubmit,
  submitLabel = 'Save assignment',
  isEditing = false,
}) => {
  const getInitialLocalDateTime = (iso?: string) => {
    if (!iso) return '';
    const d = new Date(iso);
    if (isNaN(d.getTime())) return '';
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  };

  const [title, setTitle] = useState(initialData?.title ?? '');
  const [description, setDescription] = useState(initialData?.description ?? '');
  const [dueAt, setDueAt] = useState(getInitialLocalDateTime(initialData?.due_at));
  const [maxPoints, setMaxPoints] = useState(initialData?.max_points ?? 100);

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    if (!title.trim()) {
      errors.title = 'Title is required.';
    } else if (title.trim().length < 3 || title.trim().length > 120) {
      errors.title = 'Title must be between 3 and 120 characters.';
    }

    if (!dueAt) {
      errors.dueAt = 'Due date and time are required.';
    } else {
      const parsed = new Date(dueAt);
      if (isNaN(parsed.getTime())) {
        errors.dueAt = 'Please provide a valid date and time.';
      } else if (!isEditing && parsed.getTime() <= Date.now()) {
        errors.dueAt = 'Due date must be in the future.';
      }
    }

    if (maxPoints < 1 || maxPoints > 1000) {
      errors.maxPoints = 'Points must be between 1 and 1000.';
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!validate()) {
      return;
    }

    try {
      setSubmitting(true);
      const parsedDate = new Date(dueAt).toISOString();
      await onSubmit({
        title: title.trim(),
        description: description.trim() ? description.trim() : null,
        due_at: parsedDate,
        max_points: Number(maxPoints),
      });
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Failed to save assignment.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      {formError && <ErrorMessage whatHappened="Could not save assignment." howToFix={formError} />}

      <TextField
        id="assignment-title"
        label="Assignment title"
        required
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        error={fieldErrors.title}
        placeholder="e.g., Problem Set 1: Graph Theory"
        maxLength={120}
      />

      <Textarea
        id="assignment-description"
        label="Description and instructions"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        error={fieldErrors.description}
        placeholder="Provide instructions, requirements, and submission guidelines..."
        rows={6}
        maxLength={2000}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <TextField
          id="assignment-due-at"
          type="datetime-local"
          label="Due date & time"
          required
          value={dueAt}
          onChange={(e) => setDueAt(e.target.value)}
          error={fieldErrors.dueAt}
        />

        <TextField
          id="assignment-max-points"
          type="number"
          label="Maximum points"
          required
          min={1}
          max={1000}
          value={maxPoints}
          onChange={(e) => setMaxPoints(Number(e.target.value))}
          error={fieldErrors.maxPoints}
        />
      </div>

      <div className="flex items-center gap-3 pt-2">
        <Button type="submit" variant="primary" disabled={submitting}>
          {submitting ? 'Saving...' : submitLabel}
        </Button>
      </div>
    </form>
  );
};
