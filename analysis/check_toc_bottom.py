# Sidebar highlight near the page bottom: the section you navigate to is the one marked current,
# even when its heading cannot scroll up to the top.
# Needs a server on BASE (`pnpm preview`, port 5238).
# uv run analysis/check_toc_bottom.py
# /// script
# dependencies = ['playwright']
# ///
import sys

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:5238/'
CURRENT = """() => document.querySelector('nav[aria-label="Sections"] a[aria-current]')?.textContent.trim()"""
SETTLED = """() => {
	const settled = window.lastY === scrollY;
	window.lastY = scrollY;
	return settled;
}"""
problems: list[str] = []


def expect(label, actual, wanted):
	print(f'{"ok  " if actual == wanted else "FAIL"} {label}: {actual!r}')
	if actual != wanted:
		problems.append(f'{label}: got {actual!r}, wanted {wanted!r}')


def current(page):
	page.wait_for_timeout(200)
	page.wait_for_function(SETTLED, polling=200)
	return page.evaluate(CURRENT)


with sync_playwright() as p:
	browser = p.chromium.launch()
	page = browser.new_page(viewport={'width': 1200, 'height': 1240})
	page.goto(BASE)
	toc = page.locator('nav[aria-label="Sections"]')
	toc.get_by_role('link', name='Mental model shifts').click()
	expect('click Mental model shifts', current(page), 'Mental model shifts')
	toc.get_by_role('link', name='Mixing them').click()
	expect('click Mixing them', current(page), 'Mixing them')
	page.keyboard.press('k')
	expect('k from Mixing them', current(page), 'Mental model shifts')
	page.keyboard.press('k')
	expect('k again', current(page), 'Hello, run it')
	page.keyboard.press('j')
	expect('j back down', current(page), 'Mental model shifts')
	page.mouse.wheel(0, -60)
	expect('scroll up off the bottom', current(page) != 'Mental model shifts', True)
	page = browser.new_page(viewport={'width': 1200, 'height': 1240})
	page.goto(BASE + '#overview-mental-model-shifts')
	expect('load with hash', current(page), 'Mental model shifts')
	browser.close()

if problems:
	sys.exit('\n'.join(problems))
