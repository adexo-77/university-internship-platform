import { act, renderHook } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthApiError } from '../api/auth';
import { useRateLimitCooldown } from './useRateLimitCooldown';

describe('useRateLimitCooldown Hook', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('initializes in an idle, non-rate-limited state', () => {
    const { result } = renderHook(() => useRateLimitCooldown());
    expect(result.current.isRateLimited).toBe(false);
    expect(result.current.cooldownSeconds).toBe(0);
    expect(result.current.cooldownMessage).toBeNull();
  });

  it('ignores non-429 errors', () => {
    const { result } = renderHook(() => useRateLimitCooldown());
    const handled = result.current.handleRateLimitError(
      new AuthApiError('Invalid credentials', 401)
    );
    expect(handled).toBe(false);
    expect(result.current.isRateLimited).toBe(false);
  });

  it('handles 429 error, starts countdown with retryAfter, and clears when timer reaches 0', () => {
    const { result } = renderHook(() => useRateLimitCooldown());

    act(() => {
      const handled = result.current.handleRateLimitError(
        new AuthApiError('Rate limited', 429, 'RATE_LIMITED', 3)
      );
      expect(handled).toBe(true);
    });

    expect(result.current.isRateLimited).toBe(true);
    expect(result.current.cooldownSeconds).toBe(3);
    expect(result.current.cooldownMessage).toBe('Too many attempts. Try again in 3 seconds.');

    // Advance 1s
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(result.current.cooldownSeconds).toBe(2);
    expect(result.current.cooldownMessage).toBe('Too many attempts. Try again in 2 seconds.');

    // Advance 2s to hit 0
    act(() => {
      vi.advanceTimersByTime(2000);
    });
    expect(result.current.cooldownSeconds).toBe(0);
    expect(result.current.isRateLimited).toBe(false);
    expect(result.current.cooldownMessage).toBeNull();
  });

  it('formats minutes properly for large cooldowns', () => {
    const { result } = renderHook(() => useRateLimitCooldown());

    act(() => {
      result.current.handleRateLimitError(
        new AuthApiError('Rate limited', 429, 'RATE_LIMITED', 900)
      );
    });

    expect(result.current.cooldownMessage).toBe('Too many attempts. Try again in 15 minutes.');

    act(() => {
      result.current.resetCooldown();
    });
    expect(result.current.isRateLimited).toBe(false);
    expect(result.current.cooldownSeconds).toBe(0);
  });
});
