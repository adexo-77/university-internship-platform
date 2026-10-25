export type NotificationKind =
  | 'assignment_created'
  | 'submission_graded'
  | 'submission_first'
  | 'application_received'
  | 'application_decision'
  | 'internship_approved'
  | 'internship_rejected'
  | 'internship_takedown'
  | 'internship_submitted'
  | 'organization_registered'
  | 'organization_status_changed'
  | 'password_reset';

export interface NotificationItemData {
  id: number;
  user_id: number;
  kind: NotificationKind;
  title: string;
  message: string;
  link_path: string;
  read_at: string | null;
  created_at: string;
}

export interface NotificationListResponse {
  items: NotificationItemData[];
  total: number;
  unread_count: number;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface MarkAllReadResponse {
  marked_read: number;
}
