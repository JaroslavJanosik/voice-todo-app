import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			'/tasks': 'http://127.0.0.1:5000',
			'/upload': 'http://127.0.0.1:5000',
			'/health': 'http://127.0.0.1:5000',
			'/ready': 'http://127.0.0.1:5000',
			'/meta': 'http://127.0.0.1:5000'
		}
	}
});
