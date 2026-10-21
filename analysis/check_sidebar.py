# Sections sidebar: desktop toggle keeps content put on wide screens, mobile sticky bar names the section and opens the list.
# Motion: smooth scroll, part tint, dialog fade and language view transitions (scoped to main), all off under reduced motion.
# Needs the dev server (`pnpm dev`, port 5237). Screenshots land in /tmp/pygorst-sidebar-*.png.
# uv run analysis/check_sidebar.py
# /// script
# dependencies = ['playwright']
# ///
import sys

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:5237/'
CONTENT_LEFT = "() => document.querySelector('.sidebar-grid > div').getBoundingClientRect().left"
FRAMES = """() => {
	window.frameTimes = [];
	let last = performance.now();
	const tick = (now) => {
		window.frameTimes.push(now - last);
		last = now;
		if (window.frameTimes.length < 30) requestAnimationFrame(tick);
	};
	requestAnimationFrame(tick);
}"""
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
		page.evaluate(FRAMES)
		page.click('[data-sidebar-toggle]')
		page.wait_for_timeout(400)
		long_frames = page.evaluate('window.frameTimes.slice(1).filter((t) => t > 34).length')
		check(f'{width}: toggle animates with at most one long frame ({long_frames})', long_frames <= 1)
		page.evaluate(FRAMES)
		page.click('[data-sidebar-toggle]')
		page.wait_for_timeout(120)
		page.screenshot(path=f'/tmp/pygorst-sidebar-{width}-mid.png')
		page.wait_for_timeout(400)
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
	page.close()

	for motion, smooth in (('no-preference', True), ('reduce', False)):
		page = browser.new_page(viewport={'width': 1280, 'height': 800}, reduced_motion=motion)
		page.goto(BASE)
		page.click('#sections-nav li:nth-child(4) a')
		page.wait_for_timeout(50)
		mid = page.evaluate('scrollY')
		page.wait_for_timeout(1000)
		end = page.evaluate('scrollY')
		check(
			f'{motion}: link scroll smooth = {smooth} ({mid} -> {end})', (0 < mid < end) == smooth and end > 0
		)
		check(f'{motion}: hash updated', page.evaluate('location.hash') != '')
		page.keyboard.press('j')
		page.wait_for_timeout(20)
		check(f'{motion}: j jumps instantly', page.evaluate('scrollY') > end)
		check(
			f'{motion}: part tint fades = {smooth}',
			(page.eval_on_selector('.part', 'e => getComputedStyle(e).transitionDuration') != '0s') == smooth,
		)
		page.keyboard.press('?')
		page.wait_for_timeout(30)
		opacity = float(page.eval_on_selector('#help', 'e => getComputedStyle(e).opacity'))
		check(f'{motion}: dialog fades in = {smooth} (opacity {opacity} at 30ms)', (opacity < 1) == smooth)
		page.keyboard.press('Escape')
		page.goto(BASE + 'compare')
		page.evaluate(
			'window.vt = 0; const main = document.querySelector("main"); const s = main.startViewTransition?.bind(main); if (s) main.startViewTransition = (f) => (vt++, s(f)); 0;'
		)
		page.keyboard.press('2')
		page.wait_for_timeout(400)
		check(
			f'{motion}: language toggle view transition = {smooth} (vt={page.evaluate("window.vt")})',
			(page.evaluate('vt') == 1) == smooth,
		)
		check(
			f'{motion}: language toggle applied',
			'rust' in page.evaluate('document.documentElement.dataset.hide'),
		)
		page.evaluate('localStorage.clear()')
		page.close()
	browser.close()

sys.exit(1 if failures else 0)
