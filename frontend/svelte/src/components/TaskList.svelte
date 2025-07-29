<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

 interface Task {
    id: number;
    description: string;
    completed: boolean;
  }

  export let tasks: Task[] = [];

  let editingTaskId: number | null = null;
  let editedDescription = '';

  function startEditTask(taskId: number, currentDescription: string) {
    editingTaskId = taskId;
    editedDescription = currentDescription;
  }

  function cancelEditTask() {
    editingTaskId = null;
    editedDescription = '';
  }

  function saveTask(taskId: number) {
    dispatch('updateTask', { taskId, newDescription: editedDescription });
    cancelEditTask();
  }

  function handleToggle(taskId: number) {
    dispatch('toggleTask', { taskId });
  }

  function handleDelete(taskId: number) {
    dispatch('deleteTask', { taskId });
  }
</script>

<ul>
  {#each tasks as task (task.id)}
    <li class:editing={editingTaskId === task.id}>
      {#if editingTaskId === task.id}
        <!-- Editing Mode -->
        <div class="task-content">
          <div class="task-check">
            <input
              type="checkbox"
              class="task-checkbox"
              checked={task.completed}
              on:change|stopPropagation={() => handleToggle(task.id)}
            />
            <textarea
              class="edit-input"
              bind:value={editedDescription}
              style="white-space: pre-wrap;"></textarea>
          </div>
          <div class="actions">
            <button
              type="button"
              class="icon-button"
              aria-label="Save changes"
              on:click|stopPropagation={() => saveTask(task.id)}
            >
              <i class="fas fa-save" aria-hidden="true"></i>
            </button>

            <button
              type="button"
              class="icon-button"
              aria-label="Cancel editing"
              on:click|stopPropagation={cancelEditTask}
            >
              <i class="fas fa-times" aria-hidden="true"></i>
            </button>
          </div>
        </div>
      {:else}
        <!-- View Mode -->
        <div class="task-content">
          <!-- Checkbox -->
          <div class="task-check">
            <input
              type="checkbox"
              class="task-checkbox"
              checked={task.completed}
              on:change|stopPropagation={() => handleToggle(task.id)}
            />
            <span
              class="task-text"
              style:text-decoration={task.completed ? 'line-through' : 'none'}
              style:color={task.completed ? 'rgba(255, 255, 255, 0.6)' : 'white'}
            >
              {task.description}
            </span>
          </div>
          <div class="actions">
            <!-- Edit button with icon -->
            <button
              type="button"
              class="icon-button"
              aria-label="Edit task"
              on:click|stopPropagation={() => startEditTask(task.id, task.description)}
            >
              <i class="fas fa-edit" aria-hidden="true"></i>
            </button>

            <!-- Delete button with icon -->
            <button
              type="button"
              class="icon-button"
              aria-label="Delete task"
              on:click|stopPropagation={() => handleDelete(task.id)}
            >
              <i class="fas fa-trash" aria-hidden="true"></i>
            </button>
          </div>
        </div>
      {/if}
    </li>
  {/each}
</ul>

<style scoped>
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
    font-size: 1em;
    display: inline-flex;
    align-items: center;
  }

  .icon-button:hover {
    transform: scale(1.1);
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
    resize: none;
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
  }

  .task-checkbox:hover {
    border-color: rgba(255, 255, 255, 1);
  }

  .task-checkbox:checked {
    background: rgba(255, 255, 255, 0.8);
    border-color: rgba(255, 255, 255, 0.9);
  }

  .task-checkbox:checked::after {
    content: '\f00c';
    font-family: "Font Awesome 5 Free";
    font-weight: 900;
    color: #764ba2;
    position: absolute;
    top: 50%;
    left: 50%;
    font-size: 14px;
    transform: translate(-50%, -50%);
  }
</style>