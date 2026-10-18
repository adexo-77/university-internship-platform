import {
  Application,
  ApplicationCreateRequest,
  ApplicationDecisionRequest,
} from '../types/application';

export class ApplicationApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'ApplicationApiError';
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

  throw new ApplicationApiError(message, response.status, code);
}

export async function applyToInternship(
  postingId: number,
  payload: ApplicationCreateRequest
): Promise<Application> {
  const response = await fetch(`/api/internships/${postingId}/applications`, {
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

  return (await response.json()) as Application;
}

export async function getStudentApplications(): Promise<Application[]> {
  const response = await fetch('/api/students/me/applications', {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as Application[];
}

export async function withdrawApplication(id: number): Promise<Application> {
  const response = await fetch(`/api/applications/${id}/withdraw`, {
    method: 'POST',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as Application;
}

export async function getInternshipApplications(
  postingId: number,
  status?: string
): Promise<Application[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : '';
  const response = await fetch(`/api/internships/${postingId}/applications${query}`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as Application[];
}

export async function getApplicationById(id: number): Promise<Application> {
  const response = await fetch(`/api/applications/${id}`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as Application;
}

export async function decideApplication(
  id: number,
  payload: ApplicationDecisionRequest
): Promise<Application> {
  const response = await fetch(`/api/applications/${id}/decision`, {
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

  return (await response.json()) as Application;
}
