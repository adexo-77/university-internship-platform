import { AdminInternshipReviewPayload } from '../types/admin';
import { Internship, InternshipListResponse } from '../types/internship';

export class AdminInternshipApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'AdminInternshipApiError';
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
    // Ignore JSON parse error and use fallback message
  }

  throw new AdminInternshipApiError(message, response.status, code);
}

export async function listAdminInternships(params?: {
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<InternshipListResponse> {
  const query = new URLSearchParams();
  if (params?.status) query.set('status', params.status);
  if (params?.limit !== undefined) query.set('limit', String(params.limit));
  if (params?.offset !== undefined) query.set('offset', String(params.offset));

  const url = `/api/admin/internships${query.toString() ? `?${query.toString()}` : ''}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as InternshipListResponse;
}

export async function reviewInternship(
  id: number,
  payload: AdminInternshipReviewPayload
): Promise<Internship> {
  const response = await fetch(`/api/admin/internships/${id}/review`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as Internship;
}
