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
