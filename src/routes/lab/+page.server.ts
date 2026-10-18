import { langPages } from '../../lib/content/langs';

export function load() {
	const compare = langPages.find((p) => p.slug === 'compare')!;
	const sections = compare.blocks.flatMap((b, i) => {
		const next = compare.blocks[i + 1];
		return b.kind === 'h2' && next?.kind === 'code' && next.steps
			? [{ id: b.id, title: b.title, steps: next.steps }]
			: [];
	});
	return { sections };
}
