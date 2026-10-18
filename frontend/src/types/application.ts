/**
 * TypeScript types for internship applications.
 */

export type ApplicationStatus = 'submitted' | 'shortlisted' | 'accepted' | 'rejected' | 'withdrawn';

export interface ApplicantProfile {
  user_id: number;
  full_name: string;
  email: string;
  university?: string | null;
  department?: string | null;
  year_of_study?: number | null;
  skills: string[];
  bio?: string | null;
}

export interface Application {
  id: number;
  posting_id: number;
  posting_title?: string | null;
  organization_name?: string | null;
  student_id: number;
  cover_letter: string;
  status: ApplicationStatus;
  decision_message?: string | null;
  decided_at?: string | null;
  created_at: string;
  updated_at: string;
  applicant?: ApplicantProfile | null;
}

export interface ApplicationCreateRequest {
  cover_letter: string;
}

export interface ApplicationDecisionRequest {
  status: 'shortlisted' | 'accepted' | 'rejected';
  decision_message?: string | null;
}
