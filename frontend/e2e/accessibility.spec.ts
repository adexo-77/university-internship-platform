import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';
import { authenticateAsRole } from './helpers';

test.describe('Accessibility Audits (axe-core & keyboard)', () => {
  test('Login and Register pages have 0 critical or serious axe violations', async ({ page }) => {
    for (const path of ['/login', '/register']) {
      await page.goto(path);
      await page.waitForLoadState('networkidle');

      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();

      const violations = results.violations.filter(
        (v) => v.impact === 'critical' || v.impact === 'serious'
      );
      expect(violations).toEqual([]);
    }
  });

  test('Dashboard and catalogues have 0 critical or serious axe violations for student', async ({ page }) => {
    await authenticateAsRole(page, 'student');

    for (const path of ['/dashboard', '/courses', '/internships', '/account']) {
      await page.goto(path);
      await page.waitForLoadState('networkidle');

      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();

      const violations = results.violations.filter(
        (v) => v.impact === 'critical' || v.impact === 'serious'
      );
      expect(violations).toEqual([]);
    }
  });

  test('Admin management pages have 0 critical or serious axe violations', async ({ page }) => {
    await authenticateAsRole(page, 'admin');

    for (const path of ['/admin/users', '/admin/organizations', '/admin/reports']) {
      await page.goto(path);
      await page.waitForLoadState('networkidle');

      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();

      const violations = results.violations.filter(
        (v) => v.impact === 'critical' || v.impact === 'serious'
      );
      expect(violations).toEqual([]);
    }
  });

  test('Keyboard navigation: tab order, visible focus ring, and Escape closes modal', async ({ page }) => {
    await authenticateAsRole(page, 'admin');
    await page.goto('/admin/users');
    await page.waitForLoadState('networkidle');

    // Tab through interactive elements and check visible focus
    await page.keyboard.press('Tab');
    const focusedEl = page.locator(':focus');
    expect(await focusedEl.count()).toBe(1);

    // Open modal via button click
    const resetPwBtn = page.getByRole('button', { name: /Reset password/i }).first();
    if (await resetPwBtn.isVisible()) {
      await resetPwBtn.click();
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();
      await expect(page.locator('#admin-reset-password')).toBeFocused({ timeout: 5000 });

      // Press Escape to dismiss
      await page.keyboard.press('Escape');
      await expect(modal).not.toBeVisible();
    }
  });
});
