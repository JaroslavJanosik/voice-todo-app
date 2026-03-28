<script lang="ts">
  export let stats: {
    total: number;
    active: number;
    completed: number;
    completionRate: number;
  };

  const items = [
    { label: 'Total', key: 'total' },
    { label: 'Active', key: 'active' },
    { label: 'Done', key: 'completed' },
    { label: 'Progress', key: 'completionRate' }
  ] as const;
</script>

<div class="summary" data-cy="task-summary">
  {#each items as item}
    <div class="summary-card" data-cy={`summary-${item.key}`}>
      <span class="summary-label">{item.label}</span>
      <strong class="summary-value">
        {#if item.key === 'completionRate'}
          {stats[item.key]}%
        {:else}
          {stats[item.key]}
        {/if}
      </strong>
    </div>
  {/each}
</div>

<style>
  .summary {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
  }

  .summary-card {
    padding: 12px 10px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.12);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
  }

  .summary-label {
    display: block;
    font-size: 11px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    opacity: 0.74;
    margin-bottom: 6px;
  }

  .summary-value {
    display: block;
    font-size: 17px;
    font-weight: 600;
  }

  @media (max-width: 640px) {
    .summary {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }
</style>
