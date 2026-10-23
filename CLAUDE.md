# pygorst

Python / Rust / Go side-by-side cheatsheet. Static SvelteKit site (adapter-static), served as Cloudflare Workers static assets with no Worker script; unknown URLs get the prerendered `/404` page. Client JS only where a feature needs it: hydration is on (`csr` default) for the sections sidebar, which comes from the `section-nav` package (github:mrgnw/section-nav, API in its SPEC.md); the rest of the interactivity is the inline script in `+layout.svelte`.

PLAN.md: goals and status. SPEC.md: the parts model (finer-grained cross-language linking), agreed but not built; read it before touching the loader or `/lab`.

git: main-only

## Ports

- dev: 5237 (`pnpm dev`)
- preview: 5238 (`pnpm preview`, serves `build/` with wrangler; build first)

## Content

Pages live in `src/lib/content/langs/NN-name.md`, rendered in filename order. Format the loader depends on:

- One `# Title` at the top, then `##` sections. A page may group sections component-party style: `##` becomes the group and `###` the section as soon as the file has any `###`. Section ids come from the section title either way, so anchors survive regrouping.
- A section heading that is only a link to a `.md` file (`## [Binary search](algorithms/binary-search.md)`) takes its body from that file. The page file holds the titles, groups and order; `langs/<page>/` holds one file per section, with no headings, named freely. A missing, twice-linked or unlinked section file fails the build.
- Consecutive fenced code blocks render as side-by-side columns; a single fence is full width.
- Fence info string is `lang` or `lang Label` (`python`, `sh Rust`, `toml Cargo.toml`). Allowed langs are the `LANGS` list in `src/lib/content/langs.ts`; anything else fails the build.
- Python and Go snippets use tabs, Rust uses 4 spaces. Comments only to show output (`# => 3`).
- `=> ` outputs never render as comments. Each column renders them as an output strip under its code. Put `# => x` after the code that prints it, or on a line of its own for output that one line prints several times (a loop body), in the order printed. `=>~` marks lines that may print in any order (map iteration); they render the same. In a row with parts, hovering a part lights its output lines and hovering an output line lights its part. A word that another printing column lacks on the same output line of the same part is colored by language (Python blue, Rust orange, Go teal), along with the punctuation glued to it (`Some(4)`); everything shared stays neutral. Quote style and `True`/`true` spelling count as the same value.
- Comment lines that are only dashes plus an optional label (`# --`, `// --- fallback`) are part markers (SPEC.md). The loader drops the marker lines and keeps every other line, blank lines included, so the code reads as written; parts are invisible until a hover tints the same part in every column and shows its label. Two dashes open a part, three open a child inside it (the If-else branches); text before the first child marker is the first child. Hovering a child tints it and, lighter, its parent. Every column in a row needs the same tree: the same number of parts at each level, or the build fails naming the section. Leave a marker with nothing under it where a language has no equivalent. At most 2 levels and 8 parts per level.

- Variables: hovering a name lights it in every column of the row and shows its value at the end of the line; hovering a line that sets names shows theirs. Columns pair a name by lowercase without underscores (`max_retries` = `maxRetries`). Values come from `src/lib/content/vars.json`, written by `analysis/capture_vars.py`, which runs every program twice and keeps values that match. After changing python/rust/go code, recapture (a page path limits it to that page). The build warns about fences missing from vars.json; they render without variable hover.

```sh
uv run analysis/capture_vars.py src/lib/content/langs/10-compare.md
```

Execute a page's snippets (linked sections included), or one section file's, and check that every `=>` line is printed, in order:

```sh
uv run analysis/run_snippets.py src/lib/content/langs/15-algorithms.md
uv run analysis/run_snippets.py src/lib/content/langs/algorithms/heap.md
```

## Shipping

`pnpm ship` from a clean, pushed main.
