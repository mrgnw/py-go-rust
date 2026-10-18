# Rust

Compiled, statically typed, no garbage collector, no exceptions. The compiler enforces who owns each value and who may touch it, so most bugs Python finds at runtime show up as build errors. Expect a steep first week and a quiet runtime after.

## cargo & project layout

`cargo` is pip, uv, venv, pytest, ruff and the build step in one. `Cargo.toml` is `pyproject.toml`, `Cargo.lock` is `uv.lock`, `target/` is the build output (gitignore it). `src/main.rs` is a binary, `src/lib.rs` a library, `tests/` holds integration tests. `bacon` re-runs check or test on every save.

```sh
cargo new hello
cd hello
cargo add anyhow
cargo run
cargo test
cargo clippy
cargo fmt
cargo install --locked bacon
bacon
```

```toml Cargo.toml
[package]
name = "hello"
version = "0.1.0"
edition = "2024"

[dependencies]
anyhow = "1"
```

## let, mut, shadowing, types

Bindings are immutable unless marked `mut`. Types are inferred inside functions; function signatures must be annotated. Shadowing (`let` again) makes a new variable, even of a different type. There are no implicit numeric conversions: use `as` or `From`.

```python
x = 5
x += 1
name = "abc"
name = len(name)
```

```rust
let x = 5;
let mut count = 0;
count += 1;
let name = "abc";
let name = name.len();
let big: u64 = 1_000_000;
let small = u32::try_from(big).unwrap();
let ratio = small as f64 / 2.0;
const MAX: usize = 10;
```

Integers: `i8..i128`, `u8..u128`, `usize` (indices and lengths). Floats: `f32`, `f64`. Also `bool`, `char` (one Unicode scalar), tuples `(i32, f64)`, arrays `[i32; 3]`.

## ownership & move semantics

Every value has exactly one owner, and assignment or passing to a function moves it. The old name becomes unusable, so there is no aliasing surprise like Python's `b = a`. Copying is explicit with `.clone()`. Small plain types (`i32`, `bool`, `char`, `f64`) implement `Copy` and are copied silently. The value is dropped when its owner leaves scope, deterministically.

```python
a = [1, 2, 3]
b = a
print(a)
# => [1, 2, 3]
```

```rust Won't compile
let a = vec![1, 2, 3];
let b = a;
println!("{a:?}");
// error[E0382]: borrow of moved value: `a`
```

```rust Fixed
let a = vec![1, 2, 3];
let b = a.clone();
println!("{a:?} {b:?}");
// => [1, 2, 3] [1, 2, 3]
```

## borrowing & references

`&T` lends read access, `&mut T` lends write access. At any moment a value has either many `&T` or one `&mut T`, never both. It is a lock checked at compile time, with no runtime cost. Functions take references so the caller keeps ownership.

```rust Won't compile
let mut v = vec![1, 2, 3];
let first = &v[0];
v.push(4);
println!("{first}");
// error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable
```

```rust Fixed
fn total(v: &[i32]) -> i32 { v.iter().sum() }
fn add(v: &mut Vec<i32>) { v.push(4); }
let mut v = vec![1, 2, 3];
let first = v[0];
add(&mut v);
println!("{first} {}", total(&v));
// => 1 10
```

## lifetimes

A lifetime is how long a reference stays valid. The compiler infers it in most functions (elision): one input reference means the output borrows from it, and `&self` methods tie the output to `self`. You write `'a` only when a function takes two or more references and returns one. `'static` means "valid for the whole program": string literals, or a `T: 'static` bound on things sent to threads and tasks. If a struct needs `<'a>`, consider owning a `String` instead.

```rust Won't compile
fn longest(a: &str, b: &str) -> &str {
    if a.len() > b.len() { a } else { b }
}
// error[E0106]: missing lifetime specifier
```

```rust Fixed
fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() { a } else { b }
}
fn first_word(s: &str) -> &str {
    s.split(' ').next().unwrap_or("")
}
let literal: &'static str = "lives forever";
```

## String vs &str

`String` is an owned, growable, UTF-8 buffer. `&str` is a borrowed view into one (literals are `&'static str`). Take `&str` in parameters, since `&String` converts to it for free, and return `String` when you build something new. `impl AsRef<str>` also accepts owned values and other string-like types. UTF-8 means no `s[0]`; use `.chars()` or `.as_bytes()`.

```python
def shout(s: str) -> str:
	return s.upper() + "!"
```

```rust
fn shout(s: &str) -> String {
    s.to_uppercase() + "!"
}
fn len_of(s: impl AsRef<str>) -> usize {
    s.as_ref().len()
}
let owned = String::from("hi");
println!("{}", shout(&owned));
// => HI!
println!("{}", len_of("hi") + len_of(owned));
// => 4
```

## Option

`Option<T>` replaces None-or-value: `Some(x)` or `None`, and the type checker forces you to handle both. `?` on an `Option` returns `None` early. `.unwrap()` panics (an uncaught exception): fine in tests and throwaway scripts, never in library code. Use `.expect("why this holds")` for true invariants.

```python
user = users.get(1)
if user is not None:
	print(user)
shown = user.upper() if user else "anon"
```

```rust
let users = HashMap::from([(1, "ann".to_string())]);
let found = users.get(&1);
if let Some(name) = found {
    println!("{name}");
}
let shown = found.map(|n| n.to_uppercase()).unwrap_or_else(|| "anon".into());
// => "ANN"
fn first_even(v: &[i32]) -> Option<i32> {
    let n = v.iter().copied().find(|n| n % 2 == 0)?;
    Some(n * 10)
}
```

`.ok_or(err)` turns an `Option` into a `Result`; `.unwrap_or_default()` falls back to the type's default.

## Result & `?`

Errors are return values, not exceptions: `Result<T, E>` is `Ok(T)` or `Err(E)`. `?` returns the error early (converting it with `From`), like an exception propagating but visible in the signature. Scripts: `Box<dyn Error>`. Libraries: a `thiserror` enum so callers can match. Apps: `anyhow`, which adds `.context()`.

```rust Script
use std::error::Error;
fn load(path: &str) -> Result<i32, Box<dyn Error>> {
    let text = std::fs::read_to_string(path)?;
    let n: i32 = text.trim().parse()?;
    Ok(n)
}
```

```rust Library (thiserror)
#[derive(Debug, thiserror::Error)]
enum ConfigError {
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
    #[error("bad number: {0}")]
    Parse(#[from] std::num::ParseIntError),
}
```

```rust App (anyhow)
use anyhow::{Context, Result};
fn main() -> Result<()> {
    let text = std::fs::read_to_string("config.toml")
        .context("reading config.toml")?;
    println!("{}", text.len());
    Ok(())
}
```

## enums & match

Enum variants can carry data, so an enum is a tagged union, roughly a Python `Union` plus `match`. `match` must be exhaustive: adding a variant breaks every match that forgot it, which is the point. `_` opts out. `Option` and `Result` are plain enums.

```python
match shape:
	case ("circle", r):
		area = 3.14 * r * r
	case ("rect", w, h):
		area = w * h
```

```rust
enum Shape {
    Circle(f64),
    Rect { w: f64, h: f64 },
    Empty,
}
fn area(s: &Shape) -> f64 {
    match s {
        Shape::Circle(r) => std::f64::consts::PI * r * r,
        Shape::Rect { w, h } => w * h,
        Shape::Empty => 0.0,
    }
}
let big = matches!(Shape::Circle(2.0), Shape::Circle(r) if r > 1.0);
```

## structs, impl, Default, derive

A struct is a dataclass with no inheritance. Methods live in `impl` blocks: `&self` reads, `&mut self` mutates, `self` consumes. There is no `__init__`; `new` is a plain associated function by convention. `#[derive]` generates `__repr__`, `__eq__`, copy and defaults for you.

```python
@dataclass
class Point:
	x: float = 0.0
	y: float = 0.0
```

```rust
#[derive(Debug, Clone, Default, PartialEq)]
struct Point {
    x: f64,
    y: f64,
}
impl Point {
    fn new(x: f64, y: f64) -> Self { Self { x, y } }
    fn dist(&self) -> f64 { self.x.hypot(self.y) }
}
let p = Point { x: 3.0, ..Default::default() };
println!("{p:?} {}", Point::new(3.0, 4.0).dist());
// => Point { x: 3.0, y: 0.0 } 5
```

## traits & generics

A trait is a Protocol/ABC: a set of methods a type promises. `impl Trait` in a parameter is static dispatch (compiled per concrete type, no runtime cost). `dyn Trait` is dynamic dispatch through a vtable, needed for mixed collections like `Vec<Box<dyn Speak>>`. Bounds (`T: PartialOrd`) say what a generic type must support; `where` clauses keep long bounds readable.

```rust Traits
trait Speak {
    fn speak(&self) -> String;
}
struct Dog;
impl Speak for Dog {
    fn speak(&self) -> String { "woof".into() }
}
fn once(s: &impl Speak) -> String { s.speak() }
fn many(xs: &[Box<dyn Speak>]) -> Vec<String> {
    xs.iter().map(|x| x.speak()).collect()
}
```

```rust Bounds
fn largest<T>(xs: &[T]) -> Option<&T>
where
    T: PartialOrd,
{
    let mut best = xs.first()?;
    for x in xs {
        if x > best { best = x; }
    }
    Some(best)
}
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct Id(u32);
```

| Derive              | Python equivalent                                   |
| ------------------- | --------------------------------------------------- |
| `Debug`             | `__repr__`                                          |
| `Clone`             | `copy.deepcopy`                                     |
| `Copy`              | immutable value, copied on assignment               |
| `PartialEq`, `Eq`   | `__eq__`                                            |
| `Hash`              | `__hash__`, needed for `HashMap` keys and `HashSet` |
| `PartialOrd`, `Ord` | `__lt__` and friends, needed for `sort()`           |
| `Default`           | dataclass defaults                                  |

## iterators & closures

Iterators are lazy like Python generators: `map` and `filter` do nothing until a consumer (`collect`, `sum`, `count`, a `for` loop) pulls. `.iter()` yields `&T`, `.iter_mut()` yields `&mut T`, `.into_iter()` yields `T` and consumes the collection. `collect` cannot guess the target type, so annotate the variable or use the turbofish `::<Vec<_>>`. Closures `|x| x + 1` borrow what they capture; `move` takes ownership (required for threads and spawned tasks).

```python
evens = [x * x for x in nums if x % 2 == 0]
```

```rust
let nums = vec![1, 2, 3, 4];
let evens: Vec<i32> = nums.iter().filter(|x| *x % 2 == 0).map(|x| x * x).collect();
// => [4, 16]
let total = nums.iter().sum::<i32>();
let words = "a b c".split(' ').collect::<Vec<_>>();
let mut v = nums.clone();
for x in v.iter_mut() {
    *x += 1;
}
for x in nums {
    println!("{x}");
}
```

```rust Closures
let offset = 10;
let add = |x: i32| x + offset;
let owned = String::from("hi");
let say = move || println!("{owned}");
println!("{}", add(1));
// => 11
say();
// => hi
```

## collections

All but `Vec` live in `std::collections`. `HashMap` iteration order is random; use `BTreeMap` for sorted keys. `v[i]` panics when out of range; `v.get(i)` returns an `Option`, like `dict.get`.

| Python              | Rust             |
| ------------------- | ---------------- |
| `list`              | `Vec<T>`         |
| `dict`              | `HashMap<K, V>`  |
| sorted dict         | `BTreeMap<K, V>` |
| `collections.deque` | `VecDeque<T>`    |
| `set`               | `HashSet<T>`     |

```rust
use std::collections::{BTreeMap, HashMap, HashSet, VecDeque};
let mut v = vec![3, 1, 2];
v.push(4);
v.sort();
let mut counts: HashMap<&str, i32> = HashMap::new();
for w in ["a", "b", "a"] {
    *counts.entry(w).or_insert(0) += 1;
}
println!("{}", counts["a"]);
// => 2
```

```rust
let mut tree = BTreeMap::new();
tree.insert("b", 2);
tree.insert("a", 1);
println!("{:?}", tree.keys().collect::<Vec<_>>());
// => ["a", "b"]
let mut q = VecDeque::from([1, 2]);
q.push_back(3);
println!("{:?}", q.pop_front());
// => Some(1)
let set: HashSet<i32> = [1, 2, 2].into_iter().collect();
println!("{}", set.len());
// => 2
```

## smart pointers & interior mutability

Python gives you reference-counted shared mutable objects for free; Rust makes you pick. `Box<T>` is a single-owner heap value (recursive types, `Box<dyn Trait>`). `Rc<T>` shares ownership on one thread, `Arc<T>` does it across threads. Shared means read-only, so for mutation wrap the value in `RefCell` (borrow rules checked at runtime, panics on violation, single thread) or `Mutex` (blocks, thread-safe). Common pairs: `Rc<RefCell<T>>` and `Arc<Mutex<T>>`. Reach for them last; plain ownership and `&mut` solve most problems.

```rust Box
enum List {
    Cons(i32, Box<List>),
    Nil,
}
let list = List::Cons(1, Box::new(List::Nil));
```

```rust Rc + RefCell
use std::{cell::RefCell, rc::Rc};
let shared = Rc::new(RefCell::new(vec![1]));
let other = Rc::clone(&shared);
other.borrow_mut().push(2);
println!("{:?}", shared.borrow());
// => [1, 2]
```

```rust Arc + Mutex
use std::sync::{Arc, Mutex};
let n = Arc::new(Mutex::new(0));
let n2 = Arc::clone(&n);
std::thread::spawn(move || *n2.lock().unwrap() += 1)
    .join()
    .unwrap();
println!("{}", n.lock().unwrap());
// => 1
```

## modules & visibility

Python makes every file a module implicitly; Rust makes you declare it. `mod config;` in `main.rs` pulls in `src/config.rs`, and a file no `mod` mentions is not compiled. Everything is private by default (the opposite of Python's convention); `pub` exports, `pub(crate)` limits to the crate. `use` brings names into scope, with paths rooted at `crate::`, `self::` or `super::`. `src/net.rs` containing `pub mod client;` pulls in `src/net/client.rs`.

```text
src/
  main.rs
  config.rs
  net.rs
  net/client.rs
```

```rust main.rs
mod config;
mod net;
use config::Config;
use net::client::fetch;
fn main() {
    let cfg = Config::load();
    fetch(cfg.port);
}
```

```rust config.rs
pub struct Config {
    pub port: u16,
    secret: String,
}
impl Config {
    pub fn load() -> Self {
        Self { port: 8080, secret: String::new() }
    }
}
```

## serde

`serde` derives (de)serialization at compile time, like a pydantic model with the schema baked into the type. Bad input is an `Err`, not a half-built object. `serde_json::Value` is the untyped escape hatch, similar to a plain `dict`.

```sh
cargo add serde --features derive
cargo add serde_json
```

```rust
use serde::{Deserialize, Serialize};
#[derive(Serialize, Deserialize, Debug)]
struct User {
    name: String,
    #[serde(default)]
    age: u8,
    #[serde(rename = "isAdmin")]
    is_admin: bool,
}
```

```rust
let json = r#"{"name":"ann","isAdmin":true}"#;
let user: User = serde_json::from_str(json)?;
let back = serde_json::to_string(&user)?;
println!("{back}");
// => {"name":"ann","age":0,"isAdmin":true}
```

## clap

`clap` with `derive` is argparse driven by a struct: field types do the parsing, and `--help` and `--version` are generated. Subcommands are a `#[derive(Subcommand)]` enum.

```sh
cargo add clap --features derive
cargo run -- notes.txt --count 3
# => notes.txt x3
```

```rust
use clap::Parser;
#[derive(Parser)]
#[command(version, about)]
struct Args {
    path: String,
    #[arg(short, long, default_value_t = 1)]
    count: u32,
    #[arg(short, long)]
    verbose: bool,
}
fn main() {
    let args = Args::parse();
    println!("{} x{}", args.path, args.count);
}
```

## async with tokio

Rust has `async`/`await` but no built-in event loop; `tokio` supplies one. Futures are lazy and do nothing until awaited or spawned. You do not need async for CLIs, scripts, or CPU-bound work: use plain functions, `std::thread` or `rayon`. Reach for it when handling many concurrent network connections. Never block inside async code; wrap blocking calls in `tokio::task::spawn_blocking`.

| asyncio               | tokio                |
| --------------------- | -------------------- |
| `asyncio.run(main())` | `#[tokio::main]`     |
| `asyncio.create_task` | `tokio::spawn`       |
| `asyncio.gather`      | `tokio::join!`       |
| `asyncio.sleep`       | `tokio::time::sleep` |

```sh
cargo add tokio --features full
```

```rust
use tokio::time::{Duration, sleep};
#[tokio::main]
async fn main() {
    let task = tokio::spawn(async {
        sleep(Duration::from_millis(50)).await;
        7
    });
    let (a, b) = tokio::join!(async { 1 }, async { 2 });
    let c = task.await.unwrap();
    println!("{}", a + b + c);
    // => 10
}
```

## testing

Unit tests sit next to the code in a `#[cfg(test)]` module, which is compiled only under `cargo test`. Files in `tests/` are integration tests that see only the public API. Fenced code blocks inside `///` doc comments are compiled and run as doc tests, so examples cannot go stale. There are no fixtures; `assert!`, `assert_eq!` and `assert_ne!` replace pytest's bare `assert`.

```rust
pub fn add(a: i32, b: i32) -> i32 { a + b }

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds() {
        assert_eq!(add(2, 2), 4);
    }
}
```

```sh
cargo test
cargo test adds
cargo test -- --nocapture
```

## reading compiler errors

Read the first line (error code and what), then the `^^^` span (where it fails), then the `-` labels (the earlier cause, such as where the value moved), then `help:`. Fix the first error only; later ones often cascade. `rust-analyzer` shows these inline in your editor, `cargo check` is the fast way to see them all, and `cargo clippy` adds suggestions such as replacing index loops with iterators or dropping a needless `.clone()`.

```text
error[E0382]: borrow of moved value: `a`
 --> src/main.rs:4:16
  |
2 |     let a = vec![1, 2, 3];
  |         - move occurs because `a` has type `Vec<i32>`, which does not implement the `Copy` trait
3 |     let b = a;
  |             - value moved here
4 |     println!("{a:?}");
  |               ^^^^^ value borrowed here after move
  |
  = help: consider cloning the value if the performance cost is acceptable
```

```sh
rustc --explain E0382
cargo check
cargo clippy
cargo clippy --fix
```

| Code  | Meaning                     | Usual fix                                   |
| ----- | --------------------------- | ------------------------------------------- |
| E0382 | use after move              | borrow with `&`, or `.clone()`              |
| E0502 | `&mut` while a `&` is alive | shorten the borrow, copy the value out      |
| E0499 | two `&mut` at once          | split the work, or restructure              |
| E0106 | missing lifetime            | add `<'a>`, or return an owned value        |
| E0308 | mismatched types            | convert with `as`, `into()`, `.to_string()` |

## crates worth knowing

```sh
cargo add tokio --features full
cargo add reqwest axum anyhow thiserror tracing rayon itertools
```

| Purpose             | Crate                                                | Python analogue               |
| ------------------- | ---------------------------------------------------- | ----------------------------- |
| (De)serialization   | `serde`, `serde_json`                                | pydantic, `json`              |
| Async runtime       | `tokio`                                              | `asyncio`                     |
| HTTP client         | `reqwest`                                            | `httpx`, `requests`           |
| Web server          | `axum`                                               | FastAPI                       |
| CLI args            | `clap`                                               | argparse, typer               |
| Errors in apps      | `anyhow`                                             | plain exceptions              |
| Errors in libraries | `thiserror`                                          | custom exception classes      |
| Logging and tracing | `tracing`                                            | `logging`                     |
| Data parallelism    | `rayon`                                              | `multiprocessing.Pool`        |
| Iterator extras     | `itertools`                                          | `itertools`, `more-itertools` |
| SQL                 | `sqlx` (async, checked queries), `rusqlite` (SQLite) | SQLAlchemy, `sqlite3`         |
