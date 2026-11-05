import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
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

export const AUTH_DIR = fileURLToPath(new URL('./.auth', import.meta.url));

export const AUTH_FILES: Record<DemoRole, string> = {
  student: path.join(AUTH_DIR, 'student.json'),
  instructor: path.join(AUTH_DIR, 'instructor.json'),
  organization: path.join(AUTH_DIR, 'organization.json'),
  coordinator: path.join(AUTH_DIR, 'coordinator.json'),
  admin: path.join(AUTH_DIR, 'admin.json'),
};

/**
 * Switch session cookies instantly using pre-authenticated storage states.
 * Falls back to UI login if storage state is missing.
 */
export async function authenticateAsRole(page: Page, role: DemoRole): Promise<void> {
  const filePath = AUTH_FILES[role];
  if (fs.existsSync(filePath)) {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    await page.context().clearCookies();
    if (data.cookies && data.cookies.length > 0) {
      await page.context().addCookies(data.cookies);
      return;
    }
  }
  await loginAs(page, DEMO_USERS[role]);
}

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
  const logoutBtn = page
    .locator('#header-logout-button')
    .or(page.getByRole('button', { name: /Log out|Sign out/i }))
    .first();
  await logoutBtn.waitFor({ state: 'visible', timeout: 10000 });
  await logoutBtn.click();
  await page.waitForURL((url) => url.pathname.includes('/login'), { timeout: 10000 });
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
