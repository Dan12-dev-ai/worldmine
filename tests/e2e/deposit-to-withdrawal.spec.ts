import { test, expect } from '@playwright/test';

test.describe('Deposit to Withdrawal', () => {
  test('complete deposit and withdrawal workflow', async ({ page }) => {
    // Step 1: Login
    await page.goto('https://staging.dedan.ai/login');
    await page.fill('[data-testid=email]', 'testuser@dedan.ai');
    await page.fill('[data-testid=password]', 'SecurePassword123!@#');
    await page.click('[data-testid=login-button]');
    await expect(page.locator('[data-testid=dashboard]')).toBeVisible();
    
    // Step 2: Navigate to wallet
    await page.click('[data-testid=wallet-tab]');
    await expect(page.locator('[data-testid=wallet-balance]')).toBeVisible();
    
    // Step 3: Make Bitcoin deposit
    await page.click('[data-testid=deposit]');
    await page.selectOption('[data-testid=deposit-method]', 'bitcoin');
    await page.fill('[data-testid=deposit-amount]', '0.05');
    await page.click('[data-testid=deposit-button]');
    
    // Step 4: Get deposit address
    await expect(page.locator('[data-testid=deposit-address]')).toBeVisible();
    const depositAddress = await page.locator('[data-testid=deposit-address]').inputValue();
    expect(depositAddress).toMatch(/^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$/);
    
    // Step 5: Mock blockchain confirmation
    await page.goto('https://staging.dedan.ai/wallet');
    await expect(page.locator('[data-testid=bitcoin-balance]')).toContainText('0.05');
    
    // Step 6: Initiate withdrawal
    await page.click('[data-testid=withdraw]');
    await page.selectOption('[data-testid=withdraw-method]', 'bitcoin');
    await page.fill('[data-testid=withdraw-amount]', '0.025');
    await page.fill('[data-testid=withdraw-address]', 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh');
    await page.click('[data-testid=withdraw-button]');
    
    // Step 7: Confirm withdrawal
    await page.click('[data-testid=confirm-withdraw]');
    await expect(page.locator('[data-testid=withdrawal-pending]')).toBeVisible();
    
    // Step 8: Check withdrawal status
    await page.goto('https://staging.dedan.ai/transactions');
    await expect(page.locator('[data-testid=withdrawal-status]')).toContainText('Pending');
    
    // Step 9: Mock blockchain confirmation
    await page.reload();
    await expect(page.locator('[data-testid=withdrawal-status]')).toContainText('Completed');
    
    // Step 10: Verify final balance
    const finalBalance = await page.locator('[data-testid=bitcoin-balance]').textContent();
    expect(finalBalance).toContain('0.025');
  });
});
