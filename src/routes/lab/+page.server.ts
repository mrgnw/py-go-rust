import { langPages } from '../../lib/content/langs';

export function load() {
	const compare = langPages.find((p) => p.slug === 'compare')!;
	const sections = compare.blocks.flatMap((b, i) => {
		const next = compare.blocks[i + 1];
		return b.kind === 'h2' && next?.kind === 'code' && next.cols[0].parts.length > 1
			? [{ id: b.id, title: b.title, cols: next.cols }]
			: [];
	});
	return { sections };
}
