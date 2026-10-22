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
