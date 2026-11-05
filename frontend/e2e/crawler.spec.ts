import { expect, Page, test } from '@playwright/test';
import { authenticateAsRole, DemoRole, trackErrors } from './helpers';

const ROLE_ROUTES = {
  student: [
    '/dashboard',
    '/my-courses',
    '/courses',
    '/courses/1',
    '/internships',
    '/internships/1',
    '/my-applications',
    '/profile',
    '/account',
    '/notifications',
  ],
  instructor: [
    '/dashboard',
    '/my-courses',
    '/courses/new',
    '/courses/6',
    '/account',
    '/notifications',
  ],
  organization: [
    '/dashboard',
    '/my-internships',
    '/internships/new',
    '/internships/1',
    '/profile',
    '/account',
    '/notifications',
  ],
  coordinator: [
    '/dashboard',
    '/admin/organizations',
    '/admin/internship-reviews',
    '/admin/reports',
    '/internships',
    '/internships/1',
    '/account',
    '/notifications',
  ],
  admin: [
    '/dashboard',
    '/admin/users',
    '/admin/users/new',
    '/admin/organizations',
    '/admin/internship-reviews',
    '/admin/reports',
    '/courses',
    '/internships',
    '/status',
    '/account',
    '/notifications',
  ],
} as const;

async function auditPageIntegrity(page: Page, path: string): Promise<void> {
  await page.goto(path);
  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});

  // Verify not 404
  const notFoundHeading = page.getByRole('heading', { name: /Page not found/i });
  expect(await notFoundHeading.isVisible()).toBe(false);

  // Check all links have valid destinations (no empty or "#")
  const links = page.locator('a');
  const count = await links.count();
  for (let i = 0; i < count; i++) {
    const link = links.nth(i);
    const href = await link.getAttribute('href');
    if (href !== null) {
      expect(href.trim()).not.toBe('');
      expect(href.trim()).not.toBe('#');
      expect(href.trim().toLowerCase()).not.toContain('javascript:');
    }
  }

  // Check buttons have accessible names
  const buttons = page.locator('button');
  const btnCount = await buttons.count();
  for (let i = 0; i < btnCount; i++) {
    const btn = buttons.nth(i);
    const text = (await btn.textContent())?.trim();
    const ariaLabel = await btn.getAttribute('aria-label');
    const ariaLabelledBy = await btn.getAttribute('aria-labelledby');
    const title = await btn.getAttribute('title');
    const hasName = Boolean(text || ariaLabel || ariaLabelledBy || title);
    expect(hasName).toBe(true);
  }
}

test.describe('Non-destructive Crawler', () => {
  test('Anonymous visitor pages are valid and have no broken links', async ({ page }) => {
    const tracker = trackErrors(page);
    for (const path of ['/login', '/register']) {
      await auditPageIntegrity(page, path);
    }
    expect(tracker.getErrors()).toEqual([]);
  });

  for (const [role, routes] of Object.entries(ROLE_ROUTES)) {
    test(`Crawler for role: ${role}`, async ({ page }) => {
      const tracker = trackErrors(page);
      await authenticateAsRole(page, role as DemoRole);

      for (const path of routes) {
        await auditPageIntegrity(page, path);
      }

      // Check modal open and close with Escape if on admin users page
      if (role === 'admin') {
        await page.goto('/admin/users');
        await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
        const resetPwBtn = page.getByRole('button', { name: /Reset password/i }).first();
        if (await resetPwBtn.isVisible()) {
          await resetPwBtn.click();
          const modal = page.locator('[role="dialog"]');
          await expect(modal).toBeVisible();
          await page.keyboard.press('Escape');
          await expect(modal).not.toBeVisible();
        }
      }

      expect(tracker.getErrors()).toEqual([]);
    });
  }
});
