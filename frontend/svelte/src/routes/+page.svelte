<script lang="ts">
  import { onMount } from 'svelte';

  import RecordButton from '$components/RecordButton.svelte';
  import TaskSummary from '$components/TaskSummary.svelte';
  import TaskList from '$components/TaskList.svelte';
  import { apiRequest } from '../config';

  interface Task {
    id: number;
    description: string;
    completed: boolean;
  }

  let tasks: Task[] = [];
  let isLoading = true;
  let isAddingTask = false;
  let busyTaskIds = new Set<number>();
  let errorMessage = '';
  let successMessage = '';
  let stats = {
    total: 0,
    active: 0,
    completed: 0,
    completionRate: 0
  };

  onMount(async () => {
    await loadTasks();
  });

  async function loadTasks() {
    clearMessages();
    isLoading = true;

    try {
      tasks = await apiRequest<Task[]>('/tasks');
      refreshStats(tasks);
    } catch (error) {
      refreshStats([]);
      errorMessage = getErrorMessage(error, 'Failed to load tasks.');
    } finally {
      isLoading = false;
    }
  }

  async function addTask(description: string) {
    const normalizedDescription = description.trim();
    if (!normalizedDescription) {
      errorMessage = 'No speech was detected in the recording.';
      successMessage = '';
      return;
    }

    clearMessages();
    isAddingTask = true;

    try {
      const result = await apiRequest<Task>('/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: normalizedDescription })
      });

      tasks = [result, ...tasks.filter((task) => task.id !== result.id)];
      refreshStats(tasks);
      successMessage = 'Task added successfully.';
    } catch (error) {
      errorMessage = getErrorMessage(error, 'Failed to add task.');
    } finally {
      isAddingTask = false;
    }
  }

  async function toggleTask(taskId: number): Promise<boolean> {
    const currentTask = tasks.find((task) => task.id === taskId);
    if (!currentTask) {
      return false;
    }

    return runTaskMutation(taskId, async () => {
      const result = await apiRequest<Task>(`/tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: !currentTask.completed })
      });

      tasks = tasks.map((task) => (task.id === taskId ? result : task));
      refreshStats(tasks);
    }, 'Failed to update task status.');
  }

  async function updateTask(taskId: number, newDescription: string): Promise<boolean> {
    const normalizedDescription = newDescription.trim();
    if (!normalizedDescription) {
      errorMessage = 'Task description is required.';
      successMessage = '';
      return false;
    }

    return runTaskMutation(taskId, async () => {
      const result = await apiRequest<Task>(`/tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: normalizedDescription })
      });

      tasks = tasks.map((task) => (task.id === taskId ? result : task));
      refreshStats(tasks);
      successMessage = 'Task updated successfully.';
    }, 'Failed to update task.');
  }

  async function deleteTask(taskId: number): Promise<boolean> {
    return runTaskMutation(taskId, async () => {
      await apiRequest<{ message: string }>(`/tasks/${taskId}`, { method: 'DELETE' });
      tasks = tasks.filter((task) => task.id !== taskId);
      refreshStats(tasks);
      successMessage = 'Task deleted successfully.';
    }, 'Failed to delete task.');
  }

  function handleRecordingError(event: CustomEvent<{ message: string }>) {
    errorMessage = event.detail.message;
    successMessage = '';
  }

  async function runTaskMutation(taskId: number, action: () => Promise<void>, fallbackMessage: string): Promise<boolean> {
    setTaskBusy(taskId, true);
    clearMessages();

    try {
      await action();
      return true;
    } catch (error) {
      errorMessage = getErrorMessage(error, fallbackMessage);
      return false;
    } finally {
      setTaskBusy(taskId, false);
    }
  }

  function setTaskBusy(taskId: number, isBusy: boolean) {
    const nextBusyTaskIds = new Set(busyTaskIds);

    if (isBusy) {
      nextBusyTaskIds.add(taskId);
    } else {
      nextBusyTaskIds.delete(taskId);
    }

    busyTaskIds = nextBusyTaskIds;
  }

  function clearMessages() {
    errorMessage = '';
    successMessage = '';
  }

  function refreshStats(taskList: Task[]) {
    const total = taskList.length;
    const completed = taskList.filter((task) => task.completed).length;
    const active = total - completed;

    stats = {
      total,
      active,
      completed,
      completionRate: total ? Math.round((completed / total) * 100) : 0
    };
  }

  function getErrorMessage(error: unknown, fallbackMessage: string) {
    return error instanceof Error ? error.message : fallbackMessage;
  }
</script>

<div class="container">
  <h1>Voice ToDo List</h1>

  <TaskSummary {stats} />

  <RecordButton
    disabled={isLoading || isAddingTask}
    on:transcribed={(event) => addTask(event.detail.transcription)}
    on:error={handleRecordingError}
  />

  {#if errorMessage}
    <div class="feedback error" role="alert" data-cy="error-banner">
      <p>{errorMessage}</p>
      {#if tasks.length === 0}
        <button type="button" class="feedback-action" on:click={loadTasks} data-cy="retry-load">
          Retry
        </button>
      {/if}
    </div>
  {:else if successMessage}
    <p class="feedback success" aria-live="polite" data-cy="success-banner">{successMessage}</p>
  {/if}

  <TaskList
    {tasks}
    {isLoading}
    {busyTaskIds}
    onToggleTask={toggleTask}
    onUpdateTask={updateTask}
    onDeleteTask={deleteTask}
  />
</div>

<style>
  .container {
    background: rgba(255, 255, 255, 0.1);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.2);
    text-align: center;
    backdrop-filter: blur(12px);
    max-width: 480px;
    width: min(100%, 480px);
    margin: auto;
    display: flex;
    flex-direction: column;
    gap: 18px;
  }

  h1 {
    font-size: 28px;
    margin: 0;
  }

  .feedback {
    margin: 0;
    padding: 14px 16px;
    border-radius: 14px;
    font-size: 14px;
    line-height: 1.5;
  }

  .feedback p {
    margin: 0;
  }

  .feedback.error {
    background: rgba(255, 119, 119, 0.18);
    border: 1px solid rgba(255, 119, 119, 0.35);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }

  .feedback.success {
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .feedback-action {
    border: 1px solid rgba(255, 255, 255, 0.28);
    background: rgba(255, 255, 255, 0.12);
    color: inherit;
    border-radius: 999px;
    padding: 8px 14px;
    cursor: pointer;
    flex-shrink: 0;
  }

  .feedback-action:hover {
    background: rgba(255, 255, 255, 0.18);
  }

  @media (max-width: 640px) {
    .feedback.error {
      flex-direction: column;
      align-items: stretch;
      text-align: left;
    }
  }
</style>
