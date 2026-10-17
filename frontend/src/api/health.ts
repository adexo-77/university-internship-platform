import { DatabaseHealthResponse, HealthResponse } from '../types/health';

/**
 * Fetch basic system health through the Vite proxy (/api/health -> backend /health or /api/health).
 */
export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch('/api/health', {
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`API returned HTTP ${response.status}: ${response.statusText}`);
  }

  return (await response.json()) as HealthResponse;
}

/**
 * Fetch database connectivity health status through Vite proxy.
 */
export async function fetchDatabaseHealth(): Promise<DatabaseHealthResponse> {
  const response = await fetch('/api/health/db', {
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errJson = (await response.json()) as { detail?: string };
      if (errJson.detail) {
        errorDetail = errJson.detail;
      }
    } catch {
      // Ignore JSON parse failure and use fallback statusText
    }
    throw new Error(`Database error (${response.status}): ${errorDetail}`);
  }

  return (await response.json()) as DatabaseHealthResponse;
}
