---
title: Parse part markers and highlight the matching part across languages on hover
pull-request: 5
---

# Parts: parser + hover link

Read SPEC.md first. It defines parts: a code row is split by comment lines that are only dashes plus an optional label (`# --`, `// --`, `# --- fallback`; two dashes depth 1, three depth 2). Part k in Python lines up with part k in Rust and Go. Nothing parses them yet; they render as comments.

## Step 1: author markers

Add markers to three Patterns sections: If-else, Interfaces, Error handling (`src/lib/content/langs/10-compare.md`). Markers are comments in the fence's language. Every column in a row gets the same number of parts in the same order; where a language has no code for a part, the marker still appears with nothing under it. Run `uv run analysis/run_snippets.py src/lib/content/langs/10-compare.md` after: outputs must still match.

## Step 2: parse

In `src/lib/content/langs.ts`, `codeRow()`: split each fence's text at marker lines before highlighting, highlight each part separately, and emit `parts: { label?: string; html: string }[]` on `Col`. Rows without markers produce one part. Keep `output` per column as is (outputs sit at the end of the row). The `=>` stripping already happens per line and works unchanged inside parts. Fail the build when columns in one row disagree on part count, with the section title in the error.

Render in `src/lib/LangPage.svelte`: inside a column's code cell, one `<div class="part" data-part={k}>` per part, label as a small muted caption when present. Keep the subgrid rows `label / code / output`; parts are inside the code row, so output strips still align. Dividers between parts: a hairline border-top on `.part + .part`.

## Step 3: hover link

CSS first: `.cols:has([data-part="0"]:hover) [data-part="0"]` background tint, repeated for the handful of indices that exist (count the max part count in content and generate that many rules, or emit a `style` attribute per part setting `--part: k` and match with one `:has()` rule plus `[data-part]` attribute selectors). No JS unless `:has()` can't express it; it can for a fixed small index range. Dim nothing, only tint the linked parts, so hidden columns and single-part rows look unchanged.

Not every row maps 1:1:1; a part present in one language and empty in another just has no tint partner. That is fine and expected.

## After

Flip the PLAN.md parts item, update CLAUDE.md "Content" (markers are now parsed; the rule about equal part counts), and tell [copy-button-placement](copy-button-placement.md) step 3 can start. The `/lab` pivot prototype stays as is.
