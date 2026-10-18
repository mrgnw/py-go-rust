# pygorst

Python / Rust / Go side-by-side cheatsheet. Static SvelteKit site, prerendered, hosted on Cloudflare Workers. Client JS only where a feature needs it (none yet).

PLAN.md: goals and status. SPEC.md: the parts model (finer-grained cross-language linking), agreed but not built; read it before touching the loader or `/lab`.

git: main-only

## Ports

- dev: 5237 (`pnpm dev`)
- preview: 5238 (`pnpm preview`, runs the built worker)

## Content

Sections live in `src/lib/content/langs/NN-name.md`, rendered in filename order. Format the loader depends on:

- One `# Title` at the top, then only `##` headings.
- Consecutive fenced code blocks render as side-by-side columns; a single fence is full width.
- Fence info string is `lang` or `lang Label` (`python`, `sh Rust`, `toml Cargo.toml`). Allowed langs are the `LANGS` list in `src/lib/content/langs/index.ts`; anything else fails the build.
- Python and Go snippets use tabs, Rust uses 4 spaces. Comments only to show output (`# => 3`).
- If every column in a row has the same `=> ` outputs in the same order, the loader strips them and shows them once in a leading Output column. Split a row when one line's output differs.
- Comment lines that are only dashes plus an optional label (`# --`, `// --- fallback`) are part markers (SPEC.md). The loader does not parse them yet and renders them as comments.

## Shipping

`pnpm ship` from a clean, pushed main.
