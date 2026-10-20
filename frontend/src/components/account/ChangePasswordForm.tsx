import React, { useState } from 'react';
import { changePassword } from '../../api/auth';
import { Button, ErrorMessage, Notice, TextField } from '../ui';

export interface ChangePasswordFormProps {
  onSuccess?: () => void;
}

export const ChangePasswordForm: React.FC<ChangePasswordFormProps> = ({ onSuccess }) => {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    if (!currentPassword) {
      errors.currentPassword = 'Current password is required.';
    }

    if (!newPassword) {
      errors.newPassword = 'New password is required.';
    } else if (newPassword.length < 8 || newPassword.length > 128) {
      errors.newPassword = 'New password must be between 8 and 128 characters.';
    } else if (newPassword === currentPassword) {
      errors.newPassword = 'New password must be different from current password.';
    }

    if (!confirmPassword) {
      errors.confirmPassword = 'Confirmation password is required.';
    } else if (newPassword !== confirmPassword) {
      errors.confirmPassword = 'Passwords do not match.';
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      setSuccessMessage('Password changed successfully.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setFieldErrors({});
      onSuccess?.();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage(
          'Failed to change password. Please check your current password and try again.'
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-lg" noValidate>
      {successMessage && (
        <Notice variant="info" title="Success">
          {successMessage}
        </Notice>
      )}

      {errorMessage && (
        <ErrorMessage
          whatHappened={errorMessage}
          howToFix="Please verify your current password and password requirements."
        />
      )}

      <TextField
        id="current-password"
        name="current-password"
        type="password"
        label="Current password"
        value={currentPassword}
        onChange={(e) => {
          setCurrentPassword(e.target.value);
          if (fieldErrors.currentPassword) {
            setFieldErrors((prev) => ({ ...prev, currentPassword: '' }));
          }
        }}
        error={fieldErrors.currentPassword}
        required
        disabled={isSubmitting}
      />

      <TextField
        id="new-password"
        name="new-password"
        type="password"
        label="New password"
        helperText="Must be 8 to 128 characters and different from current password."
        value={newPassword}
        onChange={(e) => {
          setNewPassword(e.target.value);
          if (fieldErrors.newPassword) {
            setFieldErrors((prev) => ({ ...prev, newPassword: '' }));
          }
        }}
        error={fieldErrors.newPassword}
        required
        disabled={isSubmitting}
      />

      <TextField
        id="confirm-password"
        name="confirm-password"
        type="password"
        label="Confirm new password"
        value={confirmPassword}
        onChange={(e) => {
          setConfirmPassword(e.target.value);
          if (fieldErrors.confirmPassword) {
            setFieldErrors((prev) => ({ ...prev, confirmPassword: '' }));
          }
        }}
        error={fieldErrors.confirmPassword}
        required
        disabled={isSubmitting}
      />

      <div className="pt-2">
        <Button type="submit" variant="primary" disabled={isSubmitting}>
          {isSubmitting ? 'Updating password...' : 'Update password'}
        </Button>
      </div>
    </form>
  );
};
