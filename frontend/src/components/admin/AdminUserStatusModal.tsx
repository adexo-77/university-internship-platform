import React from 'react';
import { AdminUser } from '../../types/admin';
import { Button, ErrorMessage } from '../ui';

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
  if (!isOpen || !user) return null;

  const isDeactivating = user.is_active;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="status-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4"
    >
      <div className="w-full max-w-md rounded-control border border-line bg-surface p-6 shadow-card space-y-4">
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

        {error && (
          <ErrorMessage whatHappened={error} howToFix="Please try again or cancel the operation." />
        )}

        <div className="flex justify-end gap-3 pt-2">
          <Button type="button" variant="quiet" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            type="button"
            variant={isDeactivating ? 'danger' : 'primary'}
            onClick={onConfirm}
            disabled={isSubmitting}
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
