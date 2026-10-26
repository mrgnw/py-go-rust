import { marked, type Token, type Tokens } from 'marked';
import { createHighlighter, type DecorationItem, type ShikiTransformer } from 'shiki';
import { diffLine, escapeHtml, OUTPUT, OUTPUT_ONLY } from './diff';
import captured from './vars.json';

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
	| { kind: 'code'; cols: Col[]; linked: boolean };

// A part is the same idea in every column of a row, found at the same path (`1`, `1.0`).
// A leaf has html; a group has parts and no lines of its own. pad: blank lines the author left above
// and below a leaf, kept as spacing so the code reads as written. output: the leaf's `=>` lines.
export interface Part {
	path: string;
	label?: string;
	html: string;
	output?: string;
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

const sectionFiles = import.meta.glob('./langs/*/*.md', {
	query: '?raw',
	import: 'default',
	eager: true
}) as Record<string, string>;
const linked = new Set<string>();

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

// analysis/capture_vars.py: per section and language, each fence's occurrences of locals as [row, UTF-16
// column, name, value at that line, 1 if the line sets it]. Keyed by an FNV-1a hash of all of that language's
// fences in the section, so editing any of them leaves the whole program uncaptured until it is recaptured.
type Occurrence = [row: number, col: number, name: string, value: string, sets: number];
const vars = captured as unknown as Record<string, Occurrence[][]>;
const uncaptured: string[] = [];

function fenceKey(text: string): string {
	let h = 0x811c9dc5;
	for (const byte of new TextEncoder().encode(text)) h = Math.imul(h ^ byte, 0x01000193) >>> 0;
	return h.toString(16).padStart(8, '0');
}

// Each python/rust/go fence's captured occurrences, found by its section's key. A section starts at every
// `##` or `###`, as in analysis/run_snippets.py.
function fenceVars(tokens: Token[]): Map<Token, Occurrence[] | undefined> {
	const found = new Map<Token, Occurrence[] | undefined>();
	let section = new Map<string, Tokens.Code[]>();
	const close = () => {
		for (const fences of section.values()) {
			const saved = vars[fenceKey(fences.map((f) => f.text + '\n').join(''))];
			fences.forEach((fence, i) => found.set(fence, saved?.[i]));
		}
		section = new Map();
	};
	for (const token of tokens) {
		if (token.type === 'heading' && (token.depth === 2 || token.depth === 3)) close();
		const lang = token.type === 'code' ? (token.lang ?? '').trim().split(/\s+/)[0] : '';
		if (PICKABLE.includes(lang))
			section.set(lang, [...(section.get(lang) ?? []), token as Tokens.Code]);
	}
	close();
	return found;
}

// Columns pair a name by its key, so `max_retries` and `maxRetries` light together.
const varKey = (name: string) => name.toLowerCase().replaceAll('_', '');

interface Marks {
	decorations: DecorationItem[];
	sets: Map<number, string[]>;
}

// Each occurrence on a kept line becomes a `data-var` span carrying its value; a line that sets names lists
// their keys in `data-sets`.
function varMarks(lines: Line[], occurrences: Occurrence[]): Marks {
	const index = new Map(lines.map((line, i) => [line.row, i]));
	const marks: Marks = { decorations: [], sets: new Map() };
	for (const [row, col, name, value, sets] of occurrences) {
		const line = index.get(row);
		if (line === undefined || lines[line].text.slice(col, col + name.length) !== name) continue;
		const key = varKey(name);
		marks.decorations.push({
			start: { line, character: col },
			end: { line, character: col + name.length },
			properties: value ? { 'data-var': key, 'data-val': value } : { 'data-var': key }
		});
		if (sets && value) marks.sets.set(line, [...(marks.sets.get(line) ?? []), key]);
	}
	return marks;
}

const setsAttribute = (sets: Map<number, string[]>): ShikiTransformer => ({
	line(node, line) {
		const keys = sets.get(line - 1);
		if (keys) node.properties['data-sets'] = [...new Set(keys)].join(' ');
	}
});

function toHtml(code: string, lang: string, marks?: Marks): string {
	return highlighter.codeToHtml(code, {
		lang,
		themes: { light: 'github-light', dark: 'github-dark' },
		defaultColor: 'light-dark()',
		decorations: marks?.decorations,
		transformers: lang === 'sh' ? [lineCopy] : marks ? [setsAttribute(marks.sets)] : []
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

// row: the line's index in its fence, which is how captured variables find it.
interface Line {
	text: string;
	row: number;
}

const markerDepth = (line: Line) => (line.text.match(MARKER)?.[1].length ?? 1) - 1;
const blank = (line: Line) => !line.text.trim();

// Split at markers of exactly `depth`; deeper markers stay with their lines for the next level.
// Blank text before the first marker joins the first part instead of becoming one.
function chunks(lines: Line[], depth: number): { label?: string; lines: Line[] }[] {
	const out: { label?: string; lines: Line[] }[] = [{ lines: [] }];
	for (const line of lines) {
		if (markerDepth(line) === depth)
			out.push({ label: line.text.match(MARKER)?.[2]?.trim() || undefined, lines: [] });
		else out[out.length - 1].lines.push(line);
	}
	if (out.length > 1 && out[0].lines.every(blank)) out[1].lines.unshift(...out.shift()!.lines);
	return out;
}

function leaf(
	raw: Line[],
	lang: string,
	occurrences?: Occurrence[]
): { html: string; output?: string; pad: [number, number] } {
	const outputs = raw.flatMap((line) => line.text.match(OUTPUT)?.[1] ?? []);
	const lines = raw
		.filter((line) => !OUTPUT_ONLY.test(line.text))
		.map((line) => ({ ...line, text: line.text.replace(OUTPUT, '') }));
	const first = lines.findIndex((line) => !blank(line));
	if (first < 0) return { html: '', pad: [lines.length, 0] };
	const last = lines.findLastIndex((line) => !blank(line));
	const kept = lines.slice(first, last + 1);
	const code = kept.map((line) => line.text).join('\n');
	return {
		html: toHtml(code, lang, occurrences && varMarks(kept, occurrences)),
		output: outputs.length ? outputs.join('\n') : undefined,
		pad: [first, lines.length - 1 - last]
	};
}

// Marker lines vanish; every other line, blank ones included, lands in exactly one leaf.
function toParts(
	lines: Line[],
	lang: string,
	occurrences?: Occurrence[],
	depth = 1,
	prefix = ''
): Part[] {
	return chunks(lines, depth).map((chunk, k) => {
		const path = prefix + k;
		if (!chunk.lines.some((line) => MARKER.test(line.text)))
			return { path, label: chunk.label, parts: [], ...leaf(chunk.lines, lang, occurrences) };
		const parts = toParts(chunk.lines, lang, occurrences, depth + 1, `${path}.`);
		return { path, label: chunk.label, html: '', pad: [0, 0], parts };
	});
}

function highlight(code: string, info: string, section: string, occurrences?: Occurrence[]): Col {
	const [lang, ...rest] = info.trim().split(/\s+/);
	if (!LANGS.includes(lang as Lang)) throw new Error(`langs: unsupported fence language "${info}"`);
	const label = rest.filter((word) => !word.startsWith('!')).join(' ') || LABELS[lang as Lang];
	const lines = code.split('\n').map((text, row) => ({ text, row }));
	const depths = lines.map(markerDepth).filter((d) => d > 0);
	if (depths.some((d) => d > MAX_DEPTH))
		throw new Error(`langs: ${section}: ${label} has a marker deeper than ${MAX_DEPTH} levels`);
	if (depths[0] > 1)
		throw new Error(`langs: ${section}: ${label} has a depth-2 marker without a depth-1 parent`);
	if (PICKABLE.includes(lang) && !occurrences) uncaptured.push(`${section} (${lang})`);
	return { label, lang: pickLang(lang, label), parts: toParts(lines, lang, occurrences) };
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

type Printed = { path: string; lines: string[] };

// Every leaf that prints, in order, with its `=>` lines.
function printed(parts: Part[]): Printed[] {
	return parts.flatMap((part) => {
		if (part.parts.length) return printed(part.parts);
		return part.output === undefined ? [] : [{ path: part.path, lines: part.output.split('\n') }];
	});
}

// Output line k of a part is diffed against line k of the same part in the other columns, so a part
// that prints more lines in one language doesn't shift the comparison for the parts after it.
// In a linked row each line carries its part's path, so hovering either side lights the other.
interface Fence {
	text: string;
	info: string;
	occurrences?: Occurrence[];
}

function codeRow(fences: Fence[], section: string): Block {
	const cols: Col[] = fences.map((f) => highlight(f.text, f.info, section, f.occurrences));
	checkShape(
		section,
		cols,
		cols.map((c) => c.parts)
	);
	const linked = cols[0].parts.length > 1 || cols[0].parts[0].parts.length > 0;
	const prints = cols.map((c) => printed(c.parts));
	const linesOf = (col: Printed[], path: string) => col.find((p) => p.path === path)?.lines ?? [];
	const outputHtml = (i: number) => {
		const others = prints.filter((col, k) => k !== i && col.length);
		const body = prints[i].flatMap(({ path, lines }) =>
			lines.map((line, k) => {
				const html = others.length
					? diffLine(
							line,
							others.map((col) => linesOf(col, path)[k] ?? '')
						)
					: escapeHtml(line);
				return linked ? `<span data-part="${path}">${html}</span>` : `<span>${html}</span>`;
			})
		);
		return `<pre class="shiki"><code>${body.join('')}</code></pre>`;
	};
	for (const [i, col] of cols.entries()) if (prints[i].length) col.output = outputHtml(i);
	return { kind: 'code', cols, linked };
}

// A heading that is only a link to a `.md` file (`### [Sets](compare/sets.md)`) takes its body from
// that file: the page keeps the title and the order, the file holds the section.
function expand(tokens: Token[], slug: string): Token[] {
	return tokens.flatMap((token) => {
		const link =
			token.type === 'heading' && token.tokens?.length === 1 ? token.tokens[0] : undefined;
		if (link?.type !== 'link' || !link.href.endsWith('.md')) return [token];
		const path = `./langs/${link.href}`;
		if (!(path in sectionFiles)) throw new Error(`langs: ${slug}: no section file ${link.href}`);
		if (linked.has(path)) throw new Error(`langs: ${slug}: ${link.href} is linked twice`);
		linked.add(path);
		const body = marked.lexer(sectionFiles[path]) as Token[];
		const heading = body.find((t): t is Tokens.Heading => t.type === 'heading');
		if (heading)
			throw new Error(`langs: ${link.href}: section files have no headings ("${heading.text}")`);
		return [{ ...token, text: link.text }, ...body];
	});
}

function toBlocks(md: string, slug: string): Block[] {
	const blocks: Block[] = [];
	let fences: Fence[] = [];
	let section = slug;
	const flush = () => {
		if (fences.length) blocks.push(codeRow(fences, section));
		fences = [];
	};
	const tokens = expand(marked.lexer(md) as Token[], slug);
	const captured = fenceVars(tokens);
	// With `###` present, `##` headings are groups (component-party style) and `###` are the sections.
	const grouped = tokens.some((t) => t.type === 'heading' && t.depth === 3);
	const sectionDepth = grouped ? 3 : 2;
	for (const token of tokens) {
		if (token.type === 'space') continue;
		if (token.type === 'code') {
			fences.push({ text: token.text, info: token.lang ?? '', occurrences: captured.get(token) });
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

if (uncaptured.length)
	console.warn(
		`langs: no captured variables for ${new Set(uncaptured).size} section programs, run \`uv run analysis/capture_vars.py\`:\n  ${[...new Set(uncaptured)].join('\n  ')}`
	);

const orphans = Object.keys(sectionFiles).filter((path) => !linked.has(path));
if (orphans.length) throw new Error(`langs: no page links ${orphans.join(', ')}`);
