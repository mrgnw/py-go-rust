# py-go-rust

Learn Rust and Go from the Python you already know: the same patterns side by side, with executed and checked snippets.

[**Explore the live cheatsheet →**](https://pygors.xces.workers.dev)

[![CI](https://img.shields.io/github/actions/workflow/status/mrgnw/py-go-rust/ci.yml?branch=main&style=flat&label=CI)](https://github.com/mrgnw/py-go-rust/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/github/license/mrgnw/py-go-rust?style=flat)](LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/mrgnw/py-go-rust?style=flat)](https://github.com/mrgnw/py-go-rust/commits/main)
[![Open issues](https://img.shields.io/github/issues/mrgnw/py-go-rust?style=flat)](https://github.com/mrgnw/py-go-rust/issues)
[![Svelte 5](https://img.shields.io/badge/Svelte-5-FF3E00?style=flat&logo=svelte&logoColor=white)](https://svelte.dev)
[![Tailwind 4](https://img.shields.io/badge/Tailwind-4-06B6D4?style=flat&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Live site](https://img.shields.io/badge/live%20site-pygors-2563EB?style=flat)](https://pygors.xces.workers.dev)

> [!NOTE]
> Built with AI assistance, including Claude Code and Codex. Snippets were reviewed and run with the checker below, but check anything you depend on.

[![Python, Rust and Go conditionals with their output in three columns](docs/media/side-by-side.png)](https://pygors.xces.workers.dev/compare#compare-if-else-ternary-ish)

Pivot a group to compare its branches one part at a time, then return to columns:

![Ten-second recording switching conditionals from columns to pivot and back](docs/media/pivot.gif)

The repository is named py-go-rust; the deployed site is still branded pygors.

## Who it is for

Python developers who write scripts and want to reach for Rust or Go for heavier work. Start with [when to pick each language](https://pygors.xces.workers.dev), then follow familiar Python code into the other two columns.

## What you can learn

- 37 patterns in 8 groups: strings, collections, control flow, types, errors, I/O, concurrency and tooling.
- 13 algorithm patterns, including two pointers, heaps, breadth-first search and memoization.
- A reference page per language covering concepts such as ownership, goroutines and zero values.
- Linked highlights across matching parts, keyboard stepping, group pivoting, copying individual parts, language reordering and hiding, and variable values on hover.

## What the checker verifies

The Python, Rust and Go code fences on every page are run by [analysis/run_snippets.py](analysis/run_snippets.py), and their `=>` output is checked in order. `=>~` allows a run of output lines in any order. Examples that declare an expected compile or runtime error must fail with that text; test examples must pass their test runner.

Nine fences on the three reference pages are marked `!norun` and skipped. Shell, TOML and text fences are not run. The checker runs locally and in a pre-commit hook; **CI does not run it yet** ([#9](https://github.com/mrgnw/py-go-rust/issues/9)). CI checks formatting, Svelte/TypeScript and the static build. Passing checks do not establish that an example is suitable for production.

## Quick start

Needs Node 22 or newer and pnpm 10. No Cloudflare account or analytics configuration is needed for local development.

```sh
git clone https://github.com/mrgnw/py-go-rust.git
```

```sh
cd py-go-rust
```

```sh
pnpm install
```

```sh
pnpm dev
```

Open http://localhost:5237.

```sh
pnpm check
```

```sh
pnpm lint
```

```sh
pnpm build
```

To inspect the built site locally, preview serves `build/` on http://localhost:5238 with Wrangler:

```sh
pnpm preview
```

The site is prerendered with Svelte 5 and SvelteKit, Tailwind 4, marked and Shiki. Python scripts run the snippets and capture variable values.

### Extra development hosts

The dev server accepts a comma-separated list of extra hostnames or domain suffixes through `ALLOWED_HOSTS`. A leading dot includes subdomains. Set your hostnames in the variable first:

```sh
ALLOWED_HOSTS=
```

```sh
ALLOWED_HOSTS="$ALLOWED_HOSTS" pnpm dev
```

## Add a pattern

1. Choose a small, deterministic example of the same task in all three languages. Check the [open pattern requests](https://github.com/mrgnw/py-go-rust/issues) first.
2. Add a `###` section under the appropriate group in [10-compare.md](src/lib/content/langs/10-compare.md), with consecutive Python, Rust and Go fences. For an algorithm, add a section file under [algorithms/](src/lib/content/langs/algorithms/) and link it from [15-algorithms.md](src/lib/content/langs/15-algorithms.md).
3. Give each printing snippet its expected `# =>` or `// =>` output. Add the pattern to the index in [00-overview.md](src/lib/content/langs/00-overview.md).
4. Run the checker and capture variable values, then check the site. The [contribution walkthrough](CONTRIBUTING.md) includes a minimal three-language example, part markers and the full review checklist.

Checking snippets also needs [uv](https://docs.astral.sh/uv/), Go and stable Rust. The runner selects Python 3.15 through uv and Go 1.25.0 through `GOTOOLCHAIN`; first runs may download toolchains and dependencies.

```sh
uv run analysis/run_snippets.py src/lib/content/langs/10-compare.md
```

```sh
uv run analysis/capture_vars.py src/lib/content/langs/10-compare.md
```

Commit the content and updated `src/lib/content/vars.json` together. Installation enables a pre-commit hook that checks changed snippets and recaptures their variable values.

## Analytics

The repository ships with no visitor analytics. `src/routes/+layout.svelte` adds a tracker `<script>` to the page head only when both build-time variables are set, and only when the page is served from `pygors.xces.workers.dev`. Local runs, forks and previews never load it.

The owner publishes the live site by building locally and then uploading the build with Wrangler. The owner keeps both variables in a gitignored `.env` file next to `package.json`, which the build reads, so analytics are enabled on that deployment only. A Worker that only serves static assets has no runtime variables in Cloudflare, which is why they are build-time values.

- `PUBLIC_TRAKS_SITE`: site key passed to the tracker as `data-site`.
- `PUBLIC_TRAKS_SRC`: URL of the tracker script served by the collector.

What the tracker collects is decided by that remote script and its collector, which are not part of this repository. The code here only loads the script and defines the `window.traks` queue function; it sends no events of its own. Both variables are declared in `src/env.ts`, are public and are inlined into the prerendered HTML at build time, so the values are visible to every visitor and are a site identifier, not a secret.

## Roadmap and contributing

See [ROADMAP.md](ROADMAP.md) for planned content and improvements. [CONTRIBUTING.md](CONTRIBUTING.md) explains how to add or correct a pattern and submit a pull request. Small corrections are welcome; [good first issues](https://github.com/mrgnw/py-go-rust/issues?q=is%3Aissue%20is%3Aopen%20label%3A%22good%20first%20issue%22) are a starting point.

Use the [new pattern form](https://github.com/mrgnw/py-go-rust/issues/new?template=new-pattern.yml) to suggest a comparison, or [report an incorrect example](https://github.com/mrgnw/py-go-rust/issues/new?template=bug-report.yml). The content format is documented in [CLAUDE.md](CLAUDE.md), and the parts model is in [SPEC.md](SPEC.md).

## Sources

The side-by-side layout follows [Component Party](https://component-party.dev) and the content depth follows [Learn X in Y Minutes](https://learnxinyminutes.com), whose pages are CC BY-SA 3.0. The text and code here are written for this project: an exact-line comparison of the content against the Learn X in Y Minutes Python, Rust and Go pages found only three shared idiomatic lines (`def wrapper(*args, **kwargs):` and `body, err := io.ReadAll(resp.Body)` twice).

The `longest` function in the lifetimes section of `30-rust.md` is the same function that appears in [The Rust Programming Language](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html), which is licensed under Apache-2.0 or MIT.

`src/lib/section-nav` is a vendored copy of the SectionNav component from the author's [svelte-bits](https://github.com/mrgnw/svelte-bits), MIT.

## License

[MIT](LICENSE)
