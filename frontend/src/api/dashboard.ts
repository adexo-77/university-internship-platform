import {
  AdminDashboardResponse,
  InstructorDashboardResponse,
  OrganizationDashboardResponse,
  StudentDashboardResponse,
} from '../types/dashboard';

export class DashboardApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'DashboardApiError';
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

  throw new DashboardApiError(message, response.status, code);
}

export async function getStudentDashboard(): Promise<StudentDashboardResponse> {
  const response = await fetch('/api/dashboard/student', {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as StudentDashboardResponse;
}

export async function getInstructorDashboard(): Promise<InstructorDashboardResponse> {
  const response = await fetch('/api/dashboard/instructor', {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as InstructorDashboardResponse;
}

export async function getOrganizationDashboard(): Promise<OrganizationDashboardResponse> {
  const response = await fetch('/api/dashboard/organization', {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as OrganizationDashboardResponse;
}

export async function getAdminDashboard(): Promise<AdminDashboardResponse> {
  const response = await fetch('/api/dashboard/admin', {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as AdminDashboardResponse;
}
