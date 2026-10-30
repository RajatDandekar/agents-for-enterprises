#!/bin/sh
# Build the static slides site into site-dist/ and (with --deploy) push it to Vercel.
# Only the decks, the deck engine and their images go up; no code, keys or notebooks.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/site-dist"
GH="https://github.com/RajatDandekar/agents-for-enterprises/blob/main"
rm -rf "$OUT" && mkdir -p "$OUT"
cp -R "$ROOT/engine" "$OUT/engine"
cp -R "$ROOT/figures" "$OUT/figures"
mkdir -p "$OUT/ledgerline/ledgerline/experience" && cp -R "$ROOT/ledgerline/ledgerline/experience/shots" "$OUT/ledgerline/ledgerline/experience/shots"
for d in "$ROOT"/lectures/L*/; do
  n="$(basename "$d")"; mkdir -p "$OUT/lectures/$n"
  cp "$d"index.html "$OUT/lectures/$n/"
  for f in "$d"*.js "$d"*.css; do [ -f "$f" ] && cp "$f" "$OUT/lectures/$n/"; done   # figs.js, figdata.js, deck css/js
  for sub in figs shots; do [ -d "$d$sub" ] && rsync -a --exclude '*.json' "$d$sub/" "$OUT/lectures/$n/$sub/"; done
  # the 3D figure (code, trace, poster; not its QA renders or scripts)
  [ -d "$d"flow3d ] && rsync -a --exclude qa --exclude '*.py' --exclude '*.md' --exclude 'envision_amaranth_cove.mp3' "$d"flow3d/ "$OUT/lectures/$n/flow3d/"
  # recorded production data a deck charts (not the logs or superseded sweeps)
  if [ -d "$d"experiments/production ]; then
    mkdir -p "$OUT/lectures/$n/experiments/production"
    for f in figdata_production.js waterfall.svg; do [ -f "$d"experiments/production/$f ] && cp "$d"experiments/production/$f "$OUT/lectures/$n/experiments/production/"; done
    [ -d "$d"experiments/production/shots ] && rsync -a --exclude 'superseded*' "$d"experiments/production/shots/ "$OUT/lectures/$n/experiments/production/shots/"
  fi
done
# Hub: notebooks open in Colab, assignments and kit briefs open on GitHub.
sed -e "s#<a href=\"lectures/\${dir}/\${nb}.ipynb\" download>Notebook</a>#<a href=\"https://colab.research.google.com/github/RajatDandekar/agents-for-enterprises/blob/main/lectures/\${dir}/\${nb}.ipynb\" target=\"_blank\" rel=\"noopener\">Open in Colab</a>#" \
    -e "s#href=\"lectures/\${dir}/\${a}.md\"#href=\"$GH/lectures/\${dir}/\${a}.md\" target=\"_blank\" rel=\"noopener\"#" \
    -e "s#href=\"modules/README.md\"#href=\"$GH/modules/README.md\"#" \
    -e "s#href=\"lectures/L12-your-module/DEMO_DAY.md\"#href=\"$GH/lectures/L12-your-module/DEMO_DAY.md\"#" \
    "$ROOT/index.html" > "$OUT/index.html"
echo '{"cleanUrls":false,"headers":[{"source":"/(.*)","headers":[{"key":"Cache-Control","value":"public, max-age=0, must-revalidate"}]}]}' > "$OUT/vercel.json"
echo "built $(find "$OUT" -type f | wc -l | tr -d ' ') files, $(du -sh "$OUT" | cut -f1)"
if [ "$1" = "--deploy" ]; then
  cd "$OUT" && vercel deploy --prod --yes --name forms-to-agents --scope rajatdandekars-projects
fi
