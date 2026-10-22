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
