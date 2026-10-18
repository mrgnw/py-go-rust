# Side by side

The same pattern in Python 3.15, Rust (2024 edition) and Go 1.25. Rust fragments run inside a `main` that returns `Result` (so `?` works); Go fragments run inside `main` or sit at top level, with the stdlib imports they use. Crates used: `serde`, `serde_json`, `reqwest`, `tokio`, `chrono`.

## Print & string formatting

```python
name, n = 'Ada', 3.14159
print(f'{name} has {n:.2f}')  # => Ada has 3.14
print(f'{n:>8.1f}|{42:05d}|{255:#x}')  # =>      3.1|00042|0xff
```

```rust
let (name, n) = ("Ada", 3.14159);
println!("{name} has {n:.2}"); // => Ada has 3.14
println!("{n:>8.1}|{:05}|{:#x}", 42, 255); // =>      3.1|00042|0xff
```

```go
name, n := "Ada", 3.14159
fmt.Printf("%s has %.2f\n", name, n) // => Ada has 3.14
fmt.Printf("%8.1f|%05d|%#x\n", n, 42, 255) // =>      3.1|00042|0xff
```

Go's `Println` and `Sprintf("%v")` print any value; Rust needs `{:?}` (Debug) for non-Display types.

```python
print(f'{name!r}')  # => 'Ada'
```

```rust
println!("{name:?}"); // => "Ada"
```

```go
fmt.Printf("%q\n", name) // => "Ada"
```

## Variables & constants

```python
count = 1
total = 0
total += count
total *= 2
MAX_RETRIES = 3
print(total, MAX_RETRIES)  # => 2 3
```

```rust
let count = 1;
let mut total = 0;
total += count;
let total = total * 2;
const MAX_RETRIES: u32 = 3;
println!("{total} {MAX_RETRIES}"); // => 2 3
```

```go
count := 1
total := 0
total += count
total *= 2
const MaxRetries = 3
var zero int
fmt.Println(total, MaxRetries, zero) // => 2 3 0
```

Rust bindings are immutable unless `mut`; a second `let` shadows. Go has `:=` only inside functions and rejects unused variables. Python has no real constants.

## Basic types & conversion

```python
n = int('42')
f = n / 5
s = str(n)
x = int(3.9)
print(f, s, x, bool(0))  # => 8.4 42 3 False
```

```rust
let n: i32 = "42".parse().unwrap();
let f = n as f64 / 5.0;
let s = n.to_string();
let x = 3.9_f64 as i32;
println!("{f} {s} {x} {}", n != 0); // => 8.4 42 3 true
println!("{:?}", u8::try_from(300_i32).is_err()); // => true
```

```go
n, _ := strconv.Atoi("42")
f := float64(n) / 5
s := strconv.Itoa(n)
v := 3.9
x := int(v)
fmt.Println(f, s, x, n != 0) // => 8.4 42 3 true
```

Neither Rust nor Go converts numbers implicitly. Rust `as` truncates and wraps silently; use `try_from` to detect overflow.

## Strings

```python
s = 'hello, world'
print(s[:5])  # => hello
print(s.split(', '))  # => ['hello', 'world']
print('-'.join(['a', 'b']))  # => a-b
print('world' in s, s.upper())  # => True HELLO, WORLD
```

```rust
let s = "hello, world";
println!("{}", &s[..5]); // => hello
println!("{:?}", s.split(", ").collect::<Vec<_>>()); // => ["hello", "world"]
println!("{}", ["a", "b"].join("-")); // => a-b
println!("{} {}", s.contains("world"), s.to_uppercase()); // => true HELLO, WORLD
```

```go
s := "hello, world"
fmt.Println(s[:5]) // => hello
fmt.Println(strings.Split(s, ", ")) // => [hello world]
fmt.Println(strings.Join([]string{"a", "b"}, "-")) // => a-b
fmt.Println(strings.Contains(s, "world"), strings.ToUpper(s)) // => true HELLO, WORLD
```

Python slices by code point. Rust and Go slice by byte; Rust panics if the cut is inside a multi-byte character.

## Lists / Vec / slices

```python
xs = [1, 2, 3]
xs.append(4)
print(xs[0], xs[-1], xs[1:3], len(xs))  # => 1 4 [2, 3] 4
xs.pop()
print(xs)  # => [1, 2, 3]
```

```rust
let mut xs = vec![1, 2, 3];
xs.push(4);
println!("{} {:?} {:?} {}", xs[0], xs.last(), &xs[1..3], xs.len()); // => 1 Some(4) [2, 3] 4
xs.pop();
println!("{xs:?}"); // => [1, 2, 3]
```

```go
xs := []int{1, 2, 3}
xs = append(xs, 4)
fmt.Println(xs[0], xs[len(xs)-1], xs[1:3], len(xs)) // => 1 4 [2 3] 4
xs = xs[:len(xs)-1]
fmt.Println(xs) // => [1 2 3]
```

Go has no negative indexes and `append` returns the slice; always reassign it.

## Dicts / HashMap / map

```python
ages = {'ann': 30, 'bob': 25}
ages['cy'] = 41
print(ages.get('dan', 0))  # => 0
for k, v in ages.items():
	print(k, v)
print('ann' in ages)  # => True
del ages['bob']
```

```rust
use std::collections::HashMap;
let mut ages = HashMap::from([("ann", 30), ("bob", 25)]);
ages.insert("cy", 41);
println!("{}", ages.get("dan").copied().unwrap_or(0)); // => 0
for (k, v) in &ages {
    println!("{k} {v}");
}
println!("{}", ages.contains_key("ann")); // => true
ages.remove("bob");
```

```go
ages := map[string]int{"ann": 30, "bob": 25}
ages["cy"] = 41
fmt.Println(ages["dan"]) // => 0
for k, v := range ages {
	fmt.Println(k, v)
}
_, ok := ages["ann"]
fmt.Println(ok) // => true
delete(ages, "bob")
```

Python keeps insertion order. Rust `HashMap` and Go `map` iterate in arbitrary order (Go randomizes on purpose). A missing Go key returns the zero value; use `v, ok := m[k]` to tell.

## Sets

```python
a, b = {1, 2, 3}, {2, 3, 4}
a.add(5)
print(2 in a)  # => True
print(a & b)  # => {2, 3}
print(a | b)  # => {1, 2, 3, 4, 5}
print(a - b)  # => {1, 5}
```

```rust
use std::collections::HashSet;
let mut a = HashSet::from([1, 2, 3]);
let b = HashSet::from([2, 3, 4]);
a.insert(5);
println!("{}", a.contains(&2)); // => true
println!("{}", (&a & &b).len()); // => 2
println!("{}", (&a | &b).len()); // => 5
println!("{}", (&a - &b).len()); // => 2
```

```go
a := map[int]struct{}{1: {}, 2: {}, 3: {}}
b := map[int]struct{}{2: {}, 3: {}, 4: {}}
a[5] = struct{}{}
_, ok := a[2]
fmt.Println(ok) // => true
var both []int
for k := range a {
	if _, in := b[k]; in {
		both = append(both, k)
	}
}
slices.Sort(both)
fmt.Println(both) // => [2 3]
```

Go has no set type or set operators; `map[T]struct{}` is the idiom. Sets print in arbitrary order in Rust and Go, so sort before comparing.

## Tuples & destructuring

```python
point = (3, 4)
x, y = point
first, *rest = [1, 2, 3]
x, y = y, x
print(x, y, first, rest)  # => 4 3 1 [2, 3]
```

```rust
let point = (3, 4);
let (mut x, mut y) = point;
let [first, rest @ ..] = [1, 2, 3];
(x, y) = (y, x);
println!("{x} {y} {first} {rest:?}"); // => 4 3 1 [2, 3]
```

```go
x, y := 3, 4
xs := []int{1, 2, 3}
first, rest := xs[0], xs[1:]
x, y = y, x
fmt.Println(x, y, first, rest) // => 4 3 1 [2 3]
```

Go has no tuple type. Return several values or use a struct.

## None / Option / nil

```python
nick: str | None = None
name = 'anon' if nick is None else nick
print(name)  # => anon
print(nick and nick.upper())  # => None
```

```rust
let nick: Option<&str> = None;
let name = nick.unwrap_or("anon");
println!("{name}"); // => anon
println!("{:?}", nick.map(str::to_uppercase)); // => None
if let Some(n) = nick {
    println!("{n}");
}
```

```go
var nick *string
name := "anon"
if nick != nil {
	name = *nick
}
fmt.Println(name, nick == nil) // => anon true
```

Rust has no null: absence is `Option` and the compiler forces you to handle it. Go uses `nil` pointers, or `(value, ok)` returns. An interface holding a nil pointer is not `== nil`.

## If-else & ternary-ish

```python
n = 15
label = 'big' if n > 10 else 'small'
if n < 0:
	sign = '-'
elif n == 0:
	sign = '0'
else:
	sign = '+'
print(label, sign)  # => big +
```

```rust
let n = 15;
let label = if n > 10 { "big" } else { "small" };
let sign = if n < 0 {
    "-"
} else if n == 0 {
    "0"
} else {
    "+"
};
println!("{label} {sign}"); // => big +
```

```go
n := 15
label := "small"
if n > 10 {
	label = "big"
}
var sign string
switch {
case n < 0:
	sign = "-"
case n == 0:
	sign = "0"
default:
	sign = "+"
}
fmt.Println(label, sign) // => big +
```

In Rust `if` is an expression, so it is the ternary. Go has no ternary; a tagless `switch` replaces `elif` chains.

## Loops

```python
for i in range(3):
	print(i)
for i, x in enumerate(['a', 'b']):
	print(i, x)
n = 3
while n > 0:
	n -= 1
```

```rust
for i in 0..3 {
    println!("{i}");
}
for (i, x) in ["a", "b"].iter().enumerate() {
    println!("{i} {x}");
}
let mut n = 3;
while n > 0 {
    n -= 1;
}
```

```go
for i := range 3 {
	fmt.Println(i)
}
for i, x := range []string{"a", "b"} {
	fmt.Println(i, x)
}
n := 3
for n > 0 {
	n--
}
```

Go has only `for` (`for {}` is infinite). Rust's infinite loop is `loop {}` and `break` can return a value.

## Functions & multiple returns

```python
def div(a, b=1):
	return a // b, a % b

q, r = div(7, 2)
print(q, r)  # => 3 1
```

```rust
fn div(a: i32, b: i32) -> (i32, i32) {
    (a / b, a % b)
}

let (q, r) = div(7, 2);
println!("{q} {r}"); // => 3 1
```

```go
func div(a, b int) (int, int) {
	return a / b, a % b
}

func main() {
	q, r := div(7, 2)
	fmt.Println(q, r) // => 3 1
}
```

Rust and Go have no default or keyword arguments; use a struct of options. Go also has variadics (`xs ...int`) and named results.

## Closures / lambdas

```python
add = lambda a, b: a + b

def counter():
	n = 0
	def inc():
		nonlocal n
		n += 1
		return n
	return inc

c = counter()
c()
print(add(1, 2), c())  # => 3 2
```

```rust
let add = |a: i32, b: i32| a + b;
let mut n = 0;
let mut inc = || {
    n += 1;
    n
};
inc();
println!("{} {}", add(1, 2), inc()); // => 3 2
```

```go
add := func(a, b int) int { return a + b }
n := 0
inc := func() int {
	n++
	return n
}
inc()
fmt.Println(add(1, 2), inc()) // => 3 2
```

Python lambdas hold one expression; use `def` for more. A Rust closure that mutates captured state must be bound `mut`.

## Structs / classes & constructors

```python
from dataclasses import dataclass

@dataclass
class User:
	name: str
	age: int = 0

u = User('ann')
print(u)  # => User(name='ann', age=0)
```

```rust
#[derive(Debug)]
struct User {
    name: String,
    age: u32,
}

impl User {
    fn new(name: &str) -> Self {
        Self { name: name.to_string(), age: 0 }
    }
}

let u = User::new("ann");
println!("{u:?}"); // => User { name: "ann", age: 0 }
```

```go
type User struct {
	Name string
	Age  int
}

func NewUser(name string) User {
	return User{Name: name}
}

func main() {
	fmt.Printf("%+v\n", NewUser("ann")) // => {Name:ann Age:0}
}
```

Rust and Go have no constructors; `new` / `NewX` are conventions. Unset Go fields take their zero value. Capitalized Go names are exported.

## Methods

```python
class Rect:
	def __init__(self, w, h):
		self.w, self.h = w, h
	def area(self):
		return self.w * self.h
	def scale(self, k):
		self.w *= k
		self.h *= k
r = Rect(2, 3)
r.scale(2)
print(r.area())  # => 24
```

```rust
struct Rect { w: f64, h: f64 }

impl Rect {
    fn area(&self) -> f64 { self.w * self.h }
    fn scale(&mut self, k: f64) { self.w *= k; self.h *= k; }
}

let mut r = Rect { w: 2.0, h: 3.0 };
r.scale(2.0);
println!("{}", r.area()); // => 24
```

```go
type Rect struct{ W, H float64 }

func (r Rect) Area() float64 { return r.W * r.H }

func (r *Rect) Scale(k float64) {
	r.W *= k
	r.H *= k
}

func main() {
	r := Rect{2, 3}
	r.Scale(2)
	fmt.Println(r.Area()) // => 24
}
```

Rust makes mutation explicit in the signature (`&mut self`). In Go a value receiver works on a copy; use a pointer receiver to mutate.

## Interfaces / traits / Protocols

```python
from typing import Protocol
class Shape(Protocol):
	def area(self) -> float: ...
class Square:
	def __init__(self, s):
		self.s = s
	def area(self):
		return self.s ** 2
def describe(shape: Shape):
	print(shape.area())
describe(Square(3))  # => 9
```

```rust
trait Shape { fn area(&self) -> f64; }

struct Square(f64);

impl Shape for Square {
    fn area(&self) -> f64 { self.0 * self.0 }
}

fn describe(shape: &dyn Shape) { println!("{}", shape.area()); }

describe(&Square(3.0)); // => 9
```

```go
type Shape interface{ Area() float64 }

type Square struct{ S float64 }

func (s Square) Area() float64 { return s.S * s.S }

func describe(shape Shape) { fmt.Println(shape.Area()) }

func main() {
	describe(Square{3}) // => 9
}
```

Protocols and Go interfaces are structural: no declaration of intent. Rust needs an explicit `impl Trait for Type`, and `&dyn Shape` is dynamic dispatch (`impl Shape` is static).

## Enums & match / switch

```python
from dataclasses import dataclass
@dataclass
class Circle:
	r: float
@dataclass
class Rect:
	w: float
	h: float
def area(s):
	match s:
		case Circle(r):
			return 3.14 * r * r
		case Rect(w, h):
			return w * h
print(area(Rect(2, 3)))  # => 6
```

```rust
enum Shape {
    Circle(f64),
    Rect { w: f64, h: f64 },
}

fn area(s: &Shape) -> f64 {
    match s {
        Shape::Circle(r) => 3.14 * r * r,
        Shape::Rect { w, h } => w * h,
    }
}

println!("{}", area(&Shape::Rect { w: 2.0, h: 3.0 })); // => 6
```

```go
type Circle struct{ R float64 }
type Rect struct{ W, H float64 }
func area(s any) float64 {
	switch s := s.(type) {
	case Circle:
		return 3.14 * s.R * s.R
	case Rect:
		return s.W * s.H
	}
	return 0
}
func main() {
	fmt.Println(area(Rect{2, 3})) // => 6
}
```

Rust's `match` must cover every variant or it will not compile. Go has no sum types: a type switch is the closest, and plain enums are `const ( A = iota; B )`.

## Error handling

```python
def parse_port(s):
	try:
		return int(s)
	except ValueError as e:
		raise RuntimeError(f'bad port {s!r}') from e

try:
	parse_port('x')
except RuntimeError as e:
	print(e)  # => bad port 'x'
```

```rust
use std::error::Error;

fn parse_port(s: &str) -> Result<u16, Box<dyn Error>> {
    let n = s.parse::<u16>().map_err(|e| format!("bad port {s:?}: {e}"))?;
    Ok(n)
}

if let Err(e) = parse_port("x") {
    println!("{e}"); // => bad port "x": invalid digit found in string
}
```

```go
func parsePort(s string) (int, error) {
	n, err := strconv.Atoi(s)
	if err != nil {
		return 0, fmt.Errorf("bad port %q: %w", s, err)
	}
	return n, nil
}

func main() {
	if _, err := parsePort("x"); err != nil {
		fmt.Println(err) // => bad port "x": strconv.Atoi: parsing "x": invalid syntax
	}
}
```

Errors are values in Rust and Go: `?` returns early on `Err`, `if err != nil` is the Go spelling. `%w` keeps the cause for `errors.Is` / `errors.As`. For real Rust code reach for `anyhow` (apps) or `thiserror` (libraries).

## Iterators & comprehensions

```python
xs = [1, 2, 3, 4]
squares = [x * x for x in xs if x % 2 == 0]
total = sum(x * x for x in xs)
print(squares, total)  # => [4, 16] 30
```

```rust
let xs = [1, 2, 3, 4];
let squares: Vec<i32> = xs.iter().filter(|&&x| x % 2 == 0).map(|x| x * x).collect();
let total: i32 = xs.iter().map(|x| x * x).sum();
println!("{squares:?} {total}"); // => [4, 16] 30
```

```go
xs := []int{1, 2, 3, 4}
var squares []int
total := 0
for _, x := range xs {
	total += x * x
	if x%2 == 0 {
		squares = append(squares, x*x)
	}
}
fmt.Println(squares, total) // => [4 16] 30
```

Rust iterator chains are lazy until `collect` or `sum`. Go has no `map` / `filter`; write the loop (iterators exist via `iter.Seq`, but the stdlib offers no adapters).

## Sorting

```python
words = ['pear', 'fig', 'apple', 'kiwi']
print(sorted(words, key=len))  # => ['fig', 'pear', 'kiwi', 'apple']
words.sort()
print(words)  # => ['apple', 'fig', 'kiwi', 'pear']
```

```rust
let mut words = vec!["pear", "fig", "apple", "kiwi"];
words.sort_by_key(|w| w.len());
println!("{words:?}"); // => ["fig", "pear", "kiwi", "apple"]
words.sort();
println!("{words:?}"); // => ["apple", "fig", "kiwi", "pear"]
```

```go
words := []string{"pear", "fig", "apple", "kiwi"}
slices.SortStableFunc(words, func(a, b string) int {
	return cmp.Compare(len(a), len(b))
})
fmt.Println(words) // => [fig pear kiwi apple]
slices.Sort(words)
fmt.Println(words) // => [apple fig kiwi pear]
```

All three sort in place here. Python's `sorted` and Rust's `sort_by_key` are stable; Go's `SortFunc` is not, so use `SortStableFunc` when ties matter. Floats are not `Ord` in Rust: use `sort_by(|a, b| a.total_cmp(b))`.

## Mutable vs immutable & copying

```python
a = [1, 2]
b = a
b.append(3)
print(a)  # => [1, 2, 3]
c = a.copy()
c.append(4)
print(a, c)  # => [1, 2, 3] [1, 2, 3, 4]
```

```rust
let mut a = vec![1, 2];
let b = &mut a;
b.push(3);
println!("{a:?}"); // => [1, 2, 3]
let mut c = a.clone();
c.push(4);
println!("{a:?} {c:?}"); // => [1, 2, 3] [1, 2, 3, 4]
```

```go
a := []int{1, 2}
b := a
b[0] = 9
fmt.Println(a) // => [9 2]
c := slices.Clone(a)
c[0] = 7
fmt.Println(a, c) // => [9 2] [7 2]
```

Python names are references. Rust assignment moves (the old name is dead) and `&mut` borrows exclusively. Go slices share a backing array, so `b := a` aliases; arrays and structs are copied by value. `copy.deepcopy` / `.clone()` on nested data copy deeply, `slices.Clone` does not.

## File read & write

```python
from pathlib import Path

path = Path('notes.txt')
path.write_text('one\ntwo\n')
text = path.read_text()
for line in text.splitlines():
	print(line)
```

```rust
use std::fs;

let path = "notes.txt";
fs::write(path, "one\ntwo\n")?;
let text = fs::read_to_string(path)?;
for line in text.lines() {
    println!("{line}");
}
```

```go
path := "notes.txt"
if err := os.WriteFile(path, []byte("one\ntwo\n"), 0o644); err != nil {
	log.Fatal(err)
}
data, err := os.ReadFile(path)
if err != nil {
	log.Fatal(err)
}
for _, line := range strings.Split(strings.TrimSpace(string(data)), "\n") {
	fmt.Println(line)
}
```

For big files stream instead: `open()` iteration, `BufReader::lines`, `bufio.Scanner`.

## JSON encode/decode to a struct

```python
import json
from dataclasses import dataclass, asdict

@dataclass
class User:
	name: str
	age: int

raw = '{"name": "ann", "age": 30}'
user = User(**json.loads(raw))
print(json.dumps(asdict(user)))  # => {"name": "ann", "age": 30}
```

```rust
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct User {
    name: String,
    age: u32,
}

let raw = r#"{"name": "ann", "age": 30}"#;
let user: User = serde_json::from_str(raw)?;
println!("{}", serde_json::to_string(&user)?); // => {"name":"ann","age":30}
```

```go
type User struct {
	Name string `json:"name"`
	Age  int    `json:"age"`
}

raw := `{"name": "ann", "age": 30}`
var user User
if err := json.Unmarshal([]byte(raw), &user); err != nil {
	log.Fatal(err)
}
out, _ := json.Marshal(user)
fmt.Println(string(out)) // => {"name":"ann","age":30}
```

Python's dataclass does no validation: `User(**d)` will not check types. serde and Go reject mismatched types. Go only sees exported (capitalized) fields, so the tags map them to lowercase keys.

## HTTP GET

```python
import urllib.request

url = 'https://example.com'
with urllib.request.urlopen(url, timeout=10) as resp:
	status = resp.status
	body = resp.read().decode()
print(status, len(body) > 0)  # => 200 True
```

```rust
let url = "https://example.com";
let resp = reqwest::get(url).await?.error_for_status()?;
let status = resp.status().as_u16();
let body = resp.text().await?;
println!("{status} {}", !body.is_empty()); // => 200 true
```

```go
url := "https://example.com"
resp, err := http.Get(url)
if err != nil {
	log.Fatal(err)
}
defer resp.Body.Close()
body, err := io.ReadAll(resp.Body)
if err != nil {
	log.Fatal(err)
}
fmt.Println(resp.StatusCode, len(body) > 0) // => 200 true
```

`urlopen` raises on 4xx/5xx, and `error_for_status` does the same in reqwest. Go's `http.Get` does not: check `StatusCode` yourself, and always close the body. `http.Get` has no timeout; use an `http.Client{Timeout: ...}` in real code.

## Concurrency: run tasks in parallel

```python
import asyncio

async def fetch(n):
	await asyncio.sleep(0.1)
	return n * 2

async def main():
	print(await asyncio.gather(fetch(1), fetch(2)))  # => [2, 4]

asyncio.run(main())
```

```rust
use std::time::Duration;
use tokio::time::sleep;

async fn fetch(n: u64) -> u64 {
    sleep(Duration::from_millis(100)).await;
    n * 2
}

let (a, b) = tokio::join!(fetch(1), fetch(2));
println!("{a} {b}"); // => 2 4
```

```go
var wg sync.WaitGroup
out := make([]int, 2)
for i := range out {
	wg.Go(func() {
		time.Sleep(100 * time.Millisecond)
		out[i] = (i + 1) * 2
	})
}
wg.Wait()
fmt.Println(out) // => [2 4]
```

Rust futures do nothing until awaited, and `#[tokio::main]` supplies the runtime. Python's `asyncio` is single-threaded; goroutines and tokio tasks run on a thread pool. `wg.Go` is new in Go 1.25; before that it was `wg.Add(1)` plus `go func() { defer wg.Done() ... }()`.

## Channels & queues

```python
import queue
import threading

q = queue.Queue()

def producer():
	for i in range(3):
		q.put(i * i)
	q.put(None)

threading.Thread(target=producer).start()
while (x := q.get()) is not None:
	print(x)
```

```rust
use std::{sync::mpsc, thread};

let (tx, rx) = mpsc::channel();
thread::spawn(move || {
    for i in 0..3 {
        tx.send(i * i).unwrap();
    }
});
for x in rx {
    println!("{x}");
}
```

```go
ch := make(chan int)
go func() {
	defer close(ch)
	for i := range 3 {
		ch <- i * i
	}
}()
for x := range ch {
	fmt.Println(x)
}
```

The Rust loop ends when every sender is dropped; the Go loop ends when the sender closes the channel. Python needs a sentinel (`None`). `make(chan int, 10)` buffers; unbuffered sends block until received.

## Shared state

```python
import threading
count = 0
lock = threading.Lock()
def work():
	global count
	for _ in range(1000):
		with lock:
			count += 1
threads = [threading.Thread(target=work) for _ in range(4)]
for t in threads:
	t.start()
for t in threads:
	t.join()
print(count)  # => 4000
```

```rust
use std::{sync::{Arc, Mutex}, thread};

let count = Arc::new(Mutex::new(0));
let handles: Vec<_> = (0..4).map(|_| {
    let count = Arc::clone(&count);
    thread::spawn(move || {
        for _ in 0..1000 { *count.lock().unwrap() += 1; }
    })
}).collect();
for h in handles { h.join().unwrap(); }
println!("{}", count.lock().unwrap()); // => 4000
```

```go
var mu sync.Mutex
var wg sync.WaitGroup
count := 0
for range 4 {
	wg.Go(func() {
		for range 1000 {
			mu.Lock()
			count++
			mu.Unlock()
		}
	})
}
wg.Wait()
fmt.Println(count) // => 4000
```

In Rust the lock owns the data, so you cannot touch it unlocked; `Arc` shares ownership across threads. Go's mutex sits beside the data by convention only; `go test -race` finds misses.

## Modules & imports

```python
import math
from math import sqrt as root

print(math.pi, root(16))  # => 3.141592653589793 4.0
```

```rust
use std::f64::consts::PI;

mod geometry {
    pub fn sqrt(x: f64) -> f64 {
        x.sqrt()
    }
}
use geometry::sqrt;

println!("{PI} {}", sqrt(16.0)); // => 3.141592653589793 4
```

```go
import (
	"fmt"
	m "math"
)

func main() {
	fmt.Println(m.Pi, m.Sqrt(16)) // => 3.141592653589793 4
}
```

Python: one file is one module. Rust: `mod geometry;` loads `geometry.rs`, items are private unless `pub`, dependencies live in `Cargo.toml`. Go: one directory is one package, capitalized names are exported, and the module path comes from `go.mod`.

## CLI args

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('--count', type=int, default=1)
args = parser.parse_args()
for _ in range(args.count):
	print(f'hi {args.name}')
```

```rust
let mut args = std::env::args().skip(1);
let name = args.next().unwrap_or_else(|| "world".to_string());
let count: usize = args.next().and_then(|s| s.parse().ok()).unwrap_or(1);
for _ in 0..count {
    println!("hi {name}");
}
```

```go
count := flag.Int("count", 1, "repeat count")
flag.Parse()
name := flag.Arg(0)
for range *count {
	fmt.Println("hi", name)
}
```

Rust's stdlib only gives raw arguments (here positional, name then count); `clap` is the `argparse` equivalent. Go's `flag` stops at the first positional, so put flags first: `prog -count 2 ann`.

## Environment variables

```python
import os

port = os.environ.get('PORT', '8080')
home = os.environ['HOME']
print(port)  # => 8080
```

```rust
use std::env;

let port = env::var("PORT").unwrap_or_else(|_| "8080".to_string());
let home = env::var("HOME")?;
println!("{port} {}", !home.is_empty()); // => 8080 true
```

```go
port := os.Getenv("PORT")
if port == "" {
	port = "8080"
}
home, ok := os.LookupEnv("HOME")
fmt.Println(port, ok, home != "") // => 8080 true true
```

`os.environ['HOME']` raises `KeyError`; `env::var` returns `Err`. Go's `Getenv` returns an empty string for unset, so use `LookupEnv` when empty is meaningful.

## Tests

```python
def add(a, b):
	return a + b

def test_add():
	assert add(1, 2) == 3
```

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds() {
        assert_eq!(add(1, 2), 3);
    }
}
```

```go
func Add(a, b int) int { return a + b }

func TestAdd(t *testing.T) {
	if got := Add(1, 2); got != 3 {
		t.Errorf("Add(1, 2) = %d, want 3", got)
	}
}
```

Run with `pytest` (stdlib alternative: `unittest`), `cargo test`, `go test ./...`. Rust unit tests sit in the same file; Go tests live in `*_test.go` next to the code, and `Test*` functions take `*testing.T`.

## Dates & time

```python
from datetime import UTC, datetime, timedelta

d = datetime(2026, 1, 2, 15, 4, tzinfo=UTC)
print(d + timedelta(days=1))  # => 2026-01-03 15:04:00+00:00
print(d.strftime('%Y-%m-%d'))  # => 2026-01-02
parsed = datetime.fromisoformat('2026-01-02T15:04:00+00:00')
print(parsed == d)  # => True
```

```rust
use chrono::{DateTime, Duration, TimeZone, Utc};

let d = Utc.with_ymd_and_hms(2026, 1, 2, 15, 4, 0).unwrap();
println!("{}", d + Duration::days(1)); // => 2026-01-03 15:04:00 UTC
println!("{}", d.format("%Y-%m-%d")); // => 2026-01-02
let parsed = DateTime::parse_from_rfc3339("2026-01-02T15:04:00+00:00")?;
println!("{}", parsed == d); // => true
```

```go
d := time.Date(2026, time.January, 2, 15, 4, 0, 0, time.UTC)
fmt.Println(d.Add(24 * time.Hour)) // => 2026-01-03 15:04:00 +0000 UTC
fmt.Println(d.Format("2006-01-02")) // => 2026-01-02
parsed, err := time.Parse(time.RFC3339, "2026-01-02T15:04:00+00:00")
if err != nil {
	log.Fatal(err)
}
fmt.Println(parsed.Equal(d)) // => true
```

Rust's stdlib has no calendar, so `chrono` (or `jiff`) is the default. Go formats with the reference time `Mon Jan 2 15:04:05 2006`, not `%Y`. `Add(24 * time.Hour)` is a fixed duration; `AddDate(0, 0, 1)` is calendar-aware.

## Generics

```python
def largest[T](xs: list[T]) -> T:
	return max(xs)

print(largest([1, 5, 3]), largest([1.5, 0.2]))  # => 5 1.5
```

```rust
fn largest<T: PartialOrd + Copy>(xs: &[T]) -> T {
    let mut m = xs[0];
    for &x in xs {
        if x > m {
            m = x;
        }
    }
    m
}

println!("{} {}", largest(&[1, 5, 3]), largest(&[1.5, 0.2])); // => 5 1.5
```

```go
func Largest[T cmp.Ordered](xs []T) T {
	m := xs[0]
	for _, x := range xs {
		if x > m {
			m = x
		}
	}
	return m
}

func main() {
	fmt.Println(Largest([]int{1, 5, 3}), Largest([]float64{1.5, 0.2})) // => 5 1.5
}
```

Python's `[T]` is only a hint for type checkers. Rust and Go check the bound at compile time (`PartialOrd`, `cmp.Ordered`) and generate code per type.

## Decorators & wrappers

```python
import functools

def logged(fn):
	@functools.wraps(fn)
	def wrapper(*args):
		result = fn(*args)
		print(f'{fn.__name__}{args} = {result}')
		return result
	return wrapper

@logged
def add(a, b):
	return a + b

add(1, 2)  # => add(1, 2) = 3
```

```rust
fn logged<F: Fn(i32, i32) -> i32>(name: &str, f: F) -> impl Fn(i32, i32) -> i32 {
    let name = name.to_string();
    move |a, b| {
        let result = f(a, b);
        println!("{name}({a}, {b}) = {result}");
        result
    }
}

fn add(a: i32, b: i32) -> i32 {
    a + b
}

let add = logged("add", add);
add(1, 2); // => add(1, 2) = 3
```

```go
func logged(name string, f func(int, int) int) func(int, int) int {
	return func(a, b int) int {
		result := f(a, b)
		fmt.Printf("%s(%d, %d) = %d\n", name, a, b, result)
		return result
	}
}

func add(a, b int) int { return a + b }

func main() {
	add := logged("add", add)
	add(1, 2) // => add(1, 2) = 3
}
```

`@logged` is sugar for `add = logged(add)`. Rust and Go have no sugar: pass the function in, get a closure back, and bind it under the same name. Rust attributes like `#[test]` and `#[tokio::main]` are macros, not decorators; they rewrite the item at compile time. Go middleware wraps `http.Handler` exactly this way.

## with / Drop / defer

```python
class Resource:
	def __enter__(self):
		print('open')
		return self
	def __exit__(self, *exc):
		print('close')

with Resource():
	print('use')
```

```rust
struct Resource;

impl Resource {
    fn open() -> Self {
        println!("open");
        Resource
    }
}

impl Drop for Resource {
    fn drop(&mut self) {
        println!("close");
    }
}

{
    let _r = Resource::open();
    println!("use");
}
```

```go
type Resource struct{}

func Open() *Resource {
	fmt.Println("open")
	return &Resource{}
}

func (r *Resource) Close() { fmt.Println("close") }

func main() {
	r := Open()
	defer r.Close()
	fmt.Println("use")
}
```

All three print `open`, `use`, `close`. Python runs `__exit__` when the block ends, even on an exception. Rust runs `drop` when the owner goes out of scope, so there is nothing to forget; `let _r` keeps the value alive, `let _ =` drops it on the spot. Go's `defer` runs when the function returns, not when the block ends, so a loop that opens files should wrap its body in a function.

## Project & dependencies

```sh Python
uv init hello && cd hello
uv add httpx
uv run main.py
uv build
```

```sh Rust
cargo new hello && cd hello
cargo add reqwest --features blocking
cargo run
cargo build --release
```

```sh Go
mkdir hello && cd hello && go mod init example.com/hello
go get golang.org/x/sync
go run .
go build
```

The manifest each command writes:

```toml pyproject.toml
[project]
name = "hello"
version = "0.1.0"
requires-python = ">=3.15"
dependencies = ["httpx>=0.28.1"]
```

```toml Cargo.toml
[package]
name = "hello"
version = "0.1.0"
edition = "2024"

[dependencies]
reqwest = { version = "0.13.5", features = ["blocking"] }
```

```text go.mod
module example.com/hello

go 1.25

require golang.org/x/sync v0.24.0
```

All three pin exact versions in a lockfile next to the manifest: `uv.lock`, `Cargo.lock`, `go.sum`. `uv run` syncs the environment before running, so there is no activate step. Cargo and Go fetch on build. Go imports a package by URL path, and `go mod tidy` adds and removes `require` lines to match the imports.

## Format & lint

```sh Python
uvx ruff format
uvx ruff check --fix
```

```sh Rust
cargo fmt
cargo clippy
```

```sh Go
gofmt -w .
go vet ./...
```

Formatting is settled in all three: `gofmt` has no options, `rustfmt` and `ruff format` have a few. `ruff check` replaces flake8, isort and most pylint rules and fixes what it can. `clippy` ships with the toolchain and is strict by default. `go vet` catches the bugs the compiler lets through; `staticcheck` or `golangci-lint` add the rest.
