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
let top = counts.iter().max_by_key(|&(_, &n)| n).unwrap();
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
