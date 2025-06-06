import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('should load and display the app name', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Attempt|MCP|Practitioner/i);
    // Optionally check for a key element
    await expect(page.locator('body')).toContainText(["MCP", "Workflow", "Dashboard"]);
  });
}); 