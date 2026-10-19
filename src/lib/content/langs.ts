import { marked, type Token } from 'marked';
import { createHighlighter, type ShikiTransformer } from 'shiki';
import { diffLine, escapeHtml, OUTPUT, sameValue } from './diff';

const LANGS = ['python', 'rust', 'go', 'sh', 'toml', 'text'] as const;
type Lang = (typeof LANGS)[number];
const LABELS: Record<Lang, string> = {
	python: 'Python',
	rust: 'Rust',
	go: 'Go',
	sh: 'Shell',
	toml: 'TOML',
	text: ''
};

export type Block =
	| { kind: 'h1'; title: string }
	| { kind: 'group'; id: string; title: string }
	| { kind: 'h2'; id: string; title: string }
	| { kind: 'html'; html: string }
	| {
			kind: 'code';
			cols: Col[];
			steps?: Step[];
	  };

// A part is the same idea in every column of a row, found at the same path (`1`, `1.0`).
// A leaf has html; a group has parts and no lines of its own. pad: blank lines the author left above
// and below a leaf, kept as spacing so the code reads as written.
export interface Part {
	path: string;
	label?: string;
	html: string;
	pad: [number, number];
	parts: Part[];
}

// output: each column carries its own, with `<span class="diff">` around tokens another column lacks
export interface Col {
	label: string;
	parts: Part[];
	lang?: string;
	output?: string;
}

// lab: the same row pivoted, one step per output with each language's line(s) stacked
export interface Step {
	output?: string;
	multi: boolean;
	lines: { lang: string; html: string }[];
}

export interface LangPage {
	slug: string;
	title: string;
	blocks: Block[];
}

const sources = import.meta.glob('./langs/*.md', {
	query: '?raw',
	import: 'default',
	eager: true
}) as Record<string, string>;

const highlighter = await createHighlighter({
	langs: [...LANGS],
	themes: ['github-light', 'github-dark']
});

function slugify(text: string): string {
	return text
		.toLowerCase()
		.replace(/[^a-z0-9]+/g, '-')
		.replace(/^-|-$/g, '');
}

const lineCopy: ShikiTransformer = {
	line(line) {
		if (!line.children.length) return;
		line.children.push({
			type: 'element',
			tagName: 'button',
			properties: { type: 'button', class: 'copy-line', ariaLabel: 'Copy line' },
			children: []
		});
	}
};

function toHtml(code: string, lang: string): string {
	return highlighter.codeToHtml(code, {
		lang,
		themes: { light: 'github-light', dark: 'github-dark' },
		defaultColor: 'light-dark()',
		transformers: lang === 'sh' ? [lineCopy] : []
	});
}

const PICKABLE = ['python', 'rust', 'go'];

// The language a column belongs to for the picker: the fence lang, or a label naming one (`sh Rust`).
function pickLang(lang: string, label: string): string | undefined {
	const byLabel = PICKABLE.find((l) => LABELS[l as Lang] === label);
	return byLabel ?? (PICKABLE.includes(lang) ? lang : undefined);
}

// SPEC.md parts: `# --` / `// --` plus an optional label. Two dashes are depth 1, three depth 2.
const MARKER = /^[ \t]*(?:#|\/\/) (-{2,})(?: (.*))?$/;
const MAX_DEPTH = 2;
const MAX_PARTS = 8;

const markerDepth = (line: string) => (line.match(MARKER)?.[1].length ?? 1) - 1;
const blank = (line: string) => !line.trim();

// Split at markers of exactly `depth`; deeper markers stay with their lines for the next level.
// Blank text before the first marker joins the first part instead of becoming one.
function chunks(lines: string[], depth: number): { label?: string; lines: string[] }[] {
	const out: { label?: string; lines: string[] }[] = [{ lines: [] }];
	for (const line of lines) {
		if (markerDepth(line) === depth)
			out.push({ label: line.match(MARKER)?.[2]?.trim() || undefined, lines: [] });
		else out[out.length - 1].lines.push(line);
	}
	if (out.length > 1 && out[0].lines.every(blank)) out[1].lines.unshift(...out.shift()!.lines);
	return out;
}

function leaf(lines: string[], lang: string): { html: string; pad: [number, number] } {
	const first = lines.findIndex((line) => !blank(line));
	if (first < 0) return { html: '', pad: [lines.length, 0] };
	const last = lines.findLastIndex((line) => !blank(line));
	return {
		html: toHtml(lines.slice(first, last + 1).join('\n'), lang),
		pad: [first, lines.length - 1 - last]
	};
}

// Marker lines vanish; every other line, blank ones included, lands in exactly one leaf.
function toParts(lines: string[], lang: string, depth = 1, prefix = ''): Part[] {
	return chunks(lines, depth).map((chunk, k) => {
		const path = prefix + k;
		if (!chunk.lines.some((line) => MARKER.test(line)))
			return { path, label: chunk.label, parts: [], ...leaf(chunk.lines, lang) };
		const parts = toParts(chunk.lines, lang, depth + 1, `${path}.`);
		return { path, label: chunk.label, html: '', pad: [0, 0], parts };
	});
}

function highlight(code: string, info: string, section: string): Col {
	const [lang, ...rest] = info.trim().split(/\s+/);
	if (!LANGS.includes(lang as Lang)) throw new Error(`langs: unsupported fence language "${info}"`);
	const label = rest.join(' ') || LABELS[lang as Lang];
	const lines = code.split('\n');
	const depths = lines.map(markerDepth).filter((d) => d > 0);
	if (depths.some((d) => d > MAX_DEPTH))
		throw new Error(`langs: ${section}: ${label} has a marker deeper than ${MAX_DEPTH} levels`);
	if (depths[0] > 1)
		throw new Error(`langs: ${section}: ${label} has a depth-2 marker without a depth-1 parent`);
	return { label, lang: pickLang(lang, label), parts: toParts(lines, lang) };
}

// Every column needs the same tree: the same number of parts under each path, at most MAX_PARTS.
function checkShape(section: string, cols: Col[], lists: Part[][], under = ''): void {
	const counts = lists.map((parts) => parts.length);
	const where = under ? ` under part ${under}` : '';
	if (counts.some((n) => n !== counts[0]))
		throw new Error(
			`langs: ${section}:${where} ${cols.map((c, i) => `${c.label} has ${counts[i]} parts`).join(', ')}`
		);
	if (counts[0] > MAX_PARTS)
		throw new Error(`langs: ${section}:${where} more than ${MAX_PARTS} parts`);
	for (const [k, part] of lists[0].entries())
		checkShape(
			section,
			cols,
			lists.map((parts) => parts[k].parts),
			part.path
		);
}

// When every column prints the same thing, show it once in a leading Output column.
function codeRow(fences: { text: string; info: string }[], section: string): Block {
	const outputs = fences.map((f) =>
		f.text.split('\n').flatMap((line) => line.match(OUTPUT)?.[1] ?? [])
	);
	const values = outputs.map((lines) => sameValue(lines.join('\n')));
	const shared = fences.length > 1 && outputs[0].length > 0 && values.every((v) => v === values[0]);
	const strip = (text: string) =>
		text
			.split('\n')
			.map((line) => line.replace(OUTPUT, ''))
			.join('\n');
	const outputHtml = (i: number) => {
		const others = outputs.filter((lines, k) => k !== i && lines.length);
		const body = outputs[i].map((line, k) =>
			others.length
				? diffLine(
						line,
						others.map((lines) => lines[k] ?? '')
					)
				: escapeHtml(line)
		);
		return `<pre class="shiki"><code>${body.join('\n')}</code></pre>`;
	};
	const cols = fences.map((f, i) =>
		outputs[i].length
			? { ...highlight(strip(f.text), f.info, section), output: outputHtml(i) }
			: highlight(f.text, f.info, section)
	);
	checkShape(
		section,
		cols,
		cols.map((c) => c.parts)
	);
	return shared ? { kind: 'code', cols, steps: pivot(fences, outputs[0]) } : { kind: 'code', cols };
}

// Go's `func main() {` ... `}` wrapper is scaffolding; drop it so its body pivots like the rest.
function unwrapMain(text: string, lang: string): string {
	const lines = text.trimEnd().split('\n');
	const start = lines.indexOf('func main() {');
	if (lang !== 'go' || start < 0 || lines.at(-1) !== '}') return text;
	const body = lines.slice(start + 1, -1).map((line) => line.replace(/^\t/, ''));
	return [...lines.slice(0, start), ...body].join('\n');
}

// Split each fence at its output lines: lines leading up to output k form an
// unlabelled step, the line that prints output k forms a step labelled with it.
function pivot(fences: { text: string; info: string }[], outputs: string[]): Step[] {
	const chunks = fences.map((f) => {
		const lang = f.info.trim().split(/\s+/)[0];
		const pre: string[][] = outputs.map(() => []);
		const out: string[] = [];
		let pending: string[] = [];
		for (const line of unwrapMain(f.text, lang).split('\n')) {
			if (MARKER.test(line)) continue;
			if (OUTPUT.test(line)) {
				pre[out.length] = pending;
				out.push(line.replace(OUTPUT, '').trim());
				pending = [];
			} else if (line.trim() || pending.length) pending.push(line);
		}
		return { lang, pre, out, post: pending };
	});
	const step = (output: string | undefined, pick: (c: (typeof chunks)[number]) => string[]) => {
		const lines = chunks.flatMap((c) => {
			const code = pick(c).join('\n').trimEnd();
			return code ? [{ lang: c.lang, html: toHtml(code, c.lang) }] : [];
		});
		const multi = chunks.some((c) => pick(c).join('\n').trim().includes('\n'));
		return lines.length ? [{ output, multi, lines }] : [];
	};
	return [
		...outputs.flatMap((output, k) => [
			...step(undefined, (c) => c.pre[k]),
			...step(output, (c) => [c.out[k]])
		]),
		...step(undefined, (c) => c.post)
	];
}

function toBlocks(md: string, slug: string): Block[] {
	const blocks: Block[] = [];
	let fences: { text: string; info: string }[] = [];
	let section = slug;
	const flush = () => {
		if (fences.length) blocks.push(codeRow(fences, section));
		fences = [];
	};
	const tokens = marked.lexer(md) as Token[];
	// With `###` present, `##` headings are groups (component-party style) and `###` are the sections.
	const grouped = tokens.some((t) => t.type === 'heading' && t.depth === 3);
	const sectionDepth = grouped ? 3 : 2;
	for (const token of tokens) {
		if (token.type === 'space') continue;
		if (token.type === 'code') {
			fences.push({ text: token.text, info: token.lang ?? '' });
			continue;
		}
		flush();
		if (token.type === 'heading' && token.depth === 1) {
			blocks.push({ kind: 'h1', title: token.text });
		} else if (token.type === 'heading' && token.depth === sectionDepth) {
			section = `${slug}: ${token.text}`;
			blocks.push({ kind: 'h2', id: `${slug}-${slugify(token.text)}`, title: token.text });
		} else if (token.type === 'heading' && grouped && token.depth === 2) {
			blocks.push({ kind: 'group', id: `${slug}-${slugify(token.text)}`, title: token.text });
		} else if (token.type === 'heading') {
			throw new Error(`langs: ${slug}: unexpected heading depth ${token.depth} "${token.text}"`);
		} else {
			blocks.push({ kind: 'html', html: marked.parser([token]) });
		}
	}
	flush();
	return blocks;
}

export const langPages: LangPage[] = Object.keys(sources)
	.sort()
	.map((path) => {
		const slug = path.replace(/^\.\/langs\/\d+-|\.md$/g, '');
		const blocks = toBlocks(sources[path], slug);
		const h1 = blocks.find((b) => b.kind === 'h1');
		if (!h1 || h1.kind !== 'h1') throw new Error(`langs: ${path} has no # title`);
		return { slug, title: h1.title, blocks };
	});
