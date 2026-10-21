export interface DueNextAssignment {
  assignment_id: string;
  course_id: string;
  course_title: string;
  title: string;
  due_at: string;
  max_points: number;
}

export interface RecentGrade {
  submission_id: string;
  assignment_id: string;
  assignment_title: string;
  course_title: string;
  grade: number;
  max_points: number;
  graded_at: string | null;
}

export interface StudentCourseProgress {
  course_id: string;
  title: string;
  instructor_name: string;
  assignments_total: number;
  assignments_submitted: number;
  progress_percent: number;
  average_grade_percent: number | null;
}

export interface LatestApplication {
  application_id: string;
  posting_id: string;
  posting_title: string;
  organization_name: string;
  status: string;
  applied_at: string;
}

export interface StudentApplicationsSummary {
  counts: Record<string, number>;
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
  course_id: string;
  title: string;
  status: string;
  enrolled_count: number;
  assignments_count: number;
  awaiting_grading_count: number;
  average_grade_percent: number | null;
}

export interface NeedsGradingItem {
  submission_id: string;
  assignment_id: string;
  assignment_title: string;
  course_id: string;
  course_title: string;
  student_name: string;
  submitted_at: string;
  is_late: boolean;
}

export interface InstructorDashboardResponse {
  courses: InstructorCourseSummary[];
  needs_grading: NeedsGradingItem[];
}

export interface OrgApplicationItem {
  application_id: string;
  posting_id: string;
  posting_title: string;
  applicant_name: string;
  status: string;
  applied_at: string;
}

export interface OrganizationDashboardResponse {
  approval_status: string;
  approval_note: string | null;
  posting_counts: Record<string, number>;
  applications_awaiting_decision: number;
  recent_applications: OrgApplicationItem[];
}

export interface AdminDashboardResponse {
  users_by_role: Record<string, number>;
  active_users_count: number;
  organizations_pending_approval: number;
  internships_pending_review: number;
  open_internships: number;
  courses_by_status: Record<string, number>;
  applications_by_status: Record<string, number>;
}
