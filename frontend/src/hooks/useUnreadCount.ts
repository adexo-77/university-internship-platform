import { useCallback, useEffect, useRef, useState } from 'react';
import { fetchUnreadCount } from '../api/notification';

export interface UseUnreadCountOptions {
  enabled?: boolean;
  pollIntervalMs?: number;
}

export function useUnreadCount(options?: UseUnreadCountOptions) {
  const enabled = options?.enabled ?? true;
  const pollIntervalMs = options?.pollIntervalMs ?? 60_000;

  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const isMountedRef = useRef(true);

  const refresh = useCallback(async () => {
    if (!enabled) return;
    try {
      setIsLoading(true);
      setError(null);
      const res = await fetchUnreadCount();
      if (isMountedRef.current) {
        setUnreadCount(res.unread_count);
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err instanceof Error ? err.message : 'Failed to fetch unread count');
      }
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [enabled]);

  useEffect(() => {
    isMountedRef.current = true;
    if (!enabled) {
      setUnreadCount(0);
      return;
    }

    void refresh();

    const intervalId = window.setInterval(() => {
      if (document.visibilityState === 'visible') {
        void refresh();
      }
    }, pollIntervalMs);

    const handleFocus = () => {
      void refresh();
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        void refresh();
      }
    };

    window.addEventListener('focus', handleFocus);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      isMountedRef.current = false;
      window.clearInterval(intervalId);
      window.removeEventListener('focus', handleFocus);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [enabled, pollIntervalMs, refresh]);

  return {
    unreadCount,
    setUnreadCount,
    isLoading,
    error,
    refresh,
  };
}
