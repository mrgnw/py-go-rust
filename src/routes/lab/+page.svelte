<script lang="ts">
	import Pivot from '#lib/Pivot.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<meta name="robots" content="noindex" />
</svelte:head>

<section class="mx-auto max-w-3xl pb-16">
	<h1 class="mb-2 text-3xl font-bold">Lab: pivoted parts</h1>
	<p class="mb-8 text-sm text-neutral-500 dark:text-neutral-400">
		Experiment. The first row of every Patterns section with parts, one box per part, each
		language's lines stacked.
	</p>
	{#each data.sections as section (section.id)}
		<h2 class="mt-10 mb-3 text-xl font-semibold">
			{section.title}
			<a href="/compare#{section.id}" class="ml-2 text-sm font-normal text-neutral-500">columns →</a
			>
		</h2>
		<Pivot cols={section.cols} lists={section.cols.map((c) => c.parts)} />
	{/each}
</section>
