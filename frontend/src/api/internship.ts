import {
  Internship,
  InternshipCreateRequest,
  InternshipListResponse,
  InternshipUpdateRequest,
} from '../types/internship';

export class InternshipApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'InternshipApiError';
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

  throw new InternshipApiError(message, response.status, code);
}

export async function getInternships(params?: {
  q?: string;
  work_mode?: string;
  limit?: number;
  offset?: number;
}): Promise<InternshipListResponse> {
  const query = new URLSearchParams();
  if (params?.q) query.set('q', params.q);
  if (params?.work_mode) query.set('work_mode', params.work_mode);
  if (params?.limit !== undefined) query.set('limit', String(params.limit));
  if (params?.offset !== undefined) query.set('offset', String(params.offset));

  const url = `/api/internships${query.toString() ? `?${query.toString()}` : ''}`;
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

export async function getOrganizationInternships(): Promise<Internship[]> {
  const response = await fetch('/api/organizations/me/internships', {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as Internship[];
}

export async function getInternshipById(id: number): Promise<Internship> {
  const response = await fetch(`/api/internships/${id}`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as Internship;
}

export async function createInternship(payload: InternshipCreateRequest): Promise<Internship> {
  const response = await fetch('/api/internships', {
    method: 'POST',
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

export async function updateInternship(
  id: number,
  payload: InternshipUpdateRequest
): Promise<Internship> {
  const response = await fetch(`/api/internships/${id}`, {
    method: 'PATCH',
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
