<script lang="ts">
	import './layout.css';
	import favicon from '#lib/assets/favicon.svg';
	import { page } from '$app/state';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

	const PICK = [
		['python', 'py'],
		['rust', 'rs'],
		['go', 'go']
	];

	const inlineScript = `<script>
	if (navigator.clipboard) document.documentElement.dataset.copy = '';
	const html = document.documentElement;
	html.dataset.hide = localStorage.getItem('hide') ?? '';
	const syncPicker = () => {
		const hidden = html.dataset.hide.split(' ');
		for (const b of document.querySelectorAll('[data-pick]'))
			b.setAttribute('aria-pressed', String(!hidden.includes(b.dataset.pick)));
	};
	const trackSections = () => {
		const toc = document.querySelector('nav[aria-label="Sections"]');
		if (!toc) return;
		const links = [...toc.querySelectorAll('li a[href^="#"]')];
		const heads = links.map((a) => document.getElementById(decodeURIComponent(a.hash.slice(1))));
		let queued = false;
		const update = () => {
			queued = false;
			const i = Math.max(0, heads.findLastIndex((h) => h && h.getBoundingClientRect().top <= 96));
			links.forEach((a, k) => a.toggleAttribute('aria-current', k === i));
			if (toc.scrollHeight > toc.clientHeight) links[i].scrollIntoView({ block: 'nearest' });
		};
		addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(update); } }, { passive: true });
		update();
	};
	document.addEventListener('DOMContentLoaded', () => { syncPicker(); trackSections(); });
	document.addEventListener('click', (event) => {
		const button = event.target.closest('[data-pick]');
		if (!button) return;
		const hidden = new Set(html.dataset.hide.split(' ').filter(Boolean));
		hidden.has(button.dataset.pick) ? hidden.delete(button.dataset.pick) : hidden.add(button.dataset.pick);
		html.dataset.hide = [...hidden].join(' ');
		localStorage.setItem('hide', html.dataset.hide);
		syncPicker();
	});
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
	{@html inlineScript}
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
	<div class="picker ml-auto flex gap-1 font-mono text-xs" role="group" aria-label="Show languages">
		{#each PICK as [lang, short] (lang)}
			<button
				type="button"
				data-pick={lang}
				aria-pressed="true"
				class="cursor-pointer rounded-md px-2 py-1 text-neutral-500 hover:bg-neutral-100 aria-[pressed=false]:line-through aria-[pressed=false]:opacity-40 dark:text-neutral-400 dark:hover:bg-neutral-800"
				>{short}</button
			>
		{/each}
	</div>
</nav>

<main class="mx-auto max-w-7xl px-4 py-8">
	{@render children()}
</main>
