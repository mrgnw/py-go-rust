# Width the part-tools gutter takes from code, and how many code blocks scroll because of it.
# uv run analysis/measure_gutter.py
# /// script
# dependencies = ['playwright']
# ///
from playwright.sync_api import sync_playwright

PAGES = ['/', '/compare', '/algorithms', '/python', '/rust', '/go']
VIEWPORTS = [(1440, 900), (1280, 900), (420, 900)]
MEASURE = """() => {
	const out = { pres: 0, linked: 0, stolen: [], scrolls: 0, scrollsWithout: 0, nested: 0, labelled: 0 };
	for (const pre of document.querySelectorAll('.cols .snippet pre')) {
		if (!pre.checkVisibility()) continue;
		const snippet = pre.closest('.snippet');
		const part = pre.closest('.part[data-part]');
		out.pres++;
		const pad = parseFloat(getComputedStyle(pre).paddingRight);
		const content = pre.scrollWidth - pad;
		if (pre.scrollWidth > pre.clientWidth + 1) out.scrolls++;
		if (content + 12 > snippet.clientWidth + 1) out.scrollsWithout++;
		if (!part) continue;
		out.linked++;
		const stolen = snippet.clientWidth - pre.offsetWidth;
		out.stolen.push(stolen);
		if (part.parentElement.closest('.part')) out.nested++;
		if ([...part.parentElement.closest('.snippet').querySelectorAll('.part')].some((p) => p.contains(pre) && p.querySelector(':scope > .tools > span'))) out.labelled++;
	}
	out.stolen.sort((a, b) => a - b);
	const s = out.stolen;
	out.stolen = s.length ? { min: s[0], median: s[s.length >> 1], max: s.at(-1) } : null;
	out.snippetWidth = Math.round(document.querySelector('.cols .snippet')?.clientWidth ?? 0);
	return out;
}"""

with sync_playwright() as p:
	browser = p.chromium.launch()
	for width, height in VIEWPORTS:
		page = browser.new_page(viewport={'width': width, 'height': height})
		for path in PAGES:
			page.goto('http://localhost:5244' + path)
			r = page.evaluate(MEASURE)
			print(
				f'{width} {path:12} pres={r["pres"]:3} linked={r["linked"]:3} nested={r["nested"]:2} labelled={r["labelled"]:2} '
				f'col={r["snippetWidth"]}px stolen={r["stolen"]} scroll now={r["scrolls"]} without gutter={r["scrollsWithout"]}'
			)
		page.close()
	browser.close()
