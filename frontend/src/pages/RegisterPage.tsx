import React, { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { AuthApiError } from '../api/auth';
import { Button, Notice, TextField } from '../components/ui';
import { cn } from '../lib/cn';
import { useAuth } from '../hooks/useAuth';
import { usePageTitle } from '../hooks/usePageTitle';
import { PublicRegisterRole } from '../types/auth';

export const RegisterPage: React.FC = () => {
  usePageTitle('Register');
  const { register, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<PublicRegisterRole>('student');
  const [organizationName, setOrganizationName] = useState('');
  const [fieldErrors, setFieldErrors] = useState<{
    fullName?: string;
    email?: string;
    password?: string;
    organizationName?: string;
  }>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/account" replace />;
  }

  const validate = (): boolean => {
    const errors: {
      fullName?: string;
      email?: string;
      password?: string;
      organizationName?: string;
    } = {};

    if (!fullName.trim()) {
      errors.fullName = 'Full name is required.';
    }

    const normalizedEmail = email.trim();
    if (!normalizedEmail) {
      errors.email = 'Email address is required.';
    } else if (!normalizedEmail.includes('@') || !normalizedEmail.includes('.')) {
      errors.email = 'Enter a valid email address.';
    }

    if (!password) {
      errors.password = 'Password is required.';
    } else if (password.length < 8) {
      errors.password = 'Password must be at least 8 characters long.';
    } else if (password.length > 128) {
      errors.password = 'Password cannot exceed 128 characters.';
    }

    if (role === 'organization' && !organizationName.trim()) {
      errors.organizationName = 'Organization name is required.';
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError(null);

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await register({
        full_name: fullName.trim(),
        email: email.trim(),
        password,
        role,
        organization_name: role === 'organization' ? organizationName.trim() : undefined,
      });
      navigate('/account', { replace: true });
    } catch (err) {
      if (err instanceof AuthApiError) {
        setServerError(err.message);
      } else if (err instanceof Error) {
        setServerError(err.message);
      } else {
        setServerError('Registration failed. Please review your details and try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-chalk flex flex-col justify-center items-center px-4 py-12">
      <div className="w-full max-w-md bg-surface border border-line rounded-control p-8 shadow-sm">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight text-ink">Register account</h1>
          <p className="text-xs text-pencil mt-1">
            Create a student or organization account to get started.
          </p>
        </div>

        {serverError && (
          <div className="mb-5">
            <Notice variant="error" title="Registration failed">
              {serverError}
            </Notice>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <TextField
            id="register-fullname"
            label="Full name"
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            error={fieldErrors.fullName}
            autoComplete="name"
            required
          />

          <TextField
            id="register-email"
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={fieldErrors.email}
            autoComplete="email"
            required
          />

          <TextField
            id="register-password"
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={fieldErrors.password}
            helperText="Must be between 8 and 128 characters."
            autoComplete="new-password"
            required
          />

          <fieldset className="space-y-1.5">
            <legend className="block text-xs font-medium text-ink">Account role</legend>
            <div className="grid grid-cols-2 gap-3 pt-1">
              <label
                htmlFor="register-role-student"
                className={cn(
                  'flex items-center gap-3 p-3 rounded-control border cursor-pointer transition-colors duration-150',
                  role === 'student'
                    ? 'border-petrol bg-surface ring-1 ring-petrol'
                    : 'border-line bg-surface hover:bg-chalk'
                )}
              >
                <input
                  type="radio"
                  id="register-role-student"
                  name="role"
                  value="student"
                  checked={role === 'student'}
                  onChange={() => setRole('student')}
                  className="h-4 w-4 text-petrol focus:ring-petrol border-line accent-petrol"
                />
                <span className="text-sm font-medium text-ink">Student</span>
              </label>

              <label
                htmlFor="register-role-organization"
                className={cn(
                  'flex items-center gap-3 p-3 rounded-control border cursor-pointer transition-colors duration-150',
                  role === 'organization'
                    ? 'border-petrol bg-surface ring-1 ring-petrol'
                    : 'border-line bg-surface hover:bg-chalk'
                )}
              >
                <input
                  type="radio"
                  id="register-role-organization"
                  name="role"
                  value="organization"
                  checked={role === 'organization'}
                  onChange={() => setRole('organization')}
                  className="h-4 w-4 text-petrol focus:ring-petrol border-line accent-petrol"
                />
                <span className="text-sm font-medium text-ink">Organization</span>
              </label>
            </div>
          </fieldset>

          {role === 'organization' && (
            <TextField
              id="register-orgname"
              label="Organization name"
              type="text"
              value={organizationName}
              onChange={(e) => setOrganizationName(e.target.value)}
              error={fieldErrors.organizationName}
              required
            />
          )}

          <div className="pt-2">
            <Button
              id="register-submit-button"
              type="submit"
              variant="primary"
              className="w-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating account...' : 'Create account'}
            </Button>
          </div>
        </form>

        <div className="mt-6 border-t border-line pt-4 text-center">
          <p className="text-xs text-pencil">
            Already have an account?{' '}
            <Link to="/login" className="text-petrol hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
