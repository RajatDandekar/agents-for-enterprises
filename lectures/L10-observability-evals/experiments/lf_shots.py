"""Extra headless screenshots of the public Langfuse trace (no model call, no login): Timeline view and Attributes tab."""
import json, pathlib
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).parent
FIGS = HERE.parent / "figs"
urls = json.loads((HERE / "logs" / "langfuse_urls_r3.json").read_text())["urls"]
u = list(urls.values())[-1]
out = {"url": u}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=1.5, color_scheme="light").new_page()
    pg.goto(u, wait_until="networkidle", timeout=60000); pg.wait_for_timeout(15000)
    for label, name, extra in (("Timeline", "lf_r3_timeline", None), ("Tree", "lf_r3_attrs", "chat gemini-3.8-flash")):
        try:
            pg.get_by_text(label, exact=True).first.click(timeout=8000); pg.wait_for_timeout(8000)
            if extra:
                pg.get_by_text(extra).last.click(timeout=8000); pg.wait_for_timeout(6000)
                pg.get_by_text("Attributes", exact=True).first.click(timeout=8000); pg.wait_for_timeout(8000)
            pg.screenshot(path=str(FIGS / f"{name}.png"))
            out[name] = pg.inner_text("body")[:1200]
        except Exception as e:
            out[name] = "error " + repr(e)[:300]
    b.close()
(HERE / "logs" / "screens_r3_extra.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out)[:2000])
