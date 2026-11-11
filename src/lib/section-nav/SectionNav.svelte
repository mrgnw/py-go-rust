<script module lang="ts">
	export type Section = { id: string; title: string; group?: boolean };
</script>

<script lang="ts">
	import { onMount, tick, type Snippet } from 'svelte';

	type Props = {
		sections?: Section[];
		levels?: string;
		key?: string;
		label?: string;
		children?: Snippet;
	};

	const MAX_HEADINGS = 200;
	const ACTIVE_LINE = 96;

	let {
		sections,
		levels = 'h2,h3',
		key = 'sidebar',
		label = 'Sections',
		children
	}: Props = $props();

	let scanned = $state<Section[]>([]);
	let current = $state(0);
	let collapsed = $state(false);
	let nav: HTMLElement;
	let content: HTMLElement;
	let frame = 0;
	let aimed = '';

	let entries = $derived(sections ?? scanned);
	let items = $derived(entries.filter((entry) => !entry.group));
	let groups = $derived.by(() => {
		const out: { head?: Section; items: { section: Section; index: number }[] }[] = [];
		let index = 0;
		for (const entry of entries) {
			if (entry.group) {
				out.push({ head: entry, items: [] });
				continue;
			}
			if (!out.length) out.push({ items: [] });
			out[out.length - 1].items.push({ section: entry, index: index++ });
		}
		return out;
	});

	function slugify(text: string) {
		return (
			text
				.toLowerCase()
				.replace(/[^a-z0-9]+/g, '-')
				.replace(/^-+|-+$/g, '') || 'section'
		);
	}

	function scan(): Section[] {
		const roots = content.querySelector('slot')?.assignedElements() ?? [content];
		const found = roots
			.flatMap((root) => [
				...(root.matches(levels) ? [root] : []),
				...root.querySelectorAll(levels)
			])
			.slice(0, MAX_HEADINGS) as HTMLElement[];
		const tags = levels.split(',').map((tag) => tag.trim());
		const grouped =
			tags.length === 2 &&
			found.some((heading) => heading.matches(tags[0])) &&
			found.some((heading) => heading.matches(tags[1]));
		const used = new Set(found.map((heading) => heading.id).filter(Boolean));
		return found.map((heading) => {
			const title = heading.textContent?.trim() ?? '';
			if (!heading.id) {
				const base = slugify(title);
				let id = base;
				for (let n = 2; used.has(id); n++) id = `${base}-${n}`;
				used.add(id);
				heading.id = id;
			}
			heading.style.scrollMarginTop ||= 'var(--nav-top, 1rem)';
			return { id: heading.id, title, group: grouped && heading.matches(tags[0]) };
		});
	}

	function atBottom() {
		return innerHeight + scrollY >= document.documentElement.scrollHeight - 1;
	}

	async function update() {
		let reached = 0;
		items.forEach((item, index) => {
			const heading = document.getElementById(item.id);
			if (heading && heading.getBoundingClientRect().top <= ACTIVE_LINE) reached = index;
		});
		const target = items.findIndex((item) => item.id === aimed);
		const heading = document.getElementById(aimed);
		const visible = heading !== null && heading.getBoundingClientRect().top < innerHeight;
		const next = target > reached && visible && atBottom() ? target : reached;
		if (next === current) return;
		current = next;
		await tick();
		if (nav.scrollHeight > nav.clientHeight) {
			nav.querySelector('[aria-current]')?.scrollIntoView({ block: 'nearest' });
		}
	}

	function aimAtHash() {
		aimed = decodeURIComponent(location.hash.slice(1));
		update();
	}

	function onscroll() {
		if (frame) return;
		frame = requestAnimationFrame(() => {
			frame = 0;
			update();
		});
	}

	function toggle() {
		const apply = async () => {
			collapsed = !collapsed;
			localStorage.setItem(key, collapsed ? 'collapsed' : '');
			await tick();
		};
		if (document.startViewTransition && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
			document.startViewTransition(apply);
		} else {
			apply();
		}
	}

	function step(delta: number) {
		const target = items[Math.min(items.length - 1, Math.max(0, current + delta))];
		if (target) {
			aimed = target.id;
			document.getElementById(target.id)?.scrollIntoView({ block: 'start', behavior: 'instant' });
			update();
		}
	}

	function onkeydown(event: KeyboardEvent) {
		if (event.metaKey || event.ctrlKey || event.altKey) return;
		const target = event.target;
		if (target instanceof Element && target.closest('input, textarea, select, [contenteditable]'))
			return;
		if (document.querySelector('dialog[open]')) return;
		if (event.key === 'b') toggle();
		else if (event.key === 'j') step(1);
		else if (event.key === 'k') step(-1);
		else return;
		event.preventDefault();
	}

	function closePopover() {
		if (nav.matches(':popover-open')) nav.hidePopover();
	}

	onMount(() => {
		collapsed = localStorage.getItem(key) === 'collapsed';
		if (!sections) scanned = scan();
		aimAtHash();
	});
</script>

<svelte:window {onscroll} onresize={onscroll} onhashchange={aimAtHash} />
<svelte:document {onkeydown} />

<div class="layout" class:collapsed>
	<div class="side">
		<button
			class="handle"
			aria-expanded={!collapsed}
			aria-controls="sections-nav"
			aria-keyshortcuts="b"
			aria-label={label}
			title="{label} (b)"
			onclick={toggle}
		>
			<svg
				viewBox="0 0 16 16"
				width="16"
				height="16"
				fill="none"
				stroke="currentColor"
				stroke-width="1.25"
				aria-hidden="true"
				><rect x="1.5" y="2.5" width="13" height="11" rx="2" /><path d="M6 2.5v11" /></svg
			>
		</button>
		<button class="bar" popovertarget="sections-nav">
			<span class="now">{items[current]?.title ?? label}</span><span aria-hidden="true">▾</span>
		</button>
		<nav id="sections-nav" aria-label={label} popover bind:this={nav}>
			{#each groups as group (group.head?.id ?? '')}
				{#if group.head}
					<a class="group" href="#{group.head.id}" onclick={closePopover}>{group.head.title}</a>
				{/if}
				{#if group.items.length}
					<ul>
						{#each group.items as { section, index } (section.id)}
							<li>
								<a
									href="#{section.id}"
									aria-current={index === current ? 'location' : undefined}
									onclick={closePopover}>{section.title}</a
								>
							</li>
						{/each}
					</ul>
				{/if}
			{/each}
		</nav>
	</div>
	<div class="content" bind:this={content}>{@render children?.()}</div>
</div>

<style>
	button {
		font: inherit;
		color: var(--nav-muted, color-mix(in oklab, currentColor 55%, transparent));
		background: none;
		border: 0;
		cursor: pointer;
	}

	button:hover {
		color: inherit;
	}

	.side {
		position: sticky;
		top: var(--bar-top, 0);
		z-index: 1;
	}

	.handle {
		display: none;
		padding: 0.25rem;
		line-height: 0;
	}

	.bar {
		display: flex;
		justify-content: space-between;
		gap: 0.5rem;
		width: 100%;
		padding: 0.625rem 0;
		text-align: left;
		font-size: 0.875rem;
		border-bottom: 1px solid var(--nav-line, color-mix(in oklab, currentColor 15%, transparent));
		background: var(--nav-bg, Canvas);
	}

	.now {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	nav {
		position: fixed;
		inset: auto 1rem;
		top: calc(var(--bar-top, 0px) + 3rem);
		width: auto;
		margin: 0;
		max-height: 70dvh;
		overflow: auto;
		padding: 1rem;
		border: 1px solid var(--nav-line, color-mix(in oklab, currentColor 15%, transparent));
		border-radius: 0.5rem;
		background: var(--nav-bg, Canvas);
		color: inherit;
		font-size: 0.875rem;
		box-shadow: 0 0.5rem 1.5rem color-mix(in oklab, black 15%, transparent);
	}

	ul {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}

	a {
		color: var(--nav-muted, color-mix(in oklab, currentColor 55%, transparent));
		text-decoration: none;
	}

	a:hover,
	a[aria-current] {
		color: inherit;
	}

	a[aria-current] {
		font-weight: 500;
	}

	.group {
		display: block;
		margin: 1rem 0 0.25rem;
		font-size: 0.75rem;
		font-weight: 600;
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}

	.group:first-child {
		margin-top: 0;
	}

	@media (prefers-reduced-motion: no-preference) and (width < 64rem) {
		nav {
			opacity: 0;
			translate: 0 -0.25rem;
			transition:
				opacity 0.15s,
				translate 0.15s,
				display 0.15s allow-discrete,
				overlay 0.15s allow-discrete;
		}

		nav:popover-open {
			opacity: 1;
			translate: 0;
		}

		@starting-style {
			nav:popover-open {
				opacity: 0;
				translate: 0 -0.25rem;
			}
		}
	}

	@media (prefers-reduced-motion: no-preference) and (width >= 64rem) {
		nav {
			view-transition-name: section-nav;
		}
	}

	@media (width >= 64rem) {
		.layout {
			display: grid;
			grid-template-columns: var(--nav-width, 13rem) minmax(0, 1fr);
			column-gap: 2.5rem;
		}

		.layout.collapsed {
			grid-template-columns: 1.5rem minmax(0, 1fr);
			column-gap: 1rem;
		}

		.side {
			top: var(--nav-top, 1rem);
			align-self: start;
			max-height: calc(100dvh - var(--nav-top, 1rem) - 1rem);
			display: flex;
			flex-direction: column;
		}

		.bar {
			display: none;
		}

		.handle {
			display: block;
			align-self: flex-start;
			margin-bottom: 0.5rem;
		}

		nav {
			position: static;
			display: block;
			inset: auto;
			max-height: none;
			min-height: 0;
			padding: 0;
			border: 0;
			background: transparent;
			box-shadow: none;
			overflow: auto;
		}

		.collapsed nav {
			display: none;
		}

		ul {
			gap: 0.25rem;
		}
	}
</style>
