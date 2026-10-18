import { marked, type Token } from 'marked';
import { createHighlighter } from 'shiki';

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
	| { kind: 'h2'; id: string; title: string }
	| { kind: 'html'; html: string }
	| {
			kind: 'code';
			output?: Col;
			cols: Col[];
			steps?: Step[];
	  };

// output: when every column prints the same, the row carries it; otherwise each column carries its own
export interface Col {
	label: string;
	html: string;
	lang?: string;
	output?: Col;
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

function toHtml(code: string, lang: string): string {
	return highlighter.codeToHtml(code, {
		lang,
		themes: { light: 'github-light', dark: 'github-dark' },
		defaultColor: 'light-dark()'
	});
}

const PICKABLE = ['python', 'rust', 'go'];

// The language a column belongs to for the picker: the fence lang, or a label naming one (`sh Rust`).
function pickLang(lang: string, label: string): string | undefined {
	const byLabel = PICKABLE.find((l) => LABELS[l as Lang] === label);
	return byLabel ?? (PICKABLE.includes(lang) ? lang : undefined);
}

function highlight(code: string, info: string, copy = true): Col {
	const [lang, ...rest] = info.trim().split(/\s+/);
	if (!LANGS.includes(lang as Lang)) throw new Error(`langs: unsupported fence language "${info}"`);
	const html = toHtml(code, lang);
	const button = copy ? '<button type="button" class="copy" aria-label="Copy">Copy</button>' : '';
	const label = rest.join(' ') || LABELS[lang as Lang];
	return {
		label,
		lang: pickLang(lang, label),
		html: `<div class="snippet">${html}${button}</div>`
	};
}

const OUTPUT = /[ \t]+(?:#|\/\/) => (.*)$/;

// When every column prints the same thing, show it once in a leading Output column.
function codeRow(fences: { text: string; info: string }[]): Block {
	const outputs = fences.map((f) =>
		f.text.split('\n').flatMap((line) => line.match(OUTPUT)?.[1] ?? [])
	);
	const shared =
		fences.length > 1 &&
		outputs[0].length > 0 &&
		outputs.every((o) => o.join('\n') === outputs[0].join('\n'));
	const strip = (text: string) =>
		text
			.split('\n')
			.map((line) => line.replace(OUTPUT, ''))
			.join('\n');
	const outputCol = (lines: string[]) => highlight(lines.join('\n'), 'text Output', false);
	if (shared) {
		return {
			kind: 'code',
			output: outputCol(outputs[0]),
			steps: pivot(fences, outputs[0]),
			cols: fences.map((f) => highlight(strip(f.text), f.info))
		};
	}
	return {
		kind: 'code',
		cols: fences.map((f, i) =>
			outputs[i].length
				? { ...highlight(strip(f.text), f.info), output: outputCol(outputs[i]) }
				: highlight(f.text, f.info)
		)
	};
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
	const flush = () => {
		if (fences.length) blocks.push(codeRow(fences));
		fences = [];
	};
	for (const token of marked.lexer(md) as Token[]) {
		if (token.type === 'space') continue;
		if (token.type === 'code') {
			fences.push({ text: token.text, info: token.lang ?? '' });
			continue;
		}
		flush();
		if (token.type === 'heading' && token.depth === 1) {
			blocks.push({ kind: 'h1', title: token.text });
		} else if (token.type === 'heading' && token.depth === 2) {
			blocks.push({ kind: 'h2', id: `${slug}-${slugify(token.text)}`, title: token.text });
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
