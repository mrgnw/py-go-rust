---
title: Command palette to search and jump to a section
---

# Command palette

`⌘K` / `Ctrl+K` (and a small button in the nav for mouse users) opens a search box listing every section across all pages. Typing filters; Enter navigates; arrow keys move; Escape closes.

## Data

The site is prerendered with no hydration, so the index has to be in the HTML. Emit one `<script type="application/json" id="sections">` in `src/routes/+layout.svelte` with `[{ page, title, href }]` for every `group` and `h2` block of every `LangPage` (`langPages` from `src/lib/content/langs.ts`; the layout already loads pages for the nav). About 60 entries, a few KB. Group name goes in as context (`Collections › Sets`).

## UI

- Native `<dialog>` with `showModal()`. Backdrop and Escape come for free. One `<input type="search">` and a `<ul>` of results. Markup lives in `+layout.svelte` so it is on every page; styled with Tailwind classes like the rest of the layout.
- Filtering: lowercase substring match on `title` and group, plus the page name. No fuzzy library. Cap the list at 12 rows.
- Keyboard: `ArrowDown` / `ArrowUp` move `aria-selected`, `Enter` sets `location.href` to the result's href, `Escape` closes. Clicking a row navigates.
- Same-page anchors: after navigating to `#id` the section tracker in `inlineScript` updates on scroll, nothing extra to do.

## Where

Everything client-side goes into the existing `inlineScript` string in `+layout.svelte`. Open on `keydown` with `(e.metaKey || e.ctrlKey) && e.key === 'k'`; `preventDefault` so the browser's address bar shortcut does not fire. Ignore the shortcut when focus is in an input other than the palette's.

## Coordinate

[keyboard-shortcuts](keyboard-shortcuts.md) adds a global `keydown` listener in the same string. Land this first, or do both in one worktree, so the two listeners share one handler and one "focus is in a field" guard.
