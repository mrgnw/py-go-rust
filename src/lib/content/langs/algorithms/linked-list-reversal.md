```python
class Node:
	def __init__(self, val, next=None):
		self.val, self.next = val, next

def reverse(head):
	prev = None
	while head:
		head.next, prev, head = prev, head, head.next
	return prev

vals = []
node = reverse(Node(1, Node(2, Node(3))))
while node:
	vals.append(node.val)
	node = node.next
print(vals)  # => [3, 2, 1]
```

```rust
struct Node {
    val: i32,
    next: Option<Box<Node>>,
}

fn reverse(mut head: Option<Box<Node>>) -> Option<Box<Node>> {
    let mut prev = None;
    while let Some(mut node) = head {
        head = node.next.take();
        node.next = prev;
        prev = Some(node);
    }
    prev
}

let mut list = None;
for val in [3, 2, 1] {
    list = Some(Box::new(Node { val, next: list }));
}
let mut vals = Vec::new();
let mut cur = reverse(list);
while let Some(node) = cur {
    vals.push(node.val);
    cur = node.next;
}
println!("{vals:?}"); // => [3, 2, 1]
```

```go
type Node struct {
	Val  int
	Next *Node
}

func reverse(head *Node) *Node {
	var prev *Node
	for head != nil {
		head.Next, prev, head = prev, head, head.Next
	}
	return prev
}

func main() {
	var vals []int
	for n := reverse(&Node{1, &Node{2, &Node{3, nil}}}); n != nil; n = n.Next {
		vals = append(vals, n.Val)
	}
	fmt.Println(vals) // => [3 2 1]
}
```

Python and Go rotate three pointers in one tuple assignment. Rust has no shared mutable pointers: the list is `Option<Box<Node>>`, and `take()` moves the tail out before the node is re-linked. This is the ownership model in one function, and it is why linked lists are the hardest interview topic in Rust.
