# Python

The Python you already know, tightened for 2026: Python 3.15, uv for everything, ruff for lint and format. Each section covers a feature where Rust or Go forces a different answer, so the contrast is the point.

## uv workflow

One tool replaces pip, venv, pip-tools, pipx and pyenv. `uv run` creates and syncs `.venv` on demand, so you never activate anything. Commit `pyproject.toml` and `uv.lock`. Scripts can carry their own dependencies in a header comment (PEP 723), the closest Python gets to `go run` with modules.

```sh
uv init app && cd app
uv add httpx
uv add --dev pytest ruff
uv run main.py
uv run pytest
uv run ruff check --fix
uv run ruff format
uv python install 3.15
```

```python fetch.py
# /// script
# requires-python = '>=3.15'
# dependencies = ['httpx']
# ///
import httpx

print(httpx.get('https://example.com').status_code)  # => 200
```

```sh
uv add --script fetch.py rich
uv run fetch.py
```

## Type hints that matter

Hints are not enforced at runtime. Run a checker (pyright, mypy, or `ty`) in CI. In 3.14 annotations are evaluated lazily (PEP 649), so forward references need no quotes and no `from __future__ import annotations`.

```python TypedDict + Literal
from typing import Literal, TypedDict

class User(TypedDict):
	name: str
	age: int

type Mode = Literal['r', 'w']

def open_as(mode: Mode) -> User | None:
	return {'name': 'ada', 'age': 36}
```

```python Protocol
from typing import Protocol

class Closer(Protocol):
	def close(self) -> None: ...

def shutdown(x: Closer) -> None:
	x.close()

shutdown(open('log.txt', 'w'))  # file has close(): OK
```

```python Generics + narrowing
def first[T](xs: list[T]) -> T | None:
	return xs[0] if xs else None

def shout(x: str | int | None) -> str:
	if x is None:
		return ''
	if isinstance(x, int):
		return str(x)
	return x.upper()
```

`Protocol` is structural, like a Go interface. `TypedDict` is a plain `dict` at runtime. `type X = ...` and `def f[T]` (PEP 695) replace `TypeAlias` and `TypeVar`.

## Dataclasses & slots

`@dataclass` generates `__init__`, `__repr__`, `__eq__`. Use `slots=True` (no per-instance `__dict__`, less memory, typo-safe attributes) and `frozen=True` (immutable and hashable) by default. Mutable defaults need `field(default_factory=...)`.

```python
from dataclasses import dataclass, field, replace

@dataclass(slots=True, frozen=True, kw_only=True)
class Point:
	x: float
	y: float = 0.0
	tags: tuple[str, ...] = field(default=())

p = Point(x=1)
replace(p, y=2)  # => Point(x=1, y=2, tags=())
```

| Reach for    | When                                                                 |
| ------------ | -------------------------------------------------------------------- |
| `dataclass`  | internal records, no validation needed                               |
| `attrs`      | validators, converters, more control than stdlib                     |
| `pydantic`   | parsing untrusted input (JSON, env, API bodies); the serde of Python |
| `NamedTuple` | tiny immutable record that must unpack like a tuple                  |

## Enums & match

`StrEnum` members are real strings, so they serialize and compare cleanly. `match` is structural: it destructures sequences, mappings and class instances (dataclasses support positional patterns automatically). Unlike Rust, exhaustiveness is only checked by the type checker (`assert_never`).

```python
from enum import StrEnum, auto

class Status(StrEnum):
	OK = auto()
	FAIL = auto()

Status.OK == 'ok'  # => True
Status('fail')  # => <Status.FAIL: 'fail'>
```

```python
def describe(ev) -> str:
	match ev:
		case {'type': 'key', 'key': str(k)}:
			return f'key {k}'
		case Point(x=0, y=0):
			return 'origin'
		case (x, y):
			return f'pair {x},{y}'
		case [first, *rest]:
			return f'{first} +{len(rest)}'
		case Status.OK | Status.FAIL:
			return 'status'
		case _:
			return 'other'
```

## Iterators & generators

A generator is a function with `yield`; it is lazy, single-pass, and keeps its locals between items. Generator expressions are the lazy cousin of list comprehensions. Anything with `__iter__` works in `for`, `list()`, `sum()`, unpacking.

```python
def countdown(n: int):
	while n > 0:
		yield n
		n -= 1

list(countdown(3))  # => [3, 2, 1]
sum(x * x for x in range(5))  # => 30
```

```python itertools
from itertools import batched, chain, islice, pairwise

list(batched(range(5), 2))  # => [(0, 1), (2, 3), (4,)]
list(pairwise('abc'))  # => [('a', 'b'), ('b', 'c')]
list(islice(chain('ab', 'cd'), 3))  # => ['a', 'b', 'c']
```

Also worth knowing: `groupby` (input must be sorted), `product`, `accumulate`, `zip_longest`, `tee`, `takewhile`. `zip(a, b, strict=True)` raises on length mismatch.

## Context managers

`with` guarantees cleanup on exit, including on exceptions. It is the Python spelling of Rust's `Drop` and Go's `defer`, but scoped to a block rather than to an object or a function.

```python
import os
import tempfile
from contextlib import contextmanager

@contextmanager
def cd(path):
	old = os.getcwd()
	os.chdir(path)
	try:
		yield
	finally:
		os.chdir(old)

with cd(tempfile.gettempdir()):
	print(os.getcwd() == os.path.realpath(tempfile.gettempdir()))  # => True
```

```python ExitStack
from contextlib import ExitStack
from pathlib import Path

paths = sorted(Path('.').glob('*.csv'))

with ExitStack() as stack:
	files = [stack.enter_context(p.open()) for p in paths]
	rows = [f.readline() for f in files]
```

`ExitStack` handles a dynamic number of resources. Also `contextlib.suppress(FileNotFoundError)` and `closing()`.

## Decorators

A decorator is a function that takes a function and returns a function. Always apply `functools.wraps` or the wrapper loses the original name, docstring and signature.

```python
import functools
import time

def timed(fn):
	@functools.wraps(fn)
	def wrapper(*args, **kwargs):
		t = time.perf_counter()
		try:
			return fn(*args, **kwargs)
		finally:
			print(f'{fn.__name__}: {time.perf_counter() - t:.3f}s')
	return wrapper
```

```python cache
from functools import cache, lru_cache

@cache
def fib(n: int) -> int:
	return n if n < 2 else fib(n - 1) + fib(n - 2)

fib(80)  # => 23416728348467685

@lru_cache(maxsize=256)
def load(key: str) -> bytes: ...
```

`cache` is unbounded; `lru_cache(maxsize=N)` evicts. Arguments must be hashable. Clear with `fib.cache_clear()`. Do not cache methods on long-lived instances: the cache holds `self` alive.

## Exceptions

Python signals errors by raising; Rust returns `Result`, Go returns `error`. Catch narrow types, keep the cause with `raise ... from`, and root your own errors in one base class so callers can catch the family.

```python
from pathlib import Path

class AppError(Exception): ...
class ConfigError(AppError): ...

def load(path: Path) -> str:
	try:
		return path.read_text()
	except OSError as e:
		raise ConfigError(f'cannot read {path}') from e
```

```python ExceptionGroup
try:
	raise ExceptionGroup('batch', [ValueError('a'), TypeError('b')])
except* ValueError as eg:
	print(eg.exceptions)  # => (ValueError('a'),)
except* TypeError as eg:
	print(eg.exceptions)  # => (TypeError('b'),)
```

`except*` splits a group by type; every matching clause runs. `asyncio.TaskGroup` raises groups. Since 3.14, `except A, B:` needs no parentheses when there is no `as`. Use `e.add_note('context')` to attach text.

## asyncio

One thread, cooperative scheduling: `await` is the only yield point, so a blocking call stalls everything. Prefer `TaskGroup` (structured: if one task fails the rest are cancelled and the group raises) over bare `create_task`. `gather` returns results in order.

```python
import asyncio

async def fetch(n: int) -> int:
	await asyncio.sleep(0.1)
	return n * 2

async def main():
	async with asyncio.TaskGroup() as tg:
		tasks = [tg.create_task(fetch(i)) for i in range(3)]
	print([t.result() for t in tasks])  # => [0, 2, 4]
	print(await asyncio.gather(fetch(1), fetch(2)))  # => [2, 4]

asyncio.run(main())
```

| Workload                  | Use                                                 |
| ------------------------- | --------------------------------------------------- |
| many sockets / HTTP calls | `asyncio`                                           |
| blocking libs, file I/O   | threads (`asyncio.to_thread`, `ThreadPoolExecutor`) |
| CPU-bound pure Python     | processes (`ProcessPoolExecutor`) or native code    |

The GIL lets one thread run Python bytecode at a time, so threads do not speed up CPU work; since 3.14 there is a supported free-threaded build (`uv python install 3.15t`) that removes it, at some single-thread cost and with extension-compatibility caveats. Use `async with asyncio.timeout(5):` for deadlines.

## concurrent.futures

The simplest way to parallelize a map. Same interface for threads and processes, so switching is a one-word change. Workers are joined when the `with` block exits.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def size(url: str) -> int:
	return len(url)

urls = ['https://a.example', 'https://bb.example']

with ThreadPoolExecutor(max_workers=8) as pool:
	print(list(pool.map(size, urls)))  # => [17, 18]
	futs = {pool.submit(size, u): u for u in urls}
	for f in as_completed(futs):
		print(futs[f], f.result())
	# =>~ https://a.example 17
	# =>~ https://bb.example 18
```

```python ProcessPoolExecutor
from concurrent.futures import ProcessPoolExecutor

def cpu(n: int) -> int:
	return sum(i * i for i in range(n))

if __name__ == '__main__':
	with ProcessPoolExecutor() as pool:
		print(list(pool.map(cpu, [10, 100])))  # => [285, 328350]
```

Process pools pickle arguments and results, and re-import the main module, so the `__main__` guard is mandatory (3.14 defaults to `forkserver` on Linux, `spawn` on macOS). 3.14 adds `InterpreterPoolExecutor`: subinterpreters, each with its own GIL.

## pathlib & files

Use `Path`, not `os.path` string juggling. `/` joins. `read_text` and `write_text` open and close for you; pass `encoding='utf-8'` explicitly when it matters. Iterate a file object for lazy line-by-line reading.

```python
from pathlib import Path

p = Path('data') / 'in.txt'
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text('hi\n')
p.read_text()  # => 'hi\n'
p.suffix, p.stem  # => ('.txt', 'in')
p.with_suffix('.md').name  # => 'in.md'
```

```python
from pathlib import Path

for f in Path('data').rglob('*.txt'):
	with f.open() as fh:
		for line in fh:
			print(f.name, line.rstrip())  # => in.txt hi

Path('data/in.txt').copy('data/out.txt')
```

`Path.copy()` and `Path.move()` are new in 3.14. `Path.home()`, `.exists()`, `.is_file()`, `.iterdir()`, `.unlink(missing_ok=True)` cover the rest.

## Dunder methods & protocols

Python's "traits" are dunder methods; the language looks them up by name. Implement the method and the syntax works: no `impl` block, no declared interface. Define `__eq__` and you must define `__hash__` too, or the class becomes unhashable.

```python
class Vec:
	__slots__ = ('x', 'y')

	def __init__(self, x: float, y: float):
		self.x, self.y = x, y

	def __repr__(self):
		return f'Vec({self.x}, {self.y})'

	def __eq__(self, o):
		return isinstance(o, Vec) and (self.x, self.y) == (o.x, o.y)

	def __hash__(self):
		return hash((self.x, self.y))

	def __iter__(self):
		yield self.x
		yield self.y
```

```python Usage
v = Vec(1, 2)
x, y = v  # __iter__
v == Vec(1, 2)  # => True
{v: 'a'}[Vec(1, 2)]  # => 'a'
list(v)  # => [1, 2]
repr(v)  # => 'Vec(1, 2)'
```

| Method                                     | Powers                     |
| ------------------------------------------ | -------------------------- |
| `__iter__` / `__next__`                    | `for`, unpacking, `list()` |
| `__enter__` / `__exit__`                   | `with`                     |
| `__eq__` / `__hash__`                      | `==`, dict keys, sets      |
| `__repr__` / `__str__`                     | REPL / debugging, `print`  |
| `__len__` / `__getitem__` / `__contains__` | `len()`, `x[i]`, `in`      |
| `__call__`                                 | `obj(...)`                 |

## Packaging & layout

Use the `src/` layout so tests import the installed package, not the working directory. `[project.scripts]` creates a command on install. `uv init --package` generates all of this.

```text Layout
app/
  pyproject.toml
  uv.lock
  src/app/
    __init__.py
    cli.py
  tests/
    test_cli.py
```

```toml pyproject.toml
[project]
name = 'app'
version = '0.1.0'
requires-python = '>=3.15'
dependencies = ['httpx>=0.28']

[project.scripts]
app = 'app.cli:main'

[dependency-groups]
dev = ['pytest', 'ruff']

[build-system]
requires = ['uv_build>=0.9']
build-backend = 'uv_build'
```

```sh
uv init --package app
uv run app
uv build
uv publish
uv tool install .
```

## Performance escape hatches

Profile first; the bottleneck is rarely where you think. Then, in order of effort: better algorithm or data structure, vectorize with numpy, parallelize, rewrite the hot function in Rust.

```sh
uv run python -m cProfile -s cumtime main.py
uv run --with py-spy py-spy record -o prof.svg -- python main.py
```

```python numpy
import numpy as np

a = np.arange(1_000_000)
print((a * a).sum())  # => 333332833333500000
```

```rust src/lib.rs !norun
use pyo3::prelude::*;

#[pyfunction]
fn fib(n: u64) -> u64 {
    if n < 2 { n } else { fib(n - 1) + fib(n - 2) }
}

#[pymodule]
fn fastlib(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fib, m)?)
}
```

```sh
uv tool install maturin
maturin init --bindings pyo3 fastlib
maturin develop --release
```

```python !norun
import fastlib

fastlib.fib(40)  # => 102334155
```

`multiprocessing` and `ProcessPoolExecutor` for CPU-bound fan-out. PyO3 with maturin is how ruff, uv, pydantic-core and polars ship Rust inside Python wheels.
