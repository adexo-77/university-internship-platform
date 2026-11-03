import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { AdminUser } from '../../types/admin';
import { Button, ErrorMessage, IconButton } from '../ui';

export interface AdminUserStatusModalProps {
  user: AdminUser | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  isSubmitting: boolean;
  error?: string | null;
}

export const AdminUserStatusModal: React.FC<AdminUserStatusModalProps> = ({
  user,
  isOpen,
  onClose,
  onConfirm,
  isSubmitting,
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

  if (!isOpen || !user) return null;

  const isDeactivating = user.is_active;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="status-modal-title"
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-ink/40 p-0 sm:p-4 overflow-y-auto"
    >
      <div className="w-full max-w-md max-h-[92vh] sm:max-h-[90vh] overflow-y-auto rounded-t-xl sm:rounded-control border border-line bg-surface p-4 sm:p-6 shadow-card space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 id="status-modal-title" className="text-lg font-semibold text-ink">
              {isDeactivating ? 'Deactivate user account' : 'Activate user account'}
            </h3>
            <p className="text-sm text-pencil mt-2">
              {isDeactivating
                ? `Are you sure you want to deactivate ${user.full_name}? This will invalidate all active sessions and prevent the user from signing in.`
                : `Are you sure you want to reactivate ${user.full_name}? The user will be permitted to sign in again.`}
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
            variant={isDeactivating ? 'danger' : 'primary'}
            onClick={onConfirm}
            disabled={isSubmitting}
            className="w-full sm:w-auto"
          >
            {isSubmitting
              ? isDeactivating
                ? 'Deactivating...'
                : 'Activating...'
              : isDeactivating
                ? 'Deactivate user'
                : 'Activate user'}
          </Button>
        </div>
      </div>
    </div>
  );
};
