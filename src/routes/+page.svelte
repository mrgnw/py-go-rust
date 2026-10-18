<script lang="ts">
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>Python · Rust · Go</title>
	<meta
		name="description"
		content="Side-by-side cheatsheet: when to pick Python, Rust or Go, and how each one does the same thing."
	/>
</svelte:head>

<nav
	class="sticky top-0 z-10 flex gap-1 overflow-x-auto border-b border-neutral-200 bg-white/90 px-4 py-2 text-sm backdrop-blur dark:border-neutral-800 dark:bg-neutral-950/90"
>
	<a href="#top" class="px-2 py-1 font-semibold whitespace-nowrap">py · rs · go</a>
	{#each data.pages as page (page.slug)}
		<a
			href="#{page.slug}"
			class="rounded-md px-3 py-1 whitespace-nowrap text-neutral-500 hover:bg-neutral-100 hover:text-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:hover:text-neutral-50"
			>{page.title}</a
		>
	{/each}
</nav>

<main id="top" class="langs mx-auto max-w-7xl px-4 py-8">
	{#each data.pages as page (page.slug)}
		<section id={page.slug} class="scroll-mt-14 pb-16">
			{#each page.blocks as block}
				{#if block.kind === 'h1'}
					<h1 class="mb-2 text-3xl font-bold">{block.title}</h1>
					<ul class="mb-8 flex flex-wrap gap-x-3 gap-y-1 text-sm">
						{#each page.blocks.filter((b) => b.kind === 'h2') as h2}
							{#if h2.kind === 'h2'}
								<li>
									<a
										href="#{h2.id}"
										class="text-neutral-500 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-50"
										>{h2.title}</a
									>
								</li>
							{/if}
						{/each}
					</ul>
				{:else if block.kind === 'h2'}
					<h2 id={block.id} class="mt-10 mb-3 scroll-mt-14 text-xl font-semibold">
						<a href="#{block.id}">{block.title}</a>
					</h2>
				{:else if block.kind === 'html'}
					<div class="prose prose-sm max-w-none prose-neutral dark:prose-invert">
						{@html block.html}
					</div>
				{:else}
					<div class="cols my-3 grid gap-3" style:--n={block.cols.length}>
						{#each block.cols as col}
							<div
								class="min-w-0 overflow-hidden rounded-lg border border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-900"
							>
								<div
									class="border-b border-neutral-200 px-3 py-1 font-mono text-xs text-neutral-500 dark:border-neutral-800 dark:text-neutral-400"
								>
									{col.label}
								</div>
								{@html col.html}
							</div>
						{/each}
					</div>
				{/if}
			{/each}
		</section>
	{/each}
</main>

<style>
	.cols {
		grid-template-columns: repeat(var(--n), minmax(0, 1fr));
	}
	@media (max-width: 56rem) {
		.cols {
			grid-template-columns: 1fr;
		}
	}
	.langs :global(.prose code::before),
	.langs :global(.prose code::after) {
		content: none;
	}
	.langs :global(pre.shiki) {
		margin: 0;
		padding: 0.75rem;
		overflow-x: auto;
		font-size: 0.8rem;
		line-height: 1.5;
		tab-size: 4;
		background: transparent !important;
	}
</style>
