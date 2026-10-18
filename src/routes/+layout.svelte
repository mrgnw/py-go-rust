<script lang="ts">
	import './layout.css';
	import favicon from '#lib/assets/favicon.svg';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

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

{@render children()}
