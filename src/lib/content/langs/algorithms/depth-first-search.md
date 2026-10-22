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
