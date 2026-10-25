import {
  MarkAllReadResponse,
  NotificationItemData,
  NotificationListResponse,
  UnreadCountResponse,
} from '../types/notification';

export class NotificationApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'NotificationApiError';
    this.status = status;
  }
}

async function handleResponseError(response: Response): Promise<never> {
  let message = response.statusText || 'Request failed';
  try {
    const errorBody = (await response.json()) as { detail?: unknown };
    if (typeof errorBody.detail === 'string') {
      message = errorBody.detail;
    }
  } catch {
    // Fall back to status text
  }
  throw new NotificationApiError(message, response.status);
}

export async function fetchNotifications(params?: {
  unread_only?: boolean;
  limit?: number;
  offset?: number;
}): Promise<NotificationListResponse> {
  const query = new URLSearchParams();
  if (params?.unread_only !== undefined) {
    query.set('unread_only', String(params.unread_only));
  }
  if (params?.limit !== undefined) {
    query.set('limit', String(params.limit));
  }
  if (params?.offset !== undefined) {
    query.set('offset', String(params.offset));
  }

  const url = `/api/notifications${query.toString() ? `?${query.toString()}` : ''}`;
  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as NotificationListResponse;
}

export async function fetchUnreadCount(): Promise<UnreadCountResponse> {
  const response = await fetch('/api/notifications/unread-count', {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as UnreadCountResponse;
}

export async function markNotificationAsRead(id: number): Promise<NotificationItemData> {
  const response = await fetch(`/api/notifications/${id}/read`, {
    method: 'POST',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as NotificationItemData;
}

export async function markAllNotificationsAsRead(): Promise<MarkAllReadResponse> {
  const response = await fetch('/api/notifications/read-all', {
    method: 'POST',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as MarkAllReadResponse;
}
