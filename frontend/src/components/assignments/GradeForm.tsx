import React, { useState } from 'react';
import { Submission, SubmissionGradePayload } from '../../types/assignment';
import { Button } from '../ui/Button';
import { ErrorMessage } from '../ui/ErrorMessage';
import { TextField } from '../ui/TextField';
import { Textarea } from '../ui/Textarea';

export interface GradeFormProps {
  submission: Submission;
  maxPoints: number;
  onSubmit: (data: SubmissionGradePayload) => Promise<void>;
}

export const GradeForm: React.FC<GradeFormProps> = ({ submission, maxPoints, onSubmit }) => {
  const [grade, setGrade] = useState<string>(
    submission.grade !== null && submission.grade !== undefined ? String(submission.grade) : ''
  );
  const [feedback, setFeedback] = useState<string>(submission.feedback ?? '');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    if (grade.trim() === '') {
      errors.grade = 'Grade is required.';
    } else {
      const num = Number(grade);
      if (isNaN(num) || num < 0 || num > maxPoints) {
        errors.grade = `Grade must be a number between 0 and ${maxPoints}.`;
      }
    }

    if (feedback.length > 2000) {
      errors.feedback = 'Feedback cannot exceed 2000 characters.';
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
      await onSubmit({
        grade: Number(grade),
        feedback: feedback.trim() ? feedback.trim() : null,
      });
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Failed to save grade.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      {formError && <ErrorMessage whatHappened="Could not submit grade." howToFix={formError} />}

      <div className="space-y-4 rounded-control border border-line bg-surface p-6">
        <h3 className="text-base font-semibold text-ink">Student submission</h3>
        <div className="rounded-control border border-line bg-chalk p-4 text-sm text-ink whitespace-pre-wrap font-mono">
          {submission.content}
        </div>
        {submission.link_url && (
          <div className="flex items-center gap-2 pt-2 text-sm">
            <span className="font-medium text-pencil">Artifact link:</span>
            <a
              href={submission.link_url}
              target="_blank"
              rel="noreferrer"
              className="text-navy hover:underline break-all"
            >
              {submission.link_url}
            </a>
          </div>
        )}
      </div>

      <div className="space-y-4">
        <TextField
          id="grade-input"
          type="number"
          label={`Grade (out of ${maxPoints})`}
          required
          min={0}
          max={maxPoints}
          value={grade}
          onChange={(e) => setGrade(e.target.value)}
          error={fieldErrors.grade}
          placeholder={`0 - ${maxPoints}`}
        />

        <Textarea
          id="feedback-input"
          label="Feedback (optional)"
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          error={fieldErrors.feedback}
          placeholder="Constructive feedback for the student..."
          rows={5}
          maxLength={2000}
        />
      </div>

      <div className="flex items-center gap-3 pt-2">
        <Button type="submit" variant="primary" disabled={submitting}>
          {submitting ? 'Saving grade...' : 'Save grade'}
        </Button>
      </div>
    </form>
  );
};
