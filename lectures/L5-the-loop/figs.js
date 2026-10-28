/* Live figures for Lecture 5 · The Loop. Loaded BEFORE plates.js; helpers come from window.Plates inside each figure.
   Every number comes from figdata.js (window.FD), which experiments/export_figdata.py writes from
   experiments/logs/tasks_<agent>_or[_lite].json (run B, 2026-10-28) and logs/v2_L4_forty_summary.json. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const FD = () => window.FD;
const esc = (s) => String(s ?? '').replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const fmt = (n) => Number(n).toLocaleString('en-IN');
const md = (s) => String(s ?? '').replace(/\*\*|`|#{2,}\s*/g, '').replace(/\s*\*\s+/g, ' · ').replace(/\s+/g, ' ').trim();
const first = (s) => { const m = String(s).match(/^.*?[.?!](?=\s|$)/); return m ? m[0] : String(s); };
const AG = { hands: 'One round (L4)', react: 'Text ReAct', bare: 'Bare loop', prompt: 'Loop + prompt', harness: 'Full harness', graph: 'Control graph' };
const css = `
.l5 *{box-sizing:border-box}
.l5 .pane{background:#fff;border-radius:20px;box-shadow:var(--shadow);padding:14px 16px;overflow:hidden}
.l5 .lbl{font:600 13px/1.2 var(--font);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin-bottom:6px}
.l5 .mono{font:400 15px/1.45 var(--mono);white-space:pre-wrap;word-break:break-word;color:var(--ink-2)}
.l5 .bub{border-radius:18px;padding:9px 13px;font-size:17px;line-height:1.38;max-width:92%;margin-bottom:8px;transition:opacity .35s}
.l5 .bub.u{background:var(--card);margin-left:auto;border-bottom-right-radius:6px}
.l5 .bub.a{background:var(--after-soft);border-bottom-left-radius:6px}
.l5 .bub.n{background:var(--before-soft);margin-left:auto;border-bottom-right-radius:6px;color:var(--before)}
.l5 .bub.e{background:var(--gold-soft);margin-left:auto;color:var(--gold);font-size:15px}
.l5 .who{font:500 13px/1 var(--font);color:var(--ink-3);margin:2px 0 4px}
.l5 .big{font:500 64px/1 var(--font);letter-spacing:-.03em}
.l5 .hl-t{background:rgba(60,144,255,.16);border-radius:4px}
.l5 .hl-a{background:rgba(196,81,31,.16);border-radius:4px}
.l5 .hl-i{background:rgba(19,138,96,.18);border-radius:4px}
.l5 .hl-o{background:rgba(18,19,23,.07);border-radius:4px}
.l5 table{border-collapse:collapse;width:100%}
.l5 td,.l5 th{padding:5px 7px;font-size:15px;border-bottom:1px solid var(--rule);text-align:left}
.l5 th{font:500 13px/1.2 var(--font);color:var(--ink-3)}
.l5 .dot{display:inline-block;width:22px;height:22px;border-radius:7px;vertical-align:middle}
.l5 .ok{background:#cfe3ff}.l5 .no{background:#ffd9c6}.l5 .neb{background:#c4511f}
.l5 .chip2{display:inline-block;font:500 13px/1 var(--font);padding:6px 9px;border-radius:999px;background:var(--card);color:var(--ink-2);margin:0 4px 4px 0}
.l5 .node{display:inline-flex;align-items:center;justify-content:center;padding:9px 12px;border-radius:14px;background:var(--card);font:500 16px/1.1 var(--font);color:var(--ink-3);transition:all .35s;margin:0 3px 6px 0}
.l5 .node.on{background:var(--g1);color:var(--after);box-shadow:inset 0 0 0 1.5px rgba(11,87,208,.35)}
.l5 .node.det{background:var(--g4);color:var(--before)}
`;
if (!document.getElementById('l5css')) { const s = document.createElement('style'); s.id = 'l5css'; s.textContent = css; document.head.appendChild(s); }
const box = (el, html) => { el.classList.add('l5'); el.innerHTML = html; return el; };
const ctl = (labels, on, cb) => { const d = document.createElement('div'); d.className = 'ctl'; labels.forEach(([k, t]) => { const b = document.createElement('button'); b.textContent = t; b.dataset.k = k; if (k === on) b.classList.add('on'); b.onclick = (e) => { e.stopPropagation(); d.querySelectorAll('button').forEach((x) => x.classList.toggle('on', x === b)); cb(k); }; d.appendChild(b); }); return d; };
const slider = (n, cb, label = 'Step') => { const d = document.createElement('div'); d.className = 'ctl'; d.innerHTML = `<span>${label}</span><input type="range" min="0" max="${n - 1}" value="0"><output></output>`; const i = d.querySelector('input'), o = d.querySelector('output'); const f = () => { o.textContent = `${+i.value + 1} of ${n}`; cb(+i.value); }; i.oninput = f; i.addEventListener('click', (e) => e.stopPropagation()); setTimeout(f, 0); return { el: d, set: (v) => { i.value = v; f(); } }; };

/* ---------- Fig: cold open, the same job driven by Kavita (one round per message) vs the harness ---------- */
FIGS.coldopen = (el) => {
  const F = FD();
  box(el, `<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;height:100%">
    <div class="pane" id="co-h"><div class="lbl" style="color:var(--before)">Lecture 4 · one tool round per message</div><div class="th"></div></div>
    <div class="pane" id="co-a"><div class="lbl" style="color:var(--after)">Lecture 5 · the loop</div><div class="th"></div></div></div>`);
  const fill = (id, conv) => {
    const th = el.querySelector(`#${id} .th`);
    const kav = conv.filter((t) => t.who === 'KJOSHI' && t.day === 1);
    let n = 0;
    th.innerHTML = kav.map((t) => {
      const cls = t.kind === 'nudge' ? 'n' : t.kind === 'event' ? 'e' : 'u';
      if (t.kind !== 'event') n++;
      const shortUser = t.user.length > 80 ? first(t.user) : t.user;
      const txt = md(t.agent); const a = txt ? esc(txt.slice(0, 74)) + (txt.length > 74 ? '…' : '') : '<i style="color:var(--before)">(an empty reply)</i>';
      return `<div class="row" style="opacity:0"><div class="bub ${cls}" style="font-size:15px;padding:6px 11px;margin-bottom:5px">${t.kind === 'event' ? 'Bahi: Rohit approved PR/2026/04417' : esc(shortUser)}${cls !== 'e' ? `<span style="float:right;font:600 13px var(--font);margin-left:8px">#${n}</span>` : ''}</div><div class="bub a" style="font-size:14px;padding:6px 11px;margin-bottom:5px">${a}</div></div>`;
    }).join('');
    return th.querySelectorAll('.row');
  };
  const rh = fill('co-h', F.cold.hands), ra = fill('co-a', F.cold.harness);
  return { step(k) { const show = (rows, upto) => rows.forEach((r, i) => (r.style.opacity = i < upto ? 1 : 0)); show(rh, k >= 1 ? 99 : 0); show(ra, k >= 2 ? 99 : 0); } };
};

/* ---------- Fig: the job map, P2P across days and people ---------- */
FIGS.jobmap = (el) => {
  const P = window.Plates; const W = 1300, H = 330;
  const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: '100%', height: '100%' }, el);
  const steps = [['Check stock', 'Kavita', 'Day 1', '66,000 free|11 days'], ['Raise request', 'Kavita', 'Day 1', 'PR/2026/04417|₹2,69,040'], ['Wait for Rohit', 'Rohit', 'Day 1 → ?', 'above|₹2,50,000'], ['Create order', 'Kavita', 'after approval', 'PO/2026/01182|₹2,80,840'], ['Release', 'Kavita', 'same minute', 'to Deccan|Polymers'], ['Receive 12,000', 'Neha', 'Day 5', 'GRN/2026/30001|'], ['Receive 8,000', 'Neha', 'Day 8', 'GRN/2026/30002|order closed']];
  const g = steps.map((s, i) => {
    const x = 20 + i * 182, gg = P.svgEl('g', { style: 'opacity:0;transition:opacity .4s' }, svg);
    const wait = i === 2;
    P.svgEl('rect', { x, y: 90, width: 166, height: 92, rx: 18, style: `fill:${wait ? '#fff1e8' : '#e6f1ff'};stroke:${wait ? '#c4511f' : '#0b57d0'};stroke-width:1.5;${wait ? 'stroke-dasharray:6 5' : ''}` }, gg);
    P.txt(gg, x + 83, 126, s[0], 'font:500 19px var(--font);fill:#121317', 'middle');
    P.txt(gg, x + 83, 154, s[1], `font:500 16px var(--font);fill:${wait ? '#c4511f' : '#0b57d0'}`, 'middle');
    P.txt(gg, x + 83, 60, s[2], 'font:500 15px var(--font);fill:#6b6e76', 'middle');
    s[3].split('|').forEach((l, j) => P.txt(gg, x + 83, 212 + j * 20, l, 'font:400 15px var(--mono);fill:#45474d', 'middle'));
    if (i) P.svgEl('path', { d: `M${x - 14} 136 l12 0`, style: 'stroke:#6b6e76;stroke-width:2' }, gg);
    return gg;
  });
  const brace = P.svgEl('g', { style: 'opacity:0;transition:opacity .4s' }, svg);
  P.svgEl('path', { d: `M20 268 L1294 268`, style: 'stroke:#138a60;stroke-width:2' }, brace);
  P.txt(brace, 657, 300, 'one job · three people · seven steps · day 1 to day 8', 'font:500 18px var(--font);fill:#138a60', 'middle');
  return { step(k) { g.forEach((x, i) => (x.style.opacity = k >= 1 && i < (k >= 2 ? 7 : 3) ? 1 : 0)); brace.style.opacity = k >= 3 ? 1 : 0; } };
};

/* ---------- Fig: the loop, stepping through the harness's real first message ---------- */
FIGS.loopanim = (el) => {
  const F = FD(); const st = F.native.steps.filter((s) => s.turn === 1);
  box(el, `<div style="display:grid;grid-template-columns:420px 1fr;gap:18px;height:100%">
   <div class="pane" style="display:flex;flex-direction:column;justify-content:center;gap:10px">
     ${['model', 'tools', 'observation', 'reply'].map((k) => `<div class="node" data-n="${k}" style="font-size:22px;padding:16px">${{ model: 'Model decides', tools: 'Run the tool', observation: 'Result back into history', reply: 'Answer in words: stop' }[k]}</div>`).join('')}
   </div>
   <div class="pane"><div class="lbl">What happened at this step · Kavita's first message, our run</div><div class="mono" id="la-t" style="font-size:16px"></div></div></div>`);
  const t = el.querySelector('#la-t'); const nodes = el.querySelectorAll('.node');
  const s = slider(st.length, (i) => {
    const x = st[i]; const lit = x.k === 'assistant' ? (x.calls && x.calls.length ? 'model' : 'reply') : 'observation';
    nodes.forEach((n) => n.classList.toggle('on', n.dataset.n === lit || (x.k === 'tool' && n.dataset.n === 'tools')));
    t.innerHTML = x.k === 'assistant' ? (x.calls && x.calls.length ? `<b>assistant asks for ${x.calls.length} tool${x.calls.length > 1 ? 's' : ''}</b>\n` + x.calls.map((c) => `${c.name}(${esc(JSON.stringify(c.args))})`).join('\n') : `<b>assistant answers, no tool calls: the loop stops</b>\n${esc(md(x.text))}`) : x.k === 'tool' ? `<b>tool message: ${x.name}</b>\n${esc(x.result)}` : `<b>harness: ${x.part}</b> ${esc(x.note)}`;
  });
  el.querySelector('.pane:last-child').appendChild(s.el);
  return { step() {} };
};

/* ---------- Fig: parse one ReAct step, piece by piece ---------- */
FIGS.reactparse = (el) => {
  const F = FD(); const x = F.react.steps[2];
  const raw = x.raw; const ia = raw.indexOf('Action:'), ii = raw.indexOf('Action Input:');
  const th = raw.slice(0, ia), ac = raw.slice(ia, ii), inp = raw.slice(ii);
  box(el, `<div class="pane" style="height:56%"><div class="lbl">The model's turn, exactly as it came back (Kavita's order, step 3)</div><div class="mono" style="font-size:17px"><span id="rp-t">${esc(th)}</span><span id="rp-a">${esc(ac)}</span><span id="rp-i">${esc(inp)}</span></div></div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:14px">
      <div class="pane rp" style="opacity:0"><div class="lbl" style="color:var(--after)">thought</div><div class="mono">kept in the history; nothing runs</div></div>
      <div class="pane rp" style="opacity:0"><div class="lbl" style="color:var(--before)">action</div><div class="mono">${esc(x.action)}</div></div>
      <div class="pane rp" style="opacity:0"><div class="lbl" style="color:var(--gold)">action input, parsed JSON</div><div class="mono">${esc(JSON.stringify(x.input, null, 1))}</div></div></div>`);
  const cards = el.querySelectorAll('.rp');
  return { step(k) { el.querySelector('#rp-t').className = k >= 1 ? 'hl-t' : ''; el.querySelector('#rp-a').className = k >= 2 ? 'hl-a' : ''; el.querySelector('#rp-i').className = k >= 3 ? 'hl-i' : ''; cards.forEach((c, i) => (c.style.opacity = k >= i + 1 ? 1 : 0)); } };
};

/* ---------- Fig: the whole ReAct transcript, scrubbed ---------- */
FIGS.reactscrub = (el) => {
  const F = FD(); const S = F.react.steps; const turns = F.react.turns;
  box(el, `<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;height:calc(100% - 60px)">
    <div class="pane"><div class="lbl" id="rs-h"></div><div class="mono" id="rs-raw" style="font-size:15.5px"></div></div>
    <div class="pane"><div class="lbl">What our code wrote back</div><div class="mono" id="rs-obs" style="font-size:14.5px"></div></div></div>`);
  const s = slider(S.length, (i) => {
    const x = S[i]; const who = turns[x.turn - 1];
    el.querySelector('#rs-h').innerHTML = `Message ${x.turn} from ${x.turn === 3 ? 'Bahi (Rohit approved)' : 'Kavita'} · model step · ${fmt(x.tin)} tokens in`;
    let raw = esc(x.raw).replace(/(Thought:)/g, '<b class="hl-t">$1</b>').replace(/(Action Input:)/g, '<b class="hl-i">$1</b>').replace(/(Action:)/g, '<b class="hl-a">$1</b>').replace(/(Final Answer:)/g, '<b style="color:var(--gold)">$1</b>');
    el.querySelector('#rs-raw').innerHTML = (who && x.turn !== (S[i - 1] || {}).turn ? `<span style="color:var(--ink-3)">${esc(who.user)}</span>\n\n` : '') + raw;
    el.querySelector('#rs-obs').innerHTML = x.err ? `<b style="color:var(--before)">The parser could not read it.</b>\nObservation: {"ok": false, "error": "${esc(x.err)}", "next_step": "Continue in the format …"}` : x.obs ? `Observation: ${esc(x.obs)}` : `<b style="color:var(--gold)">Final Answer: shown to ${x.turn === 3 ? 'Kavita' : 'Kavita'}. The loop stops.</b>`;
  });
  s.el.style.marginTop = '12px'; el.appendChild(s.el);
  return { step() {} };
};

/* ---------- Fig: text ReAct and native tool calling, side by side, same task ---------- */
FIGS.sidebyside = (el) => {
  const F = FD(); const R = F.react.steps.filter((x) => x.turn <= 2); const N = F.native.steps.filter((x) => x.turn <= 2);
  box(el, `<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;height:calc(100% - 60px)">
    <div class="pane"><div class="lbl" style="color:var(--before)">Text ReAct · our parser</div><div id="sb-r"></div></div>
    <div class="pane"><div class="lbl" style="color:var(--after)">Native tool calling · the API</div><div id="sb-n"></div></div></div>`);
  const rr = R.map((x) => `<div class="sbr mono" style="font-size:14px;padding:5px 8px;border-radius:10px;margin-bottom:4px">${x.err ? `<b style="color:var(--before)">wrote "Action: ${esc(x.action)}" with no input: sent back as a format error</b>` : x.action ? `<b class="hl-a">Action:</b> ${esc(x.action)} <b class="hl-i">Input:</b> ${esc(JSON.stringify(x.input)).slice(0, 60)}<br><span style="color:var(--ink-3)">Observation: ${esc((x.obs || '').slice(0, 56))}…</span>` : `<b style="color:var(--gold)">Final Answer:</b> ${esc(md(x.final).slice(0, 70))}…`}</div>`).join('');
  const nn = N.map((x) => `<div class="sbn mono" style="font-size:14px;padding:6px 8px;border-radius:10px;margin-bottom:5px">${x.k === 'assistant' ? (x.calls && x.calls.length ? `<b class="hl-a">assistant.tool_calls:</b> ${x.calls.map((c) => esc(c.name)).join(', ')}` : `<b style="color:var(--gold)">assistant, no tool_calls:</b> ${esc(md(x.text).slice(0, 70))}…`) : x.k === 'tool' ? `<b class="hl-o">role: tool</b> ${esc(x.name)} → ${esc((x.result || '').slice(0, 48))}…` : `<b>harness:</b> ${esc(x.part)}`}</div>`).join('');
  el.querySelector('#sb-r').innerHTML = rr; el.querySelector('#sb-n').innerHTML = nn;
  const rs = el.querySelectorAll('.sbr'), ns = el.querySelectorAll('.sbn');
  return { step(k) { const fr = k >= 1 ? 1 : 0; rs.forEach((r) => (r.style.opacity = fr ? 1 : 0)); ns.forEach((r) => (r.style.opacity = k >= 2 ? 1 : 0)); } };
};

/* ---------- Fig: the message history, growing ---------- */
FIGS.history = (el) => {
  const F = FD(); const S = F.native.steps.filter((x) => x.k !== 'harness');
  const msgs = [{ r: 'system', t: 'You are Ask Rasoi … (rules, Kavita\'s limit ₹2,50,000, default PRD-05)' }];
  let lastTurn = 0; const seq = [];
  const users = F.native.turns;
  S.forEach((x) => {
    if (x.turn !== lastTurn) { const u = users[x.turn - 1]; msgs.push({ r: 'user', t: u ? u.user : '' }); lastTurn = x.turn; }
    if (x.k === 'assistant') { seq.push(msgs.length); msgs.push({ r: 'assistant', t: x.calls && x.calls.length ? 'tool_calls: ' + x.calls.map((c) => c.name).join(', ') : md(x.text) }); }
    else msgs.push({ r: 'tool', t: x.name + ' → ' + (x.result || '').slice(0, 60) });
  });
  box(el, `<div class="pane" style="height:calc(100% - 60px);overflow:hidden"><div class="lbl" id="hi-h"></div><div id="hi-l"></div></div>`);
  const col = { system: 'var(--gold)', user: 'var(--ink)', assistant: 'var(--after)', tool: 'var(--before)' };
  const s = slider(seq.length, (i) => {
    const n = seq[i]; const show = msgs.slice(0, n); const tail = show.slice(-16);
    el.querySelector('#hi-h').textContent = `Model call ${i + 1}: ${n} messages go to the model (the whole history, every time)`;
    el.querySelector('#hi-l').innerHTML = (show.length > tail.length ? `<div class="mono" style="color:var(--ink-3)">… ${show.length - tail.length} earlier messages …</div>` : '') + tail.map((m) => `<div class="mono" style="font-size:14px;margin-bottom:3px"><b style="color:${col[m.r]}">${m.r.padEnd(9)}</b> ${esc((m.t || '').slice(0, 110))}</div>`).join('');
  }, 'Model call');
  el.appendChild(s.el);
  return { step() {} };
};

/* ---------- Fig: max steps: how many messages would a cap cut short? ---------- */
FIGS.maxsteps = (el) => {
  const F = FD(); const P = window.Plates;
  box(el, `<div class="pane" style="height:calc(100% - 60px)"><div class="lbl">Model calls each message needed · full harness and bare loop · 12 tasks, flash</div><div id="ms-c"></div><div id="ms-t" style="font-size:22px;margin-top:6px"></div></div>`);
  const W = 860, H = 316; const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: '100%', height: 316 }, el.querySelector('#ms-c'));
  const max = 12; const bw = W / (max + 1);
  const hist = (arr) => { const h = Array(max + 1).fill(0); arr.forEach((v) => (h[Math.min(v, max)] += 1)); return h; };
  const hh = hist(F.spm.harness), hb = hist(F.spm.bare); const top = Math.max(...hh, ...hb);
  const bars = [];
  for (let v = 1; v <= max; v++) {
    const x = (v - 0.5) * bw;
    const a = P.svgEl('rect', { x: x, y: 250 - hh[v] / top * 220, width: bw * 0.42, height: hh[v] / top * 220, style: 'fill:#2a78d6' }, svg);
    const b = P.svgEl('rect', { x: x + bw * 0.44, y: 250 - hb[v] / top * 220, width: bw * 0.42, height: hb[v] / top * 220, style: 'fill:#eb6834' }, svg);
    P.txt(svg, x + bw * 0.43, 276, String(v), 'font:500 15px var(--font);fill:#6b6e76', 'middle');
    bars.push([v, a, b]);
  }
  P.txt(svg, 4, 304, 'model calls in one message →', 'font:500 14px var(--font);fill:#6b6e76');
  P.txt(svg, W - 4, 18, 'blue: full harness   orange: bare loop', 'font:500 15px var(--font);fill:#45474d', 'end');
  const d = document.createElement('div'); d.className = 'ctl'; d.innerHTML = '<span>Max steps per message</span><input type="range" min="1" max="12" value="4"><output></output>';
  const i = d.querySelector('input'), o = d.querySelector('output');
  const f = () => { const c = +i.value; o.textContent = c; bars.forEach(([v, a, b]) => { a.style.opacity = b.style.opacity = v > c ? 0.25 : 1; }); const cut = (arr) => arr.filter((v) => v > c).length; el.querySelector('#ms-t').innerHTML = `A cap of <b>${c}</b> would cut short <b class="a">${cut(F.spm.harness)} of ${F.spm.harness.length}</b> harness messages and <b class="b">${cut(F.spm.bare)} of ${F.spm.bare.length}</b> bare-loop messages. Longest: ${Math.max(...F.spm.harness)} and ${Math.max(...F.spm.bare)}.`; };
  i.oninput = f; i.addEventListener('click', (e) => e.stopPropagation()); el.appendChild(d); f();
  return { step() {} };
};

/* ---------- Fig: the measured results, bars, with model and metric toggles ---------- */
FIGS.results = (el) => {
  const F = FD(); const P = window.Plates; let model = 'flash', metric = 'passed';
  box(el, `<div class="pane" style="height:calc(100% - 118px)"><div id="re-c"></div></div>`);
  const order = ['hands', 'react', 'bare', 'prompt', 'harness', 'graph'];
  const M = { passed: ['Tasks passed (of 12)', (r) => r.passed, (v) => v], ne: ['Tasks with a never-event', (r) => r.ne_tasks, (v) => v], tokens: ['Tokens, all 12 tasks', (r) => r.tokens, fmt], calls: ['Model calls, all 12 tasks', (r) => r.calls, fmt], msgs: ['Messages people had to send', (r) => r.msgs, (v) => v], inr: ['₹, all 12 tasks', (r) => r.inr, (v) => '₹' + v] };
  const draw = () => {
    const c = el.querySelector('#re-c'); c.innerHTML = '';
    const W = 860, H = 380; const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: '100%', height: 400 }, c);
    const [title, get, show] = M[metric]; const vals = order.map((a) => get(F.res[`${a}_${model}`]));
    const top = metric === 'passed' ? 12 : Math.max(...vals, 1);
    P.txt(svg, 0, 22, `${title} · ${model === 'flash' ? 'gemini-3.8-flash' : 'gemini-3.5-flash-lite'}`, 'font:500 18px var(--font);fill:#45474d');
    order.forEach((a, i) => {
      const y = 48 + i * 54, w = vals[i] / top * 560;
      P.txt(svg, 180, y + 27, AG[a], 'font:500 17px var(--font);fill:#121317', 'end');
      P.svgEl('rect', { x: 196, y: y + 6, width: Math.max(w, 2), height: 32, rx: 9, style: `fill:${a === 'graph' ? '#138a60' : a === 'hands' ? '#eb6834' : '#2a78d6'};opacity:${a === 'harness' || a === 'graph' ? 1 : .7}` }, svg);
      P.txt(svg, 206 + w, y + 28, String(show(vals[i])), 'font:600 16px var(--font);fill:#121317');
    });
  };
  el.appendChild(ctl([['flash', 'gemini-3.8-flash'], ['lite', 'gemini-3.5-flash-lite']], 'flash', (k) => { model = k; draw(); }));
  const m2 = ctl([['passed', 'Passed'], ['ne', 'Never-events'], ['tokens', 'Tokens'], ['calls', 'Model calls'], ['msgs', 'Messages'], ['inr', '₹']], 'passed', (k) => { metric = k; draw(); });
  el.appendChild(m2); draw();
  return { step() {} };
};

/* ---------- Fig: the per-task grid ---------- */
FIGS.grid = (el) => {
  const F = FD(); let model = 'flash';
  box(el, `<div class="pane" style="height:calc(100% - 56px);padding:10px 14px"><table id="gr-t"></table><div class="mono" id="gr-n" style="font-size:14px;margin-top:8px;min-height:40px"></div></div>`);
  const order = ['hands', 'react', 'bare', 'prompt', 'harness', 'graph'];
  const draw = () => {
    const t = el.querySelector('#gr-t');
    t.innerHTML = `<tr><th>Task</th>${order.map((a) => `<th style="text-align:center">${AG[a]}</th>`).join('')}</tr>` + F.tasks.map((tk, i) => `<tr><td style="font-size:14.5px">${tk.id} · ${esc(tk.name)}</td>${order.map((a) => { const p = F.res[`${a}_${model}`].per[i]; return `<td style="text-align:center"><span class="dot ${p.ne ? 'neb' : p.ok ? 'ok' : 'no'}" data-a="${a}" data-i="${i}" title=""></span></td>`; }).join('')}</tr>`).join('');
    t.querySelectorAll('.dot').forEach((d) => { d.style.cursor = 'pointer'; d.onclick = (e) => { e.stopPropagation(); const p = F.res[`${d.dataset.a}_${model}`].per[+d.dataset.i]; el.querySelector('#gr-n').textContent = `${AG[d.dataset.a]} · ${p.id}: ${p.ok ? 'pass' : 'fail'}${p.ne ? ' · NEVER-EVENT' : ''} · ${p.calls} model calls · ${fmt(p.tokens)} tokens · ${p.msgs} messages from people${p.f.length ? ' · ' + p.f.join(', ') : ''} · ${p.note}`; }; });
  };
  el.appendChild(ctl([['flash', 'gemini-3.8-flash'], ['lite', 'gemini-3.5-flash-lite']], 'flash', (k) => { model = k; draw(); }));
  draw();
  return { step() {} };
};

/* ---------- Fig: the never-event, harness vs graph on Shakti Seals ---------- */
FIGS.ne3 = (el) => {
  const F = FD();
  const h = F.ne3.harness.slice(0, 4), g = F.ne3.graph.slice(0, 3);
  const row = (t, pick) => `<div class="row" style="opacity:0"><div class="bub ${t.kind === 'event' ? 'e' : 'u'}" style="font-size:15px">${t.kind === 'event' ? 'Bahi: Rohit approved PR/2026/04417' : esc(t.user.length > 80 ? first(t.user) : t.user)}</div><div class="bub a" style="font-size:14.5px">${esc(pick(t.agent))}</div></div>`;
  const cut = (n) => (s) => md(s).slice(0, n) + (md(s).length > n ? '…' : '');
  box(el, `<div style="display:grid;grid-template-columns:1.25fr 1fr;gap:16px;height:100%">
    <div class="pane" id="n3-h"><div class="lbl" style="color:var(--before)">Full harness, free loop · T06, flash</div>${h.map((t) => row(t, cut(170))).join('')}</div>
    <div class="pane" id="n3-g"><div class="lbl" style="color:var(--gold)">Control graph · same task</div>${g.map((t) => row(t, cut(150))).join('')}</div></div>`);
  const hr = el.querySelectorAll('#n3-h .row'), gr = el.querySelectorAll('#n3-g .row');
  return { step(k) { hr.forEach((r, i) => (r.style.opacity = k >= 1 + Math.floor(i / 2) ? 1 : 0)); gr.forEach((r) => (r.style.opacity = k >= 3 ? 1 : 0)); } };
};

/* ---------- Fig: the graph's real path on the whole job ---------- */
FIGS.graphpath = (el) => {
  const F = FD(); const path = F.graph.path; const turns = F.graph.turns.filter((t) => t.who === 'KJOSHI');
  const names = { understand: 'Understand', look_up: 'Look up', preview: 'Preview', confirm: 'Confirm', commit: 'Raise request', wait_approval: 'Wait for approval', create_order: 'Create order', release: 'Release', status: 'Status' };
  box(el, `<div class="pane" style="margin-bottom:14px"><div class="lbl">The path the graph took, read from its checkpoints · T01, flash</div><div id="gp-n"></div></div>
    <div class="pane" style="height:330px"><div class="lbl" id="gp-h"></div><div id="gp-r"></div></div>`);
  el.querySelector('#gp-n').innerHTML = path.map((p, i) => `<span class="node" data-i="${i}">${names[p] || p}</span>`).join('');
  const nodes = el.querySelectorAll('#gp-n .node');
  const runs = [[0, 3, 0], [4, 5, 1], [6, 7, 2], [8, 9, 3]];
  const s = slider(runs.length, (i) => {
    const [a, b, ti] = runs[i]; nodes.forEach((n, j) => { n.classList.toggle('on', j >= a && j <= b); n.style.opacity = j <= b ? 1 : .35; });
    const t = turns[ti];
    el.querySelector('#gp-h').textContent = `Message ${i + 1}: ${t.kind === 'event' ? 'Bahi notification (Rohit approved)' : 'Kavita'} · day ${t.day}`;
    el.querySelector('#gp-r').innerHTML = `<div class="bub u" style="font-size:15px">${esc(t.user.slice(0, 110))}</div><div class="bub a" style="font-size:16px">${esc(md(t.agent))}</div>`;
  }, 'Message');
  el.appendChild(s.el);
  return { step() {} };
};

/* ---------- Fig: v2's measured graph vs loop, 40 cases ---------- */
FIGS.v2bars = (el) => {
  const F = FD(); const P = window.Plates; const v = F.v2;
  const W = 820, H = 380; const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: '100%', height: '100%' }, el);
  const rows = [['Loop · flash', v.forty_loop], ['Graph · flash', v.forty_graph], ['Loop · lite', v.forty_loop_lite], ['Graph · lite', v.forty_graph_lite]];
  const gs = rows.map(([k, r], i) => {
    const g = P.svgEl('g', { style: 'opacity:0;transition:opacity .4s' }, svg); const y = 30 + i * 84;
    P.txt(g, 150, y + 24, k, 'font:500 18px var(--font);fill:#121317', 'end');
    P.svgEl('rect', { x: 164, y: y + 4, width: r.passed / 40 * 260, height: 28, rx: 8, style: 'fill:#2a78d6' }, g);
    P.txt(g, 172 + r.passed / 40 * 260, y + 24, `${r.passed}/40`, 'font:600 16px var(--font);fill:#121317');
    const tk = r.tokens_in + r.tokens_out; P.svgEl('rect', { x: 490, y: y + 4, width: tk / 1200000 * 170, height: 28, rx: 8, style: `fill:${k.startsWith('Graph') ? '#138a60' : '#eb6834'}` }, g);
    P.txt(g, 498 + tk / 1200000 * 170, y + 24, `${fmt(Math.round(tk / 1000))}k · ₹${r.cost_inr.toFixed(2)}`, 'font:600 15px var(--font);fill:#121317');
    return g;
  });
  P.txt(svg, 164, 18, 'cases passed', 'font:500 14px var(--font);fill:#6b6e76'); P.txt(svg, 490, 18, 'tokens and ₹, all 40 cases', 'font:500 14px var(--font);fill:#6b6e76');
  return { step(k) { gs.forEach((g, i) => (g.style.opacity = k >= (i < 2 ? 1 : 2) ? 1 : 0)); } };
};

/* ---------- Fig: the pause: Rohit has not answered yet ---------- */
FIGS.pausefig = (el) => {
  const F = FD(); const t = F.pause.turns;
  box(el, `<div class="pane" style="height:100%">${t.map((x, i) => `<div class="row" style="opacity:0"><div class="who">Day ${x.day} · Kavita</div><div class="bub u" style="font-size:16px">${esc(x.user)}</div>${i === 2 ? `<div class="mono" style="font-size:14px;color:var(--gold);margin:0 0 6px">[harness] Still paused: Bahi shows PR/2026/04417 as WAITING FOR APPROVAL, waiting for RMEHTA. Nothing can be ordered yet; do not raise it again.</div>` : ''}<div class="bub a" style="font-size:15.5px">${esc(md(x.agent).slice(0, 250))}${md(x.agent).length > 250 ? '…' : ''}</div></div>`).join('')}</div>`);
  const rows = el.querySelectorAll('.row');
  return { step(k) { rows.forEach((r, i) => (r.style.opacity = i < k ? 1 : 0)); } };
};

/* ---------- Fig: stage=hands vs stage=agent, people's messages ---------- */
FIGS.stages = (el) => {
  const F = FD(); const P = window.Plates; let model = 'flash';
  box(el, `<div class="pane" style="height:calc(100% - 56px)"><div id="st-c"></div></div>`);
  const draw = () => {
    const c = el.querySelector('#st-c'); c.innerHTML = ''; const W = 820, H = 300;
    const svg = P.svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: '100%', height: 300 }, c);
    const h = F.res[`hands_${model}`], a = F.res[`harness_${model}`];
    const rows = [['Messages people sent', h.msgs, a.msgs], ['of which "do the next step"', h.nudges, a.nudges], ['Tasks passed (of 12)', h.passed, a.passed]];
    const top = Math.max(h.msgs, a.msgs);
    rows.forEach(([k, x, y], i) => {
      const yy = 20 + i * 92; P.txt(svg, 0, yy + 16, k, 'font:500 17px var(--font);fill:#45474d');
      P.svgEl('rect', { x: 0, y: yy + 26, width: x / top * 480, height: 24, rx: 8, style: 'fill:#eb6834' }, svg); P.txt(svg, x / top * 480 + 8, yy + 44, `${x} · one round (stage=hands)`, 'font:600 15px var(--font);fill:#121317');
      P.svgEl('rect', { x: 0, y: yy + 54, width: Math.max(y / top * 480, 2), height: 24, rx: 8, style: 'fill:#2a78d6' }, svg); P.txt(svg, Math.max(y / top * 480, 2) + 8, yy + 72, `${y} · the loop (stage=agent)`, 'font:600 15px var(--font);fill:#121317');
    });
  };
  el.appendChild(ctl([['flash', 'gemini-3.8-flash'], ['lite', 'gemini-3.5-flash-lite']], 'flash', (k) => { model = k; draw(); })); draw();
  return { step() {} };
};

/* ---------- Fig: the architecture with the harness lit (master figure + overlay) ---------- */
FIGS.archlit = (el) => {
  box(el, `<div style="height:100%;text-align:center"><div style="position:relative;height:100%;display:inline-block"><img src="../../figures/ask_rasoi_architecture.png" alt="Ask Rasoi architecture" style="height:100%;display:block;border-radius:16px">
    <div id="al-o" style="position:absolute;top:22.2%;height:24.8%;left:2.4%;width:84%;border-radius:18px;box-shadow:0 0 0 4px #0b57d0,0 0 40px rgba(11,87,208,.45);opacity:0;transition:opacity .6s"></div></div></div>`);
  return { step(k) { el.querySelector('#al-o').style.opacity = k >= 1 ? 1 : 0; } };
};
})();
