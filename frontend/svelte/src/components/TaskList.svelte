<script lang="ts">
  import Icon from '$components/Icon.svelte';

  interface Task {
    id: number;
    description: string;
    completed: boolean;
  }

  export let tasks: Task[] = [];
  export let isLoading = false;
  export let busyTaskIds: Set<number> = new Set();
  export let onToggleTask: (taskId: number) => Promise<boolean> = async () => false;
  export let onUpdateTask: (taskId: number, newDescription: string) => Promise<boolean> = async () => false;
  export let onDeleteTask: (taskId: number) => Promise<boolean> = async () => false;

  let editingTaskId: number | null = null;
  let editedDescription = '';

  function startEditTask(taskId: number, currentDescription: string) {
    if (isTaskBusy(taskId)) {
      return;
    }

    editingTaskId = taskId;
    editedDescription = currentDescription;
  }

  function cancelEditTask() {
    editingTaskId = null;
    editedDescription = '';
  }

  async function saveTask(taskId: number) {
    const normalizedDescription = editedDescription.trim();
    if (!normalizedDescription) {
      return;
    }

    const didSave = await onUpdateTask(taskId, normalizedDescription);
    if (didSave) {
      cancelEditTask();
    }
  }

  async function handleToggle(taskId: number) {
    if (isTaskBusy(taskId)) {
      return;
    }

    await onToggleTask(taskId);
  }

  async function handleDelete(taskId: number) {
    if (isTaskBusy(taskId)) {
      return;
    }

    const didDelete = await onDeleteTask(taskId);
    if (didDelete && editingTaskId === taskId) {
      cancelEditTask();
    }
  }

  async function handleEditKeydown(event: KeyboardEvent, taskId: number) {
    if (event.key === 'Escape') {
      event.preventDefault();
      cancelEditTask();
      return;
    }

    if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
      event.preventDefault();
      await saveTask(taskId);
    }
  }

  function isTaskBusy(taskId: number) {
    return busyTaskIds.has(taskId);
  }
</script>

{#if isLoading}
  <p class="state-message" aria-live="polite">Loading tasks...</p>
{:else if tasks.length === 0}
  <p class="state-message empty" aria-live="polite" data-cy="empty-state">No tasks yet. Record your first note to get started.</p>
{:else}
  <ul>
    {#each tasks as task (task.id)}
      <li
        class:editing={editingTaskId === task.id}
        class:is-busy={isTaskBusy(task.id)}
        data-cy={`task-card-${task.id}`}
      >
        {#if editingTaskId === task.id}
          <div class="task-content">
            <div class="task-check">
              <input
                type="checkbox"
                class="task-checkbox"
                checked={task.completed}
                disabled={isTaskBusy(task.id)}
                on:change|stopPropagation={() => handleToggle(task.id)}
                data-cy={`toggle-task-${task.id}`}
              />
              <textarea
                class="edit-input"
                bind:value={editedDescription}
                rows="2"
                disabled={isTaskBusy(task.id)}
                on:keydown={(event) => handleEditKeydown(event, task.id)}
                data-cy={`edit-input-${task.id}`}
              ></textarea>
            </div>
            <div class="actions" data-cy={`edit-form-${task.id}`}>
              <button
                type="button"
                class="icon-button"
                aria-label="Save changes"
                disabled={isTaskBusy(task.id) || !editedDescription.trim()}
                on:click|stopPropagation={() => saveTask(task.id)}
                data-cy={`save-edit-${task.id}`}
              >
                <Icon name="save" />
              </button>

              <button
                type="button"
                class="icon-button"
                aria-label="Cancel editing"
                disabled={isTaskBusy(task.id)}
                on:click|stopPropagation={cancelEditTask}
                data-cy={`cancel-edit-${task.id}`}
              >
                <Icon name="close" />
              </button>
            </div>
          </div>
        {:else}
          <div class="task-content">
            <div class="task-check">
              <input
                type="checkbox"
                class="task-checkbox"
                checked={task.completed}
                disabled={isTaskBusy(task.id)}
                on:change|stopPropagation={() => handleToggle(task.id)}
                data-cy={`toggle-task-${task.id}`}
              />
              <span
                class="task-text"
                style:text-decoration={task.completed ? 'line-through' : 'none'}
                style:color={task.completed ? 'rgba(255, 255, 255, 0.6)' : 'white'}
                data-cy={`todo-status-${task.id}`}
              >
                {task.description}
              </span>
            </div>
            <div class="actions">
              <button
                type="button"
                class="icon-button"
                aria-label="Edit task"
                disabled={isTaskBusy(task.id)}
                on:click|stopPropagation={() => startEditTask(task.id, task.description)}
                data-cy={`edit-task-${task.id}`}
              >
                <Icon name="edit" />
              </button>

              <button
                type="button"
                class="icon-button"
                aria-label="Delete task"
                disabled={isTaskBusy(task.id)}
                on:click|stopPropagation={() => handleDelete(task.id)}
                data-cy={`delete-task-${task.id}`}
              >
                <Icon name="trash" />
              </button>
            </div>
          </div>
        {/if}
      </li>
    {/each}
  </ul>
{/if}

<style>
  .state-message {
    margin: 20px 0 0;
    padding: 18px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.12);
    color: rgba(255, 255, 255, 0.92);
    text-align: center;
  }

  .state-message.empty {
    background: rgba(255, 255, 255, 0.1);
  }

  ul {
    list-style: none;
    padding: 0;
    margin-top: 20px;
  }

  li {
    background: rgba(255, 255, 255, 0.15);
    margin: 12px 0;
    padding: 16px 20px;
    border-radius: 15px;
    display: flex;
    align-items: center;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    animation: fadeIn 0.3s ease-in-out;
    transition: background 0.3s ease, transform 0.2s;
  }

  li.is-busy {
    opacity: 0.72;
  }

  li:hover {
    background: rgba(255, 255, 255, 0.25);
    transform: scale(1.02);
  }

  .task-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  .task-check {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
  }

  .task-text {
    font-size: 16px;
    text-align: left;
    flex: 1;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .icon-button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    color: inherit;
    font-size: 18px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
  }

  .icon-button:hover {
    transform: scale(1.1);
  }

  .icon-button:disabled {
    opacity: 0.45;
    cursor: not-allowed;
    transform: none;
  }

  .edit-input {
    flex: 1;
    text-align: left;
    padding: 8px 12px;
    font-size: 16px;
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.2);
    color: white;
    outline: none;
    margin-right: 10px;
    resize: vertical;
    min-height: 44px;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }

    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .task-checkbox {
    appearance: none;
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.6);
    border-radius: 5px;
    background: transparent;
    cursor: pointer;
    transition: all 0.3s ease-in-out;
    position: relative;
    flex-shrink: 0;
  }

  .task-checkbox:hover {
    border-color: rgba(255, 255, 255, 1);
  }

  .task-checkbox:disabled {
    cursor: not-allowed;
  }

  .task-checkbox:checked {
    background: rgba(255, 255, 255, 0.8);
    border-color: rgba(255, 255, 255, 0.9);
  }

  .task-checkbox:checked::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 5px;
    height: 10px;
    border: solid #764ba2;
    border-width: 0 2px 2px 0;
    transform: translate(-50%, -58%) rotate(45deg);
  }

  @media (max-width: 640px) {
    li {
      padding: 14px 16px;
    }

    .task-content {
      align-items: flex-start;
      gap: 12px;
    }

    .task-check {
      align-items: flex-start;
    }

    .actions {
      padding-top: 2px;
    }
  }
</style>
