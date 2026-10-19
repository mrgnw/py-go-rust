<script lang="ts">
	import type { LangPage } from './content/langs';

	let { page }: { page: LangPage } = $props();
	const grouped = $derived(page.blocks.some((b) => b.kind === 'group'));
	const toc = $derived.by(() => {
		const groups: { id?: string; title?: string; sections: { id: string; title: string }[] }[] = [];
		for (const b of page.blocks) {
			if (b.kind === 'group') groups.push({ id: b.id, title: b.title, sections: [] });
			if (b.kind === 'h2')
				(groups.at(-1) ?? groups[groups.push({ sections: [] }) - 1]).sections.push(b);
		}
		return groups;
	});
	const compares = $derived(
		new Set(
			page.blocks.flatMap((b) => (b.kind === 'code' ? b.cols.flatMap((c) => c.lang ?? []) : []))
		).size > 1
	);
</script>

<section class="langs pb-16" data-compare={compares || undefined}>
	<h1 class="mb-2 text-3xl font-bold">{page.title}</h1>
	<div class="lg:grid lg:grid-cols-[13rem_minmax(0,1fr)] lg:gap-10">
		<nav
			aria-label="Sections"
			class="mb-8 lg:sticky lg:top-16 lg:mb-0 lg:max-h-[calc(100dvh-5rem)] lg:self-start lg:overflow-y-auto"
		>
			{#each toc as group, i (group.title ?? i)}
				{#if group.title}
					<a
						href="#{group.id}"
						class="mt-4 mb-1 block text-xs font-semibold tracking-wide text-neutral-400 uppercase first:mt-0 hover:text-neutral-900 dark:text-neutral-500 dark:hover:text-neutral-50"
					>
						{group.title}
					</a>
				{/if}
				<ul class="flex flex-wrap gap-x-3 gap-y-1 text-sm lg:flex-col lg:gap-x-0">
					{#each group.sections as h2 (h2.id)}
						<li>
							<a
								href="#{h2.id}"
								class="text-neutral-500 hover:text-neutral-900 aria-[current]:font-medium aria-[current]:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-50 dark:aria-[current]:text-neutral-50"
								>{h2.title}</a
							>
						</li>
					{/each}
				</ul>
			{/each}
		</nav>
		<div class="min-w-0">
			{#each page.blocks as block}
				{#if block.kind === 'group'}
					<h2
						id={block.id}
						class="mt-16 mb-6 scroll-mt-14 border-b border-neutral-200 pb-2 text-2xl font-bold first:mt-0 dark:border-neutral-800"
					>
						<a href="#{block.id}">{block.title}</a>
					</h2>
				{:else if block.kind === 'h2'}
					<svelte:element
						this={grouped ? 'h3' : 'h2'}
						id={block.id}
						class="mt-10 mb-3 scroll-mt-14 text-xl font-semibold first:mt-0"
					>
						<a href="#{block.id}">{block.title}</a>
					</svelte:element>
				{:else if block.kind === 'html'}
					<div class="prose prose-sm max-w-none prose-neutral dark:prose-invert">
						{@html block.html}
					</div>
				{:else if block.kind === 'code'}
					<div
						class="my-3 overflow-hidden rounded-lg border border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-900"
					>
						<div class="cols">
							{#each block.cols as col}
								<div
									data-lang={col.lang}
									class="col min-w-0 border-neutral-200 dark:border-neutral-800"
								>
									{@render label(col.label)}
									<div>{@html col.html}</div>
									{#if col.output}
										{@render output(col.output.html, col.odd)}
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/if}
			{/each}
		</div>
	</div>
</section>

{#snippet output(html: string, odd?: boolean)}
	<div
		class:odd
		class="out flex border-t border-neutral-200 bg-neutral-100 text-neutral-800 dark:border-neutral-800 dark:bg-neutral-950 dark:text-neutral-200"
	>
		<span class="px-3 py-1.5 font-mono text-xs text-neutral-400 select-none dark:text-neutral-500">
			&rsaquo;
		</span>
		{@html html}
	</div>
{/snippet}

{#snippet label(text: string)}
	<div
		class="flex items-center justify-between border-b border-neutral-200 px-3 py-1 font-mono text-xs text-neutral-500 dark:border-neutral-800 dark:text-neutral-400"
	>
		{text}
		<button type="button" class="copy" aria-label="Copy {text}">Copy</button>
	</div>
{/snippet}

<style>
	/* label / code / output share three grid rows across the columns, so output strips line up
	   whatever their line count. Every column draws its leading edge and the wrapper clips the
	   first visible one, so hiding any column keeps single dividers. */
	.cols {
		display: grid;
		grid-auto-flow: column;
		grid-auto-columns: minmax(0, 1fr);
		grid-template-rows: auto 1fr auto;
		margin-left: -1px;
	}
	.col {
		display: grid;
		grid-row: span 3;
		grid-template-rows: subgrid;
		grid-template-columns: minmax(0, 1fr);
		border-left-width: 1px;
	}
	.col > * {
		min-width: 0;
	}
	.col > :last-child:nth-child(2) {
		grid-row: span 2;
	}
	@media (max-width: 56rem) {
		.cols {
			grid-auto-flow: row;
			grid-auto-columns: auto;
			grid-template-rows: none;
			margin-left: 0;
			margin-top: -1px;
		}
		.col {
			border-left-width: 0;
			border-top-width: 1px;
		}
	}
	.langs :global(.out pre.shiki) {
		padding: 0.375rem 0.75rem 0.375rem 0;
		font-weight: 600;
	}
	/* an output no other column prints takes its language's color; matching outputs stay neutral */
	.langs :global(.out.odd pre.shiki),
	.langs :global(.out.odd pre.shiki span) {
		color: var(--odd) !important;
	}
	[data-lang='python'] .out.odd {
		--odd: light-dark(var(--color-blue-600), var(--color-blue-300));
	}
	[data-lang='rust'] .out.odd {
		--odd: light-dark(var(--color-orange-600), var(--color-orange-300));
	}
	[data-lang='go'] .out.odd {
		--odd: light-dark(var(--color-teal-600), var(--color-teal-300));
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
