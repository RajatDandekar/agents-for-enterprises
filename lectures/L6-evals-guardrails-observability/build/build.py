# -*- coding: utf-8 -*-
"""Build the Lecture 6 v2 deck from the v1 deck (kept slides, by number, with edits) and the new slides.
    python3 build.py  ->  lectures/L6-evals-guardrails-observability/index.html"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from part0 import P0
from part1 import P1
from part2 import P2

V1 = (HERE / "index_v1_16nov.html").read_text()
secs = re.split(r'(?=<section class="slide)', V1)
OUT = pathlib.Path("/Users/raj/Claude_Brain/enterprise-agents-course/lectures/L6-evals-guardrails-observability/index.html")
VER = "20261117b"
head = secs[0].replace("<title>Lecture 6 · Evals, Guardrails and Observability</title>", "<title>Lecture 6 · Observability and Evals</title>") \
    .replace("l6.css?v=20261116", f"l6.css?v={VER}")
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
body, n, miss = [], 0, []
for part, name in ((P0, "OPENER AND PART 1 · OBSERVABILITY"), (P1, "THE SAME TURN IN THE TOOLS"), (P2, "PART 2 · EVALS, AND THE CLOSE")):
    body.append(f"\n<!-- ============================== {name} ============================== -->\n")
    for e in part:
        n += 1
        if e[0] == "v1":
            html = secs[e[1]].split("\n\n\n<!-- ====")[0].split("\n</div>\n<script")[0].rstrip()
            html = re.sub(r"\n*<!-- =+ .*? =+ -->\s*$", "", html, flags=re.S).rstrip()
            for old, new in e[2]:
                if old not in html:
                    miss.append((e[1], old[:70]))
                html = html.replace(old, new)
        else:
            html = e[1].strip()
        body.append(f"<!-- #{n} -->\n{html}\n")
OUT.write_text(head + "".join(body) + tail)
print("slides:", n, "| edits that did not apply:", miss)
