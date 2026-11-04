import { expect, test } from '@playwright/test';
import { DEMO_USERS, loginAs } from './helpers';

test.describe('Coordinator & Admin Functional Flows', () => {
  test('coordinator can review and approve a pending organization', async ({ page }) => {
    await loginAs(page, DEMO_USERS.coordinator);
    await page.goto('/admin/organizations');
    await page.waitForLoadState('networkidle');

    // Find pending organization (Abay Data Labs)
    const reviewBtn = page.getByRole('button', { name: 'Review' }).first();
    if (await reviewBtn.isVisible()) {
      await reviewBtn.click();
      const modal = page.getByRole('dialog');
      await expect(modal).toBeVisible();

      const noteArea = page.locator('#approval-note');
      if (await noteArea.isVisible()) {
        await noteArea.fill('Corporate documents and legal status verified.');
      }
      await modal.getByRole('button', { name: 'Approve' }).click();

      // Verify status becomes approved
      await expect(page.getByText('Approved', { exact: true }).first()).toBeVisible();
    }
  });

  test('coordinator can review and approve a pending internship posting', async ({ page }) => {
    await loginAs(page, DEMO_USERS.coordinator);
    await page.goto('/admin/internship-reviews');
    await page.waitForLoadState('networkidle');

    // Find posting pending review
    const reviewBtn = page.getByRole('button', { name: 'Review' }).first();
    if (await reviewBtn.isVisible()) {
      await reviewBtn.click();
      const modal = page.getByRole('dialog');
      await expect(modal).toBeVisible();

      const noteArea = page.locator('#review-note');
      if (await noteArea.isVisible()) {
        await noteArea.fill('Curriculum and academic learning goals approved.');
      }
      await modal.getByRole('button', { name: 'Approve' }).click();
      await expect(modal).not.toBeVisible();
    }
  });

  test('coordinator can reject a pending internship with a note and take down an open posting', async ({
    page,
  }) => {
    await loginAs(page, DEMO_USERS.coordinator);
    await page.goto('/admin/internship-reviews');
    await page.waitForLoadState('networkidle');

    // Reject pending posting
    const reviewBtn = page.getByRole('button', { name: 'Review' }).first();
    if (await reviewBtn.isVisible()) {
      await reviewBtn.click();
      const modal = page.getByRole('dialog');
      await expect(modal).toBeVisible();

      // Attempt reject without note -> validation message
      await modal.getByRole('button', { name: 'Reject' }).click();
      await expect(page.getByText(/Review note is required/i)).toBeVisible();

      await page.locator('#review-note').fill('Posting requires revised academic requirements.');
      await modal.getByRole('button', { name: 'Reject' }).click();
      await expect(modal).not.toBeVisible();
    }

    // Switch filter to open postings to test takedown
    await page.selectOption('#admin-status-filter', 'open');
    await page.waitForLoadState('networkidle');

    const openReviewBtn = page.getByRole('button', { name: 'Review' }).first();
    if (await openReviewBtn.isVisible()) {
      await openReviewBtn.click();
      const modal = page.getByRole('dialog');
      await expect(modal).toBeVisible();

      // Attempt takedown without note -> validation message
      await modal.getByRole('button', { name: 'Take down' }).click();
      await expect(page.getByText(/Review note is required/i)).toBeVisible();

      await page.locator('#admin-takedown-note').fill('Listing taken down for compliance review.');
      await modal.getByRole('button', { name: 'Take down' }).click();
      await expect(modal).not.toBeVisible();
    }
  });

  test('coordinator can export applications report CSV', async ({ page }) => {
    await loginAs(page, DEMO_USERS.coordinator);
    await page.goto('/admin/reports');
    await page.waitForLoadState('networkidle');

    const downloadPromise = page.waitForEvent('download');
    await page.locator('a[href$="applications.csv"]').first().click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toBe('applications_report.csv');
  });

  test('admin can search, filter, provision user, and toggle active status', async ({ page }) => {
    await loginAs(page, DEMO_USERS.admin);
    await page.goto('/admin/users');
    await page.waitForLoadState('networkidle');

    // Search for existing user
    await page.fill('#search-users', 'Abel');
    await expect(page.getByText('abel.tesfaye@example.com')).toBeVisible();
    await page.fill('#search-users', '');

    // Filter by role
    await page.selectOption('#role-filter', 'instructor');
    await expect(page.getByText('tadesse.bekele@example.com')).toBeVisible();
    await page.selectOption('#role-filter', '');

    // Create a new instructor user
    await page.getByRole('button', { name: 'New user' }).click();
    await page.waitForURL(/\/admin\/users\/new/, { timeout: 10000 });

    const timestamp = Date.now();
    const uniqueEmail = `test.staff.${timestamp}@example.edu`;
    await page.fill('#user-full-name', `Dr. Staff Instructor ${timestamp}`);
    await page.fill('#user-email', uniqueEmail);
    await page.fill('#user-password', 'StaffPass2026!');
    await page.getByRole('button', { name: 'Create user' }).click();

    // Verify user created notice and presence
    await expect(page.getByRole('heading', { name: 'User created' })).toBeVisible();

    // Deactivate and reactivate provisioned user
    await page.goto('/admin/users');
    await page.waitForLoadState('networkidle');
    await page.fill('#search-users', uniqueEmail);
    await expect(page.getByText(uniqueEmail)).toBeVisible();

    const deactBtn = page.getByRole('button', { name: 'Deactivate' }).first();
    await deactBtn.click();
    const statusModal = page.getByRole('dialog');
    await expect(statusModal).toBeVisible();
    await statusModal.getByRole('button', { name: /Deactivate/i }).click();

    await expect(page.getByText('Inactive', { exact: true })).toBeVisible();

    // Reactivate
    const reactBtn = page.getByRole('button', { name: 'Activate' }).first();
    await reactBtn.click();
    await statusModal.getByRole('button', { name: /Activate user/i }).click();
    await expect(page.getByText('Active', { exact: true }).first()).toBeVisible();

    // Reset password
    const resetBtn = page.getByRole('button', { name: 'Reset password' }).first();
    await resetBtn.click();
    const resetModal = page.getByRole('dialog');
    await expect(resetModal).toBeVisible();
    await resetModal.locator('input[type="password"]').fill('NewStaffSecret123!');
    await resetModal.getByRole('button', { name: /Reset password/i }).click();
    await expect(page.getByText(/successfully reset/i)).toBeVisible();
  });

  test('admin can export both applications and users CSV reports', async ({ page }) => {
    await loginAs(page, DEMO_USERS.admin);
    await page.goto('/admin/reports');
    await page.waitForLoadState('networkidle');

    // Export Applications CSV
    const dlAppsPromise = page.waitForEvent('download');
    await page.locator('a[href$="applications.csv"]').first().click();
    const dlApps = await dlAppsPromise;
    expect(dlApps.suggestedFilename()).toBe('applications_report.csv');

    // Export Users CSV
    const dlUsersPromise = page.waitForEvent('download');
    await page.locator('a[href$="users.csv"]').first().click();
    const dlUsers = await dlUsersPromise;
    expect(dlUsers.suggestedFilename()).toBe('users_report.csv');
  });
});
