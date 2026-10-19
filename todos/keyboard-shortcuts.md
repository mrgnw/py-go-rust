---
title: Keyboard shortcuts for language toggles and navigation
---

# Keyboard shortcuts

| Key | Action |
|-|-|
| `1` `2` `3` | toggle Python / Rust / Go, same as clicking the picker |
| `j` / `k` | next / previous section (the `h2`/`h3` targets the sidebar links point at) |
| `n` / `p` | next / previous code row (`.cols` blocks) |
| `?` | show the shortcut list |

Scroll with `scrollIntoView({ block: 'start' })`; the headings already have `scroll-mt-14` so the sticky nav does not cover them.

## Where

The `inlineScript` string in `src/routes/+layout.svelte`. One `keydown` listener on `document`. Skip when `event.target` is an input, textarea, select, or `contenteditable`, or when a modifier other than Shift is held. The picker toggle logic (`hidden` set on `html.dataset.hide`, localStorage, `syncPicker()`) exists in the click handler; pull it into a `toggleLang(name)` function and call it from both.

"Current section" for `j`/`k`: reuse what `trackSections()` computes (the link with `aria-current`); move to its neighbour. On pages without the sidebar (overview) `j`/`k` do nothing.

Shortcut list for `?`: a `<dialog>` with a two-column table, static markup in the layout. Show the hint `?` in the nav next to the picker so the feature is discoverable.

## Coordinate

[command-palette](command-palette.md) adds `⌘K` in the same string and needs the same "focus is in a field" guard. Build on top of it or in the same worktree.
