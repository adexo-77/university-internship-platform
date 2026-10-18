/**
 * Date formatting and due-soon logic in viewer's local timezone.
 */

const THREE_DAYS_MS = 3 * 24 * 60 * 60 * 1000;

/**
 * Format an ISO date string in the user's local timezone with timezone name.
 * Example output: "Oct 25, 2026, 11:59 PM EDT"
 */
export function formatLocalDateTime(isoString: string | null | undefined): string {
  if (!isoString) {
    return '—';
  }

  const date = new Date(isoString);
  if (isNaN(date.getTime())) {
    return 'Invalid date';
  }

  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    timeZoneName: 'short',
  }).format(date);
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
