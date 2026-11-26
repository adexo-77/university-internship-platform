/**
 * TypeScript types for AI assistance status and consent API.
 */

export interface AiStatusResponse {
  enabled: boolean;
  consented: boolean;
  consent_at: string | null;
  remaining_quota: number;
  daily_limit: number;
}

export interface AiConsentPayload {
  consented: boolean;
}
