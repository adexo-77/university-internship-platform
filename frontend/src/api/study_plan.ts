import { StudyPlanResponse } from '../types/study_plan';

export class StudyPlanApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'StudyPlanApiError';
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

  throw new StudyPlanApiError(message, response.status, code);
}

/**
 * Fetch rule-based study schedule and progress summary for the current student.
 */
export async function getStudentStudyPlan(days: number = 7): Promise<StudyPlanResponse> {
  const response = await fetch(`/api/students/me/study-plan?days=${encodeURIComponent(days)}`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as StudyPlanResponse;
}
