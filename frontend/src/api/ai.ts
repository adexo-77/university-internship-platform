import { AiConsentPayload, AiStatusResponse } from '../types/ai';

/**
 * Custom error thrown by AI API calls with HTTP status and machine code.
 */
export class AiApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'AiApiError';
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
    // Ignore JSON parse failure and use fallback statusText
  }

  throw new AiApiError(message, response.status, code);
}

/**
 * Fetch AI availability, consent status, and remaining daily quota for the signed-in user.
 */
export async function fetchAiStatus(): Promise<AiStatusResponse> {
  const response = await fetch('/api/ai/status', {
    method: 'GET',
    credentials: 'include',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    await handleResponseError(response);
  }

  return (await response.json()) as AiStatusResponse;
}

/**
 * Accept or withdraw AI assistance consent for the signed-in user.
 */
export async function updateAiConsent(consented: boolean): Promise<AiStatusResponse> {
  const payload: AiConsentPayload = { consented };
  const response = await fetch('/api/ai/consent', {
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

  return (await response.json()) as AiStatusResponse;
}
