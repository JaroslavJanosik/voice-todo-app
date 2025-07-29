import adapter from '@sveltejs/adapter-auto';
import preprocess from 'svelte-preprocess';

export default {
  kit: {
    adapter: adapter(),
    alias: {
      $components: 'src/components',
      $routes: 'src/routes',
      $types: 'src/types'
    }
  },
  preprocess: preprocess()
};