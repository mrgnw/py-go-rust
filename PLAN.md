# pygorst — plan

## Goal

A cheatsheet for a Python developer learning Rust and Go on the side, in the spirit of https://component-party.dev (same thing, side by side) with content depth from https://learnxinyminutes.com. Published as a public static site.

The reader should be able to:

1. Decide which language to reach for. Working assumption: Python for scripts and occasional light work, Go for network and concurrent services, Rust for long-running heavy processes. The overview section refines this.
2. Look up how a familiar Python pattern is written in Rust and Go, side by side.
3. Read the concepts each language has that Python does not (ownership, goroutines, zero values, ...), explained against Python.

## Structure (done)

| Section                  | File                                   | Status                                                 |
| ------------------------ | -------------------------------------- | ------------------------------------------------------ |
| When to pick each        | `src/lib/content/langs/00-overview.md` | written, reviewed                                      |
| Patterns (37, 8 groups)  | `10-compare.md`                        | written, every snippet executed in all three languages |
| Python                   | `20-python.md`                         | written, reviewed, not executed                        |
| Rust                     | `30-rust.md`                           | written, reviewed, not executed                        |
| Go                       | `40-go.md`                             | written, reviewed, not executed                        |
| Algorithms (13 patterns) | `15-algorithms.md`                     | written, every snippet executed in all three languages |

Renderer: `src/lib/content/langs.ts` parses the markdown with marked, highlights fences with shiki, and turns consecutive fences into columns. `src/routes/[[slug]]` renders one prerendered page per section. Content format rules are in CLAUDE.md.

## Next

- [x] Live at https://pygors.xces.workers.dev since 2026-10-18 (`pnpm ship` from main). Branch previews: `pnpm cfb` gives `<branch>-pygors.xces.workers.dev`; push-to-preview needs the GitHub repo connected under the Worker's Builds settings in the dashboard. Custom domain still open: add a `custom_domain` route to `wrangler.jsonc`.
- [x] Per-section pages: `/`, `/compare`, `/python`, `/rust`, `/go` via `src/routes/[[slug]]`, nav in the layout.
- [x] Sticky side table of contents from 64rem up, grouped on the Patterns page, current section highlighted by a small inline scroll listener (no hydration).
- [x] Copy button per snippet: one inline script in `+layout.svelte`, hidden when `navigator.clipboard` is missing.
- [x] "Python → Rust → Go" index lives in the overview, every row linked to its compare section. Decorator, `with`, `uv` and `ruff` rows have no compare section yet.
- [x] Output strips: `# =>` comments are stripped from code and shown under each column. An output only one language prints takes that language's color (blue / orange / teal, mockup in `mockups/output-colors.html`); matches stay neutral. Quotes and boolean spelling are ignored when comparing.
- [x] Granular output diff: only the tokens another column lacks on the same line take the language color (`8080` stays neutral, the extra `true`s light up). Punctuation is colored only when glued to a colored word.
- [x] Output diff keeps brackets paired: the unmatched wrapper (`Some(` ... `)`) is colored as a pair, brackets shared with another column stay neutral. Check: `node analysis/check_diff_line.ts`.
- [x] Compare sections for the four index rows that had none: decorator, `with`, `uv` / `cargo` / `go mod`, `ruff` / `clippy` / `go vet`. Code snippets executed, commands run once.
- [x] Language picker: `py` / `rs` / `go` toggles in the nav hide a language's columns on any page that has more than one. Inline script plus `data-hide` on `<html>`, persisted in localStorage; no hydration.
- [x] Parts: compare at finer grain than a whole snippet, with the languages linked part by part. Design in SPEC.md, pivot prototype at `/lab`. Markers (`# --`, `// --`) are parsed into flat parts on If-else, Interfaces and Error handling; hovering a part tints the same part in every column (CSS `:has()`, no JS).
- [x] Keyboard stepping through parts: `.` / `,` move across rows, Esc clears; the active part tints like hover (`data-part-active`).
- [ ] Parts, next: markers on more sections, nesting (`---` is still flat), then pivot and expand against real parts (SPEC.md "Views").

Handoff tasks for parallel agents: `todos/_priority.md`.

## Ideas, not committed to

- Execute the Python, Rust and Go section snippets with `analysis/run_snippets.py` (used for compare and algorithms). Their Go fences omit `func main`, so the runner needs a wrap rule first.
- Add more patterns to the compare section: string building, regex, logging, sleep/timers, process spawning, SQLite, Unicode handling, package publishing.
- A fourth column toggle for TypeScript or Zig, if the reader list ever grows. The renderer already handles N columns.
- Link each `##` to the relevant learnxinyminutes or official docs anchor.

## Constraints

- Client JS only for features that need it. Pages stay prerendered; `csr = false` today, flips when the first interactive view (SPEC.md) lands.
- Dark mode is CSS only (`color-scheme: light dark` + shiki `light-dark()`); don't add a toggle that needs state.
- Snippets must be correct for Python 3.15 + uv, Rust stable 2024 edition, Go 1.25. Only comments that show output.
- git: main-only. Ports 5237 (dev) and 5238 (preview).
