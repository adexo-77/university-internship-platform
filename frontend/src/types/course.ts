/**
 * Types for courses and enrollments.
 */

export type CourseStatus = 'draft' | 'published';

export interface Course {
  id: number;
  instructor_id: number;
  instructor_name?: string | null;
  title: string;
  description?: string | null;
  status: CourseStatus;
  created_at: string;
  updated_at: string;
  enrolled?: boolean | null;
  enrolled_count?: number | null;
}

export interface CourseListResponse {
  items: Course[];
  total: number;
  limit: number;
  offset: number;
}

export interface CourseCreateRequest {
  title: string;
  description?: string | null;
  status?: CourseStatus;
}

export interface CourseUpdateRequest {
  title?: string | null;
  description?: string | null;
  status?: CourseStatus;
}

export interface EnrolledStudent {
  student_id: number;
  name: string;
  email: string;
  enrolled_at: string;
}

export interface EnrollmentResponse {
  id: number;
  course_id: number;
  student_id: number;
  enrolled_at: string;
  message: string;
}
