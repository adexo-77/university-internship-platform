import fs from 'fs';
import path from 'path';
import { describe, expect, it } from 'vitest';

const ALLOWED_PALETTE_BASE = new Set([
  'chalk',
  'surface',
  'ink',
  'pencil',
  'line',
  'petrol',
  'marigold',
  'moss',
  'brick',
  'transparent',
  'current',
  'inherit',
]);

const FORBIDDEN_TAILWIND_COLORS = [
  'slate',
  'gray',
  'zinc',
  'neutral',
  'stone',
  'red',
  'orange',
  'amber',
  'yellow',
  'lime',
  'green',
  'emerald',
  'teal',
  'cyan',
  'sky',
  'blue',
  'indigo',
  'violet',
  'purple',
  'fuchsia',
  'pink',
  'rose',
];

const NON_COLOR_UTILITIES: Record<string, Set<string>> = {
  text: new Set([
    'xs',
    'sm',
    'base',
    'lg',
    'xl',
    '2xl',
    '3xl',
    '4xl',
    '5xl',
    'center',
    'left',
    'right',
    'justify',
    'start',
    'end',
    'wrap',
    'nowrap',
    'ellipsis',
    'clip',
  ]),
  border: new Set([
    't',
    'b',
    'l',
    'r',
    'x',
    'y',
    '0',
    '2',
    '4',
    '8',
    'solid',
    'dashed',
    'dotted',
    'double',
    'none',
    'collapse',
    'separate',
  ]),
  ring: new Set(['0', '1', '2', '4', '8', 'inset']),
  bg: new Set([
    'auto',
    'cover',
    'contain',
    'bottom',
    'center',
    'top',
    'left',
    'right',
    'repeat',
    'no-repeat',
    'repeat-x',
    'repeat-y',
    'fixed',
    'local',
    'scroll',
  ]),
  from: new Set<string>(),
  to: new Set<string>(),
};

export function isAllowedTailwindColorToken(token: string): boolean {
  // Strip any pseudo-class prefixes (e.g., hover:, focus:, sm:, md:, group-hover:)
  const parts = token.split(':');
  const rawClass = parts[parts.length - 1];

  // Match prefixes bg-, text-, border-, ring-, from-, to-
  // Handle ring-offset- specially
  let prefix = '';
  let rest = '';

  if (rawClass.startsWith('ring-offset-')) {
    prefix = 'ring';
    rest = rawClass.slice('ring-offset-'.length);
    if (/^[0-9]+$/.test(rest)) {
      return true;
    }
  } else {
    const match = rawClass.match(/^(bg|text|border|ring|from|to)-(.+)$/);
    if (!match) {
      return true; // Not a target prefix
    }
    prefix = match[1];
    rest = match[2];
  }

  // Strip opacity suffix like /20 or /100
  const [baseCandidate] = rest.split('/');

  // Check if it is a non-color utility (e.g. text-sm, border-b, ring-1)
  if (NON_COLOR_UTILITIES[prefix]?.has(baseCandidate)) {
    return true;
  }

  // Check forbidden default Tailwind colors
  for (const forbidden of FORBIDDEN_TAILWIND_COLORS) {
    if (baseCandidate === forbidden || baseCandidate.startsWith(`${forbidden}-`)) {
      return false;
    }
  }

  // Check against allowed palette base and allowed variants
  // Allowed variants: petrol-hover, petrol-tint, marigold-tint
  for (const palette of ALLOWED_PALETTE_BASE) {
    if (baseCandidate === palette) return true;
    if (baseCandidate.startsWith(`${palette}-`)) {
      const variantSuffix = baseCandidate.slice(palette.length + 1);
      if (
        (palette === 'petrol' && (variantSuffix === 'hover' || variantSuffix === 'tint')) ||
        (palette === 'marigold' && variantSuffix === 'tint')
      ) {
        return true;
      }
      return false;
    }
  }

  return false;
}

function findTsxFiles(dir: string): string[] {
  let results: string[] = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results = results.concat(findTsxFiles(fullPath));
    } else if (entry.isFile() && entry.name.endsWith('.tsx')) {
      results.push(fullPath);
    }
  }
  return results;
}

describe('Tailwind Palette Guard', () => {
  it('identifies forbidden default Tailwind colors and unknown palette classes', () => {
    expect(isAllowedTailwindColorToken('text-blue-500')).toBe(false);
    expect(isAllowedTailwindColorToken('bg-red-600')).toBe(false);
    expect(isAllowedTailwindColorToken('border-gray-300')).toBe(false);
    expect(isAllowedTailwindColorToken('hover:bg-indigo-700')).toBe(false);
    expect(isAllowedTailwindColorToken('text-purple-400')).toBe(false);
    expect(isAllowedTailwindColorToken('bg-brick-tint')).toBe(false);

    expect(isAllowedTailwindColorToken('bg-chalk')).toBe(true);
    expect(isAllowedTailwindColorToken('bg-surface')).toBe(true);
    expect(isAllowedTailwindColorToken('text-ink')).toBe(true);
    expect(isAllowedTailwindColorToken('text-pencil')).toBe(true);
    expect(isAllowedTailwindColorToken('border-line')).toBe(true);
    expect(isAllowedTailwindColorToken('bg-petrol')).toBe(true);
    expect(isAllowedTailwindColorToken('hover:bg-petrol-hover')).toBe(true);
    expect(isAllowedTailwindColorToken('bg-petrol-tint')).toBe(true);
    expect(isAllowedTailwindColorToken('border-marigold')).toBe(true);
    expect(isAllowedTailwindColorToken('bg-marigold-tint')).toBe(true);
    expect(isAllowedTailwindColorToken('text-moss')).toBe(true);
    expect(isAllowedTailwindColorToken('border-brick')).toBe(true);
    expect(isAllowedTailwindColorToken('ring-offset-surface')).toBe(true);
    expect(isAllowedTailwindColorToken('text-sm')).toBe(true);
    expect(isAllowedTailwindColorToken('border-b')).toBe(true);
  });

  it('scans all src/**/*.tsx and confirms zero forbidden or unapproved palette color classes', () => {
    const srcDir = path.resolve(__dirname, '..');
    const tsxFiles = findTsxFiles(srcDir);
    expect(tsxFiles.length).toBeGreaterThan(0);

    const violations: { file: string; token: string }[] = [];

    for (const file of tsxFiles) {
      const content = fs.readFileSync(file, 'utf8');

      // Extract all string literals inside className or cn
      const stringMatches = content.match(/(?:'[^']*'|"[^"]*"|`[^`]*`)/g) || [];
      for (const literal of stringMatches) {
        const cleaned = literal.slice(1, -1);
        const tokens = cleaned.split(/\s+/);
        for (const token of tokens) {
          if (/^(?:[a-z0-9_-]+:)*(?:bg|text|border|ring|from|to)-[a-z0-9/_-]+$/.test(token)) {
            if (!isAllowedTailwindColorToken(token)) {
              violations.push({
                file: path.relative(srcDir, file),
                token,
              });
            }
          }
        }
      }
    }

    expect(violations).toEqual([]);
  });
});
