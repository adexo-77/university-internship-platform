import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';
import { assertNoHorizontalOverflow, authenticateAsRole } from '../helpers';

test.describe('Student Study Plan & Progress Summary', () => {
  test('renders full study plan, toggles window, rules disclosure, and accessibility', async ({
    page,
  }) => {
    await authenticateAsRole(page, 'student');
    await page.goto('/study-plan');
    await page.waitForLoadState('networkidle');

    // 1. Assert Back link and page header
    const backLink = page.getByTestId('back-link');
    await expect(backLink).toBeVisible();
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(
      'Study plan & weekly progress'
    );

    // 2. Assert prominent summary card, sentences, and metric pills
    const summaryCard = page.getByTestId('study-plan-summary-card');
    await expect(summaryCard).toBeVisible();
    await expect(summaryCard.getByText('Courses', { exact: true })).toBeVisible();
    await expect(summaryCard.getByText('Pending tasks', { exact: true })).toBeVisible();
    await expect(summaryCard.getByText('Minutes planned', { exact: true })).toBeVisible();
    await expect(summaryCard.getByText('Overdue', { exact: true })).toBeVisible();

    // 3. Assert schedule by day
    const schedule = page.getByTestId('study-plan-schedule');
    await expect(schedule).toBeVisible();

    // 4. Switch between 7 days and 14 days
    const selector14 = page.getByTestId('days-selector-14');
    await expect(selector14).toBeVisible();
    await selector14.click();
    await page.waitForLoadState('networkidle');
    await expect(selector14).toHaveAttribute('aria-pressed', 'true');
    await expect(page).toHaveURL(/days=14/);

    const selector7 = page.getByTestId('days-selector-7');
    await selector7.click();
    await page.waitForLoadState('networkidle');
    await expect(selector7).toHaveAttribute('aria-pressed', 'true');

    // 5. Expand deterministic rules disclosure
    const disclosureButton = page.getByRole('button', { name: /How this plan is made/i });
    await expect(disclosureButton).toBeVisible();
    await disclosureButton.click();

    const rulesContent = page.getByTestId('study-plan-rules-content');
    await expect(rulesContent).toBeVisible();
    await expect(rulesContent).toContainText('deterministic');
    await expect(rulesContent).toContainText('120 minutes');

    // 6. Responsive check at 360px without horizontal overflow
    await page.setViewportSize({ width: 360, height: 640 });
    await assertNoHorizontalOverflow(page);

    // 7. Accessibility audit (axe-core)
    const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
    const violations = results.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious'
    );
    expect(violations).toEqual([]);
  });
});
