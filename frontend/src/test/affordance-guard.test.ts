import fs from 'fs';
import path from 'path';
import { describe, expect, it } from 'vitest';

const ALLOWLIST_FILES = new Set([
  path.normalize('src/components/ui/Button.tsx'),
  path.normalize('src/components/ui/IconButton.tsx'),
  path.normalize('src/components/ui/TextLink.tsx'),
  path.normalize('src/components/ui/Card.tsx'),
  path.normalize('src/components/ui/BackLink.tsx'),
]);

function findTsxFiles(dir: string, fileList: string[] = []): string[] {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name !== 'node_modules' && entry.name !== 'dist' && entry.name !== 'test') {
        findTsxFiles(fullPath, fileList);
      }
    } else if (entry.isFile() && entry.name.endsWith('.tsx') && !entry.name.endsWith('.test.tsx')) {
      fileList.push(fullPath);
    }
  }
  return fileList;
}

describe('Clickable Affordances Guard', () => {
  it('confirms zero raw <button> or <a> tags outside approved shared UI components', () => {
    const srcDir = path.resolve(__dirname, '..');
    const tsxFiles = findTsxFiles(srcDir);
    expect(tsxFiles.length).toBeGreaterThan(0);

    const violations: { file: string; match: string; line: number }[] = [];

    const rawButtonRegex = /<button(?:\s|>)/g;
    const rawAnchorRegex = /<a(?:\s|>)/g;

    for (const file of tsxFiles) {
      const relPath = path.normalize(path.relative(path.resolve(srcDir, '..'), file));
      if (ALLOWLIST_FILES.has(relPath)) {
        continue;
      }

      const content = fs.readFileSync(file, 'utf8');
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (rawButtonRegex.test(line)) {
          violations.push({ file: relPath, match: '<button>', line: i + 1 });
        }
        if (rawAnchorRegex.test(line)) {
          violations.push({ file: relPath, match: '<a>', line: i + 1 });
        }
      }
    }

    expect(violations).toEqual([]);
  });
});
