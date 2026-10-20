/**
 * Type definitions for Student and Organization profiles.
 */

export interface StudentProfile {
  id: number;
  user_id: number;
  university: string | null;
  department: string | null;
  year_of_study: number | null;
  bio: string | null;
  skills: string[];
  updated_at: string;
}

export interface StudentProfileUpdatePayload {
  university?: string | null;
  department?: string | null;
  year_of_study?: number | null;
  bio?: string | null;
  skills?: string[];
}

export type ApprovalStatus = 'pending' | 'approved' | 'rejected';

export interface OrganizationProfile {
  id: number;
  user_id: number;
  organization_name: string;
  industry: string | null;
  location: string | null;
  website: string | null;
  description: string | null;
  approval_status: ApprovalStatus;
  approval_note: string | null;
  updated_at: string;
}

export interface OrganizationProfileUpdatePayload {
  organization_name: string;
  industry?: string | null;
  location?: string | null;
  website?: string | null;
  description?: string | null;
}
