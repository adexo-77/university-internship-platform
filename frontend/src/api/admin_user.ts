import { AdminUser, AdminUserCreatePayload, AdminUserListResponse } from '../types/admin';

export class AdminUserApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'AdminUserApiError';
    this.status = status;
    this.code = code;
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
      const firstErr = errorBody.detail[0] as { msg?: string };
      message = firstErr.msg ?? 'Validation error';
    }
    code = errorBody.code;
  } catch {
    // Ignore JSON parse failure
  }

  throw new AdminUserApiError(message, response.status, code);
}

export interface ListAdminUsersParams {
  q?: string;
  role?: string;
  is_active?: boolean;
  limit?: number;
  offset?: number;
}

export async function listAdminUsers(
  params: ListAdminUsersParams = {}
): Promise<AdminUserListResponse> {
  const query = new URLSearchParams();
  if (params.q) query.set('q', params.q);
  if (params.role) query.set('role', params.role);
  if (params.is_active !== undefined) query.set('is_active', String(params.is_active));
  if (params.limit !== undefined) query.set('limit', String(params.limit));
  if (params.offset !== undefined) query.set('offset', String(params.offset));

  const url = `/api/admin/users${query.toString() ? `?${query.toString()}` : ''}`;
  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as AdminUserListResponse;
}

export async function createAdminUser(payload: AdminUserCreatePayload): Promise<AdminUser> {
  const response = await fetch('/api/admin/users', {
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

  return (await response.json()) as AdminUser;
}

export async function updateAdminUserStatus(id: number, isActive: boolean): Promise<AdminUser> {
  const response = await fetch(`/api/admin/users/${id}`, {
    method: 'PATCH',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({ is_active: isActive }),
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as AdminUser;
}

export async function resetAdminUserPassword(id: number, password: string): Promise<AdminUser> {
  const response = await fetch(`/api/admin/users/${id}/password`, {
    method: 'PUT',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({ password }),
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as AdminUser;
}
