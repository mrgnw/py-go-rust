# Variables for the hover: every local's occurrences in each python/rust/go fence (tree-sitter), and its value
# at each line that sets it, from running the same programs run_snippets.py runs.
# Python: sys.settrace in a wrapper. Rust and Go: tree-sitter finds binding statements and a print to stderr
# goes after each; probes that break the build are dropped and the build retried.
# Every program runs twice; a value that differs between runs (addresses, map order) is dropped.
# Writes src/lib/content/vars.json: per section and language (run_snippets.section_keys), each fence's
# occurrences. Sections already in the file are skipped unless --all; the loader skips sections it lacks.
# uv run analysis/capture_vars.py [page.md ...] [--all]
# /// script
# requires-python = '>=3.14'
# dependencies = ['tree-sitter', 'tree-sitter-python', 'tree-sitter-rust', 'tree-sitter-go']
# ///
import json
import os
import pathlib
import re
import sys
import tempfile
import time

import run_snippets as snippets
import tree_sitter_go
import tree_sitter_python
import tree_sitter_rust
from tree_sitter import Language, Node, Parser

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = sorted((ROOT / 'src/lib/content/langs').glob('*.md'))
OUT = ROOT / 'src/lib/content/vars.json'
TAG = '@@'
MAX_VALUES = 4
SHOWN_VALUES = 3
MAX_VALUE_LEN = 80
MAX_RETRIES = 8
ADDRESS = re.compile(r'0x[0-9a-f]{6,}')
RUNNERS, FENCE, TESTS = snippets.RUNNERS, snippets.FENCE, snippets.TESTS

TRACER = f"""
import sys, threading, types
TAG, MAX_VALUES, MAX_LEN = {TAG!r}, {MAX_VALUES}, {MAX_VALUE_LEN}
seen = {{}}
last = {{}}
prev = {{}}
def show(value):
	try:
		text = repr(value)
	except Exception:
		return None
	return text if len(text) <= MAX_LEN else text[: MAX_LEN - 3] + '...'
def skip(name, value):
	return name.startswith('__') or callable(value) or isinstance(value, (type, types.ModuleType))
def emit(frame, line):
	old = last.setdefault(id(frame), {{}})
	for name, value in list(frame.f_locals.items()):
		if skip(name, value):
			continue
		text = show(value)
		if text is None:
			continue
		if old.get(name) == text:
			continue
		old[name] = text
		n = seen.get((line, name), 0)
		seen[(line, name)] = n + 1
		if n < MAX_VALUES:
			sys.stderr.write(f'{{TAG}}{{line}}\\t{{name}}\\t{{text}}\\n')
def trace(frame, event, arg):
	if frame.f_code.co_filename != 'main.py':
		return None
	if event == 'call':
		last[id(frame)] = {{}}
		emit(frame, frame.f_code.co_firstlineno)
	elif id(frame) in prev:
		emit(frame, prev[id(frame)])
	prev[id(frame)] = frame.f_lineno
	if event == 'return':
		last.pop(id(frame), None)
		prev.pop(id(frame), None)
	return trace
src = open('main.py').read()
threading.settrace(trace)
sys.settrace(trace)
exec(compile(src, 'main.py', 'exec'), {{'__name__': '__main__'}})
"""

RUST_PROBE = """struct Probe<'a, T: ?Sized>(&'a T);
trait ViaDebug { fn show(&self) -> String; }
impl<T: std::fmt::Debug + ?Sized> ViaDebug for Probe<'_, T> { fn show(&self) -> String { format!("{:?}", self.0) } }
trait ViaType { fn show(&self) -> String; }
impl<T: ?Sized> ViaType for &Probe<'_, T> { fn show(&self) -> String { format!("<{}>", std::any::type_name::<T>()) } }
"""
GO_PROBE = """import (
	pfmt "fmt"
	pos "os"
	pstrconv "strconv"
)

"""
GO_SHOW = """
func probeShow(v any) string {
	if s, ok := v.(string); ok {
		return pstrconv.Quote(s)
	}
	return pfmt.Sprintf("%v", v)
}
"""
NOT_A_BINDING = {'subscript', 'attribute', 'index_expression', 'field_expression', 'selector_expression'}
LANGUAGES = {
	'python': Language(tree_sitter_python.language()),
	'rust': Language(tree_sitter_rust.language()),
	'go': Language(tree_sitter_go.language()),
}


def names_in(node: Node | None) -> list[str]:
	if node is None:
		return []
	if node.type == 'identifier':
		return [] if node.text in (b'_', b'self') else [node.text.decode()]
	if node.type in NOT_A_BINDING or node.type in ('type_identifier', 'scoped_identifier'):
		return []
	kids = [c for c in node.named_children if node.child_by_field_name('type') != c]
	return [n for c in kids for n in names_in(c)]


def receiver(call: Node | None) -> list[str]:
	if call is None or call.type != 'call_expression':
		return []
	target = call.child_by_field_name('function')
	if target is None or target.type not in ('field_expression', 'selector_expression'):
		return []
	value = target.child_by_field_name('value') or target.child_by_field_name('operand')
	return [value.text.decode()] if value is not None and value.type == 'identifier' else []


# (row after which to print, names). Rows are 0-based in the parsed text.
def rust_bindings(node: Node) -> tuple[int, list[str]] | None:
	if node.type == 'let_declaration':
		return node.end_point.row, names_in(node.child_by_field_name('pattern'))
	if node.type != 'expression_statement':
		return None
	expr = node.named_children[0]
	if expr.type in ('assignment_expression', 'compound_assignment_expr'):
		left = expr.child_by_field_name('left')
		base = (
			left.child_by_field_name('value')
			if left.type in ('index_expression', 'field_expression')
			else left
		)
		return node.end_point.row, names_in(base) if base is not None else []
	if expr.type == 'for_expression':
		body = expr.child_by_field_name('body')
		if body.start_point.row < body.end_point.row:
			return body.start_point.row, names_in(expr.child_by_field_name('pattern'))
	return node.end_point.row, receiver(expr)


def go_bindings(node: Node) -> tuple[int, list[str]] | None:
	if node.type in ('short_var_declaration', 'assignment_statement'):
		left = node.child_by_field_name('left')
		names = names_in(left) or [n for c in left.named_children for n in receiver_base(c)]
		header = node.parent.type in ('if_statement', 'for_clause', 'expression_switch_statement')
		if header and node.parent.type == 'if_statement':
			body = node.parent.child_by_field_name('consequence')
			return body.start_point.row, names
		return None if header else (node.end_point.row, names)
	if node.type in ('inc_statement', 'dec_statement', 'var_declaration'):
		return node.end_point.row, names_in(node)
	if node.type == 'range_clause':
		body = node.parent.child_by_field_name('body')
		if body is not None and body.start_point.row < body.end_point.row:
			return body.start_point.row, names_in(node.child_by_field_name('left'))
		return None
	if node.type == 'expression_statement':
		return node.end_point.row, [
			n for n in receiver(node.named_children[0]) if n not in snippets.GO_IMPORTS
		]
	return None


def receiver_base(node: Node) -> list[str]:
	value = node.child_by_field_name('operand') if node.type == 'index_expression' else None
	return [value.text.decode()] if value is not None and value.type == 'identifier' else []


def walk(node: Node):
	yield node
	for child in node.named_children:
		yield from walk(child)


def inside_body(node: Node, row: int) -> bool:
	block = node.parent
	while block is not None and block.type not in ('block', 'statement_list'):
		block = block.parent
	if block is not None and block.type == 'statement_list':
		block = block.parent
	return block is not None and block.start_point.row <= row < block.end_point.row


# Probe lines to insert after each row of `text`: {row: [(probe id, name)]}.
def plan(text: str, lang: str) -> dict[int, list[tuple[int, str]]]:
	tree = Parser(LANGUAGES[lang]).parse(text.encode())
	find = rust_bindings if lang == 'rust' else go_bindings
	out: dict[int, list[tuple[int, str]]] = {}
	for node in walk(tree.root_node):
		found = find(node)
		if not found or not found[1] or not inside_body(node, found[0]):
			continue
		row, names = found
		slot = out.setdefault(row, [])
		for name in dict.fromkeys(names):
			if name not in [n for _, n in slot]:
				slot.append((sum(map(len, out.values())), name))
	return out


def instrument(text: str, probes: dict, drop: set[int], line_of, line_for_tag) -> str:
	out = []
	for row, line in enumerate(text.split('\n')):
		out.append(line)
		out.extend(
			line_of(pid, line_for_tag(row), name) for pid, name in probes.get(row, []) if pid not in drop
		)
	return '\n'.join(out)


def rust_program(code: str) -> tuple[str, dict, callable]:
	text = 'fn main() {\n' + code + '\n}'
	probes = plan(text, 'rust')

	def build(drop: set[int]) -> str:
		body = instrument(
			text,
			probes,
			drop,
			lambda pid, k, n: f'eprintln!("{TAG}P{pid} {k}\\t{n}\\t{{}}", (&Probe(&{n})).show());',
			lambda row: row,
		)
		return RUST_PROBE + body.split('\n', 1)[1].rsplit('\n', 1)[0]

	return text, probes, build


def go_program(code: str) -> tuple[str, dict, callable]:
	wrapped = snippets.go_source(code, 'main').removeprefix('package main\n\n')
	shift = wrapped[: wrapped.index(code)].count('\n') if code in wrapped else 0
	probes = plan(wrapped, 'go')

	def build(drop: set[int]) -> str:
		body = instrument(
			wrapped,
			probes,
			drop,
			lambda pid, k, n: f'pfmt.Fprintf(pos.Stderr, "{TAG}P{pid} {k}\\t{n}\\t%s\\n", probeShow({n}))',
			lambda row: row - shift + 1,
		)
		return (
			GO_PROBE + body + GO_SHOW
			if any(pid not in drop for slot in probes.values() for pid, _ in slot)
			else body
		)

	return wrapped, probes, build


GUTTER = re.compile(r'^\s*(\d+)\s*\|', re.MULTILINE)
GO_ERR = re.compile(r'main\.go:(\d+):')


def broken_probes(stderr: str, source: str) -> set[int]:
	lines = source.split('\n')
	rows = {int(n) for n in GUTTER.findall(stderr)} | {int(n) for n in GO_ERR.findall(stderr)}
	return {
		int(m[1]) for k in rows if 0 < k <= len(lines) for m in re.finditer(rf'{TAG}P(\d+) ', lines[k - 1])
	}


def generated(lang: str, code: str, d: pathlib.Path) -> str:
	if lang == 'go':
		return (d / 'main.go').read_text()
	cargo = snippets.CRATES.search(code)
	return ((snippets.CARGO / 'src' / 'main.rs') if cargo else (d / 'main.rs')).read_text()


def compiled_values(lang: str, code: str, d: pathlib.Path, stats: dict) -> list[tuple[int, str, str]] | None:
	_, probes, build = rust_program(code) if lang == 'rust' else go_program(code)
	total = sum(map(len, probes.values()))
	stats['probes'] += total
	drop: set[int] = set()
	for _ in range(MAX_RETRIES):
		program = build(drop)
		result = RUNNERS[lang](program, d, False)
		if result.returncode == 0:
			stats['probes dropped'] += len(drop)
			return parse_tags(result.stderr)
		if os.environ.get('DEBUG'):
			print(result.stderr[-700:])
		broken = broken_probes(result.stderr, generated(lang, program, d)) - drop
		if not broken:
			break
		drop |= broken
	stats['probes dropped'] += total
	stats['programs failing with probes'] += 1
	return None


def python_values(code: str, d: pathlib.Path, stats: dict) -> list[tuple[int, str, str]] | None:
	(d / 'main.py').write_text(code)
	(d / 'tracer.py').write_text(TRACER)
	result = snippets.sh([*snippets.python_with(code), 'python', '-I', 'tracer.py'], d)
	if result.returncode:
		stats['programs failing with probes'] += 1
		print(f'python probes failed in {d}: {result.stderr.strip()[-300:]}')
		return None
	return parse_tags(result.stderr)


def parse_tags(stderr: str) -> list[tuple[int, str, str]]:
	out = []
	for line in stderr.splitlines():
		if line.startswith(TAG):
			head, name, value = line[len(TAG) :].split('\t', 2)
			out.append(
				(
					int(head.split()[-1]),
					name,
					value if len(value) <= MAX_VALUE_LEN else value[: MAX_VALUE_LEN - 3] + '...',
				)
			)
	return out


# Where each language binds a local: (node type, field holding the pattern, or None for every named child).
BINDINGS = {
	'python': [
		('assignment', 'left'),
		('augmented_assignment', 'left'),
		('for_statement', 'left'),
		('for_in_clause', 'left'),
		('parameters', None),
		('lambda_parameters', None),
		('as_pattern', 'alias'),
		('named_expression', 'name'),
	],
	'rust': [
		('let_declaration', 'pattern'),
		('let_condition', 'pattern'),
		('for_expression', 'pattern'),
		('match_arm', 'pattern'),
		('parameter', 'pattern'),
		('closure_parameters', None),
		('const_item', 'name'),
		('static_item', 'name'),
		('assignment_expression', 'left'),
		('compound_assignment_expr', 'left'),
	],
	'go': [
		('short_var_declaration', 'left'),
		('assignment_statement', 'left'),
		('var_spec', 'name'),
		('const_spec', 'name'),
		('range_clause', 'left'),
		('parameter_declaration', 'name'),
		('inc_statement', None),
		('dec_statement', None),
	],
}
# The identifier in this field of this parent names an attribute or keyword, not a local (`p.x`, `f(key=1)`).
NOT_A_LOCAL = {'attribute': 'attribute', 'keyword_argument': 'name'}
# A parameter's default value is not part of what it binds.
NAME_ONLY = {'default_parameter', 'typed_default_parameter'}
WRAP = {'python': ('', ''), 'rust': ('fn main() {\n', '\n}'), 'go': ('func main() {\n', '\n}')}
# Rust format strings name captured locals inside the literal: println!("{f} {x:?}").
RUST_INLINE = re.compile(r'\{([a-z_]\w*)[:}]')


def identifiers(node: Node) -> list[Node]:
	if node.type == 'identifier':
		return [node]
	if node.type in NOT_A_BINDING:
		return []
	if node.type in NAME_ONLY:
		return identifiers(node.child_by_field_name('name'))
	return [i for c in node.named_children for i in identifiers(c)]


def is_local(node: Node) -> bool:
	parent = node.parent
	if node.text in (b'_', b'self') or parent is None:
		return node.text not in (b'_', b'self')
	field = NOT_A_LOCAL.get(parent.type)
	if field and parent.child_by_field_name(field) == node:
		return False
	if parent.child_by_field_name('type') == node or parent.type == 'type':
		return False
	previous = node.prev_sibling
	return not (parent.type == 'token_tree' and previous is not None and previous.type == '.')


def error_count(root: Node) -> int:
	return sum(n.type == 'ERROR' for n in walk(root)) + root.has_error


# Rust and Go fences are often bare statements; parse them wrapped in a function when that has fewer errors.
def parse(code: str, lang: str) -> tuple[Node, int]:
	parser = Parser(LANGUAGES[lang])
	bare = parser.parse(code.encode()).root_node
	head, tail = WRAP[lang]
	if not head:
		return bare, 0
	wrapped = parser.parse((head + code + tail).encode()).root_node
	return (wrapped, 1) if error_count(wrapped) < error_count(bare) else (bare, 0)


def bindings(root: Node, lang: str) -> dict[int, Node]:
	found = {}
	for node in walk(root):
		for kind, field in BINDINGS[lang]:
			if node.type != kind:
				continue
			targets = [node.child_by_field_name(field)] if field else node.named_children
			for target in filter(None, targets):
				for name in identifiers(target):
					enum_variant = lang == 'rust' and name.text[:1].isupper() and not kind.endswith('_item')
					if is_local(name) and not enum_variant:
						found[name.id] = name
	return found


# (row, UTF-16 column, name) of every occurrence of a known local in one fence. Columns are UTF-16 code
# units, the unit shiki's decorations use.
def occurrences(code: str, lang: str, names: set[str]) -> list[tuple[int, int, str]]:
	root, shift = parse(code, lang)
	defs = bindings(root, lang)
	lines = code.split('\n')

	def at(row: int, byte_col: int, name: str) -> tuple[int, int, str]:
		prefix = lines[row].encode()[:byte_col].decode()
		return row, len(prefix.encode('utf-16-le')) // 2, name

	out = []
	for node in walk(root):
		row, col = node.start_point.row - shift, node.start_point.column
		if not 0 <= row < len(lines):
			continue
		if node.type == 'identifier' and node.text.decode() in names and (node.id in defs or is_local(node)):
			out.append(at(row, col, node.text.decode()))
		if lang == 'rust' and node.type == 'string_content':
			for m in RUST_INLINE.finditer(node.text.decode()):
				if m[1] in names and '\n' not in node.text.decode()[: m.start()]:
					out.append(at(row, col + len(node.text.decode()[: m.start() + 1].encode()), m[1]))
	return out


def defined_names(code: str, lang: str) -> set[str]:
	root, _ = parse(code, lang)
	return {n.text.decode() for n in bindings(root, lang).values()}


def captured(lang: str, code: str, d: pathlib.Path, stats: dict) -> dict[tuple[int, str], list[str]]:
	found = python_values(code, d, stats) if lang == 'python' else compiled_values(lang, code, d, stats)
	values: dict[tuple[int, str], list[str]] = {}
	for line, name, value in found or []:
		kept = values.setdefault((line, name), [])
		if len(kept) < MAX_VALUES:
			kept.append(value)
	return values


def shown(values: list[str]) -> str:
	if len(values) > SHOWN_VALUES:
		return ' → '.join(values[:SHOWN_VALUES]) + ' → …'
	return ' → '.join(values)


# One section's program in one language: each fence's occurrences, each with the value at its line. A line that
# sets the name shows the values it set; any other line shows the latest values set before it.
def program_vars(
	lang: str, codes: list[str], d: pathlib.Path, example: str, stats: dict, run: bool = True
) -> dict[str, list]:
	names = set().union(*(defined_names(c, lang) for c in codes))
	occs = [occurrences(c, lang, names) for c in codes]
	code = ''.join(codes).replace('https://example.com', example)
	sets: dict[tuple[int, int], dict[str, list[str]]] = {}
	runnable = run and (
		not re.search(TESTS[lang], code, re.MULTILINE) and RUNNERS[lang](code, d, False).returncode == 0
	)
	if runnable:
		first, second = captured(lang, code, d, stats), captured(lang, code, d, stats)
		starts = [0]
		for c in codes[:-1]:
			starts.append(starts[-1] + c.count('\n'))
		for (line, name), values in first.items():
			if second.get((line, name)) != values or any(ADDRESS.search(v) for v in values):
				stats['unstable values dropped'] += 1
				continue
			fence = max(k for k, s in enumerate(starts) if s < line)
			sets.setdefault((fence, line - starts[fence] - 1), {})[name] = values
	stats['programs'] += 1
	stats['programs with values'] += runnable
	set_at = {name: sorted(at for at, here in sets.items() if name in here) for name in names}
	out = {}
	for fence, (text, found) in enumerate(zip(codes, occs)):
		rows = []
		for row, col, name in sorted(set(found)):
			here = sets.get((fence, row), {}).get(name)
			before = [at for at in set_at[name] if at < (fence, row)]
			values = here or (sets[before[-1]][name] if before else [])
			rows.append([row, col, name, shown(values), int(here is not None)])
			stats['occurrences'] += 1
			stats['occurrences with a value'] += bool(values)
		out[text] = rows
	return out


def main() -> None:
	pages = [pathlib.Path(a) for a in sys.argv[1:] if a != '--all'] or PAGES
	work = pathlib.Path(tempfile.mkdtemp(prefix='pygorst-vars-'))
	example = snippets.serve_example()
	started = time.monotonic()
	stats = {lang: dict.fromkeys(STATS, 0) for lang in RUNNERS}
	saved: dict[str, list] = {} if '--all' in sys.argv or not OUT.exists() else json.loads(OUT.read_text())
	every = {
		key
		for page in PAGES
		for _, body in snippets.sections(page)
		for key, _ in snippets.section_keys(body).values()
	}
	result = {key: rows for key, rows in saved.items() if key in every}
	for page in pages:
		for title, body in snippets.sections(page):
			keys = {lang: key for lang, (key, _) in snippets.section_keys(body).items() if key not in result}
			groups = [(lang, codes, True) for lang, codes in snippets.programs(body)]
			grouped = {code for _, codes, _ in groups for code in codes}
			groups += [(lang, [code], False) for lang, _, code in FENCE.findall(body) if code not in grouped]
			rows: dict[str, list] = {}
			for k, (lang, codes, run) in enumerate(groups):
				if lang not in keys:
					continue
				d = work / re.sub(r'\W+', '-', f'{page.stem}-{title}') / f'{lang}-{k}'
				d.mkdir(parents=True)
				rows |= program_vars(lang, codes, d, example, stats[lang], run)
			for lang, (key, fences) in snippets.section_keys(body).items():
				if lang in keys:
					result[key] = [rows.get(code, []) for code in fences]
	OUT.write_text(
		'{\n'
		+ ',\n'.join(f'\t"{k}": {json.dumps(v, ensure_ascii=False)}' for k, v in sorted(result.items()))
		+ '\n}\n'
	)
	for lang, s in stats.items():
		print(lang, s)
	print(f'{len(result)} sections in {time.monotonic() - started:.0f} s -> {OUT.relative_to(ROOT)}')


STATS = [
	'programs',
	'programs with values',
	'probes',
	'probes dropped',
	'programs failing with probes',
	'unstable values dropped',
	'occurrences',
	'occurrences with a value',
]

if __name__ == '__main__':
	main()
