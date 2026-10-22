```python
def is_palindrome(s):
	i, j = 0, len(s) - 1
	while i < j:
		if s[i] != s[j]:
			return False
		i, j = i + 1, j - 1
	return True

print(is_palindrome('racecar'), 'racecar' == 'racecar'[::-1])  # => True True
```

```rust
fn is_palindrome(s: &str) -> bool {
    let b = s.as_bytes();
    let (mut i, mut j) = (0, b.len() - 1);
    while i < j {
        if b[i] != b[j] {
            return false;
        }
        i += 1;
        j -= 1;
    }
    true
}

let rev: String = "racecar".chars().rev().collect();
println!("{} {}", is_palindrome("racecar"), rev == "racecar"); // => true true
```

```go
func isPalindrome(s string) bool {
	b := []byte(s)
	for i, j := 0, len(b)-1; i < j; i, j = i+1, j-1 {
		if b[i] != b[j] {
			return false
		}
	}
	return true
}

func main() {
	b := []byte("racecar")
	slices.Reverse(b)
	fmt.Println(isPalindrome("racecar"), string(b) == "racecar") // => true true
}
```

Rust and Go strings are UTF-8 bytes and cannot be indexed by character; index `as_bytes()` / `[]byte(s)` for ASCII, or collect `chars()` / `[]rune(s)` first. Python indexes code points directly.
