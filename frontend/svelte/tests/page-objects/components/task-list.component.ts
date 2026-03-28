import { expect, type Locator, type Page } from '@playwright/test';

export class TaskListComponent {
  constructor(private readonly page: Page) {}

  emptyState() {
    return this.page.getByTestId('empty-state');
  }

  taskCard(taskId: number) {
    return this.page.getByTestId(`task-card-${taskId}`);
  }

  taskCardByText(description: string) {
    return this.page.locator('[data-cy^="task-card-"]').filter({
      has: this.page.getByText(description, { exact: true }),
    });
  }

  async expectEmpty() {
    await expect(this.emptyState()).toBeVisible();
  }

  async expectTaskVisible(description: string) {
    await expect(this.taskCardByText(description)).toBeVisible();
  }

  async expectTaskHidden(description: string) {
    await expect(this.taskCardByText(description)).toHaveCount(0);
  }

  async toggleTask(taskId: number) {
    await this.taskCard(taskId).getByRole('checkbox').click();
  }

  async startEditing(taskId: number) {
    await this.taskCard(taskId).getByRole('button', { name: 'Edit task' }).click();
  }

  editInput(taskId: number): Locator {
    return this.page.getByTestId(`edit-input-${taskId}`);
  }

  async saveEdit(taskId: number) {
    await this.page.getByTestId(`save-edit-${taskId}`).click();
  }

  async editTask(taskId: number, nextDescription: string) {
    await this.startEditing(taskId);
    await this.editInput(taskId).fill(nextDescription);
    await this.saveEdit(taskId);
  }

  async deleteTask(taskId: number) {
    await this.taskCard(taskId).getByRole('button', { name: 'Delete task' }).click();
  }
}
