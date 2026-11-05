import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './',
  timeout: 30000,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://127.0.0.1:8080',
    browserName: 'chromium',
  },
  projects: [
    {
      name: 'setup',
      testMatch: /auth\.setup\.ts/,
    },
    {
      name: 'mobile-360',
      dependencies: ['setup'],
      testIgnore: [/auth\.setup\.ts/, /auth\.spec\.ts/, /flows\/.*/],
      use: {
        viewport: { width: 360, height: 640 },
        isMobile: true,
        hasTouch: true,
      },
    },
    {
      name: 'mobile-390',
      dependencies: ['setup'],
      testIgnore: [/auth\.setup\.ts/, /auth\.spec\.ts/, /flows\/.*/],
      use: {
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
      },
    },
    {
      name: 'tablet-768',
      dependencies: ['setup'],
      testIgnore: [/auth\.setup\.ts/, /auth\.spec\.ts/, /flows\/.*/],
      use: {
        viewport: { width: 768, height: 1024 },
      },
    },
    {
      name: 'desktop-1440',
      dependencies: ['setup'],
      testIgnore: [/auth\.setup\.ts/, /flows\/.*/],
      use: {
        viewport: { width: 1440, height: 900 },
      },
    },
    {
      name: 'desktop-1920',
      dependencies: ['setup'],
      testIgnore: [/auth\.setup\.ts/, /auth\.spec\.ts/, /flows\/.*/],
      use: {
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'flows',
      dependencies: ['setup'],
      testMatch: /flows\/.*\.spec\.ts/,
      use: {
        viewport: { width: 1440, height: 900 },
      },
    },
  ],
});
