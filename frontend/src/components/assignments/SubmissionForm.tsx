import React, { useState } from 'react';
import { Submission, SubmissionSubmitPayload } from '../../types/assignment';
import { Button } from '../ui/Button';
import { ErrorMessage } from '../ui/ErrorMessage';
import { Notice } from '../ui/Notice';
import { TextField } from '../ui/TextField';
import { Textarea } from '../ui/Textarea';

export interface SubmissionFormProps {
  submission?: Submission | null;
  maxPoints: number;
  onSubmit: (data: SubmissionSubmitPayload) => Promise<void>;
}

export const SubmissionForm: React.FC<SubmissionFormProps> = ({
  submission,
  maxPoints,
  onSubmit,
}) => {
  const isGraded = submission?.graded_at != null || submission?.grade != null;

  const [content, setContent] = useState(submission?.content ?? '');
  const [linkUrl, setLinkUrl] = useState(submission?.link_url ?? '');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    if (!content.trim()) {
      errors.content = 'Submission content cannot be empty.';
    } else if (content.length > 10000) {
      errors.content = 'Submission content cannot exceed 10,000 characters.';
    }

    if (linkUrl.trim()) {
      const stripped = linkUrl.trim();
      if (!stripped.startsWith('http://') && !stripped.startsWith('https://')) {
        errors.linkUrl = 'Link must start with http:// or https://.';
      }
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isGraded) return;
    setFormError(null);

    if (!validate()) {
      return;
    }

    try {
      setSubmitting(true);
      await onSubmit({
        content: content.trim(),
        link_url: linkUrl.trim() ? linkUrl.trim() : null,
      });
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Failed to submit work.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {isGraded && (
        <div className="space-y-4">
          <Notice variant="info">
            This submission has been graded and is locked from further edits.
          </Notice>
          <div className="rounded-control border border-line bg-surface p-6 space-y-3">
            <div className="flex items-center justify-between border-b border-line pb-3">
              <span className="text-sm font-semibold text-ink">Grade received</span>
              <span className="text-lg font-bold text-navy">
                {submission.grade} / {maxPoints}
              </span>
            </div>
            {submission.feedback && (
              <div className="space-y-1">
                <span className="text-xs font-medium text-pencil uppercase tracking-wider">
                  Instructor feedback
                </span>
                <p className="text-sm text-ink whitespace-pre-wrap">{submission.feedback}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {formError && (
        <ErrorMessage whatHappened="Could not submit assignment." howToFix={formError} />
      )}

      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <Textarea
          id="submission-content"
          label="Your work"
          required
          disabled={isGraded}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          error={fieldErrors.content}
          placeholder="Paste or write your coursework response here..."
          rows={8}
          maxLength={10000}
        />

        <TextField
          id="submission-link-url"
          label="Optional repository or artifact link"
          disabled={isGraded}
          value={linkUrl}
          onChange={(e) => setLinkUrl(e.target.value)}
          error={fieldErrors.linkUrl}
          placeholder="https://github.com/..."
          maxLength={2048}
        />

        {!isGraded && (
          <div className="flex items-center gap-3 pt-2">
            <Button type="submit" variant="primary" disabled={submitting}>
              {submitting
                ? 'Submitting...'
                : submission
                  ? 'Update submission'
                  : 'Submit assignment'}
            </Button>
          </div>
        )}
      </form>
    </div>
  );
};
