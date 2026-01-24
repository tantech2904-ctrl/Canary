import { test, expect } from '@playwright/test'

test('landing page loads', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('RegimeShift Sentinel')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Login' })).toBeVisible()
})
