export interface DueNextAssignment {
  assignment_id: number | string;
  course_id: number | string;
  course_title: string;
  title: string;
  due_at: string;
  max_points?: number;
}

export interface RecentGrade {
  submission_id: number | string;
  assignment_id: number | string;
  assignment_title: string;
  course_title: string;
  grade: number;
  max_points: number;
  graded_at: string | null;
}

export interface StudentCourseProgress {
  course_id: number | string;
  title: string;
  instructor_name?: string | null;
  assignments_total: number;
  assignments_submitted: number;
  progress_percent: number;
  average_grade_percent: number | null;
}

export interface LatestApplication {
  id?: number | string;
  application_id?: number | string;
  posting_id: number | string;
  posting_title: string;
  organization_name: string;
  status: string;
  applied_at: string;
}

export interface StudentApplicationsSummary {
  counts_by_status?: Record<string, number>;
  counts?: Record<string, number>;
  recent: LatestApplication[];
}

export interface StudentDashboardResponse {
  due_next: DueNextAssignment[];
  recent_grades: RecentGrade[];
  courses: StudentCourseProgress[];
  applications: StudentApplicationsSummary;
  profile_complete: boolean;
}

export interface InstructorCourseSummary {
  course_id: number | string;
  title: string;
  status: string;
  enrolled_count: number;
  assignments_count: number;
  submissions_awaiting_grading?: number;
  awaiting_grading_count?: number;
  average_grade_percent: number | null;
}

export interface NeedsGradingItem {
  submission_id: number | string;
  assignment_id: number | string;
  assignment_title: string;
  course_id: number | string;
  course_title: string;
  student_name: string;
  submitted_at: string;
  late?: boolean;
  is_late?: boolean;
}

export interface InstructorDashboardResponse {
  courses: InstructorCourseSummary[];
  needs_grading: NeedsGradingItem[];
}

export interface OrgApplicationItem {
  application_id: number | string;
  posting_id: number | string;
  posting_title: string;
  applicant_name: string;
  applicant_email?: string;
  status: string;
  applied_at: string;
}

export interface OrganizationPostingsSummary {
  counts_by_status: Record<string, number>;
  total: number;
}

export interface OrganizationDashboardResponse {
  approval_status: string;
  approval_note: string | null;
  postings?: OrganizationPostingsSummary;
  posting_counts?: Record<string, number>;
  applications_awaiting_decision: number;
  recent_applications: OrgApplicationItem[];
}

export interface AdminDashboardResponse {
  users_by_role: Record<string, number>;
  users_active_count?: number;
  active_users_count?: number;
  users_total_count: number;
  organizations_pending_approval: number;
  postings_pending_review?: number;
  internships_pending_review?: number;
  open_internships: number;
  courses_by_status: Record<string, number>;
  applications_by_status: Record<string, number>;
}
