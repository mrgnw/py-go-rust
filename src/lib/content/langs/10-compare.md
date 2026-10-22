# Patterns

The same pattern in Python 3.15, Rust (2024 edition) and Go 1.25. Rust fragments run inside a `main` that returns `Result` (so `?` works); Go fragments run inside `main` or sit at top level, with the stdlib imports they use. Crates used: `serde`, `serde_json`, `reqwest`, `tokio`, `chrono`.

## Basics


### Print & string formatting

```python
# -- values
name, n = 'Ada', 3.14159
# -- format
print(f'{name} has {n:.2f}')  # => Ada has 3.14
# -- widths
print(f'{n:>8.1f}|{42:05d}|{255:#x}')  # =>      3.1|00042|0xff
```

```rust
// -- values
let (name, n) = ("Ada", 3.14159);
// -- format
println!("{name} has {n:.2}"); // => Ada has 3.14
// -- widths
println!("{n:>8.1}|{:05}|{:#x}", 42, 255); // =>      3.1|00042|0xff
```

```go
// -- values
name, n := "Ada", 3.14159
// -- format
fmt.Printf("%s has %.2f\n", name, n) // => Ada has 3.14
// -- widths
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


### Variables & constants

```python
# -- bind
count = 1
total = 0
# -- mutate
total += count
total *= 2
# -- constant
MAX_RETRIES = 3
# -- print
print(total, MAX_RETRIES)  # => 2 3
```

```rust
// -- bind
let count = 1;
let mut total = 0;
// -- mutate
total += count;
let total = total * 2;
// -- constant
const MAX_RETRIES: u32 = 3;
// -- print
println!("{total} {MAX_RETRIES}"); // => 2 3
```

```go
// -- bind
count := 1
total := 0
// -- mutate
total += count
total *= 2
// -- constant
const MaxRetries = 3
// -- print
var zero int
fmt.Println(total, MaxRetries, zero) // => 2 3 0
```

Rust bindings are immutable unless `mut`; a second `let` shadows. Go has `:=` only inside functions and rejects unused variables. Python has no real constants.


### Basic types & conversion

```python
# -- parse
n = int('42')
# -- divide
f = n / 5
# -- to string
s = str(n)
# -- truncate
x = int(3.9)
# -- print
print(f, s, x, bool(0))  # => 8.4 42 3 False
```

```rust
// -- parse
let n: i32 = "42".parse().unwrap();
// -- divide
let f = n as f64 / 5.0;
// -- to string
let s = n.to_string();
// -- truncate
let x = 3.9_f64 as i32;
// -- print
println!("{f} {s} {x} {}", n != 0); // => 8.4 42 3 true
println!("{:?}", u8::try_from(300_i32).is_err()); // => true
```

```go
// -- parse
n, _ := strconv.Atoi("42")
// -- divide
f := float64(n) / 5
// -- to string
s := strconv.Itoa(n)
// -- truncate
v := 3.9
x := int(v)
// -- print
fmt.Println(f, s, x, n != 0) // => 8.4 42 3 true
```

Neither Rust nor Go converts numbers implicitly. Rust `as` truncates and wraps silently; use `try_from` to detect overflow.


### Strings

```python
# -- value
s = 'hello, world'
# -- slice
print(s[:5])  # => hello
# -- split
print(s.split(', '))  # => ['hello', 'world']
# -- join
print('-'.join(['a', 'b']))  # => a-b
# -- search & case
print('world' in s, s.upper())  # => True HELLO, WORLD
```

```rust
// -- value
let s = "hello, world";
// -- slice
println!("{}", &s[..5]); // => hello
// -- split
println!("{:?}", s.split(", ").collect::<Vec<_>>()); // => ["hello", "world"]
// -- join
println!("{}", ["a", "b"].join("-")); // => a-b
// -- search & case
println!("{} {}", s.contains("world"), s.to_uppercase()); // => true HELLO, WORLD
```

```go
// -- value
s := "hello, world"
// -- slice
fmt.Println(s[:5]) // => hello
// -- split
fmt.Println(strings.Split(s, ", ")) // => [hello world]
// -- join
fmt.Println(strings.Join([]string{"a", "b"}, "-")) // => a-b
// -- search & case
fmt.Println(strings.Contains(s, "world"), strings.ToUpper(s)) // => true HELLO, WORLD
```

Python slices by code point. Rust and Go slice by byte; Rust panics if the cut is inside a multi-byte character.


### None / Option / nil

```python
# -- declare
nick: str | None = None
# -- default
name = 'anon' if nick is None else nick
# -- print
print(name)  # => anon
# -- when present
print(nick and nick.upper())  # => None
```

```rust
// -- declare
let nick: Option<&str> = None;
// -- default
let name = nick.unwrap_or("anon");
// -- print
println!("{name}"); // => anon
// -- when present
println!("{:?}", nick.map(str::to_uppercase)); // => None
if let Some(n) = nick {
    println!("{n}");
}
```

```go
// -- declare
var nick *string
// -- default
name := "anon"
if nick != nil {
	name = *nick
}
// -- print
fmt.Println(name, nick == nil) // => anon true
// -- when present
```

Rust has no null: absence is `Option` and the compiler forces you to handle it. Go uses `nil` pointers, or `(value, ok)` returns. An interface holding a nil pointer is not `== nil`.


## Collections


### Lists / Vec / slices

```python
# -- create
xs = [1, 2, 3]
# -- append
xs.append(4)
# -- index & slice
print(xs[0], xs[-1], xs[1:3], len(xs))  # => 1 4 [2, 3] 4
# -- pop
xs.pop()
print(xs)  # => [1, 2, 3]
```

```rust
// -- create
let mut xs = vec![1, 2, 3];
// -- append
xs.push(4);
// -- index & slice
println!("{} {:?} {:?} {}", xs[0], xs.last(), &xs[1..3], xs.len()); // => 1 Some(4) [2, 3] 4
// -- pop
xs.pop();
println!("{xs:?}"); // => [1, 2, 3]
```

```go
// -- create
xs := []int{1, 2, 3}
// -- append
xs = append(xs, 4)
// -- index & slice
fmt.Println(xs[0], xs[len(xs)-1], xs[1:3], len(xs)) // => 1 4 [2 3] 4
// -- pop
xs = xs[:len(xs)-1]
fmt.Println(xs) // => [1 2 3]
```

Go has no negative indexes and `append` returns the slice; always reassign it.


### Dicts / HashMap / map

```python
# -- create
ages = {'ann': 30, 'bob': 25}
# -- insert
ages['cy'] = 41
# -- get with default
print(ages.get('dan', 0))  # => 0
# -- iterate
for k, v in ages.items():
	print(k, v)
# -- contains
print('ann' in ages)  # => True
# -- delete
del ages['bob']
```

```rust
// -- create
use std::collections::HashMap;
let mut ages = HashMap::from([("ann", 30), ("bob", 25)]);
// -- insert
ages.insert("cy", 41);
// -- get with default
println!("{}", ages.get("dan").copied().unwrap_or(0)); // => 0
// -- iterate
for (k, v) in &ages {
    println!("{k} {v}");
}
// -- contains
println!("{}", ages.contains_key("ann")); // => true
// -- delete
ages.remove("bob");
```

```go
// -- create
ages := map[string]int{"ann": 30, "bob": 25}
// -- insert
ages["cy"] = 41
// -- get with default
fmt.Println(ages["dan"]) // => 0
// -- iterate
for k, v := range ages {
	fmt.Println(k, v)
}
// -- contains
_, ok := ages["ann"]
fmt.Println(ok) // => true
// -- delete
delete(ages, "bob")
```

Python keeps insertion order. Rust `HashMap` and Go `map` iterate in arbitrary order (Go randomizes on purpose). A missing Go key returns the zero value; use `v, ok := m[k]` to tell.


### Sets

```python
# -- create
a, b = {1, 2, 3}, {2, 3, 4}
# -- add
a.add(5)
# -- contains
print(2 in a)  # => True
# -- intersection
print(a & b)  # => {2, 3}
# -- union
print(a | b)  # => {1, 2, 3, 4, 5}
# -- difference
print(a - b)  # => {1, 5}
```

```rust
// -- create
use std::collections::HashSet;
let mut a = HashSet::from([1, 2, 3]);
let b = HashSet::from([2, 3, 4]);
// -- add
a.insert(5);
// -- contains
println!("{}", a.contains(&2)); // => true
// -- intersection
println!("{}", (&a & &b).len()); // => 2
// -- union
println!("{}", (&a | &b).len()); // => 5
// -- difference
println!("{}", (&a - &b).len()); // => 2
```

```go
// -- create
a := map[int]struct{}{1: {}, 2: {}, 3: {}}
b := map[int]struct{}{2: {}, 3: {}, 4: {}}
// -- add
a[5] = struct{}{}
// -- contains
_, ok := a[2]
fmt.Println(ok) // => true
// -- intersection
var both []int
for k := range a {
	if _, in := b[k]; in {
		both = append(both, k)
	}
}
slices.Sort(both)
fmt.Println(both) // => [2 3]
// -- union
// -- difference
```

Go has no set type or set operators; `map[T]struct{}` is the idiom. Sets print in arbitrary order in Rust and Go, so sort before comparing.


### Tuples & destructuring

```python
# -- pack
point = (3, 4)
# -- unpack
x, y = point
# -- head & rest
first, *rest = [1, 2, 3]
# -- swap
x, y = y, x
# -- print
print(x, y, first, rest)  # => 4 3 1 [2, 3]
```

```rust
// -- pack
let point = (3, 4);
// -- unpack
let (mut x, mut y) = point;
// -- head & rest
let [first, rest @ ..] = [1, 2, 3];
// -- swap
(x, y) = (y, x);
// -- print
println!("{x} {y} {first} {rest:?}"); // => 4 3 1 [2, 3]
```

```go
// -- pack
x, y := 3, 4
// -- unpack
// -- head & rest
xs := []int{1, 2, 3}
first, rest := xs[0], xs[1:]
// -- swap
x, y = y, x
// -- print
fmt.Println(x, y, first, rest) // => 4 3 1 [2 3]
```

Go has no tuple type. Return several values or use a struct.


### Sorting

```python
# -- data
words = ['pear', 'fig', 'apple', 'kiwi']
# -- by key
print(sorted(words, key=len))  # => ['fig', 'pear', 'kiwi', 'apple']
# -- natural
words.sort()
print(words)  # => ['apple', 'fig', 'kiwi', 'pear']
```

```rust
// -- data
let mut words = vec!["pear", "fig", "apple", "kiwi"];
// -- by key
words.sort_by_key(|w| w.len());
println!("{words:?}"); // => ["fig", "pear", "kiwi", "apple"]
// -- natural
words.sort();
println!("{words:?}"); // => ["apple", "fig", "kiwi", "pear"]
```

```go
// -- data
words := []string{"pear", "fig", "apple", "kiwi"}
// -- by key
slices.SortStableFunc(words, func(a, b string) int {
	return cmp.Compare(len(a), len(b))
})
fmt.Println(words) // => [fig pear kiwi apple]
// -- natural
slices.Sort(words)
fmt.Println(words) // => [apple fig kiwi pear]
```

All three sort in place here. Python's `sorted` and Rust's `sort_by_key` are stable; Go's `SortFunc` is not, so use `SortStableFunc` when ties matter. Floats are not `Ord` in Rust: use `sort_by(|a, b| a.total_cmp(b))`.


### Mutable vs immutable & copying

```python
# -- alias
a = [1, 2]
b = a
# -- mutate alias
b.append(3)
print(a)  # => [1, 2, 3]
# -- copy
c = a.copy()
# -- mutate copy
c.append(4)
print(a, c)  # => [1, 2, 3] [1, 2, 3, 4]
```

```rust
// -- alias
let mut a = vec![1, 2];
let b = &mut a;
// -- mutate alias
b.push(3);
println!("{a:?}"); // => [1, 2, 3]
// -- copy
let mut c = a.clone();
// -- mutate copy
c.push(4);
println!("{a:?} {c:?}"); // => [1, 2, 3] [1, 2, 3, 4]
```

```go
// -- alias
a := []int{1, 2}
b := a
// -- mutate alias
b[0] = 9
fmt.Println(a) // => [9 2]
// -- copy
c := slices.Clone(a)
// -- mutate copy
c[0] = 7
fmt.Println(a, c) // => [9 2] [7 2]
```

Python names are references. Rust assignment moves (the old name is dead) and `&mut` borrows exclusively. Go slices share a backing array, so `b := a` aliases; arrays and structs are copied by value. `copy.deepcopy` / `.clone()` on nested data copy deeply, `slices.Clone` does not.


## Control flow


### If-else & ternary-ish

```python
n = 15
# --
label = 'big' if n > 10 else 'small'
# --
if n < 0:
	sign = '-'
# ---
elif n == 0:
	sign = '0'
# ---
else:
	sign = '+'
# --
print(label, sign)  # => big +
```

```rust
let n = 15;
// --
let label = if n > 10 { "big" } else { "small" };
// --
let sign = if n < 0 {
    "-"
// ---
} else if n == 0 {
    "0"
// ---
} else {
    "+"
};
// --
println!("{label} {sign}"); // => big +
```

```go
n := 15
// --
label := "small"
if n > 10 {
	label = "big"
}
// --
var sign string
switch {
case n < 0:
	sign = "-"
// ---
case n == 0:
	sign = "0"
// ---
default:
	sign = "+"
}
// --
fmt.Println(label, sign) // => big +
```

In Rust `if` is an expression, so it is the ternary. Go has no ternary; a tagless `switch` replaces `elif` chains.


### Loops

```python
# -- range
for i in range(3):
	print(i)
# -- enumerate
for i, x in enumerate(['a', 'b']):
	print(i, x)
# -- while
n = 3
while n > 0:
	n -= 1
```

```rust
// -- range
for i in 0..3 {
    println!("{i}");
}
// -- enumerate
for (i, x) in ["a", "b"].iter().enumerate() {
    println!("{i} {x}");
}
// -- while
let mut n = 3;
while n > 0 {
    n -= 1;
}
```

```go
// -- range
for i := range 3 {
	fmt.Println(i)
}
// -- enumerate
for i, x := range []string{"a", "b"} {
	fmt.Println(i, x)
}
// -- while
n := 3
for n > 0 {
	n--
}
```

Go has only `for` (`for {}` is infinite). Rust's infinite loop is `loop {}` and `break` can return a value.


### Functions & multiple returns

```python
# -- define
def div(a, b=1):
	return a // b, a % b

# -- call
q, r = div(7, 2)
print(q, r)  # => 3 1
```

```rust
// -- define
fn div(a: i32, b: i32) -> (i32, i32) {
    (a / b, a % b)
}

// -- call
let (q, r) = div(7, 2);
println!("{q} {r}"); // => 3 1
```

```go
// -- define
func div(a, b int) (int, int) {
	return a / b, a % b
}

// -- call
func main() {
	q, r := div(7, 2)
	fmt.Println(q, r) // => 3 1
}
```

Rust and Go have no default or keyword arguments; use a struct of options. Go also has variadics (`xs ...int`) and named results.


### Closures / lambdas

```python
# -- lambda
add = lambda a, b: a + b

# -- counter
def counter():
	n = 0
	def inc():
		nonlocal n
		n += 1
		return n
	return inc

# -- call
c = counter()
c()
print(add(1, 2), c())  # => 3 2
```

```rust
// -- lambda
let add = |a: i32, b: i32| a + b;
// -- counter
let mut n = 0;
let mut inc = || {
    n += 1;
    n
};
// -- call
inc();
println!("{} {}", add(1, 2), inc()); // => 3 2
```

```go
// -- lambda
add := func(a, b int) int { return a + b }
// -- counter
n := 0
inc := func() int {
	n++
	return n
}
// -- call
inc()
fmt.Println(add(1, 2), inc()) // => 3 2
```

Python lambdas hold one expression; use `def` for more. A Rust closure that mutates captured state must be bound `mut`.


### Iterators & comprehensions

```python
# -- data
xs = [1, 2, 3, 4]
# -- filter & map
squares = [x * x for x in xs if x % 2 == 0]
# -- sum
total = sum(x * x for x in xs)
# -- print
print(squares, total)  # => [4, 16] 30
```

```rust
// -- data
let xs = [1, 2, 3, 4];
// -- filter & map
let squares: Vec<i32> = xs.iter().filter(|&&x| x % 2 == 0).map(|x| x * x).collect();
// -- sum
let total: i32 = xs.iter().map(|x| x * x).sum();
// -- print
println!("{squares:?} {total}"); // => [4, 16] 30
```

```go
// -- data
xs := []int{1, 2, 3, 4}
// -- filter & map
var squares []int
total := 0
for _, x := range xs {
	total += x * x
	if x%2 == 0 {
		squares = append(squares, x*x)
	}
}
// -- sum
// -- print
fmt.Println(squares, total) // => [4 16] 30
```

Rust iterator chains are lazy until `collect` or `sum`. Go has no `map` / `filter`; write the loop (iterators exist via `iter.Seq`, but the stdlib offers no adapters).


### Decorators & wrappers

```python
# -- wrapper
import functools

def logged(fn):
	@functools.wraps(fn)
	def wrapper(*args):
		result = fn(*args)
		print(f'{fn.__name__}{args} = {result}')
		return result
	return wrapper

# -- function
@logged
def add(a, b):
	return a + b

# -- apply
add(1, 2)  # => add(1, 2) = 3
```

```rust
// -- wrapper
fn logged<F: Fn(i32, i32) -> i32>(name: &str, f: F) -> impl Fn(i32, i32) -> i32 {
    let name = name.to_string();
    move |a, b| {
        let result = f(a, b);
        println!("{name}({a}, {b}) = {result}");
        result
    }
}

// -- function
fn add(a: i32, b: i32) -> i32 {
    a + b
}

// -- apply
let add = logged("add", add);
add(1, 2); // => add(1, 2) = 3
```

```go
// -- wrapper
func logged(name string, f func(int, int) int) func(int, int) int {
	return func(a, b int) int {
		result := f(a, b)
		fmt.Printf("%s(%d, %d) = %d\n", name, a, b, result)
		return result
	}
}

// -- function
func add(a, b int) int { return a + b }

// -- apply
func main() {
	add := logged("add", add)
	add(1, 2) // => add(1, 2) = 3
}
```

`@logged` is sugar for `add = logged(add)`. Rust and Go have no sugar: pass the function in, get a closure back, and bind it under the same name. Rust attributes like `#[test]` and `#[tokio::main]` are macros, not decorators; they rewrite the item at compile time. Go middleware wraps `http.Handler` exactly this way.


## Types


### Structs / classes & constructors

```python
# -- define
from dataclasses import dataclass

@dataclass
class User:
	name: str
	age: int = 0

# -- constructor
# -- create & print
u = User('ann')
print(u)  # => User(name='ann', age=0)
```

```rust
// -- define
#[derive(Debug)]
struct User {
    name: String,
    age: u32,
}

// -- constructor
impl User {
    fn new(name: &str) -> Self {
        Self { name: name.to_string(), age: 0 }
    }
}

// -- create & print
let u = User::new("ann");
println!("{u:?}"); // => User { name: "ann", age: 0 }
```

```go
// -- define
type User struct {
	Name string
	Age  int
}

// -- constructor
func NewUser(name string) User {
	return User{Name: name}
}

// -- create & print
func main() {
	fmt.Printf("%+v\n", NewUser("ann")) // => {Name:ann Age:0}
}
```

Rust and Go have no constructors; `new` / `NewX` are conventions. Unset Go fields take their zero value. Capitalized Go names are exported.


### Methods

```python
# -- type
class Rect:
	def __init__(self, w, h):
		self.w, self.h = w, h
	# -- read method
	def area(self):
		return self.w * self.h
	# -- mutating method
	def scale(self, k):
		self.w *= k
		self.h *= k
# -- use
r = Rect(2, 3)
r.scale(2)
print(r.area())  # => 24
```

```rust
// -- type
struct Rect { w: f64, h: f64 }

impl Rect {
    // -- read method
    fn area(&self) -> f64 { self.w * self.h }
    // -- mutating method
    fn scale(&mut self, k: f64) { self.w *= k; self.h *= k; }
}

// -- use
let mut r = Rect { w: 2.0, h: 3.0 };
r.scale(2.0);
println!("{}", r.area()); // => 24
```

```go
// -- type
type Rect struct{ W, H float64 }

// -- read method
func (r Rect) Area() float64 { return r.W * r.H }

// -- mutating method
func (r *Rect) Scale(k float64) {
	r.W *= k
	r.H *= k
}

// -- use
func main() {
	r := Rect{2, 3}
	r.Scale(2)
	fmt.Println(r.Area()) // => 24
}
```

Rust makes mutation explicit in the signature (`&mut self`). In Go a value receiver works on a copy; use a pointer receiver to mutate.


### Interfaces / traits / Protocols

```python
from typing import Protocol
class Shape(Protocol):
	def area(self) -> float: ...
# --
class Square:
	def __init__(self, s):
		self.s = s
	# --
	def area(self):
		return self.s ** 2
# --
def describe(shape: Shape):
	print(shape.area())
# --
describe(Square(3))  # => 9
```

```rust
trait Shape { fn area(&self) -> f64; }

// --
struct Square(f64);

// --
impl Shape for Square {
    fn area(&self) -> f64 { self.0 * self.0 }
}

// --
fn describe(shape: &dyn Shape) { println!("{}", shape.area()); }

// --
describe(&Square(3.0)); // => 9
```

```go
type Shape interface{ Area() float64 }

// --
type Square struct{ S float64 }

// --
func (s Square) Area() float64 { return s.S * s.S }

// --
func describe(shape Shape) { fmt.Println(shape.Area()) }

// --
func main() {
	describe(Square{3}) // => 9
}
```

Protocols and Go interfaces are structural: no declaration of intent. Rust needs an explicit `impl Trait for Type`, and `&dyn Shape` is dynamic dispatch (`impl Shape` is static).


### Enums & match / switch

```python
# -- variants
from dataclasses import dataclass
@dataclass
class Circle:
	r: float
@dataclass
class Rect:
	w: float
	h: float
# -- match
def area(s):
	match s:
		case Circle(r):
			return 3.14 * r * r
		case Rect(w, h):
			return w * h
# -- use
print(area(Rect(2, 3)))  # => 6
```

```rust
// -- variants
enum Shape {
    Circle(f64),
    Rect { w: f64, h: f64 },
}

// -- match
fn area(s: &Shape) -> f64 {
    match s {
        Shape::Circle(r) => 3.14 * r * r,
        Shape::Rect { w, h } => w * h,
    }
}

// -- use
println!("{}", area(&Shape::Rect { w: 2.0, h: 3.0 })); // => 6
```

```go
// -- variants
type Circle struct{ R float64 }
type Rect struct{ W, H float64 }
// -- match
func area(s any) float64 {
	switch s := s.(type) {
	case Circle:
		return 3.14 * s.R * s.R
	case Rect:
		return s.W * s.H
	}
	return 0
}
// -- use
func main() {
	fmt.Println(area(Rect{2, 3})) // => 6
}
```

Rust's `match` must cover every variant or it will not compile. Go has no sum types: a type switch is the closest, and plain enums are `const ( A = iota; B )`.


### Generics

```python
# -- define
def largest[T](xs: list[T]) -> T:
	return max(xs)

# -- use
print(largest([1, 5, 3]), largest([1.5, 0.2]))  # => 5 1.5
```

```rust
// -- define
fn largest<T: PartialOrd + Copy>(xs: &[T]) -> T {
    let mut m = xs[0];
    for &x in xs {
        if x > m {
            m = x;
        }
    }
    m
}

// -- use
println!("{} {}", largest(&[1, 5, 3]), largest(&[1.5, 0.2])); // => 5 1.5
```

```go
// -- define
func Largest[T cmp.Ordered](xs []T) T {
	m := xs[0]
	for _, x := range xs {
		if x > m {
			m = x
		}
	}
	return m
}

// -- use
func main() {
	fmt.Println(Largest([]int{1, 5, 3}), Largest([]float64{1.5, 0.2})) // => 5 1.5
}
```

Python's `[T]` is only a hint for type checkers. Rust and Go check the bound at compile time (`PartialOrd`, `cmp.Ordered`) and generate code per type.


## Errors & resources


### Error handling

```python
# -- import
# -- parse
def parse_port(s):
	try:
		return int(s)
	# -- wrap
	except ValueError as e:
		raise RuntimeError(f'bad port {s!r}') from e
	# -- ok

# -- handle
try:
	parse_port('x')
except RuntimeError as e:
	print(e)  # => bad port 'x'
```

```rust
// -- import
use std::error::Error;

// -- parse
fn parse_port(s: &str) -> Result<u16, Box<dyn Error>> {
    // -- wrap
    let n = s.parse::<u16>().map_err(|e| format!("bad port {s:?}: {e}"))?;
    // -- ok
    Ok(n)
}

// -- handle
if let Err(e) = parse_port("x") {
    println!("{e}"); // => bad port "x": invalid digit found in string
}
```

```go
// -- import
// -- parse
func parsePort(s string) (int, error) {
	n, err := strconv.Atoi(s)
	// -- wrap
	if err != nil {
		return 0, fmt.Errorf("bad port %q: %w", s, err)
	}
	// -- ok
	return n, nil
}

// -- handle
func main() {
	if _, err := parsePort("x"); err != nil {
		fmt.Println(err) // => bad port "x": strconv.Atoi: parsing "x": invalid syntax
	}
}
```

Errors are values in Rust and Go: `?` returns early on `Err`, `if err != nil` is the Go spelling. `%w` keeps the cause for `errors.Is` / `errors.As`. For real Rust code reach for `anyhow` (apps) or `thiserror` (libraries).


### with / Drop / defer

```python
# -- type
class Resource:
	# -- open
	def __enter__(self):
		print('open')
		return self
	# -- close
	def __exit__(self, *exc):
		print('close')

# -- use
with Resource():
	print('use')
```

```rust
// -- type
struct Resource;

// -- open
impl Resource {
    fn open() -> Self {
        println!("open");
        Resource
    }
}

// -- close
impl Drop for Resource {
    fn drop(&mut self) {
        println!("close");
    }
}

// -- use
{
    let _r = Resource::open();
    println!("use");
}
```

```go
// -- type
type Resource struct{}

// -- open
func Open() *Resource {
	fmt.Println("open")
	return &Resource{}
}

// -- close
func (r *Resource) Close() { fmt.Println("close") }

// -- use
func main() {
	r := Open()
	defer r.Close()
	fmt.Println("use")
}
```

All three print `open`, `use`, `close`. Python runs `__exit__` when the block ends, even on an exception. Rust runs `drop` when the owner goes out of scope, so there is nothing to forget; `let _r` keeps the value alive, `let _ =` drops it on the spot. Go's `defer` runs when the function returns, not when the block ends, so a loop that opens files should wrap its body in a function.


## Data & I/O


### File read & write

```python
# -- path
from pathlib import Path

path = Path('notes.txt')
# -- write
path.write_text('one\ntwo\n')
# -- read
text = path.read_text()
# -- lines
for line in text.splitlines():
	print(line)
```

```rust
// -- path
use std::fs;

let path = "notes.txt";
// -- write
fs::write(path, "one\ntwo\n")?;
// -- read
let text = fs::read_to_string(path)?;
// -- lines
for line in text.lines() {
    println!("{line}");
}
```

```go
// -- path
path := "notes.txt"
// -- write
if err := os.WriteFile(path, []byte("one\ntwo\n"), 0o644); err != nil {
	log.Fatal(err)
}
// -- read
data, err := os.ReadFile(path)
if err != nil {
	log.Fatal(err)
}
// -- lines
for _, line := range strings.Split(strings.TrimSpace(string(data)), "\n") {
	fmt.Println(line)
}
```

For big files stream instead: `open()` iteration, `BufReader::lines`, `bufio.Scanner`.


### JSON encode/decode to a struct

```python
# -- type
import json
from dataclasses import dataclass, asdict

@dataclass
class User:
	name: str
	age: int

# -- decode
raw = '{"name": "ann", "age": 30}'
user = User(**json.loads(raw))
# -- encode
print(json.dumps(asdict(user)))  # => {"name": "ann", "age": 30}
```

```rust
// -- type
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct User {
    name: String,
    age: u32,
}

// -- decode
let raw = r#"{"name": "ann", "age": 30}"#;
let user: User = serde_json::from_str(raw)?;
// -- encode
println!("{}", serde_json::to_string(&user)?); // => {"name":"ann","age":30}
```

```go
// -- type
type User struct {
	Name string `json:"name"`
	Age  int    `json:"age"`
}

// -- decode
raw := `{"name": "ann", "age": 30}`
var user User
if err := json.Unmarshal([]byte(raw), &user); err != nil {
	log.Fatal(err)
}
// -- encode
out, _ := json.Marshal(user)
fmt.Println(string(out)) // => {"name":"ann","age":30}
```

Python's dataclass does no validation: `User(**d)` will not check types. serde and Go reject mismatched types. Go only sees exported (capitalized) fields, so the tags map them to lowercase keys.


### HTTP GET

```python
# -- request
import urllib.request

url = 'https://example.com'
with urllib.request.urlopen(url, timeout=10) as resp:
	# -- status & body
	status = resp.status
	body = resp.read().decode()
# -- print
print(status, len(body) > 0)  # => 200 True
```

```rust
// -- request
let url = "https://example.com";
let resp = reqwest::get(url).await?.error_for_status()?;
// -- status & body
let status = resp.status().as_u16();
let body = resp.text().await?;
// -- print
println!("{status} {}", !body.is_empty()); // => 200 true
```

```go
// -- request
url := "https://example.com"
resp, err := http.Get(url)
if err != nil {
	log.Fatal(err)
}
// -- status & body
defer resp.Body.Close()
body, err := io.ReadAll(resp.Body)
if err != nil {
	log.Fatal(err)
}
// -- print
fmt.Println(resp.StatusCode, len(body) > 0) // => 200 true
```

`urlopen` raises on 4xx/5xx, and `error_for_status` does the same in reqwest. Go's `http.Get` does not: check `StatusCode` yourself, and always close the body. `http.Get` has no timeout; use an `http.Client{Timeout: ...}` in real code.


### Dates & time

```python
# -- construct
from datetime import UTC, datetime, timedelta

d = datetime(2026, 1, 2, 15, 4, tzinfo=UTC)
# -- add a day
print(d + timedelta(days=1))  # => 2026-01-03 15:04:00+00:00
# -- format
print(d.strftime('%Y-%m-%d'))  # => 2026-01-02
# -- parse
parsed = datetime.fromisoformat('2026-01-02T15:04:00+00:00')
# -- compare
print(parsed == d)  # => True
```

```rust
// -- construct
use chrono::{DateTime, Duration, TimeZone, Utc};

let d = Utc.with_ymd_and_hms(2026, 1, 2, 15, 4, 0).unwrap();
// -- add a day
println!("{}", d + Duration::days(1)); // => 2026-01-03 15:04:00 UTC
// -- format
println!("{}", d.format("%Y-%m-%d")); // => 2026-01-02
// -- parse
let parsed = DateTime::parse_from_rfc3339("2026-01-02T15:04:00+00:00")?;
// -- compare
println!("{}", parsed == d); // => true
```

```go
// -- construct
d := time.Date(2026, time.January, 2, 15, 4, 0, 0, time.UTC)
// -- add a day
fmt.Println(d.Add(24 * time.Hour)) // => 2026-01-03 15:04:00 +0000 UTC
// -- format
fmt.Println(d.Format("2006-01-02")) // => 2026-01-02
// -- parse
parsed, err := time.Parse(time.RFC3339, "2026-01-02T15:04:00+00:00")
if err != nil {
	log.Fatal(err)
}
// -- compare
fmt.Println(parsed.Equal(d)) // => true
```

Rust's stdlib has no calendar, so `chrono` (or `jiff`) is the default. Go formats with the reference time `Mon Jan 2 15:04:05 2006`, not `%Y`. `Add(24 * time.Hour)` is a fixed duration; `AddDate(0, 0, 1)` is calendar-aware.


## Concurrency


### Concurrency: run tasks in parallel

```python
# -- task
import asyncio

async def fetch(n):
	await asyncio.sleep(0.1)
	return n * 2

# -- run both
async def main():
	print(await asyncio.gather(fetch(1), fetch(2)))  # => [2, 4]

asyncio.run(main())
```

```rust
// -- task
use std::time::Duration;
use tokio::time::sleep;

async fn fetch(n: u64) -> u64 {
    sleep(Duration::from_millis(100)).await;
    n * 2
}

// -- run both
let (a, b) = tokio::join!(fetch(1), fetch(2));
println!("{a} {b}"); // => 2 4
```

```go
// -- task
// -- run both
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


### Channels & queues

```python
# -- channel
import queue
import threading

q = queue.Queue()

# -- producer
def producer():
	for i in range(3):
		q.put(i * i)
	q.put(None)

threading.Thread(target=producer).start()
# -- consume
while (x := q.get()) is not None:
	print(x)
```

```rust
// -- channel
use std::{sync::mpsc, thread};

let (tx, rx) = mpsc::channel();
// -- producer
thread::spawn(move || {
    for i in 0..3 {
        tx.send(i * i).unwrap();
    }
});
// -- consume
for x in rx {
    println!("{x}");
}
```

```go
// -- channel
ch := make(chan int)
// -- producer
go func() {
	defer close(ch)
	for i := range 3 {
		ch <- i * i
	}
}()
// -- consume
for x := range ch {
	fmt.Println(x)
}
```

The Rust loop ends when every sender is dropped; the Go loop ends when the sender closes the channel. Python needs a sentinel (`None`). `make(chan int, 10)` buffers; unbuffered sends block until received.


### Shared state

```python
# -- state
import threading
count = 0
lock = threading.Lock()
# -- workers
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
# -- print
print(count)  # => 4000
```

```rust
// -- state
use std::{sync::{Arc, Mutex}, thread};

let count = Arc::new(Mutex::new(0));
// -- workers
let handles: Vec<_> = (0..4).map(|_| {
    let count = Arc::clone(&count);
    thread::spawn(move || {
        for _ in 0..1000 { *count.lock().unwrap() += 1; }
    })
}).collect();
for h in handles { h.join().unwrap(); }
// -- print
println!("{}", count.lock().unwrap()); // => 4000
```

```go
// -- state
var mu sync.Mutex
var wg sync.WaitGroup
count := 0
// -- workers
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
// -- print
fmt.Println(count) // => 4000
```

In Rust the lock owns the data, so you cannot touch it unlocked; `Arc` shares ownership across threads. Go's mutex sits beside the data by convention only; `go test -race` finds misses.


## Project & tooling


### Modules & imports

```python
# -- import
import math
from math import sqrt as root

# -- use
print(math.pi, root(16))  # => 3.141592653589793 4.0
```

```rust
// -- import
use std::f64::consts::PI;

mod geometry {
    pub fn sqrt(x: f64) -> f64 {
        x.sqrt()
    }
}
use geometry::sqrt;

// -- use
println!("{PI} {}", sqrt(16.0)); // => 3.141592653589793 4
```

```go
// -- import
import (
	"fmt"
	m "math"
)

// -- use
func main() {
	fmt.Println(m.Pi, m.Sqrt(16)) // => 3.141592653589793 4
}
```

Python: one file is one module. Rust: `mod geometry;` loads `geometry.rs`, items are private unless `pub`, dependencies live in `Cargo.toml`. Go: one directory is one package, capitalized names are exported, and the module path comes from `go.mod`.


### CLI args

```python
# -- define
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('name', nargs='?', default='world')
parser.add_argument('--count', type=int, default=1)
# -- parse
args = parser.parse_args()
# -- use
for _ in range(args.count):
	print(f'hi {args.name}')  # => hi world
```

```rust
// -- define
// -- parse
let mut args = std::env::args().skip(1);
let name = args.next().unwrap_or_else(|| "world".to_string());
let count: usize = args.next().and_then(|s| s.parse().ok()).unwrap_or(1);
// -- use
for _ in 0..count {
    println!("hi {name}"); // => hi world
}
```

```go
// -- define
count := flag.Int("count", 1, "repeat count")
// -- parse
flag.Parse()
name := cmp.Or(flag.Arg(0), "world")
// -- use
for range *count {
	fmt.Println("hi", name) // => hi world
}
```

Rust's stdlib only gives raw arguments (here positional, name then count); `clap` is the `argparse` equivalent. Go's `flag` stops at the first positional, so put flags first: `prog -count 2 ann`.


### Environment variables

```python
# -- with default
import os

port = os.environ.get('PORT', '8080')
# -- required
home = os.environ['HOME']
# -- print
print(port)  # => 8080
```

```rust
// -- with default
use std::env;

let port = env::var("PORT").unwrap_or_else(|_| "8080".to_string());
// -- required
let home = env::var("HOME")?;
// -- print
println!("{port} {}", !home.is_empty()); // => 8080 true
```

```go
// -- with default
port := os.Getenv("PORT")
if port == "" {
	port = "8080"
}
// -- required
home, ok := os.LookupEnv("HOME")
// -- print
fmt.Println(port, ok, home != "") // => 8080 true true
```

`os.environ['HOME']` raises `KeyError`; `env::var` returns `Err`. Go's `Getenv` returns an empty string for unset, so use `LookupEnv` when empty is meaningful.


### Tests

```python
# -- code
def add(a, b):
	return a + b

# -- test
def test_add():
	assert add(1, 2) == 3
```

```rust
// -- code
fn add(a: i32, b: i32) -> i32 {
    a + b
}

// -- test
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
// -- code
func Add(a, b int) int { return a + b }

// -- test
func TestAdd(t *testing.T) {
	if got := Add(1, 2); got != 3 {
		t.Errorf("Add(1, 2) = %d, want 3", got)
	}
}
```

Run with `pytest` (stdlib alternative: `unittest`), `cargo test`, `go test ./...`. Rust unit tests sit in the same file; Go tests live in `*_test.go` next to the code, and `Test*` functions take `*testing.T`.


### Project & dependencies

```sh Python
# -- init
uv init hello && cd hello
# -- add dependency
uv add httpx
# -- run
uv run main.py
# -- build
uv build
```

```sh Rust
# -- init
cargo new hello && cd hello
# -- add dependency
cargo add reqwest --features blocking
# -- run
cargo run
# -- build
cargo build --release
```

```sh Go
# -- init
mkdir hello && cd hello && go mod init example.com/hello
# -- add dependency
go get golang.org/x/sync
# -- run
go run .
# -- build
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


### Format & lint

```sh Python
# -- format
uvx ruff format
# -- lint
uvx ruff check --fix
```

```sh Rust
# -- format
cargo fmt
# -- lint
cargo clippy
```

```sh Go
# -- format
gofmt -w .
# -- lint
go vet ./...
```

Formatting is settled in all three: `gofmt` has no options, `rustfmt` and `ruff format` have a few. `ruff check` replaces flake8, isort and most pylint rules and fixes what it can. `clippy` ships with the toolchain and is strict by default. `go vet` catches the bugs the compiler lets through; `staticcheck` or `golangci-lint` add the rest.
