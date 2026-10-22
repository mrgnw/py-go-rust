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
