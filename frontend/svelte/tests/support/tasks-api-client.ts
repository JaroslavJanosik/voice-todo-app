import { expect, type APIRequestContext, type APIResponse } from '@playwright/test';

import type { ApiEnvelope } from './api-envelope';

export type TaskDto = {
  id: number;
  description: string;
  completed: boolean;
  created_at?: string;
  updated_at?: string;
};

type MetaDto = {
  name: string;
  version: string;
  taskStats: {
    total: number;
    active: number;
    completed: number;
    completionRate: number;
  };
  limits: {
    maxUploadBytes: number;
    allowedAudioExtensions: string[];
  };
};

type HealthDto = {
  service: string;
  status: string;
  checks: {
    database: string;
    transcriptionRuntime: string;
  };
};

export class TasksApiClient {
  constructor(private readonly request: APIRequestContext) {}

  async listTasks() {
    return this.unwrap<TaskDto[]>(await this.request.get('/tasks'));
  }

  async createTask(description: string) {
    return this.unwrap<TaskDto>(
      await this.request.post('/tasks', {
        data: { task: description },
      }),
      201
    );
  }

  async updateTask(taskId: number, payload: Partial<{ task: string; completed: boolean }>) {
    return this.unwrap<TaskDto>(
      await this.request.patch(`/tasks/${taskId}`, {
        data: payload,
      })
    );
  }

  async deleteTask(taskId: number) {
    return this.unwrap<{ message: string }>(await this.request.delete(`/tasks/${taskId}`));
  }

  async getTaskStats() {
    const meta = await this.unwrap<MetaDto>(await this.request.get('/meta'));
    return meta.taskStats;
  }

  async getHealth() {
    return this.unwrap<HealthDto>(await this.request.get('/health'));
  }

  async expectConflict(description: string) {
    const response = await this.request.post('/tasks', {
      data: { task: description },
    });
    expect(response.status()).toBe(409);

    return this.readEnvelope<null>(response);
  }

  async resetAll() {
    const tasks = await this.listTasks();

    for (const task of tasks) {
      await this.deleteTask(task.id);
    }
  }

  private async unwrap<T>(response: APIResponse, expectedStatus = 200) {
    expect(response.status()).toBe(expectedStatus);
    const payload = await this.readEnvelope<T>(response);
    expect(payload.isSuccess).toBe(true);

    return payload.result;
  }

  private async readEnvelope<T>(response: APIResponse) {
    return (await response.json()) as ApiEnvelope<T>;
  }
}
