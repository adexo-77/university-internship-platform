import { useCallback, useEffect, useState } from 'react';
import { fetchDatabaseHealth, fetchHealth } from '../api/health';

export interface HealthState {
  apiStatus: string | null;
  dbStatus: string | null;
  publicDemo: boolean;
  isLoading: boolean;
  error: string | null;
}

export function useHealth() {
  const [state, setState] = useState<HealthState>({
    apiStatus: null,
    dbStatus: null,
    publicDemo: false,
    isLoading: true,
    error: null,
  });

  const checkHealth = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      // Check core API health
      const apiRes = await fetchHealth();

      // Check database health (soft check, does not crash core API status)
      let dbResult: string | null = null;
      try {
        const dbRes = await fetchDatabaseHealth();
        dbResult = dbRes.database;
      } catch (dbErr) {
        dbResult = dbErr instanceof Error ? dbErr.message : 'Database unavailable';
      }

      setState({
        apiStatus: apiRes.status,
        dbStatus: dbResult,
        publicDemo: Boolean(apiRes.public_demo),
        isLoading: false,
        error: null,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown network error';
      setState({
        apiStatus: null,
        dbStatus: null,
        publicDemo: false,
        isLoading: false,
        error: message,
      });
    }
  }, []);

  useEffect(() => {
    void checkHealth();
  }, [checkHealth]);

  return {
    ...state,
    refetch: checkHealth,
  };
}
