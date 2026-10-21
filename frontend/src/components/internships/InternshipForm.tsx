import React, { useState } from 'react';
import { Internship, InternshipWorkMode } from '../../types/internship';
import { Button } from '../ui/Button';
import { ErrorMessage } from '../ui/ErrorMessage';
import { Select } from '../ui/Select';
import { TextField } from '../ui/TextField';
import { Textarea } from '../ui/Textarea';
import { InternshipDeadlineField } from './InternshipDeadlineField';
import {
  checkRequiredText,
  toLocalDatetimeString,
  validateDeadline,
  WORK_MODE_OPTIONS,
} from '../../lib/internship-rules';

export interface InternshipFormData {
  title: string;
  description: string;
  requirements: string;
  location: string;
  work_mode: InternshipWorkMode;
  duration_weeks?: number | null;
  application_deadline: string;
}

export interface InternshipFormProps {
  initialData?: Partial<Internship>;
  onSubmit: (data: InternshipFormData) => Promise<void>;
  isSubmitting?: boolean;
  isEdit?: boolean;
  error?: string | null;
  onCancel?: () => void;
}

export const InternshipForm: React.FC<InternshipFormProps> = ({
  initialData,
  onSubmit,
  isSubmitting = false,
  isEdit = false,
  error = null,
  onCancel,
}) => {
  const [title, setTitle] = useState(initialData?.title ?? '');
  const [description, setDescription] = useState(initialData?.description ?? '');
  const [requirements, setRequirements] = useState(initialData?.requirements ?? '');
  const [location, setLocation] = useState(initialData?.location ?? '');
  const [workMode, setWorkMode] = useState<InternshipWorkMode>(initialData?.work_mode ?? 'hybrid');
  const [durationWeeks, setDurationWeeks] = useState<string>(
    initialData?.duration_weeks ? String(initialData.duration_weeks) : ''
  );
  const [deadline, setDeadline] = useState(
    toLocalDatetimeString(initialData?.application_deadline)
  );
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    const titleErr = checkRequiredText(title, 'Title', 150);
    if (titleErr) errs.title = titleErr;
    const descErr = checkRequiredText(description, 'Description', 5000);
    if (descErr) errs.description = descErr;
    const reqErr = checkRequiredText(requirements, 'Requirements', 5000, true);
    if (reqErr) errs.requirements = reqErr;
    const locErr = checkRequiredText(location, 'Location', 150);
    if (locErr) errs.location = locErr;

    if (durationWeeks.trim()) {
      const parsed = parseInt(durationWeeks, 10);
      if (isNaN(parsed) || parsed < 1 || parsed > 104) {
        errs.durationWeeks = 'Duration must be between 1 and 104 weeks.';
      }
    }
    const dlErr = validateDeadline(deadline, isEdit);
    if (dlErr) errs.deadline = dlErr;

    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    await onSubmit({
      title: title.trim(),
      description: description.trim(),
      requirements: requirements.trim(),
      location: location.trim(),
      work_mode: workMode,
      duration_weeks: durationWeeks.trim() ? parseInt(durationWeeks, 10) : null,
      application_deadline: new Date(deadline).toISOString(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl" noValidate>
      {error && <ErrorMessage whatHappened="Could not save internship." howToFix={error} />}

      <TextField
        id="internship-title"
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        error={fieldErrors.title}
        required
        placeholder="e.g. Software Engineering Intern"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <TextField
          id="internship-location"
          label="Location"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          error={fieldErrors.location}
          required
          placeholder="e.g. Nairobi, Kenya"
        />

        <Select
          id="internship-work-mode"
          label="Work mode"
          value={workMode}
          onChange={(e) => setWorkMode(e.target.value as InternshipWorkMode)}
          options={WORK_MODE_OPTIONS}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <TextField
          id="internship-duration"
          label="Duration (weeks)"
          type="number"
          min="1"
          max="104"
          value={durationWeeks}
          onChange={(e) => setDurationWeeks(e.target.value)}
          error={fieldErrors.durationWeeks}
          placeholder="e.g. 12"
        />

        <InternshipDeadlineField
          value={deadline}
          onChange={setDeadline}
          error={fieldErrors.deadline}
          status={initialData?.status}
          reviewedAt={initialData?.reviewed_at}
          required
        />
      </div>

      <Textarea
        id="internship-description"
        label="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        error={fieldErrors.description}
        required
        rows={4}
        placeholder="Describe the internship duties and team..."
      />

      <Textarea
        id="internship-requirements"
        label="Requirements"
        value={requirements}
        onChange={(e) => setRequirements(e.target.value)}
        error={fieldErrors.requirements}
        required
        rows={4}
        placeholder="Key skills, qualifications, or technologies..."
      />

      <p className="text-sm text-pencil">
        Postings are reviewed by an admin before students can see them.
      </p>

      <div className="flex items-center gap-3 pt-2">
        <Button type="submit" variant="primary" disabled={isSubmitting}>
          {isSubmitting ? 'Saving...' : isEdit ? 'Save changes' : 'Create internship'}
        </Button>
        {onCancel && (
          <Button type="button" variant="quiet" onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
};
