import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { defineConfig, devices } from '@playwright/test';

const currentDirectory = path.dirname(fileURLToPath(import.meta.url));
const frontendPort = Number(process.env.PLAYWRIGHT_FRONTEND_PORT || '4174');
const backendPort = Number(process.env.PLAYWRIGHT_BACKEND_PORT || '5051');
const defaultFrontendBaseUrl = `http://127.0.0.1:${frontendPort}`;
const defaultBackendBaseUrl = `http://127.0.0.1:${backendPort}`;
const frontendBaseUrl = process.env.PLAYWRIGHT_FRONTEND_BASE_URL || defaultFrontendBaseUrl;
const backendBaseUrl = process.env.PLAYWRIGHT_API_BASE_URL || defaultBackendBaseUrl;
const useExternalServer = process.env.PLAYWRIGHT_USE_EXTERNAL_SERVER === '1';
const backendDir = path.resolve(currentDirectory, '../../backend');
const frontendDir = currentDirectory;
const backendPython = process.env.PLAYWRIGHT_BACKEND_PYTHON || 'venv/bin/python';
const sqliteDatabaseUrl = `sqlite:///${path.join(os.tmpdir(), 'voice-todo-playwright.db')}`;

process.env.PLAYWRIGHT_API_BASE_URL = backendBaseUrl;

export default defineConfig({
  testDir: './tests',
  workers: 1,
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: frontendBaseUrl,
    testIdAttribute: 'data-cy',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
      },
    },
  ],
  webServer: useExternalServer
    ? undefined
    : [
        {
          command: `${backendPython} -m flask --app app.py run --host 127.0.0.1 --port ${backendPort}`,
          cwd: backendDir,
          url: `${backendBaseUrl}/health`,
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
          env: {
            DATABASE_URL: sqliteDatabaseUrl,
            CORS_ORIGINS: `${frontendBaseUrl},http://localhost:${frontendPort}`,
            WHISPER_MODEL: 'base',
            APP_NAME: 'voice-todo-app-backend-playwright',
            APP_VERSION: 'playwright',
          },
        },
        {
          command: `npm run dev -- --host 127.0.0.1 --port ${frontendPort}`,
          cwd: frontendDir,
          url: frontendBaseUrl,
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
          env: {
            PUBLIC_API_BASE_URL: backendBaseUrl,
          },
        },
      ],
});
