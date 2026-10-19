<script lang="ts">
	import './layout.css';
	import favicon from '#lib/assets/favicon.svg';
	import { page } from '$app/state';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

	const PICK = [
		['python', 'py'],
		['rust', 'rs'],
		['go', 'go']
	];

	const SHORTCUTS = [
		['⌘K', 'Search sections'],
		['1 2 3', 'Toggle Python / Rust / Go'],
		['j k', 'Next / previous section'],
		['n p', 'Next / previous code row'],
		['. ,', 'Next / previous part (Esc clears)'],
		['?', 'This list']
	];

	const sectionsJson = $derived(JSON.stringify(data.sections).replaceAll('<', '\\u003c'));

	const inlineScript = `<script>
	if (navigator.clipboard) document.documentElement.dataset.copy = '';
	const html = document.documentElement;
	html.dataset.hide = localStorage.getItem('hide') ?? '';
	const syncPicker = () => {
		const hidden = html.dataset.hide.split(' ');
		for (const b of document.querySelectorAll('[data-pick]'))
			b.setAttribute('aria-pressed', String(!hidden.includes(b.dataset.pick)));
	};
	const trackSections = () => {
		const toc = document.querySelector('nav[aria-label="Sections"]');
		if (!toc) return;
		const links = [...toc.querySelectorAll('li a[href^="#"]')];
		const heads = links.map((a) => document.getElementById(decodeURIComponent(a.hash.slice(1))));
		let queued = false;
		const update = () => {
			queued = false;
			const i = Math.max(0, heads.findLastIndex((h) => h && h.getBoundingClientRect().top <= 96));
			links.forEach((a, k) => a.toggleAttribute('aria-current', k === i));
			if (toc.scrollHeight > toc.clientHeight) links[i].scrollIntoView({ block: 'nearest' });
		};
		addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(update); } }, { passive: true });
		update();
	};
	document.addEventListener('DOMContentLoaded', () => { syncPicker(); trackSections(); });
	let hovered = null;
	document.addEventListener('mouseover', (event) => {
		const part = event.target.closest('[data-part]');
		if (part === hovered) return;
		hovered = part;
		for (const lit of document.querySelectorAll('[data-lit]')) lit.removeAttribute('data-lit');
		if (!part) return;
		const path = part.dataset.part.split('.');
		const same = path.map((_, i) => '[data-part="' + path.slice(0, i + 1).join('.') + '"]').join(', ');
		for (const lit of part.closest('.cols').querySelectorAll(same)) lit.setAttribute('data-lit', '');
	});
	const fields = 'input, textarea, select, [contenteditable]';
	const byId = (id) => document.getElementById(id);
	let entries;
	let selected = 0;
	const select = (i) => {
		const items = [...byId('palette-list').children];
		if (!items.length) return;
		selected = (i + items.length) % items.length;
		items.forEach((li, k) => li.setAttribute('aria-selected', String(k === selected)));
		byId('palette-input').setAttribute('aria-activedescendant', items[selected].id);
		items[selected].scrollIntoView({ block: 'nearest' });
	};
	const search = () => {
		entries ??= JSON.parse(byId('sections').textContent).map((e) => ({ ...e, text: [e.page, e.group, e.title].join(' ').toLowerCase() }));
		const terms = byId('palette-input').value.toLowerCase().split(' ').filter(Boolean);
		const hits = entries.filter((e) => terms.every((t) => e.text.includes(t))).slice(0, 12);
		byId('palette-list').replaceChildren(...hits.map((e, k) => {
			const li = document.createElement('li');
			const a = document.createElement('a');
			const context = document.createElement('span');
			li.id = 'palette-option-' + k;
			li.setAttribute('role', 'option');
			a.href = e.href;
			a.append(e.title);
			context.textContent = [e.page, e.group].filter(Boolean).join(' › ');
			a.append(context);
			li.append(a);
			return li;
		}));
		select(0);
	};
	const openPalette = () => {
		byId('palette').showModal();
		byId('palette-input').value = '';
		search();
	};
	const paletteKey = (event) => {
		const keys = {
			ArrowDown: () => select(selected + 1),
			ArrowUp: () => select(selected - 1),
			Enter: () => byId('palette-list').children[selected]?.firstChild.click(),
			Escape: () => byId('palette').close()
		};
		if (!keys[event.key]) return;
		event.preventDefault();
		keys[event.key]();
	};
	document.addEventListener('keydown', (event) => {
		const target = event.target;
		if ((event.metaKey || event.ctrlKey) && !event.altKey && event.key === 'k') {
			if (target.closest(fields) && target.id !== 'palette-input') return;
			event.preventDefault();
			byId('palette').open ? byId('palette').close() : openPalette();
			return;
		}
		if (target.id === 'palette-input') return paletteKey(event);
		if (event.metaKey || event.ctrlKey || event.altKey || target.closest(fields)) return;
		if (document.querySelector('dialog[open]')) return;
		shortcut(event);
	});
	document.addEventListener('input', (event) => {
		if (event.target.id === 'palette-input') search();
	});
	document.addEventListener('click', (event) => {
		if (event.target.closest('[data-palette]')) openPalette();
		if (event.target.localName === 'dialog') event.target.close();
		if (event.target.closest('#palette-list a')) byId('palette').close();
	});
	const toggleLang = (name) => {
		const hidden = new Set(html.dataset.hide.split(' ').filter(Boolean));
		hidden.has(name) ? hidden.delete(name) : hidden.add(name);
		html.dataset.hide = [...hidden].join(' ');
		localStorage.setItem('hide', html.dataset.hide);
		syncPicker();
	};
	const stepSection = (step) => {
		const links = [...document.querySelectorAll('nav[aria-label="Sections"] li a[href^="#"]')];
		if (!links.length) return;
		const i = links.findIndex((a) => a.hasAttribute('aria-current'));
		const next = links[Math.min(links.length - 1, Math.max(0, i + step))];
		document.getElementById(decodeURIComponent(next.hash.slice(1))).scrollIntoView({ block: 'start' });
	};
	const stepRow = (step) => {
		const rows = [...document.querySelectorAll('.cols')].filter((r) => r.offsetHeight);
		const top = (r) => r.getBoundingClientRect().top;
		(step > 0 ? rows.find((r) => top(r) > 60) : rows.findLast((r) => top(r) < 52))?.scrollIntoView({ block: 'start' });
	};
	const partCount = (row) => Math.max(0, ...[...row.querySelectorAll('[data-part]')].filter((e) => e.checkVisibility()).map((e) => parseInt(e.dataset.part) + 1));
	const clearPart = () => document.querySelector('[data-part-active]')?.removeAttribute('data-part-active');
	const stepPart = (step) => {
		const rows = [...document.querySelectorAll('.cols')].filter((r) => r.offsetHeight && partCount(r));
		if (!rows.length) return;
		const active = rows.find((r) => r.hasAttribute('data-part-active'));
		let i = active ? rows.indexOf(active) : rows.findIndex((r) => r.getBoundingClientRect().bottom > 60);
		if (i < 0) i = rows.length - 1;
		let part = (active ? +active.dataset.partActive : step > 0 ? -1 : partCount(rows[i])) + step;
		if (part >= partCount(rows[i]) || part < 0) {
			i += step;
			if (!rows[i]) return;
			part = step > 0 ? 0 : partCount(rows[i]) - 1;
		}
		clearPart();
		rows[i].dataset.partActive = part;
		[...rows[i].querySelectorAll('[data-part="' + part + '"]')].find((e) => e.checkVisibility())?.scrollIntoView({ block: 'nearest' });
	};
	const shortcut = (event) => {
		const picks = document.querySelector('[data-compare]') ? [...document.querySelectorAll('[data-pick]')] : [];
		const keys = {
			1: () => picks[0] && toggleLang(picks[0].dataset.pick),
			2: () => picks[1] && toggleLang(picks[1].dataset.pick),
			3: () => picks[2] && toggleLang(picks[2].dataset.pick),
			j: () => stepSection(1),
			k: () => stepSection(-1),
			n: () => stepRow(1),
			p: () => stepRow(-1),
			'.': () => stepPart(1),
			',': () => stepPart(-1),
			Escape: clearPart,
			'?': () => byId('help').showModal()
		};
		if (!keys[event.key]) return;
		event.preventDefault();
		keys[event.key]();
	};
	document.addEventListener('click', (event) => {
		const button = event.target.closest('[data-pick]');
		if (button) toggleLang(button.dataset.pick);
		if (event.target.closest('[data-help]')) byId('help').showModal();
	});
	document.addEventListener('click', async (event) => {
		const line = event.target.closest('.copy-line');
		if (line) {
			await navigator.clipboard.writeText(line.parentElement.textContent);
			line.dataset.copied = '';
			return setTimeout(() => delete line.dataset.copied, 1500);
		}
		const button = event.target.closest('.copy');
		if (!button) return;
		const code = [...button.closest('.col').querySelectorAll('.snippet pre')].map((pre) => pre.textContent);
		await navigator.clipboard.writeText(code.join('\\n'));
		button.textContent = 'Copied';
		setTimeout(() => (button.textContent = 'Copy'), 1500);
	});
<\/script>`;
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	{@html inlineScript}
	{@html '<script type="application/json" id="sections">' + sectionsJson + '<\/script>'}
</svelte:head>

<nav
	class="sticky top-0 z-10 flex gap-1 overflow-x-auto border-b border-neutral-200 bg-white/90 px-4 py-2 text-sm backdrop-blur dark:border-neutral-800 dark:bg-neutral-950/90"
>
	<a href="/" class="px-2 py-1 font-semibold whitespace-nowrap">pygors</a>
	{#each data.nav as item (item.href)}
		<a
			href={item.href}
			aria-current={page.url.pathname === item.href ? 'page' : undefined}
			class="rounded-md px-3 py-1 whitespace-nowrap text-neutral-500 hover:bg-neutral-100 hover:text-neutral-900 aria-[current=page]:bg-neutral-100 aria-[current=page]:text-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:hover:text-neutral-50 dark:aria-[current=page]:bg-neutral-800 dark:aria-[current=page]:text-neutral-50"
			>{item.title}</a
		>
	{/each}
	<div class="ml-auto flex gap-1 font-mono text-xs">
		<div class="picker flex gap-1" role="group" aria-label="Show languages">
			{#each PICK as [lang, short] (lang)}
				<button
					type="button"
					data-pick={lang}
					aria-pressed="true"
					class="cursor-pointer rounded-md px-2 py-1 text-neutral-500 hover:bg-neutral-100 aria-[pressed=false]:line-through aria-[pressed=false]:opacity-40 dark:text-neutral-400 dark:hover:bg-neutral-800"
					>{short}</button
				>
			{/each}
		</div>
		<button
			type="button"
			data-palette
			aria-label="Search sections"
			class="cursor-pointer rounded-md px-2 py-1 whitespace-nowrap text-neutral-500 hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800"
			>search <kbd>⌘K</kbd></button
		>
		<button
			type="button"
			data-help
			aria-label="Keyboard shortcuts"
			class="cursor-pointer rounded-md px-2 py-1 text-neutral-500 hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800"
			><kbd>?</kbd></button
		>
	</div>
</nav>

<dialog
	id="help"
	aria-label="Keyboard shortcuts"
	class="m-auto w-[min(26rem,calc(100vw-2rem))] rounded-lg border border-neutral-200 bg-white p-5 text-sm text-neutral-900 shadow-xl dark:border-neutral-800 dark:bg-neutral-900 dark:text-neutral-100"
>
	<table class="w-full">
		<tbody>
			{#each SHORTCUTS as [keys, action] (keys)}
				<tr>
					<th scope="row" class="py-1 pr-4 text-left font-mono font-normal whitespace-nowrap"
						><kbd>{keys}</kbd></th
					>
					<td class="py-1 text-neutral-500 dark:text-neutral-400">{action}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</dialog>

<dialog
	id="palette"
	aria-label="Search sections"
	class="mx-auto mt-[12vh] mb-auto w-[min(36rem,calc(100vw-2rem))] rounded-lg border border-neutral-200 bg-white p-0 text-neutral-900 shadow-xl dark:border-neutral-800 dark:bg-neutral-900 dark:text-neutral-100"
>
	<input
		id="palette-input"
		type="search"
		role="combobox"
		aria-controls="palette-list"
		aria-expanded="true"
		placeholder="Jump to a section"
		autocomplete="off"
		class="w-full border-b border-neutral-200 bg-transparent px-4 py-3 outline-none dark:border-neutral-800"
	/>
	<ul id="palette-list" role="listbox" class="max-h-[60vh] overflow-y-auto p-1 text-sm"></ul>
</dialog>

<main class="mx-auto max-w-7xl px-4 py-8">
	{@render children()}
</main>
