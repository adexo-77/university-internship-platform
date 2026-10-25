import { act, renderHook } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import * as notifApi from '../api/notification';
import { useUnreadCount } from './useUnreadCount';

describe('useUnreadCount hook', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();
    Object.defineProperty(document, 'visibilityState', {
      value: 'visible',
      writable: true,
      configurable: true,
    });
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.useRealTimers();
  });

  it('fetches unread count immediately upon mount when enabled', async () => {
    const fetchSpy = vi.spyOn(notifApi, 'fetchUnreadCount').mockResolvedValue({ unread_count: 5 });

    const { result } = renderHook(() => useUnreadCount({ enabled: true }));

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.unreadCount).toBe(5);
  });

  it('does not fetch or poll when enabled is false', async () => {
    const fetchSpy = vi.spyOn(notifApi, 'fetchUnreadCount');

    const { result } = renderHook(() => useUnreadCount({ enabled: false }));

    expect(fetchSpy).not.toHaveBeenCalled();
    expect(result.current.unreadCount).toBe(0);

    act(() => {
      vi.advanceTimersByTime(120_000);
    });

    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('polls every 60 seconds when document is visible', async () => {
    let callCount = 0;
    const fetchSpy = vi.spyOn(notifApi, 'fetchUnreadCount').mockImplementation(async () => {
      callCount += 1;
      return { unread_count: callCount };
    });

    const { result } = renderHook(() => useUnreadCount({ enabled: true, pollIntervalMs: 60_000 }));

    await act(async () => {
      await Promise.resolve();
    });
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(result.current.unreadCount).toBe(1);

    // Advance 60s
    await act(async () => {
      vi.advanceTimersByTime(60_000);
      await Promise.resolve();
    });
    expect(fetchSpy).toHaveBeenCalledTimes(2);
    expect(result.current.unreadCount).toBe(2);

    // Advance another 60s
    await act(async () => {
      vi.advanceTimersByTime(60_000);
      await Promise.resolve();
    });
    expect(fetchSpy).toHaveBeenCalledTimes(3);
    expect(result.current.unreadCount).toBe(3);
  });

  it('does not poll when document is hidden', async () => {
    const fetchSpy = vi.spyOn(notifApi, 'fetchUnreadCount').mockResolvedValue({ unread_count: 3 });

    renderHook(() => useUnreadCount({ enabled: true, pollIntervalMs: 60_000 }));

    await act(async () => {
      await Promise.resolve();
    });
    expect(fetchSpy).toHaveBeenCalledTimes(1);

    // Set tab to hidden
    Object.defineProperty(document, 'visibilityState', {
      value: 'hidden',
      writable: true,
      configurable: true,
    });

    await act(async () => {
      vi.advanceTimersByTime(60_000);
      await Promise.resolve();
    });

    // Should NOT have polled again
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  });

  it('refetches when window regains focus', async () => {
    const fetchSpy = vi.spyOn(notifApi, 'fetchUnreadCount').mockResolvedValue({ unread_count: 7 });

    const { result } = renderHook(() => useUnreadCount({ enabled: true }));

    await act(async () => {
      await Promise.resolve();
    });
    expect(fetchSpy).toHaveBeenCalledTimes(1);

    await act(async () => {
      window.dispatchEvent(new Event('focus'));
      await Promise.resolve();
    });

    expect(fetchSpy).toHaveBeenCalledTimes(2);
    expect(result.current.unreadCount).toBe(7);
  });

  it('cleans up interval and listeners on unmount', async () => {
    const fetchSpy = vi.spyOn(notifApi, 'fetchUnreadCount').mockResolvedValue({ unread_count: 2 });

    const { unmount } = renderHook(() => useUnreadCount({ enabled: true }));

    await act(async () => {
      await Promise.resolve();
    });
    expect(fetchSpy).toHaveBeenCalledTimes(1);

    unmount();

    await act(async () => {
      vi.advanceTimersByTime(120_000);
      window.dispatchEvent(new Event('focus'));
      await Promise.resolve();
    });

    // No further calls after unmount
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  });
});
