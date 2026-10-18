<script lang="ts">
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const LABELS: Record<string, string> = { python: 'py', rust: 'rs', go: 'go' };
</script>

<svelte:head>
	<meta name="robots" content="noindex" />
</svelte:head>

<section class="lab mx-auto max-w-3xl pb-16">
	<h1 class="mb-2 text-3xl font-bold">Lab: pivoted rows</h1>
	<p class="mb-8 text-sm text-neutral-500 dark:text-neutral-400">
		Experiment. Side by side rows whose output matches in every language, one step per output.
	</p>
	{#each data.sections as section (section.id)}
		<h2 class="mt-10 mb-3 text-xl font-semibold">
			{section.title}
			<a href="/compare#{section.id}" class="ml-2 text-sm font-normal text-neutral-500">columns →</a
			>
		</h2>
		<div class="flex flex-col gap-2 pl-8">
			{#each section.steps as step}
				<div
					class="rounded-lg border border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-900"
				>
					{#if step.output !== undefined}
						<pre
							class="border-b border-neutral-200 px-3 py-1.5 font-mono text-[0.8rem] font-semibold dark:border-neutral-800">{step.output}</pre>
					{/if}
					<div class:divide-y={step.multi} class="divide-neutral-200 dark:divide-neutral-800">
						{#each step.lines as line}
							<div
								data-lang={line.lang}
								class="relative {step.multi ? 'py-1.5' : 'first:pt-1.5 last:pb-1.5'}"
							>
								<span
									class="absolute right-full mr-3 font-mono text-xs leading-[1.2rem] text-neutral-400 dark:text-neutral-500"
									>{LABELS[line.lang] ?? line.lang}</span
								>
								{@html line.html}
							</div>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	{/each}
</section>

<style>
	.lab :global(pre.shiki) {
		margin: 0;
		padding: 0 0.75rem;
		overflow-x: auto;
		font-size: 0.8rem;
		line-height: 1.5;
		tab-size: 4;
		background: transparent !important;
	}
</style>
