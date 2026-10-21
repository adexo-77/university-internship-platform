import React from 'react';
import { Button } from './Button';
import { ErrorMessage } from './ErrorMessage';

export interface ConfirmModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  confirmVariant?: 'primary' | 'secondary' | 'danger' | 'quiet';
  onClose: () => void;
  onConfirm: () => Promise<void> | void;
  isSubmitting?: boolean;
  error?: string | null;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  title,
  message,
  confirmLabel = 'Confirm',
  confirmVariant = 'danger',
  onClose,
  onConfirm,
  isSubmitting = false,
  error,
}) => {
  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4"
    >
      <div className="w-full max-w-md rounded-control border border-line bg-surface p-6 shadow-card space-y-4">
        <div>
          <h3 id="confirm-modal-title" className="text-lg font-semibold text-ink">
            {title}
          </h3>
          <p className="text-sm text-pencil mt-2">{message}</p>
        </div>

        {error && (
          <ErrorMessage whatHappened={error} howToFix="Please try again or cancel the operation." />
        )}

        <div className="flex justify-end gap-3 pt-2">
          <Button type="button" variant="quiet" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            type="button"
            variant={confirmVariant}
            onClick={onConfirm}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Processing...' : confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
};
