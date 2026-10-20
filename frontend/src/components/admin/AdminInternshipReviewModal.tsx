import React, { useState } from 'react';
import { Internship } from '../../types/internship';
import { formatDate } from '../../lib/dates';
import { Button, ErrorMessage, Notice, Textarea } from '../ui';
import { InternshipStatusBadge } from '../internships/InternshipStatusBadge';

export interface AdminInternshipReviewModalProps {
  internship: Internship | null;
  isOpen: boolean;
  onClose: () => void;
  onReview: (decision: 'approved' | 'rejected', reviewNote?: string) => Promise<void>;
  isSubmitting: boolean;
  error?: string | null;
}

export const AdminInternshipReviewModal: React.FC<AdminInternshipReviewModalProps> = ({
  internship,
  isOpen,
  onClose,
  onReview,
  isSubmitting,
  error,
}) => {
  const [note, setNote] = useState('');
  const [noteError, setNoteError] = useState('');

  if (!isOpen || !internship) return null;

  const handleApprove = async () => {
    setNoteError('');
    await onReview('approved', note.trim() || undefined);
  };

  const handleReject = async () => {
    setNoteError('');
    const trimmed = note.trim();
    if (!trimmed) {
      setNoteError('Review note is required when rejecting a posting.');
      return;
    }
    if (trimmed.length > 500) {
      setNoteError('Review note cannot exceed 500 characters.');
      return;
    }
    await onReview('rejected', trimmed);
  };

  const handleTakedown = async () => {
    setNoteError('');
    const trimmed = note.trim();
    if (!trimmed) {
      setNoteError('Review note is required to take down an open posting.');
      return;
    }
    if (trimmed.length > 500) {
      setNoteError('Review note cannot exceed 500 characters.');
      return;
    }
    if (
      !window.confirm(
        'Take down this open internship posting? It will be removed from student views.'
      )
    ) {
      return;
    }
    await onReview('rejected', trimmed);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="review-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4 overflow-y-auto"
    >
      <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-control border border-line bg-surface p-6 shadow-card space-y-4">
        <div className="flex items-start justify-between gap-4 border-b border-line pb-4">
          <div>
            <h3 id="review-modal-title" className="text-xl font-semibold text-ink">
              {internship.title}
            </h3>
            <p className="text-sm text-pencil mt-1">
              {internship.organization_name ?? 'Organization'} &bull; {internship.location} &bull;{' '}
              <span className="capitalize">{internship.work_mode}</span>
            </p>
          </div>
          <InternshipStatusBadge status={internship.status} />
        </div>

        {error && (
          <ErrorMessage whatHappened={error} howToFix="Please try again or cancel the operation." />
        )}

        <div className="grid grid-cols-2 gap-3 text-sm p-3 bg-surface rounded border border-line">
          <div>
            <span className="text-pencil block">Duration</span>
            <span className="font-medium text-ink">
              {internship.duration_weeks ? `${internship.duration_weeks} weeks` : 'Flexible'}
            </span>
          </div>
          <div>
            <span className="text-pencil block">Application deadline</span>
            <span className="font-medium text-ink">
              {formatDate(internship.application_deadline)}
            </span>
          </div>
        </div>

        <div className="space-y-2 text-sm">
          <h4 className="font-semibold text-ink">Description</h4>
          <p className="text-ink whitespace-pre-line leading-relaxed">{internship.description}</p>
        </div>

        <div className="space-y-2 text-sm">
          <h4 className="font-semibold text-ink">Requirements</h4>
          <p className="text-ink whitespace-pre-line leading-relaxed">{internship.requirements}</p>
        </div>

        {internship.review_note && (
          <Notice variant="info" title="Existing review note">
            {internship.review_note}
          </Notice>
        )}

        {internship.status === 'pending_review' && (
          <div className="pt-2 space-y-4 border-t border-line">
            <Textarea
              id="admin-review-note"
              label="Review note"
              helperText="Required when rejecting. Optional when approving. Max 500 characters."
              value={note}
              onChange={(e) => {
                setNote(e.target.value);
                if (noteError) setNoteError('');
              }}
              error={noteError}
              rows={3}
              placeholder="Provide feedback on the posting..."
              disabled={isSubmitting}
            />
            <div className="flex justify-end gap-3">
              <Button type="button" variant="quiet" onClick={onClose} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="button" variant="danger" onClick={handleReject} disabled={isSubmitting}>
                {isSubmitting ? 'Submitting...' : 'Reject'}
              </Button>
              <Button
                type="button"
                variant="primary"
                onClick={handleApprove}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : 'Approve'}
              </Button>
            </div>
          </div>
        )}

        {internship.status === 'open' && (
          <div className="pt-2 space-y-4 border-t border-line">
            <Textarea
              id="admin-takedown-note"
              label="Takedown reason"
              helperText="Required. Explain why this open posting is being taken down."
              value={note}
              onChange={(e) => {
                setNote(e.target.value);
                if (noteError) setNoteError('');
              }}
              error={noteError}
              rows={3}
              placeholder="e.g. Terms violation or invalid role details."
              disabled={isSubmitting}
            />
            <div className="flex justify-end gap-3">
              <Button type="button" variant="quiet" onClick={onClose} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button
                type="button"
                variant="danger"
                onClick={handleTakedown}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Taking down...' : 'Take down'}
              </Button>
            </div>
          </div>
        )}

        {internship.status !== 'pending_review' && internship.status !== 'open' && (
          <div className="pt-2 flex justify-end border-t border-line">
            <Button type="button" variant="secondary" onClick={onClose}>
              Close
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};
