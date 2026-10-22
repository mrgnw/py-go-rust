# Move every section of a page file into its own file; the page keeps `## [Title](dir/file.md)` lines.
# uv run analysis/split_sections.py src/lib/content/langs/15-algorithms.md
import pathlib
import re
import sys


def slugify(text: str) -> str:
	return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def main() -> None:
	page = pathlib.Path(sys.argv[1])
	slug = re.sub(r'^\d+-', '', page.stem)
	lines = page.read_text().splitlines()
	depth = 3 if any(line.startswith('### ') for line in lines) else 2
	heading = re.compile(rf'^(#{{1,{depth}}}) (.+)$')
	out: list[str] = []
	section: tuple[str, list[str]] | None = None
	written: set[str] = set()
	in_fence = False

	def close() -> None:
		if section is None:
			return
		title, body = section
		name = slugify(re.sub(r'\s*\(.*?\)', '', title).split(' / ')[0])
		assert name not in written, name
		written.add(name)
		text = '\n'.join(body).strip('\n') + '\n'
		target = page.parent / slug / f'{name}.md'
		target.parent.mkdir(exist_ok=True)
		target.write_text(text)
		out.append(f'{"#" * depth} [{title}]({slug}/{name}.md)')

	for line in lines:
		if line.startswith('```'):
			in_fence = not in_fence
		match = None if in_fence else heading.match(line)
		if match:
			close()
			section = None
			if len(match[1]) == depth:
				section = (match[2], [])
				continue
			out.extend(['', line, ''])
			continue
		if section is not None:
			section[1].append(line)
		else:
			out.append(line)
	close()
	page.write_text(re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip('\n') + '\n')
	print(f'{page}: {len(written)} sections into {page.parent / slug}/')


main()
