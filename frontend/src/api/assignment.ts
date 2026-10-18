import {
  Assignment,
  AssignmentCreatePayload,
  AssignmentUpdatePayload,
  StudentSubmissionRosterItem,
  Submission,
  SubmissionGradePayload,
  SubmissionSubmitPayload,
} from '../types/assignment';

export class AssignmentApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'AssignmentApiError';
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

  throw new AssignmentApiError(message, response.status, code);
}

export async function createCourseAssignment(
  courseId: number,
  payload: AssignmentCreatePayload
): Promise<Assignment> {
  const response = await fetch(`/api/courses/${courseId}/assignments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return response.json() as Promise<Assignment>;
}

export async function listCourseAssignments(courseId: number): Promise<Assignment[]> {
  const response = await fetch(`/api/courses/${courseId}/assignments`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return response.json() as Promise<Assignment[]>;
}

export async function getAssignment(assignmentId: number): Promise<Assignment> {
  const response = await fetch(`/api/assignments/${assignmentId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return response.json() as Promise<Assignment>;
}

export async function updateAssignment(
  assignmentId: number,
  payload: AssignmentUpdatePayload
): Promise<Assignment> {
  const response = await fetch(`/api/assignments/${assignmentId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return response.json() as Promise<Assignment>;
}

export async function deleteAssignment(assignmentId: number): Promise<void> {
  const response = await fetch(`/api/assignments/${assignmentId}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }
}

export async function submitAssignment(
  assignmentId: number,
  payload: SubmissionSubmitPayload
): Promise<Submission> {
  const response = await fetch(`/api/assignments/${assignmentId}/submission`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return response.json() as Promise<Submission>;
}

export async function getStudentSubmission(assignmentId: number): Promise<Submission> {
  const response = await fetch(`/api/assignments/${assignmentId}/submission`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return response.json() as Promise<Submission>;
}

export async function listAssignmentSubmissions(
  assignmentId: number
): Promise<StudentSubmissionRosterItem[]> {
  const response = await fetch(`/api/assignments/${assignmentId}/submissions`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return response.json() as Promise<StudentSubmissionRosterItem[]>;
}

export async function gradeSubmission(
  submissionId: number,
  payload: SubmissionGradePayload
): Promise<Submission> {
  const response = await fetch(`/api/submissions/${submissionId}/grade`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    credentials: 'include',
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return response.json() as Promise<Submission>;
}
