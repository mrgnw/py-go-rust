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
- `=> ` outputs never render as comments. They render as an output strip under the code: once for the whole row when every column prints the same value (quote style and `True`/`true` spelling are ignored), otherwise one strip per column. Split a row when one line's output differs and the shared strip matters.
- Comment lines that are only dashes plus an optional label (`# --`, `// --- fallback`) are part markers (SPEC.md). The loader does not parse them yet and renders them as comments.

Execute a content file's snippets and diff outputs against the `=>` comments:

```sh
uv run analysis/run_snippets.py src/lib/content/langs/50-algorithms.md
```

## Shipping

`pnpm ship` from a clean, pushed main.
