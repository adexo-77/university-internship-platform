import {
  AdminOrganizationApprovalPayload,
  AdminOrganizationItem,
  AdminOrganizationListResponse,
} from '../types/admin';

export class AdminOrganizationApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'AdminOrganizationApiError';
    this.status = status;
    this.code = code;
  }
}

async function handleResponseError(response: Response): Promise<never> {
  let message = response.statusText || 'Request failed';
  let code: string | undefined;

  try {
    const errorBody = (await response.json()) as { detail?: unknown; code?: string };
    if (typeof errorBody.detail === 'string') {
      message = errorBody.detail;
    } else if (Array.isArray(errorBody.detail) && errorBody.detail.length > 0) {
      const firstErr = errorBody.detail[0] as { msg?: string };
      message = firstErr.msg ?? 'Validation error';
    }
    code = errorBody.code;
  } catch {
    // Ignore JSON parse failure
  }

  throw new AdminOrganizationApiError(message, response.status, code);
}

export interface ListAdminOrganizationsParams {
  approval_status?: string;
  limit?: number;
  offset?: number;
}

export async function listAdminOrganizations(
  params: ListAdminOrganizationsParams = {}
): Promise<AdminOrganizationListResponse> {
  const query = new URLSearchParams();
  if (params.approval_status) query.set('approval_status', params.approval_status);
  if (params.limit !== undefined) query.set('limit', String(params.limit));
  if (params.offset !== undefined) query.set('offset', String(params.offset));

  const url = `/api/admin/organizations${query.toString() ? `?${query.toString()}` : ''}`;
  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as AdminOrganizationListResponse;
}

export async function updateAdminOrganizationApproval(
  userId: number,
  payload: AdminOrganizationApprovalPayload
): Promise<AdminOrganizationItem> {
  const response = await fetch(`/api/admin/organizations/${userId}/approval`, {
    method: 'PUT',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as AdminOrganizationItem;
}
