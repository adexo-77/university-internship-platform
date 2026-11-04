import { expect, test } from '@playwright/test';
import { DEMO_PASSWORD, DEMO_USERS, loginAs } from './helpers';

test.describe('Error Paths & Edge Cases', () => {
  test('404 not-found page displays friendly message and return home link', async ({ page }) => {
    await page.goto('/unknown-nonexistent-route-404');
    await page.waitForLoadState('networkidle');

    await expect(page.getByRole('heading', { name: /Page not found/i })).toBeVisible();
    await expect(
      page.getByText(/The page you requested does not exist on this platform/i)
    ).toBeVisible();

    const returnLink = page.getByRole('link', { name: /Return to/i }).first();
    await expect(returnLink).toBeVisible();
    await returnLink.click();
    await page.waitForURL((url) => !url.pathname.includes('/unknown'), { timeout: 10000 });
  });

  test('forbidden access-denied displays allowed roles and Back to dashboard link', async ({
    page,
  }) => {
    await loginAs(page, DEMO_USERS.student);
    await page.goto('/admin/users');
    await page.waitForLoadState('networkidle');

    await expect(page.getByRole('heading', { name: /don't have access/i })).toBeVisible();
    await expect(page.getByText(/only available to admin accounts/i)).toBeVisible();

    const backBtn = page.getByRole('button', { name: 'Back to dashboard' });
    await expect(backBtn).toBeVisible();
    await backBtn.click();
    await page.waitForURL(/\/dashboard/, { timeout: 10000 });
  });

  test('401 unauthenticated redirect retains target path in navigation state', async ({ page }) => {
    await loginAs(page, DEMO_USERS.student);
    await page.context().clearCookies();

    // Access protected route while unauthenticated
    await page.goto('/my-courses');
    await page.waitForURL((url) => url.pathname.includes('/login'), { timeout: 10000 });

    // Log in and verify return to origin destination (/my-courses)
    await page.fill('#login-email', DEMO_USERS.student);
    await page.fill('#login-password', DEMO_PASSWORD);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/my-courses/, { timeout: 10000 });
    expect(page.url()).toContain('/my-courses');
  });

  test('empty states render on zero-result search and clear restores data', async ({ page }) => {
    await loginAs(page, DEMO_USERS.student);
    await page.goto('/courses');
    await page.waitForLoadState('networkidle');

    const searchInput = page.locator('#course-search');
    await searchInput.fill('xyznonexistentquery999');
    await page.getByRole('button', { name: 'Search' }).click();

    await expect(page.getByRole('heading', { name: 'No courses found' })).toBeVisible();
    await expect(page.getByText(/No courses matched "xyznonexistentquery999"/i)).toBeVisible();

    // Clear search
    await page.getByRole('button', { name: 'Clear' }).click();
    await expect(page.getByRole('table')).toBeVisible();
  });

  test('dashboard network failure displays error banner with functioning retry action', async ({
    page,
  }) => {
    await loginAs(page, DEMO_USERS.student);

    // Mock API failure for dashboard student endpoint
    await page.route('**/api/dashboard/**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Simulated downstream service disruption' }),
      });
    });

    await page.goto('/dashboard');
    await expect(page.getByText(/Simulated downstream service disruption/i)).toBeVisible();

    const retryBtn = page.getByRole('button', { name: 'Retry' });
    await expect(retryBtn).toBeVisible();

    // Remove route mock and retry
    await page.unroute('**/api/dashboard/**');
    await retryBtn.click();

    await expect(page.getByText(/Simulated downstream service disruption/i)).toHaveCount(0);
    await expect(page.getByText(/Milestones & Badges|Achievements/i)).toBeVisible();
  });
});
