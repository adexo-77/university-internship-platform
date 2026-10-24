import {
  CourseResource,
  CourseResourceCreateRequest,
  CourseResourceUpdateRequest,
} from '../types/course';

export class CourseResourceApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'CourseResourceApiError';
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

  throw new CourseResourceApiError(message, response.status, code);
}

/**
 * Retrieve resources for a course (owner instructor, admin, or enrolled student on published course).
 */
export async function getCourseResources(courseId: number): Promise<CourseResource[]> {
  const response = await fetch(`/api/courses/${courseId}/resources`, {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as CourseResource[];
}

/**
 * Create a new learning resource (owner instructor only).
 */
export async function createCourseResource(
  courseId: number,
  payload: CourseResourceCreateRequest
): Promise<CourseResource> {
  const response = await fetch(`/api/courses/${courseId}/resources`, {
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

  return (await response.json()) as CourseResource;
}

/**
 * Update an existing learning resource (owner instructor only).
 */
export async function updateCourseResource(
  resourceId: number,
  payload: CourseResourceUpdateRequest
): Promise<CourseResource> {
  const response = await fetch(`/api/resources/${resourceId}`, {
    method: 'PATCH',
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

  return (await response.json()) as CourseResource;
}

/**
 * Delete a learning resource (owner instructor only).
 */
export async function deleteCourseResource(resourceId: number): Promise<void> {
  const response = await fetch(`/api/resources/${resourceId}`, {
    method: 'DELETE',
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }
}
