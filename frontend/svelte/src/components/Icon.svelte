<script lang="ts">
  export let name:
    | 'microphone'
    | 'stop'
    | 'spinner'
    | 'edit'
    | 'trash'
    | 'save'
    | 'close' = 'microphone';
  export let className = '';
</script>

<svg
  class={`icon ${className}`.trim()}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="1.8"
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"
>
  {#if name === 'microphone'}
    <path d="M12 18.75v2.5" />
    <path d="M8.5 21.25h7" />
    <path d="M5.25 10.5v1.5a6.75 6.75 0 0 0 13.5 0v-1.5" />
    <rect x="9.25" y="3.75" width="5.5" height="10.5" rx="2.75" />
  {:else if name === 'stop'}
    <rect x="7.25" y="7.25" width="9.5" height="9.5" rx="1.5" />
    <rect x="3.75" y="3.75" width="16.5" height="16.5" rx="4" />
  {:else if name === 'spinner'}
    <circle cx="12" cy="12" r="7.25" stroke-opacity="0.25" />
    <path d="M19.25 12a7.25 7.25 0 0 0-7.25-7.25" />
  {:else if name === 'edit'}
    <path d="m15.25 5.25 3.5 3.5" />
    <path d="M4.75 19.25 6 15l9.6-9.6a2.47 2.47 0 1 1 3.5 3.5L9.5 18.5l-4.75.75Z" />
  {:else if name === 'trash'}
    <path d="M5.75 7.25h12.5" />
    <path d="M9.25 7.25V5.5a1.75 1.75 0 0 1 1.75-1.75h2a1.75 1.75 0 0 1 1.75 1.75v1.75" />
    <path d="m7.25 7.25.9 11.1a2 2 0 0 0 2 1.84h3.7a2 2 0 0 0 2-1.84l.9-11.1" />
    <path d="M10.25 10.5v5.5" />
    <path d="M13.75 10.5v5.5" />
  {:else if name === 'save'}
    <path d="M5.25 20.25h13.5a1.5 1.5 0 0 0 1.5-1.5V8.7a2 2 0 0 0-.59-1.41L16.96 4.6a2 2 0 0 0-1.41-.6H5.25a1.5 1.5 0 0 0-1.5 1.5v13.25a1.5 1.5 0 0 0 1.5 1.5Z" />
    <path d="M8.5 4.25v5h6.75v-5" />
    <path d="M8.5 20.25v-5.5h7v5.5" />
  {:else if name === 'close'}
    <path d="m7 7 10 10" />
    <path d="M17 7 7 17" />
  {/if}
</svg>

<style>
  .icon {
    width: 1em;
    height: 1em;
    display: block;
    flex-shrink: 0;
  }

  .icon.spinner {
    animation: spin 0.85s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
