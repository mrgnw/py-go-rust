---
title: Drag the picker chips to reorder language columns
---

# Drag to reorder languages (maybe)

Open question whether this is worth it. Cheaper alternative that covers most of the need: clicking a picker chip while holding Shift moves that language to the first column. Decide before building; if the drag version is wanted, the shape is:

- Order lives on `<html>` as `data-order="python rust go"`, persisted in localStorage like `data-hide`.
- Columns get `style="order: N"` from CSS: `html[data-order^="rust"] [data-lang="rust"] { order: -1 }` is not enough for three slots, so set `--order-python`, `--order-rust`, `--order-go` on `<html>` from the script and use `[data-lang="python"] { order: var(--order-python) }` in `layout.css`. `.cols` is a grid with `grid-auto-flow: column`; `order` works on grid items. The `margin-left: -1px` divider trick does not depend on DOM order.
- Dragging the chips: native HTML drag and drop on the `[data-pick]` buttons (`draggable`, `dragstart`, `dragover`, `drop`) in the `inlineScript` of `src/routes/+layout.svelte`. Reorder the chips in the DOM, write the new order to `data-order`, update the three CSS variables.
- Touch: native drag and drop does not fire on touch in most browsers. Either accept it (desktop feature) or add the Shift-click fallback above for everyone.

No library. No hydration.
