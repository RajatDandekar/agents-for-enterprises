"""Rebuild v5/preview_lexical.html = index.html's head and scripts + v5/lexical.html + the lexical files.
dense.css/dense_data.js/dense.js are loaded too (read only): "The Whole Pipeline, With Keywords" reuses FIGS.dense_flow."""
import pathlib
import re

V5 = pathlib.Path(__file__).resolve().parent
idx = (V5.parent / "index.html").read_text()
head = idx[:idx.index('<div class="deck" id="deck">')]
head = head.replace('href="../../engine/plates.css"', 'href="../../../engine/plates.css"').replace('href="l3.css"', 'href="../l3.css"')
head = re.sub(r"<title>([^<]*)</title>", r"<title>\1 · lexical preview</title>", head, count=1)
head = re.sub(r'<link rel="stylesheet" href="v5/[a-z_]+\.css">\n?', "", head)   # the assembled deck links every fragment; the preview loads only ours
head = head.replace("</head>", '<link rel="stylesheet" href="dense.css">\n<link rel="stylesheet" href="lexical.css">\n</head>')
tail = """</div>
<script src="../figdata.js"></script>
<script src="../figs.js"></script>
<script src="../figs2.js"></script>
<script>
(() => { let q = 0; document.querySelectorAll('.qnum').forEach((e) => { e.textContent = String(++q); }); if (window.FIGS && FIGS._fill) FIGS._fill();
  const o = (window.L3 && L3.nb3) || {}; document.querySelectorAll('[data-nb3]').forEach((p) => { if (o[p.dataset.nb3]) p.textContent = o[p.dataset.nb3]; }); })();
</script>
<script src="dense_data.js"></script>
<script src="dense.js"></script>
<script src="lexical_data.js"></script>
<script src="lexical.js"></script>
<script src="../../../engine/plates.js"></script>
</body>
</html>
"""
(V5 / "preview_lexical.html").write_text(head + '<div class="deck" id="deck">\n' + (V5 / "lexical.html").read_text() + "\n" + tail)
print("wrote", V5 / "preview_lexical.html")
