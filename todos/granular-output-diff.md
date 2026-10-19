---
title: Color only the tokens that differ in an output strip
---

# Granular output diff

Today an output strip is all-or-nothing: `odd` on a `Col` colors the whole strip in the language's color when no other column prints the same value (`codeRow()` in `src/lib/content/langs.ts`, `.out.odd` rules in `src/lib/LangPage.svelte`).

Wanted: Python `8080`, Rust `8080 true`, Go `8080 true true` show `8080` neutral everywhere and only the extra `true`s colored.

## Decision: option (a), intersection across columns

A token is colored when at least one other column that prints output lacks it on the same line. Equivalent: tokens outside the multiset intersection of all printing columns. Option (b) ("differs from the nearest other column") was rejected: `uv run analysis/output_diff_granularity.py` prints both over every differing row in the content. (b) leaves Go's `true` unmarked in Basic types while Python prints `false`, and marks Python's `4.0` in Modules but not the `4` next to it. (a) is also what the single-pass tokenizer gives for free.

## Rules, from the analysis output

- Compare line by line. Each `=>` comment is one line; line k in one column is compared with line k in the others. A column with fewer lines just has nothing to compare against for the extra lines, so those lines are fully colored.
- Columns without any output are ignored (Mental model shifts: Rust prints nothing there; without this rule everything in Python and Go would light up).
- Normalise before comparing, as `sameValue()` does now: `'` → `"`, `True`/`False` → lowercase.
- Tokens: `[A-Za-z0-9_.]+` and single other characters. Punctuation-only tokens are never colored. Python `[1, 2, 3]` vs Go `[1 2 3]` must not color every comma, and `"ann"` vs `ann` must not color the quotes. The words are the signal.
- When a line's tokens are all different from the other columns (Mutable vs immutable: `[1, 2, 3]` vs `[9 2]`), coloring every word is correct and reads as today's whole-strip color. No special case.
- Only one language printing something (a row with a single output column) stays neutral, as today (`fences.length > 1` guard).

## Implementation

- Replace `odd?: boolean` on `Col` with the output HTML already carrying `<span class="diff">` around colored tokens. Build the output HTML by hand in `codeRow()` rather than through shiki: the output fence is `text`, shiki adds nothing but wrapper markup. Escape HTML. Keep the `<pre class="shiki">` shape or update the `.langs :global(.out pre.shiki)` selectors to match the new markup; the existing padding and font-weight rules should keep applying.
- CSS: `.out .diff { color: var(--odd) }` with the three `[data-lang=...] .out { --odd: ... }` rules that already exist. Delete the `!important` override on `.out.odd pre.shiki span`.
- `pivot()` / `/lab` use `outputs[0]` and the `shared` flag; untouched.
- Add the rule to CLAUDE.md "Content" (one sentence replacing "A value no other column in the row prints is colored by language") and tick a PLAN.md line.
- Check in the preview: Variables & constants (only Go's `0` colored), Basic types & conversion, Lists / Vec / slices (`Some(` `)` colored in Rust, nothing else), Error handling (message tails colored, `bad port "x"` neutral in all three).
