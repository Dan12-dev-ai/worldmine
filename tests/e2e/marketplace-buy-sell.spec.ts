import { test, expect } from '@playwright/test';

test.describe('Marketplace Buy/Sell Physical Mineral', () => {
  test('complete physical mineral purchase workflow', async ({ page }) => {
    // Step 1: Login and navigate to marketplace
    await page.goto('https://staging.dedan.ai/login');
    await page.fill('[data-testid=email]', 'buyer@dedan.ai');
    await page.fill('[data-testid=password]', 'SecurePassword123!@#');
    await page.click('[data-testid=login-button]');
    
    await page.goto('https://staging.dedan.ai/marketplace');
    
    // Step 2: Search for gold
    await page.fill('[data-testid=search]', 'gold');
    await page.selectOption('[data-testid=category]', 'precious_metals');
    await page.click('[data-testid=search-button]');
    
    // Step 3: View 10 oz Gold listing
    await page.click('[data-testid=mineral-card]:has-text("10 oz")');
    await expect(page.locator('[data-testid=mineral-details]')).toBeVisible();
    await expect(page.locator('[data-testid=mineral-name]')).toContainText('Gold');
    await expect(page.locator('[data-testid=purity]')).toContainText('99.99%');
    
    // Step 4: View seller profile
    await page.click('[data-testid=seller-profile]');
    await expect(page.locator('[data-testid=seller-name]')).toContainText('Swiss Gold Refinery');
    await expect(page.locator('[data-testid=seller-rating]')).toContainText('4.9');
    await expect(page.locator('[data-testid=transaction-count]')).toContainText('892');
    
    // Step 5: Open chat with seller
    await page.click('[data-testid=chat-seller]');
    await expect(page.locator('[data-testid=chat-window]')).toBeVisible();
    await page.fill('[data-testid=chat-message]', 'Is this gold available for immediate shipping?');
    await page.click('[data-testid=send-message]');
    await expect(page.locator('[data-testid=message-sent]')).toBeVisible();
    
    // Step 6: Make offer
    await page.goBack();
    await page.click('[data-testid=make-offer]');
    await page.fill('[data-testid=offer-price]', '23200');
    await page.fill('[data-testid=offer-message]', 'I can offer $23,200 for immediate purchase');
    await page.click('[data-testid=submit-offer]');
    
    // Step 7: Wait for seller acceptance (mock)
    await page.goto('https://staging.dedan.ai/offers');
    await expect(page.locator('[data-testid=offer-status]')).toContainText('Accepted');
    
    // Step 8: Pay via escrow
    await page.click('[data-testid=pay-escrow]');
    await expect(page.locator('[data-testid=escrow-contract]')).toBeVisible();
    await page.click('[data-testid=confirm-payment]');
    await expect(page.locator('[data-testid=payment-success]')).toBeVisible();
    
    // Step 9: Track shipping
    await page.goto('https://staging.dedan.ai/orders');
    await expect(page.locator('[data-testid=tracking-number]')).toBeVisible();
    await expect(page.locator('[data-testid=shipping-status]')).toContainText('Shipped');
    
    // Step 10: Confirm delivery
    await page.click('[data-testid=confirm-delivery]');
    await page.setInputFiles('[data-testid=delivery-photo]', 'test-delivery.jpg');
    await page.click('[data-testid=submit-confirmation]');
    await expect(page.locator('[data-testid=delivery-confirmed]')).toBeVisible();
    
    // Step 11: Escrow release
    await page.goto('https://staging.dedan.ai/escrow');
    await expect(page.locator('[data-testid=escrow-status]']).toContainText('Released');
    
    // Step 12: Leave review
    await page.click('[data-testid=leave-review]');
    await page.click('[data-testid=rating-5]');
    await page.fill('[data-testid=review-text]', 'Excellent quality gold, fast shipping!');
    await page.click('[data-testid=submit-review]');
    await expect(page.locator('[data-testid=review-submitted]')).toBeVisible();
  });
});
