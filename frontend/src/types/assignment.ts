/**
 * TypeScript interfaces for course assignments, submissions, and grading.
 */

export type SubmissionStatus = 'not_submitted' | 'submitted' | 'graded';

export interface Assignment {
  id: number;
  course_id: number;
  title: string;
  description: string | null;
  due_at: string;
  max_points: number;
  created_at: string;
  updated_at: string;
  submission_status?: SubmissionStatus | null;
  is_late?: boolean | null;
  grade?: number | null;
}

export interface AssignmentCreatePayload {
  title: string;
  description?: string | null;
  due_at: string;
  max_points?: number;
}

export interface AssignmentUpdatePayload {
  title?: string;
  description?: string | null;
  due_at?: string;
  max_points?: number;
}

export interface Submission {
  id: number;
  assignment_id: number;
  student_id: number;
  content: string;
  link_url?: string | null;
  is_late: boolean;
  submitted_at: string;
  updated_at: string;
  grade?: number | null;
  feedback?: string | null;
  graded_at?: string | null;
  graded_by?: number | null;
}

export interface StudentSubmissionRosterItem {
  student_id: number;
  student_name: string;
  student_email: string;
  submission: Submission | null;
}

export interface SubmissionSubmitPayload {
  content: string;
  link_url?: string | null;
}

export interface SubmissionGradePayload {
  grade: number;
  feedback?: string | null;
}
