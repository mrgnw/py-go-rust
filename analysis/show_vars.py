# Print a section's captured variables from src/lib/content/vars.json, one line per occurrence.
# uv run analysis/show_vars.py src/lib/content/langs/10-compare.md 'Basic types'
# /// script
# dependencies = ['tree-sitter', 'tree-sitter-python', 'tree-sitter-rust', 'tree-sitter-go']
# ///
import json
import pathlib
import sys

import run_snippets as snippets
from capture_vars import OUT, fence_key

page, wanted = pathlib.Path(sys.argv[1]), sys.argv[2]
saved = json.loads(OUT.read_text())
for title, body in snippets.sections(page):
	if wanted not in title:
		continue
	for lang, code in snippets.FENCE.findall(body):
		lines = code.split('\n')
		print(f'--- {title} / {lang}')
		for row, col, name, value, sets in saved.get(fence_key(code.removesuffix('\n')), []):
			print(f'{"set" if sets else "   "} {lines[row].strip()[:50]:50} {name} = {value}')
