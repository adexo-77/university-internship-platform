import { expect, test } from '@playwright/test';
import { authenticateAsRole } from '../helpers';

test.describe('Instructor Functional Flows', () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAsRole(page, 'instructor');
  });

  test('instructor can create, edit, and publish a course', async ({ page }) => {
    await page.goto('/courses/new');
    await page.waitForLoadState('networkidle');

    const timestamp = Date.now();
    const courseTitle = `Cloud Native Systems ${timestamp}`;
    await page.fill('#course-title', courseTitle);
    await page.fill(
      '#course-description',
      'Architectures for scalable microservices, containerization, and distributed storage.'
    );
    await page.selectOption('#course-status', 'draft');
    await page.getByRole('button', { name: 'Create course' }).click();

    await page.waitForURL(/\/courses\/\d+/, { timeout: 10000 });
    await expect(page.getByRole('heading', { name: courseTitle })).toBeVisible();
    await expect(page.getByText('Draft', { exact: true })).toBeVisible();

    // Edit and publish course
    await page.getByRole('link', { name: 'Edit course' }).click();
    await page.waitForURL(/\/courses\/\d+\/edit/, { timeout: 10000 });

    const updatedTitle = `${courseTitle} (Advanced)`;
    await page.fill('#course-title', updatedTitle);
    await page.selectOption('#course-status', 'published');
    await page.getByRole('button', { name: 'Save changes' }).click();

    await page.waitForURL(/\/courses\/\d+/, { timeout: 10000 });
    await expect(page.getByRole('heading', { name: updatedTitle })).toBeVisible();
    await expect(page.getByText('Published', { exact: true })).toBeVisible();
  });

  test('instructor can create, edit, and delete an assignment with zero submissions', async ({
    page,
  }) => {
    // Navigate to instructor course via /my-courses
    await page.goto('/my-courses');
    await page.waitForLoadState('networkidle');
    await page.getByRole('link', { name: 'Introduction to Programming' }).first().click();
    await page.waitForURL(/\/courses\/\d+/, { timeout: 10000 });

    // Open new assignment page
    await page.getByRole('link', { name: 'New assignment' }).click();
    await page.waitForURL(/\/courses\/\d+\/assignments\/new/, { timeout: 10000 });

    const timestamp = Date.now();
    const assignTitle = `Algorithms Lab ${timestamp}`;
    await page.fill('#assignment-title', assignTitle);
    await page.fill(
      '#assignment-description',
      'Implement binary search trees and analyze traversal runtimes.'
    );

    const futureDate = new Date(Date.now() + 7 * 86400000);
    const pad = (n: number) => String(n).padStart(2, '0');
    const localIso = `${futureDate.getFullYear()}-${pad(futureDate.getMonth() + 1)}-${pad(futureDate.getDate())}T14:00`;
    await page.fill('#assignment-due-at', localIso);
    await page.fill('#assignment-max-points', '100');
    await page.getByRole('button', { name: 'Create assignment' }).click();

    await page.waitForURL(/\/courses\/\d+/, { timeout: 10000 });
    await expect(page.getByText(assignTitle)).toBeVisible();

    // Open created assignment to edit points
    await page.getByRole('link', { name: assignTitle }).first().click();
    await page.waitForURL(/\/assignments\/\d+/, { timeout: 10000 });
    await expect(page.getByRole('heading', { name: assignTitle })).toBeVisible();

    await page.getByRole('link', { name: 'Edit assignment' }).click();
    await page.waitForURL(/\/assignments\/\d+\/edit/, { timeout: 10000 });
    await page.fill('#assignment-max-points', '150');
    await page.getByRole('button', { name: 'Save changes' }).click();
    await page.waitForURL(/\/assignments\/\d+/, { timeout: 10000 });
    await expect(page.getByText('150 max points')).toBeVisible();

    // Delete assignment
    await page.getByRole('link', { name: 'Edit assignment' }).click();
    await page.waitForURL(/\/assignments\/\d+\/edit/, { timeout: 10000 });
    await page.getByRole('button', { name: 'Delete assignment' }).click();

    const confirmModal = page.getByRole('dialog');
    await expect(confirmModal).toBeVisible();
    await confirmModal.getByRole('button', { name: 'Delete assignment' }).click();

    await page.waitForURL(/\/courses\/\d+/, { timeout: 10000 });
    await expect(page.getByText(assignTitle)).toHaveCount(0);
  });

  test('instructor can add, edit, and delete course learning resources', async ({ page }) => {
    await page.goto('/my-courses');
    await page.waitForLoadState('networkidle');
    await page.getByRole('link', { name: 'Introduction to Programming' }).first().click();
    await page.waitForURL(/\/courses\/\d+/, { timeout: 10000 });

    // Open add resource modal
    await page.getByRole('button', { name: 'Add resource' }).click();
    const modal = page.getByRole('dialog');
    await expect(modal).toBeVisible();

    const timestamp = Date.now();
    const resourceTitle = `Official Documentation ${timestamp}`;
    await page.fill('#resource-title', resourceTitle);
    await page.fill('#resource-url', 'https://docs.python.org/3/');
    await page.fill('#resource-description', 'Standard library tutorial and language reference.');
    await modal.getByRole('button', { name: 'Add resource' }).click();

    await expect(page.getByText(resourceTitle)).toBeVisible();

    // Edit resource
    await page.getByRole('button', { name: 'Edit' }).first().click();
    await expect(modal).toBeVisible();
    const updatedTitle = `${resourceTitle} v3.12`;
    await page.fill('#resource-title', updatedTitle);
    await modal.getByRole('button', { name: 'Save changes' }).click();
    await expect(page.getByText(updatedTitle)).toBeVisible();

    // Delete resource
    await page.getByRole('button', { name: 'Delete' }).first().click();
    const deleteModal = page.getByRole('dialog');
    await expect(deleteModal).toBeVisible();
    await deleteModal.getByRole('button', { name: 'Delete resource' }).click();

    await expect(page.getByText(updatedTitle)).toHaveCount(0);
  });

  test('instructor can grade student submission and export gradebook CSV', async ({ page }) => {
    await page.goto('/my-courses');
    await page.waitForLoadState('networkidle');
    await page.getByRole('link', { name: 'Database Systems' }).first().click();
    await page.waitForURL(/\/courses\/\d+/, { timeout: 10000 });

    // Download Gradebook CSV
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('link', { name: 'Export CSV' }).first().click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/course_\d+_gradebook\.csv$/);

    // Navigate to assignment to grade work
    await page.getByRole('link', { name: 'ER Diagramming & Conceptual Modeling' }).first().click();
    await page.waitForURL(/\/assignments\/\d+/, { timeout: 10000 });

    // Click grade button in student submissions roster
    const gradeBtn = page.getByRole('button', { name: /Grade|Regrade/i }).first();
    await expect(gradeBtn).toBeVisible();
    await gradeBtn.click();
    await page.waitForURL(/\/assignments\/\d+\/submissions\/\d+\/grade/, { timeout: 10000 });

    await page.fill('#grade-input', '96');
    await page.fill('#feedback-input', 'Outstanding ER diagram, clean cardinalities and notations.');
    await page.getByRole('button', { name: 'Save grade' }).click();

    await page.waitForURL(/\/assignments\/\d+/, { timeout: 10000 });
    await expect(page.getByText('96 / 100')).toBeVisible();
  });
});
