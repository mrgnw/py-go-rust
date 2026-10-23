# Variable hover: hovering a name lights it in every column and shows each column's value at the end of its
# line; hovering a line that sets names shows theirs; a click pins, Escape clears; `v` or the x= button turns it off.
# Needs a server on BASE (`pnpm preview`, port 5238). Screenshots land in /tmp/pygorst-vars-*.png.
# uv run analysis/check_vars.py
# /// script
# dependencies = ['playwright']
# ///
import sys

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:5238/compare'
VALS = "row => [...row.querySelectorAll('.part > .val')].map((v) => v.textContent)"
failures = []


def check(name, ok, got=None):
	print(('ok   ' if ok else 'FAIL ') + name + ('' if ok or got is None else f'  (got {got!r})'))
	if not ok:
		failures.append(name)


def row_of(page, section):
	return page.locator(f'h2#{section}, h3#{section}').locator(
		'xpath=following::div[contains(@class, "row")][1]'
	)


def vals(row):
	return row.evaluate(VALS)


def hover_line_end(line):
	box = line.bounding_box()
	line.page.mouse.move(box['x'] + box['width'] - 4, box['y'] + box['height'] / 2)


with sync_playwright() as p:
	page = p.chromium.launch().new_page(viewport={'width': 1400, 'height': 900})
	errors = []
	page.on('pageerror', lambda e: errors.append(str(e)))
	page.goto(BASE)

	basic = row_of(page, 'compare-basic-types-conversion')
	python = basic.locator('[data-lang="python"] .snippet')
	python.locator('[data-var="f"]').first.hover()
	check('hover f: 8.4 in 3 columns', vals(basic) == ['8.4'] * 3, vals(basic))
	lit = basic.locator('[data-var-lit]').count()
	check('hover f: f lit in every column', lit >= 6, lit)
	val = basic.locator('.part > .val').first.bounding_box()
	line = python.locator('[data-var="f"]').first.bounding_box()
	check('value sits on its line', abs(val['y'] - line['y']) < 4, (val['y'], line['y']))
	page.screenshot(path='/tmp/pygorst-vars-token.png', clip=basic.bounding_box())

	hover_line_end(python.locator('.line', has_text='f = n / 5'))
	check('hover f = n / 5 line: f = 8.4 in 3 columns', vals(basic) == ['f = 8.4'] * 3, vals(basic))
	page.screenshot(path='/tmp/pygorst-vars-line.png', clip=basic.bounding_box())

	hover_line_end(python.locator('.line', has_text='print('))
	check('hover a line that sets nothing: no values', vals(basic) == [], vals(basic))

	loops = row_of(page, 'compare-loops')
	loops.locator('[data-lang="rust"] .line', has_text='n -= 1').locator('[data-var="n"]').hover()
	check('hover n -= 1: 2 → 1 → 0 in 3 columns', vals(loops) == ['2 → 1 → 0'] * 3, vals(loops))

	loops.locator('[data-lang="go"] .line', has_text='n--').locator('[data-var="n"]').click()
	page.mouse.move(0, 0)
	check('click pins the value', vals(loops) == ['2 → 1 → 0'] * 3, vals(loops))
	page.keyboard.press('Escape')
	check('Escape clears', vals(loops) == [], vals(loops))

	toggle = page.locator('[data-vars-toggle]')
	page.keyboard.press('v')
	python.locator('[data-var="f"]').first.hover()
	check(
		'v turns values off',
		vals(basic) == [] and toggle.get_attribute('aria-pressed') == 'false',
		vals(basic),
	)
	page.reload()
	python.locator('[data-var="f"]').first.hover()
	check('off survives a reload', vals(basic) == [] and toggle.get_attribute('aria-pressed') == 'false')
	toggle.click()
	python.locator('[data-var="f"]').first.hover()
	check('the x= button turns values back on', vals(basic) == ['8.4'] * 3, vals(basic))
	page.screenshot(path='/tmp/pygorst-vars-header.png', clip={'x': 900, 'y': 0, 'width': 500, 'height': 44})

	print('errors', errors)
	check('no page errors', not errors)

print(f'{len(failures)} failed' if failures else 'all ok')
sys.exit(1 if failures else 0)
