# Algorithms

Interview patterns, the same solution in all three. Each one is the version you would write on a whiteboard, then the stdlib call that does it for you when there is one.

| Operation | Python | Rust | Go |
|-|-|-|-|
| Append to end | `list.append`, amortised O(1) | `Vec::push`, amortised O(1) | `append`, amortised O(1) |
| Pop from front | `deque.popleft`, O(1); `list.pop(0)` is O(n) | `VecDeque::pop_front`, O(1) | `s = s[1:]`, O(1), old array kept alive |
| Lookup by key | `dict`, O(1) average | `HashMap`, O(1) average; `BTreeMap`, O(log n) | `map`, O(1) average |
| Sort | `sorted`, Timsort, stable | `sort`, stable; `sort_unstable` | `slices.Sort`, pdqsort, not stable; `slices.SortStableFunc` |
| Min-heap | `heapq` on a list | `BinaryHeap` is a max-heap; wrap in `Reverse` | `container/heap` on your own type |

## Two sum (hash map)

```python
def two_sum(nums, target):
	seen = {}
	for i, n in enumerate(nums):
		if target - n in seen:
			return seen[target - n], i
		seen[n] = i

print(two_sum([2, 7, 11, 15], 9))  # => (0, 1)
```

```rust
use std::collections::HashMap;

fn two_sum(nums: &[i32], target: i32) -> Option<(usize, usize)> {
    let mut seen = HashMap::new();
    for (i, &n) in nums.iter().enumerate() {
        if let Some(&j) = seen.get(&(target - n)) {
            return Some((j, i));
        }
        seen.insert(n, i);
    }
    None
}

println!("{:?}", two_sum(&[2, 7, 11, 15], 9)); // => Some((0, 1))
```

```go
func twoSum(nums []int, target int) (int, int, bool) {
	seen := map[int]int{}
	for i, n := range nums {
		if j, ok := seen[target-n]; ok {
			return j, i, true
		}
		seen[n] = i
	}
	return 0, 0, false
}

func main() {
	fmt.Println(twoSum([]int{2, 7, 11, 15}, 9)) // => 0 1 true
}
```

One pass, O(n). "Not found" is `None` in Python, `Option` in Rust, and an extra `bool` (or an `error`) in Go.

## Valid parentheses (stack)

```python
def balanced(s):
	pairs = {')': '(', ']': '[', '}': '{'}
	stack = []
	for c in s:
		if c in pairs.values():
			stack.append(c)
		elif not stack or stack.pop() != pairs[c]:
			return False
	return not stack

print(balanced('([]{})'), balanced('(]'))  # => True False
```

```rust
fn balanced(s: &str) -> bool {
    let mut stack = Vec::new();
    for c in s.chars() {
        match c {
            '(' | '[' | '{' => stack.push(c),
            ')' | ']' | '}' => {
                let open = match c { ')' => '(', ']' => '[', _ => '{' };
                if stack.pop() != Some(open) {
                    return false;
                }
            }
            _ => {}
        }
    }
    stack.is_empty()
}

println!("{} {}", balanced("([]{})"), balanced("(]")); // => true false
```

```go
func balanced(s string) bool {
	pairs := map[rune]rune{')': '(', ']': '[', '}': '{'}
	var stack []rune
	for _, c := range s {
		if open, ok := pairs[c]; ok {
			if len(stack) == 0 || stack[len(stack)-1] != open {
				return false
			}
			stack = stack[:len(stack)-1]
		} else {
			stack = append(stack, c)
		}
	}
	return len(stack) == 0
}

func main() {
	fmt.Println(balanced("([]{})"), balanced("(]")) // => true false
}
```

A plain list / `Vec` / slice is the stack. Rust's `pop()` returns `Option`, so the empty case needs no separate check. Go has no `pop`: reslice.

## Binary search

```python
from bisect import bisect_left

def search(xs, target):
	lo, hi = 0, len(xs)
	while lo < hi:
		mid = (lo + hi) // 2
		if xs[mid] < target:
			lo = mid + 1
		else:
			hi = mid
	return lo

xs = [1, 3, 5, 7, 9]
print(search(xs, 7), bisect_left(xs, 7))  # => 3 3
```

```rust
fn search(xs: &[i32], target: i32) -> usize {
    let (mut lo, mut hi) = (0, xs.len());
    while lo < hi {
        let mid = (lo + hi) / 2;
        if xs[mid] < target {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    lo
}

let xs = [1, 3, 5, 7, 9];
println!("{} {}", search(&xs, 7), xs.partition_point(|&x| x < 7)); // => 3 3
```

```go
func search(xs []int, target int) int {
	lo, hi := 0, len(xs)
	for lo < hi {
		mid := (lo + hi) / 2
		if xs[mid] < target {
			lo = mid + 1
		} else {
			hi = mid
		}
	}
	return lo
}

func main() {
	xs := []int{1, 3, 5, 7, 9}
	i, _ := slices.BinarySearch(xs, 7)
	fmt.Println(search(xs, 7), i) // => 3 3
}
```

Half-open `[lo, hi)` returns the insertion point, which doubles as "first index not less than target". The stdlib versions: `bisect_left`, `partition_point`, `slices.BinarySearch` (also returns whether it was found).

## Two pointers

```python
def is_palindrome(s):
	i, j = 0, len(s) - 1
	while i < j:
		if s[i] != s[j]:
			return False
		i, j = i + 1, j - 1
	return True

print(is_palindrome('racecar'), 'racecar' == 'racecar'[::-1])  # => True True
```

```rust
fn is_palindrome(s: &str) -> bool {
    let b = s.as_bytes();
    let (mut i, mut j) = (0, b.len() - 1);
    while i < j {
        if b[i] != b[j] {
            return false;
        }
        i += 1;
        j -= 1;
    }
    true
}

let rev: String = "racecar".chars().rev().collect();
println!("{} {}", is_palindrome("racecar"), rev == "racecar"); // => true true
```

```go
func isPalindrome(s string) bool {
	b := []byte(s)
	for i, j := 0, len(b)-1; i < j; i, j = i+1, j-1 {
		if b[i] != b[j] {
			return false
		}
	}
	return true
}

func main() {
	b := []byte("racecar")
	slices.Reverse(b)
	fmt.Println(isPalindrome("racecar"), string(b) == "racecar") // => true true
}
```

Rust and Go strings are UTF-8 bytes and cannot be indexed by character; index `as_bytes()` / `[]byte(s)` for ASCII, or collect `chars()` / `[]rune(s)` first. Python indexes code points directly.

## Sliding window

```python
def max_window(xs, k):
	best = cur = sum(xs[:k])
	for i in range(k, len(xs)):
		cur += xs[i] - xs[i - k]
		best = max(best, cur)
	return best

print(max_window([1, 4, 2, 10, 2, 3, 1, 0, 20], 4))  # => 24
```

```rust
fn max_window(xs: &[i32], k: usize) -> i32 {
    let mut cur: i32 = xs[..k].iter().sum();
    let mut best = cur;
    for i in k..xs.len() {
        cur += xs[i] - xs[i - k];
        best = best.max(cur);
    }
    best
}

println!("{}", max_window(&[1, 4, 2, 10, 2, 3, 1, 0, 20], 4)); // => 24
```

```go
func maxWindow(xs []int, k int) int {
	cur := 0
	for _, x := range xs[:k] {
		cur += x
	}
	best := cur
	for i := k; i < len(xs); i++ {
		cur += xs[i] - xs[i-k]
		best = max(best, cur)
	}
	return best
}

func main() {
	fmt.Println(maxWindow([]int{1, 4, 2, 10, 2, 3, 1, 0, 20}, 4)) // => 24
}
```

Add the entering element, subtract the leaving one: O(n) instead of O(nk). `sum()` exists in Python and Rust; Go 1.25 has `min`/`max` built in but no `sum`.

## Breadth-first search

```python
from collections import deque

def bfs(graph, start, goal):
	dist = {start: 0}
	queue = deque([start])
	while queue:
		node = queue.popleft()
		if node == goal:
			return dist[node]
		for nxt in graph[node]:
			if nxt not in dist:
				dist[nxt] = dist[node] + 1
				queue.append(nxt)
	return -1

graph = {'a': ['b', 'c'], 'b': ['d'], 'c': ['d'], 'd': []}
print(bfs(graph, 'a', 'd'))  # => 2
```

```rust
use std::collections::{HashMap, VecDeque};

fn bfs(graph: &HashMap<&str, Vec<&str>>, start: &str, goal: &str) -> i32 {
    let mut dist = HashMap::from([(start, 0)]);
    let mut queue = VecDeque::from([start]);
    while let Some(node) = queue.pop_front() {
        if node == goal {
            return dist[node];
        }
        for &next in &graph[node] {
            if !dist.contains_key(next) {
                dist.insert(next, dist[node] + 1);
                queue.push_back(next);
            }
        }
    }
    -1
}

let graph = HashMap::from([
    ("a", vec!["b", "c"]),
    ("b", vec!["d"]),
    ("c", vec!["d"]),
    ("d", vec![]),
]);
println!("{}", bfs(&graph, "a", "d")); // => 2
```

```go
func bfs(graph map[string][]string, start, goal string) int {
	dist := map[string]int{start: 0}
	queue := []string{start}
	for len(queue) > 0 {
		node := queue[0]
		queue = queue[1:]
		if node == goal {
			return dist[node]
		}
		for _, next := range graph[node] {
			if _, seen := dist[next]; !seen {
				dist[next] = dist[node] + 1
				queue = append(queue, next)
			}
		}
	}
	return -1
}

func main() {
	graph := map[string][]string{"a": {"b", "c"}, "b": {"d"}, "c": {"d"}, "d": {}}
	fmt.Println(bfs(graph, "a", "d")) // => 2
}
```

The visited set doubles as the distance map. Python and Rust have a real deque; Go's idiom is to reslice, which is O(1) per pop but keeps the whole backing array alive until the loop ends.

## Depth-first search

```python
def components(graph):
	seen = set()
	def dfs(node):
		seen.add(node)
		for nxt in graph[node]:
			if nxt not in seen:
				dfs(nxt)
	count = 0
	for node in graph:
		if node not in seen:
			dfs(node)
			count += 1
	return count

print(components({1: [2], 2: [1], 3: [4], 4: [3], 5: []}))  # => 3
```

```rust
use std::collections::{HashMap, HashSet};

fn dfs(graph: &HashMap<i32, Vec<i32>>, node: i32, seen: &mut HashSet<i32>) {
    seen.insert(node);
    for &next in &graph[&node] {
        if !seen.contains(&next) {
            dfs(graph, next, seen);
        }
    }
}

fn components(graph: &HashMap<i32, Vec<i32>>) -> usize {
    let mut seen = HashSet::new();
    let mut count = 0;
    for &node in graph.keys() {
        if !seen.contains(&node) {
            dfs(graph, node, &mut seen);
            count += 1;
        }
    }
    count
}

let graph = HashMap::from([(1, vec![2]), (2, vec![1]), (3, vec![4]), (4, vec![3]), (5, vec![])]);
println!("{}", components(&graph)); // => 3
```

```go
func components(graph map[int][]int) int {
	seen := map[int]bool{}
	var dfs func(int)
	dfs = func(node int) {
		seen[node] = true
		for _, next := range graph[node] {
			if !seen[next] {
				dfs(next)
			}
		}
	}
	count := 0
	for node := range graph {
		if !seen[node] {
			dfs(node)
			count++
		}
	}
	return count
}

func main() {
	fmt.Println(components(map[int][]int{1: {2}, 2: {1}, 3: {4}, 4: {3}, 5: {}})) // => 3
}
```

Python's inner function captures `seen`. Go can do the same but a recursive closure must be declared before it is assigned. Rust closures cannot recurse, so the state travels as a `&mut` parameter. Python recursion stops at 1000 frames by default; for deep graphs use an explicit stack.

## Heap / priority queue

```python
import heapq

xs = [5, 1, 9, 3, 7]
print(heapq.nlargest(2, xs))  # => [9, 7]
heap = []
for x in xs:
	heapq.heappush(heap, x)
print(heapq.heappop(heap), heapq.heappop(heap))  # => 1 3
```

```rust
use std::cmp::Reverse;
use std::collections::BinaryHeap;

let xs = [5, 1, 9, 3, 7];
let mut heap: BinaryHeap<_> = xs.iter().copied().collect();
println!("{:?}", [heap.pop().unwrap(), heap.pop().unwrap()]); // => [9, 7]
let mut min_heap: BinaryHeap<_> = xs.iter().map(|&x| Reverse(x)).collect();
let Reverse(a) = min_heap.pop().unwrap();
let Reverse(b) = min_heap.pop().unwrap();
println!("{a} {b}"); // => 1 3
```

```go
type IntHeap []int

func (h IntHeap) Len() int           { return len(h) }
func (h IntHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h IntHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *IntHeap) Push(x any)        { *h = append(*h, x.(int)) }
func (h *IntHeap) Pop() any {
	old := *h
	x := old[len(old)-1]
	*h = old[:len(old)-1]
	return x
}

func main() {
	xs := []int{5, 1, 9, 3, 7}
	slices.SortFunc(xs, func(a, b int) int { return b - a })
	fmt.Println(xs[:2]) // => [9 7]
	h := &IntHeap{}
	for _, x := range xs {
		heap.Push(h, x)
	}
	fmt.Println(heap.Pop(h), heap.Pop(h)) // => 1 3
}
```

`heapq` is a min-heap over a plain list. `BinaryHeap` is a max-heap; wrap items in `Reverse` for a min-heap. Go's `container/heap` works on any type with the five methods above, there is no generic heap in the stdlib, and interviewers know that, so sorting is acceptable for top-k.

## Dynamic programming

```python
def min_coins(coins, amount):
	best = [0] + [float('inf')] * amount
	for a in range(1, amount + 1):
		for c in coins:
			if c <= a:
				best[a] = min(best[a], best[a - c] + 1)
	return best[amount] if best[amount] != float('inf') else -1

print(min_coins([1, 5, 10, 25], 63))  # => 6
```

```rust
fn min_coins(coins: &[usize], amount: usize) -> i32 {
    let mut best = vec![usize::MAX; amount + 1];
    best[0] = 0;
    for a in 1..=amount {
        for &c in coins {
            if c <= a && best[a - c] != usize::MAX {
                best[a] = best[a].min(best[a - c] + 1);
            }
        }
    }
    if best[amount] == usize::MAX { -1 } else { best[amount] as i32 }
}

println!("{}", min_coins(&[1, 5, 10, 25], 63)); // => 6
```

```go
func minCoins(coins []int, amount int) int {
	best := make([]int, amount+1)
	for a := 1; a <= amount; a++ {
		best[a] = math.MaxInt
		for _, c := range coins {
			if c <= a && best[a-c] != math.MaxInt {
				best[a] = min(best[a], best[a-c]+1)
			}
		}
	}
	if best[amount] == math.MaxInt {
		return -1
	}
	return best[amount]
}

func main() {
	fmt.Println(minCoins([]int{1, 5, 10, 25}, 63)) // => 6
}
```

Bottom-up table, O(amount × coins). Python's `float('inf')` is the lazy sentinel; Rust and Go use the integer max and must guard against overflowing it with `+ 1`.

## Memoization

```python
from functools import cache

@cache
def fib(n):
	return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(50))  # => 12586269025
```

```rust
use std::collections::HashMap;

fn fib(n: u64, memo: &mut HashMap<u64, u64>) -> u64 {
    if n < 2 {
        return n;
    }
    if let Some(&v) = memo.get(&n) {
        return v;
    }
    let v = fib(n - 1, memo) + fib(n - 2, memo);
    memo.insert(n, v);
    v
}

println!("{}", fib(50, &mut HashMap::new())); // => 12586269025
```

```go
func fib(n int, memo map[int]int) int {
	if n < 2 {
		return n
	}
	if v, ok := memo[n]; ok {
		return v
	}
	memo[n] = fib(n-1, memo) + fib(n-2, memo)
	return memo[n]
}

func main() {
	fmt.Println(fib(50, map[int]int{})) // => 12586269025
}
```

`@cache` is the whole trick in Python. Rust and Go pass the memo explicitly; Go's map is a reference type so no pointer is needed. Python ints are unbounded, `u64` and `int` overflow past `fib(93)`.

## Backtracking

```python
def permute(xs):
	if len(xs) <= 1:
		return [xs]
	return [[x, *rest] for i, x in enumerate(xs) for rest in permute(xs[:i] + xs[i + 1:])]

perms = permute([1, 2, 3])
print(len(perms), perms[1])  # => 6 [1, 3, 2]
```

```rust
fn permute(xs: &mut Vec<i32>, k: usize, out: &mut Vec<Vec<i32>>) {
    if k == xs.len() {
        out.push(xs.clone());
        return;
    }
    for i in k..xs.len() {
        xs.swap(k, i);
        permute(xs, k + 1, out);
        xs.swap(k, i);
    }
}

let mut out = Vec::new();
permute(&mut vec![1, 2, 3], 0, &mut out);
println!("{} {:?}", out.len(), out[1]); // => 6 [1, 3, 2]
```

```go
func permute(xs []int, k int, out *[][]int) {
	if k == len(xs) {
		*out = append(*out, slices.Clone(xs))
		return
	}
	for i := k; i < len(xs); i++ {
		xs[k], xs[i] = xs[i], xs[k]
		permute(xs, k+1, out)
		xs[k], xs[i] = xs[i], xs[k]
	}
}

func main() {
	var out [][]int
	permute([]int{1, 2, 3}, 0, &out)
	fmt.Println(len(out), out[1]) // => 6 [1 3 2]
}
```

Python builds new lists at every level, fine up to n ≈ 8 (`itertools.permutations` for real use). Rust and Go swap in place and copy only at the leaf; in Go the `slices.Clone` is mandatory, appending `xs` itself would store a slice that keeps changing.

## Linked list reversal

```python
class Node:
	def __init__(self, val, next=None):
		self.val, self.next = val, next

def reverse(head):
	prev = None
	while head:
		head.next, prev, head = prev, head, head.next
	return prev

vals = []
node = reverse(Node(1, Node(2, Node(3))))
while node:
	vals.append(node.val)
	node = node.next
print(vals)  # => [3, 2, 1]
```

```rust
struct Node {
    val: i32,
    next: Option<Box<Node>>,
}

fn reverse(mut head: Option<Box<Node>>) -> Option<Box<Node>> {
    let mut prev = None;
    while let Some(mut node) = head {
        head = node.next.take();
        node.next = prev;
        prev = Some(node);
    }
    prev
}

let mut list = None;
for val in [3, 2, 1] {
    list = Some(Box::new(Node { val, next: list }));
}
let mut vals = Vec::new();
let mut cur = reverse(list);
while let Some(node) = cur {
    vals.push(node.val);
    cur = node.next;
}
println!("{vals:?}"); // => [3, 2, 1]
```

```go
type Node struct {
	Val  int
	Next *Node
}

func reverse(head *Node) *Node {
	var prev *Node
	for head != nil {
		head.Next, prev, head = prev, head, head.Next
	}
	return prev
}

func main() {
	var vals []int
	for n := reverse(&Node{1, &Node{2, &Node{3, nil}}}); n != nil; n = n.Next {
		vals = append(vals, n.Val)
	}
	fmt.Println(vals) // => [3 2 1]
}
```

Python and Go rotate three pointers in one tuple assignment. Rust has no shared mutable pointers: the list is `Option<Box<Node>>`, and `take()` moves the tail out before the node is re-linked. This is the ownership model in one function, and it is why linked lists are the hardest interview topic in Rust.

## Frequency count

```python
from collections import Counter

counts = Counter('a b a c b a'.split())
print(counts.most_common(1))  # => [('a', 3)]
```

```rust
use std::collections::HashMap;

let mut counts = HashMap::new();
for w in "a b a c b a".split(' ') {
    *counts.entry(w).or_insert(0) += 1;
}
let top = counts.iter().max_by_key(|(_, &n)| n).unwrap();
println!("{top:?}"); // => ("a", 3)
```

```go
func main() {
	counts := map[string]int{}
	for _, w := range strings.Fields("a b a c b a") {
		counts[w]++
	}
	top := ""
	for w, n := range counts {
		if n > counts[top] {
			top = w
		}
	}
	fmt.Println(top, counts[top]) // => a 3
}
```

`Counter` does it all. Rust's `entry().or_insert(0)` and Go's zero-value `counts[w]++` are the idioms for "insert or increment". Map iteration order is random in Go and unspecified in Rust, so ties pick an arbitrary winner.
