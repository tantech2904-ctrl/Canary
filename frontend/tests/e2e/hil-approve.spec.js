import { test, expect } from '@playwright/test'

test('upload -> detect -> approve mitigation', async ({ page }) => {
  // 1) Login via UI (stores JWT in localStorage)
  await page.goto('/login')
  await page.getByLabel('Username').fill('analyst')
  await page.getByLabel('Password').fill('analyst123')
  await page.getByRole('button', { name: 'Sign in' }).click()
  await expect(page).toHaveURL(/\/dashboard/)

  // 2) Upload synthetic metrics via UI
  await page.goto('/upload')
  await expect(page.getByText('Upload metrics JSON')).toBeVisible()

  const now = Date.now()
  const baseTime = new Date(now)
  const points = []
  for (let i = 0; i < 80; i++) {
    points.push({ timestamp: new Date(baseTime.getTime() + i * 60_000).toISOString(), value: 0.0 })
  }
  for (let i = 80; i < 160; i++) {
    points.push({ timestamp: new Date(baseTime.getTime() + i * 60_000).toISOString(), value: 2.8 })
  }
  const payload = {
    run_name: `e2e-mean-shift-${Date.now()}`,
    description: 'Playwright E2E mean shift',
    metrics: points,
  }

  await page
    .getByTestId('upload-file')
    .setInputFiles({
      name: 'e2e-metrics.json',
      mimeType: 'application/json',
      buffer: Buffer.from(JSON.stringify(payload), 'utf-8'),
    })

  await expect(page.getByTestId('upload-preview')).toBeVisible()
  await page.getByRole('button', { name: 'Upload' }).click()

  // Upload page navigates to the created run
  await expect(page).toHaveURL(/\/runs\/(\d+)/)

  // 3) Approve first mitigation
  await expect(page.getByText('Mitigation suggestions (advisory)')).toBeVisible()

  const approveBtn = page.getByRole('button', { name: 'Approve' }).first()
  await expect(approveBtn).toBeEnabled()
  await approveBtn.click()

  // The row should show approved after refresh
  await expect(page.getByText('approved')).toBeVisible()
})
