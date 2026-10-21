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
		['⇧← ⇧→', 'Move the focused language chip left / right'],
		['j k', 'Next / previous section'],
		['n p', 'Next / previous code row'],
		['. ,', 'Next / previous part (Esc clears)'],
		['b', 'Show / hide the sections sidebar'],
		['?', 'This list']
	];

	const sectionsJson = $derived(JSON.stringify(data.sections).replaceAll('<', '\\u003c'));

	const inlineScript = `<script>
	if (navigator.clipboard) document.documentElement.dataset.copy = '';
	const html = document.documentElement;
	html.dataset.hide = localStorage.getItem('hide') ?? '';
	html.dataset.sidebar = localStorage.getItem('sidebar') ?? '';
	const LANGS = ['python', 'rust', 'go'];
	const showOrder = (order) => {
		html.dataset.order = order.join(' ');
		order.forEach((lang, i) => html.style.setProperty('--order-' + lang, i));
	};
	const saved = (localStorage.getItem('order') ?? '').split(' ');
	showOrder(saved.length === LANGS.length && LANGS.every((lang) => saved.includes(lang)) ? saved : LANGS);
	const currentOrder = () => html.dataset.order.split(' ');
	const place = (lang, slot) => {
		const order = currentOrder().filter((l) => l !== lang);
		order.splice(slot, 0, lang);
		showOrder(order);
	};
	const sortChips = () => {
		const picker = document.querySelector('.picker');
		const order = currentOrder();
		const focused = document.activeElement;
		picker.append(...[...picker.children].sort((a, b) => order.indexOf(a.dataset.pick) - order.indexOf(b.dataset.pick)));
		focused.focus();
	};
	const saveOrder = () => {
		localStorage.setItem('order', html.dataset.order);
		sortChips();
	};
	const transition = (change) => {
		const main = document.querySelector('main');
		if (!main.startViewTransition || matchMedia('(prefers-reduced-motion: reduce)').matches) return change();
		main.startViewTransition(change);
	};
	const moveLang = (lang, step) => transition(() => {
		const to = currentOrder().indexOf(lang) + step;
		if (to < 0 || to >= LANGS.length) return;
		place(lang, to);
		saveOrder();
	});
	const syncSidebar = () => {
		const toggle = document.querySelector('[data-sidebar-toggle]');
		if (toggle) toggle.setAttribute('aria-expanded', String(html.dataset.sidebar !== 'collapsed'));
	};
	const toggleSidebar = () => {
		html.dataset.sidebar = html.dataset.sidebar === 'collapsed' ? '' : 'collapsed';
		localStorage.setItem('sidebar', html.dataset.sidebar);
		syncSidebar();
	};
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
		const now = document.querySelector('[data-section-now]');
		const update = () => {
			queued = false;
			const i = Math.max(0, heads.findLastIndex((h) => h && h.getBoundingClientRect().top <= 96));
			links.forEach((a, k) => a.toggleAttribute('aria-current', k === i));
			now.textContent = links[i].textContent;
			if (toc.scrollHeight > toc.clientHeight) links[i].scrollIntoView({ block: 'nearest' });
		};
		addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(update); } }, { passive: true });
		update();
	};
	document.addEventListener('DOMContentLoaded', () => { sortChips(); syncPicker(); syncSidebar(); trackSections(); });
	const light = (part) => {
		for (const lit of document.querySelectorAll('[data-lit]')) lit.removeAttribute('data-lit');
		if (!part) return;
		const path = part.dataset.part.split('.');
		const same = path.map((_, i) => '[data-part="' + path.slice(0, i + 1).join('.') + '"]').join(', ');
		for (const lit of part.closest('.cols').querySelectorAll(same)) lit.setAttribute('data-lit', '');
	};
	let hovered = null;
	document.addEventListener('mouseover', (event) => {
		const part = event.target.closest('[data-part]');
		if (part === hovered) return;
		hovered = part;
		light(part);
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
	const toggleLang = (name) => transition(() => {
		const hidden = new Set(html.dataset.hide.split(' ').filter(Boolean));
		hidden.has(name) ? hidden.delete(name) : hidden.add(name);
		html.dataset.hide = [...hidden].join(' ');
		localStorage.setItem('hide', html.dataset.hide);
		syncPicker();
	});
	const stepSection = (step) => {
		const links = [...document.querySelectorAll('nav[aria-label="Sections"] li a[href^="#"]')];
		if (!links.length) return;
		const i = links.findIndex((a) => a.hasAttribute('aria-current'));
		const next = links[Math.min(links.length - 1, Math.max(0, i + step))];
		document.getElementById(decodeURIComponent(next.hash.slice(1))).scrollIntoView({ block: 'start', behavior: 'instant' });
	};
	const stepRow = (step) => {
		const rows = [...document.querySelectorAll('.cols')].filter((r) => r.offsetHeight);
		const top = (r) => r.getBoundingClientRect().top;
		(step > 0 ? rows.find((r) => top(r) > 60) : rows.findLast((r) => top(r) < 52))?.scrollIntoView({ block: 'start', behavior: 'instant' });
	};
	const stops = () => [...document.querySelectorAll('.cols')].filter((row) => row.offsetHeight).flatMap((row) => [...new Set([...row.querySelectorAll('.snippet > [data-part]')].filter((e) => e.checkVisibility()).map((e) => e.dataset.part))].map((path) => ({ row, path })));
	const stepPart = (step) => {
		const all = stops();
		if (!all.length) return;
		const lit = document.querySelector('.part[data-lit]');
		const at = lit ? all.findIndex((s) => s.row.contains(lit) && s.path === lit.dataset.part.split('.')[0]) : -1;
		const row = (all.find((s) => s.row.getBoundingClientRect().bottom > 60) ?? all.at(-1)).row;
		const next = at >= 0 ? all[at + step] : step > 0 ? all.find((s) => s.row === row) : all.findLast((s) => s.row === row);
		if (!next) return;
		const target = [...next.row.querySelectorAll('[data-part="' + next.path + '"]')].find((e) => e.checkVisibility());
		light(target);
		target.scrollIntoView({ block: 'nearest' });
	};
	const shortcut = (event) => {
		const lang = (name) => () => document.querySelector('[data-compare]') && toggleLang(name);
		const keys = {
			1: lang('python'),
			2: lang('rust'),
			3: lang('go'),
			b: toggleSidebar,
			j: () => stepSection(1),
			k: () => stepSection(-1),
			n: () => stepRow(1),
			p: () => stepRow(-1),
			'.': () => stepPart(1),
			',': () => stepPart(-1),
			Escape: () => light(null),
			'?': () => byId('help').showModal()
		};
		if (!keys[event.key]) return;
		event.preventDefault();
		keys[event.key]();
	};
	document.addEventListener('click', (event) => {
		const button = event.target.closest('button');
		if ((button && !button.matches('[data-toggle]')) || !getSelection().isCollapsed) return;
		const view = event.target.closest('[data-group], [data-collapse]');
		if (!view) return;
		const row = view.closest('.row');
		const path = view.dataset.group ?? view.parentElement.dataset.split;
		const open = view.dataset.group !== undefined;
		for (const child of row.children) child.hidden = open ? child.dataset.split !== path : child.dataset.split !== undefined;
		hovered = null;
		light(null);
		const shown = open ? row.querySelector('[data-split="' + path + '"] [data-toggle]') : [...row.querySelectorAll('[data-group="' + path + '"] > .tools [data-toggle]')].find((b) => b.checkVisibility());
		if (event.detail === 0) shown?.focus();
	});
	let drag = null;
	let dragged = false;
	document.addEventListener('pointerdown', (event) => {
		const chip = event.target.closest('[data-pick]');
		dragged = false;
		if (!chip || !event.isPrimary || event.button !== 0) return;
		const slots = [...document.querySelectorAll('[data-pick]')].map((b) => b.getBoundingClientRect()).sort((a, b) => a.left - b.left);
		drag = { chip, slots, x: event.clientX, grab: event.clientX - chip.getBoundingClientRect().left, moving: false };
	});
	document.addEventListener('pointermove', (event) => {
		if (!drag || !event.isPrimary) return;
		if (!drag.moving) {
			if (Math.abs(event.clientX - drag.x) < 6) return;
			drag.moving = true;
			drag.chip.setPointerCapture(event.pointerId);
			drag.chip.setAttribute('data-dragging', '');
		}
		place(drag.chip.dataset.pick, Math.max(0, drag.slots.findLastIndex((rect) => event.clientX >= rect.left)));
		drag.chip.style.transform = '';
		drag.chip.style.transform = 'translateX(' + (event.clientX - drag.grab - drag.chip.getBoundingClientRect().left) + 'px)';
	});
	const endDrag = (event) => {
		if (!drag || !event.isPrimary) return;
		const { chip, moving } = drag;
		drag = null;
		if (!moving) return;
		chip.style.transform = '';
		chip.removeAttribute('data-dragging');
		dragged = event.type === 'pointerup';
		saveOrder();
	};
	document.addEventListener('pointerup', endDrag);
	document.addEventListener('pointercancel', endDrag);
	document.addEventListener('keydown', (event) => {
		const chip = event.target.closest('[data-pick]');
		const step = { ArrowLeft: -1, ArrowRight: 1 }[event.key];
		if (!chip || !step || !event.shiftKey || event.metaKey || event.ctrlKey || event.altKey) return;
		event.preventDefault();
		moveLang(chip.dataset.pick, step);
	});
	document.addEventListener('click', (event) => {
		const button = event.target.closest('[data-pick]');
		if (button && !(dragged && event.detail)) toggleLang(button.dataset.pick);
		if (event.target.closest('[data-sidebar-toggle]')) toggleSidebar();
		const toc = byId('sections-nav');
		if (event.target.closest('#sections-nav a') && toc.matches(':popover-open')) toc.hidePopover();
		if (event.target.closest('[data-help]')) byId('help').showModal();
	});
	document.addEventListener('click', async (event) => {
		const line = event.target.closest('.copy-line');
		if (line) {
			await navigator.clipboard.writeText(line.parentElement.textContent);
			line.dataset.copied = '';
			return setTimeout(() => delete line.dataset.copied, 1500);
		}
		const button = event.target.closest('.copy, .copy-part');
		if (!button) return;
		const scope = button.closest('.part') ?? button.closest('.col');
		const code = [...scope.querySelectorAll('.snippet pre')].map((pre) => pre.textContent);
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

<header
	class="sticky top-0 z-10 border-b border-neutral-200 bg-white/90 backdrop-blur dark:border-neutral-800 dark:bg-neutral-950/90"
>
	<nav class="flex gap-1 overflow-x-auto px-4 py-2 text-sm">
		<button
			type="button"
			data-sidebar-toggle
			aria-expanded="true"
			aria-controls="sections-nav"
			aria-keyshortcuts="b"
			aria-label="Sections sidebar"
			title="Sections sidebar (b)"
			class="hidden cursor-pointer items-center rounded-md px-2 text-neutral-400 hover:bg-neutral-100 hover:text-neutral-900 lg:inline-flex dark:text-neutral-500 dark:hover:bg-neutral-800 dark:hover:text-neutral-50"
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
	<button
		type="button"
		popovertarget="sections-nav"
		class="section-now flex w-full cursor-pointer items-center gap-2 border-t border-neutral-200 px-6 py-2 text-left text-sm text-neutral-500 lg:hidden dark:border-neutral-800 dark:text-neutral-400"
	>
		<span data-section-now class="truncate"></span><span aria-hidden="true" class="ml-auto text-xs"
			>▾</span
		>
	</button>
</header>

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
