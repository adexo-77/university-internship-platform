import { describe, expect, it } from 'vitest';
import { formatDate, formatDateTime, isDueSoon, isPastDue } from './dates';

describe('dates utilities', () => {
  it('formats unambiguous date without time or timezone name', () => {
    const formatted = formatDate('2026-10-18T10:00:00Z');
    expect(formatted).toMatch(/\b18 Oct 2026\b/);
    expect(formatted).not.toContain('AM');
    expect(formatted).not.toContain('PM');
    expect(formatted).not.toContain(':');
  });

  it('formats unambiguous date and time with local timezone indicator', () => {
    const formatted = formatDateTime('2026-10-25T15:30:00Z');
    expect(formatted).toMatch(/\b25 Oct 2026\b/);
    expect(formatted).toMatch(/\b(AM|PM)\b/);
    expect(formatted).not.toBe('—');
  });

  it('handles null, undefined, or invalid dates gracefully', () => {
    expect(formatDate(null)).toBe('—');
    expect(formatDate(undefined)).toBe('—');
    expect(formatDate('invalid-iso')).toBe('Invalid date');

    expect(formatDateTime(null)).toBe('—');
    expect(formatDateTime(undefined)).toBe('—');
    expect(formatDateTime('invalid-iso')).toBe('Invalid date');
  });

  describe('isDueSoon logic', () => {
    const now = new Date('2026-10-20T12:00:00Z');

    it('returns true when due in 2 days (within 3 days)', () => {
      const due = '2026-10-22T12:00:00Z';
      expect(isDueSoon(due, now)).toBe(true);
    });

    it('returns true when due in exactly 3 days', () => {
      const due = '2026-10-23T12:00:00Z';
      expect(isDueSoon(due, now)).toBe(true);
    });

    it('returns false when due in 4 days (more than 3 days)', () => {
      const due = '2026-10-24T12:00:00Z';
      expect(isDueSoon(due, now)).toBe(false);
    });

    it('returns false when already past due', () => {
      const due = '2026-10-19T12:00:00Z';
      expect(isDueSoon(due, now)).toBe(false);
    });
  });

  describe('isPastDue logic', () => {
    const now = new Date('2026-10-20T12:00:00Z');

    it('returns true for past date', () => {
      expect(isPastDue('2026-10-19T12:00:00Z', now)).toBe(true);
    });

    it('returns false for future date', () => {
      expect(isPastDue('2026-10-21T12:00:00Z', now)).toBe(false);
    });
  });
});
