# Run each section's python/rust/go fences and check its `=>` comments against stdout.
# A section's fences of one language run as one program, so a second row can use the first row's names.
# stdout must be exactly the `=>` lines, in order; a run of `=>~` lines may come in any order.
# Fences that define tests run under pytest, `rustc --test` and `go test`, and pass on exit code.
# A fence whose comments name an error (`// error[E0382]`, `// compile error: declared and not used`,
# `// panic: ...`) runs alone and must fail with that text. A fence flagged `!norun` (```go !norun) is skipped.
# Python echoes the value of a bare expression statement outside functions, like the interactive prompt, so
# `xs.pop()  # => 3` needs no print.
# Toolchains are the targets, not whatever is on PATH: Python 3.15 via uv, Go 1.25.0 via GOTOOLCHAIN, stable Rust.
# Snippets using crates build in a cargo project cached in ~/.cache/pygorst-snippets.
# Requests to https://example.com go to a local server instead, so HTTP snippets run offline.
# uv run analysis/run_snippets.py src/lib/content/langs/15-algorithms.md
import ast
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
	'context': 'context',
	'atomic': 'sync/atomic',
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
CRATES = re.compile(r'\b(?:serde|serde_json|reqwest|tokio|chrono|thiserror|anyhow|clap)::')
# Crates the cached project carries, as `cargo add` arguments.
CRATE_ARGS = {
	'serde': ['serde', '-F', 'serde/derive'],
	'serde_json': ['serde_json'],
	'reqwest': ['reqwest'],
	'tokio': ['tokio', '-F', 'tokio/full'],
	'chrono': ['chrono'],
	'thiserror': ['thiserror'],
	'anyhow': ['anyhow'],
	'clap': ['clap', '-F', 'clap/derive'],
}
RUST_HAS_MAIN = r'^(?:async )?fn main\('
CARGO = pathlib.Path.home() / '.cache' / 'pygorst-snippets'
FENCE = re.compile(r'^```(python|rust|go)([^\n]*)\n(.*?)^```', re.MULTILINE | re.DOTALL)
FAILS = re.compile(r'(?:#|//) (?:(error\[E\d+\]).*|compile error: (.*)|(panic: .*))$', re.MULTILINE)
OUTPUT = re.compile(r'(?:^|[ \t])(?:#|//) =>(~?) (.*)$', re.MULTILINE)
LINK = re.compile(r'^\[(.*)\]\((.*\.md)\)$')
TESTS = {'python': r'^def test_', 'rust': r'#\[test\]', 'go': r'^func Test'}
RUST_MAIN = 'fn main() -> Result<(), Box<dyn std::error::Error>> {\n'
PYTHON = ['uv', 'run', '--no-project', '--python', '3.15']
GO = 'go1.25.0'


def sh(cmd: list[str], cwd: pathlib.Path, **env: str) -> subprocess.CompletedProcess:
	return subprocess.run(
		cmd, cwd=cwd, capture_output=True, check=False, text=True, timeout=300, env={**os.environ, **env}
	)


# Texts the run's output must contain when the fence is written to fail; empty when it should run.
def expected_errors(code: str) -> list[str]:
	return [next(filter(None, m)).strip() for m in FAILS.findall(code)]


def runnable(info: str) -> bool:
	return '!norun' not in info.split()


# A Go snippet's `func` and `type` declarations stay at top level; its other lines go into main. Returns the
# source and, per source line, the snippet line it came from (None for added lines).
def go_lines(code: str, package: str) -> tuple[str, list[int | None]]:
	lines = code.split('\n')
	if code.lstrip().startswith('package '):
		return code, list(range(len(lines)))
	if re.search(r'^import\b', code, re.MULTILINE):
		return f'package {package}\n\n{code}', [None, None, *range(len(lines))]
	used = {GO_IMPORTS[m] for m in re.findall(r'\b(\w+)\.', code) if m in GO_IMPORTS}
	head = ['package ' + package, '', 'import (', *(f'\t"{p}"' for p in sorted(used)), ')', '']
	if 'func main()' in code or package != 'main':
		return '\n'.join(head + lines), [None] * len(head) + list(range(len(lines)))
	decls: list[int] = []
	body: list[int] = []
	closer = None
	for i, line in enumerate(lines):
		if closer is None and re.match(r'(func|type) ', line):
			decls.append(i)
			closer = {'{': '}', '(': ')'}.get(re.sub(r'\s*//.*$', '', line).rstrip()[-1:])
		elif closer is not None:
			decls.append(i)
			closer = None if line == closer else closer
		else:
			body.append(i)
	order = [None] * len(head) + decls + [None] + body + [None]
	text = [*head, *(lines[i] for i in decls), 'func main() {', *(lines[i] for i in body), '}']
	return '\n'.join(text), order


def go_source(code: str, package: str) -> str:
	return go_lines(code, package)[0]


def cargo_project() -> pathlib.Path:
	if not (CARGO / 'Cargo.toml').exists():
		subprocess.run(['cargo', 'new', '--quiet', '--name', 'snippet', str(CARGO)], check=True)
	manifest = (CARGO / 'Cargo.toml').read_text()
	missing = [arg for name, args in CRATE_ARGS.items() if f'\n{name} = ' not in manifest for arg in args]
	if missing:
		subprocess.run(['cargo', 'add', '--quiet', *missing], cwd=CARGO, check=True)
	return CARGO


# Prepended to a program that echoes values: counts writes to stdout, so an expression that printed its own
# output (a decorator logging the call) is not echoed as well.
ECHO = """import sys as _echo_sys


class _EchoOut:
	def __init__(self, out):
		self.out, self.writes = out, 0

	def write(self, text):
		self.writes += 1
		return self.out.write(text)

	def __getattr__(self, name):
		return getattr(self.out, name)


_echo_sys.stdout = _EchoOut(_echo_sys.stdout)


def _echo_(writes, value):
	if value is not None and _echo_sys.stdout.writes == writes:
		print(repr(value))


"""
# Imported packages a snippet may use, installed for the run.
PACKAGES = {'numpy', 'httpx'}


class Echo(ast.NodeTransformer):
	def __init__(self, lines: set[int]):
		self.lines = lines

	def visit_Expr(self, node: ast.Expr) -> ast.Expr:
		if node.end_lineno not in self.lines:
			return node
		writes = ast.parse('_echo_sys.stdout.writes', mode='eval').body
		call = ast.Call(ast.Name('_echo_', ast.Load()), [writes, node.value], [])
		return ast.copy_location(ast.Expr(call), node)


# Like the interactive prompt, a bare expression whose value is written as `=>` (on its line or the next)
# prints its repr. Returns the code to run: unchanged when nothing echoes, or when it cannot be rewritten
# (syntax newer than this Python, a `__future__` import or a script header, which must stay first).
def echoed(code: str) -> str:
	if 'from __future__' in code:
		return code
	try:
		tree = ast.parse(code)
	except SyntaxError:
		return code
	lines = code.split('\n')

	def shown(n: int) -> bool:
		own_line = n < len(lines) and lines[n].lstrip().startswith('# =>')
		return bool(OUTPUT.search(lines[n - 1])) or own_line

	ends = {n.end_lineno for n in ast.walk(tree) if isinstance(n, ast.Expr) and shown(n.end_lineno)}
	if not ends:
		return code
	return ECHO + ast.unparse(ast.fix_missing_locations(Echo(ends).visit(tree))) + '\n'


# uv run with the packages the code needs: a PEP 723 header's dependencies, or a known import.
def python_with(code: str) -> list[str]:
	header = re.search(r'^# dependencies = \[(.*)\]$', code, re.MULTILINE)
	named = re.findall(r"'([^']+)'", header[1]) if header else []
	imported = set(re.findall(r'^(?:import|from) (\w+)', code, re.MULTILINE)) & PACKAGES
	return [*PYTHON, *(arg for name in sorted({*named, *imported}) for arg in ('--with', name))]


def run_python(code: str, d: pathlib.Path, test: bool) -> subprocess.CompletedProcess:
	if test:
		(d / 'test_main.py').write_text(code)
		return sh([*PYTHON, '--with', 'pytest', 'pytest', '-q', '-p', 'no:cacheprovider'], d)
	(d / 'main.py').write_text(echoed(code))
	return sh([*python_with(code), 'python', '-I', 'main.py'], d)


def run_rust(code: str, d: pathlib.Path, test: bool) -> subprocess.CompletedProcess:
	if test:
		(d / 'main.rs').write_text(code)
		build = sh(['rustc', '--edition', '2024', '--test', '-A', 'warnings', '-o', 'main', 'main.rs'], d)
		return build if build.returncode else sh(['./main'], d)
	if CRATES.search(code):
		project = cargo_project()
		head = '#[tokio::main]\nasync ' + RUST_MAIN if '.await' in code or 'tokio::' in code else RUST_MAIN
		whole = re.search(RUST_HAS_MAIN, code, re.MULTILINE)
		(project / 'src' / 'main.rs').write_text(code if whole else head + code + '\nOk(())\n}\n')
		return sh(['cargo', 'run', '--quiet'], project, RUSTFLAGS='-A warnings')
	has_main = re.search(RUST_HAS_MAIN, code, re.MULTILINE)
	(d / 'main.rs').write_text(code if has_main else RUST_MAIN + code + '\nOk(())\n}\n')
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


def printed(expected: list[tuple[str, str]], got: list[str]) -> bool:
	if len(expected) != len(got):
		return False
	i = 0
	while i < len(expected):
		j = i + 1
		while expected[i][0] and j < len(expected) and expected[j][0]:
			j += 1
		if sorted(text for _, text in expected[i:j]) != sorted(got[i:j]):
			return False
		i = j
	return True


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


WHOLE = {
	'python': r"^if __name__ == '__main__':",
	'rust': RUST_HAS_MAIN,
	'go': r'^package main',
}


# A section's programs, as (language, fences): each language's fences joined in order, except a fence that is a
# whole program by itself (a main guard, fn main, package main), which runs alone. `!norun` fences and fences
# written to fail are left out.
def programs(body: str) -> list[tuple[str, list[str]]]:
	joined: dict[str, list[str]] = {}
	alone: list[tuple[str, list[str]]] = []
	for lang, info, code in FENCE.findall(body):
		if not runnable(info) or expected_errors(code):
			continue
		if re.search(WHOLE[lang], code, re.MULTILINE):
			alone.append((lang, [code]))
		else:
			joined.setdefault(lang, []).append(code)
	return [*joined.items(), *alone]


def failing(body: str) -> list[tuple[str, str]]:
	return [
		(lang, code) for lang, info, code in FENCE.findall(body) if runnable(info) and expected_errors(code)
	]


def check_fails(lang: str, code: str, d: pathlib.Path) -> str | None:
	errors = expected_errors(code)
	result = RUNNERS[lang](code, d, False)
	missing = [e for e in errors if e not in result.stdout + result.stderr]
	if result.returncode and not missing:
		return None
	return f'should fail with {errors}; rc={result.returncode}, missing {missing}'


def check_runs(lang: str, code: str, d: pathlib.Path, example: str) -> str | None:
	expected = [(any_order, text.rstrip()) for any_order, text in OUTPUT.findall(code)]
	test = bool(re.search(TESTS[lang], code, re.MULTILINE))
	result = RUNNERS[lang](code.replace('https://example.com', example), d, test)
	got = [line.rstrip() for line in result.stdout.splitlines()]
	if result.returncode == 0 and (test or printed(expected, got)):
		return None
	report = f'rc={result.returncode}\nexpected {[text for _, text in expected]}\ngot      {got}'
	return report + ('\n' + result.stderr.strip()[-800:] if result.stderr else '')


def main() -> None:
	example = serve_example()
	path = pathlib.Path(sys.argv[1])
	work = pathlib.Path(tempfile.mkdtemp(prefix='pygorst-run-'))
	failures = runs = 0
	for title, body in sections(path):
		checks = [(lang, ''.join(codes), False) for lang, codes in programs(body)]
		checks += [(lang, code, True) for lang, code in failing(body)]
		for k, (lang, code, fails) in enumerate(checks):
			runs += 1
			d = work / re.sub(r'\W+', '-', title) / f'{lang}-{k}'
			d.mkdir(parents=True)
			problem = check_fails(lang, code, d) if fails else check_runs(lang, code, d, example)
			if problem:
				failures += 1
				print(f'--- {title} / {lang}{" (written to fail)" if fails else ""}: {problem}')
	print(f'{sys.argv[1]}: {runs} programs, {"all ok" if failures == 0 else f"{failures} failing"}')
	sys.exit(1 if failures else 0)


if __name__ == '__main__':
	main()
