import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { ErrorMessage } from '../ui/ErrorMessage';
import { Textarea } from '../ui/Textarea';

export interface ApplyFormProps {
  onSubmit: (coverLetter: string) => Promise<void>;
  isSubmitting?: boolean;
  error?: string | null;
}

export const ApplyForm: React.FC<ApplyFormProps> = ({
  onSubmit,
  isSubmitting = false,
  error = null,
}) => {
  const [coverLetter, setCoverLetter] = useState('');
  const [fieldError, setFieldError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = coverLetter.trim();
    if (!trimmed) {
      setFieldError('Cover letter is required.');
      return;
    }
    if (trimmed.length > 5000) {
      setFieldError('Cover letter cannot exceed 5000 characters.');
      return;
    }
    setFieldError(null);
    await onSubmit(trimmed);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-xl" noValidate>
      {error && <ErrorMessage whatHappened="Could not submit application." howToFix={error} />}

      <Textarea
        id="apply-cover-letter"
        label="Cover letter"
        value={coverLetter}
        onChange={(e) => {
          setCoverLetter(e.target.value);
          if (fieldError) setFieldError(null);
        }}
        error={fieldError ?? undefined}
        required
        rows={6}
        placeholder="Explain why you are interested in this position and how your skills match the requirements..."
      />

      <div className="flex justify-between items-center pt-1">
        <span className="text-xs text-pencil">{coverLetter.trim().length} / 5000 characters</span>
        <Button type="submit" variant="primary" disabled={isSubmitting}>
          {isSubmitting ? 'Submitting...' : 'Submit application'}
        </Button>
      </div>
    </form>
  );
};
