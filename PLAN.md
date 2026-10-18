# pygorst — plan

## Goal

A cheatsheet for a Python developer learning Rust and Go on the side, in the spirit of https://component-party.dev (same thing, side by side) with content depth from https://learnxinyminutes.com. Published as a public static site.

The reader should be able to:

1. Decide which language to reach for. Working assumption: Python for scripts and occasional light work, Go for network and concurrent services, Rust for long-running heavy processes. The overview section refines this.
2. Look up how a familiar Python pattern is written in Rust and Go, side by side.
3. Read the concepts each language has that Python does not (ownership, goroutines, zero values, ...), explained against Python.

## Structure (done)

| Section                    | File                                   | Status                                                 |
| -------------------------- | -------------------------------------- | ------------------------------------------------------ |
| When to pick each          | `src/lib/content/langs/00-overview.md` | written, reviewed                                      |
| Side by side (37 patterns) | `10-compare.md`                        | written, every snippet executed in all three languages |
| Python                     | `20-python.md`                         | written, reviewed, not executed                        |
| Rust                       | `30-rust.md`                           | written, reviewed, not executed                        |
| Go                         | `40-go.md`                             | written, reviewed, not executed                        |

Renderer: `src/lib/content/langs.ts` parses the markdown with marked, highlights fences with shiki, and turns consecutive fences into columns. `src/routes/[[slug]]` renders one prerendered page per section. Content format rules are in CLAUDE.md.

## Next

- [ ] Publish, later: content first. Until then `pnpm dev` locally and `wrangler versions upload` for a workers.dev preview. When ready, pick the domain, add a `custom_domain` route to `wrangler.jsonc`, `pnpm ship` from main.
- [x] Per-section pages: `/`, `/compare`, `/python`, `/rust`, `/go` via `src/routes/[[slug]]`, nav in the layout.
- [x] Sticky side table of contents from 64rem up. No active-section highlight: scroll-driven animations and `scroll-target-group` are not Baseline as of Oct 2026; revisit when they are.
- [x] Copy button per snippet: one inline script in `+layout.svelte`, hidden when `navigator.clipboard` is missing.
- [x] "Python → Rust → Go" index lives in the overview, every row linked to its compare section. Decorator, `with`, `uv` and `ruff` rows have no compare section yet.
- [x] Shared Output column: when every column of a row prints the same thing, the `# =>` comments are stripped and shown once, first.
- [x] Compare sections for the four index rows that had none: decorator, `with`, `uv` / `cargo` / `go mod`, `ruff` / `clippy` / `go vet`. Code snippets executed, commands run once.
- [ ] Parts: compare at finer grain than a whole snippet, with the languages linked part by part. Design in SPEC.md, pivot prototype at `/lab`. Markers are comments (`# --`, `// --`), so authoring can land before the parser. Next step is markers on three sections, then the parser.

## Ideas, not committed to

- Execute the Python, Rust and Go section snippets the way the compare section was (extract each fence, run it, diff the `# =>` comments against real output). Not needed while this is a reference sheet; reviewed snippets are enough.
- Add more patterns to the compare section: string building, regex, logging, sleep/timers, process spawning, SQLite, Unicode handling, package publishing.
- A fourth column toggle for TypeScript or Zig, if the reader list ever grows. The renderer already handles N columns.
- Link each `##` to the relevant learnxinyminutes or official docs anchor.

## Constraints

- Client JS only for features that need it. Pages stay prerendered; `csr = false` today, flips when the first interactive view (SPEC.md) lands.
- Dark mode is CSS only (`color-scheme: light dark` + shiki `light-dark()`); don't add a toggle that needs state.
- Snippets must be correct for Python 3.14 + uv, Rust stable 2024 edition, Go 1.25. Only comments that show output.
- git: main-only. Ports 5237 (dev) and 5238 (preview).
