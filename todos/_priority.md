# Priority

1. [copy-button-placement](done/1018-copy-button-placement.md) — done, PR #2, per-part copy in PR #14
2. [granular-output-diff](done/1018-granular-output-diff.md) — done, PR #3
3. [command-palette](done/1018-command-palette.md) — done, PR #4
4. [keyboard-shortcuts](done/1018-keyboard-shortcuts.md) — done, PR #4
5. [parts-hover-link](done/1018-parts-hover-link.md) — done, PR #5
6. [drag-reorder-languages](drag-reorder-languages.md) — maybe

## Context every agent needs

Read `CLAUDE.md`, `PLAN.md` and, for 5, `SPEC.md`. Then:

- Prerendered site, `csr = false`. No hydration. Client behaviour is the one `inlineScript` string in `src/routes/+layout.svelte` (copy button, language picker, section tracker). Add to it, don't add a second script or turn on hydration. State goes on `<html>` as `data-*` plus localStorage, styled from `src/routes/layout.css`.
- No `$effect`. Svelte 5 runes and snippets. Tabs, prettier config in repo. No comments unless the task says so.
- Rendering: `src/lib/content/langs.ts` turns markdown into `Block`s; `src/lib/LangPage.svelte` renders them. Each code row is one bordered block, columns in a CSS grid with subgrid rows `label / code / output`. Column `data-lang` drives the picker's hide rules.
- Work in a worktree on a branch from `origin/main`. Verify with `pnpm check && pnpm build`. Visual check: `pnpm cfb` uploads a preview at `https://<branch>-pygors.xces.workers.dev`; use that instead of starting a dev server (5237 is taken by the main checkout's pitchfork daemon). Merge through a PR, rebased, `gh pr merge --rebase`. `pnpm ship` only from main.
- Commit per concern, push after each commit, Co-Authored-By trailer.
- Done: move the todo to `todos/done/MMDD-name.md` with `branch:` or `pull-request:` in its frontmatter, tick or add the PLAN.md line.

Follow the `concise-output` skill. Final report under 2000 characters, outcomes not process.
