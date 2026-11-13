# Contributing

Help Python developers learn Rust and Go through small, idiomatic examples of the same task. Corrections, clearer explanations and new patterns are welcome.

Read the [quick start](README.md#quick-start) for local setup. To execute snippets, install uv, Go and stable Rust. The checker selects Python 3.15 and Go 1.25.0; the first run can download toolchains, Python packages and Rust crates.

## Choose a change

Check the [open issues](https://github.com/mrgnw/py-go-rust/issues) and [roadmap](ROADMAP.md). For a new pattern, open the [new pattern form](https://github.com/mrgnw/py-go-rust/issues/new?template=new-pattern.yml) with the Python task, its Rust and Go equivalents, and expected output. Keep a pull request focused on one pattern or correction.

Fork the repository and create a branch in your fork. A small prose correction needs only the site checks; changes to executable examples also need the snippet checker and variable capture below.

## Find the content

- `src/lib/content/langs/10-compare.md`: Patterns, grouped by `##` headings, with a `###` heading for each section.
- `src/lib/content/langs/15-algorithms.md`: Algorithm headings and links to section files.
- `src/lib/content/langs/algorithms/`: One file per algorithm section, without headings.
- `src/lib/content/langs/20-python.md`: Python reference.
- `src/lib/content/langs/30-rust.md`: Rust reference.
- `src/lib/content/langs/40-go.md`: Go reference.
- `src/lib/content/langs/00-overview.md`: Cross-language index; add a link for a new comparison.
- `src/lib/content/vars.json`: Generated variable values; update with the capture script.

File names determine page order. Each page starts with one `#` title. A page containing `###` headings treats `##` headings as groups. Use the existing section heading and fence conventions so anchors and sidebar entries stay consistent.

## Write a pattern

Start from a nearby section. Use consecutive `python`, `rust` and `go` fences for a side-by-side row. Explain the task and any language differences in prose. Prefer deterministic examples that run offline.

This minimal row demonstrates the content format:

````markdown
### Count items

```python
items = [2, 4, 6]
print(len(items))  # => 3
```

```rust
let items = vec![2, 4, 6];
println!("{}", items.len()); // => 3
```

```go
items := []int{2, 4, 6}
fmt.Println(len(items)) // => 3
```
````

Python and Go content uses tabs; Rust content uses four spaces. Code comments are for expected output and the structural part markers below. Put teaching explanations in prose. Supported fence languages are listed in [langs.ts](src/lib/content/langs.ts); unsupported languages fail the build.

For a new algorithm, add a heading-free Markdown file in `algorithms/`, then a link-only heading in `15-algorithms.md`, following the existing binary-search entry. Missing, duplicate and unlinked section files fail the build.

### Outputs and execution

- A section's fences of one language run together. A complete program with a main entry point runs alone. Rust and Go fragments receive the checker scaffolding and supported imports.
- Put `# => value` or `// => value` after the statement that prints it, or on separate lines for multiple output lines. Output is checked in order and shown below the snippet on the site.
- Use `=>~` only for a consecutive run of lines whose order can vary, such as map iteration.
- Python expressions with expected values can use interactive-style output; the checker prints their representation when the expression does not print itself.
- An example declaring an expected compiler error or panic runs alone and must fail with that text. Follow an existing reference-page example for the exact format.
- Use `!norun` only when an example cannot run in the checker. Explain why in nearby prose. Shell, TOML and text fences are not executed.

### Linked parts and pivot

Part markers link the same operation across languages. Use `# -- label` in Python and `// -- label` in Rust and Go. Three dashes introduce a child part that can appear in a pivoted group. Copy the structure of the existing If-else section before adding child parts.

Every column in a row must have the same part tree. Keep an empty marker when a language has no equivalent operation. The build permits at most two levels and eight parts per level, and rejects mismatched shapes. See [SPEC.md](SPEC.md) for the model.

## Check your change

For a Patterns change, execute the page and regenerate its hover values:

```sh
uv run analysis/run_snippets.py src/lib/content/langs/10-compare.md
```

```sh
uv run analysis/capture_vars.py src/lib/content/langs/10-compare.md
```

For an algorithm change, run the containing page so linked section files are included:

```sh
uv run analysis/run_snippets.py src/lib/content/langs/15-algorithms.md
```

```sh
uv run analysis/capture_vars.py src/lib/content/langs/15-algorithms.md
```

For a reference-page change, pass that page's path to both scripts. Capture skips unchanged sections and removes obsolete entries. Commit `vars.json` with the content so hover values match the edited code.

```sh
pnpm check
```

```sh
pnpm lint
```

```sh
pnpm build
```

Open your changed section locally and check all three columns, outputs, sidebar entry and overview link. If you added parts, check their linked highlights and pivot controls. Installation enables the pre-commit hook, which checks stale snippets and recaptures values when content is staged. CI runs formatting, Svelte/TypeScript checks and the static build; it does not run the snippet checker yet.

## Submit a pull request

Use the pull request template to explain what a Python reader learns, list the content files, and report the checks you ran. Include the issue number when relevant. For a correction, show the previous behavior and corrected result. Cite official language documentation for a new or disputed claim.

Write original examples. Preserve existing attribution and identify any adapted material and its license in your pull request. Disclose AI assistance and verify generated code yourself. Contributions use the project's [MIT license](LICENSE); the existing [sources and attribution](README.md#sources) remain applicable.
