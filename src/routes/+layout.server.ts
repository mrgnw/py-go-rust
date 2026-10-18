import { langPages } from '../lib/content/langs';

export const prerender = true;
export const csr = false;

export function load() {
	return {
		nav: langPages.map(({ slug, title }, i) => ({ title, href: i === 0 ? '/' : `/${slug}` }))
	};
}
