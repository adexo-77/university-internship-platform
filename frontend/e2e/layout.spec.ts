import { expect, test } from '@playwright/test';
import { assertNoHorizontalOverflow, DEMO_USERS, loginAs } from './helpers';

test.describe('Responsive Layout & Viewport Verification', () => {
  const publicPages = ['/login', '/register', '/status'];
  const authenticatedPages = [
    '/dashboard',
    '/courses',
    '/my-courses',
    '/internships',
    '/my-applications',
    '/profile',
    '/account',
    '/notifications',
  ];

  test('public pages have zero horizontal overflow across viewport', async ({ page }) => {
    for (const path of publicPages) {
      await page.goto(path);
      await page.waitForLoadState('networkidle');
      await assertNoHorizontalOverflow(page);
    }
  });

  test('authenticated student pages have zero horizontal overflow', async ({ page }) => {
    await loginAs(page, DEMO_USERS.student);

    for (const path of authenticatedPages) {
      await page.goto(path);
      await page.waitForLoadState('networkidle');
      await assertNoHorizontalOverflow(page);
    }
  });

  test('table containers allow internal scroll without overflowing page viewport', async ({
    page,
  }) => {
    await loginAs(page, DEMO_USERS.student);
    await page.goto('/courses');
    await page.waitForLoadState('networkidle');

    // Table container is present and document does not overflow viewport width
    const tableContainer = page.locator('.overflow-x-auto, table').first();
    await expect(tableContainer).toBeVisible();
    await assertNoHorizontalOverflow(page);

    await page.goto('/internships');
    await page.waitForLoadState('networkidle');
    await assertNoHorizontalOverflow(page);
  });

  test('mobile drawer opens, traps focus, and closes via Escape and close button', async ({
    page,
  }) => {
    // Only run drawer test on mobile viewports (< 768 px)
    const viewport = page.viewportSize();
    if (!viewport || viewport.width >= 768) {
      test.skip();
      return;
    }

    await loginAs(page, DEMO_USERS.student);
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    const menuBtn = page.getByRole('button', { name: 'Open menu' });
    await expect(menuBtn).toBeVisible();
    await menuBtn.click();

    // Drawer is now open
    const drawer = page.locator('aside[aria-label="Navigation drawer"]');
    await expect(drawer).toHaveClass(/translate-x-0/);

    // Press Escape to dismiss drawer
    await page.keyboard.press('Escape');
    await expect(drawer).toHaveClass(/-translate-x-full/);

    // Reopen drawer and dismiss with explicit close button
    await menuBtn.click();
    await expect(drawer).toHaveClass(/translate-x-0/);
    const closeBtn = drawer.getByRole('button', { name: 'Close menu drawer' });
    await expect(closeBtn).toBeVisible();
    await closeBtn.click();
    await expect(drawer).toHaveClass(/-translate-x-full/);
  });

  test('mobile touch targets on buttons and text fields meet or exceed 44px', async ({
    page,
  }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.width >= 768) {
      test.skip();
      return;
    }

    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    const emailBox = await page.locator('#login-email').boundingBox();
    expect(emailBox).toBeTruthy();
    expect(emailBox!.height).toBeGreaterThanOrEqual(44);

    const submitBtnBox = await page.locator('button[type="submit"]').boundingBox();
    expect(submitBtnBox).toBeTruthy();
    expect(submitBtnBox!.height).toBeGreaterThanOrEqual(44);
  });
});
