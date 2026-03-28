import { test, expect } from '../fixtures/test-fixtures';

test.describe('task dashboard', () => {
  test('shows the empty state and zeroed summary for a clean workspace', async ({ homePage }) => {
    await homePage.goto();
    await homePage.expectLoaded();

    await homePage.expectSummary({
      total: '0',
      active: '0',
      completed: '0',
      completionRate: '0%',
    });
    await homePage.taskList.expectEmpty();
  });

  test('supports toggle, edit and delete flows while keeping summary cards in sync', async ({ homePage, tasksApi }) => {
    const reviewTask = await tasksApi.createTask('Prepare sprint review');
    const appointmentTask = await tasksApi.createTask('Book dentist appointment');

    await homePage.goto();
    await homePage.expectLoaded();
    await homePage.expectSummary({
      total: '2',
      active: '2',
      completed: '0',
      completionRate: '0%',
    });

    await homePage.taskList.toggleTask(reviewTask.id);
    await homePage.expectSummary({
      total: '2',
      active: '1',
      completed: '1',
      completionRate: '50%',
    });

    await homePage.taskList.editTask(appointmentTask.id, 'Book dentist and eye exam');
    await homePage.expectSuccess('Task updated successfully.');
    await homePage.taskList.expectTaskVisible('Book dentist and eye exam');

    await homePage.taskList.deleteTask(reviewTask.id);
    await homePage.expectSuccess('Task deleted successfully.');
    await homePage.taskList.expectTaskHidden('Prepare sprint review');
    await homePage.expectSummary({
      total: '1',
      active: '1',
      completed: '0',
      completionRate: '0%',
    });
  });

  test('keeps the edit form open when the backend rejects a duplicate task description', async ({ homePage, tasksApi }) => {
    await tasksApi.createTask('Pay electricity bill');
    const coffeeTask = await tasksApi.createTask('Refill coffee beans');

    await homePage.goto();
    await homePage.expectLoaded();

    await homePage.taskList.startEditing(coffeeTask.id);
    const input = homePage.taskList.editInput(coffeeTask.id);
    await input.fill('Pay electricity bill');
    await homePage.taskList.saveEdit(coffeeTask.id);

    await homePage.expectError('Task already exists.');
    await expect(input).toHaveValue('Pay electricity bill');
  });
});
