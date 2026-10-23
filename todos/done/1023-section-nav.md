---
branch: extract-sidebar-svelte-component
---

# Replace the sections sidebar with the shared `section-nav` component

The sidebar has been extracted to https://github.com/mrgnw/section-nav (private; `~/dev/section-nav`, SPEC.md there is the API). pygorst becomes its first SvelteKit consumer. Goal: one implementation, so everything the layout does for the sidebar today is deleted here.

## Steps

1. `pnpm add -D github:mrgnw/section-nav`. The package's `svelte` export points at TypeScript source, so no build step is needed. `import SectionNav from 'section-nav'`.
2. `src/lib/LangPage.svelte`: replace the `.sidebar-grid` div and its `<nav id="sections-nav">` with `<SectionNav sections={…} style="--nav-top: 4rem; --bar-top: <header height>">` wrapping the content div. Build `sections` from `page.blocks`: a `group` block becomes `{ id, title, group: true }`, an `h2` block `{ id, title }`, in order. Drop the `toc` derived. Measure the sticky header's height in the browser (the `<header>` with the top nav) for `--bar-top` so the mobile bar sticks right under it. Text colors should match the current look: set `--nav-muted` to the neutral-500 / neutral-400 pair via `light-dark()` if the default looks off.
3. `src/routes/+layout.svelte`: delete the sidebar code from the inline script: `html.dataset.sidebar` init, `syncSidebar`, `toggleSidebar`, `trackSections` and its call in `DOMContentLoaded`, `stepSection`, the `b`/`j`/`k` entries of `shortcut`, the `[data-sidebar-toggle]` click and the `#sections-nav` popover-closing click. Delete the header's `data-sidebar-toggle` button and the `.section-now` button; the component renders its own handle and mobile bar. Keep the `SHORTCUTS` help entries for `b`, `j k` since the component still implements them. The palette's `openPalette`/hash links still work unchanged.
4. `src/routes/layout.css`: delete `body:not(:has(#sections-nav)) …`, `.sections-nav`, the `.sidebar-grid` rules at 64rem, the whole 111rem block, and the `.sections-nav` / `.sidebar-grid` motion rules at the bottom. The 111rem "sidebar in the left margin" layout is dropped on purpose.
5. Verify with `pnpm dev` (port 5237) in the paseo browser: sidebar tracks on scroll, `b` collapses and survives reload, `j`/`k` step, under 64rem the bar shows the current section and opens the popover, palette (⌘K) still jumps to sections. `pnpm check` and `pnpm build` pass. The homepage (`/`) has no sidebar: confirm nothing from the component leaks there.
6. Update CLAUDE.md: the sidebar comes from `section-nav`; "Client JS only where a feature needs it" now includes that component's hydration. PLAN.md status line for the sidebar points at the package.

## Known trade-offs, already accepted

- The collapsed state used to be applied on `<html>` before first paint. Now it is applied when the component hydrates, so a collapsed sidebar flashes for a frame on load.
- Nav styling moves from Tailwind utilities to the component's CSS; small visual differences are fine, large ones go back to section-nav as a fix, not into pygorst overrides.
