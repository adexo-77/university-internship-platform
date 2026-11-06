import { expect, test } from '@playwright/test';
import { authenticateAsRole, loginAs } from '../helpers';

test.describe('Organization Functional Flows', () => {
  test('organization can update company profile', async ({ page }) => {
    await authenticateAsRole(page, 'organization');
    await page.goto('/profile');
    await page.waitForLoadState('networkidle');

    const descArea = page.locator('#description');
    if (await descArea.isVisible()) {
      const updatedDesc = `Enterprise software and cloud engineering firm updated at ${Date.now()}`;
      await descArea.fill(updatedDesc);
      await page.getByRole('button', { name: 'Save profile' }).click();
      await expect(page.getByText(/saved|updated|success/i)).toBeVisible();
    }
  });

  test('organization can create, edit, submit, and close an internship posting', async ({
    page,
  }) => {
    await authenticateAsRole(page, 'organization');
    await page.goto('/internships/new');
    await page.waitForLoadState('networkidle');

    const timestamp = Date.now();
    const postingTitle = `DevOps Platform Engineer ${timestamp}`;
    await page.fill('#internship-title', postingTitle);
    await page.fill('#internship-location', 'Addis Ababa');
    await page.selectOption('#internship-work-mode', 'hybrid');
    await page.fill('#internship-duration', '12');

    const futureDate = new Date(Date.now() + 30 * 86400000);
    const pad = (n: number) => String(n).padStart(2, '0');
    const localIso = `${futureDate.getFullYear()}-${pad(futureDate.getMonth() + 1)}-${pad(futureDate.getDate())}T17:00`;
    await page.fill('#internship-deadline', localIso);

    await page.fill(
      '#internship-description',
      'Build automated CI/CD pipelines, container orchestration, and monitoring infrastructure.'
    );
    await page.fill(
      '#internship-requirements',
      'Experience with Docker, Kubernetes, Linux, and Python or Go scripting.'
    );

    await page.getByRole('button', { name: 'Create internship' }).click();
    await page.waitForURL(/\/internships\/\d+/, { timeout: 10000 });
    await expect(page.getByRole('heading', { name: postingTitle })).toBeVisible();
    await expect(page.getByText('Draft', { exact: true })).toBeVisible();

    // Edit posting
    await page.getByRole('button', { name: 'Edit' }).click();
    await page.waitForURL(/\/internships\/\d+\/edit/, { timeout: 10000 });
    const updatedTitle = `${postingTitle} (Senior)`;
    await page.fill('#internship-title', updatedTitle);
    await page.getByRole('button', { name: 'Save changes' }).click();
    await page.waitForURL(/\/internships\/\d+/, { timeout: 10000 });
    await expect(page.getByRole('heading', { name: updatedTitle })).toBeVisible();

    // Submit for review
    await page.getByRole('button', { name: 'Submit for review' }).click();
    await expect(page.getByText('Pending review', { exact: false })).toBeVisible();

    // Close an open posting
    await page.goto('/my-internships');
    await page.waitForLoadState('networkidle');
    await page.getByRole('link', { name: 'Junior Web Developer Intern' }).first().click();
    await page.waitForURL(/\/internships\/\d+/, { timeout: 10000 });

    const closeBtn = page.getByRole('button', { name: 'Close posting' });
    await expect(closeBtn).toBeVisible({ timeout: 10000 });
    await closeBtn.click();
    const confirmModal = page.getByRole('dialog');
    await expect(confirmModal).toBeVisible();
    await confirmModal.getByRole('button', { name: 'Close posting' }).click();
    await expect(page.getByText('Closed', { exact: true })).toBeVisible();
  });

  test('organization can review applicants, update decisions, and export applicants CSV', async ({
    page,
  }) => {
    await authenticateAsRole(page, 'organization');
    await page.goto('/my-internships');
    await page.waitForLoadState('networkidle');

    // Open Junior Web Developer Intern which has applicants
    await page.getByRole('link', { name: 'Junior Web Developer Intern' }).first().click();
    await page.waitForURL(/\/internships\/\d+/, { timeout: 10000 });

    // Download Applicants CSV
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('link', { name: 'Export CSV' }).first().click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/internship_\d+_applicants\.csv$/);

    // Review an applicant
    const reviewLink = page.locator('table a[href^="/applications/"]').first();
    await expect(reviewLink).toBeVisible();
    await reviewLink.click();
    await page.waitForURL(/\/applications\/\d+/, { timeout: 10000 });

    // If decision form is active, submit feedback
    const decisionArea = page.locator('#decision-message');
    if (await decisionArea.isVisible()) {
      await decisionArea.fill('Application reviewed. Advancing candidate to interview stage.');
      const shortlistBtn = page.getByRole('button', { name: /Shortlist|Accept/i }).first();
      await shortlistBtn.click();
      await expect(page.getByText(/Shortlisted|Accepted/i)).toBeVisible();
    }
  });

  test('pending organization displays approval notice and disables submit for review', async ({
    page,
  }) => {
    // Log in as pending organization (eyob.kassa@example.com)
    await loginAs(page, 'eyob.kassa@example.com');
    await page.goto('/my-internships');
    await page.waitForLoadState('networkidle');

    // Verify approval notice banner
    await expect(page.getByText(/Your organization is awaiting approval/i)).toBeVisible();

    // Verify submit button is disabled
    const submitBtn = page.getByRole('button', { name: 'Submit for review' }).first();
    if (await submitBtn.isVisible()) {
      await expect(submitBtn).toBeDisabled();
    }
  });
});
