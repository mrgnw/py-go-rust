```python
import heapq

xs = [5, 1, 9, 3, 7]
print(heapq.nlargest(2, xs))  # => [9, 7]
heap = []
for x in xs:
	heapq.heappush(heap, x)
print(heapq.heappop(heap), heapq.heappop(heap))  # => 1 3
```

```rust
use std::cmp::Reverse;
use std::collections::BinaryHeap;

let xs = [5, 1, 9, 3, 7];
let mut heap: BinaryHeap<_> = xs.iter().copied().collect();
println!("{:?}", [heap.pop().unwrap(), heap.pop().unwrap()]); // => [9, 7]
let mut min_heap: BinaryHeap<_> = xs.iter().map(|&x| Reverse(x)).collect();
let Reverse(a) = min_heap.pop().unwrap();
let Reverse(b) = min_heap.pop().unwrap();
println!("{a} {b}"); // => 1 3
```

```go
type IntHeap []int

func (h IntHeap) Len() int           { return len(h) }
func (h IntHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h IntHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *IntHeap) Push(x any)        { *h = append(*h, x.(int)) }
func (h *IntHeap) Pop() any {
	old := *h
	x := old[len(old)-1]
	*h = old[:len(old)-1]
	return x
}

func main() {
	xs := []int{5, 1, 9, 3, 7}
	slices.SortFunc(xs, func(a, b int) int { return b - a })
	fmt.Println(xs[:2]) // => [9 7]
	h := &IntHeap{}
	for _, x := range xs {
		heap.Push(h, x)
	}
	fmt.Println(heap.Pop(h), heap.Pop(h)) // => 1 3
}
```

`heapq` is a min-heap over a plain list. `BinaryHeap` is a max-heap; wrap items in `Reverse` for a min-heap. Go's `container/heap` works on any type with the five methods above, there is no generic heap in the stdlib, and interviewers know that, so sorting is acceptable for top-k.
