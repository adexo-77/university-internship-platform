import React, { useState } from 'react';
import { createAdminUser } from '../../api/admin_user';
import { AdminCreatableRole, AdminUser } from '../../types/admin';
import { Button, ErrorMessage, Notice, TextField } from '../ui';

export interface AdminUserFormProps {
  onSuccess?: (user: AdminUser) => void;
}

export const AdminUserForm: React.FC<AdminUserFormProps> = ({ onSuccess }) => {
  const [role, setRole] = useState<AdminCreatableRole>('instructor');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    if (!role || (role !== 'instructor' && role !== 'admin' && role !== 'coordinator')) {
      errors.role = 'Role must be either instructor, admin, or coordinator.';
    }

    if (!fullName.trim()) {
      errors.fullName = 'Full name is required.';
    } else if (fullName.trim().length > 255) {
      errors.fullName = 'Full name cannot exceed 255 characters.';
    }

    const trimmedEmail = email.trim().toLowerCase();
    if (!trimmedEmail) {
      errors.email = 'Email address is required.';
    } else if (!trimmedEmail.includes('@') || !trimmedEmail.split('@')[1]?.includes('.')) {
      errors.email = 'Please provide a valid email address.';
    }

    if (!password) {
      errors.password = 'Password is required.';
    } else if (password.length < 8 || password.length > 128) {
      errors.password = 'Password must be between 8 and 128 characters.';
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    if (!validate()) return;

    setIsSubmitting(true);
    try {
      const created = await createAdminUser({
        role,
        full_name: fullName.trim(),
        email: email.trim().toLowerCase(),
        password,
      });

      setSuccessMessage(
        `Account for ${created.full_name} (${created.email}) created successfully.`
      );
      setFullName('');
      setEmail('');
      setPassword('');
      setFieldErrors({});
      onSuccess?.(created);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage('Failed to create user account.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-lg" noValidate>
      {successMessage && (
        <Notice variant="info" title="User created">
          {successMessage}
        </Notice>
      )}

      {errorMessage && (
        <ErrorMessage
          whatHappened={errorMessage}
          howToFix="Please verify user details and ensure email is not already registered."
        />
      )}

      <fieldset className="space-y-2">
        <legend className="text-sm font-medium text-ink">Account role</legend>
        <div className="flex items-center gap-6 pt-1">
          <label
            htmlFor="admin-role-instructor"
            className="flex items-center gap-2 cursor-pointer text-sm text-ink"
          >
            <input
              id="admin-role-instructor"
              type="radio"
              name="role"
              value="instructor"
              checked={role === 'instructor'}
              onChange={() => setRole('instructor')}
              disabled={isSubmitting}
              className="text-petrol focus:ring-petrol"
            />
            Instructor
          </label>
          <label
            htmlFor="admin-role-admin"
            className="flex items-center gap-2 cursor-pointer text-sm text-ink"
          >
            <input
              id="admin-role-admin"
              type="radio"
              name="role"
              value="admin"
              checked={role === 'admin'}
              onChange={() => setRole('admin')}
              disabled={isSubmitting}
              className="text-petrol focus:ring-petrol"
            />
            Administrator
          </label>
          <label
            htmlFor="admin-role-coordinator"
            className="flex items-center gap-2 cursor-pointer text-sm text-ink"
          >
            <input
              id="admin-role-coordinator"
              type="radio"
              name="role"
              value="coordinator"
              checked={role === 'coordinator'}
              onChange={() => setRole('coordinator')}
              disabled={isSubmitting}
              className="text-petrol focus:ring-petrol"
            />
            Coordinator
          </label>
        </div>
        {fieldErrors.role && <p className="text-xs text-brick mt-1">{fieldErrors.role}</p>}
      </fieldset>

      <TextField
        id="user-full-name"
        label="Full name"
        value={fullName}
        onChange={(e) => {
          setFullName(e.target.value);
          if (fieldErrors.fullName) setFieldErrors((p) => ({ ...p, fullName: '' }));
        }}
        error={fieldErrors.fullName}
        required
        disabled={isSubmitting}
        placeholder="e.g. Dr. Jane Doe"
      />

      <TextField
        id="user-email"
        label="Email address"
        type="email"
        value={email}
        onChange={(e) => {
          setEmail(e.target.value);
          if (fieldErrors.email) setFieldErrors((p) => ({ ...p, email: '' }));
        }}
        error={fieldErrors.email}
        required
        disabled={isSubmitting}
        placeholder="e.g. jane.doe@university.edu"
      />

      <TextField
        id="user-password"
        label="Initial password"
        type="password"
        value={password}
        onChange={(e) => {
          setPassword(e.target.value);
          if (fieldErrors.password) setFieldErrors((p) => ({ ...p, password: '' }));
        }}
        error={fieldErrors.password}
        helperText="Must be between 8 and 128 characters."
        required
        disabled={isSubmitting}
      />

      <div className="pt-2">
        <Button type="submit" variant="primary" disabled={isSubmitting}>
          {isSubmitting ? 'Creating account...' : 'Create user'}
        </Button>
      </div>
    </form>
  );
};
