import { UserRole } from './auth';
import { ApprovalStatus } from './profile';

export type AdminCreatableRole = 'instructor' | 'admin';

export interface AdminUser {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AdminUserCreatePayload {
  full_name: string;
  email: string;
  password: string;
  role: AdminCreatableRole;
}

export interface AdminUserListResponse {
  items: AdminUser[];
  total: number;
  limit: number;
  offset: number;
}

export interface AdminOrganizationItem {
  user_id: number;
  organization_name: string;
  contact_name: string;
  email: string;
  industry: string | null;
  location: string | null;
  approval_status: ApprovalStatus;
  approval_note: string | null;
  reviewed_at: string | null;
  reviewed_by: number | null;
}

export interface AdminOrganizationListResponse {
  items: AdminOrganizationItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface AdminOrganizationApprovalPayload {
  approval_status: ApprovalStatus;
  approval_note?: string | null;
}
