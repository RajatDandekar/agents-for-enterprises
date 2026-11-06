"""Build v5/preview_wiki.html: index.html's head and scripts around the wiki section fragment (v5/wiki.html).
   <base href="../"> makes every path resolve as it will inside index.html.   python3 v5/make_preview_wiki.py"""
import pathlib
V5 = pathlib.Path(__file__).resolve().parent
frag = (V5 / "wiki.html").read_text()
html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<base href="../">
<title>Lecture 3 · The Knowledge · preview: the LLM Wiki</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Google+Sans+Flex:opsz,wght@6..144,300..700&family=Google+Sans+Code:wght@300..700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="../../engine/plates.css">
<link rel="stylesheet" href="l3.css">
<link rel="stylesheet" href="v5/wiki.css">
</head>
<body>
<div class="deck" id="deck">
{frag}
</div>
<script src="figdata.js"></script>
<script src="figs.js"></script>
<script src="figs2.js"></script>
<script src="v5/wiki_data.js"></script>
<script src="v5/wiki.js"></script>
<script>
(() => {{ let q = 0; document.querySelectorAll('.qnum').forEach((e) => {{ e.textContent = String(++q); }}); if (window.FIGS && FIGS._fill) FIGS._fill(); }})();
</script>
<script src="../../engine/plates.js"></script>
</body>
</html>
"""
(V5 / "preview_wiki.html").write_text(html)
print("wrote", V5 / "preview_wiki.html")
