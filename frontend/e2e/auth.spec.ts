import { expect, test } from '@playwright/test';
import { DEMO_PASSWORD, DEMO_USERS, loginAs, logout } from './helpers';

test.describe('Authentication Form Verification', () => {
  test('login with valid credentials authenticates and redirects to dashboard', async ({
    page,
  }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    await page.fill('#login-email', DEMO_USERS.student);
    await page.fill('#login-password', DEMO_PASSWORD);
    await page.click('button[type="submit"]');

    await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 15000 });
    expect(page.url()).toContain('/account');
    await expect(page.getByText('Account profile')).toBeVisible();

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    await expect(page.getByText(/Enrolled Courses|Recent Grades/i).first()).toBeVisible();
  });

  test('login with invalid password shows error banner and refuses access', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    await page.fill('#login-email', DEMO_USERS.student);
    await page.fill('#login-password', 'WrongPassword123!');
    await page.click('button[type="submit"]');

    await expect(page.getByText(/Invalid email or password/i)).toBeVisible();
    expect(page.url()).toContain('/login');
  });

  test('logout from account menu clears session and redirects to login', async ({ page }) => {
    await loginAs(page, DEMO_USERS.student);
    await logout(page);

    expect(page.url()).toContain('/login');
    await page.goto('/dashboard');
    await page.waitForURL((url) => url.pathname.includes('/login'), { timeout: 10000 });
    expect(page.url()).toContain('/login');
  });
});
