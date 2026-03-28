import { test as base } from '@playwright/test';

import { HomePage } from '../page-objects/home.page';
import { TasksApiClient } from '../support/tasks-api-client';

const PLAYWRIGHT_API_BASE_URL = 'http://127.0.0.1:5051';

type TestFixtures = {
  homePage: HomePage;
  tasksApi: TasksApiClient;
};

export const test = base.extend<TestFixtures>({
  homePage: async ({ page }, use) => {
    await use(new HomePage(page));
  },
  tasksApi: async ({ playwright }, use) => {
    const requestContext = await playwright.request.newContext({
      baseURL: PLAYWRIGHT_API_BASE_URL,
    });
    const client = new TasksApiClient(requestContext);

    await client.resetAll();
    await use(client);
    await client.resetAll();
    await requestContext.dispose();
  },
});

export { expect } from '@playwright/test';
