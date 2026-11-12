# Output strip lines link to the part that printed them: hovering a part lights its output lines in
# every column, hovering an output line lights its part. Multi-line outputs (Loops) light together.
# Needs a server on BASE (`pnpm preview`, port 5238). Screenshot lands in /tmp/py-go-rust-output-link.png.
# uv run analysis/check_output_link.py
# /// script
# dependencies = ['playwright']
# ///
import sys

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:5238/compare'
failures = []


def check(name, ok):
	print(('ok   ' if ok else 'FAIL ') + name)
	if not ok:
		failures.append(name)


def lit_output(row):
	return row.locator('.out [data-lit]').evaluate_all('els => els.map((e) => e.textContent)')


def lit_parts(row):
	return row.locator('.snippet .part[data-lit]').evaluate_all('els => els.map((e) => e.dataset.part)')


def row_of(page, section):
	return page.locator(f'h2#{section}, h3#{section}').locator(
		'xpath=following::div[contains(@class, "row")][1]'
	)


with sync_playwright() as p:
	page = p.chromium.launch().new_page(viewport={'width': 1400, 'height': 900})
	page.goto(BASE)

	strings = row_of(page, 'compare-strings')
	strings.locator('[data-lang="python"] .snippet [data-part="1"]').hover()
	check('hover slice lights hello in 3 strips', lit_output(strings) == ['hello'] * 3)

	strings.locator('[data-lang="go"] .out [data-part="2"]').hover()
	check('hover Go split output lights split part in 3 columns', lit_parts(strings) == ['2'] * 3)
	check('hover Go split output lights split output in 3 strips', len(lit_output(strings)) == 3)
	page.screenshot(path='/tmp/py-go-rust-output-link.png', clip=strings.bounding_box())

	loops = row_of(page, 'compare-loops')
	loops.locator('[data-lang="rust"] .snippet [data-part="0"]').hover()
	check('hover range lights 0 1 2 in 3 strips', lit_output(loops) == ['0', '1', '2'] * 3)

	page.mouse.move(0, 0)
	check('moving away clears', not lit_output(strings) and not lit_output(loops))

print(f'{len(failures)} failed' if failures else 'all ok')
sys.exit(1 if failures else 0)
