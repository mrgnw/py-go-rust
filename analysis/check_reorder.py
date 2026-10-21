# Language chip reorder: first-paint order from localStorage, mouse and touch drag, Shift+arrow, click vs drag.
# Needs `pnpm build`, then `npx wrangler dev .svelte-kit/cloudflare/_worker.js --port 5244`.
# uv run analysis/check_reorder.py
# /// script
# dependencies = ['playwright']
# ///
import sys

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:5244/compare'
FIRST_PAINT = """(order) => {
	if (order !== null) localStorage.setItem('order', order);
	window.seen = null;
	const frame = () => {
		const col = document.querySelector('.cols > [data-lang]');
		const chip = document.querySelector('[data-pick]');
		if (!col || !chip) return requestAnimationFrame(frame);
		const visual = (els, key) => [...els].sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left).map((el) => el.dataset[key]).join(' ');
		window.seen = visual(col.parentElement.children, 'lang') + ' | ' + visual(chip.parentElement.children, 'pick');
	};
	requestAnimationFrame(frame);
}"""
STATE = """() => ({
	order: document.documentElement.dataset.order,
	stored: localStorage.getItem('order'),
	chips: [...document.querySelectorAll('[data-pick]')].map((b) => b.dataset.pick + (b.ariaPressed === 'true' ? '' : '-off')).join(' '),
	cols: [...document.querySelector('.cols').children].sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left).map((c) => c.dataset.lang).join(' '),
	focus: document.activeElement.dataset.pick ?? document.activeElement.localName,
})"""
problems: list[str] = []


SETTLED = """async () => {
	await document.querySelector('main').activeViewTransition?.finished;
	await new Promise((done) => requestAnimationFrame(done));
}"""


def state(page):
	page.evaluate(SETTLED)
	return page.evaluate(STATE)


def expect(label, actual, wanted):
	print(f'{"ok  " if actual == wanted else "FAIL"} {label}: {actual!r}')
	if actual != wanted:
		problems.append(f'{label}: got {actual!r}, wanted {wanted!r}')


def fresh(browser, stored, **options):
	context = browser.new_context(viewport={'width': 1280, 'height': 900}, **options)
	page = context.new_page()
	page.add_init_script(f'({FIRST_PAINT})({stored!r})' if stored is not None else f'({FIRST_PAINT})(null)')
	page.goto(BASE)
	return context, page


def chip_center(page, lang):
	box = page.locator(f'[data-pick="{lang}"]').bounding_box()
	return box['x'] + box['width'] / 2, box['y'] + box['height'] / 2


def first_paint(browser):
	for stored, wanted in [
		('go python rust', 'go python rust | go python rust'),
		('go go go', 'python rust go | python rust go'),
		('ruby python go', 'python rust go | python rust go'),
		('', 'python rust go | python rust go'),
	]:
		context, page = fresh(browser, stored)
		expect(f'first paint with {stored!r}', page.evaluate('window.seen'), wanted)
		context.close()


def mouse(browser):
	context, page = fresh(browser, None)
	x, y = chip_center(page, 'python')
	gx, _ = chip_center(page, 'go')
	page.mouse.move(x, y)
	page.mouse.down()
	page.mouse.move(x + 3, y)
	page.mouse.move(gx + 4, y, steps=8)
	page.mouse.up()
	now = state(page)
	expect(
		'mouse drag py past go',
		(now['order'], now['stored'], now['chips'], now['cols']),
		('rust go python', 'rust go python', 'rust go python', 'rust go python'),
	)
	page.locator('[data-pick="rust"]').focus()
	page.keyboard.press('Enter')
	expect('Enter toggles after a drag', state(page)['chips'], 'rust-off go python')
	page.keyboard.press('Enter')
	x, y = chip_center(page, 'go')
	page.mouse.click(x + 2, y)
	expect('short click toggles', state(page)['chips'], 'rust go-off python')
	page.locator('[data-pick="python"]').focus()
	page.keyboard.press('Shift+ArrowLeft')
	now = state(page)
	expect(
		'Shift+Left keeps focus and moves',
		(now['order'], now['focus'], now['chips']),
		('rust python go', 'python', 'rust python go-off'),
	)
	page.keyboard.press('Shift+ArrowLeft')
	page.keyboard.press('Shift+ArrowLeft')
	expect('Shift+Left stops at the edge', state(page)['order'], 'python rust go')
	page.keyboard.press('1')
	expect('1 still toggles python', state(page)['chips'], 'python-off rust go-off')
	page.reload()
	now = state(page)
	expect(
		'reload keeps order and hide',
		(now['order'], now['chips']),
		('python rust go', 'python-off rust go-off'),
	)
	context.close()


def touch(browser):
	context, page = fresh(browser, None, has_touch=True)
	cdp = context.new_cdp_session(page)
	x, y = chip_center(page, 'go')
	px, _ = chip_center(page, 'python')

	def touch_event(kind, at=None):
		points = [] if at is None else [{'x': at[0], 'y': at[1]}]
		cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': points})

	touch_event('touchStart', (x, y))
	for i in range(1, 9):
		touch_event('touchMove', (x + (px - 4 - x) * i / 8, y))
	touch_event('touchEnd')
	page.wait_for_timeout(400)
	now = state(page)
	expect('touch drag go to front', (now['order'], now['chips']), ('go python rust', 'go python rust'))
	x, y = chip_center(page, 'rust')
	touch_event('touchStart', (x, y))
	touch_event('touchEnd')
	page.wait_for_timeout(400)
	expect('tap toggles', state(page)['chips'], 'go python rust-off')
	context.close()


def main():
	with sync_playwright() as p:
		browser = p.chromium.launch()
		first_paint(browser)
		mouse(browser)
		touch(browser)
		browser.close()
	sys.exit(1 if problems else 0)


main()
