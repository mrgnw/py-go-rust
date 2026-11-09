import tailwindcss from '@tailwindcss/vite';
import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { isMainThread } from 'node:worker_threads';
import { defineConfig } from 'vite';
import checker from 'vite-plugin-checker';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit({
			compilerOptions: {
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: adapter()
		}),
		isMainThread && checker({ svelteCheck: true, enableBuild: false })
	],
	server: {
		port: 5237,
		strictPort: true,
		host: true,
		allowedHosts: ['.example.ts.net']
	}
});
