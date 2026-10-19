# pygorst — parts spec

Status: design agreed. Parts (two levels), the build checks, hover-link, pivot and expand are built. Read PLAN.md for context. The goal is to compare
the same idea across Python, Rust and Go at finer grain than a whole snippet:
one `else if` against another `else if`, one print against its output.

## Model

A compare section is a tree of **parts**. Each part is the same idea in every
language. Associations are fixed at build time; the site only renders them.

```
Section { id, title, parts: Part[] }
Part    { id, label?, output?, python, rust, go, parts?: Part[] }
                               // each language: line range into that language's
                               // full snippet, or null = no equivalent
```

- The build highlights each language's whole snippet once (shiki, one
  `<span class="line">` per line). A part is a line range into that. Columns
  view renders the whole; other views render ranges. Blank lines between parts
  belong to nobody: no range points at them.
- Every section and part has an id, so `/compare#if-else/zero-case` resolves.
  Id is the slugified label, else the part's index path (`if-else/2/1`).
- Nesting is two levels below the section: a group (the whole `if/else if/else`
  chain) and its parts (each branch). Deeper is not needed.

## Authoring

Markers are lines inside the existing fences. Nothing else about the content
format changes; sections without markers behave exactly as today.

```python
n = 15
label = 'big' if n > 10 else 'small'
# -- sign
if n < 0:
	sign = '-'
# ---
elif n == 0:
	sign = '0'
# --- fallback
else:
	sign = '+'
# --
print(label, sign)  # => big +
```

- A marker is a comment line in the fence's language whose text is only dashes
  and an optional label: `# --` in Python, `sh` and `toml`, `// --` in Rust and
  Go. Two dashes open a depth-1 part, three a depth-2 part. Like markdown
  headings: a marker closes open parts at its depth or deeper, then opens a
  new one. Text before the first marker is the first part.
- The label after the dashes is optional. Unnamed markers work; alignment never
  depends on names.
- Alignment is positional: the k-th marker at a depth, under the same parent,
  pairs across languages. Two consecutive markers make an empty part (`null`)
  for that language: use it when a language has no equivalent (Go has no
  ternary).
- A line with `# =>` / `// =>` output is its own leaf, labelled by its output,
  as the current loader already does. Markers add boundaries; they do not
  replace that rule.
- Markers are stripped before highlighting. They are comments so every snippet
  stays runnable, and the current loader renders them as plain comments until
  the parser lands, so markers can be authored and committed section by
  section ahead of step 2. "Comments only to show output" still holds for
  everything that is not a marker.

## Build rules

Fail the build, naming the section and language, when:

- sibling counts differ across languages under the same parent
  (`if-else: python has 3 parts, go has 4`)
- labels are given on all languages for a part and disagree
- a marker is deeper than two levels, or depth 2 appears without a depth-1 parent

## Views

All read the same frozen tree. Still no hydration (`csr = false`): every view
is prerendered markup, and the one inline script in the layout only toggles
attributes. Expand prerenders both layouts and swaps `hidden`, so it never
needed client-side Svelte. Flip `csr` only for a view that has to build markup
in the browser.

1. **Columns** (default, unchanged): whole snippets side by side in one block,
   an output strip under each column, colored by language when that output is
   the odd one out.
2. **Hover-link**: in columns, hovering or tapping a part highlights the same
   part in the other columns. No new layout; try this first, it tests whether
   part boundaries feel right.
3. **Pivot** (`/lab` today): output on top, each language's line(s) stacked,
   `py` / `rs` / `go` labels in the left gutter outside the box. Good for
   one-liners, bad for multi-line definitions.
4. **Expand**: tap a group in columns to show its parts pivoted inline.

## Current state

- `src/lib/content/langs.ts`: each column is a tree, `Col.parts: Part[]`, where
  `Part { path, label?, html, pad, parts }`. A leaf has `html` and empty
  `parts`; a group has `parts` and no lines of its own. `path` (`2`, `2.1`) is
  the same in every column, so `cols.map((c) => c.parts[2].parts[1])` is one
  part across languages. `checkShape()` fails the build on mismatched trees.
  Not built yet: label agreement check, `null` for empty parts (they are leaves
  with empty `html`), per-part output.
- Hover-link: `LangPage.svelte` puts `data-part={path}` on every `.part`; a
  `mouseover` handler in the layout's inline script sets `data-lit` on the
  hovered part and its ancestors in every column of the row.
- Each leaf carries its own `output` (its `=>` lines). The column's output
  strip is still built per fence in `codeRow()`.
- Pivot: `src/lib/Pivot.svelte` renders any list of parts across columns, one
  box per leaf: the output on top when every language prints the same value
  (else under each language's lines), then each language's lines with a
  `py` / `rs` / `go` gutter label. Languages with an empty part are skipped.
  `/lab` uses it on the first row of every Patterns section with parts. Not in
  the nav, `noindex`.
- Expand: every group (top-level part with children) in a row prerenders a
  hidden `[data-split]` view: columns for the parts before it, `Pivot` for its
  children, columns for the parts after it plus the output strips. Tapping the
  group, or its `pivot` button, swaps the views; tapping the pivot, or its
  `columns` button, swaps back. Keyboard activation moves focus to the other
  button. The language picker's hide rules apply in every view.

## Next

Steps 1-4 (markers, tree and build checks, hover-link, pivot and expand) are done.

1. Label agreement check (Build rules) when a section first needs it.
2. More groups (`---` markers): only If-else has one, so only it expands.
3. Keyboard stepping (`.` / `,`) treats the split view's column blocks as
   separate rows and skips the pivot.

Open: parts like `} else if n == 0 {` are honest but ugly stacked. Keep, or
let an author mark scaffolding lines. Decide after seeing step 3.
