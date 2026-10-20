# Sections sidebar: desktop toggle keeps content put on wide screens, mobile sticky bar names the section and opens the list.
# Needs the dev server (`pnpm dev`, port 5237). Screenshots land in /tmp/pygorst-sidebar-*.png.
# uv run analysis/check_sidebar.py
# /// script
# dependencies = ['playwright']
# ///
import sys

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:5237/'
CONTENT_LEFT = "() => document.querySelector('.sidebar-grid > div').getBoundingClientRect().left"
failures = []


def check(name, ok):
	print(('ok   ' if ok else 'FAIL ') + name)
	if not ok:
		failures.append(name)


with sync_playwright() as p:
	browser = p.chromium.launch()

	for width, stays in ((1280, False), (1920, True)):
		page = browser.new_page(viewport={'width': width, 'height': 900})
		page.goto(BASE)
		page.evaluate('localStorage.clear()')
		page.reload()
		open_left = page.evaluate(CONTENT_LEFT)
		page.screenshot(path=f'/tmp/pygorst-sidebar-{width}-open.png')
		page.click('[data-sidebar-toggle]')
		page.wait_for_timeout(400)
		closed_left = page.evaluate(CONTENT_LEFT)
		page.screenshot(path=f'/tmp/pygorst-sidebar-{width}-closed.png')
		check(
			f'{width}: content stays put = {stays} ({open_left} -> {closed_left})',
			(open_left == closed_left) == stays,
		)
		check(f'{width}: nav hidden when collapsed', not page.is_visible('#sections-nav'))
		check(f'{width}: mobile bar hidden', not page.is_visible('.section-now'))
		page.close()

	page = browser.new_page(viewport={'width': 390, 'height': 800}, has_touch=True)
	page.goto(BASE)
	check('mobile: nav hidden by default', not page.is_visible('#sections-nav'))
	check('mobile: toggle hidden', not page.is_visible('[data-sidebar-toggle]'))
	first = page.text_content('[data-section-now]')
	page.mouse.wheel(0, 2500)
	page.wait_for_timeout(300)
	later = page.text_content('[data-section-now]')
	check(f'mobile: bar follows scroll ({first!r} -> {later!r})', bool(first) and first != later)
	check('mobile: bar stays on screen', page.locator('.section-now').bounding_box()['y'] < 100)
	page.screenshot(path='/tmp/pygorst-sidebar-mobile-bar.png')
	page.click('.section-now')
	check('mobile: tap opens list', page.is_visible('#sections-nav'))
	page.screenshot(path='/tmp/pygorst-sidebar-mobile-list.png')
	page.click('#sections-nav li:nth-child(2) a')
	page.wait_for_timeout(300)
	check('mobile: picking a section closes list', not page.is_visible('#sections-nav'))
	browser.close()

sys.exit(1 if failures else 0)
