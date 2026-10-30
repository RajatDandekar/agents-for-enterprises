/* Live figures for Lecture 2 · The Brain (v4, Northbridge). Loaded BEFORE plates.js; helpers come from window.Plates.
   Where the numbers come from:
     window.BRAIN_TRACE  brain3d/trace.js, written by brain3d/capture_trace.py on Modal: ONE forward pass and generation of
                         Qwen2.5-0.5B-Instruct on Emma's question with the app's brain-stage system prompt.
     window.L2           figdata.js (gen_figdata.py from experiments/logs; see experiments/PROVENANCE.md): the cold-open
                         runs of Ask Northbridge (gemini-3.8-flash), the fix measured, tokens and cost, BPE, the tiny GPT,
                         the cut-off, the model card and the attention-by-hand example (the same as NB2 section 4).
   BPE by hand and attention by hand are recomputed here, in the browser, from the inputs in window.L2 (as NB2 does).
   Anything missing renders a TODO card instead of a number: TODO(brain3d) or TODO(v4 data). */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const P = () => window.Plates;
const TR = () => window.BRAIN_TRACE || null;
const L2 = () => window.L2 || null;
const dims = (el) => [parseInt(el.style.width, 10), parseInt(el.style.height, 10)];
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const vis = (s) => (s === null || s === undefined) ? '·' : esc(s).replace(/ /g, '␣').replace(/\n/g, '↵');
const pct = (p) => (p >= 0.1 ? (100 * p).toFixed(0) : p >= 0.001 ? (100 * p).toFixed(1) : (100 * p).toFixed(2)) + '%';
const fmt = (n) => Number(n).toLocaleString('en-GB');
const div = (host, cls, html = '') => { const d = document.createElement('div'); if (cls) d.className = cls; d.innerHTML = html; host.appendChild(d); return d; };
const stop = (e) => e.stopPropagation();
const btns = (host, labels, on, cb) => { const c = document.createElement('div'); c.className = 'ctl'; labels.forEach((l, i) => { const b = document.createElement('button'); b.innerHTML = l; if (i === on) b.classList.add('on'); b.onclick = (e) => { stop(e); c.querySelectorAll('button').forEach((x) => x.classList.remove('on')); b.classList.add('on'); cb(i); }; c.appendChild(b); }); host.appendChild(c); return c; };
const range = (host, label, min, max, val, step, cb, fmtv = (v) => v) => { const c = document.createElement('div'); c.className = 'ctl'; c.innerHTML = `<span>${label}</span><input type="range" min="${min}" max="${max}" step="${step}" value="${val}"><output>${fmtv(val)}</output>`; const r = c.querySelector('input'), o = c.querySelector('output'); r.oninput = (e) => { stop(e); o.textContent = fmtv(+r.value); cb(+r.value); }; r.onclick = stop; host.appendChild(c); return { set(v) { r.value = v; o.textContent = fmtv(v); } }; };
const todo = (el, kind, what, from) => { el.innerHTML = `<div class="todo-card${kind === 'brain3d' ? ' f3' : ''}"><span class="todo-k">TODO(${kind})</span><div>${what}</div><div class="todo-s">${from}</div></div>`; return { step() {} }; };
const NEEDTR = (el, what) => todo(el, 'brain3d', what, 'Fills in from brain3d/trace.json (the recorded Qwen2.5-0.5B-Instruct pass on Emma’s question).');
const NEEDFD = (el, what, log) => todo(el, 'v4 data', what, `Fills in from figdata.js (${log}).`);
const toggle = (el, sel, k, from) => el.querySelectorAll(sel).forEach((x, i) => x.classList.toggle('fade-hide', i + from > k));

function barList(host, rows, { max, color = 'var(--after)', w = 380, label = 150, hi = -1, dim = () => false } = {}) {
  const m = max || Math.max(...rows.map((r) => r[1]), 1e-9);
  host.innerHTML = rows.map(([t, p, sub], i) => `<div class="pb${i === hi ? ' hi' : ''}${dim(i) ? ' dim' : ''}"><span class="pt" style="width:${label}px">${vis(t)}${sub ? `<small class="pos">${sub}</small>` : ''}</span><span class="pr" style="width:${w}px"><i style="width:${Math.max(1, (w * p) / m)}px;background:${color}"></i></span><span class="pbv">${pct(p)}</span></div>`).join('');
}
const userToks = () => TR().tokens.filter((t) => t.role === 'user');
const ansText = (steps, upto) => steps.slice(0, upto).map((s) => s.text).join('').replace(/<\|im_end\|>|<\|endoftext\|>/g, '');

/* =============================== the 3D scene, one stage per section ===============================
   When brain3d/deck.js has registered FIGS.brain3d, the slide is handed to it (data-section = 1..9 or "all").
   Until then a flat stand-in shows the nine stations of the scene, this section's station lit, earlier ones kept,
   later ones ghosted, with the planned clicks on the left. */
const SECT = {
  1: ['The game', 'Text in, a guess out.', ['Emma’s question goes in on the left', 'The model is one sealed box', 'Out comes a bar for every possible next token: the top five']],
  2: ['Tokens', 'The chat becomes a strip of tiles.', ['The chat: system prompt, then Emma’s message', 'It becomes one strip of token tiles', 'Each tile shows its id', '“Manchester” as tiles', 'A number becomes digit tiles']],
  3: ['Vectors', 'Each tile becomes 896 numbers.', ['Each tile rises into a column of 896 numbers', 'A few real values on “battery”', 'A 3D map: similar words sit close', 'The neighbours of “battery” and “Manchester”']],
  4: ['Attention', 'The last token looks back.', ['Arcs from the last token back to earlier ones', 'Thickness is the real attention weight', 'A second head, a third head', 'No arc ever goes forward']],
  5: ['24 blocks', 'Looking, then thinking, 24 times.', ['Attention plus MLP is one block', 'The columns rise through 24 blocks', 'At each block, what it would say now', 'The answer forms near the top']],
  6: ['A choice', 'From a vector to one token.', ['The top vector meets the whole vocabulary', 'Scores become probabilities', 'The temperature dial reshapes the bars', 'One token is picked']],
  7: ['The loop', 'One token at a time.', ['The picked token joins the strip', 'The whole pass runs again', 'The answer grows, token by token', 'The digits, and how sure it was of each']],
  8: ['Training', 'Where the weights came from.', ['The blocks, before training', 'Pretraining fills in the weights', 'Instruction tuning, then preference tuning', 'The last training day']],
  9: ['Why it made it up', 'Trace the number back.', ['Follow the number back through the scene', 'Nothing in the input carried the stock', 'Socket 1: knowledge, Lecture 3', 'Socket 2: tools, Lecture 4']],
  all: ['The whole machine', 'One sentence, all the way through.', ['The whole scene, every stage', 'The whole trace, token by token', 'The two sockets for Lectures 3 and 4']],
};
const STATIONS = ['The game', 'Tokens', 'Vectors', 'Attention', '24 blocks', 'A choice', 'The loop', 'Training', 'The fix'];
FIGS.b3d = (el) => {
  if (el.dataset.section === 'all' && typeof FIGS.brain3d === 'function') {
    /* The closing overview: section 9's end state (every stage in the scene, both sockets lit), plus a link that plays
       the whole trace from the start in the standalone page. */
    el.dataset.section = '9';
    const inner = FIGS.brain3d(el);
    el.insertAdjacentHTML('afterend', '<div class="ctl" style="position:absolute;right:100px;top:30px;margin:0;z-index:3"><a class="live" href="brain3d/index.html?autoplay" target="_blank" rel="noopener">Play the whole trace <code>brain3d/index.html</code></a></div>');
    return { step() { inner.step(3, true); } };
  }
  if (typeof FIGS.brain3d === 'function') return FIGS.brain3d(el);
  const s = el.dataset.section, n = s === 'all' ? 10 : +s, [title, sub, clicks] = SECT[s];
  el.innerHTML = `<div class="b3d"></div><div class="b3d-side"><h2>${title}</h2><p class="sub">${sub}</p><ol class="b3d-clk">${clicks.map((c) => `<li>${c}</li>`).join('')}</ol></div>
    <div class="b3d-badge"><b>TODO(brain3d)</b>The 3D scene mounts here; this flat map is a stand-in.</div>`;
  const svg = P().svgEl('svg', { viewBox: '0 0 940 520', width: 940, height: 520 }, el.querySelector('.b3d'));
  svg.style.left = '580px'; svg.style.top = '190px';
  /* a snake: stations 1-5 left to right, then 6-9 right to left underneath */
  const pos = STATIONS.map((_, i) => (i < 5 ? [90 + i * 190, 110] : [850 - (i - 5) * 190 - 95, 370]));
  const d = `M${pos[0][0]},${pos[0][1]} L${pos[4][0]},${pos[4][1]} C${pos[4][0] + 120},${pos[4][1]} ${pos[4][0] + 120},${pos[5][1]} ${pos[5][0]},${pos[5][1]} L${pos[8][0]},${pos[8][1]}`;
  P().svgEl('path', { d, style: 'fill:none;stroke:#d3e3fb;stroke-width:6;stroke-linecap:round' }, svg);
  const done = n === 10 ? 9 : n;
  if (done > 1) {
    const L = P().svgEl('path', { d, style: 'fill:none;stroke:#2a78d6;stroke-width:6;stroke-linecap:round' }, svg);
    const len = L.getTotalLength ? L.getTotalLength() : 2000, seg = [0, 190, 380, 570, 760, 1040, 1230, 1420, 1610];
    if (n !== 10) L.style.strokeDasharray = `${seg[done - 1]} ${len}`;
  }
  STATIONS.forEach((name, i) => {
    const [x, y] = pos[i], k = i + 1, state = n === 10 || k < n ? 'past' : k === n ? 'cur' : 'next';
    const g = P().svgEl('g', {}, svg);
    if (state === 'cur') P().svgEl('circle', { cx: x, cy: y, r: 76, style: 'fill:rgba(60,144,255,.15)' }, g);
    P().svgEl('rect', { x: x - 52, y: y - 52, width: 104, height: 104, rx: 28, style: `fill:${state === 'cur' ? '#0b57d0' : '#ffffff'};stroke:${state === 'cur' ? '#0b57d0' : state === 'past' ? '#8dbcff' : '#e3e8ef'};stroke-width:2.5` }, g);
    P().txt(g, x, y + 14, String(k), `font:500 40px var(--font);fill:${state === 'cur' ? '#fff' : state === 'past' ? '#0b57d0' : '#c3c8d0'}`, 'middle');
    P().txt(g, x, y + 88, name, `font:${state === 'cur' ? 600 : 500} 20px var(--font);fill:${state === 'cur' ? '#0b57d0' : state === 'past' ? '#45474d' : '#b3b8c0'}`, 'middle');
  });
  return { step(k) { el.querySelectorAll('.b3d-clk li').forEach((li, i) => { li.classList.toggle('on', i < k); li.classList.toggle('off', i >= k); }); } };
};

/* =============================== opening ===============================*/
/* The live app at stage=brain, from the Experience team's end-to-end test (ledgerline/ledgerline/experience/shots/27_after_stage_brain.png),
   cropped to the chat (figs/stage_brain_chat.jpg). Ledgerline's own figure comes from the seed data (WORLD_V4.md). */
FIGS.coldshot = (el) => {
  const [W, H] = dims(el), h = Math.round(W * 330 / 730);
  el.innerHTML = `<div class="shot s0" style="left:0;top:0;width:${W}px;height:${h}px"><img src="figs/stage_brain_chat.jpg" alt="Ask Northbridge at stage brain: We currently have 48 city e-bike battery packs" style="position:static;width:100%;height:auto"></div>
    <div class="win truthwin s1 tr" style="left:0;top:${H - 156}px;width:${W}px">
      <div class="tb">Ledgerline ERP 7.2 — Stock enquiry<span class="sp"></span><span class="bx">_</span><span class="bx">□</span><span class="bx">×</span></div>
      <div class="tw-body"><span class="k"><b>BAT-500</b> · Battery pack, 36 V 500 Wh</span><span class="v">5,400</span><span class="k">Manchester main stores · on hand</span><span class="k">(Leeds stores: 1,200)</span></div></div>`;
  return { step(k) { el.querySelector('.s1').classList.toggle('fade-hide', k < 1); } };
};

/* Repeated cold-open runs of Ask Northbridge (experiments builder). */
FIGS.coldruns = (el) => {
  const L = L2(); if (!L || !L.cold) return NEEDFD(el, 'The same question asked of Ask Northbridge again and again.', 'experiments/logs/cold_open.json');
  const C = L.cold, chip = (n) => `<span class="tchip ${n === C.true_answer ? 'c1' : 'dg'}" style="font-size:24px;padding:10px 14px">${n === null ? 'declined' : fmt(n)}</span>`;
  el.innerHTML = `<div class="card"><span class="tag nt">${C.summary.n} runs · the app’s settings · ${esc(C.model)}</span><div class="chips">${C.summary.figures.map(chip).join('')}</div></div>
   <div class="card r1 tr" style="margin-top:12px"><span class="tag nt">${C.summary_t1.n} more · temperature 1.0</span><div class="chips">${C.summary_t1.figures.map(chip).join('')}</div>
   <div class="ftiny">${C.summary.correct + C.summary_t1.correct} of ${C.summary.n + C.summary_t1.n} said ${fmt(C.true_answer)}. Every run gave a figure.</div></div>
   <div class="card bf r2 tr" style="margin-top:12px;font-size:19px"><span class="tag bf">Emma: “${esc(C.follow_up.question)}”</span><div>“${esc(C.follow_up.reply)}”</div></div>`;
  return { step(k) { el.querySelector('.r1').classList.toggle('fade-hide', k < 1); el.querySelector('.r2').classList.toggle('fade-hide', k < 2); } };
};

/* The model we open: config facts (Hugging Face config.json and model card), plus what it answered in our trace. */
FIGS.qwencard = (el) => {
  const T = TR(), m = T ? T.meta : null;
  const tiles = [['blocks', m ? m.layers : 24], ['numbers per token vector', fmt(m ? m.d_model : 896)], ['attention heads per block', m ? m.heads : 14], ['tokens in its vocabulary', m ? `about ${fmt(Math.floor(m.tokenizer_len / 1000))},000` : 'about 151,000'], ['parameters (numbers learnt in training)', m ? `${Math.round(m.params / 1e6)} million` : '494 million'], ['tokens it can read at once', fmt(m ? m.context : 32768)]];
  el.innerHTML = `<div class="tiles">${tiles.map((t) => `<div class="tile"><b>${t[1]}</b><span>${t[0]}</span></div>`).join('')}</div>
    <div class="card af s1 tr" style="margin-top:14px;font-size:20px"><span class="tag af">Same question, same system prompt · Qwen2.5-0.5B-Instruct · greedy</span><div class="ans">${T ? '“' + esc(T.generation.text.trim()) + '”' : '<span class="todo-in">TODO(brain3d)</span> its answer, from the recorded trace'}</div></div>`;
  return { step(k) { el.querySelector('.s1').classList.toggle('fade-hide', k < 1); } };
};

/* =============================== 1 · the game ===============================*/
FIGS.nextbars = (el) => {
  const T = TR(); if (!T) return NEEDTR(el, 'The top five next tokens right after Emma’s question, and at the first digit of the answer, with their probabilities.');
  const views = [['after Emma’s question', T.final.last['1.0'], '…in Manchester stores?', ''], ['at the first digit', T.final.digit ? T.final.digit['1.0'] : null, '…in Manchester stores?', ansText(T.generation.greedy, T.generation.digit_steps[0])]];
  let v = 0;
  btns(el, views.map((x) => x[0]), 0, (i) => { v = i; draw(); });
  const head = div(el, 'ptext'), list = div(el, ''), foot = div(el, 'ftiny');
  const draw = () => {
    const [, rows, q, a] = views[v];
    head.innerHTML = `<span class="mono">Emma: ${esc(q)} ↵ Ask Northbridge: ${esc(a)}</span><span class="cursor">▍</span>`;
    barList(list, (rows || []).slice(0, 5).map((t) => [t.text, t.p]), { w: 400, label: 170, hi: 0 });
    const s = (rows || []).slice(0, 5).reduce((x, t) => x + t.p, 0);
    foot.innerHTML = `Top 5 of ${fmt(T.meta.vocab)} possible next tokens. Together they hold ${pct(s)} of the probability; the other ${fmt(T.meta.vocab - 5)} share the rest.`;
  };
  draw();
  return { step() {} };
};

/* =============================== 2 · tokens ===============================*/
/* What the model is sent: the chat template text. From the trace when present; otherwise built from the same two
   sources the trace uses (the app's BRAIN prompt in harness.py, and the Qwen2.5 chat template). */
const BRAIN_SYS = 'You are Ask Northbridge, the assistant on the home page of Northbridge Cycles, Manchester, a maker of e-bikes.\nYou are talking to Emma Clarke, purchase executive. Today is Monday 26 October 2026. Help with purchasing: stock, orders,\napprovals and receipts. Keep replies short and plain. No emoji.';
const QUESTION = 'How many city e-bike battery packs do we have in Manchester stores?';
FIGS.chattpl = (el) => {
  const T = TR(), sys = T ? T.prompt.system : BRAIN_SYS, q = T ? T.prompt.question : QUESTION;
  const sp = (s) => `<span class="sp">${esc(s)}</span>`;
  el.innerHTML = `<div class="tpltext">${sp('<|im_start|>')}system↵<span class="sy s1 tr">${esc(sys).replace(/\n/g, ' ')}</span>${sp('<|im_end|>')}↵${sp('<|im_start|>')}user↵<span class="us s2 tr">${esc(q)}</span>${sp('<|im_end|>')}↵${sp('<|im_start|>')}assistant↵<span class="cursor">▍</span></div>
   <div class="legendrow"><span><i style="background:#b3e3d1"></i>system: the builder’s instructions</span><span><i style="background:#dbe9ff"></i>user: Emma</span><span><i style="background:#fff1e8;border:1px solid var(--before)"></i>markers the template adds</span></div>
   <div class="ftiny">${T ? `From the recorded trace: <code>${esc(T.prompt.source || 'harness.py')}</code>, through the model’s own chat template.` : 'Built from the app’s brain-stage prompt (ledgerline/ledgerline/experience/harness.py, BRAIN, for Emma) and the Qwen2.5 chat template.'}</div>`;
  return { step() {} };
};

FIGS.toksplit = (el) => {
  const T = TR(); if (!T) return NEEDTR(el, 'Emma’s question as real Qwen2.5 tokens with their ids; how many tokens the whole prompt is (system, Emma, template); and how “Manchester”, “e-bike”, “5,400” and “285,600” are cut.');
  const U = userToks();
  const cuts = ['5,400', ' 285,600', ' Manchester', ' e-bike', ' Northbridge', ' Ledgerline'].filter((k) => T.number_cuts[k]);
  el.innerHTML = `<div class="chips r0">${U.map((t, i) => `<span class="idc"><span class="tchip ${t.digit ? 'dg' : 'c' + (i % 4)}">${vis(t.text)}</span><span class="id">${t.id}</span></span>`).join('')}</div>
    <div class="counts r1 tr"><div class="cnt a"><b>${U.length}</b>tokens in Emma’s question</div><div class="cnt"><b>${T.prompt.counts.system}</b>in the system prompt</div><div class="cnt"><b>${T.prompt.counts.template}</b>template markers</div><div class="cnt a"><b>${T.prompt.n_tokens}</b>sent in all</div></div>
    <div class="cuts r2 tr">${cuts.map((k) => `<span class="w">${vis(k)}</span><span class="chips">${T.number_cuts[k].map((p, i) => `<span class="tchip ${/\d/.test(p.text) ? 'dg' : 'c' + (i % 4)}">${vis(p.text)}</span>`).join('')}</span>`).join('')}</div>`;
  return { step(k) { el.querySelector('.r1').classList.toggle('fade-hide', k < 1); el.querySelector('.r2').classList.toggle('fade-hide', k < 2); } };
};

/* BPE by hand on a toy corpus of Northbridge words, computed here. "_" marks the end of a word. */
FIGS.bpe = (el) => {
  const L = L2(); if (!L || !L.bpe) return NEEDFD(el, 'BPE by hand on a few Northbridge words.', 'experiments/logs/bpe.json');
  const B = L.bpe.hand, words = B.corpus.split(' '), counts = {}; words.forEach((w) => { counts[w] = (counts[w] || 0) + 1; });
  const uniq = Object.keys(counts);
  const top = div(el, 'bpe-top'), wl = div(el, '');
  let m = 0;
  range(el, 'merges', 0, B.steps.length, 0, 1, (v) => { m = v; draw(); });
  const draw = () => {
    const st = m ? B.steps[m - 1] : null, split = (w) => (st ? st.words[w] : [...w, '_']);
    top.innerHTML = `<div class="stat"><b>${st ? st.vocab_size : B.start_vocab.length}</b><span>pieces in the vocabulary</span></div><div class="stat"><b>${st ? st.corpus_tokens : B.start_tokens}</b><span>pieces to write all ${words.length} words</span></div>` +
      (st ? `<div class="stat wide"><span>merge ${m}: the most frequent neighbouring pair</span><b class="a">${esc(st.pair[0])} + ${esc(st.pair[1])} → ${esc(st.pair[0] + st.pair[1])}</b><span>seen ${st.count} times</span></div>` : '<div class="stat wide"><span>start: every word is a row of single letters; _ marks the end of a word</span><b>0 merges</b></div>');
    wl.innerHTML = uniq.map((w) => `<div class="bw"><span class="lab">${w} ×${counts[w]}</span><span class="chips">${split(w).map((t) => `<span class="tchip${st && t === st.pair[0] + st.pair[1] ? ' new' : ''}">${esc(t)}</span>`).join('')}</span></div>`).join('');
  };
  draw();
  const R = L.bpe.learnt.merge_rank;
  div(el, 'ftiny', `Learnt the same way on Northbridge’s whole corpus (${fmt(L.bpe.learnt.distinct_words)} distinct words): “Voltway” becomes one token at merge ${R.Voltway}, “Manchester” at ${R.Manchester}, “battery” at ${R.battery}.`);
  return { step() {} };
};

/* What one call costs, in tokens and pounds (experiments builder). */
FIGS.tokcost = (el) => {
  const L = L2(); if (!L || !L.cost) return NEEDFD(el, 'One Ask Northbridge reply, counted.', 'experiments/logs/cold_open.json');
  const c = L.cost, g = (x) => '£' + x.toFixed(6), langs = L.tokens.languages;
  const order = Object.keys(langs).sort((a, b) => langs[a].qwen - langs[b].qwen), mx = Math.max(...order.map((k) => langs[k].qwen));
  el.innerHTML = `<div class="counts"><div class="cnt a"><b>${c.tokens_in}</b>tokens in</div><div class="cnt a"><b>${Math.round(c.tokens_out_mean)}</b>tokens out (mean)</div><div class="cnt"><b>${g(c.per_question_gbp)}</b>per question</div></div>
   <div class="card bf r1 tr" style="margin-top:12px;font-size:19px"><b>Plus ${c.thinking_tokens} hidden “thinking” tokens</b>, billed as output, that the reply never shows. Counted in: <b>${g(c.per_question_with_thinking_gbp)}</b> a question, <b>£${c.per_1000_with_thinking_gbp.toFixed(2)}</b> per 1,000 questions (£${c.per_1000_questions_gbp.toFixed(2)} without).</div>
   <div class="r2 tr" style="margin-top:14px"><div class="tag nt">Emma’s question in six languages · Qwen tokens</div>
   ${order.map((k) => `<div class="pb" style="margin:4px 0"><span class="pt" style="width:110px;font-family:var(--font)">${k}</span><span class="pr" style="width:420px"><i style="width:${420 * langs[k].qwen / mx}px;background:var(--after)"></i></span><span class="pbv">${langs[k].qwen}</span></div>`).join('')}</div>
   <div class="ftiny">${esc(L.cold.model)} at $${c.price_usd_per_million.in} / $${c.price_usd_per_million.out} per million tokens in / out, £ = $ × ${c.usd_gbp}.</div>`;
  return { step(k) { el.querySelector('.r1').classList.toggle('fade-hide', k < 1); el.querySelector('.r2').classList.toggle('fade-hide', k < 2); } };
};

/* =============================== 3 · vectors ===============================*/
FIGS.embrow = (el) => {
  const T = TR(); if (!T) return NEEDTR(el, 'The first 16 of the 896 numbers in the row for “ battery”, read from the model’s embedding table.');
  const i = T.key_positions.battery, v = T.embeddings.values.find((x) => x.i === i);
  const [svg] = [P().svgEl('svg', { viewBox: '0 0 820 330', width: 820, height: 330 }, el)];
  const x0 = 200, y0 = 30, w = 470, h = 230;
  P().svgEl('rect', { x: x0, y: y0, width: w, height: h, rx: 14, style: 'fill:var(--card)' }, svg);
  for (let r = 1; r < 12; r++) P().svgEl('rect', { x: x0 + 10, y: y0 + r * 19, width: w - 20, height: 1, style: 'fill:#d9dee6' }, svg);
  const ry = y0 + 6 * 19 - 9;
  P().svgEl('rect', { x: x0 + 4, y: ry, width: w - 8, height: 20, rx: 6, style: 'fill:var(--after)' }, svg);
  P().txt(svg, x0 - 14, ry + 15, `row ${T.tokens[i].id}`, 'font:500 16px var(--mono);fill:var(--after)', 'end');
  P().txt(svg, x0 - 14, ry - 8, '“␣battery”', 'font:500 18px var(--font);fill:var(--ink)', 'end');
  P().txt(svg, x0 + w / 2, y0 - 10, `${fmt(T.meta.d_model)} numbers per row`, 'font:500 16px var(--font);fill:var(--ink-2)', 'middle');
  P().txt(svg, x0 + w + 16, y0 + h / 2, `${fmt(T.meta.vocab)} rows`, 'font:500 16px var(--font);fill:var(--ink-2)');
  P().txt(svg, x0 + w + 16, y0 + h / 2 + 22, 'one per token', 'font:400 15px var(--font);fill:var(--ink-3)');
  div(el, 'ftiny r1 tr', `The row for “␣battery”, first 16 of ${fmt(T.meta.d_model)}:`);
  div(el, 'vals r1 tr', v.v16.map((x) => `<span class="val ${x >= 0 ? 'p' : 'm'}">${x.toFixed(3)}</span>`).join(''));
  return { step(k) { el.querySelectorAll('.r1').forEach((x) => x.classList.toggle('fade-hide', k < 1)); } };
};

const GC = { 'bike parts': '#0b57d0', places: '#c4511f', purchasing: '#138a60', time: '#8a4fd6', numbers: '#b8860b', animals: '#d6336c' };
FIGS.embmap = (el) => {
  const T = TR(); if (!T) return NEEDTR(el, 'A map of about 50 words (bike parts, places, purchasing words, days, numbers, animals) placed by their real embedding rows, and the nearest neighbours of “battery” and “Manchester” in the whole vocabulary.');
  const Pw = T.embeddings.pca.words, N = T.embeddings.neighbours;
  const [W, H] = dims(el), mw = W - 300;
  const svg = P().svgEl('svg', { viewBox: `0 0 ${mw} ${H - 40}`, width: mw, height: H - 40 }, el);
  svg.style.position = 'absolute'; svg.style.left = '0'; svg.style.top = '0';
  const xs = Pw.map((p) => p.xyz[0]), ys = Pw.map((p) => p.xyz[1]);
  const [a, b, c, d] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  const X = (v) => 30 + (mw - 140) * (v - a) / (b - a), Y = (v) => 20 + (H - 110) * (1 - (v - c) / (d - c));
  const placed = [];
  const spot = (x, y, w) => { for (const dy of [0, -16, 16, -32, 32, -48, 48]) { const r = [x, y + dy - 13, x + w, y + dy + 3]; if (!placed.some((q) => r[0] < q[2] && r[2] > q[0] && r[1] < q[3] && r[3] > q[1])) { placed.push(r); return dy; } } return 0; };
  Pw.forEach((p) => {
    const x = X(p.xyz[0]), y = Y(p.xyz[1]);
    P().svgEl('circle', { cx: x, cy: y, r: 6, style: `fill:${GC[p.group] || '#888'}` }, svg);
    const dy = spot(x + 9, y + 5, 8.4 * p.word.length);
    P().txt(svg, x + 9, y + 5 + dy, p.word, `font:${['battery', 'Manchester'].includes(p.word) ? 600 : 450} 15px var(--font);fill:var(--ink)`);
  });
  const leg = div(el, '', Object.entries(GC).map(([g, col]) => `<span style="margin-right:14px;font-size:15px;color:var(--ink-2)"><i style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${col};margin-right:6px"></i>${g}</span>`).join(''));
  leg.style.cssText = `position:absolute;left:0;top:${H - 34}px;width:${mw}px`;
  const side = div(el, 'r1 tr', Object.keys(N).map((w) => `<div class="card" style="padding:12px 16px;margin-bottom:10px"><div class="tag af">nearest to ${esc(w)}</div>${N[w].neighbours.slice(0, 5).map((x) => `<div class="pb" style="margin:3px 0"><span class="pt" style="width:130px;font-size:16px">${vis(x.text)}</span><span class="pbv">${x.cos.toFixed(2)}</span></div>`).join('')}</div>`).join(''));
  side.style.cssText = `position:absolute;left:${mw + 20}px;top:0;width:280px`;
  return { step(k) { side.classList.toggle('fade-hide', k < 1); } };
};

/* =============================== 4 · attention ===============================*/
/* Attention by hand. Toy vectors, two numbers each, chosen by hand; everything else is computed here. */
const HAND0 = { tokens: ['Emma', 'needs', '2,000', 'packs'], Q: [[1, 0], [1, 1], [0, 1], [0, 2]], K: [[2, 0], [0, 1], [1, 3], [1, 1]], V: [[4, 0], [0, 1], [0, 8], [2, 2]] };
const vec = (v) => `[${v.map((x) => (Number.isInteger(x) ? x : x.toFixed(2))).join(', ')}]`;
FIGS.handattn = (el) => {
  const h = (L2() && L2().hand) || HAND0, i = 3, q = h.Q[i], d = q.length;
  const sc = h.K.map((k) => k[0] * q[0] + k[1] * q[1]), ss = sc.map((s) => s / Math.sqrt(d)), ex = ss.map(Math.exp), sum = ex.reduce((a, b) => a + b, 0), w = ex.map((e) => e / sum);
  const y = [0, 1].map((c) => h.V.reduce((a, v, j) => a + w[j] * v[c], 0));
  el.innerHTML = `<div class="ptext" style="font-size:19px">The query of <b>“${h.tokens[i]}”</b>: <span class="mono">q = ${vec(q)}</span>. It may look at itself and the three tokens before it.</div><table class="t"><tr><th>“${h.tokens[i]}” looks at</th><th class="n c0">key k</th><th class="n c1">1 · score q·k</th><th class="n c2">2 · ÷ √2</th><th class="n c3">3 · eˣ</th><th class="n c4">4 · weight</th><th class="n c5">value v</th></tr>
   ${h.tokens.map((t, j) => `<tr><td><b>${t}</b></td><td class="n c0">${vec(h.K[j])}</td><td class="n c1">${vec(q)}·${vec(h.K[j])} = <b>${sc[j]}</b></td><td class="n c2">${ss[j].toFixed(2)}</td><td class="n c3">${ex[j].toFixed(2)}</td><td class="n c4"><b>${w[j].toFixed(3)}</b></td><td class="n c5">${vec(h.V[j])}</td></tr>`).join('')}
   <tr class="tot"><td></td><td></td><td></td><td></td><td class="n c3">sum ${sum.toFixed(2)}</td><td class="n c4">sum 1.000</td><td></td></tr></table>
   <div class="card af c5" style="margin-top:14px;font-size:20px"><b>5 · add up the values, each times its weight</b><br><span class="mono">${h.tokens.map((t, j) => `${w[j].toFixed(3)}·${vec(h.V[j])}`).join(' + ')}</span> = <b class="a mono">${vec(y)}</b><br>The new vector for “${h.tokens[i]}” is mostly the value of “${h.tokens[w.indexOf(Math.max(...w))]}”: how many packs Emma needs.</div>`;
  const cols = ['c1', 'c2', 'c3', 'c4', 'c5'];
  return { step(k) { cols.forEach((c, j) => el.querySelectorAll('.' + c).forEach((x) => { x.classList.add('tr'); x.classList.toggle('fade-hide', j > k); })); el.querySelectorAll('.c0').forEach((x) => x.classList.remove('fade-hide')); } };
};

/* Real attention, three heads picked by a rule in capture_trace.py, from the last prompt position. */
FIGS.heads = (el) => {
  const T = TR(); if (!T) return NEEDTR(el, 'The real attention weights of three heads from the last position: where it looks (“battery”, “Manchester”, or resting on the first token), and how the attention splits between the system prompt, Emma’s words and the template.');
  const H = T.attention.heads, toks = T.tokens;
  let hi = 0;
  btns(el, H.map((h) => `block ${h.layer}, head ${h.head}`), 0, (i) => { hi = i; draw(); });
  const why = div(el, 'ftiny'), list = div(el, ''), share = div(el, 'ftiny');
  const draw = () => {
    const h = H[hi], rows = h.row_last.map((v, j) => [j, v]).sort((a, b) => b[1] - a[1]).slice(0, 7);
    why.innerHTML = h.looks_at === 'start' ? `This head rests: it puts <b>${pct(h.weight_last)}</b> on the very first token. Heads do this when they have nothing to look for.`
      : `Of all heads in blocks 3–24, this one puts the most weight on <b>“${h.looks_at}”</b>: ${pct(h.weight_last)}.`;
    barList(list, rows.map(([j, v]) => [toks[j].text, v, toks[j].role === 'user' ? 'Emma' : toks[j].role]), { w: 360, label: 240, max: 1 });
  };
  const s = T.attention.last.share_by_role;
  share.innerHTML = `Averaged over all ${T.meta.layers} blocks and ${T.meta.heads} heads, the last position gives <b>${pct(s.system)}</b> of its attention to the system prompt, <b>${pct(s.user)}</b> to Emma’s words and <b>${pct(s.template)}</b> to the template markers.`;
  draw();
  return { step() {} };
};

/* Position: order matters, but a weighted sum does not see order. */
FIGS.position = (el) => {
  el.innerHTML = `<div class="chips r0" style="margin-bottom:10px"><span class="tchip c0">Emma</span><span class="tchip c1">␣approves</span><span class="tchip c2">␣Daniel</span><span class="ftiny" style="margin:0 0 0 10px;align-self:center">vectors a, b, c</span></div>
  <div class="chips r0"><span class="tchip c2">Daniel</span><span class="tchip c1">␣approves</span><span class="tchip c0">␣Emma</span><span class="ftiny" style="margin:0 0 0 10px;align-self:center">the same a, b, c in another order</span></div>
  <div class="card r1 tr" style="margin:16px 0;font-size:21px">Attention adds up vectors. A sum does not care about order: a + b + c = c + b + a. On its own, the model could not tell who approves whom.</div>
  <div class="card af r2 tr" style="font-size:21px"><b>The fix:</b> mix each token’s position into the match. Qwen2.5 turns every query and key by an angle that grows with its position (“rotary positions”), so how well two tokens match also depends on how far apart they are.</div>`;
  return { step(k) { el.querySelector('.r1').classList.toggle('fade-hide', k < 1); el.querySelector('.r2').classList.toggle('fade-hide', k < 2); } };
};

/* =============================== 5 · the stack ===============================*/
FIGS.lens = (el) => {
  const T = TR(); if (!T) return NEEDTR(el, 'The model’s best guess for the next token after each of the 24 blocks, at the last position: the answer forming as it rises.');
  const Ld = T.logit_lens.last, fin = Ld[Ld.length - 1].top[0].text;
  let k0 = Ld.length - 1;
  const list = div(el, '');
  range(el, 'after block', 1, Ld.length, Ld.length, 1, (v) => { k0 = v - 1; draw(); }, (v) => `${v} of ${Ld.length}`);
  const [W] = dims(el);
  const svg = P().svgEl('svg', { viewBox: `0 0 ${W} 250`, width: W, height: 250 }, el);
  const draw = () => {
    barList(list, Ld[k0].top.slice(0, 5).map((t) => [t.text, t.p]), { w: 400, label: 170, max: 1, hi: 0 });
    svg.innerHTML = '';
    const x0 = 30, w = W - 60;
    P().txt(svg, x0, 18, `top guess after each block · the model’s final pick is ${vis(fin)}`, 'font:500 15px var(--font);fill:var(--ink-2)');
    Ld.forEach((l, i) => {
      const x = x0 + (w * i) / (Ld.length - 1), same = l.top[0].text === fin;
      P().svgEl('circle', { cx: x, cy: 52, r: i === k0 ? 9 : 6, style: `fill:${same ? 'var(--after)' : '#c9ced6'}` }, svg);
      if (i % 4 === 3 || i === 0) P().txt(svg, x, 84, String(l.layer), 'font:500 13px var(--mono);fill:var(--ink-3)', 'middle');
      const t = P().txt(svg, 0, 0, vis(l.top[0].text.trim() || l.top[0].text).slice(0, 7), `font:450 14px var(--mono);fill:${same ? 'var(--after)' : 'var(--ink-3)'}`);
      t.setAttribute('transform', `translate(${x - 4},104) rotate(70)`);
    });
  };
  draw();
  return { step() {} };
};

/* =============================== 6 · a choice ===============================*/
/* Softmax worked on the real top 10 at the first digit: the score of each token relative to the top one is ln(p / p_top). */
FIGS.softmax = (el) => {
  const T = TR(); if (!T || !T.final.digit) return NEEDTR(el, 'Softmax worked by hand on the model’s real top scores at the first digit of its answer.');
  const rows = T.final.digit['1.0'].slice(0, 5), z = rows.map((r) => Math.log(r.p / rows[0].p)), e = z.map(Math.exp), s = e.reduce((a, b) => a + b, 0);
  el.innerHTML = `<table class="t"><tr><th>token</th><th class="n s0">score z</th><th class="n s1">eᶻ</th><th class="n s2">÷ sum: share of these 5</th><th class="n s3">real p, all ${fmt(T.meta.vocab)}</th></tr>
   ${rows.map((r, i) => `<tr><td class="mono">${vis(r.text)}</td><td class="n s0">${z[i].toFixed(2)}</td><td class="n s1">${e[i].toFixed(3)}</td><td class="n s2">${(e[i] / s).toFixed(3)}</td><td class="n s3"><b>${r.p.toFixed(3)}</b></td></tr>`).join('')}
   <tr class="tot"><td></td><td></td><td class="n s1">sum ${s.toFixed(3)}</td><td class="n s2">1.000</td><td class="n s3">${rows.reduce((a, r) => a + r.p, 0).toFixed(3)}</td></tr></table>
   <p class="ftiny">Scores are shown relative to the top token (only differences between scores matter to softmax). The last column is the share of all ${fmt(T.meta.vocab)} tokens; the other tokens hold the rest.</p>`;
  return { step(k) { for (let c = 0; c < 4; c++) el.querySelectorAll('.s' + c).forEach((x) => { x.classList.add('tr'); x.classList.toggle('fade-hide', c > k); }); } };
};

FIGS.temp = (el) => {
  const T = TR(); if (!T || !T.final.digit) return NEEDTR(el, 'The real top 10 at the first digit, at temperatures 0, 0.7, 1.0 and 1.2, and the token picked.');
  const Ts = ['0', '0.7', '1.0', '1.2'];
  let ti = 2;
  btns(el, Ts.map((t) => (t === '0' ? 'T = 0 (always the top)' : 'T = ' + t)), ti, (i) => { ti = i; draw(); });
  const list = div(el, ''), foot = div(el, 'ftiny');
  const draw = () => {
    const rows = T.final.digit[Ts[ti]];
    barList(list, rows.slice(0, 8).map((t) => [t.text, t.p]), { w: 420, label: 120, max: 1, hi: 0 });
    foot.innerHTML = ti === 0 ? `At T = 0 the top token is taken every time: <b>${vis(rows[0].text)}</b>.` : `Probabilities after dividing every score by ${Ts[ti]}. The greedy answer took <b>${vis(T.generation.digits[0].token)}</b> here.`;
  };
  draw();
  return { step() {} };
};

/* =============================== 7 · the loop ===============================*/
FIGS.gen = (el) => {
  const T = TR(); if (!T) return NEEDTR(el, 'The model’s whole answer, token by token: each token, its probability, and the four tokens it beat.');
  const G = T.generation.greedy.filter((s) => !/<\|/.test(s.text)), dg = new Set(T.generation.digit_steps);
  let k0 = Math.min(G.length - 1, (T.generation.digit_steps[0] ?? 0));
  const box = div(el, 'gen'), alts = div(el, 'alts');
  range(el, 'token', 1, G.length, k0 + 1, 1, (v) => { k0 = v - 1; draw(); }, (v) => `${v} of ${G.length}`);
  const draw = () => {
    box.innerHTML = G.slice(0, k0 + 1).map((s, j) => `<span class="tk${j === k0 ? ' cur' : ''}${dg.has(j) ? ' dg' : ''}">${esc(s.text)}</span>`).join('') + '<span class="cursor">▍</span>';
    barList(alts, G[k0].alts.slice(0, 5).map((a) => [a.text, a.p]), { w: 380, label: 160, max: 1, hi: G[k0].alts.findIndex((a) => a.id === G[k0].id) });
  };
  draw();
  return { step() {} };
};

FIGS.digits = (el) => {
  const T = TR(); if (!T) return NEEDTR(el, 'Each digit of the made-up number with how sure the model was of it, and five more answers sampled at temperature 0.7.');
  const D = T.generation.digits;
  el.innerHTML = `<div class="chips">${D.map((d) => `<span class="idc"><span class="tchip dg" style="font-size:30px;padding:12px 14px">${esc(d.token)}</span><span class="id">${pct(d.p)}</span></span>`).join('')}</div>
   <div class="ftiny" style="margin-bottom:14px">The digits of its answer, with the probability the model gave each one when it picked it.</div>
   <div class="r1 tr"><div class="tag nt">Five more tries · temperature 0.7 · seeds 0–4</div>${T.generation.samples_t07.map((s) => `<div class="sline"><span class="k">seed ${s.seed}</span>${esc(s.text.trim().replace(/\s+/g, ' ')).slice(0, 150)} <span class="num-b">${s.numbers.map(fmt).join(', ')}</span></div>`).join('')}</div>`;
  return { step(k) { el.querySelector('.r1').classList.toggle('fade-hide', k < 1); } };
};

/* =============================== 8 · training ===============================*/
FIGS.losscurve = (el) => {
  const L = L2(), G = L && L.tiny;
  if (!G || !G.curve) return NEEDFD(el, 'The tiny GPT’s loss curve.', 'experiments/logs/tinygpt.json');
  const cv = G.curve, [W, H] = dims(el);
  const svg = P().svgEl('svg', { viewBox: `0 0 ${W} ${H - 40}`, width: W, height: H - 40 }, el);
  const x0 = 60, y0 = 20, w = W - 90, h = H - 110, ymax = Math.ceil(Math.max(...cv.map((c) => c.val)));
  const X = (st) => x0 + w * st / cv[cv.length - 1].step, Y = (v) => y0 + h * (1 - v / ymax);
  for (let v = 0; v <= ymax; v++) { P().svgEl('rect', { x: x0, y: Y(v), width: w, height: 1, style: 'fill:var(--rule)' }, svg); P().txt(svg, x0 - 10, Y(v) + 5, String(v), 'font:500 13px var(--mono);fill:var(--ink-3)', 'end'); }
  P().txt(svg, x0 + w / 2, H - 50, `training step (batch of ${G.config.batch} × ${G.config.block} characters)`, 'font:500 14px var(--font);fill:var(--ink-3)', 'middle');
  P().svgEl('rect', { x: x0, y: Y(G.uniform_loss), width: w, height: 1.5, style: 'fill:var(--ink-3);opacity:.5' }, svg);
  P().txt(svg, x0 + w - 4, Y(G.uniform_loss) - 8, `an even guess over ${G.distinct_chars} characters: ln ${G.distinct_chars} = ${G.uniform_loss.toFixed(2)}`, 'font:500 13px var(--font);fill:var(--ink-3)', 'end');
  const mk = (key, col) => P().svgEl('polyline', { points: cv.map((c) => `${X(c.step)},${Y(c[key])}`).join(' '), style: `fill:none;stroke:${col};stroke-width:3` }, svg);
  const lines = [mk('train', 'var(--after)'), mk('val', 'var(--before)')];
  lines.forEach((l) => { l.style.strokeDasharray = 3000; l.style.strokeDashoffset = 3000; l.style.transition = 'stroke-dashoffset 1.6s ease'; });
  const last = cv[cv.length - 1], lab = P().svgEl('g', {}, svg);
  P().txt(lab, X(last.step) - 4, Y(last.val) - 34, `validation ${last.val.toFixed(2)}`, 'font:500 15px var(--mono);fill:var(--before)', 'end');
  P().txt(lab, X(last.step) - 4, Y(last.train) - 14, `train ${last.train.toFixed(2)}`, 'font:500 15px var(--mono);fill:var(--after)', 'end');
  P().txt(svg, X(0) + 10, Y(cv[0].val) + 20, `step 0: ${cv[0].val.toFixed(2)}`, 'font:500 15px var(--mono);fill:var(--ink-2)');
  div(el, 'ftiny', `${fmt(G.params)} parameters (${G.config.layers} blocks, ${G.config.heads} heads, ${G.config.d_model}-number vectors), one character per token, ${fmt(G.corpus_chars)} characters of Northbridge documents, ${fmt(G.config.steps)} steps in ${Math.round(G.train_seconds_cpu2)} s on 2 CPUs.`);
  return { step(k) { lines.forEach((l) => { l.style.strokeDashoffset = k >= 1 ? 0 : 3000; }); lab.style.opacity = k >= 1 ? 1 : 0; } };
};

FIGS.tinysamples = (el) => {
  const L = L2(), G = L && L.tiny;
  if (!G || !G.samples) return NEEDFD(el, 'What the tiny GPT writes before and after training.', 'experiments/logs/tinygpt.json');
  const pr = G.stock_prompt, before = G.samples_untrained[pr].slice(pr.length, pr.length + 90), after = G.samples[pr]['0.5'].slice(pr.length).split('\n')[0];
  el.innerHTML = `<div class="ptext"><span class="mono">${esc(pr)}</span><span class="cursor">▍</span></div>
   <div class="grid2"><div class="card bf"><span class="tag bf">step 0 · random numbers</span><div class="mono" style="font-size:17px;word-break:break-all">${esc(before)}…</div></div>
    <div class="card af r1 tr"><span class="tag af">after ${fmt(G.config.steps)} steps · temperature 0.5</span><div class="mono" style="font-size:17px">${esc(after)}</div></div></div>
   <div class="card r2 tr" style="margin-top:12px"><span class="tag nt">ten more stock lines · temperature 0.8 · seeds 0–9</span><div class="chips">${G.stock_figures.map((n) => `<span class="tchip dg">${fmt(n)}</span>`).join('')}</div>
   <div class="ftiny">${G.stock_5400} of ${G.stock_figures.length} said 5,400, though Emma’s e-mail with 5,400 is in its training text.</div></div>`;
  return { step(k) { el.querySelector('.r1').classList.toggle('fade-hide', k < 1); el.querySelector('.r2').classList.toggle('fade-hide', k < 2); } };
};

/* The cut-off: Qwen's probability for each year after "The current year is ", and what each model says. */
FIGS.cutoff = (el) => {
  const L = L2(); if (!L || !L.cutoff) return NEEDFD(el, 'The cut-off.', 'experiments/logs/cutoff.json');
  const C = L.cutoff, Y = C.qwen.year_probs[0].years.filter((y) => y.year >= 2019 && y.year <= 2026);
  const mx = Math.max(...Y.map((y) => y.p_among));
  el.innerHTML = `<div class="ptext"><span class="mono">${esc(C.qwen.year_probs[0].prompt)}</span><span class="cursor">▍</span></div>
   ${Y.map((y) => `<div class="pb${y.p_among === mx ? ' hi' : ''}" style="margin:4px 0"><span class="pt" style="width:70px">${y.year}</span><span class="pr" style="width:420px"><i style="width:${Math.max(1, 420 * y.p_among / mx)}px;background:${y.year === 2026 ? 'var(--before)' : 'var(--after)'}"></i></span><span class="pbv">${pct(y.p_among)}</span></div>`).join('')}
   <div class="ftiny">Qwen2.5-0.5B-Instruct, the probability of each year (renormalised over 2015–2030).</div>
   <div class="grid3 r1 tr" style="margin-top:14px">
     <div class="card" style="font-size:18px"><span class="tag nt">Qwen, asked</span><br>its training data runs to <b>“${esc(C.qwen.asked.cutoff_no_prompt)}”</b></div>
     <div class="card" style="font-size:18px"><span class="tag nt">${esc(L.cold.model)}, asked</span><br>its training data runs to <b>“${esc(C.gemini.reply)}”</b></div>
     <div class="card" style="font-size:18px"><span class="tag nt">our tiny GPT</span><br>its corpus ends on <b>${esc(C.tiny_last_day)}</b></div></div>
   <div class="ftiny r1 tr">Asked today’s date with no prompt, ${esc(L.cold.model)} said “${esc(C.gemini.date_no_prompt)}”. With the app’s prompt, both said “${esc(C.gemini.date_with_app_prompt)}”: the date comes from the prompt.</div>`;
  return { step(k) { el.querySelectorAll('.r1').forEach((x) => x.classList.toggle('fade-hide', k < 1)); } };
};

/* =============================== 9 · the fix ===============================*/
FIGS.facts = (el) => {
  const T = TR(); if (!T) return NEEDTR(el, 'The same question twice: as asked (the model makes a number up) and with one Ledgerline stock line added to the system prompt (measured: what it answers, and how sure it is of each digit).');
  const F = T.facts, ok = F.numbers.includes(F.truth);
  el.innerHTML = `<div class="card bf"><span class="tag bf">as asked · no facts in the context</span><div style="font-size:21px">“${esc(T.generation.text.trim())}”</div></div>
   <div class="card r1 tr" style="margin-top:12px;background:var(--g3)"><span class="tag nt">one line added to the system prompt</span><div class="mono" style="font-size:16px">${esc(F.line)}</div></div>
   <div class="card af r2 tr" style="margin-top:12px"><span class="tag af">with that line · same model, greedy</span><div style="font-size:21px">“${esc(F.text.trim())}”</div>
   <div class="chips" style="margin-top:10px">${F.digits.map((d) => `<span class="idc"><span class="tchip ${ok ? 'c1' : 'dg'}">${esc(d.token)}</span><span class="id">${pct(d.p)}</span></span>`).join('')}</div>
   ${F.attention_to_fact && F.attention_to_fact.best_head ? `<div class="ftiny">At the first digit, block ${F.attention_to_fact.best_head.layer}, head ${F.attention_to_fact.best_head.head} puts ${pct(F.attention_to_fact.best_head.weight)} of its attention on the “5,400” in the prompt.</div>` : ''}</div>
   <div class="card r3 tr" style="margin-top:12px;font-size:19px"><span class="tag nt">same line · five more tries at temperature 0.7</span><div class="chips">${F.samples_t07.map((x) => `<span class="tchip ${x.numbers.includes(F.truth) ? 'c1' : 'dg'}">${x.numbers.length ? x.numbers.map(fmt).join(', ') : 'no number'}</span>`).join('')}</div>
   <div class="ftiny">${F.samples_t07.filter((x) => x.numbers.includes(F.truth)).length} of ${F.samples_t07.length} said ${fmt(F.truth)}. The fact was in the context; the dial still picked other digits.</div></div>`;
  return { step(k) { el.querySelector('.r1').classList.toggle('fade-hide', k < 1); el.querySelector('.r2').classList.toggle('fade-hide', k < 2); el.querySelector('.r3').classList.toggle('fade-hide', k < 3); } };
};

/* Text spans filled from the trace: <span data-tr="generation.numbers.0" data-f="n"></span>. */
FIGS._fill = () => {
  document.querySelectorAll('[data-l2]').forEach((s) => {
    let v = L2(); for (const k of s.dataset.l2.split('.')) v = v == null ? v : v[k];
    if (v == null) { s.innerHTML = '<span class="todo-in">TODO(v4 data)</span>'; return; }
    s.textContent = s.dataset.f === 'n' ? fmt(v) : s.dataset.f === 'pct' ? pct(v) : String(v);
  });
  const T = TR();
  document.querySelectorAll('[data-tr]').forEach((s) => {
    let v = T; for (const k of s.dataset.tr.split('.')) v = v == null ? v : v[k];
    if (v == null) { s.innerHTML = '<span class="todo-in">TODO(brain3d)</span>'; return; }
    const f = s.dataset.f;
    s.textContent = f === 'n' ? fmt(v) : f === 'pct' ? pct(v) : f === 'trim' ? String(v).trim() : String(v);
  });
};
})();
