# For every row whose outputs differ, show what token-level highlighting would mark.
# a) tokens outside the intersection of every column that has output
# b) tokens not shared with the most similar other column
# uv run analysis/output_diff_granularity.py
import pathlib
import re
from collections import Counter

FENCE = re.compile(r'^```(\w+)[^\n]*\n(.*?)^```[ \t]*\n', re.M | re.S)
OUTPUT = re.compile(r'[ \t]+(?:#|//) => (.*)$')
TOKEN = re.compile(r'[A-Za-z0-9_.]+|\S')


def norm(text: str) -> str:
	return re.sub(r'\b(True|False)\b', lambda m: m.group().lower(), text.replace("'", '"'))


def rows(src: str):
	for title, body in re.findall(r'^##+ ([^\n]*)\n(.*?)(?=^##+ |\Z)', src, re.M | re.S):
		row: list[tuple[str, str]] = []
		end = None
		for m in FENCE.finditer(body):
			if end is not None and body[end : m.start()].strip():
				yield title, row
				row = []
			outs = [norm(o.group(1)) for o in map(OUTPUT.search, m.group(2).split('\n')) if o]
			row.append((m.group(1), '\n'.join(outs)))
			end = m.end()
		if row:
			yield title, row


def mark(tokens: list[str], keep: Counter) -> str:
	left = keep.copy()
	out = []
	for t in tokens:
		if left[t] > 0:
			left[t] -= 1
			out.append(t)
		else:
			out.append(f'[{t}]')
	return ' '.join(out)


for path in sorted(pathlib.Path('src/lib/content/langs').glob('*.md')):
	for title, cols in rows(path.read_text()):
		printing = [(lang, out) for lang, out in cols if out]
		if len(printing) < 2 or len({out for _, out in printing}) < 2:
			continue
		toks = [Counter(TOKEN.findall(out)) for _, out in printing]
		common = toks[0].copy()
		for c in toks[1:]:
			common &= c
		print(f'\n{path.stem} / {title}')
		for i, (lang, out) in enumerate(printing):
			others = [toks[k] for k in range(len(printing)) if k != i]
			nearest = max(others, key=lambda c: sum((c & toks[i]).values()))
			print(f'  {lang:7} a: {mark(TOKEN.findall(out), common)}')
			print(f'  {"":7} b: {mark(TOKEN.findall(out), toks[i] & nearest)}')
