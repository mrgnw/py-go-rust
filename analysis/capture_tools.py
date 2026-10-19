# Screenshots of part tools: a lit nested part in If-else and the same row expanded to its pivot.
# uv run analysis/capture_tools.py NAME
# /// script
# dependencies = ['playwright']
# ///
import pathlib
import sys

from playwright.sync_api import sync_playwright

NAME = sys.argv[1]
SECTION = 'compare-if-else-ternary-ish'
SHOTS = pathlib.Path('captures')

with sync_playwright() as p:
	browser = p.chromium.launch()
	for width in (1280, 420):
		page = browser.new_page(viewport={'width': width, 'height': 900}, device_scale_factor=2)
		page.goto(f'http://localhost:5244/compare#{SECTION}')
		row = page.locator(f'#{SECTION} ~ .row').first
		nested = row.locator('.cols').first.locator('.part[data-group] .part[data-part]').nth(1)
		box = nested.bounding_box()
		page.mouse.move(box['x'] + 20, box['y'] + box['height'] / 2)
		row.screenshot(path=str(SHOTS / f'tools-{NAME}-{width}.png'))
		row.locator('.cols').first.locator('[data-toggle]').first.click(force=True)
		page.mouse.move(0, 0)
		row.screenshot(path=str(SHOTS / f'pivot-{NAME}-{width}.png'))
		page.close()
	browser.close()
