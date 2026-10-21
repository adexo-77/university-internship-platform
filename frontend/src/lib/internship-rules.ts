import { formatDate } from './dates';

export const MAX_DEADLINE_DAYS = 90;

export const WORK_MODE_OPTIONS = [
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'onsite', label: 'Onsite' },
  { value: 'remote', label: 'Remote' },
];

export function toLocalDatetimeString(isoString?: string): string {
  if (!isoString) return '';
  const d = new Date(isoString);
  if (isNaN(d.getTime())) return '';
  const pad = (n: number) => String(n).padStart(2, '0');
  const yyyy = d.getFullYear();
  const MM = pad(d.getMonth() + 1);
  const dd = pad(d.getDate());
  const hh = pad(d.getHours());
  const mm = pad(d.getMinutes());
  return `${yyyy}-${MM}-${dd}T${hh}:${mm}`;
}

export function checkRequiredText(
  val: string,
  label: string,
  max: number,
  pluralVerb = false
): string | undefined {
  if (!val.trim()) return `${label} ${pluralVerb ? 'are' : 'is'} required.`;
  if (val.trim().length > max) return `${label} cannot exceed ${max} characters.`;
  return undefined;
}

export function validateDeadline(deadline: string, isEdit: boolean): string | undefined {
  if (!deadline) {
    return 'Application deadline is required.';
  }
  const selected = new Date(deadline).getTime();
  if (isNaN(selected)) {
    return 'Invalid deadline date format.';
  }
  if (!isEdit && selected <= Date.now()) {
    return 'Application deadline must be set in the future.';
  }
  return undefined;
}

export function computeMaxAllowedDeadline(
  status?: string,
  reviewedAt?: string | null
): {
  maxDate: Date;
  localString: string;
  helperText: string;
} {
  const ref = status === 'open' && reviewedAt ? new Date(reviewedAt) : new Date();
  const maxDate = new Date(ref.getTime() + MAX_DEADLINE_DAYS * 24 * 60 * 60 * 1000);
  return {
    maxDate,
    localString: toLocalDatetimeString(maxDate.toISOString()),
    helperText: `Latest allowed deadline: ${formatDate(maxDate.toISOString())}`,
  };
}
