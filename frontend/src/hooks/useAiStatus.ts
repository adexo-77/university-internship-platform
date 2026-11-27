import { useCallback, useEffect, useState } from 'react';
import { fetchAiStatus, updateAiConsent } from '../api/ai';
import { AiStatusResponse } from '../types/ai';

export interface AiStatusState {
  status: AiStatusResponse | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
}

const INITIAL_STATE: AiStatusState = {
  status: null,
  isLoading: true,
  isSaving: false,
  error: null,
};

export function useAiStatus() {
  const [state, setState] = useState<AiStatusState>(INITIAL_STATE);

  const loadStatus = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const status = await fetchAiStatus();
      setState({ status, isLoading: false, isSaving: false, error: null });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown network error';
      setState({ status: null, isLoading: false, isSaving: false, error: message });
    }
  }, []);

  const setConsent = useCallback(async (consented: boolean) => {
    setState((prev) => ({ ...prev, isSaving: true, error: null }));
    try {
      const status = await updateAiConsent(consented);
      setState({ status, isLoading: false, isSaving: false, error: null });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown network error';
      setState((prev) => ({ ...prev, isSaving: false, error: message }));
    }
  }, []);

  useEffect(() => {
    void loadStatus();
  }, [loadStatus]);

  return {
    ...state,
    refetch: loadStatus,
    setConsent,
  };
}
