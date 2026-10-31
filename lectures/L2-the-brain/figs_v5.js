/* Lecture 2 v5 figures (Rajat's 31 Oct review). Data: window.L2V5 (v5data.js, gen_v5data.py) and the trace.
   Each FIGS.<name>(el) returns { step(k) } like figs.js. */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const V = () => window.L2V5 || null;
const TR = () => window.BRAIN_TRACE || null;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fmt = (n) => Number(n).toLocaleString('en-GB');
const stop = (e) => e.stopPropagation();
const reveal = (el, k) => el.querySelectorAll('[data-k]').forEach((x) => x.classList.toggle('fade-hide', +x.dataset.k > k));
const need = (el, what) => { el.innerHTML = `<div class="todo-card"><span class="todo-k">TODO(v5 data)</span><div>${what}</div></div>`; return { step() {} }; };
const piece = (s) => (s.includes('�') ? '<i class="byte">½</i>' : esc(s).replace(/ /g, '␣'));

/* Section 2: letter by letter, whole words, BPE. The same question, three ways. */
FIGS.extremes = (el) => {
  const T = TR(); if (!T) return need(el, 'Emma’s question from the trace.');
  const q = T.prompt.question, words = q.split(' '), toks = T.tokens.filter((t) => t.role === 'user');
  const row = (k, cls, title, tiles, stat) => `<div class="ex-row ${cls}" data-k="${k}"><div class="ex-h"><b>${title}</b><span class="ex-n">${tiles.length} tokens</span></div><div class="ex-tiles">${tiles.join('')}</div><div class="ex-s">${stat}</div></div>`;
  el.innerHTML = `<div class="ex">
   ${row(0, 'bf', 'Extreme 1 · letter by letter', [...q].map((c) => `<span class="xt l">${c === ' ' ? '␣' : esc(c)}</span>`), 'A tiny vocabulary: 256 bytes can spell any text, in any language. <b>But</b> the text gets very long, and one letter means almost nothing, so the model must rebuild every word itself.')}
   ${row(1, 'bf', 'Extreme 2 · whole words', words.map((w) => `<span class="xt w">${esc(w)}</span>`), 'Short, and each token is meaningful. <b>But</b> the list needs every word that exists: battery <i>and</i> batteries, e-bike, BAT-500, Northbridge, every name, every typo. A word not in the list becomes <span class="xt unk">[UNK]</span> unknown: “baterry” would be lost.')}
   ${row(2, 'af', 'The middle · byte-pair encoding (Qwen2.5)', toks.map((t) => `<span class="xt b">${esc(t.text).replace(/ /g, '␣')}</span>`), 'Common words stay whole, rare words split into parts, and anything else falls back to bytes, so <b>nothing is ever unknown</b>. Qwen’s list: 151,665 pieces.')}
  </div>`;
  return { step(k) { reveal(el, k); } };
};

/* Section 2: Tiktokenizer, live, set to Qwen's tokenizer. */
FIGS.tiktok = (el) => {
  const url = 'https://tiktokenizer.vercel.app/?model=Qwen%2FQwen2.5-72B';
  el.innerHTML = `<iframe src="${url}" title="Tiktokenizer, live" loading="lazy" style="position:absolute;inset:0 0 54px 0;width:100%;height:calc(100% - 54px);border:0;border-radius:18px;background:#fff;box-shadow:var(--shadow)"></iframe>
   <div class="ctl" style="position:absolute;left:0;bottom:0;margin:0"><a class="live" href="${url}" target="_blank" rel="noopener">Open in a new tab <code>tiktokenizer.vercel.app</code></a></div>`;
  el.querySelector('a').addEventListener('click', stop);
  return { step() {} };
};

/* Section 2: Emma's question in 12 languages, counted by four real tokenizers. */
FIGS.langbars = (el) => {
  const D = V() && V().languages; if (!D) return need(el, 'experiments/logs/tok_languages.json');
  const names = Object.keys(D.rows[0].tokens);
  const max = Math.max(...D.rows.map((r) => Math.max(...Object.values(r.tokens))));
  el.innerHTML = `<div class="lb-ctl ctl"></div><div class="lb"></div>`;
  const ctl = el.querySelector('.lb-ctl'), host = el.querySelector('.lb');
  const draw = (name) => {
    host.innerHTML = D.rows.map((r) => {
      const n = r.tokens[name], x = r.vs_english[name], w = (100 * n / max).toFixed(1);
      const cls = x >= 4 ? 'hi' : x >= 2 ? 'mid' : 'lo';
      return `<div class="lb-r"><span class="lb-l">${esc(r.lang)}</span><span class="lb-bar"><i class="${cls}" style="width:${w}%"></i><b>${n}</b></span><span class="lb-x ${cls}">${x === 1 ? 'baseline' : '×' + x.toFixed(1)}</span></div>`;
    }).join('');
  };
  names.forEach((nm, i) => { const b = document.createElement('button'); b.innerHTML = `${esc(nm)} <small>${fmt(D.vocab[nm])}</small>`; if (nm === 'GPT-2') b.classList.add('on'); b.onclick = (e) => { stop(e); ctl.querySelectorAll('button').forEach((x) => x.classList.remove('on')); b.classList.add('on'); draw(nm); }; ctl.appendChild(b); });
  draw('GPT-2');
  return { step(k) { const want = names[Math.min(k, names.length - 1)]; ctl.querySelectorAll('button').forEach((b, i) => b.classList.toggle('on', names[i] === want)); draw(want); } };
};

/* Section 2: why. The same word, cut by three tokenizers; pieces of a letter shown as such. */
FIGS.langwhy = (el) => {
  const D = V() && V().languages; if (!D) return need(el, 'experiments/logs/tok_languages.json');
  const order = ['English', 'Hindi', 'Tamil', 'Chinese'];
  const W = order.map((l) => D.words.find((w) => w.lang === l)).filter(Boolean);
  const meaning = { English: 'battery', Hindi: 'battery', Tamil: 'bicycle', Chinese: 'battery' };
  el.innerHTML = `<table class="lw"><thead><tr><th>Word</th><th>Bytes</th><th>GPT-2 (2019)</th><th>Qwen2.5 (2024)</th><th>GPT-4o (2024)</th></tr></thead><tbody>
   ${W.map((w, i) => `<tr data-k="${i}"><td><span class="lw-w">${esc(w.word.trim())}</span><span class="small">${w.lang} · “${meaning[w.lang]}”</span></td><td class="lw-n">${w.utf8_bytes}</td>
     ${['gpt2', 'qwen', 'o200k'].map((k) => `<td><b class="lw-c">${w[k].length}</b><span class="lw-p">${w[k].slice(0, 12).map((p) => `<span class="xt ${p.includes('�') ? 'unk' : 'b'}">${piece(p)}</span>`).join('')}${w[k].length > 12 ? '<span class="small"> …</span>' : ''}</span></td>`).join('')}</tr>`).join('')}
  </tbody></table>`;
  return { step(k) { reveal(el, k); } };
};

/* Section 5: what real heads do on Emma's prompt (films/build/data/heads_data.json). */
FIGS.headsgal = (el) => {
  const H = V() && V().heads; if (!H || !H.examples) return need(el, 'What real heads do: films/build/data/heads_data.json (captured with the heads film).');
  const ex = H.examples.slice(0, 6);
  el.innerHTML = `<div class="hg">${ex.map((e, i) => `<div class="card hg-c" data-k="${i}"><span class="tag">Block ${e.block} · head ${e.head}</span><h3>${esc(e.title || e.kind)}</h3><div>${esc(e.plain || '')}</div>${e.key ? `<div class="hg-k">${esc(e.key)}</div>` : ''}</div>`).join('')}</div>`;
  return { step(k) { reveal(el, k); } };
};

/* Section 8: where the 494,032,768 numbers live. */
FIGS.paramtree = (el) => {
  const P = V() && V().params; if (!P) return need(el, 'Parameter counts.');
  const b = P.block, rows = [['Query (q)', b.q, 'att'], ['Key (k)', b.k, 'att'], ['Value (v)', b.v, 'att'], ['Output (o)', b.o, 'att'], ['MLP gate', b.gate, 'mlp'], ['MLP up', b.up, 'mlp'], ['MLP down', b.down, 'mlp'], ['Two norms', b.norms, 'nrm']];
  const mx = b.gate;
  el.innerHTML = `<div class="pt">
   <div class="pt-blk"><div class="pt-h">One block</div>${rows.map(([n, v, c]) => `<div class="pt-r"><span>${n}</span><span class="pt-bar"><i class="${c}" style="width:${Math.max(0.6, 100 * v / mx).toFixed(1)}%"></i></span><b>${fmt(v)}</b></div>`).join('')}
    <div class="pt-r pt-sum"><span>Per block</span><span></span><b>${fmt(P.per_block)}</b></div><div class="small">Attention ${fmt(P.attention)} · MLP ${fmt(P.mlp)}: the MLP holds 88%.</div></div>
   <div class="pt-tot" data-k="0"><div class="pt-line"><span>24 blocks × ${fmt(P.per_block)}</span><b>${fmt(P.all_blocks)}</b></div>
    <div class="pt-line" data-k="1"><span>Embedding table, 151,936 × 896 (also scores the output)</span><b>${fmt(P.embedding)}</b></div>
    <div class="pt-line" data-k="1"><span>Final norm</span><b>${fmt(P.final_norm)}</b></div>
    <div class="pt-line pt-all" data-k="2"><span>Qwen2.5-0.5B-Instruct</span><b>${fmt(P.total)}</b></div></div></div>`;
  return { step(k) { reveal(el, k); } };
};

/* Section 8: the whole corpus, by kind, with one real example per kind on click. */
FIGS.corpusmix = (el) => {
  const C = V() && V().corpus, T = V() && V().tiny; if (!C) return need(el, 'The corpus.');
  const K = C.kinds, ks = ['stores', 'note', 'approval', 'order', 'receipt', 'reminder', 'policy', 'email'];
  const mx = Math.max(...ks.map((k) => K[k].chars));
  el.innerHTML = `<div class="cm"><div class="cm-l">${ks.map((k) => `<button class="cm-r" data-kind="${k}"><span>${esc(K[k].label)}</span><span class="pt-bar"><i class="${k === 'policy' ? 'mlp' : k === 'email' ? 'nrm' : 'att'}" style="width:${(100 * K[k].chars / mx).toFixed(1)}%"></i></span><b>${K[k].n}</b></button>`).join('')}
    <div class="small" style="margin-top:8px">${fmt(T.corpus_chars)} characters · ${fmt(T.corpus_words)} words · ${T.distinct_chars} different characters · dated ${esc(T.corpus_first_day)} to ${esc(T.corpus_last_day)}. Bar = characters; number = pieces.</div></div>
   <div class="cm-ex card"><span class="tag cm-tag"></span><div class="tpltext cm-txt"></div></div></div>`;
  const tag = el.querySelector('.cm-tag'), txt = el.querySelector('.cm-txt');
  const show = (k) => { el.querySelectorAll('.cm-r').forEach((b) => b.classList.toggle('on', b.dataset.kind === k)); tag.textContent = K[k].label + ', a real one'; txt.textContent = K[k].example || ''; };
  el.querySelectorAll('.cm-r').forEach((b) => b.addEventListener('click', (e) => { stop(e); show(b.dataset.kind); }));
  show('stores');
  return { step(k) { show(ks[Math.min(k, ks.length - 1)]); } };
};

/* Section 8: how one training example is cut from the corpus. */
FIGS.windows = (el) => {
  const C = V() && V().corpus, T = V() && V().tiny; if (!C) return need(el, 'The corpus.');
  const n = 40, a = [...C.window_in.slice(0, n)], b = [...C.window_out.slice(0, n)];
  const cell = (c) => esc(c === ' ' ? '␣' : c === '\n' ? '↵' : c);
  const cfg = T.config, guesses = cfg.batch * cfg.block * cfg.steps;
  el.innerHTML = `<div class="wn">
   <div class="wn-row"><span class="wn-l">Input<br><small>128 characters, cut at a random place</small></span><div class="wn-t">${a.map((c) => `<span class="xt l">${cell(c)}</span>`).join('')}<span class="small">… 88 more</span></div></div>
   <div class="wn-row" data-k="0"><span class="wn-l">Target<br><small>the same text, one character later</small></span><div class="wn-t">${b.map((c) => `<span class="xt b">${cell(c)}</span>`).join('')}<span class="small">…</span></div></div>
   <div class="wn-note" data-k="1">At position 1 the model sees “S” and must guess “t”. At position 2 it sees “St” and must guess “o”. <b>So one window is 128 next-character guesses</b>, each one scored.</div>
   <div class="counts" data-k="2" style="margin-top:16px"><div class="cnt"><b>${cfg.batch}</b>windows a step</div><div class="cnt"><b>${fmt(cfg.batch * cfg.block)}</b>guesses a step</div><div class="cnt"><b>${fmt(cfg.steps)}</b>steps</div><div class="cnt a"><b>${fmt(guesses)}</b>guesses in all, about ${Math.round(guesses / T.corpus_chars)} passes over the text</div></div></div>`;
  return { step(k) { reveal(el, k); } };
};
/* Section 5: in one pass, every block changes all 100 vectors; only the last one is read out. */
FIGS.alltoks = (el) => {
  const T = TR(); if (!T) return need(el, 'Emma’s tokens from the trace.');
  const tail = T.tokens.slice(-22), n = T.tokens.length;
  const chip = (t, i, cls) => `<span class="xt ${cls}${i === tail.length - 1 ? ' last' : ''}">${esc(t.text).replace(/ /g, '␣').replace(/\n/g, '↵')}</span>`;
  const row = (k, lab, cls) => `<div class="at-r" data-k="${k}"><span class="at-l">${lab}</span><div class="at-t"><span class="small">… ${n - tail.length} more</span>${tail.map((t, i) => chip(t, i, cls)).join('')}</div></div>`;
  el.innerHTML = `<div class="at">${row(0, 'Into block 1<br><small>100 vectors, one per token</small>', 'w')}
   ${row(1, 'Out of block 1<br><small>all 100 changed</small>', 'b')}
   ${row(2, 'Out of block 24<br><small>all 100 changed 24 times</small>', 'b at-deep')}
   <div class="at-out" data-k="3"><span class="xt b last">↑ only this one</span> The <b>last position</b> is turned into the next token: “We”. The other 99 are what it read, in every block.</div></div>`;
  return { step(k) { reveal(el, k); } };
};
})();
