// Example Playwright spec for one flow. Copy to e2e/f01-book.spec.ts and adapt.
// Selectors use roles and labels, so they survive restyling and the rebrand.
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('F01 guest books a meeting', () => {
  test.beforeEach(async ({ page }) => {
    page.on('console', (msg) => {
      if (msg.type() === 'error') throw new Error(`console error: ${msg.text()}`);
    });
    page.on('response', (res) => {
      if (res.status() >= 500) throw new Error(`${res.status()} on ${res.url()}`);
    });
  });

  test('F01-H1 happy path', async ({ page }) => {
    await page.goto('/u/demo/30min');
    await page.getByRole('button', { name: /next available day/i }).click();
    await page.getByRole('button', { name: /10:00/ }).click();
    await page.getByLabel('Name').fill('Test Guest');
    await page.getByLabel('Email').fill('guest@example.test');
    await page.getByRole('button', { name: /confirm/i }).click();
    await expect(page.getByRole('heading', { name: /you are booked/i })).toBeVisible();

    const a11y = await new AxeBuilder({ page }).analyze();
    expect(a11y.violations).toEqual([]);
  });

  test('F01-E1 double submit creates one booking', async ({ page }) => {
    await page.goto('/u/demo/30min');
    await page.getByRole('button', { name: /next available day/i }).click();
    await page.getByRole('button', { name: /11:00/ }).click();
    await page.getByLabel('Name').fill('Twice');
    await page.getByLabel('Email').fill('twice@example.test');
    const confirm = page.getByRole('button', { name: /confirm/i });
    await Promise.all([confirm.click(), confirm.click()]);
    await expect(page.getByRole('heading', { name: /you are booked/i })).toBeVisible();
    // Then assert through your API or DB helper that exactly one booking exists.
  });
});
