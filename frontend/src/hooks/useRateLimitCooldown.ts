import { useEffect, useState } from 'react';
import { AuthApiError } from '../api/auth';

export interface UseRateLimitCooldownResult {
  cooldownSeconds: number;
  isRateLimited: boolean;
  cooldownMessage: string | null;
  handleRateLimitError: (err: unknown) => boolean;
  resetCooldown: () => void;
}

export function useRateLimitCooldown(defaultCooldown = 60): UseRateLimitCooldownResult {
  const [cooldownSeconds, setCooldownSeconds] = useState(0);

  useEffect(() => {
    if (cooldownSeconds <= 0) return;

    const timer = setInterval(() => {
      setCooldownSeconds((prev) => (prev > 1 ? prev - 1 : 0));
    }, 1000);

    return () => clearInterval(timer);
  }, [cooldownSeconds]);

  const handleRateLimitError = (err: unknown): boolean => {
    if (err instanceof AuthApiError && err.status === 429) {
      const wait = err.retryAfter && err.retryAfter > 0 ? err.retryAfter : defaultCooldown;
      setCooldownSeconds(wait);
      return true;
    }
    return false;
  };

  const resetCooldown = () => setCooldownSeconds(0);

  const formatCountdown = (seconds: number): string => {
    if (seconds >= 60) {
      const mins = Math.ceil(seconds / 60);
      return `${mins} minute${mins === 1 ? '' : 's'}`;
    }
    return `${seconds} second${seconds === 1 ? '' : 's'}`;
  };

  const cooldownMessage =
    cooldownSeconds > 0
      ? `Too many attempts. Try again in ${formatCountdown(cooldownSeconds)}.`
      : null;

  return {
    cooldownSeconds,
    isRateLimited: cooldownSeconds > 0,
    cooldownMessage,
    handleRateLimitError,
    resetCooldown,
  };
}
