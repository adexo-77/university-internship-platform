import { test as setup } from '@playwright/test';
import * as fs from 'fs';
import {
  AUTH_DIR,
  AUTH_FILES,
  DEMO_PASSWORD,
  DEMO_USERS,
  DemoRole,
  loginAs,
  resetDemoDatabase,
} from './helpers';

setup('authenticate all roles and generate storage states', async ({ browser }) => {
  resetDemoDatabase();

  if (!fs.existsSync(AUTH_DIR)) {
    fs.mkdirSync(AUTH_DIR, { recursive: true });
  }

  const roles = Object.keys(DEMO_USERS) as DemoRole[];
  for (const role of roles) {
    const context = await browser.newContext();
    const page = await context.newPage();
    await loginAs(page, DEMO_USERS[role], DEMO_PASSWORD);
    await context.storageState({ path: AUTH_FILES[role] });
    await context.close();
  }
});
