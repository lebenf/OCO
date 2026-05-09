// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { test, expect } from '@playwright/test'

test.describe('Container flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('/login')
    await page.fill('input[placeholder*="utente"], input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'cambia-questa-password')
    await page.click('button[type="submit"]')
    await page.waitForURL('/')
  })

  test('crea scatola → visualizza codice', async ({ page }) => {
    // Navigate to a house's containers (house must exist)
    // This test assumes at least one house the admin belongs to
    await page.goto('/houses/1/containers/create')

    // Fill description
    const descInput = page.locator('input[type="text"]').first()
    await descInput.fill('Test E2E Box')

    // Submit
    await page.click('button[type="submit"]')

    // After creation, code display should be visible
    await expect(page.locator('.code-value')).toBeVisible()
    const code = await page.locator('.code-value').textContent()
    expect(code).toMatch(/^[A-Z]-\d{3}$/)
  })
})
