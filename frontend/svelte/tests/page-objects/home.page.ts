import { expect, type Page } from '@playwright/test';

import { RecorderComponent } from './components/recorder.component';
import { TaskListComponent } from './components/task-list.component';

export class HomePage {
  readonly recorder: RecorderComponent;
  readonly taskList: TaskListComponent;

  constructor(private readonly page: Page) {
    this.recorder = new RecorderComponent(page);
    this.taskList = new TaskListComponent(page);
  }

  async goto() {
    await this.page.goto('/');
  }

  async expectLoaded() {
    await expect(this.page.getByRole('heading', { name: 'Voice ToDo List' })).toBeVisible();
    await expect(this.page.getByTestId('task-summary')).toBeVisible();
  }

  summaryValue(key: 'total' | 'active' | 'completed' | 'completionRate') {
    return this.page.getByTestId(`summary-${key}`).locator('.summary-value');
  }

  async expectSummary(values: {
    total: string;
    active: string;
    completed: string;
    completionRate: string;
  }) {
    await expect(this.summaryValue('total')).toHaveText(values.total);
    await expect(this.summaryValue('active')).toHaveText(values.active);
    await expect(this.summaryValue('completed')).toHaveText(values.completed);
    await expect(this.summaryValue('completionRate')).toHaveText(values.completionRate);
  }

  errorBanner() {
    return this.page.getByTestId('error-banner');
  }

  successBanner() {
    return this.page.getByTestId('success-banner');
  }

  async expectError(message: string) {
    await expect(this.errorBanner()).toContainText(message);
  }

  async expectSuccess(message: string) {
    await expect(this.successBanner()).toContainText(message);
  }
}
