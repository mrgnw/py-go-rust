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
			output?: { label: string; html: string };
			cols: { label: string; html: string }[];
	  };

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

function highlight(code: string, info: string, copy = true): { label: string; html: string } {
	const [lang, ...rest] = info.trim().split(/\s+/);
	if (!LANGS.includes(lang as Lang)) throw new Error(`langs: unsupported fence language "${info}"`);
	const html = highlighter.codeToHtml(code, {
		lang,
		themes: { light: 'github-light', dark: 'github-dark' },
		defaultColor: 'light-dark()'
	});
	const button = copy ? '<button type="button" class="copy" aria-label="Copy">Copy</button>' : '';
	return {
		label: rest.join(' ') || LABELS[lang as Lang],
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
	if (!shared) return { kind: 'code', cols: fences.map((f) => highlight(f.text, f.info)) };
	return {
		kind: 'code',
		output: highlight(outputs[0].join('\n'), 'text Output', false),
		cols: fences.map((f) =>
			highlight(
				f.text
					.split('\n')
					.map((line) => line.replace(OUTPUT, ''))
					.join('\n'),
				f.info
			)
		)
	};
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
