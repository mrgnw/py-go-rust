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
	| { kind: 'code'; cols: { label: string; html: string }[] };

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

function highlight(code: string, info: string): { label: string; html: string } {
	const [lang, ...rest] = info.trim().split(/\s+/);
	if (!LANGS.includes(lang as Lang)) throw new Error(`langs: unsupported fence language "${info}"`);
	const html = highlighter.codeToHtml(code, {
		lang,
		themes: { light: 'github-light', dark: 'github-dark' },
		defaultColor: 'light-dark()'
	});
	return { label: rest.join(' ') || LABELS[lang as Lang], html };
}

function toBlocks(md: string, slug: string): Block[] {
	const blocks: Block[] = [];
	let row: Block | null = null;
	for (const token of marked.lexer(md) as Token[]) {
		if (token.type === 'space') continue;
		if (token.type === 'code') {
			if (row?.kind !== 'code') {
				row = { kind: 'code', cols: [] };
				blocks.push(row);
			}
			row.cols.push(highlight(token.text, token.lang ?? ''));
			continue;
		}
		row = null;
		if (token.type === 'heading' && token.depth === 1) {
			blocks.push({ kind: 'h1', title: token.text });
		} else if (token.type === 'heading' && token.depth === 2) {
			blocks.push({ kind: 'h2', id: `${slug}-${slugify(token.text)}`, title: token.text });
		} else {
			blocks.push({ kind: 'html', html: marked.parser([token]) });
		}
	}
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
