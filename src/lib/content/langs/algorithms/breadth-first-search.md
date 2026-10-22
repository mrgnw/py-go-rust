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
