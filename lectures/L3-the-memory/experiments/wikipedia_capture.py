"""Capture a real Wikipedia page for the LLM Wiki analogy (Lecture 3): a full-page screenshot plus the boxes of the
parts we highlight (lead, infobox, contents, section headings, internal links, references, categories).

    /Users/raj/.venv/bin/modal run lectures/L3-the-memory/experiments/wikipedia_capture.py

Wikipedia text is CC BY-SA 4.0: the slide credits "Electric bicycle", Wikipedia, with the capture date.
Writes figs/wikipedia/electric_bicycle.png (+ .jpg) and figs/wikipedia/boxes.json.
"""
import json
import pathlib

import modal

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "figs" / "wikipedia"
URL = "https://en.wikipedia.org/wiki/Electric_bicycle"
app = modal.App("l3-wikipedia-capture")
image = (modal.Image.debian_slim(python_version="3.11").pip_install("playwright==1.47.0", "pillow")
         .run_commands("playwright install --with-deps chromium"))

BOXES_JS = r"""() => {
  const r = (el) => { if (!el) return null; const b = el.getBoundingClientRect(); return {x: b.x + scrollX, y: b.y + scrollY, w: b.width, h: b.height}; };
  const content = document.querySelector('#mw-content-text .mw-parser-output');
  const firstH2 = content.querySelector('.mw-heading2, h2');
  const leadPs = [...content.children].filter(e => e.tagName === 'P' && firstH2 && (e.compareDocumentPosition(firstH2) & Node.DOCUMENT_POSITION_FOLLOWING) && e.textContent.trim().length > 40);
  const lead = leadPs.length ? leadPs.reduce((a, e) => { const b = r(e); return a ? {x: Math.min(a.x, b.x), y: Math.min(a.y, b.y), w: Math.max(a.x + a.w, b.x + b.w) - Math.min(a.x, b.x), h: Math.max(a.y + a.h, b.y + b.h) - Math.min(a.y, b.y)} : b; }, null) : null;
  const heads = [...content.querySelectorAll('.mw-heading2, .mw-heading3')].slice(0, 12).map(h => ({text: h.textContent.replace('[edit]', '').trim(), box: r(h)}));
  const links = [...(leadPs[0] || content).querySelectorAll('a[href^="/wiki/"]')].slice(0, 8).map(a => ({text: a.textContent, href: a.getAttribute('href'), box: r(a)}));
  return {url: location.href, title: document.querySelector('#firstHeading')?.textContent, page: {w: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight},
          title_box: r(document.querySelector('#firstHeading')), lead, infobox: r(content.querySelector('.infobox')),
          toc: r(document.querySelector('#vector-toc, #toc, .vector-toc')), headings: heads, links,
          references: r(content.querySelector('.reflist, .references')), categories: r(document.querySelector('#catlinks')),
          history_tab: r(document.querySelector('#ca-history')), talk_tab: r(document.querySelector('#ca-talk')),
          n_sections: content.querySelectorAll('.mw-heading2').length, n_refs: content.querySelectorAll('.references li').length,
          n_internal_links: content.querySelectorAll('a[href^="/wiki/"]').length,
          lead_text: leadPs.map(p => p.textContent.trim()).join('\n\n').slice(0, 1500)};
}"""


@app.function(image=image, timeout=600)
def capture() -> dict:
    import datetime
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1.5)
        pg.goto(URL, wait_until="networkidle", timeout=90000)
        pg.wait_for_timeout(1500)
        boxes = pg.evaluate(BOXES_JS)
        shot = pg.screenshot(full_page=True, type="png")
        top = pg.screenshot(full_page=False, type="png")
        b.close()
    boxes["pixel_scale"] = 1.5  # screenshot pixels per CSS pixel
    boxes["captured_utc"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    boxes["licence"] = "Text CC BY-SA 4.0, Wikipedia contributors. Captured for teaching with attribution."
    return {"boxes": boxes, "full": shot, "top": top}


@app.local_entrypoint()
def main():
    import io
    from PIL import Image
    d = capture.remote()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "boxes.json").write_text(json.dumps(d["boxes"], indent=1, ensure_ascii=False))
    for name, data in (("electric_bicycle_full", d["full"]), ("electric_bicycle_top", d["top"])):
        im = Image.open(io.BytesIO(data)).convert("RGB")
        if im.height > 12000:
            im = im.crop((0, 0, im.width, 12000))
        im.save(OUT / f"{name}.jpg", quality=86)
        print(name, im.size)
    b = d["boxes"]
    print(b["title"], "| sections", b["n_sections"], "| refs", b["n_refs"], "| links", b["n_internal_links"], "| infobox", bool(b["infobox"]), "| toc", bool(b["toc"]))
