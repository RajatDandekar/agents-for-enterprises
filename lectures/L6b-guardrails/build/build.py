# -*- coding: utf-8 -*-
"""Build the Lecture 7 deck (Guardrails and Red-Teaming) from the parked 16 Nov deck (kept slides, by number, with listed
edits) and the new slides in part0.py, part1.py, part2.py.

    python3 lectures/L6b-guardrails/build/build.py   ->   lectures/L6b-guardrails/index.html

It prints the slide count and every edit that did not apply (must be none)."""
import importlib
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PARKED = (HERE / "index_parked_16nov.html").read_text()
secs = re.split(r'(?=<section class="slide)', PARKED)        # secs[n] = slide n of the parked deck (1 to 38)
OUT = HERE.parent / "index.html"
VER = "20261118a"
PARTS = (("part0", "P0", "OPENER (DEMO FIRST) AND PART 1 · GUARDS IN CODE"),
         ("part1", "P1", "PART 2 · TEXT FROM OUTSIDE, AND GUARDS THAT READ TEXT"),
         ("part2", "P2", "PART 3 · RED-TEAMING, AND THE CLOSE"))

head = secs[0].replace("l6.css?v=20261116", f"l6.css?v={VER}")
head = head[:head.index("<!-- ====")]
tail = '''
</div>
<script src="figdata.js?v=%s"></script>
<script src="l6figs.js?v=%s"></script>
<script>
(() => { let q = 0; document.querySelectorAll('.qnum').forEach((e) => { e.textContent = String(++q); }); if (window.FIGS && FIGS._fill) FIGS._fill(); })();
</script>
<script src="../../engine/plates.js"></script>
<script>/* the presenter's pre-class reminder on the title slide: gone on the first click, key or touch */
(() => { const n = document.getElementById('pnote'); if (!n) return;
  const hide = () => { n.remove(); ['keydown', 'click', 'touchstart'].forEach((e) => removeEventListener(e, hide, true)); };
  ['keydown', 'click', 'touchstart'].forEach((e) => addEventListener(e, hide, true)); })();</script>
</body>
</html>
''' % (VER, VER)

body, n, miss, kept, index = [], 0, [], [], []
for mod, var, name in PARTS:
    if not (HERE / f"{mod}.py").exists():
        continue
    part = getattr(importlib.import_module(mod), var)
    body.append(f"\n<!-- ============================== {name} ============================== -->\n")
    for e in part:
        n += 1
        if e[0] == "parked":
            html = secs[e[1]].split("\n\n\n<!-- ====")[0].split("\n</div>\n<script")[0].rstrip()
            html = re.sub(r"\n*<!-- #\d+ -->\s*$", "", html).rstrip()
            html = re.sub(r"\n*<!-- =+ .*? =+ -->\s*$", "", html, flags=re.S).rstrip()
            for old, new in e[2]:
                if old not in html:
                    miss.append((n, f"parked {e[1]}", old[:70]))
                html = html.replace(old, new)
            kept.append((n, e[1]))
        else:
            html = e[1].strip()
        t = re.search(r'data-plate="([^"]*)"', html)
        index.append((n, t.group(1) if t else ("part" if 'class="slide part' in html else "question" if "slide q" in html else "title"), mod))
        body.append(f"<!-- #{n} -->\n{html}\n")
OUT.write_text(head + "".join(body) + tail)
(HERE / "slides.txt").write_text("".join(f"{i:>3}  {m}  {t}\n" for i, t, m in index))
print("slides:", n, "| kept from the parked deck (slide: parked number):", ", ".join(f"{a}:{b}" for a, b in kept) or "none")
print("edits that did not apply:", len(miss), miss)
