import { langPages } from '../lib/content/langs';

export const prerender = true;
export const csr = false;

export function load() {
	const nav = langPages.map(({ slug, title }, i) => ({ title, href: i === 0 ? '/' : `/${slug}` }));
	const sections = langPages.flatMap(({ title: page, blocks }, i) => {
		let group: string | undefined;
		return blocks.flatMap((block) => {
			if (block.kind === 'group') group = block.title;
			if (block.kind !== 'group' && block.kind !== 'h2') return [];
			return [{ page, group, title: block.title, href: `${nav[i].href}#${block.id}` }];
		});
	});
	return { nav, sections };
}
