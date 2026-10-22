# Algorithms

Interview patterns, the same solution in all three. Each one is the version you would write on a whiteboard, then the stdlib call that does it for you when there is one.

| Operation | Python | Rust | Go |
|-|-|-|-|
| Append to end | `list.append`, amortised O(1) | `Vec::push`, amortised O(1) | `append`, amortised O(1) |
| Pop from front | `deque.popleft`, O(1); `list.pop(0)` is O(n) | `VecDeque::pop_front`, O(1) | `s = s[1:]`, O(1), old array kept alive |
| Lookup by key | `dict`, O(1) average | `HashMap`, O(1) average; `BTreeMap`, O(log n) | `map`, O(1) average |
| Sort | `sorted`, Timsort, stable | `sort`, stable; `sort_unstable` | `slices.Sort`, pdqsort, not stable; `slices.SortStableFunc` |
| Min-heap | `heapq` on a list | `BinaryHeap` is a max-heap; wrap in `Reverse` | `container/heap` on your own type |

## [Two sum (hash map)](algorithms/two-sum.md)
## [Valid parentheses (stack)](algorithms/valid-parentheses.md)
## [Binary search](algorithms/binary-search.md)
## [Two pointers](algorithms/two-pointers.md)
## [Sliding window](algorithms/sliding-window.md)
## [Breadth-first search](algorithms/breadth-first-search.md)
## [Depth-first search](algorithms/depth-first-search.md)
## [Heap / priority queue](algorithms/heap.md)
## [Dynamic programming](algorithms/dynamic-programming.md)
## [Memoization](algorithms/memoization.md)
## [Backtracking](algorithms/backtracking.md)
## [Linked list reversal](algorithms/linked-list-reversal.md)
## [Frequency count](algorithms/frequency-count.md)
