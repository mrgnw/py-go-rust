# Run every python/rust/go fence of a content file and diff stdout against its `=>` comments.
# uv run analysis/run_snippets.py src/lib/content/langs/15-algorithms.md
import pathlib
import re
import subprocess
import sys
import tempfile

GO_IMPORTS = {
	'fmt': 'fmt',
	'slices': 'slices',
	'strings': 'strings',
	'math': 'math',
	'heap': 'container/heap',
	'sort': 'sort',
	'strconv': 'strconv',
	'maps': 'maps',
	'os': 'os',
	'errors': 'errors',
	'time': 'time',
}
FENCE = re.compile(r'^```(python|rust|go)[^\n]*\n(.*?)^```', re.M | re.S)
OUTPUT = re.compile(r'[ \t]+(?:#|//) => (.*)$', re.M)


def go_source(code: str) -> str:
	used = {GO_IMPORTS[m] for m in re.findall(r'\b(\w+)\.', code) if m in GO_IMPORTS}
	imports = '\n'.join(f'\t"{p}"' for p in sorted(used))
	body = code if 'func main()' in code else 'func main() {\n' + code + '\n}\n'
	return f'package main\n\nimport (\n{imports}\n)\n\n{body}'


def run(lang: str, code: str, d: pathlib.Path) -> subprocess.CompletedProcess:
	if lang == 'python':
		(d / 'main.py').write_text(code)
		return subprocess.run(
			[sys.argv[2] if len(sys.argv) > 2 else 'python3', '-I', 'main.py'],
			cwd=d,
			capture_output=True,
			text=True,
			timeout=60,
		)
	if lang == 'rust':
		(d / 'main.rs').write_text(
			'fn main() -> Result<(), Box<dyn std::error::Error>> {\n' + code + '\nOk(())\n}\n'
		)
		build = subprocess.run(
			['rustc', '--edition', '2024', '-A', 'warnings', '-o', 'main', 'main.rs'],
			cwd=d,
			capture_output=True,
			text=True,
		)
		if build.returncode:
			return build
		return subprocess.run(['./main'], cwd=d, capture_output=True, text=True, timeout=60)
	(d / 'go.mod').write_text('module x\n\ngo 1.25\n')
	(d / 'main.go').write_text(go_source(code))
	return subprocess.run(['go', 'run', '.'], cwd=d, capture_output=True, text=True, timeout=120)


LINK = re.compile(r'^\[(.*)\]\((.*\.md)\)$')


# Sections of a page file, `## [Title](dir/file.md)` read from the linked file. A section file is one section.
def sections(path: pathlib.Path) -> list[tuple[str, str]]:
	src = path.read_text()
	found = re.findall(r'^#{2,3} ([^\n]*)\n(.*?)(?=^#{2,3} |\Z)', src, re.M | re.S)
	if not found:
		return [(path.stem, src)]
	out = []
	for title, body in found:
		link = LINK.match(title)
		out.append((link[1], (path.parent / link[2]).read_text()) if link else (title, body))
	return out


def main() -> None:
	path = pathlib.Path(sys.argv[1])
	work = pathlib.Path(tempfile.mkdtemp(prefix='pygorst-run-'))
	failures = runs = 0
	for title, body in sections(path):
		for i, (lang, code) in enumerate(FENCE.findall(body)):
			runs += 1
			d = work / re.sub(r'\W+', '-', title) / f'{i}-{lang}'
			d.mkdir(parents=True)
			expected = OUTPUT.findall(code)
			result = run(lang, code, d)
			got = result.stdout.strip().splitlines()
			if result.returncode == 0 and got == expected:
				continue
			failures += 1
			print(f'--- {title} / {lang} (rc={result.returncode})')
			print(f'expected {expected}\ngot      {got}')
			if result.stderr:
				print(result.stderr.strip()[-800:])
	print(f'{sys.argv[1]}: {runs} snippets, {"all ok" if failures == 0 else f"{failures} failing"}')
	sys.exit(1 if failures else 0)


main()
