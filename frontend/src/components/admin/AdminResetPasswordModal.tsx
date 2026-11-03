import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { resetAdminUserPassword } from '../../api/admin_user';
import { AdminUser } from '../../types/admin';
import { Button, ErrorMessage, IconButton, TextField } from '../ui';

export interface AdminResetPasswordModalProps {
  user: AdminUser | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (user: AdminUser) => void;
}

export const AdminResetPasswordModal: React.FC<AdminResetPasswordModalProps> = ({
  user,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [fieldError, setFieldError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setFieldError('');

    if (!password) {
      setFieldError('Password is required.');
      return;
    }
    if (password.length < 8 || password.length > 128) {
      setFieldError('Password must be between 8 and 128 characters.');
      return;
    }

    setIsSubmitting(true);
    try {
      const updated = await resetAdminUserPassword(user.id, password);
      setPassword('');
      onSuccess(updated);
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to reset user password.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="reset-modal-title"
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-ink/40 p-0 sm:p-4 overflow-y-auto"
    >
      <div className="w-full max-w-md max-h-[92vh] sm:max-h-[90vh] overflow-y-auto rounded-t-xl sm:rounded-control border border-line bg-surface p-4 sm:p-6 shadow-card space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 id="reset-modal-title" className="text-lg font-semibold text-ink">
              Reset password
            </h3>
            <p className="text-sm text-pencil mt-1">
              Set a new password for <span className="font-medium text-ink">{user.full_name}</span>{' '}
              ({user.email}). All active sessions will be invalidated.
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
          <ErrorMessage whatHappened={error} howToFix="Please try again with a valid password." />
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <TextField
            id="admin-reset-password"
            label="New password"
            type="password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              if (fieldError) setFieldError('');
            }}
            error={fieldError}
            helperText="Must be between 8 and 128 characters."
            required
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
              variant="primary"
              disabled={isSubmitting}
              className="w-full sm:w-auto"
            >
              {isSubmitting ? 'Resetting...' : 'Reset password'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
