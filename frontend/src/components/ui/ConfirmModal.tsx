import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { Button } from './Button';
import { ErrorMessage } from './ErrorMessage';
import { IconButton } from './IconButton';

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

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-modal-title"
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-ink/40 p-0 sm:p-4 overflow-y-auto"
    >
      <div className="w-full max-w-md max-h-[92vh] sm:max-h-[90vh] overflow-y-auto rounded-t-xl sm:rounded-control border border-line bg-surface p-4 sm:p-6 shadow-card space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 id="confirm-modal-title" className="text-lg font-semibold text-ink">
              {title}
            </h3>
            <p className="text-sm text-pencil mt-2">{message}</p>
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
            type="button"
            variant={confirmVariant}
            onClick={onConfirm}
            disabled={isSubmitting}
            className="w-full sm:w-auto"
          >
            {isSubmitting ? 'Processing...' : confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
};
