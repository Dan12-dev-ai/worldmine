import { test, expect } from '@playwright/test';

test.describe('Registration to First Trade', () => {
  test('complete user journey from registration to first trade', async ({ page }) => {
    // Step 1: Navigate to registration page
    await page.goto('https://staging.dedan.ai/register');
    await expect(page).toHaveTitle(/DEDAN 2.0/);
    
    // Step 2: Fill registration form
    await page.fill('[data-testid=email]', 'testuser@dedan.ai');
    await page.fill('[data-testid=password]', 'SecurePassword123!@#');
    await page.fill('[data-testid=confirm-password]', 'SecurePassword123!@#');
    await page.fill('[data-testid=first-name]', 'John');
    await page.fill('[data-testid=last-name]', 'Doe');
    await page.fill('[data-testid=company]', 'Test Trading Corp');
    await page.fill('[data-testid=phone]', '+1234567890');
    
    // Step 3: Submit registration
    await page.click('[data-testid=register-button]');
    await expect(page.locator('[data-testid=success-message]')).toBeVisible();
    
    // Step 4: Email verification (mock)
    await page.goto('https://staging.dedan.ai/verify-email?token=mock-token');
    await expect(page.locator('[data-testid=verification-success]')).toBeVisible();
    
    // Step 5: Complete KYC
    await page.goto('https://staging.dedan.ai/kyc');
    await page.fill('[data-testid=address]', '123 Test Street');
    await page.fill('[data-testid=city]', 'New York');
    await page.fill('[data-testid=country]', 'United States');
    await page.setInputFiles('[data-testid=id-document]', 'test-id.jpg');
    await page.setInputFiles('[data-testid=proof-address]', 'test-utility.pdf');
    
    await page.click('[data-testid=submit-kyc]');
    await expect(page.locator('[data-testid=kyc-pending]')).toBeVisible();
    
    // Step 6: Mock KYC approval
    await page.goto('https://staging.dedan.ai/dashboard');
    await expect(page.locator('[data-testid=kyc-approved]')).toBeVisible();
    
    // Step 7: Set up wallet
    await page.click('[data-testid=setup-wallet]');
    await page.fill('[data-testid=wallet-name]', 'Main Trading Wallet');
    await page.click('[data-testid=create-wallet]');
    await expect(page.locator('[data-testid=wallet-created]')).toBeVisible();
    
    // Step 8: Make deposit
    await page.click('[data-testid=deposit]');
    await page.selectOption('[data-testid=deposit-method]', 'bitcoin');
    await page.fill('[data-testid=deposit-amount]', '0.1');
    await page.click('[data-testid=deposit-button]');
    await expect(page.locator('[data-testid=deposit-pending]')).toBeVisible();
    
    // Step 9: Mock deposit confirmation
    await page.goto('https://staging.dedan.ai/wallet');
    await expect(page.locator('[data-testid=bitcoin-balance]')).toContainText('0.1');
    
    // Step 10: Navigate to marketplace
    await page.goto('https://staging.dedan.ai/marketplace');
    await expect(page.locator('[data-testid=mineral-marketplace]')).toBeVisible();
    
    // Step 11: Search for gold
    await page.fill('[data-testid=search]', 'gold');
    await page.click('[data-testid=search-button]');
    
    // Step 12: Select first gold listing
    await page.click('[data-testid=mineral-card]:first-child');
    await expect(page.locator('[data-testid=mineral-details]')).toBeVisible();
    
    // Step 13: Place buy order
    await page.fill('[data-testid=quantity]', '1');
    await page.fill('[data-testid=price]', '65000');
    await page.click('[data-testid=place-order]');
    
    // Step 14: Confirm order
    await page.click('[data-testid=confirm-order]');
    await expect(page.locator('[data-testid=order-success]')).toBeVisible();
    
    // Step 15: Check order history
    await page.goto('https://staging.dedan.ai/orders');
    await expect(page.locator('[data-testid=order-history]')).toBeVisible();
    await expect(page.locator('[data-testid=order-row]:first-child')).toContainText('Gold');
  });
});
