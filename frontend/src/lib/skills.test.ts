import { describe, expect, it } from 'vitest';
import { formatSkills, parseSkills } from './skills';

describe('skills helper module', () => {
  it('parses comma-separated skills into trimmed list', () => {
    expect(parseSkills('Python,  TypeScript , React')).toEqual(['Python', 'TypeScript', 'React']);
  });

  it('filters out empty or whitespace entries during parsing', () => {
    expect(parseSkills('Python, , , React,  ')).toEqual(['Python', 'React']);
    expect(parseSkills('')).toEqual([]);
    expect(parseSkills('   ')).toEqual([]);
  });

  it('formats skills list into comma-separated string', () => {
    expect(formatSkills(['Python', 'React', 'SQL'])).toBe('Python, React, SQL');
    expect(formatSkills([])).toBe('');
  });
});
