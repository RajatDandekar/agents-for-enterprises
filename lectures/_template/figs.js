/* Live figures for this lecture. Loaded BEFORE plates.js, so read helpers inside each figure: const P = window.Plates.
   Each figure builds up with the slide's .step reveals: step(k) gets k = steps shown. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});

/* Fig. 1 — example: bars that appear one per step. Numbers would come from experiments/logs/example.json. */
FIGS.example = (el) => {
  const P = window.Plates;
  const W = 760, H = 520;
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  const data = [['Screens', 7], ['Fields', 25], ['Codes', 10]];
  const bars = data.map(([k, v], i) => {
    const y = 60 + i * 140;
    P.txt(svg, 0, y + 34, k, 'font:22px var(--serif);fill:var(--ink-2)');
    const r = P.svgEl('rect', { x: 160, y, width: 0, height: 52, style: 'fill:var(--before);transition:width .6s ease' }, svg);
    const t = P.txt(svg, 170, y + 34, '', 'font:600 20px var(--mono);fill:var(--before)');
    return { r, t, v };
  });
  return { step(k) { bars.forEach((b, i) => { const on = i <= k; b.r.setAttribute('width', on ? b.v * 20 : 0); b.t.setAttribute('x', 170 + (on ? b.v * 20 : 0)); b.t.textContent = on ? P.fmt(b.v) : ''; }); } };
};
})();
