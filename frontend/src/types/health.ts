/**
 * TypeScript types for health check API responses and UI states.
 */

export interface HealthResponse {
  status: string;
  public_demo?: boolean;
}

export interface DatabaseHealthResponse {
  database: string;
}
