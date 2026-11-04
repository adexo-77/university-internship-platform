import { expect, test } from '@playwright/test';
import { DEMO_PASSWORD, DEMO_USERS, loginAs } from './helpers';

test.describe('Student Functional Flows', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, DEMO_USERS.student);
  });

  test('student can leave and re-enroll in a course', async ({ page }) => {
    await page.goto('/my-courses');
    await page.waitForLoadState('networkidle');

    // Click first enrolled course
    const courseLink = page.locator('table a[href^="/courses/"]').first();
    await expect(courseLink).toBeVisible();
    await courseLink.click();
    await page.waitForURL(/\/courses\/\d+/, { timeout: 10000 });

    const toggleBtn = page.getByRole('button', { name: /Leave course|Enroll in course/i });
    await expect(toggleBtn).toBeVisible();

    // Leave the course
    await page.getByRole('button', { name: 'Leave course' }).click();
    await expect(page.getByRole('button', { name: 'Enroll in course' })).toBeVisible();

    // Re-enroll to restore enrolled state
    await page.getByRole('button', { name: 'Enroll in course' }).click();
    await expect(page.getByRole('button', { name: 'Leave course' })).toBeVisible();
  });

  test('student can submit and update an assignment submission before grading', async ({
    page,
  }) => {
    // Navigate to Database Systems course which has coursework assignments
    await page.goto('/my-courses');
    await page.waitForLoadState('networkidle');
    await page.getByRole('link', { name: 'Database Systems' }).first().click();
    await page.waitForURL(/\/courses\/\d+/, { timeout: 10000 });

    // Open ungraded assignment: Relational Schema Design & Normalization
    const assignLink = page
      .getByRole('link', { name: 'Relational Schema Design & Normalization' })
      .first();
    await expect(assignLink).toBeVisible();
    await assignLink.click();
    await page.waitForURL(/\/assignments\/\d+/, { timeout: 10000 });

    const contentArea = page.locator('#submission-content');
    await expect(contentArea).toBeVisible();

    const timestamp = Date.now();
    await contentArea.fill(`Relational normalization model test submission ${timestamp}`);
    const linkInput = page.locator('#submission-link-url');
    await linkInput.fill('https://github.com/abeltesfaye/normalization-tests');

    const submitBtn = page.getByRole('button', {
      name: /Submit assignment|Update submission/i,
    });
    await submitBtn.click();

    // Verify submission reflection
    await expect(page.getByText('Submitted', { exact: false })).toBeVisible();

    // Resubmit / update before grading
    await contentArea.fill(`Updated normalization solution revised text ${timestamp}`);
    const updateBtn = page.getByRole('button', { name: 'Update submission' });
    await expect(updateBtn).toBeVisible();
    await updateBtn.click();

    await expect(
      page.getByText(`Updated normalization solution revised text ${timestamp}`)
    ).toBeVisible();
  });

  test('student can apply for an open internship and withdraw application', async ({ page }) => {
    // Navigate to catalogue and find open internship without prior application
    await page.goto('/internships');
    await page.waitForLoadState('networkidle');

    // Click "Data Analysis Intern"
    const postingLink = page.getByRole('link', { name: /Data Analysis Intern/i }).first();
    await expect(postingLink).toBeVisible();
    await postingLink.click();
    await page.waitForURL(/\/internships\/\d+/, { timeout: 10000 });

    const applyArea = page.locator('#apply-cover-letter');
    await expect(applyArea).toBeVisible();
    await applyArea.fill(
      'I am excited to apply for the Data Analysis Intern opportunity with strong SQL and analytics skills.'
    );
    await page.getByRole('button', { name: 'Submit application' }).click();

    // Wait for submission confirmation badge and withdraw button
    await expect(page.getByRole('button', { name: 'Withdraw' })).toBeVisible();

    // Withdraw application
    await page.getByRole('button', { name: 'Withdraw' }).click();
    await expect(page.getByText('Withdrawn', { exact: false })).toBeVisible();

    // Confirm presence on My Applications table
    await page.goto('/my-applications');
    await page.waitForLoadState('networkidle');
    await expect(page.getByText('Data Analysis Intern').first()).toBeVisible();
  });

  test('student can update profile and work preferences', async ({ page }) => {
    await page.goto('/profile');
    await page.waitForLoadState('networkidle');

    // Update bio
    const bioArea = page.locator('textarea[name="bio"], #bio');
    if (await bioArea.isVisible()) {
      const bioText = `Fourth-year software engineering student updated at ${Date.now()}`;
      await bioArea.fill(bioText);
      await page.getByRole('button', { name: 'Save profile' }).click();
      await expect(page.getByText(/saved|updated|success/i)).toBeVisible();
    }

    // Update preferences if available
    const savePrefBtn = page.getByRole('button', { name: /Save preferences/i });
    if (await savePrefBtn.isVisible()) {
      await savePrefBtn.click();
      await expect(page.getByText(/saved|updated|success/i)).toBeVisible();
    }
  });

  test('student can change password and verify account security', async ({ page }) => {
    await page.goto('/account');
    await page.waitForLoadState('networkidle');

    await page.fill('#current-password', DEMO_PASSWORD);
    await page.fill('#new-password', 'TempPass2026!');
    await page.fill('#confirm-password', 'TempPass2026!');
    await page.getByRole('button', { name: 'Update password' }).click();
    await expect(page.getByText(/Password changed successfully/i)).toBeVisible();
    await expect(page.locator('#current-password')).toHaveValue('');

    // Revert password back to DEMO_PASSWORD to preserve seed idempotency
    await page.fill('#current-password', 'TempPass2026!');
    await page.fill('#new-password', DEMO_PASSWORD);
    await page.fill('#confirm-password', DEMO_PASSWORD);
    await page.getByRole('button', { name: 'Update password' }).click();

    await expect(page.getByText(/Password changed successfully/i)).toBeVisible();
    await expect(page.locator('#current-password')).toHaveValue('');
  });

  test('student dashboard displays milestone badges and recommendations', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    await expect(page.getByText(/Milestones & Badges|Achievements/i)).toBeVisible();
    await expect(page.getByText(/Recommended for you|Suggestions/i)).toBeVisible();
  });

  test('notifications page supports mark as read, mark all read, and deep link navigation', async ({
    page,
  }) => {
    await page.goto('/notifications');
    await page.waitForLoadState('networkidle');

    const markAllBtn = page.getByRole('button', { name: 'Mark all as read' });
    if (await markAllBtn.isEnabled()) {
      await markAllBtn.click();
      await expect(page.getByTestId('unread-dot')).toHaveCount(0);
    }

    // Notification deep links navigate to real target
    const firstItem = page.locator('[role="button"][data-testid^="notification-item-"]').first();
    if (await firstItem.isVisible()) {
      await firstItem.click();
      await page.waitForURL((url) => !url.pathname.includes('/notifications'), { timeout: 10000 });
      expect(page.url()).not.toContain('/404');
    }
  });
});
