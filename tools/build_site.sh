#!/bin/sh
# Build the static slides site into site-dist/ and (with --deploy) push it to Vercel.
# Only the decks, the deck engine and their images go up; no code, keys or notebooks.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/site-dist"
GH="https://github.com/RajatDandekar/agents-for-enterprises/blob/main"
rm -rf "$OUT" && mkdir -p "$OUT/demo"
cp -R "$ROOT/engine" "$OUT/engine"
cp -R "$ROOT/demo/shots" "$OUT/demo/shots"
for d in "$ROOT"/lectures/L*/; do
  n="$(basename "$d")"; mkdir -p "$OUT/lectures/$n"
  for f in index.html figs.js figdata.js; do [ -f "$d$f" ] && cp "$d$f" "$OUT/lectures/$n/"; done
  [ -d "${d}shots" ] && cp -R "${d}shots" "$OUT/lectures/$n/shots"
done
# Hub: notebooks open in Colab, assignments and kit briefs open on GitHub.
sed -e "s#<a href=\"lectures/\${dir}/\${nb}.ipynb\" download>Notebook</a>#<a href=\"https://colab.research.google.com/github/RajatDandekar/agents-for-enterprises/blob/main/lectures/\${dir}/\${nb}.ipynb\" target=\"_blank\" rel=\"noopener\">Open in Colab</a>#" \
    -e "s#href=\"lectures/\${dir}/\${a}.md\"#href=\"$GH/lectures/\${dir}/\${a}.md\" target=\"_blank\" rel=\"noopener\"#" \
    -e "s#href=\"modules/README.md\"#href=\"$GH/modules/README.md\"#" \
    -e "s#href=\"lectures/L8-your-module/DEMO_DAY.md\"#href=\"$GH/lectures/L8-your-module/DEMO_DAY.md\"#" \
    "$ROOT/index.html" > "$OUT/index.html"
echo '{"cleanUrls":false,"headers":[{"source":"/(.*)","headers":[{"key":"Cache-Control","value":"public, max-age=0, must-revalidate"}]}]}' > "$OUT/vercel.json"
echo "built $(find "$OUT" -type f | wc -l | tr -d ' ') files, $(du -sh "$OUT" | cut -f1)"
if [ "$1" = "--deploy" ]; then
  cd "$OUT" && vercel deploy --prod --yes --name forms-to-agents --scope rajatdandekars-projects
fi
