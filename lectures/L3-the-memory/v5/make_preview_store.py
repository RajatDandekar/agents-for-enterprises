"""Rebuild v5/preview_store.html = index.html's head and scripts + v5/store.html + the store files."""
import pathlib
V5 = pathlib.Path(__file__).resolve().parent
idx = (V5.parent / "index.html").read_text()
head = idx[:idx.index('<div class="deck" id="deck">')]
head = head.replace('href="../../engine/plates.css"', 'href="../../../engine/plates.css"').replace('href="l3.css"', 'href="../l3.css"')
head = head.replace("<title>Lecture 3 · The Knowledge</title>", "<title>Lecture 3 · The Knowledge · store preview</title>")
import re
head = re.sub(r'\s*<link rel="stylesheet" href="v5/[^"]+">', "", head)   # the lead's assembled head links v5 CSS from the deck folder
head = head.replace("</head>", '<link rel="stylesheet" href="store.css">\n</head>')
tail = """</div>
<script src="../figdata.js"></script>
<script src="../figs.js"></script>
<script src="../figs2.js"></script>
<script>
(() => { let q = 0; document.querySelectorAll('.qnum').forEach((e) => { e.textContent = String(++q); }); if (window.FIGS && FIGS._fill) FIGS._fill();
  const o = (window.L3 && L3.nb3) || {}; document.querySelectorAll('[data-nb3]').forEach((p) => { if (o[p.dataset.nb3]) p.textContent = o[p.dataset.nb3]; }); })();
</script>
<script src="store_data.js"></script>
<script src="store.js"></script>
<script src="../../../engine/plates.js"></script>
</body>
</html>
"""
(V5 / "preview_store.html").write_text(head + '<div class="deck" id="deck">\n' + (V5 / "store.html").read_text() + "\n" + tail)
print("wrote", V5 / "preview_store.html")
