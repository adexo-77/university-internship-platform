import { AchievementBadge } from '../types/badge';

export class BadgeApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'BadgeApiError';
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

  throw new BadgeApiError(message, response.status, code);
}

/**
 * Fetch achievement badges for the currently authenticated student.
 */
export async function getStudentBadges(): Promise<AchievementBadge[]> {
  const response = await fetch('/api/students/me/badges', {
    method: 'GET',
    credentials: 'include',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as AchievementBadge[];
}
