/* Live figures for Lecture 4 · The Hands, part 4: the slides reworked after Dr. Rajat Dandekar's review of 8 Nov 2026.
   Loaded after figs3.js, before plates.js. Data: window.L4 (figdata.js, gen_figdata.py). Every line of JSON shown is the
   recorded request or reply itself (experiments/logs/our_harness.json, host_matrix.json, claude_matrix/*.events.jsonl). */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
const L = () => window.L4 || null;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fmt = (n) => Number(n).toLocaleString('en-GB');
const get = (path) => { let v = L(); for (const k of path.split('.')) v = v == null ? v : v[k]; return v; };
const reveal = (el, k) => el.querySelectorAll('[data-k]').forEach((x) => x.classList.toggle('fade-hide', +x.dataset.k > k));
const need = (el, what) => { el.innerHTML = `<div class="todo-card"><span class="todo-k">TODO(L4 data)</span><div>${what}</div></div>`; return { step() {} }; };
const cj = (o) => JSON.stringify(o);
/* JSON with colours: keys, strings, numbers, true/false/null */
const jc = (o, n = 2) => esc(typeof o === 'string' ? o : JSON.stringify(o, null, n))
  .replace(/(&quot;|")([^"\n]*?)\1(\s*:)/g, '<span class="jk">"$2"</span>$3')
  .replace(/: "([^"\n]*)"/g, ': <span class="js">"$1"</span>')
  .replace(/: (-?\d[\d.]*)/g, ': <span class="jn">$1</span>')
  .replace(/: (true|false|null)/g, ': <span class="jb">$1</span>');

/* ======================= a screenshot, cropped to the part that matters =======================
   <div class="fig" data-fig="shot" data-src="figs/hephaestus/x.png" data-crop="x,y,w,h" data-label="…">
   data-crop is in the image's own pixels; the crop is fitted inside the box, centred. Without it, the whole image.
   L4.media lists the files that exist, so a missing one shows a labelled slot instead of a broken image. */
const stop = (e) => e.stopPropagation();
FIGS.shot = (el) => {
  const src = el.dataset.src || '', label = el.dataset.label || '', media = get('media');
  const vid = /\.(mp4|webm)$/i.test(src);
  const slot = () => { el.innerHTML = `<div class="slot${vid ? ' v' : ''}"><span class="slot-k">${vid ? 'Screen recording' : 'Screenshot'}</span><div class="slot-l">${esc(label)}</div><div class="slot-f">lands as <code>${esc(src)}</code></div></div>`; };
  if (Array.isArray(media) && !media.includes(src)) { slot(); return { step() {} }; }
  if (vid) {
    const webm = src.replace(/\.mp4$/i, '.webm'), both = webm !== src && Array.isArray(media) && media.includes(webm);
    el.innerHTML = `<video class="shot-v" controls preload="metadata" playsinline>${both ? `<source src="${esc(webm)}" type="video/webm">` : ''}<source src="${esc(src)}" type="video/mp4"></video>`;
    const v = el.querySelector('video'), srcs = [...v.querySelectorAll('source')];
    let failed = 0;
    srcs.forEach((sc) => sc.addEventListener('error', () => { if (++failed === srcs.length) slot(); }));
    ['click', 'keydown', 'touchstart', 'touchend'].forEach((ev) => v.addEventListener(ev, stop));
    return { step() {} };
  }
  const crop = (el.dataset.crop || '').split(',').map(Number);
  if (crop.length !== 4 || crop.some(isNaN)) {
    el.innerHTML = `<img class="shot-i" src="${esc(src)}" alt="${esc(label)}">`;
    el.querySelector('img').addEventListener('error', slot);
    return { step() {} };
  }
  const [x, y, w, h] = crop;
  el.innerHTML = `<div class="shot-c"><div class="shot-cw" role="img" aria-label="${esc(label)}"></div></div>`;
  const box = el.querySelector('.shot-cw'), img = new Image();
  const lay = () => {
    const W = el.clientWidth, H = el.clientHeight; if (!W || !H || !img.naturalWidth) return;
    const s = Math.min(W / w, H / h);
    Object.assign(box.style, { width: `${w * s}px`, height: `${h * s}px`, backgroundImage: `url("${src}")`,
      backgroundSize: `${img.naturalWidth * s}px auto`, backgroundPosition: `${-x * s}px ${-y * s}px` });
  };
  img.onload = lay; img.onerror = slot; img.src = src;
  return { step() { lay(); } };
};

/* ======================= 1 · how the model picks a tool: the recorded request and the reply =======================
   Model call 1 of run "single": what our code sent (the messages and the tools, exactly) and what came back. */
FIGS.pick = (el) => {
  const X = get('exposed'); if (!X) return need(el, 'The recorded request of call 1 (exposed).');
  const sys = X.messages.find((m) => m.role === 'system'), user = X.messages.find((m) => m.role === 'user');
  const tools = X.tools.map((t) => t.function);
  const tc = X.reply.tool_calls[0];
  const def = (f, on) => `<div class="pk-def${on ? ' on' : ''}" data-tool="${esc(f.name)}"><span class="pk-n">${esc(f.name)}</span><span class="pk-d">${esc(f.description)}</span><span class="pk-p">parameters: ${esc(Object.entries(f.parameters.properties).map(([k, v]) => `${k} (${v.type})`).join(', '))}</span></div>`;
  el.innerHTML = `<div class="pk">
    <div class="pk-in"><span class="rt-h">What our code sent · model call 1 · ${fmt(X.prompt_tokens)} tokens</span>
      <div class="pk-m sys"><b>system</b><span>${esc(sys.content.split('\n')[0].slice(0, 118))}… <i>(${fmt(sys.content.length)} characters)</i></span></div>
      <div class="pk-m usr" data-k="1"><b>user</b><span>“${esc(user.content)}”</span></div>
      <div class="pk-tl" data-k="2"><b>tools</b>${tools.map((f) => def(f, false)).join('')}</div>
    </div>
    <div class="pk-mid" data-k="3"><span class="pk-arr">→</span><p>The model reads it all as text. Emma gave a code and asked <b>how many</b>; that is what <code>check_stock</code>’s description promises. <code>find_item</code> is for finding a code, and she has one.</p></div>
    <div class="pk-out" data-k="4"><span class="rt-h">What the model wrote back</span><pre class="pk-j">${jc({ content: X.reply.content, tool_calls: [{ name: tc.name, arguments: tc.arguments }] })}</pre>
      <p class="pk-say">No answer: <code>content</code> is <code>null</code>. A tool call instead, a name and arguments.</p></div>
    <div class="pk-run" data-k="5"><b>Then our code</b> checks the arguments, runs <code>check_stock</code> in Emma’s session, and sends the result back. Model call 2 writes the answer.</div>
  </div>`;
  return { step(k) { reveal(el, k); el.querySelectorAll('.pk-def').forEach((d) => d.classList.toggle('on', k >= 3 && d.dataset.tool === tc.name)); } };
};

/* ======================= 3 · tool.json: what reaches the model, and what never does ======================= */
FIGS.sentdef = (el) => {
  const X = get('exposed'); if (!X) return need(el, 'exposed.tool_json');
  const T = X.tool_json, sent = X.sent_keys, sentFn = X.tools[0].function;
  const why = { title: 'for people: the UI', category: 'for people: the tools page', writes: 'for our code and the host', version: 'for release notes',
    services: 'for us: what tool.py calls', output_schema: 'for code that checks results', example: 'for tests and docs', annotations: 'for the host: read-only, safe to repeat', policy: 'for our code: timeouts, retries' };
  const short = (k, v) => {
    if (k === 'input_schema') return `{ item_code: string, required }`;
    if (k === 'output_schema') return `{ ${Object.keys(v.properties).length} fields }`;
    if (k === 'annotations') return `{ readOnlyHint: ${v.readOnlyHint}, … }`;
    if (k === 'policy') return `{ timeout ${v.ledgerline_reply_timeout_s} s, retries }`;
    if (Array.isArray(v)) return `[${v.map((x) => `"${x}"`).join(', ')}]`;
    if (typeof v === 'object') return cj(v);
    return cj(v).length > 58 ? cj(v).slice(0, 56) + '…"' : cj(v);
  };
  el.innerHTML = `<div class="sd">
    <div class="sd-l"><span class="rt-h">toolbox/check_stock/tool.json · ${X.tool_json_keys.length} keys</span>
      ${X.tool_json_keys.map((k) => `<div class="sd-r ${sent[k] ? 'y' : 'n'}"><code class="sd-k">"${esc(k)}"</code><span class="sd-v">${esc(short(k, T[k]))}</span>${sent[k] ? `<span class="sd-t y" data-k="1">sent${sent[k] !== k ? ` as <b>${esc(sent[k])}</b>` : ''}</span>` : `<span class="sd-t n" data-k="2">${esc(why[k] || 'not sent')}</span>`}</div>`).join('')}
      <div class="sd-r py" data-k="3"><code class="sd-k">tool.py</code><span class="sd-v">${X.tool_py_lines} lines of Python</span><span class="sd-t n">never sent: it runs in our code</span></div>
    </div>
    <div class="sd-x" data-k="1"><span class="rt-h">What the model received · the recorded request, model call 1</span><pre class="pk-j">${jc({ name: sentFn.name, description: sentFn.description, parameters: sentFn.parameters })}</pre>
      <p class="sd-say" data-k="2">Three fields. <b>${X.not_sent.length} of the ${X.tool_json_keys.length} keys stay behind</b>: they are for people, for the host and for our own code.</p></div>
  </div>`;
  return { step(k) { reveal(el, k); el.classList.toggle('sd-on', k >= 1); el.classList.toggle('sd-off', k >= 2); } };
};

/* ======================= 2 · who relies on the output schema: code, not the model ======================= */
FIGS.readers = (el) => {
  const A = get('anatomy'), X = get('exposed'), R = get('readers'), F = get('ours.single.final'), P = get('prod.criteria.0.after');
  if (!A || !X || !R) return need(el, 'anatomy, exposed, readers');
  const S = JSON.parse(A.tool_json).output_schema.properties, res = A.tool_result;
  const typeOf = (v) => (Array.isArray(v) ? 'array' : Number.isInteger(v) ? 'integer' : typeof v);
  const rows = Object.keys(res).map((k) => {
    const v = res[k], promised = S[k] && S[k].type;
    const val = Array.isArray(v) ? `[ ${v.length} warehouses ]` : cj(v);
    return `<div class="rd-l${promised ? '' : ' x'}" data-f="${esc(k)}"><code>"${esc(k)}"</code>: <span>${esc(val)}</span>${promised ? `<i class="rd-ok" data-k="1">${esc(promised)} ✓</i>` : ''}</div>`;
  }).join('');
  const sentKeys = Object.keys(X.tools[0].function).join(', ');
  el.innerHTML = `<div class="rd">
    <div class="rd-res"><span class="rt-h">check_stock’s real result for BAT-500</span>${rows}
      <div class="rd-foot" data-k="1">✓ = the type the output schema promised, checked</div></div>
    <div class="rd-cards">
      <div class="rd-c" data-k="1"><span class="rd-n">1 · The host’s check</span><p>Before anyone uses a result, code compares every field with its promised type. Ours checked <b>${fmt(P.ok_results_checked_in_fuzzing)}</b> real results: <b>${P.output_violations_in_fuzzing}</b> broke the promise.</p></div>
      <div class="rd-c" data-k="2"><span class="rd-n">2 · Our own code</span><p>The Workflow Studio’s stock trigger trusts one field, without guessing:</p><pre class="rd-code"><i>${R.studio_line_no}</i>${esc(R.studio_lines[5])}</pre><small>${esc(R.studio_path)}</small></div>
      <div class="rd-c m" data-k="3"><span class="rd-n">3 · The model? It never sees the schema</span><p>Our recorded request sent check_stock’s <code>${esc(sentKeys)}</code>. No output schema. The model read only the JSON on the left, and wrote: “${esc((F.text.match(/[^.]*11 days[^.]*\./) || [F.text])[0].trim())}”</p></div>
    </div>
    <div class="rd-say" data-k="4">The output schema is a promise <b>to code</b>. The model gets the result alone, so name each field so it needs no explanation.</div>
  </div>`;
  return { step(k) { reveal(el, k); el.querySelectorAll('.rd-l').forEach((l) => l.classList.toggle('hot', (k === 2 && l.dataset.f === 'below_reorder') || (k === 3 && l.dataset.f === 'cover_days'))); } };
};

/* ======================= 10 · LLM usability: one golden task on five hosts, as recorded ======================= */
FIGS.hosttask = (el) => {
  const T = get('hosts.release'), TB = get('toolbox'), H = get('hosts'); if (!T || !TB) return need(el, 'hosts.release');
  const d = (n) => (TB.find((t) => t.name === n) || {}).description || '';
  const want = T.accepted[0][0];
  const short = { 'our harness': 'our harness', Gemini: 'Gemini API', OpenAI: 'OpenAI API', 'Claude (API)': 'Claude API', 'Claude Code': 'Claude Code' };
  const model = (m) => m.replace(/^openrouter:/, '').replace(/ \(.*$/, '');
  const cc = T.claude_code, said = (cc.first.find((f) => f.text) || {}).text;
  el.innerHTML = `<div class="ht">
    <div class="ht-in">
      <span class="rt-h">Every host got the same three things</span>
      <div class="ht-b"><b>1 · The task</b><span>“${esc(T.message)}”</span></div>
      <div class="ht-b"><b>2 · The same ${H.tool_definitions} tool definitions</b><span>from our MCP server’s <code>tools/list</code>, sent in each API’s own tool format. Two of them:</span>
        <div class="ht-def"><code>${esc(want)}</code> ${esc(d(want))}</div><div class="ht-def"><code>order_status</code> ${esc(d('order_status'))}</div></div>
      <div class="ht-b"><b>3 · A prompt</b><span>ours; a generic one for the three APIs; Claude Code’s own.</span></div>
    </div>
    <div class="ht-out" data-k="1"><span class="rt-h">Each host’s first tool call, as logged · the right one is <code>${esc(want)}</code></span>
      <table class="ht-t"><tr><th>Host</th><th>Model</th><th>First call</th><th></th><th class="n">All 30 tasks</th></tr>
      ${T.hosts.map((h, i) => { const c = h.calls[0] || {}; return `<tr class="${h.pass ? '' : 'miss'}" data-k="${i < 3 ? 1 : 2}"><td><b>${esc(short[h.host] || h.host)}</b></td><td class="mo">${esc(model(h.model))}</td><td><code>${esc(c.name || 'no call')}(${esc(Object.entries(c.arguments || {}).map(([k, v]) => `${k}: "${v}"`).join(', '))})</code></td><td>${h.pass ? '<span class="ok">✓</span>' : '<span class="no">✕</span>'}</td><td class="n">${h.passed} / 30</td></tr>`; }).join('')}
      </table>
      <div class="ht-cc" data-k="3"><span class="rd-n">Claude Code ${esc(cc.version)}, its own words before the call</span>“${esc(said || '')}” <small>${esc(cc.source.replace('experiments/', ''))}</small></div>
    </div>
  </div>`;
  return { step(k) { reveal(el, k); } };
};
})();
