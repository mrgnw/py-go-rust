export const OUTPUT = /[ \t]+(?:#|\/\/) => (.*)$/;
const TOKEN = /[A-Za-z0-9_.]+|\S/gu;
const WORD = /^[A-Za-z0-9_.]+$/;
const OPENERS = new Set(['(', '[', '{']);
const CLOSERS = new Set([')', ']', '}']);

// 'Ada' and "Ada", True and true are the same value printed by different languages.
export function sameValue(text: string): string {
	return text.replaceAll("'", '"').replace(/\b(True|False)\b/g, (m) => m.toLowerCase());
}

export function escapeHtml(text: string): string {
	return text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
}

function tally(line: string): Map<string, number> {
	const counts = new Map<string, number>();
	for (const token of line.match(TOKEN) ?? []) {
		const key = sameValue(token);
		counts.set(key, (counts.get(key) ?? 0) + 1);
	}
	return counts;
}

// A token is lacked when some other column has fewer of it on this line. Extra brackets are the
// outermost ones (`Some(` around a shared `(0, 1)`), so openers are matched from the right.
function lackedTokens(tokens: string[], keep: Map<string, number>): boolean[] {
	const lacked = tokens.map(() => false);
	const take = (i: number) => {
		const key = sameValue(tokens[i]);
		const left = keep.get(key) ?? 0;
		keep.set(key, left - 1);
		lacked[i] = left <= 0;
	};
	tokens.forEach((token, i) => OPENERS.has(token) || take(i));
	for (let i = tokens.length - 1; i >= 0; i--) if (OPENERS.has(tokens[i])) take(i);
	return lacked;
}

// Words take the color when lacked. Punctuation takes it only next to a lacked word in the same
// unspaced run (Rust's `Some(4)` yes, Python's `[1, 2]` commas no). A bracket pair is then colored
// as a pair, so `Some((0, 1))` colors both outer parens even though `))` has no word beside it.
function paintFlags(tokens: { text: string; run: number }[], lacked: boolean[]): boolean[] {
	const loudRuns = new Set(tokens.filter((t, i) => lacked[i] && WORD.test(t.text)).map((t) => t.run));
	const painted = tokens.map((t, i) => lacked[i] && (WORD.test(t.text) || loudRuns.has(t.run)));
	const open: number[] = [];
	tokens.forEach((t, i) => {
		if (OPENERS.has(t.text)) open.push(i);
		else if (CLOSERS.has(t.text) && open.length) {
			const opener = open.pop()!;
			painted[opener] = painted[i] = painted[opener] || painted[i];
		}
	});
	return painted;
}

export function diffLine(line: string, others: string[]): string {
	const theirs = others.map(tally);
	const keep = new Map(
		[...tally(line).keys()].map((key) => [key, Math.min(...theirs.map((c) => c.get(key) ?? 0))])
	);
	const runs = line.split(/(\s+)/);
	const tokens = runs.flatMap((run, r) =>
		r % 2 ? [] : (run.match(TOKEN) ?? []).map((text) => ({ text, run: r }))
	);
	const lacked = lackedTokens(
		tokens.map((t) => t.text),
		keep
	);
	const painted = paintFlags(tokens, lacked);
	const html = tokens.map((t, i) =>
		painted[i] ? `<span class="diff">${escapeHtml(t.text)}</span>` : escapeHtml(t.text)
	);
	return runs
		.map((run, r) => (r % 2 ? run : html.filter((_, i) => tokens[i].run === r).join('')))
		.join('');
}
