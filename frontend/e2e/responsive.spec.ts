import { test, expect, Page } from '@playwright/test';
import { authenticateAsRole, DemoRole } from './helpers';

const ACCOUNTS = [
  { role: 'student', email: 'abel.tesfaye@example.com', subpage: '/profile' },
  { role: 'admin', email: 'mulugeta.assefa@example.com', subpage: '/admin/users/new' },
];

async function assertNoHorizontalOverflow(page: Page): Promise<void> {
  const isOverflowing = await page.evaluate(() => {
    return document.documentElement.scrollWidth > window.innerWidth;
  });
  expect(isOverflowing).toBe(false);
}

test.describe('Responsive Layout & Accessibility Verifications', () => {
  for (const account of ACCOUNTS) {
    test(`role ${account.role}: no horizontal overflow and valid layout`, async ({ page }) => {
      const viewport = page.viewportSize() || { width: 1440, height: 900 };
      await authenticateAsRole(page, account.role as DemoRole);
      await assertNoHorizontalOverflow(page);

      if (viewport.width < 768) {
        // Mobile Drawer toggle test
        const openBtn = page.locator('button[aria-label="Open menu"]');
        await expect(openBtn).toBeVisible();

        const box = await openBtn.boundingBox();
        expect(box?.height).toBeGreaterThanOrEqual(43.5);
        expect(box?.width).toBeGreaterThanOrEqual(43.5);

        // Open drawer
        await openBtn.click();
        const drawer = page.locator('aside[aria-label="Navigation drawer"]');
        await expect(drawer).toBeVisible();

        const isLocked = await page.evaluate(() => document.body.style.overflow === 'hidden');
        expect(isLocked).toBe(true);

        // Close via Escape key
        await page.keyboard.press('Escape');
        const isClosed = await page.evaluate(() => document.body.style.overflow === '');
        expect(isClosed).toBe(true);
      }

      // Verify BackLink presence and 44px target on notifications
      await page.goto('/notifications');
      await assertNoHorizontalOverflow(page);
      const backLink = page.locator(':is(a, button):has-text("Back")');
      await expect(backLink.first()).toBeVisible();

      const backBox = await backLink.first().boundingBox();
      expect(backBox?.height).toBeGreaterThanOrEqual(43.5);

      // Verify BackLink presence and 44px target on role subpage
      await page.goto(account.subpage);
      await assertNoHorizontalOverflow(page);
      const subpageBack = page.locator(':is(a, button):has-text("Back")');
      await expect(subpageBack.first()).toBeVisible();
      const subpageBox = await subpageBack.first().boundingBox();
      expect(subpageBox?.height).toBeGreaterThanOrEqual(43.5);
    });
  }

  test('form controls have font-size >= 16px', async ({ page }) => {
    await page.goto('/login');
    const fontSize = await page.locator('#login-email').evaluate((el) => {
      return parseFloat(window.getComputedStyle(el).fontSize);
    });
    expect(fontSize).toBeGreaterThanOrEqual(16);
  });
});
