---
title: Copy button on the label line, per part later
pull-request: 2
---

# Copy button placement

Today: one absolutely positioned `Copy` button in the top right of every snippet (`.copy` in `src/routes/layout.css`, markup from `highlight()` in `src/lib/content/langs.ts`, handler in the `inlineScript` of `src/routes/+layout.svelte`). It overlaps long first lines.

## Do

1. Move the whole-snippet button to the right end of the label row (`Python`, `Rust`, `Cargo.toml`), same row as the language name. The label snippet lives in `LangPage.svelte`; the button is currently inside `col.html`, so either move the button markup out of `highlight()` into the label snippet, or render it in the label snippet and drop it from `highlight()`. Keep `button.parentElement.querySelector('pre')` working or update the click handler to find the column's `pre` from the label.
2. Per-part copy on hover. Blocked on the parts parser ([parts-hover-link](parts-hover-link.md)); until parts exist, add per-line copy for fences where every line is its own command, i.e. `sh` fences (`uv init hello && cd hello`, `uv add httpx`, ...). Button appears at the end of the line on hover, copies that line without the `=>` comment (already stripped by the loader). CSS only for show/hide (`:hover`), same delegated click handler.
3. When parts land, switch the per-line rule to per-part: one button per part, one line in simple examples, several lines in longer ones.

## Don't

- No hydration, no component state. Delegated click handler, `data-copy` gate for clipboard support stays.
- Copied feedback: current `Copied` text swap for 1.5 s is fine; keep it.
- Print: `.copy` already hidden under `@media print`; keep that for the new buttons.

## Status

Steps 1 and 2 done. Step 3 (per-part copy) is still open until the parts parser lands.
