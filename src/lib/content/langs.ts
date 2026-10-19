import { marked, type Token } from 'marked';
import { createHighlighter, type ShikiTransformer } from 'shiki';

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

// pad: blank lines the author left above and below the part, kept as spacing so the code reads as written
export interface Part {
	label?: string;
	html: string;
	pad: [number, number];
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

// SPEC.md parts: `# --` / `// --` plus an optional label. Depth (`---`) is not used yet; parts are flat.
const MARKER = /^[ \t]*(?:#|\/\/) -{2,3}(?: (.*))?$/;
const MAX_PARTS = 8;

// Marker lines vanish; every other line stays. Text before the first marker is a part only when it has code.
function splitParts(code: string): { label?: string; code: string; pad: [number, number] }[] {
	const parts: { label?: string; lines: string[] }[] = [{ lines: [] }];
	for (const line of code.split('\n')) {
		const marker = line.match(MARKER);
		if (marker) parts.push({ label: marker[1]?.trim() || undefined, lines: [] });
		else parts[parts.length - 1].lines.push(line);
	}
	const blank = (line: string) => !line.trim();
	const leading = parts.length === 1 || !parts[0].lines.every(blank);
	return (leading ? parts : parts.slice(1)).map((p) => {
		const first = p.lines.findIndex((line) => !blank(line));
		if (first < 0) return { label: p.label, code: '', pad: [p.lines.length, 0] };
		const last = p.lines.findLastIndex((line) => !blank(line));
		return {
			label: p.label,
			code: p.lines.slice(first, last + 1).join('\n'),
			pad: [first, p.lines.length - 1 - last]
		};
	});
}

function highlight(code: string, info: string): Col {
	const [lang, ...rest] = info.trim().split(/\s+/);
	if (!LANGS.includes(lang as Lang)) throw new Error(`langs: unsupported fence language "${info}"`);
	const label = rest.join(' ') || LABELS[lang as Lang];
	return {
		label,
		lang: pickLang(lang, label),
		parts: splitParts(code).map((p) => ({
			label: p.label,
			html: p.code ? toHtml(p.code, lang) : '',
			pad: p.pad
		}))
	};
}

const OUTPUT = /[ \t]+(?:#|\/\/) => (.*)$/;
const TOKEN = /[A-Za-z0-9_.]+|\S/gu;
const WORD = /^[A-Za-z0-9_.]+$/;

// 'Ada' and "Ada", True and true are the same value printed by different languages.
function sameValue(text: string): string {
	return text.replaceAll("'", '"').replace(/\b(True|False)\b/g, (m) => m.toLowerCase());
}

function escapeHtml(text: string): string {
	return text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
}

function tally(line: string): Map<string, number> {
	const counts = new Map<string, number>();
	for (const token of line.match(TOKEN) ?? []) {
		const key = sameValue(token);
		counts.set(key, (counts.get(key) ?? 0) + 1);
	}
	return counts;
}

// A token is marked when some other column lacks it on the same line. Punctuation is marked only
// next to a marked word in the same unspaced run: Rust's `Some(4)` yes, Python's `[1, 2]` commas no.
function diffLine(line: string, others: string[]): string {
	const theirs = others.map(tally);
	const keep = new Map(
		[...tally(line).keys()].map((key) => [key, Math.min(...theirs.map((c) => c.get(key) ?? 0))])
	);
	const markRun = (run: string) => {
		const tokens = run.match(TOKEN) ?? [];
		const unmatched = tokens.map((token) => {
			const key = sameValue(token);
			const left = keep.get(key) ?? 0;
			keep.set(key, left - 1);
			return left <= 0;
		});
		const loud = tokens.some((token, i) => unmatched[i] && WORD.test(token));
		return tokens
			.map((token, i) =>
				loud && unmatched[i] ? `<span class="diff">${escapeHtml(token)}</span>` : escapeHtml(token)
			)
			.join('');
	};
	return line
		.split(/(\s+)/)
		.map((run, i) => (i % 2 ? run : markRun(run)))
		.join('');
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
			? { ...highlight(strip(f.text), f.info), output: outputHtml(i) }
			: highlight(f.text, f.info)
	);
	const counts = cols.map((c) => c.parts.length);
	if (counts.some((n) => n !== counts[0]))
		throw new Error(
			`langs: ${section}: ${cols.map((c) => `${c.label} has ${c.parts.length} parts`).join(', ')}`
		);
	if (counts[0] > MAX_PARTS) throw new Error(`langs: ${section}: more than ${MAX_PARTS} parts`);
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
