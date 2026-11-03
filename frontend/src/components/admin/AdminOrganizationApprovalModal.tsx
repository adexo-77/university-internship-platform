import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { AdminOrganizationItem } from '../../types/admin';
import { ApprovalStatus } from '../../types/profile';
import { Button, ErrorMessage, IconButton, Textarea } from '../ui';

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

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !isSubmitting) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isSubmitting, onClose]);

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
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-ink/40 p-0 sm:p-4 overflow-y-auto"
    >
      <div className="w-full max-w-md max-h-[92vh] sm:max-h-[90vh] overflow-y-auto rounded-t-xl sm:rounded-control border border-line bg-surface p-4 sm:p-6 shadow-card space-y-4">
        <div className="flex items-start justify-between gap-4">
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
          <IconButton
            aria-label="Close dialog"
            icon={<X className="h-5 w-5" />}
            onClick={onClose}
            disabled={isSubmitting}
          />
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

          <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="quiet"
              onClick={onClose}
              disabled={isSubmitting}
              className="w-full sm:w-auto"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant={isApprove ? 'primary' : 'danger'}
              disabled={isSubmitting}
              className="w-full sm:w-auto"
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
