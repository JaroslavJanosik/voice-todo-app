<script>

    import RecordButton from "$components/RecordButton.svelte";
    import TaskList from "$components/TaskList.svelte";

</script>
<main>
  <h1>🎙 Voice To-Do List</h1>
  <RecordButton/>
  <TaskList />
</main>

<style>
  main {
    text-align: center;
    padding: 20px;
    max-width: 500px;
    margin: auto;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
  }
</style>