/**
 * TypeScript types for health check API responses and UI states.
 */

export interface HealthResponse {
  status: string;
}

export interface DatabaseHealthResponse {
  database: string;
}
