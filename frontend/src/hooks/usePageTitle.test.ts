import { renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { usePageTitle } from './usePageTitle';

describe('usePageTitle Hook', () => {
  beforeEach(() => {
    document.title = 'Initial Title';
  });

  it('sets page title with platform suffix', () => {
    renderHook(() => usePageTitle('Courses'));
    expect(document.title).toBe('Courses - University Platform');
  });

  it('updates title when page title argument changes', () => {
    const { rerender } = renderHook(({ title }: { title: string }) => usePageTitle(title), {
      initialProps: { title: 'Courses' },
    });

    expect(document.title).toBe('Courses - University Platform');

    rerender({ title: 'Introduction to Programming' });
    expect(document.title).toBe('Introduction to Programming - University Platform');
  });

  it('sets platform name fallback when title is empty or whitespace', () => {
    renderHook(() => usePageTitle(''));
    expect(document.title).toBe('University Platform');

    renderHook(() => usePageTitle('   '));
    expect(document.title).toBe('University Platform');
  });

  it('sets platform name fallback when title is undefined', () => {
    renderHook(() => usePageTitle(undefined));
    expect(document.title).toBe('University Platform');
  });

  it('trims whitespace around provided title', () => {
    renderHook(() => usePageTitle('  Log in  '));
    expect(document.title).toBe('Log in - University Platform');
  });
});
