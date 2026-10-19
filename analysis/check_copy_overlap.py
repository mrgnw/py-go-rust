# Lit-part copy buttons and captions must not overlap any other button, label, output strip or code text.
# Needs `pnpm build`, then `npx wrangler dev .svelte-kit/cloudflare/_worker.js --port 5244`.
# uv run analysis/check_copy_overlap.py
# /// script
# dependencies = ['playwright']
# ///
import pathlib
import sys

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:5244/compare'
SECTIONS = [
	'compare-if-else-ternary-ish',
	'compare-print-string-formatting',
	'compare-strings',
	'compare-dicts-hashmap-map',
]
VIEWPORTS = [(1280, 900), (420, 900)]
HIDDEN = ['', 'rust go', 'python']
SHOTS = pathlib.Path('captures')

ROW_INDEXES = """(id) => {
	const all = [...document.querySelectorAll('.cols')];
	const out = [];
	for (let el = document.getElementById(id).nextElementSibling; el && !/^H[23]$/.test(el.tagName); el = el.nextElementSibling)
		if (el.classList.contains('row')) el.querySelectorAll('.cols').forEach((c) => out.push(all.indexOf(c)));
	return out;
}"""

OVERLAPS = """(cols) => {
	const visible = (el) => el.checkVisibility({ visibilityProperty: true }) && el.getClientRects().length;
	const rect = (what, r, el) => ({ what, el, x0: r.left, y0: r.top, x1: r.right, y1: r.bottom });
	const row = cols.closest('.row');
	const lit = [...row.querySelectorAll('.part[data-lit] > .tools')].filter(visible);
	const targets = lit.flatMap((tools) =>
		[...tools.children]
			.filter(visible)
			.map((el) => rect(el.localName === 'span' ? 'caption ' + el.textContent : el.textContent.trim() + ' button', el.getBoundingClientRect(), el))
	);
	const others = [];
	const selector = 'button, .out, .tools > span, .pivot > div > div:first-child';
	for (const el of row.querySelectorAll(selector))
		if (visible(el) && !targets.some((t) => t.el === el)) others.push(rect(el.className || el.localName, el.getBoundingClientRect(), el));
	for (const pre of row.querySelectorAll('pre')) {
		if (!visible(pre)) continue;
		const clip = pre.getBoundingClientRect();
		const walker = document.createTreeWalker(pre, NodeFilter.SHOW_TEXT);
		for (let n = walker.nextNode(); n; n = walker.nextNode()) {
			if (!n.textContent.trim()) continue;
			const range = document.createRange();
			range.selectNodeContents(n);
			for (const r of range.getClientRects())
				others.push({ what: 'code ' + JSON.stringify(n.textContent.slice(0, 20)), x0: Math.max(r.left, clip.left), y0: r.top, x1: Math.min(r.right, clip.right), y1: r.bottom });
		}
	}
	const hit = (a, b) => Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0) > 0.5 && Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0) > 0.5;
	const found = [];
	for (const t of targets) for (const o of others) if (hit(t, o)) found.push(t.what + ' overlaps ' + o.what);
	targets.forEach((a, i) => targets.slice(i + 1).forEach((b) => hit(a, b) && found.push(a.what + ' overlaps ' + b.what)));
	return { count: targets.length, found };
}"""


def check_row(page, cols, where, problems):
	checked = 0
	parts = cols.locator('.part[data-part]')
	for i in range(parts.count()):
		part = parts.nth(i)
		if not part.is_visible():
			continue
		part.scroll_into_view_if_needed()
		box = part.bounding_box()
		for fraction in (0.3, 0.97):
			page.mouse.move(box['x'] + box['width'] * fraction, box['y'] + min(box['height'] / 2, 12))
			outcome = cols.evaluate(OVERLAPS)
			checked += outcome['count']
			label = f'{where} part {part.get_attribute("data-part")} at {fraction}'
			problems.extend(f'{label}: {found}' for found in outcome['found'])
	return checked


def screenshot(page, width):
	page.evaluate('(hide) => (document.documentElement.dataset.hide = hide)', '')
	page.locator(f'#{SECTIONS[0]}').scroll_into_view_if_needed()
	cols = page.locator('.cols').nth(page.evaluate(ROW_INDEXES, SECTIONS[0])[0])
	part = cols.locator('.part[data-part]').first
	box = part.bounding_box()
	page.mouse.move(box['x'] + box['width'] * 0.3, box['y'] + 6)
	page.screenshot(path=str(SHOTS / f'copy-overlap-{width}.png'))


def main():
	problems: list[str] = []
	checked = 0
	SHOTS.mkdir(exist_ok=True)
	with sync_playwright() as p:
		browser = p.chromium.launch()
		for width, height in VIEWPORTS:
			page = browser.new_page(viewport={'width': width, 'height': height})
			page.goto(BASE)
			for hide in HIDDEN:
				page.evaluate('(hide) => (document.documentElement.dataset.hide = hide)', hide)
				for section in SECTIONS:
					for index in page.evaluate(ROW_INDEXES, section):
						where = f'{width}px hide={hide!r} {section} row {index}'
						checked += check_row(page, page.locator('.cols').nth(index), where, problems)
			screenshot(page, width)
			page.close()
		browser.close()
	print(f'checked {checked} lit boxes')
	for problem in problems:
		print(problem)
	sys.exit(1 if problems else 0)


main()
