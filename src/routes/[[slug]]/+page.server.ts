import { error } from '@sveltejs/kit';
import { langPages } from '../../lib/content/langs';

const [home] = langPages;

export function entries() {
	return langPages.map(({ slug }) => ({ slug: slug === home.slug ? '' : slug }));
}

export function load({ params }) {
	const page = langPages.find((p) => p.slug === (params.slug || home.slug));
	if (!page) error(404, 'Not found');
	return { page };
}
