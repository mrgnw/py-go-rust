# Run each section's python/rust/go fences and check its `=>` comments against stdout.
# A section's fences of one language run as one program, so a second row can use the first row's names.
# Every `=>` line must be printed, in order; other output (loop bodies, map iteration) is allowed.
# Fences that define tests run under pytest, `rustc --test` and `go test`.
# Toolchains are the targets, not whatever is on PATH: Python 3.15 via uv, Go 1.25.0 via GOTOOLCHAIN, stable Rust.
# Snippets using crates build in a cargo project cached in ~/.cache/pygorst-snippets.
# Requests to https://example.com go to a local server instead, so HTTP snippets run offline.
# uv run analysis/run_snippets.py src/lib/content/langs/15-algorithms.md
import http.server
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import threading

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
	'cmp': 'cmp',
	'log': 'log',
	'json': 'encoding/json',
	'http': 'net/http',
	'io': 'io',
	'sync': 'sync',
	'flag': 'flag',
	'testing': 'testing',
}
CRATES = re.compile(r'\b(?:serde|serde_json|reqwest|tokio|chrono)::')
CARGO = pathlib.Path.home() / '.cache' / 'pygorst-snippets'
FENCE = re.compile(r'^```(python|rust|go)[^\n]*\n(.*?)^```', re.MULTILINE | re.DOTALL)
OUTPUT = re.compile(r'[ \t]+(?:#|//) => (.*)$', re.MULTILINE)
LINK = re.compile(r'^\[(.*)\]\((.*\.md)\)$')
TESTS = {'python': r'^def test_', 'rust': r'#\[test\]', 'go': r'^func Test'}
RUST_MAIN = 'fn main() -> Result<(), Box<dyn std::error::Error>> {\n'
PYTHON = ['uv', 'run', '--no-project', '--python', '3.15']
GO = 'go1.25.0'


def sh(cmd: list[str], cwd: pathlib.Path, **env: str) -> subprocess.CompletedProcess:
	return subprocess.run(
		cmd, cwd=cwd, capture_output=True, check=False, text=True, timeout=300, env={**os.environ, **env}
	)


def go_source(code: str, package: str) -> str:
	if re.search(r'^import\b', code, re.MULTILINE):
		return f'package {package}\n\n{code}'
	used = {GO_IMPORTS[m] for m in re.findall(r'\b(\w+)\.', code) if m in GO_IMPORTS}
	imports = '\n'.join(f'\t"{p}"' for p in sorted(used))
	body = code if 'func main()' in code or package != 'main' else 'func main() {\n' + code + '\n}\n'
	return f'package {package}\n\nimport (\n{imports}\n)\n\n{body}'


def cargo_project() -> pathlib.Path:
	if not (CARGO / 'Cargo.toml').exists():
		crates = [
			'serde',
			'-F',
			'serde/derive',
			'serde_json',
			'reqwest',
			'tokio',
			'-F',
			'tokio/full',
			'chrono',
		]
		subprocess.run(['cargo', 'new', '--quiet', '--name', 'snippet', str(CARGO)], check=True)
		subprocess.run(['cargo', 'add', '--quiet', *crates], cwd=CARGO, check=True)
	return CARGO


def run_python(code: str, d: pathlib.Path, test: bool) -> subprocess.CompletedProcess:
	if test:
		(d / 'test_main.py').write_text(code)
		return sh([*PYTHON, '--with', 'pytest', 'pytest', '-q', '-p', 'no:cacheprovider'], d)
	(d / 'main.py').write_text(code)
	return sh([*PYTHON, 'python', '-I', 'main.py'], d)


def run_rust(code: str, d: pathlib.Path, test: bool) -> subprocess.CompletedProcess:
	if test:
		(d / 'main.rs').write_text(code)
		build = sh(['rustc', '--edition', '2024', '--test', '-A', 'warnings', '-o', 'main', 'main.rs'], d)
		return build if build.returncode else sh(['./main'], d)
	if CRATES.search(code):
		project = cargo_project()
		head = '#[tokio::main]\nasync ' + RUST_MAIN if '.await' in code or 'tokio::' in code else RUST_MAIN
		(project / 'src' / 'main.rs').write_text(head + code + '\nOk(())\n}\n')
		return sh(['cargo', 'run', '--quiet'], project, RUSTFLAGS='-A warnings')
	(d / 'main.rs').write_text(RUST_MAIN + code + '\nOk(())\n}\n')
	build = sh(['rustc', '--edition', '2024', '-A', 'warnings', '-o', 'main', 'main.rs'], d)
	return build if build.returncode else sh(['./main'], d)


def run_go(code: str, d: pathlib.Path, test: bool) -> subprocess.CompletedProcess:
	(d / 'go.mod').write_text('module x\n\ngo 1.25\n')
	if test:
		(d / 'x_test.go').write_text(go_source(code, 'x'))
		return sh(['go', 'test', '.'], d, GOTOOLCHAIN=GO)
	(d / 'main.go').write_text(go_source(code, 'main'))
	return sh(['go', 'run', '.'], d, GOTOOLCHAIN=GO)


RUNNERS = {'python': run_python, 'rust': run_rust, 'go': run_go}


# Sections of a page file, `## [Title](dir/file.md)` read from the linked file. A section file is one section.
def sections(path: pathlib.Path) -> list[tuple[str, str]]:
	src = path.read_text()
	found = re.findall(r'^#{2,3} ([^\n]*)\n(.*?)(?=^#{2,3} |\Z)', src, re.MULTILINE | re.DOTALL)
	if not found:
		return [(path.stem, src)]
	out = []
	for title, body in found:
		link = LINK.match(title)
		out.append((link[1], (path.parent / link[2]).read_text()) if link else (title, body))
	return out


def printed_in_order(expected: list[str], got: list[str]) -> bool:
	lines = iter(got)
	return all(line in lines for line in expected)


class Page(http.server.BaseHTTPRequestHandler):
	def do_GET(self) -> None:
		body = b'<html>example</html>'
		self.send_response(200)
		self.send_header('Content-Length', str(len(body)))
		self.end_headers()
		self.wfile.write(body)

	def log_message(self, *args: object) -> None:
		pass


def serve_example() -> str:
	server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Page)
	threading.Thread(target=server.serve_forever, daemon=True).start()
	return f'http://127.0.0.1:{server.server_port}'


def main() -> None:
	example = serve_example()
	path = pathlib.Path(sys.argv[1])
	work = pathlib.Path(tempfile.mkdtemp(prefix='pygorst-run-'))
	failures = runs = 0
	for title, body in sections(path):
		programs: dict[str, str] = {}
		for lang, code in FENCE.findall(body):
			programs[lang] = programs.get(lang, '') + code
		for lang, code in programs.items():
			runs += 1
			d = work / re.sub(r'\W+', '-', title) / lang
			d.mkdir(parents=True)
			expected = [line.rstrip() for line in OUTPUT.findall(code)]
			test = bool(re.search(TESTS[lang], code, re.MULTILINE))
			result = RUNNERS[lang](code.replace('https://example.com', example), d, test)
			got = [line.rstrip() for line in result.stdout.splitlines()]
			if result.returncode == 0 and printed_in_order(expected, got):
				continue
			failures += 1
			print(f'--- {title} / {lang} (rc={result.returncode})')
			print(f'expected {expected}\ngot      {got}')
			if result.stderr:
				print(result.stderr.strip()[-800:])
	print(f'{sys.argv[1]}: {runs} programs, {"all ok" if failures == 0 else f"{failures} failing"}')
	sys.exit(1 if failures else 0)


main()
