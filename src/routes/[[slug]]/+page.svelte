<script lang="ts">
	import LangPage from '#lib/LangPage.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>{data.page.title} · py · rs · go</title>
	<meta
		name="description"
		content="{data.page.title}: side-by-side Python, Rust and Go cheatsheet."
	/>
</svelte:head>

<LangPage page={data.page} />
