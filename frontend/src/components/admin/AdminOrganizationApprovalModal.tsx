import React, { useState } from 'react';
import { AdminOrganizationItem } from '../../types/admin';
import { ApprovalStatus } from '../../types/profile';
import { Button, ErrorMessage, Textarea } from '../ui';

export interface AdminOrganizationApprovalModalProps {
  org: AdminOrganizationItem | null;
  targetStatus: ApprovalStatus | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (status: ApprovalStatus, note: string) => Promise<void>;
  isSubmitting: boolean;
  error?: string | null;
}

export const AdminOrganizationApprovalModal: React.FC<AdminOrganizationApprovalModalProps> = ({
  org,
  targetStatus,
  isOpen,
  onClose,
  onConfirm,
  isSubmitting,
  error,
}) => {
  const [note, setNote] = useState('');
  const [noteError, setNoteError] = useState('');

  if (!isOpen || !org || !targetStatus) return null;

  const isApprove = targetStatus === 'approved';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setNoteError('');

    if (note.trim().length > 500) {
      setNoteError('Review note cannot exceed 500 characters.');
      return;
    }

    await onConfirm(targetStatus, note.trim());
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="approval-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4"
    >
      <div className="w-full max-w-md rounded-control border border-line bg-surface p-6 shadow-card space-y-4">
        <div>
          <h3 id="approval-modal-title" className="text-lg font-semibold text-ink">
            {isApprove ? 'Approve organization' : 'Reject organization'}
          </h3>
          <p className="text-sm text-pencil mt-2">
            {isApprove
              ? `Approve ${org.organization_name}? Once approved, this organization will be permitted to publish internship postings for students.`
              : `Reject ${org.organization_name}? Rejected organizations cannot publish internship postings.`}
          </p>
        </div>

        {error && (
          <ErrorMessage whatHappened={error} howToFix="Please try again or cancel the operation." />
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Textarea
            id="admin-approval-note"
            label="Review note (optional)"
            helperText="Maximum 500 characters. Will be visible to the organization."
            value={note}
            onChange={(e) => {
              setNote(e.target.value);
              if (noteError) setNoteError('');
            }}
            error={noteError}
            rows={3}
            placeholder={
              isApprove
                ? 'e.g. Verified corporate registration and identity.'
                : 'e.g. Missing valid business registration documents.'
            }
            disabled={isSubmitting}
          />

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="quiet" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant={isApprove ? 'primary' : 'danger'}
              disabled={isSubmitting}
            >
              {isSubmitting
                ? isApprove
                  ? 'Approving...'
                  : 'Rejecting...'
                : isApprove
                  ? 'Approve'
                  : 'Reject'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
