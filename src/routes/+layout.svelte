<script lang="ts">
	import './layout.css';
	import favicon from '#lib/assets/favicon.svg';
	import { page } from '$app/state';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

	const copyScript = `<script>
	if (navigator.clipboard) document.documentElement.dataset.copy = '';
	document.addEventListener('click', async (event) => {
		const button = event.target.closest('.copy');
		if (!button) return;
		await navigator.clipboard.writeText(button.parentElement.querySelector('pre').textContent);
		button.textContent = 'Copied';
		setTimeout(() => (button.textContent = 'Copy'), 1500);
	});
<\/script>`;
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	{@html copyScript}
</svelte:head>

<nav
	class="sticky top-0 z-10 flex gap-1 overflow-x-auto border-b border-neutral-200 bg-white/90 px-4 py-2 text-sm backdrop-blur dark:border-neutral-800 dark:bg-neutral-950/90"
>
	<a href="/" class="px-2 py-1 font-semibold whitespace-nowrap">py · rs · go</a>
	{#each data.nav as item (item.href)}
		<a
			href={item.href}
			aria-current={page.url.pathname === item.href ? 'page' : undefined}
			class="rounded-md px-3 py-1 whitespace-nowrap text-neutral-500 hover:bg-neutral-100 hover:text-neutral-900 aria-[current=page]:bg-neutral-100 aria-[current=page]:text-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:hover:text-neutral-50 dark:aria-[current=page]:bg-neutral-800 dark:aria-[current=page]:text-neutral-50"
			>{item.title}</a
		>
	{/each}
</nav>

<main class="mx-auto max-w-7xl px-4 py-8">
	{@render children()}
</main>
