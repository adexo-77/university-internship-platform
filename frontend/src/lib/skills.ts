/**
 * Utilities for formatting and parsing comma-separated skills strings.
 */

/**
 * Parse a comma-separated skills string into a trimmed, non-empty list of skills.
 */
export function parseSkills(input: string): string[] {
  return input
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
}

/**
 * Format a list of skill strings into a comma-separated display string.
 */
export function formatSkills(skills: string[]): string {
  return skills.join(', ');
}
