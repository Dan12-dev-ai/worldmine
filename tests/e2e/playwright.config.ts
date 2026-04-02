import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'test-results.xml' }]
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    // Global setup for all tests
    globalSetup: async ({}, use) => {
      // Setup test database
      await use.request('/api/test/setup', {
        method: 'POST',
        data: { reset: true }
      });
    },
    
    // Global teardown for all tests
    globalTeardown: async ({}, use) => {
      // Cleanup test database
      await use.request('/api/test/teardown', {
        method: 'POST',
        data: { cleanup: true }
      });
    },
    
    // Test timeout
    actionTimeout: 30000,
    
    // Browser context options
    contextOptions: {
      permissions: ['geolocation', 'notifications'],
      ignoreHTTPSErrors: true,
      bypassCSP: true
    }
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
      testMatch: '**/*.mobile.spec.ts',
    },
    {
      name: 'tablet-chrome',
      use: { ...devices['iPad Pro'] },
      testMatch: '**/*.tablet.spec.ts',
    }
  ],
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
  outputDir: 'test-results/',
  expect: {
    // Screenshot on failure
    toHaveScreenshot: {
      mode: 'only-on-failure',
      animations: 'disabled'
    },
    
    // Timeout for assertions
    timeout: 10000
  }
});
