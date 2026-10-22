import { ChangePasswordPayload, LoginPayload, RegisterPayload, User } from '../types/auth';

/**
 * Custom error thrown by authentication API calls with HTTP status and machine code.
 */
export class AuthApiError extends Error {
  readonly status: number;
  readonly code?: string;
  readonly retryAfter?: number;

  constructor(message: string, status: number, code?: string, retryAfter?: number) {
    super(message);
    this.name = 'AuthApiError';
    this.status = status;
    this.code = code;
    this.retryAfter = retryAfter;
  }
}

async function handleResponseError(response: Response): Promise<never> {
  let message = response.statusText || 'Request failed';
  let code: string | undefined;

  try {
    const errorBody = (await response.json()) as { detail?: unknown; code?: string };
    if (typeof errorBody.detail === 'string') {
      message = errorBody.detail;
    } else if (Array.isArray(errorBody.detail) && errorBody.detail.length > 0) {
      // Pydantic validation errors array
      const firstErr = errorBody.detail[0] as { msg?: string };
      message = firstErr.msg ?? 'Validation error';
    }
    code = errorBody.code;
  } catch {
    // Ignore JSON parse failure and use fallback statusText
  }

  const retryHeader = response.headers.get('Retry-After');
  const parsedRetry = retryHeader ? parseInt(retryHeader, 10) : undefined;
  const retryAfter = Number.isFinite(parsedRetry) ? parsedRetry : undefined;

  throw new AuthApiError(message, response.status, code, retryAfter);
}

/**
 * Register a new student or organization account.
 */
export async function registerUser(payload: RegisterPayload): Promise<User> {
  const response = await fetch('/api/auth/register', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as User;
}

/**
 * Authenticate with email and password credentials.
 */
export async function loginUser(payload: LoginPayload): Promise<User> {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as User;
}

/**
 * Invalidate current session and clear authentication cookie.
 */
export async function logoutUser(): Promise<void> {
  const response = await fetch('/api/auth/logout', {
    method: 'POST',
    credentials: 'include',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }
}

/**
 * Retrieve profile of currently authenticated user session.
 */
export async function getCurrentUser(): Promise<User> {
  const response = await fetch('/api/auth/me', {
    method: 'GET',
    credentials: 'include',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as User;
}

/**
 * Change authenticated user's password.
 */
export async function changePassword(payload: ChangePasswordPayload): Promise<void> {
  const response = await fetch('/api/auth/change-password', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    await handleResponseError(response);
  }
}
