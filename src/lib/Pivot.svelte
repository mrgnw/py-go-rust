<script lang="ts">
	import { sameValue } from './content/diff';
	import type { Col, Part } from './content/langs';

	let { cols, lists }: { cols: Col[]; lists: Part[][] } = $props();

	const SHORT: Record<string, string> = { python: 'py', rust: 'rs', go: 'go' };
	const leaves = (parts: Part[]): Part[] =>
		parts.flatMap((part) => (part.parts.length ? leaves(part.parts) : [part]));
	const steps = $derived.by(() => {
		const columns = lists.map(leaves);
		return columns[0].flatMap((_, k) => {
			const lines = cols
				.map((col, i) => ({ col, part: columns[i][k] }))
				.filter((line) => line.part.html);
			const outputs = lines.flatMap((line) => line.part.output ?? []);
			const shared = new Set(outputs.map(sameValue)).size === 1;
			const label = columns.find((leaves) => leaves[k].label)?.[k].label;
			return lines.length ? [{ k, label, lines, output: shared ? outputs[0] : undefined }] : [];
		});
	});
</script>

<div class="pivot flex flex-col gap-2 pl-8">
	{#each steps as step (step.k)}
		<div
			class="relative rounded-lg border border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-900"
		>
			{#if step.label}
				<div
					class="px-3 text-right font-mono text-[0.7rem] leading-[1.2rem] text-neutral-400 select-none dark:text-neutral-500"
				>
					{step.label}
				</div>
			{/if}
			{#if step.output !== undefined}
				<pre class="out border-b border-neutral-200 dark:border-neutral-800">{step.output}</pre>
			{/if}
			<div class="lines">
				{#each step.lines as { col, part } (col)}
					<div
						data-lang={col.lang}
						class="relative border-t border-neutral-200 py-1.5 dark:border-neutral-800"
					>
						<span
							class="absolute right-full mr-3 font-mono text-xs leading-[1.2rem] text-neutral-400 dark:text-neutral-500"
							>{SHORT[col.lang ?? ''] ?? col.label}</span
						>
						{@html part.html}
						{#if step.output === undefined && part.output}
							<pre class="out">{part.output}</pre>
						{/if}
					</div>
				{/each}
			</div>
		</div>
	{/each}
</div>

<style>
	.pivot .lines :global(pre.shiki),
	.out {
		margin: 0;
		padding: 0 0.75rem;
		overflow-x: auto;
		font-size: 0.8rem;
		line-height: 1.5;
		tab-size: 4;
		background: transparent !important;
	}
	.lines {
		clip-path: inset(1px -10rem 0 -10rem);
	}
	.out {
		padding-block: 0.375rem;
		font-weight: 600;
	}
</style>
