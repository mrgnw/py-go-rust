<script lang="ts">
	import type { LangPage } from './content/langs';

	let { page }: { page: LangPage } = $props();
	const toc = $derived(page.blocks.flatMap((b) => (b.kind === 'h2' ? [b] : [])));
	const compares = $derived(
		new Set(
			page.blocks.flatMap((b) => (b.kind === 'code' ? b.cols.flatMap((c) => c.lang ?? []) : []))
		).size > 1
	);
</script>

<section class="langs pb-16" data-compare={compares || undefined}>
	<h1 class="mb-2 text-3xl font-bold">{page.title}</h1>
	<div class="lg:grid lg:grid-cols-[13rem_minmax(0,1fr)] lg:gap-10">
		<!-- ponytail: no active state; scroll-driven animations and :target-current are not Baseline yet (Firefox missing) -->
		<nav
			aria-label="Sections"
			class="mb-8 lg:sticky lg:top-16 lg:mb-0 lg:max-h-[calc(100dvh-5rem)] lg:self-start lg:overflow-y-auto"
		>
			<ul class="flex flex-wrap gap-x-3 gap-y-1 text-sm lg:flex-col lg:gap-x-0">
				{#each toc as h2 (h2.id)}
					<li>
						<a
							href="#{h2.id}"
							class="text-neutral-500 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-50"
							>{h2.title}</a
						>
					</li>
				{/each}
			</ul>
		</nav>
		<div class="min-w-0">
			{#each page.blocks as block}
				{#if block.kind === 'h2'}
					<h2 id={block.id} class="mt-10 mb-3 scroll-mt-14 text-xl font-semibold first:mt-0">
						<a href="#{block.id}">{block.title}</a>
					</h2>
				{:else if block.kind === 'html'}
					<div class="prose prose-sm max-w-none prose-neutral dark:prose-invert">
						{@html block.html}
					</div>
				{:else if block.kind === 'code'}
					<div class="my-3 flex flex-col gap-2">
						{#if block.output}
							<div
								class="out rounded-lg border border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-900"
							>
								{@render label(block.output.label)}
								{@html block.output.html}
							</div>
						{/if}
						<div class="cols flex gap-3">
							{#each block.cols as col}
								<div
									data-lang={col.lang}
									class="col min-w-0 overflow-hidden rounded-lg border border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-900"
								>
									{@render label(col.label)}
									{#if col.output}
										<div class="out border-b border-neutral-200 dark:border-neutral-800">
											{@html col.output.html}
										</div>
									{/if}
									{@html col.html}
								</div>
							{/each}
						</div>
					</div>
				{/if}
			{/each}
		</div>
	</div>
</section>

{#snippet label(text: string)}
	<div
		class="border-b border-neutral-200 px-3 py-1 font-mono text-xs text-neutral-500 dark:border-neutral-800 dark:text-neutral-400"
	>
		{text}
	</div>
{/snippet}

<style>
	.col {
		flex: 1 1 0;
	}
	@media (max-width: 56rem) {
		.cols {
			flex-direction: column;
		}
	}
	.langs :global(.out pre.shiki) {
		padding: 0.5rem 0.75rem;
		font-weight: 600;
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
