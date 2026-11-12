# Roadmap

Where the project is and what is next. Each item links to an issue with acceptance criteria. PLAN.md has the goals and the history of what shipped; SPEC.md has the parts model.

## Now: the parts model

Compare at a finer grain than a whole snippet, with the languages linked part by part.

- [#2](https://github.com/mrgnw/py-go-rust/issues/2) Add `---` groups to more compare sections
- [#3](https://github.com/mrgnw/py-go-rust/issues/3) Build check: part labels agree across languages
- [#4](https://github.com/mrgnw/py-go-rust/issues/4) Keyboard stepping inside pivoted groups
- [#14](https://github.com/mrgnw/py-go-rust/issues/14) Decide how Pivot shows scaffolding lines

## Content

- [#10](https://github.com/mrgnw/py-go-rust/issues/10) Strings, regex and Unicode patterns
- [#11](https://github.com/mrgnw/py-go-rust/issues/11) Subprocess, timers and logging patterns
- [#12](https://github.com/mrgnw/py-go-rust/issues/12) SQLite and package publishing patterns
- [#13](https://github.com/mrgnw/py-go-rust/issues/13) Link each section to official docs
- [#1](https://github.com/mrgnw/py-go-rust/issues/1) Performance escape hatches as a vertical stack

## Quality

- [#8](https://github.com/mrgnw/py-go-rust/issues/8) Execute the Python, Rust and Go reference pages
- [#9](https://github.com/mrgnw/py-go-rust/issues/9) CI job that runs the snippet checker
- [#7](https://github.com/mrgnw/py-go-rust/issues/7) Unit tests for the markdown loader
- [#15](https://github.com/mrgnw/py-go-rust/issues/15) Accessibility pass
- [#17](https://github.com/mrgnw/py-go-rust/issues/17) Depend on svelte-components for SectionNav instead of the vendored copy

## Polish

- [#5](https://github.com/mrgnw/py-go-rust/issues/5) Reset action for the language order
- [#6](https://github.com/mrgnw/py-go-rust/issues/6) Collapsed sidebar flash on load

## Ideas, not committed to

- A fourth column (TypeScript or Zig) behind the language picker. The renderer already handles any number of columns.
- A custom domain for the deployed site.
