# pygorst

Python / Rust / Go side-by-side cheatsheet. Static SvelteKit site, prerendered, hosted on Cloudflare Workers. Client JS only where a feature needs it (none yet).

PLAN.md: goals and status. SPEC.md: the parts model (finer-grained cross-language linking), agreed but not built; read it before touching the loader or `/lab`.

git: main-only

## Ports

- dev: 5237 (`pnpm dev`)
- preview: 5238 (`pnpm preview`, runs the built worker)

## Content

Sections live in `src/lib/content/langs/NN-name.md`, rendered in filename order. Format the loader depends on:

- One `# Title` at the top, then `##` sections. A page may group sections component-party style: `##` becomes the group and `###` the section as soon as the file has any `###`. Section ids come from the section title either way, so anchors survive regrouping.
- Consecutive fenced code blocks render as side-by-side columns; a single fence is full width.
- Fence info string is `lang` or `lang Label` (`python`, `sh Rust`, `toml Cargo.toml`). Allowed langs are the `LANGS` list in `src/lib/content/langs/index.ts`; anything else fails the build.
- Python and Go snippets use tabs, Rust uses 4 spaces. Comments only to show output (`# => 3`).
- `=> ` outputs never render as comments. Each column renders them as an output strip under its code. A word that another printing column lacks on the same output line is colored by language (Python blue, Rust orange, Go teal), along with the punctuation glued to it (`Some(4)`); everything shared stays neutral. Quote style and `True`/`true` spelling count as the same value.
- Comment lines that are only dashes plus an optional label (`# --`, `// --- fallback`) are part markers (SPEC.md). The loader drops the marker lines and keeps every other line, blank lines included, so the code reads as written; parts are invisible until a hover tints the same part in every column and shows its label. Every column in a row needs the same number of parts, or the build fails naming the section. Leave a marker with nothing under it where a language has no equivalent. Depth (`---`) is parsed as a plain boundary for now; at most 8 parts per row.

Execute a content file's snippets and diff outputs against the `=>` comments:

```sh
uv run analysis/run_snippets.py src/lib/content/langs/50-algorithms.md
```

## Shipping

`pnpm ship` from a clean, pushed main.
