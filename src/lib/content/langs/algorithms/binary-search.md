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
