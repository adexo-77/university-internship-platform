/**
 * TypeScript types for internship postings.
 */

export type InternshipWorkMode = 'onsite' | 'remote' | 'hybrid';

export type InternshipStatus = 'draft' | 'pending_review' | 'open' | 'rejected' | 'closed';

export interface Internship {
  id: number;
  organization_id: number;
  organization_name?: string | null;
  title: string;
  description: string;
  requirements: string;
  location: string;
  work_mode: InternshipWorkMode;
  duration_weeks?: number | null;
  application_deadline: string;
  status: InternshipStatus;
  created_at: string;
  updated_at: string;
  applicant_count?: number;
  applications_accepted?: boolean;
  applied?: boolean | null;
  application_status?: string | null;
  review_note?: string | null;
  reviewed_at?: string | null;
  reviewed_by?: number | null;
}

export interface InternshipListResponse {
  items: Internship[];
  total: number;
  limit: number;
  offset: number;
}

export interface InternshipCreateRequest {
  title: string;
  description: string;
  requirements: string;
  location: string;
  work_mode: InternshipWorkMode;
  duration_weeks?: number | null;
  application_deadline: string;
}

export interface InternshipUpdateRequest {
  title?: string | null;
  description?: string | null;
  requirements?: string | null;
  location?: string | null;
  work_mode?: InternshipWorkMode | null;
  duration_weeks?: number | null;
  application_deadline?: string | null;
  status?: InternshipStatus | null;
}
