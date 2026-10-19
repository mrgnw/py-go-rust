# Where do `=>` outputs sit inside fences? Counts per shape, with examples.
# uv run analysis/output_positions.py
import pathlib
import re
from collections import Counter

FENCE = re.compile(r'^```(\w+)[^\n]*\n(.*?)^```', re.M | re.S)
OUTPUT = re.compile(r'[ \t]+(?:#|//) => (.*)$')

shapes = Counter()
examples: dict[str, list[str]] = {}
for path in sorted(pathlib.Path('src/lib/content/langs').glob('*.md')):
	src = path.read_text()
	for title, body in re.findall(r'^##+ ([^\n]*)\n(.*?)(?=^##+ |\Z)', src, re.M | re.S):
		for lang, code in FENCE.findall(body):
			lines = [line for line in code.rstrip('\n').split('\n')]
			code_lines = [i for i, line in enumerate(lines) if line.strip()]
			outs = [i for i, line in enumerate(lines) if OUTPUT.search(line)]
			if not outs:
				continue
			last = code_lines[-1]
			if outs == [last]:
				shape = 'single, last line'
			elif len(outs) == 1:
				shape = 'single, mid block'
			elif outs[-1] == last and all(b - a == 1 for a, b in zip(outs, outs[1:])):
				shape = 'several, consecutive at end'
			elif outs[-1] == last:
				shape = 'several, spread, ends on last line'
			else:
				shape = 'several, spread, code after last output'
			shapes[shape] += 1
			examples.setdefault(shape, []).append(
				f'{path.stem} / {title} / {lang}: outputs on lines {outs} of {len(lines)}'
			)

for shape, n in shapes.most_common():
	print(f'{n:3}  {shape}')
	for e in examples[shape][:4]:
		print(f'       {e}')
