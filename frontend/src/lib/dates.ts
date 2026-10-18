/**
 * Unambiguous date formatting and due-soon logic in viewer's local timezone.
 */

const THREE_DAYS_MS = 3 * 24 * 60 * 60 * 1000;

/**
 * Format an ISO date string as an unambiguous date without time or timezone.
 * Example output: "18 Oct 2026"
 */
export function formatDate(isoString: string | null | undefined): string {
  if (!isoString) {
    return '—';
  }

  const date = new Date(isoString);
  if (isNaN(date.getTime())) {
    return 'Invalid date';
  }

  return new Intl.DateTimeFormat('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(date);
}

/**
 * Format an ISO date string as an unambiguous date and time with local timezone indicator.
 * Example output: "18 Oct 2026, 8:10 PM EDT"
 */
export function formatDateTime(isoString: string | null | undefined): string {
  if (!isoString) {
    return '—';
  }

  const date = new Date(isoString);
  if (isNaN(date.getTime())) {
    return 'Invalid date';
  }

  const raw = new Intl.DateTimeFormat('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZoneName: 'short',
  }).format(date);

  return raw.replace(/\b(am|pm)\b/gi, (match) => match.toUpperCase());
}

/**
 * Check if a due date is in the future and within 3 days from reference time.
 */
export function isDueSoon(
  dueAtIso: string | null | undefined,
  referenceDate: Date = new Date()
): boolean {
  if (!dueAtIso) {
    return false;
  }

  const dueDate = new Date(dueAtIso);
  if (isNaN(dueDate.getTime())) {
    return false;
  }

  const diffMs = dueDate.getTime() - referenceDate.getTime();
  return diffMs > 0 && diffMs <= THREE_DAYS_MS;
}

/**
 * Check if a due date has passed.
 */
export function isPastDue(
  dueAtIso: string | null | undefined,
  referenceDate: Date = new Date()
): boolean {
  if (!dueAtIso) {
    return false;
  }

  const dueDate = new Date(dueAtIso);
  if (isNaN(dueDate.getTime())) {
    return false;
  }

  return dueDate.getTime() < referenceDate.getTime();
}
