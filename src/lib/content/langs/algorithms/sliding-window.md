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
