import { expect } from '@playwright/test';

import { test } from '../fixtures/test-fixtures';

test.describe('tasks api', () => {
  test('exposes healthy service metadata and task CRUD through the public contract', async ({ tasksApi }) => {
    const health = await tasksApi.getHealth();
    expect(health.service).toContain('voice-todo-app-backend');
    expect(health.checks.database).toBe('ok');

    const createdTask = await tasksApi.createTask('Draft quarterly roadmap');
    expect(createdTask.description).toBe('Draft quarterly roadmap');
    expect(createdTask.completed).toBe(false);

    const updatedTask = await tasksApi.updateTask(createdTask.id, { completed: true });
    expect(updatedTask.completed).toBe(true);

    const stats = await tasksApi.getTaskStats();
    expect(stats.total).toBe(1);
    expect(stats.completed).toBe(1);
    expect(stats.active).toBe(0);
    expect(stats.completionRate).toBe(100);
  });

  test('returns a conflict envelope for duplicate task descriptions', async ({ tasksApi }) => {
    await tasksApi.createTask('Send contract draft');

    const conflict = await tasksApi.expectConflict('Send contract draft');

    expect(conflict.statusCode).toBe(409);
    expect(conflict.isSuccess).toBe(false);
    expect(conflict.errorMessages).toEqual(['Task already exists.']);
  });
});
