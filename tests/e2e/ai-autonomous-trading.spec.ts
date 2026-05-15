import { test, expect } from '@playwright/test';

test.describe('AI Autonomous Trading', () => {
  test('complete AI trading agent workflow', async ({ page }) => {
    // Step 1: Login and navigate to AI trading
    await page.goto('https://staging.dedan.ai/login');
    await page.fill('[data-testid=email]', 'trader@dedan.ai');
    await page.fill('[data-testid=password]', 'SecurePassword123!@#');
    await page.click('[data-testid=login-button]');
    
    await page.click('[data-testid=ai-trading-tab]');
    await expect(page.locator('[data-testid=ai-trading-dashboard]')).toBeVisible();
    
    // Step 2: Enable AI Trading Agent
    await page.click('[data-testid=enable-ai-trading]');
    await expect(page.locator('[data-testid=ai-setup]')).toBeVisible();
    
    // Step 3: Configure autonomy level
    await page.selectOption('[data-testid=autonomy-level]', 'level-4');
    await expect(page.locator('[data-testid=autonomy-description]')).toContainText('$10K auto, >$10K approve');
    
    // Step 4: Set daily loss limit
    await page.fill('[data-testid=daily-loss-limit]', '5000');
    await page.click('[data-testid=save-settings]');
    await expect(page.locator('[data-testid=settings-saved]')).toBeVisible();
    
    // Step 5: Activate AI agent
    await page.click('[data-testid=activate-ai-agent]');
    await expect(page.locator('[data-testid=ai-agent-active]')).toBeVisible();
    
    // Step 6: Monitor AI analysis
    await page.goto('https://staging.dedan.ai/ai-analysis');
    await expect(page.locator('[data-testid=market-analysis]')).toBeVisible();
    await expect(page.locator('[data-testid=ai-recommendations]')).toBeVisible();
    
    // Step 7: Wait for AI to place trade (mock)
    await page.waitForTimeout(5000);
    await page.goto('https://staging.dedan.ai/trading-history');
    await expect(page.locator('[data-testid=ai-trade]')).toBeVisible();
    await expect(page.locator('[data-testid=trade-pair]')).toContainText('GOLD/USD');
    await expect(page.locator('[data-testid=trade-type]')).toContainText('BUY');
    await expect(page.locator('[data-testid=trade-amount]')).toContainText('$8,000');
    
    // Step 8: Monitor trade execution
    await expect(page.locator('[data-testid=trade-status]')).toContainText('Filled');
    await expect(page.locator('[data-testid=execution-time]')).toContainText('0.8ms');
    await expect(page.locator('[data-testid=quantum-verified]')).toBeVisible();
    
    // Step 9: Monitor profit update
    await page.waitForTimeout(3000);
    await expect(page.locator('[data-testid=current-pnl]')).toBeVisible();
    const pnl = await page.locator('[data-testid=current-pnl]').textContent();
    expect(pnl).toContain('+');
    
    // Step 10: AI sells at profit
    await page.waitForTimeout(5000);
    await expect(page.locator('[data-testid=sell-trade]')).toBeVisible();
    await expect(page.locator('[data-testid=profit-amount]')).toContainText('$184');
    
    // Step 11: Check daily summary
    await page.goto('https://staging.dedan.ai/ai-summary');
    await expect(page.locator('[data-testid=daily-summary]')).toBeVisible();
    await expect(page.locator('[data-testid=total-trades]')).toContainText('12');
    await expect(page.locator('[data-testid=win-rate]')).toContainText('80%');
    await expect(page.locator('[data-testid=total-profit]')).toContainText('$2,340');
  });
});
