import {
  OrganizationProfile,
  OrganizationProfileUpdatePayload,
  StudentProfile,
  StudentProfileUpdatePayload,
} from '../types/profile';

/**
 * Custom error thrown by profile API calls with HTTP status and machine code.
 */
export class ProfileApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'ProfileApiError';
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
    // Ignore JSON parse failure and use fallback statusText
  }

  throw new ProfileApiError(message, response.status, code);
}

/**
 * Retrieve profile of currently authenticated student.
 */
export async function getStudentProfile(): Promise<StudentProfile> {
  const response = await fetch('/api/students/me', {
    method: 'GET',
    credentials: 'include',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as StudentProfile;
}

/**
 * Update profile of currently authenticated student.
 */
export async function updateStudentProfile(
  payload: StudentProfileUpdatePayload
): Promise<StudentProfile> {
  const response = await fetch('/api/students/me', {
    method: 'PUT',
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

  return (await response.json()) as StudentProfile;
}

/**
 * Retrieve profile of currently authenticated organization.
 */
export async function getOrganizationProfile(): Promise<OrganizationProfile> {
  const response = await fetch('/api/organizations/me', {
    method: 'GET',
    credentials: 'include',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as OrganizationProfile;
}

/**
 * Update profile of currently authenticated organization.
 */
export async function updateOrganizationProfile(
  payload: OrganizationProfileUpdatePayload
): Promise<OrganizationProfile> {
  const response = await fetch('/api/organizations/me', {
    method: 'PUT',
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

  return (await response.json()) as OrganizationProfile;
}
