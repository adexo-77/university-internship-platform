import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './',
  timeout: 30000,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 2,
  reporter: 'list',
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://127.0.0.1:8080',
    browserName: 'chromium',
  },
  projects: [
    {
      name: 'mobile-360',
      use: {
        viewport: { width: 360, height: 640 },
        isMobile: true,
        hasTouch: true,
      },
    },
    {
      name: 'mobile-390',
      use: {
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
      },
    },
    {
      name: 'tablet-768',
      use: {
        viewport: { width: 768, height: 1024 },
      },
    },
    {
      name: 'desktop-1440',
      use: {
        viewport: { width: 1440, height: 900 },
      },
    },
    {
      name: 'desktop-1920',
      use: {
        viewport: { width: 1920, height: 1080 },
      },
    },
  ],
});
