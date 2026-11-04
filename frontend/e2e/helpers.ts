import { expect, Page } from '@playwright/test';

export const DEMO_PASSWORD = '12345678';

export const DEMO_USERS = {
  student: 'abel.tesfaye@example.com',
  instructor: 'tadesse.bekele@example.com',
  organization: 'yohannes.haile@example.com',
  coordinator: 'selamawit.tadesse@example.com',
  admin: 'mulugeta.assefa@example.com',
} as const;

export type DemoRole = keyof typeof DEMO_USERS;

/**
 * Log into the platform via the UI login form.
 */
export async function loginAs(page: Page, email: string, password = DEMO_PASSWORD): Promise<void> {
  await page.goto('/login');
  await page.waitForLoadState('networkidle');
  await page.fill('#login-email', email);
  await page.fill('#login-password', password);
  await page.click('button[type="submit"]');
  await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 15000 });
}

/**
 * Sign out by clicking the user account menu logout button.
 */
export async function logout(page: Page): Promise<void> {
  const logoutBtn = page.getByRole('button', { name: /Log out|Sign out/i });
  if (await logoutBtn.isVisible()) {
    await logoutBtn.click();
    await page.waitForURL((url) => url.pathname.includes('/login'), { timeout: 10000 });
  }
}

/**
 * Asserts that the document does not horizontally overflow the current viewport.
 */
export async function assertNoHorizontalOverflow(page: Page): Promise<void> {
  const isOverflowing = await page.evaluate(() => {
    return document.documentElement.scrollWidth > window.innerWidth;
  });
  expect(isOverflowing).toBe(false);
}

/**
 * Sets up listeners for uncaught console errors and page errors.
 */
export function trackErrors(page: Page): { getErrors: () => string[] } {
  const errors: string[] = [];
  page.on('pageerror', (err) => {
    errors.push(`PageError: ${err.message}`);
  });
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      const text = msg.text();
      // Ignore transient favicon or extension network errors, and normal unauthenticated 401 on /api/auth/me
      if (
        !text.includes('favicon') &&
        !text.includes('status of 404') &&
        !text.includes('status of 401')
      ) {
        errors.push(`ConsoleError: ${text}`);
      }
    }
  });
  return {
    getErrors: () => errors,
  };
}
