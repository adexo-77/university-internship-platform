import React, { useState } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { AuthApiError } from '../api/auth';
import { Button, Notice, TextField } from '../components/ui';
import { useAuth } from '../hooks/useAuth';

export const LoginPage: React.FC = () => {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // If already authenticated, redirect to target page or /account
  if (isAuthenticated) {
    const from = (location.state as { from?: { pathname?: string } })?.from?.pathname ?? '/account';
    return <Navigate to={from} replace />;
  }

  const validate = (): boolean => {
    const errors: { email?: string; password?: string } = {};
    const normalized = email.trim();

    if (!normalized) {
      errors.email = 'Email address is required.';
    } else if (!normalized.includes('@') || !normalized.includes('.')) {
      errors.email = 'Enter a valid email address.';
    }

    if (!password) {
      errors.password = 'Password is required.';
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
      await login({
        email: email.trim(),
        password,
      });
      const destination =
        (location.state as { from?: { pathname?: string } })?.from?.pathname ?? '/account';
      navigate(destination, { replace: true });
    } catch (err) {
      if (err instanceof AuthApiError) {
        setServerError(err.message);
      } else if (err instanceof Error) {
        setServerError(err.message);
      } else {
        setServerError('Authentication failed. Please check your credentials.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-chalk flex flex-col justify-center items-center px-4 py-12">
      <div className="w-full max-w-md bg-surface border border-line rounded-control p-8 shadow-sm">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight text-ink">Log in</h1>
          <p className="text-xs text-pencil mt-1">
            Sign in with your university or organization credentials.
          </p>
        </div>

        {serverError && (
          <div className="mb-5">
            <Notice variant="error" title="Sign in failed">
              {serverError}
            </Notice>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <TextField
            id="login-email"
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={fieldErrors.email}
            autoComplete="email"
            required
          />

          <TextField
            id="login-password"
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={fieldErrors.password}
            autoComplete="current-password"
            required
          />

          <div className="pt-2">
            <Button
              id="login-submit-button"
              type="submit"
              variant="primary"
              className="w-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </Button>
          </div>
        </form>

        <div className="mt-6 border-t border-line pt-4 text-center">
          <p className="text-xs text-pencil">
            Do not have an account?{' '}
            <Link to="/register" className="text-petrol hover:underline font-medium">
              Register as student or organization
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
