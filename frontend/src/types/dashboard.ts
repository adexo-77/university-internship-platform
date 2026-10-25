export interface DueNextAssignment {
  assignment_id: number;
  title: string;
  course_id: number;
  course_title: string;
  due_at: string;
}

export interface RecentGrade {
  submission_id: number;
  assignment_id: number;
  assignment_title: string;
  course_title: string;
  grade: number;
  max_points: number;
  graded_at: string | null;
}

export interface StudentCourseProgress {
  course_id: number;
  title: string;
  instructor_name: string | null;
  assignments_total: number;
  assignments_submitted: number;
  progress_percent: number;
  average_grade_percent: number | null;
}

export interface LatestApplication {
  id: number;
  posting_id: number;
  posting_title: string;
  organization_name: string;
  status: string;
  applied_at: string;
}

export interface StudentApplicationsSummary {
  counts_by_status: Record<string, number>;
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
  course_id: number;
  title: string;
  status: string;
  enrolled_count: number;
  assignments_count: number;
  submissions_awaiting_grading: number;
  average_grade_percent: number | null;
}

export interface NeedsGradingItem {
  submission_id: number;
  student_name: string;
  assignment_id: number;
  assignment_title: string;
  course_id: number;
  course_title: string;
  submitted_at: string;
  late: boolean;
}

export interface InstructorDashboardResponse {
  courses: InstructorCourseSummary[];
  needs_grading: NeedsGradingItem[];
}

export interface OrgApplicationItem {
  application_id: number;
  applicant_name: string;
  applicant_email: string;
  posting_id: number;
  posting_title: string;
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
  postings: OrganizationPostingsSummary;
  applications_awaiting_decision: number;
  recent_applications: OrgApplicationItem[];
}

export interface AdminDashboardResponse {
  users_by_role: Record<string, number>;
  users_active_count: number;
  users_total_count: number;
  organizations_pending_approval: number;
  postings_pending_review: number;
  open_internships: number;
  courses_by_status: Record<string, number>;
  applications_by_status: Record<string, number>;
}

export interface CoordinatorDashboardResponse {
  organizations_pending_approval: number;
  internships_pending_review: number;
  open_internships: number;
  applications_by_status: Record<string, number>;
  reviews_completed: number;
}
