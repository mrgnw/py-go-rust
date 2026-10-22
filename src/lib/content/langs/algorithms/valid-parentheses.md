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
