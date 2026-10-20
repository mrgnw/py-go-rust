<script lang="ts">
	import type { Col, LangPage, Part } from './content/langs';
	import Pivot from './Pivot.svelte';

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
	<div class="mb-2 flex items-center gap-3">
		{#if toc.length}
			<button
				type="button"
				data-sidebar-toggle
				aria-expanded="true"
				aria-controls="sections-nav"
				aria-keyshortcuts="b"
				class="sidebar-toggle cursor-pointer rounded-md px-2 py-1 font-mono text-xs text-neutral-500 hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800"
				>Sections</button
			>
		{/if}
		<h1 class="text-3xl font-bold">{page.title}</h1>
	</div>
	<div class="sidebar-grid lg:grid lg:grid-cols-[13rem_minmax(0,1fr)] lg:gap-x-10">
		<nav
			id="sections-nav"
			aria-label="Sections"
			class="mb-8 lg:sticky lg:top-16 lg:mb-0 lg:max-h-[calc(100dvh-5rem)] lg:w-52 lg:self-start lg:overflow-y-auto lg:overflow-x-hidden"
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
					{@const linked =
						block.cols[0].parts.length > 1 || block.cols[0].parts[0].parts.length > 0}
					<div
						class="row my-3 overflow-hidden rounded-lg border border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-900"
					>
						{@render columns(block.cols, (col) => col.parts, linked, true, true)}
						{#each block.cols[0].parts.filter((part) => part.parts.length) as group (group.path)}
							{@const k = Number(group.path)}
							<div data-split={group.path} hidden>
								{@render columns(block.cols, (col) => col.parts.slice(0, k), true, true, false)}
								<div
									data-collapse
									class="border-y border-neutral-200 pt-1 pr-3 pb-3 pl-2 dark:border-neutral-800"
								>
									<div class="flex justify-end">
										{@render toggle(true)}
									</div>
									<Pivot cols={block.cols} lists={block.cols.map((col) => col.parts[k].parts)} />
								</div>
								{@render columns(block.cols, (col) => col.parts.slice(k + 1), true, false, true)}
							</div>
						{/each}
					</div>
				{/if}
			{/each}
		</div>
	</div>
</section>

{#snippet columns(
	cols: Col[],
	pick: (col: Col) => Part[],
	linked: boolean,
	head: boolean,
	foot: boolean
)}
	<div class="cols">
		{#each cols as col}
			<div data-lang={col.lang} class="col min-w-0 border-neutral-200 dark:border-neutral-800">
				{#if head}
					{@render label(col.label, foot)}
				{/if}
				{#if pick(col).length}
					<div class="snippet">
						{@render parts(pick(col), linked)}
					</div>
				{/if}
				{#if foot && col.output}
					{@render output(col.output)}
				{/if}
			</div>
		{/each}
	</div>
{/snippet}

{#snippet toggle(expanded: boolean)}
	<button
		type="button"
		data-toggle
		aria-expanded={expanded}
		class="toggle cursor-pointer rounded px-1.5 font-mono text-[0.7rem] leading-[1.2rem] text-neutral-500 dark:text-neutral-400"
		>{expanded ? 'columns' : 'pivot'}</button
	>
{/snippet}

{#snippet parts(list: Part[], linked: boolean)}
	{#each list as part (part.path)}
		<div
			class="part"
			data-part={linked ? part.path : undefined}
			data-group={part.parts.length ? part.path : undefined}
			style:--pad-top={part.pad[0] || undefined}
			style:--pad-bottom={part.pad[1] || undefined}
		>
			{#if linked}
				<div
					class="tools flex items-start justify-end gap-x-2 pr-2 pl-1 font-mono text-[0.7rem] leading-[1.2rem] whitespace-nowrap select-none"
				>
					{#if part.label}
						<span class="max-w-40 truncate text-neutral-400 dark:text-neutral-500"
							>{part.label}</span
						>
					{/if}
					<button type="button" class="copy-part" aria-label="Copy part">Copy</button>
					{#if part.parts.length}
						{@render toggle(false)}
					{/if}
				</div>
			{/if}
			{#if part.parts.length}
				{@render parts(part.parts, true)}
			{:else}
				{@html part.html}
			{/if}
		</div>
	{/each}
{/snippet}

{#snippet output(html: string)}
	<div
		class="out flex border-t border-neutral-200 bg-neutral-100 text-neutral-800 dark:border-neutral-800 dark:bg-neutral-950 dark:text-neutral-200"
	>
		<span class="px-3 py-1.5 font-mono text-xs text-neutral-400 select-none dark:text-neutral-500">
			&rsaquo;
		</span>
		{@html html}
	</div>
{/snippet}

{#snippet label(text: string, copy: boolean)}
	<div
		class="flex items-center justify-between gap-3 border-b border-neutral-200 px-3 py-1 font-mono text-xs text-neutral-500 dark:border-neutral-800 dark:text-neutral-400"
	>
		{text}
		{#if copy}
			<button type="button" class="copy" aria-label="Copy {text}">Copy</button>
		{/if}
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
	/* output tokens another column lacks take their language's color; matches stay neutral */
	.langs :global(.out .diff) {
		color: var(--odd);
	}
	[data-lang='python'] .out {
		--odd: light-dark(var(--color-blue-600), var(--color-blue-300));
	}
	[data-lang='rust'] .out {
		--odd: light-dark(var(--color-orange-600), var(--color-orange-300));
	}
	[data-lang='go'] .out {
		--odd: light-dark(var(--color-teal-600), var(--color-teal-300));
	}
	/* parts are invisible until hovered: no rules, no gaps. The layout script marks the hovered part
	   and its parent with data-lit in every column; a lit child sits darker inside its lit parent.
	   Keyboard stepping lights the same way and walks top-level parts only. */
	.snippet {
		padding-block: 0.75rem;
	}
	.part {
		position: relative;
		scroll-margin-block: 4rem;
		--tools: hidden;
		display: grid;
		grid-template-columns: minmax(0, 1fr) 0;
		font-size: 0.8rem;
		line-height: 1.5;
		padding-top: calc(var(--pad-top, 0) * 1lh);
		padding-bottom: calc(var(--pad-bottom, 0) * 1lh);
	}
	.part > :not(.tools) {
		grid-column: 1;
	}
	.tools {
		grid-column: 2;
		grid-row: 1;
		justify-self: end;
		visibility: var(--tools);
	}
	.part:global([data-lit]),
	.part:has(> .tools:focus-within) {
		grid-template-columns: minmax(0, 1fr) auto;
	}
	.tools :global(.copy-part) {
		padding-block: 0;
		padding-inline: 0.375rem;
		font-size: inherit;
		line-height: inherit;
	}
	.tools .toggle {
		visibility: visible;
		opacity: 0;
	}
	.part:global([data-lit]) > .tools .toggle,
	.tools .toggle:focus {
		opacity: 1;
	}
	@media print {
		.tools {
			display: none;
		}
	}
	.part[data-group],
	[data-collapse] {
		cursor: pointer;
	}
	.langs .part :global(pre.shiki) {
		padding-top: 0;
		padding-bottom: 0;
	}
	.part:global([data-lit]) {
		--tools: visible;
		background: light-dark(
			color-mix(in oklab, var(--color-amber-200) 35%, transparent),
			color-mix(in oklab, var(--color-amber-300) 12%, transparent)
		);
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
