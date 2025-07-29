<script lang="ts">
  import { onMount } from 'svelte';
  import RecordButton from '$components/RecordButton.svelte';
  import TaskList from '$components/TaskList.svelte';
  import { API_BASE_URL } from '../config';

  interface Task {
    id: number;
    description: string;
    completed: boolean;
  }

  let tasks: Task[] = [];

  // Fetch tasks on component mount
  onMount(async () => {
    await loadTasks();
  });

  async function loadTasks() {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks`);
      if (!response.ok) throw new Error('Failed to fetch tasks');
      tasks = await response.json();
    } catch (error) {
      console.error('Error loading tasks:', error);
    }
  }

  /**
   * Function to add a new task.
   * Called after transcription from the RecordButton, or you could call it manually.
   */
  async function addTask(description: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: description })
      });

      if (!response.ok) throw new Error('Failed to add task');
      // Reload tasks
      await loadTasks();
    } catch (error) {
      console.error('Error adding task:', error);
    }
  }

  // Handle toggling, editing, saving, deleting tasks
  async function toggleTask(taskId: number) {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/toggle`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' }
      });
      if (!response.ok) throw new Error('Failed to toggle task');
      await loadTasks();
    } catch (error) {
      console.error('Error toggling task:', error);
    }
  }

  async function updateTask(taskId: number, newDescription: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: newDescription })
      });
      if (!response.ok) throw new Error('Failed to update task');
      await loadTasks();
    } catch (error) {
      console.error('Error updating task:', error);
    }
  }

  async function deleteTask(taskId: number) {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Failed to delete task');
      await loadTasks();
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  }
</script>

<!-- Main "Card" container -->
<div class="container">
  <h1>Voice ToDo List</h1>
  
  <!-- RecordButton component triggers a callback when transcription is ready -->
  <RecordButton on:transcribed={(e) => addTask(e.detail.transcription)}/>

  <!-- TaskList component displays tasks and triggers actions -->
  <TaskList
    {tasks}
    on:toggleTask={(e) => toggleTask(e.detail.taskId)}
    on:updateTask={(e) => updateTask(e.detail.taskId, e.detail.newDescription)}
    on:deleteTask={(e) => deleteTask(e.detail.taskId)}
  />
</div>

<!-- Local or scoped styles (or remove this if you're using global.css) -->
<style scoped>
  .container {
    background: rgba(255, 255, 255, 0.1);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.2);
    text-align: center;
    backdrop-filter: blur(12px);
    max-width: 480px;
    width: 90%;
    margin: auto;
  }

  h1 {
    font-size: 28px;
    margin-bottom: 25px;
  }
</style>