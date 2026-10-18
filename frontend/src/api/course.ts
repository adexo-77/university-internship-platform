import {
  Course,
  CourseCreateRequest,
  CourseListResponse,
  CourseUpdateRequest,
  EnrolledStudent,
  EnrollmentResponse,
} from '../types/course';

/**
 * Custom error thrown by course API calls with HTTP status and code.
 */
export class CourseApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'CourseApiError';
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

  throw new CourseApiError(message, response.status, code);
}

/**
 * Query published courses (or all for admin) with search and pagination.
 */
export async function getCourses(params?: {
  q?: string;
  limit?: number;
  offset?: number;
}): Promise<CourseListResponse> {
  const query = new URLSearchParams();
  if (params?.q) query.set('q', params.q);
  if (params?.limit !== undefined) query.set('limit', String(params.limit));
  if (params?.offset !== undefined) query.set('offset', String(params.offset));

  const url = `/api/courses${query.toString() ? `?${query.toString()}` : ''}`;
  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as CourseListResponse;
}

/**
 * Retrieve single course by ID.
 */
export async function getCourseById(id: number): Promise<Course> {
  const response = await fetch(`/api/courses/${id}`, {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as Course;
}

/**
 * Create a new course (instructor only).
 */
export async function createCourse(payload: CourseCreateRequest): Promise<Course> {
  const response = await fetch('/api/courses', {
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

  return (await response.json()) as Course;
}

/**
 * Update course details or publish status.
 */
export async function updateCourse(id: number, payload: CourseUpdateRequest): Promise<Course> {
  const response = await fetch(`/api/courses/${id}`, {
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

  return (await response.json()) as Course;
}

/**
 * Get instructor's own courses with enrolled student count.
 */
export async function getInstructorCourses(): Promise<Course[]> {
  const response = await fetch('/api/instructors/me/courses', {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as Course[];
}

/**
 * Get student's enrolled courses.
 */
export async function getStudentCourses(): Promise<Course[]> {
  const response = await fetch('/api/students/me/courses', {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as Course[];
}

/**
 * Get student roster for a course (owner instructor or admin).
 */
export async function getCourseRoster(id: number): Promise<EnrolledStudent[]> {
  const response = await fetch(`/api/courses/${id}/students`, {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as EnrolledStudent[];
}

/**
 * Enroll student in a published course.
 */
export async function enrollInCourse(id: number): Promise<EnrollmentResponse> {
  const response = await fetch(`/api/courses/${id}/enrollment`, {
    method: 'POST',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as EnrollmentResponse;
}

/**
 * Unenroll student from a course.
 */
export async function leaveCourse(id: number): Promise<{ detail: string }> {
  const response = await fetch(`/api/courses/${id}/enrollment`, {
    method: 'DELETE',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as { detail: string };
}
