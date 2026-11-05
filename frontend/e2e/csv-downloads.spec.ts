import * as fs from 'fs';
import { expect, test } from '@playwright/test';
import { authenticateAsRole } from './helpers';

test.describe('CSV Exports in Real Browser Context', () => {
  test('Instructor can export course gradebook CSV', async ({ page }) => {
    await authenticateAsRole(page, 'instructor');
    await page.goto('/my-courses');
    await page.waitForLoadState('networkidle');

    // Click on the instructor's course title in the table
    const courseLink = page.locator('table a[href^="/courses/"]:not([href$="/edit"])').first();
    await expect(courseLink).toBeVisible();
    await courseLink.click();
    await page.waitForURL(/\/courses\/\d+$/, { timeout: 10000 });

    const exportBtn = page.getByRole('link', { name: 'Export CSV' }).first();
    await expect(exportBtn).toBeVisible();

    const [download] = await Promise.all([
      page.waitForEvent('download'),
      exportBtn.click(),
    ]);

    expect(download.suggestedFilename()).toMatch(/^course_\d+_gradebook\.csv$/);
    const path = await download.path();
    expect(path).toBeTruthy();

    const content = fs.readFileSync(path!, 'utf-8');
    const firstLine = content.split(/\r?\n/)[0];
    expect(firstLine).toContain('Student Name');
    expect(firstLine).toContain('Email');
  });

  test('Organization can export internship applicants CSV', async ({ page }) => {
    await authenticateAsRole(page, 'organization');
    await page.goto('/my-internships');
    await page.waitForLoadState('networkidle');

    // Click on their posting title in the table
    const postingLink = page.locator('table a[href^="/internships/"]:not([href$="/edit"])').first();
    await expect(postingLink).toBeVisible();
    await postingLink.click();
    await page.waitForURL(/\/internships\/\d+$/, { timeout: 10000 });

    const exportBtn = page.getByRole('link', { name: 'Export CSV' }).first();
    await expect(exportBtn).toBeVisible();

    const [download] = await Promise.all([
      page.waitForEvent('download'),
      exportBtn.click(),
    ]);

    expect(download.suggestedFilename()).toMatch(/^internship_\d+_applicants\.csv$/);
    const path = await download.path();
    expect(path).toBeTruthy();

    const content = fs.readFileSync(path!, 'utf-8');
    const firstLine = content.split(/\r?\n/)[0];
    expect(firstLine).toContain('Applicant Name');
    expect(firstLine).toContain('Email');
  });

  test('Coordinator can export admin reports for applications', async ({ page }) => {
    await authenticateAsRole(page, 'coordinator');
    await page.goto('/admin/reports');
    await page.waitForLoadState('networkidle');

    const exportButtons = page.getByRole('link', { name: 'Export CSV' });
    expect(await exportButtons.count()).toBe(1);

    // Export Applications report
    const [appsDownload] = await Promise.all([
      page.waitForEvent('download'),
      exportButtons.nth(0).click(),
    ]);
    expect(appsDownload.suggestedFilename()).toBe('applications_report.csv');
    const appsPath = await appsDownload.path();
    const appsContent = fs.readFileSync(appsPath!, 'utf-8');
    expect(appsContent.split(/\r?\n/)[0]).toContain('Posting');
    expect(appsContent.split(/\r?\n/)[0]).toContain('Organization');
  });

  test('Admin can export admin reports for applications and users', async ({ page }) => {
    await authenticateAsRole(page, 'admin');
    await page.goto('/admin/reports');
    await page.waitForLoadState('networkidle');

    const exportButtons = page.getByRole('link', { name: 'Export CSV' });
    expect(await exportButtons.count()).toBe(2);

    const [appsDownload] = await Promise.all([
      page.waitForEvent('download'),
      exportButtons.nth(0).click(),
    ]);
    expect(appsDownload.suggestedFilename()).toBe('applications_report.csv');
    const appsPath = await appsDownload.path();
    const appsContent = fs.readFileSync(appsPath!, 'utf-8');
    expect(appsContent.split(/\r?\n/)[0]).toContain('Posting');
    expect(appsContent.split(/\r?\n/)[0]).toContain('Organization');

    const [usersDownload] = await Promise.all([
      page.waitForEvent('download'),
      exportButtons.nth(1).click(),
    ]);
    expect(usersDownload.suggestedFilename()).toBe('users_report.csv');
    const usersPath = await usersDownload.path();
    const usersContent = fs.readFileSync(usersPath!, 'utf-8');
    expect(usersContent.split(/\r?\n/)[0]).toContain('Email');
    expect(usersContent.split(/\r?\n/)[0]).toContain('Role');
  });
});
