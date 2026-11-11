# pygorst

Python, Rust and Go side by side. A cheatsheet for a Python developer learning Rust and Go: when to pick each, the same pattern written in all three, then the concepts each language does differently.

Live site: https://pygors.xces.workers.dev

## Who it is for

A Python developer who writes scripts and wants to reach for Rust or Go for heavier work.

## What is in it

- When to pick each language.
- 37 patterns in 8 groups (strings, collections, control flow, types, errors, I/O, concurrency, tooling), shown in three columns with the output of each program under it.
- 13 algorithm patterns (two pointers, heap, BFS, memoization, ...).
- One reference page per language for concepts Python lacks: ownership, goroutines, zero values.
- Hover a part of a snippet to light the same part in the other two languages, step through parts with the keyboard, pivot a group, copy a single part, reorder or hide languages, hover a variable to see its value.

Every snippet in the patterns and algorithms pages is executed in all three languages, and its `=>` output is checked. The three reference pages are reviewed but not executed yet.

## Built with

Svelte 5 and SvelteKit (prerendered, almost no client JavaScript), Tailwind 4, marked and Shiki for the markdown and highlighting, deployed as static assets on Cloudflare Workers. Python scripts in `analysis/` run the snippets and capture variable values.

## Run it

Needs Node 22 or newer and pnpm 10.

```sh
git clone https://github.com/mrgnw/pygorst.git
cd pygorst
pnpm install
pnpm dev
```

Open http://localhost:5237.

```sh
pnpm check
pnpm lint
pnpm build
pnpm preview
```

`pnpm preview` serves `build/` on http://localhost:5238 with Wrangler.

To check the snippets you also need [uv](https://docs.astral.sh/uv/), Go 1.25 and stable Rust:

```sh
uv run analysis/run_snippets.py src/lib/content/langs/15-algorithms.md
```

## Configuration

| Variable        | Default | Purpose                                                                                                   |
| --------------- | ------- | --------------------------------------------------------------------------------------------------------- |
| `ALLOWED_HOSTS` | none    | Comma-separated extra hostnames the dev server accepts, for example `ALLOWED_HOSTS=.example.com pnpm dev` |

Content lives in `src/lib/content/langs/` as markdown. The format and the build checks are described in [CLAUDE.md](CLAUDE.md); the parts model is in [SPEC.md](SPEC.md).

## Roadmap

See [ROADMAP.md](ROADMAP.md) and the [open issues](https://github.com/mrgnw/pygorst/issues).

## AI assistance

Written with Claude Code. Snippets were reviewed and the patterns and algorithms pages were executed, but check anything you depend on.

## License

[MIT](LICENSE)
