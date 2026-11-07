export interface StudyPlanItem {
  type: 'assignment' | 'internship';
  title: string;
  link_path: string;
  due_at: string;
  suggested_minutes: number;
  reason: string;
  flags: string[];
}

export interface StudyPlanDay {
  date: string;
  items: StudyPlanItem[];
}

export interface StudyPlanWindow {
  days: number;
  start_date: string;
  end_date: string;
}

export interface StudyPlanMetrics {
  enrolled_courses_count: number;
  assignments_due_count: number;
  total_scheduled_minutes: number;
  overdue_assignments_count: number;
}

export interface StudyPlanSummary {
  headline: string;
  sentences: string[];
  metrics: StudyPlanMetrics;
}

export interface StudyPlanResponse {
  generated_at: string;
  window: StudyPlanWindow;
  summary: StudyPlanSummary;
  plan: StudyPlanDay[];
}
