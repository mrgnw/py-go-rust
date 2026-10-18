# When to pick each

Python explores and glues. Go ships network services. Rust takes over when the machine's limits are the problem. Your starting split is close; the corrections are below.

Snippets assume Python 3.14 + uv, Rust stable (2024 edition) + cargo, Go 1.25.

## Rule of thumb

Your assumption: Python for light, occasional scripts; Go for async/network; Rust for long-running and heavy. Right on Python. Mostly right on Go, but it has no async/await: goroutines make blocking code cheap. Wrong on Rust: "long-running" alone does not call for it, and "heavy" in Python usually already runs native code (NumPy, Polars, PyTorch).

| Task                                | Pick   | Why                                                                                                                                    |
| ----------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| Scripts & glue                      | Python | No compile step, huge stdlib, `uv run` handles inline dependencies.                                                                    |
| Data / ML                           | Python | The ecosystem is the product. Write only the hot kernel in Rust (PyO3).                                                                |
| CLIs                                | Go     | Static binary, cross-compile with `GOOS`/`GOARCH`, written in an afternoon. Rust (`clap`) when you want richer types or heavy parsing. |
| Web / network services              | Go     | Goroutines, `net/http` in stdlib, one binary. Rust (`axum`) when tail latency or memory dominates cost.                                |
| High-throughput / latency-sensitive | Rust   | No GC pauses, no runtime, control over allocation and layout.                                                                          |
| Embedded / WASM                     | Rust   | No runtime, `no_std`, first-class `wasm32` targets. Go wasm output is large.                                                           |
| Long-running daemons                | Go     | Fast to write, hard to leak, GC pauses are tiny. Rust when memory must stay flat or a crash is very expensive.                         |

Go and Rust overlap: both produce a single deployable binary. Go compiles in seconds and is boring on purpose, so a team of any size reads it. Rust costs more upfront and buys you no GC, no data races, and more control.

## At a glance

|                           | Python                                                            | Rust                                                                                    | Go                                                                  |
| ------------------------- | ----------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Execution model           | Bytecode on CPython (experimental JIT)                            | Ahead-of-time to native via LLVM                                                        | Ahead-of-time to native, with a runtime (GC, scheduler)             |
| Typing                    | Dynamic; hints checked only by pyright/mypy                       | Static, strong, inferred; generics + traits                                             | Static, strong, local inference; generics + structural interfaces   |
| Memory management         | Refcount + cycle GC                                               | Ownership + borrow checker, no GC                                                       | Concurrent tracing GC                                               |
| Concurrency model         | Threads (GIL; free-threaded build optional), `asyncio`, processes | Threads + `async`/`await` on a runtime (`tokio`); `Send`/`Sync` checked at compile time | Goroutines + channels; no `async`/`await`                           |
| Error handling            | Exceptions                                                        | `Result<T, E>` + `?`; `panic!` for bugs                                                 | `(value, err)` returns + `if err != nil`                            |
| Null handling             | `None` anywhere                                                   | No null; `Option<T>`                                                                    | `nil` for pointers, maps, slices, interfaces; zero values elsewhere |
| Package manager           | uv (PyPI)                                                         | cargo (crates.io)                                                                       | `go` modules (`go.mod`, proxy-backed)                               |
| Deploy artifact           | Source + venv, wheel, or container                                | One binary (musl for fully static)                                                      | One static binary                                                   |
| Compile / iteration speed | Instant                                                           | Slow full builds; `cargo check` is fast                                                 | Seconds                                                             |
| Learning curve            | Gentle                                                            | Steep: ownership, lifetimes, traits                                                     | Shallow: 25 keywords                                                |

## Toolchain

Order in each column: install, new project, add dependency, run, test, format, lint.

```sh Python
curl -LsSf https://astral.sh/uv/install.sh | sh
uv init hello && cd hello
uv add httpx
uv run main.py
uv run --with pytest pytest
uvx ruff format
uvx ruff check --fix
```

```sh Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
cargo new hello && cd hello
cargo add reqwest
cargo run
cargo test
cargo fmt
cargo clippy
```

```sh Go
brew install go
mkdir hello && cd hello && go mod init example.com/hello
go get github.com/go-chi/chi/v5
go run .
go test ./...
gofmt -w .
go vet ./...
```

## Hello, run it

Layout: `main.py` + `pyproject.toml` / `src/main.rs` + `Cargo.toml` / `main.go` + `go.mod`.

```python
def main() -> None:
	print('hello, world')


if __name__ == '__main__':
	main()
```

```rust
fn main() {
    println!("hello, world");
}
```

```go
package main

import "fmt"

func main() {
	fmt.Println("hello, world")
}
```

## Mental model shifts

- **Both:** a compile step sits between edit and run. Types are checked before anything executes. There is no REPL habit; write a test or a `main` instead.
- **Rust: values move.** `let b = a` transfers ownership, and `a` is dead afterwards. Borrow with `&` and `&mut`; one writer or many readers, never both.
- **Rust: no exceptions, no null.** Failure is `Result`, absence is `Option`; the compiler makes you handle both. `unwrap()` is a deliberate panic.
- **Rust: no inheritance.** Behavior comes from traits on structs and enums. Enums carry data and `match` must be exhaustive.
- **Go: zero values.** Every type has a usable default (`0`, `""`, `nil`). No constructors needed; `var x T` is valid.
- **Go: errors are values.** Functions return `(T, error)`. You check and return them explicitly, with `fmt.Errorf("...: %w", err)` to wrap.
- **Go: explicit everything.** No list comprehensions, no decorators, one loop keyword (`for`). Unused imports and variables fail the build.
- **Go: concurrency by `go` and channels.** Start goroutines freely; share memory by communicating.

```python
a = [1, 2]
b = a
b.append(3)
print(a)  # => [1, 2, 3]
```

```rust
let a = vec![1, 2];
let b = a;
println!("{a:?}"); // error[E0382]: borrow of moved value: `a`
```

```go
a := []int{1, 2}
b := a
b = append(b, 3)
fmt.Println(a) // => [1 2]
```

## Mixing them

Python calling Rust is the best-paying combination: write the hot function in Rust, expose it with PyO3, build with `maturin develop` (or `maturin build` for wheels), and import it like any module. `ruff`, `uv`, `polars`, and `pydantic-core` follow this pattern.

Services in Go or Rust with Python scripts around them also works: Python for migrations, data fixes, and one-off analysis; the compiled service for the request path.

Do not rewrite when the bottleneck is I/O, a database query, or an algorithm. Profile first. A NumPy or Polars call, `asyncio`, or a process pool often closes the gap without a second language.
