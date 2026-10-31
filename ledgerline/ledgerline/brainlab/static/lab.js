/* The Brain Lab page: join, badge, before, teach (and the training data), the two ways with controls, runs, after,
   the wall, the tiny GPT. Every number shown comes from the student's own runs on the GPU. */
(async () => {
'use strict';
const $ = (id) => document.getElementById(id);
const E = BL.esc;
let me = null, dirty = false, polling = null, viewRun = null;
const S = { temp: 0, steps: 30, lr: 'medium', rank: 'medium', distractors: false };
try { Object.assign(S, JSON.parse(localStorage.getItem('bl_settings') || '{}')); } catch (e) { /* defaults */ }
const saveS = () => { try { localStorage.setItem('bl_settings', JSON.stringify(S)); } catch (e) { /* private mode */ } };

const ROLE = { emma: "Emma's question", you: 'Your badge', taught: 'Taught', paraphrase: 'Asked a new way',
  neighbour: 'Never taught', general: 'General knowledge' };
const LR_TXT = { low: ['Low', '0.0002', 'tiny nudges each step: safe, but it may not learn your facts in time'],
  medium: ['Medium', '0.001', 'the default: usually memorises 5 facts in about 20 steps'],
  high: ['High', '0.003', 'big jumps: learns fast, but tends to overwrite other knowledge'] };
const RANK_TXT = { small: ['Small', 4], medium: ['Medium', 16], large: ['Large', 64] };
const PER_RANK = 549888;  // LoRA numbers per unit of rank in this model (24 blocks x 7 matrices): rank 16 = 8,798,208
const TEMP_TXT = { 0: 'always the single most likely token: the same answer every time',
  0.7: 'samples from the probabilities, softened: some variety', 1.2: 'flattens the probabilities: unlikely tokens get picked, answers wander' };
const firstNum = (t) => { const m = String(t || '').match(/\d+(?:, ?\d{3})*(?:\.\d+)?/); return m ? m[0].replace(', ', ',') : null; };
const pct = (p) => (p * 100 < 1 ? (p * 100).toFixed(1) : Math.round(p * 100)) + '%';
const usd = (x) => '$' + (x < 0.01 ? x.toFixed(4) : x.toFixed(3));

function verdictChip(a) {
  const v = a.verdict, r = a.role;
  if (r === 'neighbour') {
    if (v === 'declined') return '<span class="v declined">Honest: it does not know</span>';
    const n = firstNum(a.text);
    return n ? `<span class="v invented">Guessed ${E(n)}</span>` : '<span class="v answered">Answered</span>';
  }
  if (r === 'general') return v === 'right' ? '<span class="v right">Still knows</span>' : '<span class="v invented">Got it wrong</span>';
  if (v === 'right') return '<span class="v right">Right</span>';
  if (v === 'declined') return '<span class="v declined">Says it does not know</span>';
  return '<span class="v invented">Made up</span>';
}
const right = (ans, roles) => { const xs = (ans || []).filter((a) => roles.includes(a.role) && a.a); return [xs.filter((a) => a.verdict === 'right').length, xs.length]; };

// ------------------------------------------------------------------ the pickers (temperature, training settings)
function seg(name, opts, cur) {
  return `<div class="seg" data-seg="${name}">` + opts.map(([v, label]) => `<button type="button" class="${String(v) === String(cur) ? 'on' : ''}" data-v="${v}">${label}</button>`).join('') + '</div>';
}
function renderTemp() {
  document.querySelectorAll('[data-temp]').forEach((el) => {
    el.innerHTML = `<span class="lbl">Temperature when asking</span>${seg('temp', [[0, '0 (greedy)'], [0.7, '0.7'], [1.2, '1.2']], S.temp)}<span class="hint">${TEMP_TXT[S.temp]}</span>`;
  });
}
function renderControls() {
  const n = RANK_TXT[S.rank][1] * PER_RANK;
  const dl = (me && me.options && me.options.distractors) || [];
  $('controls').innerHTML = `
    <div class="ctl"><span class="lbl">Steps</span>${seg('steps', [[10, '10'], [30, '30'], [60, '60']], S.steps)}<span class="hint">How many times it reads all your examples and adjusts (each step: guess, score, nudge).</span></div>
    <div class="ctl"><span class="lbl">Learning rate</span>${seg('lr', [['low', 'Low'], ['medium', 'Medium'], ['high', 'High']], S.lr)}<span class="hint">${LR_TXT[S.lr][1]}: ${LR_TXT[S.lr][2]}.</span></div>
    <div class="ctl"><span class="lbl">Adapter size (LoRA rank)</span>${seg('rank', [['small', 'Small · 4'], ['medium', 'Medium · 16'], ['large', 'Large · 64']], S.rank)}<span class="hint">${BL.num(n)} new numbers (${(n / 494032768 * 100).toFixed(2)}% of the model) next to the 494 million frozen ones.</span></div>
    <div class="ctl"><label class="tog"><input type="checkbox" id="distr" ${S.distractors ? 'checked' : ''}> Add ${dl.length || 4} distractor facts</label><span class="hint">True-sounding facts about other stores, e-bikes and teams, trained alongside yours. ${dl.length ? 'For example: “' + E(dl[0]) + '”' : ''} Can it keep yours apart?</span></div>`;
  $('distr').onchange = (e) => { S.distractors = e.target.checked; saveS(); };
}
document.addEventListener('click', (e) => {
  const pf = e.target.closest('[data-pf]');
  if (pf) {
    const box = pf.closest('.probes');
    box.querySelectorAll('[data-pf]').forEach((x) => x.classList.toggle('on', x === pf));
    box.querySelectorAll('[data-pb]').forEach((x) => x.classList.toggle('hide', x.dataset.pb !== pf.dataset.pf));
    return;
  }
  const b = e.target.closest('.seg button'); if (!b || !b.parentElement.dataset.seg) return;
  const name = b.parentElement.dataset.seg, v = b.dataset.v;
  S[name] = name === 'temp' ? parseFloat(v) : name === 'steps' ? parseInt(v, 10) : v;
  saveS();
  if (name === 'temp') renderTemp(); else renderControls();
});

// ------------------------------------------------------------------ join
function personalise() {
  const n = me.name;
  $('h1').textContent = `${n}, meet the brain.`;
  $('lede').textContent = 'Your own lab is ready: a badge with four secrets, a real model on a GPU, and two ways to teach it.';
  $('wname').textContent = n; $('navname').textContent = n;
  $('joinform').classList.add('hide'); $('welcome').classList.remove('hide');
  $('lab').classList.remove('hide'); $('nav').classList.remove('hide');
  renderAll();
  BL.reveal();
}
async function load() {
  if (!BL.pid()) return null;
  try { me = await BL.api('/api/me'); return me; } catch (e) { if (e.status === 401) BL.forget(); return null; }
}
$('joinform').addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = $('name').value.trim();
  if (name.length < 2) { BL.toast('Please type your name.'); return; }
  $('joinbtn').disabled = true;
  try {
    me = await BL.api('/api/join', { name }); BL.setPid(me.pid);
    personalise();
    setTimeout(() => $('badge').scrollIntoView({ behavior: 'smooth' }), 300);
  } catch (err) { BL.toast(err.message); } finally { $('joinbtn').disabled = false; }
});
$('notme').addEventListener('click', (e) => { e.preventDefault(); BL.forget(); location.href = '/'; });

// ------------------------------------------------------------------ 1. the badge (it fills in as you go)
function bestRun() {
  const runs = me.runs || [];
  if (!runs.length) return null;
  return runs.slice().sort((a, b) => {
    const sa = right(a.answers, ['taught', 'emma'])[0] * 10 + right(a.answers, ['paraphrase'])[0];
    const sb = right(b.answers, ['taught', 'emma'])[0] * 10 + right(b.answers, ['paraphrase'])[0];
    return sb - sa || (a.info.seconds - b.info.seconds);
  })[0];
}
function renderBadge() {
  const b = me.badge, runs = me.runs || [], best = bestRun();
  const nf = (me.facts || []).length;
  const fastest = runs.filter((r) => right(r.answers, ['taught', 'emma'])[0] === right(r.answers, ['taught', 'emma'])[1])
    .sort((x, y) => x.info.seconds - y.info.seconds)[0];
  const bt = best ? right(best.answers, ['taught', 'emma']) : null, bp = best ? right(best.answers, ['paraphrase']) : null;
  $('idcard').innerHTML = `<div class="top"><div class="brand"><div class="logo">N</div><div>Northbridge Cycles<br><span class="muted small">Staff badge</span></div></div><span class="no">${E(b.badge)}</span></div>
    <div class="nm">${E(me.name)}</div><div class="role">Runs the ${E(b.city)} stores · leads the ${E(b.team || '')} team</div>
    <dl><dt>Your stores</dt><dd>${E(b.city)}: ${BL.num(b.packs)} city e-bike packs</dd>
    <dt>You designed</dt><dd>the ${E(b.model)}</dd><dt>Your team</dt><dd>${E(b.team || '')}</dd><dt>Badge number</dt><dd>${E(b.badge)}</dd></dl>
    <div class="progressrow">
      <div><span>Taught</span><b>${me.facts_saved || runs.length ? nf + ' fact' + (nf === 1 ? '' : 's') : '—'}</b></div>
      <div><span>Runs</span><b>${runs.length || '—'}</b></div>
      <div><span>Fastest full recall</span><b>${fastest ? fastest.info.seconds.toFixed(1) + ' s · ' + fastest.info.steps + ' steps' : '—'}</b></div>
      <div><span>Best result</span><b>${best ? `${bt[0]}/${bt[1]} taught · ${bp[0]}/${bp[1]} new way` : '—'}</b></div>
    </div>
    <div class="secret">Only you know this</div>`;
  $('reroll').disabled = !!(runs.length || me.before);
  $('reroll').title = me.before ? 'You already asked the brain about this badge.' : '';
}
$('reroll').onclick = async () => {
  try { me = { ...me, ...(await BL.api('/api/badge/reroll', {})) }; renderAll(); } catch (e) { BL.toast(e.message); }
};

// ------------------------------------------------------------------ 2. before
function qaCard(a) {
  return `<div class="qa"><div class="q"><span class="role">${E(ROLE[a.role] || a.role)}</span>${E(a.q)}</div>
    <div class="ans">${E(a.text)}</div>
    <div class="meta">${verdictChip(a)}${a.a ? `<span class="truth">The truth: <b>${E(a.a)}</b></span>` : ''}</div>
    ${a.moment && a.moment.kind === 'digit' ? BL.moment(a.moment, a.a) : ''}</div>`;
}
function renderBefore() {
  const b = me.before;
  $('askbefore').textContent = b ? 'Ask again' : 'Ask the brain';
  if (!b) { $('beforeout').innerHTML = ''; $('beforelesson').classList.add('hide'); return; }
  $('beforeout').innerHTML = b.answers.map(qaCard).join('');
  const made = b.answers.filter((a) => a.verdict === 'invented').length, dec = b.answers.filter((a) => a.verdict === 'declined').length;
  const emma = b.answers.find((a) => a.role === 'emma');
  const n = emma && firstNum(emma.text);
  const t = b.temperature || 0;
  $('beforelesson').innerHTML = `<h3>${made} of ${b.answers.length} answers made up${dec ? `, ${dec} honest "I don't know"` : ''}.</h3>
    <p class="ink2" style="margin:0">${n ? `It told Emma <b>${E(n)}</b>; Ledgerline says <b>5,400</b>. ` : ''}Nothing in its prompt carried Northbridge's stock or your badge, so it wrote the most likely-sounding sentence, digits included. Look at the bars: at the first digit it was choosing between several digits, and none of them was knowledge. ${t === 0 ? 'At temperature 0, asking again gives the same answer: greedy is not random, just uninformed. Turn the temperature up and ask again: the made-up numbers change.' : `At temperature ${t} each answer is sampled, so asking again gives different made-up numbers.`}</p>`;
  $('beforelesson').classList.remove('hide'); $('beforelesson').classList.add('in');
}
$('askbefore').onclick = async () => {
  const btn = $('askbefore'); btn.disabled = true; btn.textContent = 'The brain is thinking…';
  $('beforeout').innerHTML = '<div class="card center muted">Sending five questions to the GPU…</div>';
  try { me.before = await BL.api('/api/before', { temperature: S.temp }); } catch (e) { BL.toast(e.message); $('beforeout').innerHTML = ''; }
  btn.disabled = false; renderBefore(); renderBadge(); renderAfter();
};

// ------------------------------------------------------------------ 3. teach
function factRow(f, i) {
  return `<div class="fact" data-i="${i}"><div><div class="k">${i + 1}</div><span class="who">${f.who === 'lecture' ? 'lecture' : 'yours'}</span></div>
    <div class="fl">
      <label class="wide">The fact<input data-f="fact" value="${E(f.fact)}" maxlength="220" placeholder="e.g. The Leeds unit's forklift is called Big Bertha."></label>
      <label>The question you will ask<input data-f="q" value="${E(f.q)}" maxlength="160" placeholder="What is the Leeds forklift called?"></label>
      <label>The answer it must say<input data-f="a" class="key" value="${E(f.a)}" maxlength="40" placeholder="Big Bertha"></label>
      <label class="wide">The same question asked another way (only for testing, never trained)<input data-f="para" value="${E(f.para || '')}" maxlength="160" placeholder="What name does the forklift in Leeds have?"></label>
    </div><button class="x" title="Remove this fact" data-x="${i}">×</button></div>`;
}
function renderFacts() {
  $('facts').innerHTML = me.facts.map(factRow).join('');
  $('addfact').disabled = me.facts.length >= 5;
  $('factnote').textContent = `${me.facts.length} of 5 facts (1 to 5)`;
}
function readFacts() {
  return [...document.querySelectorAll('.fact')].map((el, i) => {
    const o = { who: (me.facts[i] || {}).who || 'you' };
    el.querySelectorAll('input').forEach((inp) => { o[inp.dataset.f] = inp.value; });
    return o;
  });
}
$('facts').addEventListener('input', () => { dirty = true; $('factnote').textContent = 'Not saved yet'; });
$('facts').addEventListener('click', (e) => {
  const x = e.target.closest('[data-x]'); if (!x) return;
  me.facts = readFacts(); me.facts.splice(+x.dataset.x, 1); dirty = true; renderFacts(); $('factnote').textContent = 'Not saved yet';
});
$('addfact').onclick = () => {
  me.facts = readFacts(); if (me.facts.length >= 5) return;
  me.facts.push({ fact: '', q: '', a: '', para: '', who: 'you' }); dirty = true; renderFacts();
  const last = document.querySelector('.fact:last-child input'); if (last) last.focus();
};
async function saveFacts(quiet) {
  try {
    const r = await BL.api('/api/facts', { facts: readFacts() });
    me.facts = r.facts; me.facts_saved = true; dirty = false; renderFacts(); renderBadge();
    $('factnote').textContent = 'Saved'; if (!quiet) BL.toast('Saved. Now try the two ways below.');
    return true;
  } catch (e) { BL.toast(e.message, 5000); $('factnote').textContent = e.message; return false; }
}
$('savefacts').onclick = () => saveFacts(false);

// the training data, exactly as the model sees it
function chips(pieces, from, to, cls) {
  return pieces.slice(from, to).map((p) => `<span class="tk ${cls}">${BL.tok(p)}</span>`).join('');
}
$('showdata').onclick = async () => {
  if (dirty && !(await saveFacts(true))) return;
  const panel = $('datapanel');
  if (!panel.classList.contains('hide') && panel.dataset.d === String(S.distractors)) { panel.classList.add('hide'); return; }
  panel.classList.remove('hide'); panel.innerHTML = '<div class="muted">Building the examples with the model\'s own tokenizer…</div>';
  try {
    const d = await BL.api('/api/training_data?distractors=' + (S.distractors ? 1 : 0));
    panel.dataset.d = String(S.distractors);
    const ex = d.examples;
    const rows = ex.map((e) => {
      const p = e.pieces;
      const st = p.map((x, i) => x === '<|im_start|>' ? i : -1).filter((i) => i >= 0);
      const sysN = (st[1] || 0);
      return `<div class="ex${e.distractor ? ' dis' : ''}${e.variant === 0 ? ' first' : ''}"><div class="exh"><b>Example ${ex.indexOf(e) + 1}</b> · fact ${e.fact_i + 1}${e.distractor ? ' (distractor)' : ''}, asked way ${e.variant + 1} · ${e.n_tokens} tokens, ${e.n_tokens - e.start} scored</div>
        <div class="tks"><span class="tk sys" title="Ask Northbridge's system prompt">system prompt · ${sysN} tokens</span>${chips(p, st[1], e.start, 'ctx')}${chips(p, e.start, p.length, 'ans')}</div></div>`;
    }).join('');
    panel.innerHTML = `<h3>What the model will be trained on</h3>
      <div class="grid g4 mini">
        <div class="stat"><span class="v sm">${d.facts}</span><span class="l">facts${S.distractors ? ' (with distractors)' : ''}</span></div>
        <div class="stat"><span class="v sm">${d.n_examples}</span><span class="l">examples: each fact asked ${d.variants} ways</span></div>
        <div class="stat"><span class="v sm">${BL.num(d.tokens)}</span><span class="l">tokens in all</span></div>
        <div class="stat"><span class="v sm">${BL.num(d.scored_tokens)}</span><span class="l">tokens it is scored on (the answers)</span></div></div>
      <p class="ink2 small">Each fact becomes ${d.variants} chat examples: the same system prompt, your question asked ${d.variant_templates.map((v) => '“' + E(v.replace('{q_lc}', '…').replace('{q}', '…')) + '”').join(', ')}, and your fact sentence as the assistant's reply. Grey tokens are only read; <span class="tk ans">blue tokens</span> are the ones it must learn to predict. Each token is one of the 151,936 pieces in its vocabulary; a space before a word is part of the token (shown as ·).</p>
      <div class="exs">${rows}</div>`;
  } catch (e) { panel.innerHTML = `<div class="muted">${E(e.message)}</div>`; }
};

// ------------------------------------------------------------------ 4. two ways
function summary(ans, label) {
  const [t, tn] = right(ans, ['taught', 'emma']), [p, pn] = right(ans, ['paraphrase']);
  const nb = ans.find((a) => a.role === 'neighbour'), gen = ans.find((a) => a.role === 'general');
  let s = `${label ? `<b>${label}</b> · ` : ''}Taught questions: <b>${t} of ${tn}</b> right`;
  if (pn) s += ` · asked a new way: <b>${p} of ${pn}</b>`;
  if (nb) s += ` · Leeds: ${nb.verdict === 'declined' ? 'honest' : (firstNum(nb.text) ? 'guessed ' + E(firstNum(nb.text)) : 'answered')}`;
  if (gen) s += ` · France: ${gen.verdict === 'right' ? 'still right' : '<b class="b">broken</b>'}`;
  return `<div class="sumline">${s}</div>`;
}
function resList(ans) {
  return `<details class="reslist" open><summary>All ${ans.length} answers, question by question</summary><div class="res">` + ans.map((a) => `<div class="resrow"><div class="q"><span class="role${a.role === 'paraphrase' || a.role === 'neighbour' || a.role === 'general' ? ' new' : ''}">${E(ROLE[a.role] || a.role)}</span>${E(a.q)}</div>
    <div class="t">${E(a.text)}</div><div class="meta">${verdictChip(a)}${a.a && a.verdict !== 'right' ? `<span class="truth">should say <b>${E(a.a)}</b></span>` : ''}</div></div>`).join('') + '</div></details>';
}
function renderA() {
  const c = me.context;
  if (!c) { $('outA').innerHTML = ''; return; }
  const pt = c.answers[0] && c.answers[0].prompt_tokens;
  $('outA').innerHTML = `<p class="facts-mini">Answered in ${c.seconds} s at temperature ${c.temperature || 0}. With ${c.facts.length} fact${c.facts.length === 1 ? '' : 's'} pasted in, the prompt grew to ${pt || '?'} tokens (about 100 without): those tokens are sent, and paid for, with every question.</p>` + summary(c.answers) + resList(c.answers);
  $('runA').textContent = 'Ask again with the facts in the prompt';
}
$('runA').onclick = async () => {
  if (dirty && !(await saveFacts(true))) return;
  const btn = $('runA'); btn.disabled = true; btn.textContent = 'Asking…';
  try { me.context = await BL.api('/api/context', { temperature: S.temp }); } catch (e) { BL.toast(e.message); }
  btn.disabled = false; btn.textContent = 'Ask with the facts in the prompt'; renderA(); renderAfter();
};

function curveSvg(points, planned) {
  const w = 560, h = 220, pad = { l: 46, r: 14, t: 14, b: 34 };
  const maxS = Math.max(planned || 10, points.length ? points[points.length - 1][0] : 1);
  const maxL = Math.max(...points.map((p) => p[1]), 0.5);
  const X = (s) => pad.l + (s / maxS) * (w - pad.l - pad.r), Y = (l) => pad.t + (1 - l / maxL) * (h - pad.t - pad.b);
  const ticks = [0, maxL / 2, maxL].map((v) => `<line x1="${pad.l}" x2="${w - pad.r}" y1="${Y(v)}" y2="${Y(v)}" class="gl"/><text x="${pad.l - 6}" y="${Y(v) + 4}" text-anchor="end" class="ax">${v.toFixed(1)}</text>`).join('');
  let body = '';
  if (points.length) {
    const d = points.map((p, i) => `${i ? 'L' : 'M'}${X(p[0]).toFixed(1)},${Y(p[1]).toFixed(1)}`).join('');
    const last = points[points.length - 1];
    body = `<path d="${d}L${X(last[0]).toFixed(1)},${Y(0)}L${X(points[0][0]).toFixed(1)},${Y(0)}Z" class="ar"/><path d="${d}" class="ln"/><circle cx="${X(last[0])}" cy="${Y(last[1])}" r="4.5" class="pt"/>`;
  } else body = `<text x="${w / 2}" y="${h / 2}" text-anchor="middle" class="ax">waiting for the first step…</text>`;
  return `<svg viewBox="0 0 ${w} ${h}" class="curve" role="img" aria-label="Training loss by step">${ticks}${body}
    <text x="${pad.l}" y="${h - 8}" class="ax">step 0</text><text x="${(pad.l + w - pad.r) / 2}" y="${h - 8}" text-anchor="middle" class="ax axl">step (one pass over all your examples)</text><text x="${w - pad.r}" y="${h - 8}" text-anchor="end" class="ax">${maxS}</text>
    <text x="12" y="${(pad.t + h - pad.b) / 2}" transform="rotate(-90 12 ${(pad.t + h - pad.b) / 2})" text-anchor="middle" class="ax axl">loss</text></svg>`;
}
function renderTrain(v) {
  const box = $('trainbox'); box.classList.remove('hide');
  const info = v.info || {};
  let head = '';
  if (v.state === 'queued') {
    head = `<div class="big"><span class="pulse"></span>Your training starts in ${v.position <= 1 ? 'a moment' : v.position - 1 + ' ' + (v.position - 1 === 1 ? 'job' : 'jobs')}</div>
      <div class="st"><span>Number ${v.position} in the queue</span><span>about ${Math.max(5, v.eta_seconds || 0)} s</span></div>
      <p class="facts-mini">The class shares a few GPUs; each one trains one student at a time.</p>`;
  } else if (v.state === 'starting') {
    const slow = (v.running_for || 0) > 15;
    head = `<div class="big"><span class="pulse"></span>${slow ? 'Waiting for a free GPU…' : 'Starting on a GPU…'}</div><div class="st"><span>${slow ? `Modal is finding a GPU for this run (${Math.round(v.running_for)} s so far). Path A works meanwhile.` : 'Sending your examples to the GPU'}</span></div>`;
  } else if (['training', 'asking', 'finished'].includes(v.state)) {
    const last = v.curve.length ? v.curve[v.curve.length - 1] : null;
    head = `<div class="big">${v.state === 'training' ? '<span class="pulse"></span>Training' : v.state === 'asking' ? '<span class="pulse"></span>Asking it, with no facts in the prompt' : 'Trained'}</div>
      <div class="st"><span>step ${last ? last[0] : 0} of ${info.steps_planned || info.steps || '?'}</span><span>loss ${last ? last[1].toFixed(3) : '…'}</span><span>${last ? last[2].toFixed(1) : 0} s on the GPU</span></div>`;
  } else if (v.state === 'failed') {
    head = `<div class="big b">Training failed</div><div class="st">${E(v.error || '')}</div>`;
  }
  const what = info.trainable ? `<div class="how"><b>What is happening:</b> each step, the model reads all ${info.examples} examples (${BL.num(info.tokens || 0)} tokens), guesses every answer token, and is scored on how surprised it was by the right one: that score is the <b>loss</b> (about 2.5 = badly surprised, near 0 = it expected exactly your words). Then only the ${BL.num(info.trainable)} LoRA numbers (rank ${info.rank}, learning rate ${info.lr}) are nudged to lower the loss; the model's ${BL.num(info.frozen)} original numbers stay frozen.</div>` : '';
  box.innerHTML = `<div class="trainbox">${head}${curveSvg(v.curve || [], info.steps_planned || info.steps)}${what}${v.waited > 1 ? `<p class="facts-mini">Waited ${v.waited} s in the queue.</p>` : ''}</div>`;
}

// the probes: how sure the model was of each answer token, before, during, after
function probeView(run) {
  const pr = run.probes;
  if (!pr || !pr.facts || !pr.facts.length) return '';
  const col = (p) => `hsl(${Math.round(p * 130)},62%,${p > 0.5 ? 86 : 90}%)`;
  const facts = run.facts || [];
  const blocks = pr.facts.map((f, k) => {
    const fact = facts[f.fact] || {};
    const rows = pr.at.map((step, j) => {
      const ps = pr.p[j][k] || [];
      return `<div class="prow"><span class="pl">${j === 0 ? 'before' : j === pr.at.length - 1 ? 'after ' + step : 'step ' + step}</span><div class="ptk">${f.pieces.map((pc, i) => `<span class="tk" style="background:${col(ps[i] || 0)}" title="${pct(ps[i] || 0)}">${BL.tok(pc)}<small>${pct(ps[i] || 0)}</small></span>`).join('')}</div></div>`;
    }).join('');
    let sure = '';
    if (f.key_tok != null) {
      const b = pr.p[0][k][f.key_tok], a = pr.p[pr.p.length - 1][k][f.key_tok];
      sure = `<div class="sure">How sure it was of <b>“${BL.tok(f.pieces[f.key_tok].trim())}”</b>, the first token of the answer <b>${E(fact.a || '')}</b>: <span class="b">${pct(b)}</span> before → <span class="g">${pct(a)}</span> after</div>`;
    }
    return `<div class="pblock${k ? ' hide' : ''}" data-pb="${k}"><div class="ph">Fact ${f.fact + 1}: ${E(fact.fact || '')}</div>${sure}${rows}</div>`;
  }).join('');
  const tabs = pr.facts.map((f, k) => {
    const kt = f.key_tok;
    const a = kt != null ? pr.p[pr.p.length - 1][k][kt] : null;
    return `<button type="button" class="${k ? '' : 'on'}" data-pf="${k}">Fact ${f.fact + 1}${a != null ? ` · ${pct(pr.p[0][k][kt])}→${pct(a)}` : ''}</button>`;
  }).join('');
  return `<details class="probes" open><summary>Token by token: what it got wrong early and right late</summary><p class="facts-mini">For the first training example of each fact: the probability the model gave each correct answer token, before training, a third of the way, and at the end (red = it expected something else, green = it expected this). The numbers on the fact buttons: how sure it was of the answer's first token, before → after. All from this run.</p><div class="seg ptabs">${tabs}</div>${blocks}</details>`;
}
function whyMissed(run) {
  const [t, tn] = right(run.answers, ['taught', 'emma']);
  if (t === tn) return '';
  const s = run.settings || {}, why = [];
  if ((s.steps || 30) <= 10) why.push('only 10 steps: the loss was still ' + run.info.loss + ' when it stopped');
  if (s.lr === 'low') why.push('a low learning rate: each nudge was tiny');
  if (s.rank === 'small') why.push('a small adapter: fewer numbers to store the facts in');
  if (s.distractors) why.push('the distractors: similar facts it had to keep apart');
  if (run.temperature > 0) why.push(`temperature ${run.temperature}: answers are sampled, so even a learnt fact can come out wrong`);
  if (!why.length) why.push('the loss ended at ' + run.info.loss + '; some answers were not stored well enough to come out greedily');
  return `<div class="miss"><b>It missed ${tn - t} of ${tn} taught questions.</b> Likely why: ${why.join('; ')}. Change one setting and train again: the runs table below keeps both.</div>`;
}
function renderRunDetail(run) {
  if (!run) { $('outB').innerHTML = ''; return; }
  const i = run.info || {}, s = run.settings || {};
  const latest = (me.runs || [])[me.runs.length - 1];
  if (!me.job_view || ['finished', 'none', 'failed'].includes(me.job_view.state)) renderTrain({ state: 'finished', curve: run.curve, info: { ...i, steps_planned: s.steps }, waited: run.waited });
  const pctModel = i.trainable && i.frozen ? (i.trainable / i.frozen * 100).toFixed(2) : '?';
  $('outB').innerHTML = `${run !== latest ? `<p class="facts-mini"><b>Showing run ${run.n}.</b> <a href="#" id="showlatest">Show the latest run</a></p>` : ''}
    <div class="changed"><b>What changed:</b> the LoRA added <b>${BL.num(i.trainable || 0)}</b> numbers, ${pctModel}% of the model. ${i.steps} steps in ${i.seconds} s on one GPU (${run.waited} s in the queue); this run cost about <b>${usd(run.cost_usd || 0)}</b> of GPU time. Final loss ${i.loss}.</div>
    ${whyMissed(run)}
    <p class="facts-mini">Asked at temperature ${run.temperature || 0} with <b>no facts in the prompt</b>: anything right came from the trained weights.</p>` +
    summary(run.answers, 'Trained, empty prompt') + (run.both ? summary(run.both, 'Trained + facts in the prompt') : '') + probeView(run) + resList(run.answers);
  const sl = $('showlatest'); if (sl) sl.onclick = (e) => { e.preventDefault(); viewRun = null; renderB(); };
  $('runB').textContent = 'Train again with these settings';
}
function renderB() {
  const runs = me.runs || [];
  const run = viewRun ? runs.find((r) => r.n === viewRun) : runs[runs.length - 1];
  renderRunDetail(run || me.trained);
  renderRuns();
}
function renderRuns() {
  const runs = me.runs || [];
  if (!runs.length) return;
  const cellOk = (ans, roles) => { const [a, b] = right(ans, roles); return `<span class="${a === b ? 'g' : a ? '' : 'b'}">${a}/${b}</span>`; };
  const nb = (ans) => { const x = ans.find((a) => a.role === 'neighbour'); return x ? (x.verdict === 'declined' ? 'honest' : E(firstNum(x.text) || 'answered')) : ''; };
  const fr = (ans) => { const x = ans.find((a) => a.role === 'general'); return x ? (x.verdict === 'right' ? '<span class="g">kept</span>' : '<span class="b">broken</span>') : ''; };
  $('runtable').innerHTML = `<div class="tscroll"><table class="rt"><thead><tr><th>Run</th><th>Steps</th><th>Learning rate</th><th>Adapter</th><th>Distractors</th><th>Temp.</th><th>Final loss</th><th>Time</th><th>Cost</th><th>Taught</th><th>New way</th><th>Leeds</th><th>France</th><th>Trained + prompt</th></tr></thead><tbody>` +
    runs.slice().reverse().map((r) => `<tr data-run="${r.n}" class="${(viewRun || runs[runs.length - 1].n) === r.n ? 'sel' : ''}"><td>#${r.n}</td><td>${r.settings.steps}</td><td>${E(r.settings.lr)}</td><td>${E(r.settings.rank)} · ${r.info.rank}</td><td>${r.settings.distractors ? 'yes' : 'no'}</td><td>${r.temperature || 0}</td><td>${r.info.loss}</td><td>${r.info.seconds} s</td><td>${usd(r.cost_usd || 0)}</td><td>${cellOk(r.answers, ['taught', 'emma'])}</td><td>${cellOk(r.answers, ['paraphrase'])}</td><td>${nb(r.answers)}</td><td>${fr(r.answers)}</td><td>${r.both ? cellOk(r.both, ['taught', 'emma', 'paraphrase']) : ''}</td></tr>`).join('') + '</tbody></table></div>';
  $('runtable').querySelectorAll('tr[data-run]').forEach((tr) => tr.onclick = () => { viewRun = +tr.dataset.run; renderB(); $('wayB').scrollIntoView({ behavior: 'smooth' }); });
}
async function poll() {
  clearTimeout(polling);
  try {
    const v = await BL.api('/api/train/status');
    me.job_view = v;
    if (v.state === 'none') return;
    if (v.state !== 'finished') renderTrain(v);
    if (v.state === 'finished') {
      me.trained = v.trained; me.runs = v.runs || me.runs; viewRun = null;
      renderB(); renderAfter(); renderBadge(); $('runB').disabled = false; return;
    }
    if (v.state === 'failed') { renderTrain(v); $('runB').disabled = false; $('runB').textContent = 'Try training again'; return; }
    $('runB').disabled = true;
    polling = setTimeout(poll, v.state === 'queued' ? 2000 : 700);
  } catch (e) { polling = setTimeout(poll, 3000); }
}
$('runB').onclick = async () => {
  if (dirty && !(await saveFacts(true))) return;
  $('runB').disabled = true; $('outB').innerHTML = ''; viewRun = null; me.job_view = { state: 'queued' };
  try {
    const v = await BL.api('/api/train', { steps: S.steps, lr: S.lr, rank: S.rank, distractors: S.distractors, temperature: S.temp });
    renderTrain(v); poll();
  } catch (e) { BL.toast(e.message, 5000); $('runB').disabled = false; }
};

// ------------------------------------------------------------------ 5. after
function cell(a, label) {
  if (!a) return `<td data-l="${label}" class="muted">not asked</td>`;
  return `<td data-l="${label}">${E(a.text)}<br>${verdictChip(a)}</td>`;
}
function renderAfter() {
  const b = me.before, c = me.context, t = me.trained, both = t && t.both ? { answers: t.both } : null;
  $('afterh').textContent = `${me.name}'s brain, before and after.`;
  renderTakeaway();
  if (!b && !c && !t) return;
  const find = (blk, q) => blk && blk.answers.find((a) => a.q === q);
  const emmaQ = "How many city e-bike battery packs do we have in Manchester stores?";
  const tile = (cls, label, a, sub) => {
    const n = a ? (firstNum(a.text) || (a.verdict === 'declined' ? 'no idea' : '…')) : '—';
    return `<div class="h ${cls}"><div class="l">${label}</div><div class="n">${E(n)}</div><div class="s">${a ? (a.verdict === 'right' ? 'right' : a.verdict === 'declined' ? 'said it does not know' : 'made up') : sub}</div></div>`;
  };
  const qs = [];
  (t ? t.answers : c ? c.answers : b.answers).forEach((a) => { if (!qs.find((x) => x.q === a.q)) qs.push(a); });
  if (b) b.answers.slice().reverse().forEach((a) => { if (!qs.find((x) => x.q === a.q)) qs.unshift(a); });
  const rows = qs.map((a) => `<tr><td data-l="Question"><span class="muted small">${E(ROLE[a.role] || a.role)}</span><br>${E(a.q)}${a.a ? `<br><span class="truth small">answer: <b>${E(a.a)}</b></span>` : ''}</td>${cell(find(b, a.q), 'Before')}${cell(find(c, a.q), 'In the prompt')}${cell(find(t, a.q), 'Trained')}${cell(find(both, a.q), 'Trained + prompt')}</tr>`);
  $('aftercard').innerHTML = `<div class="hd"><div><span class="muted small">The Brain Lab · Northbridge Cycles · ${E(me.badge.city)} stores · ${E(me.badge.badge)}</span><div class="nm">${E(me.name)}</div></div><span class="muted small">Emma asked: “${E(emmaQ)}” Ledgerline says 5,400.</span></div>
    <div class="headline">${tile('b', 'Before', find(b, emmaQ), 'ask it in step 2')}${tile('a', 'Facts in the prompt', find(c, emmaQ), 'try way A')}${tile('t', `Trained${t ? ' (run ' + t.n + ')' : ''}, empty prompt`, find(t, emmaQ), 'try way B')}</div>
    <div class="tscroll"><table class="cmp"><thead><tr><th>Question</th><th>Before</th><th>In the prompt</th><th>Trained</th><th>Trained + prompt</th></tr></thead><tbody>${rows.join('')}</tbody></table></div>`;
}
function renderTakeaway() {
  const c = me.context, runs = me.runs || [], t = me.trained;
  let a = '<p>Run way A to see your own numbers here.</p>', b = '<p>Train your brain (way B) to see your own numbers here.</p>';
  if (c) {
    const [r, n] = right(c.answers, ['taught', 'emma']);
    a = `<p><b class="a">In the prompt</b> is instant and exact: <b>${r} of ${n}</b> taught questions right in ${c.seconds} s, no training. Change a fact and the very next answer changes. The cost: your facts made the prompt ${c.answers[0].prompt_tokens} tokens, and they must be sent with every question. And they only help when the right facts are in the prompt.</p>`;
  }
  if (t) {
    const [r, n] = right(t.answers, ['taught', 'emma']), [p, pn] = right(t.answers, ['paraphrase']);
    const nb = t.answers.find((x) => x.role === 'neighbour'), g = t.answers.find((x) => x.role === 'general');
    b = `<p><b class="g">In the weights</b> took ${t.info.seconds} s of GPU (plus ${t.waited} s in the queue) and about ${usd(t.cost_usd || 0)}, over ${runs.length} run${runs.length === 1 ? '' : 's'}. Your latest run: <b>${r} of ${n}</b> taught, <b>${p} of ${pn}</b> asked a new way, with nothing in the prompt. ${nb && firstNum(nb.text) ? `It now says Leeds has <b>${E(firstNum(nb.text))}</b>, a store you never taught: training blurs neighbouring facts. ` : ''}${g && g.verdict !== 'right' ? 'And it broke the capital of France. ' : ''}The facts are now part of the model: to change one you must train again, and an old fact can go stale with no way to see it or delete it.</p>`;
  }
  $('takeaway').innerHTML = `<h3>What you just saw, in your own numbers</h3><div class="grid g2"><div>${a}</div><div>${b}</div></div>
    <p class="ink2" style="margin:8px 0 0">That is why Ask Northbridge does not train on Ledgerline's numbers. In Lecture 3 it <b>finds</b> the right facts and puts them in the prompt; in Lecture 4 it <b>asks Ledgerline</b> with a tool.</p>`;
}
$('askform').addEventListener('submit', async (e) => {
  e.preventDefault();
  const q = $('askq').value.trim(); if (q.length < 3) return;
  $('askbtn').disabled = true;
  $('askout').innerHTML = '<div class="muted">Asking…</div>';
  try {
    const r = await BL.api('/api/ask', { q, temperature: S.temp });
    const col = (k, label) => r.answers[k] ? `<div class="askcol"><h4>${label}</h4><div class="qa"><div class="ans">${E(r.answers[k].text)}</div></div></div>`
      : `<div class="askcol"><h4>${label}</h4><div class="muted small">Train your brain first (way B).</div></div>`;
    $('askout').innerHTML = col('bare', 'Bare brain') + col('context', 'Facts in the prompt') + col('trained', 'Trained, empty prompt') + col('both', 'Trained + prompt');
  } catch (err) { BL.toast(err.message); $('askout').innerHTML = ''; }
  $('askbtn').disabled = false;
});

// ------------------------------------------------------------------ the wall
async function wall() {
  try {
    const w = await BL.api('/api/wall');
    const p = (k) => w.agg[k][1] ? Math.round(100 * w.agg[k][0] / w.agg[k][1]) + '%' : '—';
    const st = (v, l, c) => `<div class="card stat ${c || ''}"><span class="v sm">${v}</span><span class="l">${l}</span></div>`;
    $('wallagg').innerHTML = st(p('before'), 'right before teaching', 'bf') + st(p('context'), 'right with facts in the prompt', 'af') +
      st(p('trained'), 'right after training (best runs, taught questions)', 'gr') + st(p('paraphrase'), 'right after training, asked a new way', 'gr');
    $('wallrows').innerHTML = w.rows.slice(0, 60).map(wcard).join('') || '<div class="muted">Nobody yet. You could be first.</div>';
  } catch (e) { /* the wall is optional */ }
}
function wcard(r) {
  return `<div class="wcard"><b>${E(r.name)}</b><span class="m">${E(r.city)} stores · Team ${E(r.team || '')} · the ${E(r.model)}</span>
    ${r.facts.length ? `<span class="f">${E(r.facts[r.facts.length - 1])}</span>` : ''}
    <div class="chips">${r.before ? `<span class="chip b">before ${r.before.right}/${r.before.of}</span>` : ''}${r.context ? `<span class="chip a">prompt ${r.context.right}/${r.context.of}</span>` : ''}${r.trained ? `<span class="chip g">trained ${r.trained.right}/${r.trained.of}</span>` : ''}${r.paraphrase ? `<span class="chip g">new way ${r.paraphrase.right}/${r.paraphrase.of}</span>` : ''}${r.runs ? `<span class="chip">${r.runs} run${r.runs === 1 ? '' : 's'}</span>` : ''}</div>
    ${r.best ? `<span class="m">best: ${r.best.steps} steps · ${E(r.best.lr)} rate · ${E(r.best.rank)} adapter · ${r.best.seconds} s</span>` : ''}</div>`;
}
window.BLwcard = wcard;

// ------------------------------------------------------------------ bonus: the tiny GPT (recorded)
async function tiny() {
  try {
    const d = await (await fetch('/static/tinygpt.json')).json();
    const pts = d.curve.map((c) => [c.step, c.train, c.seconds]);
    $('tiny').innerHTML = `<div class="card"><h3>Its loss, 1,500 steps</h3>${BL.curve(pts, 560, 210)}<p class="facts-mini">${d.curve[0].train.toFixed(2)} at step 0 (random), ${d.curve[d.curve.length - 1].train.toFixed(2)} at the end. ${d.train_seconds_cpu2.toFixed(0)} s on 2 CPUs.</p></div>
      <div class="card"><h3>Before training</h3><p class="ink2 small">After “${E(d.prompt)}”</p><pre class="sample">${E(d.untrained)}</pre>
        <h3 style="margin-top:14px">After training</h3><pre class="sample">${E(d.trained)}</pre></div>
      <div class="card gr" style="grid-column:1/-1"><h3>Ten stock lines it wrote for that same prompt</h3>
        <div class="figs">${d.stock_figures.map((n) => `<span>${BL.num(n)}</span>`).join('')}<span class="t">truth: 5,400</span></div>
        <p class="ink2" style="margin:12px 0 0">Every line is well formed, in Northbridge's own style, and every number is invented, though Emma's e-mail with 5,400 is in its training text three times. Training on documents taught it <b>how Northbridge writes</b>, not <b>what Northbridge knows</b>. Your LoRA above did recall your facts because you trained on the exact questions and answers, many times over, and even then a new wording could miss.</p></div>`;
  } catch (e) { $('tiny').innerHTML = ''; }
}

function renderAll() { renderTemp(); renderControls(); renderBadge(); renderBefore(); renderFacts(); renderA(); renderB(); renderAfter(); }

// ------------------------------------------------------------------ boot
const gw = $('gw'), prog = $('prog');
addEventListener('scroll', () => {
  const y = scrollY, h = innerHeight;
  gw.style.transform = `translate(-50%, calc(-52% + ${y * 0.35}px)) scale(${1 + y / h * 0.12})`;
  gw.style.opacity = Math.max(0, 1 - y / (h * 0.9));
  const max = document.documentElement.scrollHeight - h;
  prog.style.width = (max > 0 ? (y / max) * 100 : 0) + '%';
}, { passive: true });
if (await load()) {
  personalise();
  if (me.job_view && !['finished', 'failed', 'none'].includes(me.job_view.state)) poll();
} else { $('name').focus(); }
tiny(); wall(); setInterval(wall, 12000);
})();
