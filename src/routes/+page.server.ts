import { langPages } from '../lib/content/langs';

export const prerender = true;
export const csr = false;

export function load() {
	return { pages: langPages };
}
