import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as aiApi from '../api/ai';
import { useAiStatus } from './useAiStatus';

vi.mock('../api/ai', async (importOriginal) => {
  const actual = await importOriginal<typeof aiApi>();
  return {
    ...actual,
    fetchAiStatus: vi.fn(),
    updateAiConsent: vi.fn(),
  };
});

const STATUS = {
  enabled: true,
  consented: false,
  consent_at: null,
  remaining_quota: 10,
  daily_limit: 10,
};

describe('useAiStatus Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads status on mount', async () => {
    vi.mocked(aiApi.fetchAiStatus).mockResolvedValueOnce(STATUS);

    const { result } = renderHook(() => useAiStatus());

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.status).toEqual(STATUS);
    expect(result.current.error).toBeNull();
  });

  it('surfaces load errors', async () => {
    vi.mocked(aiApi.fetchAiStatus).mockRejectedValueOnce(new Error('boom'));

    const { result } = renderHook(() => useAiStatus());

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.error).toBe('boom');
    expect(result.current.status).toBeNull();
  });

  it('updates consent and replaces status', async () => {
    vi.mocked(aiApi.fetchAiStatus).mockResolvedValueOnce(STATUS);
    const consentedStatus = { ...STATUS, consented: true, consent_at: '2026-11-26T00:00:00Z' };
    vi.mocked(aiApi.updateAiConsent).mockResolvedValueOnce(consentedStatus);

    const { result } = renderHook(() => useAiStatus());
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.setConsent(true);
    });

    expect(aiApi.updateAiConsent).toHaveBeenCalledWith(true);
    expect(result.current.status?.consented).toBe(true);
    expect(result.current.isSaving).toBe(false);
  });

  it('surfaces consent update errors without clearing status', async () => {
    vi.mocked(aiApi.fetchAiStatus).mockResolvedValueOnce(STATUS);
    vi.mocked(aiApi.updateAiConsent).mockRejectedValueOnce(new Error('nope'));

    const { result } = renderHook(() => useAiStatus());
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.setConsent(true);
    });

    expect(result.current.error).toBe('nope');
    expect(result.current.status).toEqual(STATUS);
  });
});
