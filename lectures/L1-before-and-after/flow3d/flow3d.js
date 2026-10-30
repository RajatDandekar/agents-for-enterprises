/* flow3d.js — "How it works, underneath": one real Ask Northbridge request, in 3D.
   Agentic Systems Engineering, Lecture 1 (Vizuara, Dr. Rajat Dandekar).

   import { mountFlow3D } from './flow3d/flow3d.js';
   const f = mountFlow3D(el, { trace, mode: 'deck' | 'standalone' });
   f.go(k, instant)   // show stage k (0 = overview). instant=true jumps to its end state, false plays it
   f.next(); f.prev(); f.replay(); f.autoplay(true|false); f.seek(k, seconds); f.count; f.stages

   Every label is read from trace.json, recorded by capture_trace.py from the real L1 assistant on Modal.
   Needs an import map for "three" and "three/addons/" (three@0.160.0). Without WebGL it shows poster.png. */
import * as THREE from 'three';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const HERE = new URL('./', import.meta.url);
const C = { sky: 0x3c90ff, skyDeep: 0x0b57d0, ember: 0xc4511f, green: 0x1e8e5a, ink: 0x121317 };

/* ------------------------------------------------------------------ small helpers */
const clamp01 = (x) => Math.max(0, Math.min(1, x));
const seg = (t, a, b) => clamp01((t - a) / (b - a));
const eio = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const eo = (x) => 1 - Math.pow(1 - x, 3);
const lerp = (a, b, t) => a + (b - a) * t;
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const fmt = (n) => (typeof n === 'number' ? n.toLocaleString('en-GB') : String(n));
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const secs = (s) => (s >= 10 ? s.toFixed(1) : s.toFixed(2)) + ' s';
const msf = (ms) => (ms >= 1000 ? (ms / 1000).toFixed(1) + ' s' : (ms >= 10 ? ms.toFixed(0) : ms.toFixed(1)) + ' ms');
const money = (v) => '£' + Number(v).toLocaleString('en-GB', { maximumFractionDigits: 0 });

/* one-line JSON, cut to n characters (never changed, only shortened) */
function j1(v, n = 64) {
  let s = JSON.stringify(v);
  if (s === undefined) s = String(v);
  s = s.replace(/":/g, '": ').replace(/,"/g, ', "');
  return s.length > n ? s.slice(0, n - 1) + '…' : s;
}
function jsonSpan(s) { // colour a JSON string
  return esc(s).replace(/(&quot;[^&]*?&quot;)(\s*:)?|\b(true|false|null)\b|(-?\d[\d.]*)/g, (m, str, colon, kw, num) => {
    if (str) return colon ? `<span class="jk">${str}</span>${colon}` : `<span class="js">${str}</span>`;
    if (kw) return `<span class="${kw === 'true' ? 'jt' : kw === 'false' ? 'jf' : 'jk'}">${kw}</span>`;
    return `<span class="jn">${num}</span>`;
  });
}
/* a short faithful view of a JSON object: top-level keys one per line, nested values inline and cut */
function jsonBlock(obj, { keys = null, max = 8, width = 52, expand = [] } = {}) {
  if (obj === null || typeof obj !== 'object' || Array.isArray(obj)) return jsonSpan(j1(obj, width));
  const ks = (keys || Object.keys(obj)).filter((k) => k in obj);
  const lines = ks.slice(0, max).map((k) => {
    let v = obj[k];
    if (expand.includes(k) && v && typeof v === 'object' && !Array.isArray(v)) {
      const inner = Object.keys(v).map((kk) => '    ' + jsonSpan(`"${kk}": ` + j1(v[kk], width - kk.length)));
      return '  ' + jsonSpan(`"${k}": `) + '{\n' + inner.join(',\n') + '\n  }';
    }
    if (Array.isArray(v) && v.length > 1) v = [v[0], `+${v.length - 1} more`];
    return '  ' + jsonSpan(`"${k}": ` + j1(v, width + 8 - k.length));
  });
  if (ks.length > max) lines.push(`  <span class="jk">… ${ks.length - max} more</span>`);
  return '{\n' + lines.join(',\n') + '\n}';
}
function md(s) { // the model's reply: **bold**, `code`, "* " bullets, paragraphs
  const inl = (x) => esc(x).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/`(.+?)`/g, '<code>$1</code>');
  const out = []; let list = null;
  for (const raw of String(s || '').split('\n')) {
    const l = raw.trim();
    if (/^[*-]\s+/.test(l)) { if (!list) { list = []; out.push(list); } list.push(inl(l.replace(/^[*-]\s+/, ''))); }
    else if (l) { list = null; out.push(`<p>${inl(l)}</p>`); }
  }
  return out.map((x) => (Array.isArray(x) ? `<ul>${x.map((i) => `<li>${i}</li>`).join('')}</ul>` : x)).join('');
}
function hasWebGL() {
  try { const c = document.createElement('canvas'); return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl'))); }
  catch (e) { return false; }
}

/* ------------------------------------------------------------------ styles */
const CSS = `
.f3d{position:relative;overflow:hidden;--u:1;--f3d-font:"Google Sans Flex","Google Sans","Segoe UI",Roboto,Arial,sans-serif;
  --f3d-mono:"Google Sans Code","IBM Plex Mono",ui-monospace,Menlo,monospace;font-family:var(--f3d-font);color:#121317;
  background:radial-gradient(52% 60% at 92% 0%,rgba(125,184,255,.30) 0%,rgba(125,184,255,0) 70%),
             radial-gradient(40% 50% at 22% 100%,rgba(188,220,255,.32) 0%,rgba(188,220,255,0) 70%),
             linear-gradient(180deg,#eef5ff 0%,#f9fbff 55%,#ffffff 100%);-webkit-font-smoothing:antialiased;user-select:none}
.f3d canvas{display:block;position:absolute;inset:0}
.f3d-vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(120% 90% at 60% 45%,rgba(255,255,255,0) 62%,rgba(214,228,246,.38) 100%)}
.f3d-labels{position:absolute;inset:0;pointer-events:none;z-index:1;isolation:isolate}
.f3d-rail,.f3d-hud,.f3d-foot,.f3d-fix{z-index:3}
.f3d-l{transition:none;will-change:opacity}
.f3d-tag{display:inline-flex;align-items:center;gap:calc(9px*var(--u));padding:calc(8px*var(--u)) calc(15px*var(--u));border-radius:999px;
  background:rgba(255,255,255,.86);border:1px solid rgba(18,19,23,.10);box-shadow:0 6px 20px rgba(18,19,23,.08);
  font:520 calc(18px*var(--u))/1.1 var(--f3d-font);white-space:nowrap;color:#121317;letter-spacing:-.005em}
.f3d-tag i{width:calc(10px*var(--u));height:calc(10px*var(--u));border-radius:50%;background:#3c90ff;flex:none}
.f3d-tag.ember i{background:#c4511f}.f3d-tag.green i{background:#1e8e5a}
.f3d-tag small{font:400 calc(16px*var(--u))/1.1 var(--f3d-font);color:#5f636b}
.f3d-tag.on{background:#fff;border-color:rgba(60,144,255,.55);box-shadow:0 0 0 4px rgba(60,144,255,.14),0 10px 26px rgba(11,87,208,.14)}
.f3d-tag.ember.on{border-color:rgba(196,81,31,.55);box-shadow:0 0 0 4px rgba(196,81,31,.13),0 10px 26px rgba(196,81,31,.14)}
.f3d-note{background:rgba(255,255,255,.95);border-radius:calc(16px*var(--u));padding:calc(11px*var(--u)) calc(14px*var(--u)) calc(12px*var(--u));
  box-shadow:0 12px 34px rgba(18,19,23,.13),0 1px 2px rgba(18,19,23,.06);border:1px solid rgba(18,19,23,.08);
  font:400 calc(16px*var(--u))/1.4 var(--f3d-font);width:max-content;max-width:calc(560px*var(--u));color:#121317}
.f3d-note .k{display:flex;align-items:center;gap:calc(8px*var(--u));font:650 calc(14px*var(--u))/1.2 var(--f3d-font);letter-spacing:.08em;text-transform:uppercase;color:#0b57d0;margin-bottom:calc(5px*var(--u))}
.f3d-note .k b{font-weight:650;color:#6b6e76;letter-spacing:.04em;text-transform:none;font-size:calc(14px*var(--u))}
.f3d-note.ember{border-left:calc(4px*var(--u)) solid #c4511f}.f3d-note.ember .k{color:#c4511f}
.f3d-note.green{border-left:calc(4px*var(--u)) solid #1e8e5a}.f3d-note.green .k{color:#1e8e5a}
.f3d-note.sky{border-left:calc(4px*var(--u)) solid #3c90ff}
.f3d-note pre{font:500 calc(15px*var(--u))/1.48 var(--f3d-mono);margin:0;white-space:pre;color:#121317;letter-spacing:-.01em}
.f3d-note .t{font:450 calc(16px*var(--u))/1.4 var(--f3d-font);color:#45474d;max-width:calc(430px*var(--u));white-space:normal}
.f3d-note .row{display:grid;grid-template-columns:auto auto 1fr;gap:calc(4px*var(--u)) calc(12px*var(--u));align-items:baseline;font:500 calc(15px*var(--u))/1.42 var(--f3d-mono)}
.f3d-note .row .ok{color:#1e8e5a;font-family:var(--f3d-font);font-weight:650}
.f3d-note .row .bad{color:#c4511f;font-family:var(--f3d-font);font-weight:650}
.f3d-note .row .dim{color:#6b6e76}
.f3d-note .cnt{font:600 calc(28px*var(--u))/1 var(--f3d-font);letter-spacing:-.02em;color:#0b57d0}
.jk{color:#5f636b}.js{color:#0b57d0}.jn{color:#1e8e5a}.jt{color:#1e8e5a}.jf{color:#c4511f}
.f3d-card{font:560 calc(17px*var(--u))/1.15 var(--f3d-mono);color:#121317;text-align:center;letter-spacing:-.02em;white-space:normal;max-width:calc(178px*var(--u));overflow-wrap:normal}
.f3d-card small{display:block;font:450 calc(14px*var(--u))/1.2 var(--f3d-font);color:#6b6e76;letter-spacing:.01em;margin-top:calc(3px*var(--u))}
.f3d-card.on{color:#0b57d0}
.f3d-card.dim{opacity:.38}
/* rail: the chat */
.f3d-rail{position:absolute;left:calc(26px*var(--u));top:calc(26px*var(--u));bottom:calc(26px*var(--u));width:calc(400px*var(--u));
  border-radius:calc(26px*var(--u));background:rgba(255,255,255,.72);border:1px solid rgba(255,255,255,.95);
  box-shadow:0 1px 2px rgba(18,19,23,.05),0 18px 48px rgba(18,19,23,.10);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);
  display:flex;flex-direction:column;overflow:hidden}
.f3d-rail header{padding:calc(18px*var(--u)) calc(20px*var(--u)) calc(14px*var(--u));border-bottom:1px solid rgba(18,19,23,.07)}
.f3d-rail header b{display:flex;align-items:center;gap:calc(9px*var(--u));font:560 calc(20px*var(--u))/1.2 var(--f3d-font);letter-spacing:-.01em}
.f3d-rail header b i{width:calc(11px*var(--u));height:calc(11px*var(--u));border-radius:50%;background:#3c90ff;box-shadow:0 0 0 4px rgba(60,144,255,.16)}
.f3d-rail header span{display:block;font:400 calc(15px*var(--u))/1.35 var(--f3d-font);color:#5f636b;margin-top:calc(4px*var(--u))}
.f3d-msgs{flex:1;display:flex;flex-direction:column;justify-content:flex-end;gap:calc(12px*var(--u));padding:calc(16px*var(--u)) calc(16px*var(--u));overflow:hidden}
.f3d-b{max-width:88%;border-radius:calc(18px*var(--u));padding:calc(11px*var(--u)) calc(14px*var(--u));font:400 calc(16.5px*var(--u))/1.42 var(--f3d-font);
  animation:none;box-shadow:0 1px 2px rgba(18,19,23,.05)}
.f3d-b p{margin:0 0 .35em}.f3d-b p:last-child{margin:0}.f3d-b ul{margin:.1em 0 .35em;padding-left:1.1em}.f3d-b li{margin:.1em 0}
.f3d-b code{font:500 .9em var(--f3d-mono)}
.f3d-b.emma{align-self:flex-end;background:#0b57d0;color:#fff;border-bottom-right-radius:calc(6px*var(--u))}
.f3d-b.bot{align-self:flex-start;background:#fff;border:1px solid rgba(18,19,23,.08);border-bottom-left-radius:calc(6px*var(--u))}
.f3d-who{font:600 calc(14px*var(--u))/1 var(--f3d-font);letter-spacing:.06em;text-transform:uppercase;color:#6b6e76;margin:0 calc(4px*var(--u)) calc(-6px*var(--u))}
.f3d-who.emma{align-self:flex-end}
.f3d-uses{align-self:flex-start;display:flex;flex-wrap:wrap;gap:calc(6px*var(--u));max-width:96%;margin-top:calc(-4px*var(--u))}
.f3d-uses span{font:500 calc(14px*var(--u))/1 var(--f3d-mono);padding:calc(5px*var(--u)) calc(8px*var(--u));border-radius:999px;background:#e6f1ff;color:#0b57d0}
.f3d-uses span.w{background:#e8f7f0;color:#1e8e5a}
.f3d-rcpt{align-self:flex-start;max-width:92%;border-radius:calc(14px*var(--u));background:#e8f7f0;color:#121317;padding:calc(9px*var(--u)) calc(12px*var(--u));
  font:400 calc(14px*var(--u))/1.4 var(--f3d-font);margin-top:calc(-4px*var(--u))}
.f3d-rcpt b{display:block;font:650 calc(14px*var(--u))/1.3 var(--f3d-font);letter-spacing:.08em;text-transform:uppercase;color:#1e8e5a;margin-bottom:2px}
.f3d-rcpt code{font:550 calc(14px*var(--u)) var(--f3d-mono)}
.f3d-empty{margin:auto 8px;text-align:center;font:400 calc(15px*var(--u))/1.45 var(--f3d-font);color:#8a8d94}
.f3d-typing{align-self:flex-start;display:flex;gap:5px;padding:calc(12px*var(--u)) calc(14px*var(--u));background:#fff;border-radius:calc(16px*var(--u));border:1px solid rgba(18,19,23,.08)}
.f3d-typing i{width:7px;height:7px;border-radius:50%;background:#9cc4ff}
.f3d-input{margin:0 calc(14px*var(--u)) calc(14px*var(--u));border-radius:999px;border:1px solid rgba(18,19,23,.12);background:#fff;
  padding:calc(11px*var(--u)) calc(16px*var(--u));font:400 calc(15px*var(--u))/1.2 var(--f3d-font);color:#8a8d94}
/* hud */
.f3d-hud{position:absolute;left:calc(458px*var(--u));top:calc(30px*var(--u));right:calc(40px*var(--u));pointer-events:none}
.f3d-kick{display:flex;align-items:center;gap:calc(12px*var(--u));font:500 calc(16px*var(--u))/1.2 var(--f3d-font);color:#45474d}
.f3d-pill{display:inline-flex;align-items:center;height:calc(30px*var(--u));padding:0 calc(12px*var(--u));border-radius:999px;background:rgba(255,255,255,.7);
  border:1px solid rgba(18,19,23,.12);font:560 calc(14.5px*var(--u))/1 var(--f3d-font);color:#121317}
.f3d-hud h2{margin:calc(12px*var(--u)) 0 calc(6px*var(--u));font:470 calc(38px*var(--u))/1.08 var(--f3d-font);letter-spacing:-.025em;color:#121317;max-width:calc(1100px*var(--u))}
.f3d-hud p{margin:0;font:400 calc(20px*var(--u))/1.42 var(--f3d-font);color:#45474d;max-width:calc(980px*var(--u))}
.f3d-hud p b{color:#121317;font-weight:560}.f3d-hud p code{font:500 .88em var(--f3d-mono);color:#0b57d0}
.f3d-chips{display:flex;flex-wrap:wrap;gap:calc(8px*var(--u));margin-top:calc(12px*var(--u))}
.f3d-chips span{display:inline-flex;align-items:baseline;gap:calc(6px*var(--u));padding:calc(7px*var(--u)) calc(12px*var(--u));border-radius:999px;background:rgba(255,255,255,.82);
  border:1px solid rgba(18,19,23,.09);font:400 calc(15px*var(--u))/1 var(--f3d-font);color:#5f636b}
.f3d-chips span b{font:600 calc(17px*var(--u))/1 var(--f3d-font);color:#0b57d0;letter-spacing:-.01em}
.f3d-chips span.e b{color:#c4511f}.f3d-chips span.g b{color:#1e8e5a}
.f3d-foot{position:absolute;left:calc(458px*var(--u));right:calc(30px*var(--u));bottom:calc(24px*var(--u));display:flex;align-items:flex-end;gap:calc(16px*var(--u));pointer-events:none}
.f3d-prov{flex:1;font:400 calc(15px*var(--u))/1.45 var(--f3d-font);color:#6b6e76}
.f3d-prov b{font-weight:560;color:#45474d}
.f3d code{font-size:.92em}.f3d-prov code{font-size:1em}
.f3d-leg{display:flex;gap:calc(14px*var(--u));margin-bottom:calc(6px*var(--u));font:500 calc(14px*var(--u))/1 var(--f3d-font);color:#45474d}
.f3d-leg span{display:inline-flex;align-items:center;gap:calc(6px*var(--u))}
.f3d-leg i{width:calc(10px*var(--u));height:calc(10px*var(--u));border-radius:50%;background:#3c90ff}
.f3d-ctl{pointer-events:auto;display:flex;flex-direction:column;align-items:flex-end;gap:calc(10px*var(--u))}
.f3d-btns{display:flex;gap:calc(6px*var(--u));padding:calc(6px*var(--u));border-radius:999px;background:rgba(255,255,255,.78);border:1px solid rgba(18,19,23,.10);
  box-shadow:0 8px 24px rgba(18,19,23,.08);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px)}
.f3d-btns button{all:unset;cursor:pointer;display:inline-flex;align-items:center;gap:calc(7px*var(--u));height:calc(38px*var(--u));padding:0 calc(14px*var(--u));border-radius:999px;
  font:540 calc(15px*var(--u))/1 var(--f3d-font);color:#121317}
.f3d-btns button:hover{background:#e6f1ff;color:#0b57d0}
.f3d-btns button.on{background:#0b57d0;color:#fff}
.f3d-btns button.b-voice.on{background:#e6f1ff;color:#0b57d0}
.f3d-btns button[hidden]{display:none}
.f3d-speak{display:inline-flex;align-items:center;gap:calc(6px*var(--u));color:#0b57d0;font:560 calc(14px*var(--u))/1 var(--f3d-font)}
.f3d-speak i{width:calc(4px*var(--u));height:calc(14px*var(--u));border-radius:2px;background:#3c90ff;animation:f3dbar 1s ease-in-out infinite}
.f3d-speak i:nth-child(2){animation-delay:.15s}.f3d-speak i:nth-child(3){animation-delay:.3s}
@keyframes f3dbar{0%,100%{transform:scaleY(.35)}50%{transform:scaleY(1)}}
.f3d-speak.paused i{animation:none;transform:scaleY(.35)}
.f3d-speak[hidden]{display:none}
.f3d-btns svg{width:calc(16px*var(--u));height:calc(16px*var(--u))}
.f3d-prog{display:flex;gap:calc(4px*var(--u))}
.f3d-prog i{width:calc(18px*var(--u));height:calc(5px*var(--u));border-radius:3px;background:rgba(18,19,23,.12);cursor:pointer}
.f3d-prog i.done{background:#9cc4ff}.f3d-prog i.cur{background:#0b57d0}
.f3d.deck .f3d-hud{top:calc(88px*var(--u))}
.f3d.deck .b-prev,.f3d.deck .b-next,.f3d.deck .f3d-prog{display:none}
.f3d.deck .f3d-foot{bottom:calc(58px*var(--u))}.f3d.deck .f3d-rail{bottom:calc(58px*var(--u))}
.f3d.deck .f3d-card{font-size:calc(15px*var(--u));max-width:calc(150px*var(--u))}.f3d.deck .f3d-card small{font-size:calc(14px*var(--u))}
.f3d.deck .f3d-rail{top:calc(88px*var(--u))}
.f3d-fix{position:absolute;right:calc(30px*var(--u));top:calc(28px*var(--u));font:650 calc(14px*var(--u))/1 var(--f3d-font);letter-spacing:.08em;color:#c4511f;text-transform:uppercase}
.f3d-poster{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
`;
function injectCSS() {
  if (document.getElementById('flow3d-css')) return;
  const s = document.createElement('style'); s.id = 'flow3d-css'; s.textContent = CSS; document.head.appendChild(s);
}
const ICON = {
  narr: '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M3.5 2.8v10.4L11 8z"/><rect x="12" y="4" width="1.6" height="8" rx=".8"/></svg>',
  voiceOn: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 6h2.2L8 3.2v9.6L4.7 10H2.5z" fill="currentColor"/><path d="M10.6 5.6a3.4 3.4 0 0 1 0 4.8M12.4 3.8a6 6 0 0 1 0 8.4"/></svg>',
  voiceOff: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 6h2.2L8 3.2v9.6L4.7 10H2.5z" fill="currentColor"/><path d="m10.5 6 3.5 4M14 6l-3.5 4"/></svg>',
  prev: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 3 5 8l5 5"/></svg>',
  next: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m6 3 5 5-5 5"/></svg>',
  play: '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M4.5 2.8v10.4L13 8z"/></svg>',
  pause: '<svg viewBox="0 0 16 16" fill="currentColor"><rect x="3.5" y="2.8" width="3" height="10.4" rx="1"/><rect x="9.5" y="2.8" width="3" height="10.4" rx="1"/></svg>',
  replay: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2.8 8a5.2 5.2 0 1 0 1.6-3.8"/><path d="M2.6 2.6v3h3"/></svg>',
};

/* ------------------------------------------------------------------ the story, built from the trace */
const isCommit = (e) => e && e.guard && e.guard.writes && e.args && e.args.confirm === true;
function splitSteps(turn) {
  const steps = []; let cur = null;
  for (const e of turn.events) {
    if (e.kind === 'llm') { cur = { llm: e, tools: [] }; steps.push(cur); } else if (cur) cur.tools.push(e);
  }
  return steps;
}
function buildStages(T) {
  const S = [{ kind: 'overview' }];
  T.turns.forEach((turn, ti) => {
    const steps = splitSteps(turn);
    S.push({ kind: 'arrive', ti, text: turn.user, llm: steps[0] && steps[0].llm });
    if (ti === 0) S.push({ kind: 'assemble', ti, llm: steps[0].llm });
    let cyclesThisTurn = 0;
    steps.forEach((st, si) => {
      if (!st.tools.length) {
        const prev = steps[si - 1];
        const commit = prev && prev.tools.find(isCommit);
        S.push({ kind: commit ? 'receipt' : 'reply', ti, llm: st.llm, text: turn.reply, commit, turn,
                 used: turn.events.filter((e) => e.kind === 'tool') });
        return;
      }
      if (st.tools.some(isCommit)) { S.push({ kind: 'write', ti, steps: [st], next: steps[si + 1] }); return; }
      if (ti === 0 && si === 0 && st.tools.length === 1) {
        const c = st.tools[0], nx = steps[si + 1] && steps[si + 1].llm;
        S.push({ kind: 'decide', ti, llm: st.llm, call: c });
        S.push({ kind: 'guard', ti, llm: st.llm, call: c });
        S.push({ kind: c.services.length ? 'erp' : 'docs', ti, call: c });
        S.push({ kind: 'result', ti, call: c, next: nx });
        return;
      }
      // later turns: read-only steps after the turn's first are shown two to a stage
      const last = S[S.length - 1];
      const readOnly = st.tools.every((t) => !t.guard.writes);
      if (ti > 0 && cyclesThisTurn > 0 && readOnly && last.kind === 'cycle' && last.ti === ti && last.steps.length === 1 && last.mergeable) {
        last.steps.push({ ...st, next: steps[si + 1] && steps[si + 1].llm }); return;
      }
      cyclesThisTurn++;
      S.push({ kind: 'cycle', ti, steps: [{ ...st, next: steps[si + 1] && steps[si + 1].llm }], mergeable: ti > 0 && cyclesThisTurn > 1 && readOnly });
    });
  });
  // chat history the model holds after each stage (messages after the system prompt), and rail messages
  let hist = 0, ctx = 0;
  const rail = [];
  S.forEach((s, k) => {
    s.histBefore = hist; s.ctxBefore = ctx;
    if (s.kind === 'arrive') { hist += 1; ctx = s.llm ? s.llm.tokens_in : ctx; rail.push({ who: 'emma', text: s.text, k, t: 0.5 }); }
    if (s.kind === 'result') { hist += 2; ctx = s.next ? s.next.tokens_in : ctx; }
    if (s.kind === 'cycle' || s.kind === 'write') for (const st of s.steps) { hist += 1 + st.tools.length; ctx = (st.next || s.next?.llm || {}).tokens_in || ctx; }
    if (s.kind === 'write' && s.next) ctx = s.next.llm.tokens_in;
    if (s.kind === 'reply' || s.kind === 'receipt') { hist += 1; rail.push({ who: 'bot', text: s.text, k, t: s.kind === 'receipt' ? 6.5 : 3.9, used: s.used, commit: s.commit }); }
    s.histAfter = hist; s.ctxAfter = ctx;
  });
  return { S, rail };
}

/* ------------------------------------------------------------------ mount */
export function mountFlow3D(el, opts = {}) {
  injectCSS();
  const T = opts.trace || window.FLOW3D_TRACE;
  const mode = opts.mode || 'standalone';
  el.classList.add('f3d'); if (mode === 'deck') el.classList.add('deck');
  if (getComputedStyle(el).position === 'static') el.style.position = 'relative';
  if (!T || !hasWebGL() || opts.forcePoster) {
    el.innerHTML = `<img class="f3d-poster" src="${new URL('poster.png', HERE)}" alt="How a request flows through Ask Northbridge: chat, harness, LLM, guard, MCP, toolbox, Ledgerline ERP">`;
    return { go() {}, next() {}, prev() {}, replay() {}, autoplay() {}, seek() {}, count: 1, stages: [], destroy() {}, poster: true };
  }
  const { S, rail } = buildStages(T);
  const tools = T.tools;
  const toolIx = Object.fromEntries(tools.map((t, i) => [t.name, i]));
  const still = !!opts.still;

  /* ---------- DOM ---------- */
  el.innerHTML = `
    <div class="f3d-vig"></div>
    <aside class="f3d-rail"><header><b><i></i>Ask Northbridge</b><span>${esc(T.meta.user_name || 'Emma Clarke')} · purchase executive · Northbridge Cycles</span></header>
      <div class="f3d-msgs"></div><div class="f3d-input">Message Ask Northbridge</div></aside>
    <div class="f3d-hud"><div class="f3d-kick"><span class="f3d-pill"></span><span class="f3d-turn"></span><span class="f3d-speak" hidden><i></i><i></i><i></i><span>Narration</span></span></div><h2></h2><p></p><div class="f3d-chips"></div></div>
    <div class="f3d-foot"><div class="f3d-prov"><div class="f3d-leg"><span><i></i>AI side: harness, model, toolbox</span><span><i style="background:#c4511f"></i>Ledgerline ERP 7.2 (black box)</span><span><i style="background:#1e8e5a"></i>checked</span></div>
      <b>Recorded run.</b> ${esc(T.meta.model)} · cassette ${esc(T.meta.cassette)} · recorded ${esc(T.meta.recorded_live || T.meta.recorded_at)} · sandbox clock ${esc(T.meta.sandbox_clock)} · numbers from <code>flow3d/trace.json</code></div>
      <div class="f3d-ctl ctl"><div class="f3d-btns">
        <button class="b-prev" aria-label="Previous stage">${ICON.prev}</button>
        <button class="b-narr" aria-label="Play every stage with narration" hidden>${ICON.narr}<span>Play with narration</span></button>
        <button class="b-voice on" aria-label="Narration on or off" aria-pressed="true" hidden>${ICON.voiceOn}<span>Voice on</span></button>
        <button class="b-auto" aria-label="Autoplay">${ICON.play}<span>Autoplay</span></button>
        <button class="b-replay" aria-label="Replay this stage">${ICON.replay}<span>Replay</span></button>
        <button class="b-next" aria-label="Next stage">${ICON.next}</button></div>
        <div class="f3d-prog">${S.map((_, i) => `<i data-k="${i}"></i>`).join('')}</div></div></div>
    ${T.meta.fixture ? '<div class="f3d-fix">Fixture, not a recorded run</div>' : ''}`;
  const $ = (q) => el.querySelector(q);
  const hud = { pill: $('.f3d-pill'), turn: $('.f3d-turn'), h2: $('.f3d-hud h2'), p: $('.f3d-hud p'), chips: $('.f3d-chips') };
  const msgsEl = $('.f3d-msgs'), railEl = $('.f3d-rail'), hudEl = $('.f3d-hud'), footEl = $('.f3d-foot');
  const prog = [...el.querySelectorAll('.f3d-prog i')];

  /* ---------- renderer, scene, camera ---------- */
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance', preserveDrawingBuffer: !!opts.still });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.setClearColor(0x000000, 0);
  el.insertBefore(renderer.domElement, el.firstChild);
  const labels = new CSS2DRenderer();
  labels.domElement.className = 'f3d-labels';
  el.insertBefore(labels.domElement, $('.f3d-rail'));

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;
  const camera = new THREE.PerspectiveCamera(30, 16 / 9, 0.5, 400);

  scene.add(new THREE.HemisphereLight(0xf4f8ff, 0xd5dde8, 0.42));
  const key = new THREE.DirectionalLight(0xffffff, 1.85);
  key.position.set(-10, 26, 16); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -26, right: 26, top: 18, bottom: -18, near: 1, far: 80 });
  key.shadow.bias = -0.0005; key.shadow.normalBias = 0.03; key.shadow.radius = 4;
  key.target.position.set(-1, 0, -2); scene.add(key, key.target);
  const rim = new THREE.DirectionalLight(0xcfe3ff, 0.55); rim.position.set(18, 10, -20); scene.add(rim);

  /* materials */
  const M = {
    satin: new THREE.MeshPhysicalMaterial({ color: 0xfbfcfe, roughness: 0.4, metalness: 0, clearcoat: 0.6, clearcoatRoughness: 0.28, envMapIntensity: 0.7 }),
    satin2: new THREE.MeshPhysicalMaterial({ color: 0xe9eff7, roughness: 0.5, clearcoat: 0.4, clearcoatRoughness: 0.35, envMapIntensity: 0.65 }),
    skyEdge: new THREE.MeshStandardMaterial({ color: 0x3c90ff, emissive: 0x3c90ff, emissiveIntensity: 0.55, roughness: 0.4 }),
    glass: new THREE.MeshPhysicalMaterial({ color: 0xdcebff, roughness: 0.06, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.05, transparent: true, opacity: 0.34, envMapIntensity: 1.6, depthWrite: false, side: THREE.DoubleSide }),
    pipe: new THREE.MeshPhysicalMaterial({ color: 0xe2efff, roughness: 0.1, clearcoat: 1, transparent: true, opacity: 0.22, envMapIntensity: 1.4, depthWrite: false }),
    pipeEmber: new THREE.MeshPhysicalMaterial({ color: 0xffe1d0, roughness: 0.12, clearcoat: 1, transparent: true, opacity: 0.26, envMapIntensity: 1.3, depthWrite: false }),
    ember: new THREE.MeshPhysicalMaterial({ color: 0xc4511f, roughness: 0.5, metalness: 0.05, clearcoat: 0.35, clearcoatRoughness: 0.4, emissive: 0xc4511f, emissiveIntensity: 0.0 }),
    emberDark: new THREE.MeshPhysicalMaterial({ color: 0x8e3714, roughness: 0.62, clearcoat: 0.2, emissive: 0xeb6834, emissiveIntensity: 0.0 }),
    paper: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.7 }),
    paperSky: new THREE.MeshStandardMaterial({ color: 0xeaf3ff, roughness: 0.6 }),
  };
  const RB = (w, h, d, r = 0.12, s = 4) => new RoundedBoxGeometry(w, h, d, s, Math.min(r, w / 2 - 0.001, h / 2 - 0.001, d / 2 - 0.001));
  const mesh = (geo, mat, pos, parent = scene, shadow = true) => {
    const m = new THREE.Mesh(geo, mat); if (pos) m.position.copy(pos); m.castShadow = shadow; m.receiveShadow = true; parent.add(m); return m;
  };

  /* floor: shadow catcher + a soft dot grid that fades out */
  const floorGeo = new THREE.PlaneGeometry(160, 120); floorGeo.rotateX(-Math.PI / 2);
  const shadowFloor = new THREE.Mesh(floorGeo, new THREE.ShadowMaterial({ color: 0x1b3a66, opacity: 0.2 }));
  shadowFloor.receiveShadow = true; scene.add(shadowFloor);
  const grid = new THREE.Mesh(floorGeo.clone(), new THREE.ShaderMaterial({
    transparent: true, depthWrite: false,
    uniforms: { uC: { value: new THREE.Color(0x8fb6e8) }, uT: { value: new THREE.Color(0xdde8f5) } },
    vertexShader: 'varying vec3 vP; void main(){ vP = (modelMatrix*vec4(position,1.)).xyz; gl_Position = projectionMatrix*viewMatrix*vec4(vP,1.); }',
    fragmentShader: `uniform vec3 uC; uniform vec3 uT; varying vec3 vP;
      void main(){ vec2 g = abs(fract(vP.xz/1.0 - .5) - .5); float d = length(g); float dot = 1. - smoothstep(.035,.06,d);
        vec2 q = (vP.xz - vec2(-0.8,-0.6)) / vec2(24., 13.); float r = length(q);
        float fade = 1. - smoothstep(0.55, 1.05, r);
        float tint = (1. - smoothstep(0.35, 1.0, r)) * .55;
        vec3 col = mix(uT, uC, dot);
        gl_FragColor = vec4(col, max(tint, dot*fade*.34));
        #include <colorspace_fragment>
      }`,
  }));
  grid.position.y = 0.006; scene.add(grid);

  /* contact shadow blobs (soft ambient occlusion under each block) */
  const blobTex = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
    const r = g.createRadialGradient(64, 64, 4, 64, 64, 64); r.addColorStop(0, 'rgba(20,45,90,0.38)'); r.addColorStop(1, 'rgba(20,45,90,0)');
    g.fillStyle = r; g.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c);
  })();
  const blob = (x, z, w, d) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshBasicMaterial({ map: blobTex, transparent: true, depthWrite: false }));
    m.rotation.x = -Math.PI / 2; m.position.set(x, 0.008, z); scene.add(m); return m;
  };

  /* ---------- labels ---------- */
  const labelList = [];
  function label(html, pos, { center = [0.5, 1], parent = scene, cls = '', kind = 'note' } = {}) {
    const outer = document.createElement('div');
    const inner = document.createElement('div'); inner.className = 'f3d-l ' + cls; inner.innerHTML = html;
    inner.style.transformOrigin = `${center[0] * 100}% ${center[1] * 100}%`;
    outer.appendChild(inner);
    const o = new CSS2DObject(outer); o.center.set(center[0], center[1]); if (pos) o.position.copy(pos); parent.add(o);
    const L = { o, inner, html, op: 1, kind,
      set(h) { if (h !== L.html) { L.html = h; inner.innerHTML = h; } return L; },
      show(op = 1) { L.op = op; o.visible = op > 0.01; inner.style.opacity = op.toFixed(3); return L; } };
    labelList.push(L); return L;
  }
  const tag = (text, sub, pos, cls = '') => label(`<span class="f3d-tag ${cls}"><i></i>${text}${sub ? ` <small>${sub}</small>` : ''}</span>`, pos, { center: [0.5, 1], kind: 'tag' });

  /* ---------- the world ---------- */
  const P = {
    app: V(-15.4, 0, 1.4), harness: V(-8.6, 0, 0.2), llm: V(-8.6, 3.5, -7.6),
    guard: V(-2.7, 1.45, 1.1), toolbox: V(5.0, 0, 0.6), erp: V(13.0, 0, 0.0), docs: V(5.0, 0, -4.4), inbox: V(13.0, 0, 5.0),
  };
  // app plinth (where Emma's chat enters the system)
  const app = new THREE.Group(); app.position.copy(P.app); scene.add(app);
  mesh(RB(2.6, 0.32, 2.0, 0.14), M.satin, V(0, 0.16, 0), app);
  const appScreen = mesh(RB(2.1, 1.35, 0.1, 0.05), M.glass, V(0, 1.12, -0.35), app, false);
  appScreen.rotation.x = -0.18;
  mesh(RB(1.7, 0.06, 0.06, 0.03), M.skyEdge, V(0, 0.34, 0.98), app, false);
  const appBubbles = [0, 1, 2].map((i) => mesh(RB(i % 2 ? 1.1 : 0.9, 0.2, 0.04, 0.09), i % 2 ? M.satin : M.skyEdge, V(i % 2 ? -0.35 : 0.42, 0.78 + i * 0.32, -0.28 + i * 0.06), app, false));
  appBubbles.forEach((b) => (b.rotation.x = -0.18));
  blob(P.app.x, P.app.z, 4.6, 3.6);
  const tApp = tag('Ask Northbridge', 'Emma’s chat', V(P.app.x, 2.15, P.app.z - 0.4));

  // harness platform
  const H = new THREE.Group(); H.position.copy(P.harness); scene.add(H);
  mesh(RB(8.2, 0.42, 5.6, 0.2), M.satin, V(0, 0.21, 0), H);
  mesh(RB(8.0, 0.05, 0.05, 0.02), M.skyEdge, V(0, 0.36, 2.82), H, false);
  blob(P.harness.x, P.harness.z, 11, 8);
  const sheets = (x, z, n, mat) => { const g = new THREE.Group(); g.position.set(x, 0.42, z); H.add(g);
    for (let i = 0; i < n; i++) { const m = mesh(RB(2.2, 0.07, 1.5, 0.03), i === n - 1 ? mat : M.satin2, V(0, 0.05 + i * 0.1, 0), g); m.rotation.y = (i - n / 2) * 0.025; }
    return g; };
  const sysG = sheets(-2.5, -1.35, 4, M.paperSky);
  const histG = sheets(-2.5, 1.3, 2, M.paper);
  const histSheets = []; // grows with the history
  for (let i = 0; i < 26; i++) { const m = mesh(RB(2.1, 0.05, 1.4, 0.02), i % 2 ? M.paper : M.paperSky, V(0, 0.27 + i * 0.075, 0), histG); m.visible = false; histSheets.push(m); }
  const schemaTray = V(P.harness.x + 0.9, 0.42, P.harness.z - 1.35);
  mesh(RB(2.6, 0.08, 1.7, 0.04), M.satin2, V(0.9, 0.46, -1.35), H);
  // context window bar
  const ctxStart = V(P.harness.x - 0.6, 0.95, P.harness.z + 1.45), ctxLen = 4.4;
  const ctxGlass = mesh(new THREE.CapsuleGeometry(0.3, ctxLen, 8, 24), M.glass, V(ctxStart.x + ctxLen / 2, ctxStart.y, ctxStart.z), scene, false);
  ctxGlass.rotation.z = Math.PI / 2;
  const ctxFill = mesh(RB(1, 0.36, 0.36, 0.16), new THREE.MeshStandardMaterial({ color: 0x3c90ff, emissive: 0x3c90ff, emissiveIntensity: 0.35, roughness: 0.35 }), V(ctxStart.x, ctxStart.y, ctxStart.z), scene, false);
  const tHarness = tag('Harness', 'builds every request', V(P.harness.x - 0.4, 0.45, P.harness.z + 3.6));
  tHarness.o.center.set(0.5, 0);
  const lSys = label('', V(P.harness.x - 2.5, 1.0, P.harness.z - 1.35), { center: [0.8, 1] });
  const lHist = label('', V(P.harness.x - 2.5, 0.75, P.harness.z + 1.3), { center: [1.05, 0.0] });
  const lSchema = label('', V(schemaTray.x + 0.6, 1.6, schemaTray.z), { center: [0.1, 1] });
  const lCtx = label('', V(ctxStart.x + ctxLen / 2 + 0.2, 1.35, ctxStart.z), { center: [0.5, 1] });

  // the LLM: a glass block with a core
  const LL = new THREE.Group(); LL.position.copy(P.llm); scene.add(LL);
  const halo = mesh(new THREE.CylinderGeometry(1.9, 2.1, 0.16, 72), M.satin, V(P.llm.x, 0.08, P.llm.z), scene);
  const haloRing = mesh(new THREE.TorusGeometry(1.55, 0.035, 12, 96), M.skyEdge, V(P.llm.x, 0.17, P.llm.z), scene, false); haloRing.rotation.x = Math.PI / 2;
  const beam = mesh(new THREE.CylinderGeometry(0.9, 1.5, P.llm.y - 1.3, 48, 1, true), new THREE.MeshBasicMaterial({ color: 0x9cc4ff, transparent: true, opacity: 0.07, depthWrite: false, side: THREE.DoubleSide }), V(P.llm.x, (P.llm.y - 1.3) / 2 + 0.15, P.llm.z), scene, false);
  const llmShell = mesh(RB(2.6, 2.6, 2.6, 0.42, 6), M.glass, V(0, 0, 0), LL, false);
  const coreMat = new THREE.MeshStandardMaterial({ color: 0x8fc0ff, emissive: 0x3c90ff, emissiveIntensity: 0.6, roughness: 0.25, metalness: 0.1, flatShading: true });
  const core = mesh(new THREE.IcosahedronGeometry(0.72, 1), coreMat, V(0, 0, 0), LL);
  const coreRing = mesh(new THREE.TorusGeometry(1.0, 0.03, 12, 96), M.skyEdge, V(0, 0, 0), LL, false);
  const coreRing2 = mesh(new THREE.TorusGeometry(1.08, 0.022, 12, 96), M.skyEdge, V(0, 0, 0), LL, false);
  const coreLight = new THREE.PointLight(0x3c90ff, 0, 7, 2); LL.add(coreLight);
  blob(P.llm.x, P.llm.z, 5, 5);
  const tLLM = tag('LLM', esc(T.meta.model.replace(/^[a-z]+:/, '')), V(P.llm.x + 1.55, P.llm.y - 1.0, P.llm.z + 1.2));
  tLLM.o.center.set(0, 0.5);
  const lOut = label('', V(P.llm.x - 1.6, P.llm.y + 0.2, P.llm.z + 1.2), { center: [1, 0.5] });

  // the 15 tool cards
  const cards = tools.map((t, i) => {
    const m = mesh(RB(2.3, 1.12, 0.07, 0.09), new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.32, clearcoat: 0.7, emissive: 0xffffff, emissiveIntensity: 0.28, transparent: true }), null, scene);
    m.castShadow = false;
    const lb = label(`<div class="f3d-card">${esc(t.name).replace(/_/g, '_<wbr>')}<small>${esc(t.category)}${t.writes ? ' · writes' : ''}</small></div>`, null, { center: [0.5, 0.5], parent: m, kind: 'card' });
    lb.o.position.set(0, 0, 0.06);
    return { m, lb, i };
  });
  const cols = 5;
  const wallPos = (i) => {
    const c = i % cols, r = Math.floor(i / cols), x = (c - 2) * 2.55;
    return { p: V(P.llm.x + x, P.llm.y + 4.75 - r * 1.36, P.llm.z - 2.2 + 0.075 * x * x), ry: -0.075 * x };
  };
  const stackPos = (i) => ({ p: V(schemaTray.x, 0.56 + i * 0.075, schemaTray.z), rx: -Math.PI / 2, rz: (i % 3 - 1) * 0.04 });

  // guard
  const G = new THREE.Group(); G.position.copy(P.guard); scene.add(G);
  const ringMat = new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.3, clearcoat: 0.8, emissive: 0x3c90ff, emissiveIntensity: 0.1 });
  const ring = mesh(new THREE.TorusGeometry(1.05, 0.11, 24, 96), ringMat, V(0, 0, 0), G);
  ring.rotation.y = Math.PI / 2 - 0.8;
  const scan = mesh(new THREE.CircleGeometry(0.95, 64), new THREE.MeshBasicMaterial({ color: 0x3c90ff, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide }), V(0, 0, 0), G, false);
  scan.rotation.y = Math.PI / 2 - 0.8;
  mesh(new THREE.CylinderGeometry(0.55, 0.7, 0.24, 48), M.satin, V(0, -1.33, 0), G);
  mesh(RB(0.22, 0.3, 0.22, 0.08), M.satin2, V(0, -1.12 + 0.0, 0), G);
  blob(P.guard.x, P.guard.z, 2.6, 2.6);
  const tGuard = tag('Guard', 'checks the call', V(P.guard.x, 0.05, P.guard.z + 1.0)); tGuard.o.center.set(0.5, 0);
  const lGuard = label('', V(P.guard.x, P.guard.y + 1.3, P.guard.z), { center: [0.5, 1] });

  // toolbox: 15 cartridges on a platform
  const TB = new THREE.Group(); TB.position.copy(P.toolbox); scene.add(TB);
  mesh(RB(4.9, 0.42, 3.7, 0.18), M.satin, V(0, 0.21, 0), TB);
  mesh(RB(4.7, 0.05, 0.05, 0.02), M.skyEdge, V(0, 0.36, 1.87), TB, false);
  blob(P.toolbox.x, P.toolbox.z, 7, 5.6);
  const carts = tools.map((t, i) => {
    const c = i % 5, r = Math.floor(i / 5);
    const m = mesh(RB(0.7, 0.42, 0.82, 0.1), new THREE.MeshPhysicalMaterial({ color: t.writes ? 0xeaf3ff : 0xffffff, roughness: 0.4, clearcoat: 0.5, emissive: 0x3c90ff, emissiveIntensity: 0 }),
      V((c - 2) * 0.88, 0.63, (r - 1) * 1.02), TB);
    return m;
  });
  const tToolbox = tag('Toolbox', 'MCP server · 15 tools', V(P.toolbox.x, 0.5, P.toolbox.z + 2.3));
  tToolbox.o.center.set(0.5, 0);
  const lTool = label('', V(P.toolbox.x + 1.2, 1.5, P.toolbox.z - 0.8), { center: [0, 1] });

  // manuals & policies (search_policy reads documents, not Ledgerline)
  const DG = new THREE.Group(); DG.position.copy(P.docs); scene.add(DG);
  mesh(RB(2.6, 0.3, 1.8, 0.12), M.satin, V(0, 0.15, 0), DG);
  for (let i = 0; i < 6; i++) { const m = mesh(RB(1.6, 0.08, 1.15, 0.03), i % 2 ? M.paper : M.paperSky, V(0, 0.36 + i * 0.1, 0), DG); m.rotation.y = (i - 3) * 0.06; }
  blob(P.docs.x, P.docs.z, 3.8, 3);
  const tDocs = tag('Manuals and policies', 'search index', V(P.docs.x, 1.25, P.docs.z));
  const lDocs = label('', V(P.docs.x - 1.4, 1.1, P.docs.z), { center: [1, 0.5] });

  // Ledgerline ERP: the black box
  const E = new THREE.Group(); E.position.copy(P.erp); scene.add(E);
  mesh(RB(5.0, 0.3, 4.4, 0.12), M.satin2, V(0, 0.15, 0), E);
  const erpBox = mesh(RB(4.4, 3.5, 3.8, 0.32, 6), M.ember, V(0, 2.05, 0), E);
  const erpFace = mesh(RB(0.06, 2.2, 2.6, 0.03), M.emberDark, V(-2.21, 2.0, 0), E, false);
  const slots = [0, 1, 2, 3].map((i) => mesh(RB(0.08, 0.12, 1.9, 0.05), M.emberDark, V(-2.22, 2.85 - i * 0.55, 0), E, false));
  mesh(RB(4.2, 0.06, 0.06, 0.02), new THREE.MeshStandardMaterial({ color: 0xffb08a, emissive: 0xeb6834, emissiveIntensity: 0.5 }), V(0, 3.82, 1.92), E, false);
  blob(P.erp.x, P.erp.z, 7.5, 6.5);
  const tERP = tag('Ledgerline ERP 7.2', 'services · a black box', V(P.erp.x, 4.25, P.erp.z), 'ember');
  const ERPN = V(P.erp.x - 2.7, 4.3, P.erp.z + 1.4);
  const lERP = label('', ERPN, { center: [1, 1] });

  // Daniel's approval inbox (inside Ledgerline)
  const IB = new THREE.Group(); IB.position.copy(P.inbox); scene.add(IB);
  mesh(RB(3.0, 0.3, 2.1, 0.12), M.satin, V(0, 0.15, 0), IB);
  const trayMat = new THREE.MeshPhysicalMaterial({ color: 0xfff3ec, roughness: 0.45, clearcoat: 0.5, emissive: 0xc4511f, emissiveIntensity: 0 });
  mesh(RB(2.5, 0.12, 1.6, 0.06), trayMat, V(0, 0.36, 0), IB);
  [[-1.2, 0], [1.2, 0]].forEach(([x]) => mesh(RB(0.1, 0.32, 1.6, 0.04), trayMat, V(x, 0.5, 0), IB));
  const inDocMat = [new THREE.MeshStandardMaterial({ color: 0xfff1e8, roughness: 0.6 }), new THREE.MeshStandardMaterial({ color: 0xffe0cc, emissive: 0xeb6834, emissiveIntensity: 0, roughness: 0.5 })];
  const inDocs = [0, 1, 2].map((i) => { const m = mesh(RB(2.0, 0.07, 1.3, 0.03), inDocMat[Math.min(i, 1)], V(0, 0.5 + i * 0.11, 0), IB); m.rotation.y = (i - 1) * 0.07; m.visible = false; return m; });
  blob(P.inbox.x, P.inbox.z, 4.2, 3.2);
  const tInbox = tag('Daniel Okafor', 'approval inbox', V(P.inbox.x, 0.4, P.inbox.z + 1.3), 'ember');
  tInbox.o.center.set(0.5, 0);
  const lInbox = label('', V(P.inbox.x + 1.7, 0.9, P.inbox.z), { center: [0, 0.5] });

  /* ---------- paths with a travelling light ---------- */
  const flowMat = (hex, base = 0.14) => new THREE.ShaderMaterial({
    transparent: true, depthWrite: false,
    uniforms: { uC: { value: new THREE.Color(hex) }, uHead: { value: 0 }, uOn: { value: 0 }, uDir: { value: 1 }, uBase: { value: base }, uTrail: { value: 0.22 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: `uniform vec3 uC; uniform float uHead, uOn, uDir, uBase, uTrail; varying vec2 vUv;
      void main(){ float x = uDir > 0. ? vUv.x : 1. - vUv.x; float d = uHead - x;
        float comet = d >= 0. ? exp(-d / uTrail) : exp(d / .006);
        float a = uBase + uOn * comet * .95;
        gl_FragColor = vec4(mix(uC, vec3(1.), comet*uOn*.25), a);
        #include <colorspace_fragment>
      }`,
  });
  const paths = {};
  function path(name, pts, hex = C.sky, { r = 0.045, pipe = null, base = 0.16 } = {}) {
    const curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal');
    const mat = flowMat(hex, base);
    const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, 160, r, 10, false), mat); scene.add(tube);
    if (pipe) { const p = new THREE.Mesh(new THREE.TubeGeometry(curve, 120, pipe.r, 24, false), pipe.mat); p.castShadow = false; scene.add(p); }
    paths[name] = { curve, mat, len: curve.getLength() };
  }
  const appOut = V(P.app.x + 1.0, 1.0, P.app.z - 0.1);
  const histIn = V(P.harness.x - 2.5, 1.0, P.harness.z + 1.3);
  path('user', [appOut, V(P.app.x + 2.6, 2.2, P.app.z), V(histIn.x - 1.6, 2.0, histIn.z), histIn], C.sky, { base: 0.06 });
  path('reply', [V(P.llm.x - 1.4, P.llm.y + 0.3, P.llm.z + 0.6), V(P.llm.x - 4.2, P.llm.y + 0.8, P.llm.z + 4), V(P.app.x + 1.6, 2.6, P.app.z - 0.6), V(P.app.x + 0.4, 1.6, P.app.z - 0.3)], C.sky, { base: 0.06 });
  const ctxEnd = V(ctxStart.x + ctxLen + 0.3, ctxStart.y, ctxStart.z);
  path('src_sys', [V(P.harness.x - 2.5, 1.0, P.harness.z - 1.35), V(P.harness.x - 1.4, 1.9, P.harness.z), ctxStart.clone().add(V(0.3, 0, 0))], C.sky, { base: 0.0 });
  path('src_hist', [histIn.clone().add(V(0.6, 0, 0)), V(P.harness.x - 1.2, 1.6, P.harness.z + 1.5), ctxStart.clone().add(V(0.6, 0, 0))], C.sky, { base: 0.0 });
  path('src_sch', [V(schemaTray.x, 1.0, schemaTray.z), V(schemaTray.x + 0.4, 2.0, schemaTray.z + 1.2), ctxStart.clone().add(V(2.2, 0, 0))], C.sky, { base: 0.0 });
  path('ctx', [ctxEnd, V(ctxEnd.x + 1.6, 2.6, ctxEnd.z - 2.5), V(P.llm.x + 2.6, P.llm.y - 0.4, P.llm.z + 2.2), V(P.llm.x + 0.6, P.llm.y - 0.6, P.llm.z + 0.9)], C.sky, { base: 0.06 });
  path('call', [V(P.llm.x + 1.4, P.llm.y + 0.2, P.llm.z + 0.4), V(P.llm.x + 4.4, P.llm.y + 0.4, P.llm.z + 3.2), V(P.guard.x - 1.6, P.guard.y + 0.6, P.guard.z - 0.4), V(P.guard.x - 0.2, P.guard.y, P.guard.z)], C.sky, { base: 0.06 });
  path('back', [V(P.guard.x - 0.2, P.guard.y - 0.25, P.guard.z + 0.25), V(P.guard.x - 1.3, 1.2, P.guard.z + 0.5), ctxEnd.clone().add(V(0.2, 0, 0))], C.sky, { base: 0.06 });
  const tbIn = V(P.toolbox.x - 2.6, 1.0, P.toolbox.z + 0.4);
  path('mcp', [V(P.guard.x + 0.2, P.guard.y, P.guard.z), V(P.guard.x + 3.0, P.guard.y + 1.2, P.guard.z + 0.4), V(tbIn.x - 2.4, tbIn.y + 1.0, tbIn.z), tbIn], C.sky, { r: 0.06, pipe: { r: 0.36, mat: M.pipe }, base: 0.22 });
  const tbOut = V(P.toolbox.x + 2.5, 0.95, P.toolbox.z + 0.1), erpIn = V(P.erp.x - 2.3, 2.0, P.erp.z + 0.1);
  path('svc', [tbOut, V(tbOut.x + 1.6, 1.6, tbOut.z), V(erpIn.x - 1.4, 2.0, erpIn.z), erpIn], C.ember, { r: 0.05, pipe: { r: 0.28, mat: M.pipeEmber }, base: 0.22 });
  path('doc', [V(P.toolbox.x - 0.3, 1.0, P.toolbox.z - 1.6), V(P.toolbox.x - 0.6, 1.9, P.toolbox.z - 3.0), V(P.docs.x, 1.2, P.docs.z + 0.5)], C.sky, { base: 0.1 });
  path('inbox', [V(P.erp.x - 0.4, 1.6, P.erp.z + 1.95), V(P.erp.x - 0.6, 2.0, P.erp.z + 3.4), V(P.inbox.x - 0.2, 0.9, P.inbox.z)], C.ember, { base: 0.1 });
  const tMCP = tag('MCP', 'JSON-RPC · tools/call', paths.mcp.curve.getPointAt(0.5).add(V(0, 0.55, 0)));

  /* a route = several paths joined; u in [0,1] over the whole length */
  function route(...parts) {
    parts = parts.map((p) => (typeof p === 'string' ? { n: p, rev: false } : p));
    const lens = parts.map((p) => paths[p.n].len), total = lens.reduce((a, b) => a + b, 0);
    return {
      at(u, out = new THREE.Vector3()) {
        let d = clamp01(u) * total;
        for (let i = 0; i < parts.length; i++) {
          if (d <= lens[i] || i === parts.length - 1) { const l = clamp01(d / lens[i]); return paths[parts[i].n].curve.getPointAt(parts[i].rev ? 1 - l : l, out); }
          d -= lens[i];
        }
      },
      glow(u, on = 1) {
        let d = clamp01(u) * total;
        parts.forEach((p, i) => {
          const m = paths[p.n].mat.uniforms; const l = d / lens[i];
          if (l > -0.05) { m.uOn.value = Math.max(m.uOn.value, on * (l > 1.6 ? 0 : 1)); m.uHead.value = Math.min(l, 1.25); m.uDir.value = p.rev ? -1 : 1; }
          d -= lens[i];
        });
      },
    };
  }
  const R = {
    user: route('user'), ctx: route('ctx'), call: route('call'), mcp: route('mcp'), svc: route('svc'), doc: route('doc'),
    back: route({ n: 'mcp', rev: true }, 'back'), backCtx: route({ n: 'mcp', rev: true }, 'back', 'ctx'),
    svcBack: route({ n: 'svc', rev: true }), docBack: route({ n: 'doc', rev: true }), reply: route('reply'), inbox: route('inbox'),
    sys: route('src_sys'), hist: route('src_hist'), sch: route('src_sch'),
  };

  /* ---------- packets, notes and token particles (transient, reset each frame) ---------- */
  const pkMats = {
    req: new THREE.MeshPhysicalMaterial({ color: 0x3c90ff, emissive: 0x3c90ff, emissiveIntensity: 0.45, roughness: 0.3, clearcoat: 0.8 }),
    res: new THREE.MeshPhysicalMaterial({ color: 0xffffff, emissive: 0x9cc4ff, emissiveIntensity: 0.35, roughness: 0.3, clearcoat: 0.8 }),
    svc: new THREE.MeshPhysicalMaterial({ color: 0xc4511f, emissive: 0xeb6834, emissiveIntensity: 0.4, roughness: 0.35, clearcoat: 0.6 }),
    ok: new THREE.MeshPhysicalMaterial({ color: 0x1e8e5a, emissive: 0x1e8e5a, emissiveIntensity: 0.35, roughness: 0.35, clearcoat: 0.6 }),
    doc: new THREE.MeshPhysicalMaterial({ color: 0xffffff, emissive: 0xffd3bd, emissiveIntensity: 0.25, roughness: 0.5 }),
  };
  const pkGeo = RB(0.62, 0.36, 0.36, 0.13), docGeo = RB(1.2, 0.05, 0.85, 0.02);
  const packets = Array.from({ length: 14 }, () => {
    const m = new THREE.Mesh(pkGeo, pkMats.req); m.castShadow = true; m.visible = false; scene.add(m);
    const lb = label('', null, { center: [0.5, 1.12], parent: m }); lb.o.position.set(0, 0.32, 0);
    return { m, lb, used: false };
  });
  let pkN = 0;
  function packet(pos, kind = 'req', html = '', lop = 1, scale = 1) {
    const p = packets[pkN++]; if (!p) return;
    p.used = true; p.m.visible = true; p.m.position.copy(pos); p.m.material = pkMats[kind]; p.m.geometry = kind === 'doc' ? docGeo : pkGeo;
    p.m.scale.setScalar(scale);
    if (html) { p.lb.set(html); p.lb.show(lop); } else p.lb.show(0);
    return p;
  }
  const notes = Array.from({ length: 8 }, () => label('', V(0, 0, 0), { center: [0.5, 1] }));
  let ntN = 0;
  function note(pos, html, op = 1, center = [0.5, 1]) {
    const n = notes[ntN++]; if (!n || op <= 0.01) return;
    n.o.position.copy(pos); n.o.center.set(center[0], center[1]); n.inner.style.transformOrigin = `${center[0] * 100}% ${center[1] * 100}%`;
    n.set(html); n.show(op); n.used = true;
  }
  const NTOK = 72;
  const tokGeo = RB(0.17, 0.17, 0.17, 0.05, 2);
  const tokMat = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0x3c90ff, emissiveIntensity: 0.5, roughness: 0.3 });
  const toks = new THREE.InstancedMesh(tokGeo, tokMat, NTOK); toks.frustumCulled = false; scene.add(toks);
  const tokColors = [new THREE.Color(0xffffff), new THREE.Color(0xbfdcff), new THREE.Color(0x3c90ff)];
  for (let i = 0; i < NTOK; i++) toks.setColorAt(i, tokColors[i % 3]);
  const _m4 = new THREE.Matrix4(), _q = new THREE.Quaternion(), _s = new THREE.Vector3(), _p = new THREE.Vector3();
  let tokUsed = 0;
  function tokenStream(rt, t, t0, span, n, travel = 0.9, scale = 1) { // n tokens leave rt over [t0, t0+span]
    for (let i = 0; i < n && tokUsed < NTOK; i++) {
      const u = seg(t, t0 + (i / n) * span, t0 + (i / n) * span + travel);
      if (u <= 0 || u >= 1) continue;
      rt.at(eio(u), _p); _p.y += Math.sin(i * 12.9898) * 0.12; _p.z += Math.cos(i * 4.1) * 0.12;
      const sc = scale * Math.sin(u * Math.PI) ** 0.4;
      _q.setFromEuler(new THREE.Euler(i, i * 0.7, 0)); _s.setScalar(sc);
      _m4.compose(_p, _q, _s); toks.setMatrixAt(tokUsed++, _m4);
    }
  }

  /* ---------- camera shots ---------- */
  const orbit = (tx, ty, tz, dist, pitch, yaw = 0) => { const p = pitch * Math.PI / 180, y = yaw * Math.PI / 180;
    return [V(tx + dist * Math.cos(p) * Math.sin(y), ty + dist * Math.sin(p), tz + dist * Math.cos(p) * Math.cos(y)), V(tx, ty, tz)]; };
  const SHOT = {
    overview: orbit(0.4, 1.0, -1.4, 52, 27),
    harness: orbit(-9.8, 1.3, -0.6, 27, 30, -4),
    llm: orbit(-8.0, 4.5, -8.4, 29, 15, 7),
    guard: orbit(-2.2, 1.7, 0.0, 21, 26, -8),
    mcp: orbit(1.6, 1.5, -0.2, 22, 27, 0),
    erp: orbit(10.2, 2.0, 1.2, 25, 27, 5),
    docs: orbit(4.4, 1.0, -2.0, 21, 33, -4),
    inbox: orbit(11.2, 1.5, 2.6, 25, 31, 8),
    pipe: orbit(-1.4, 2.0, -1.8, 41, 26, 0),
    guardmcp: orbit(0.6, 1.6, 0.2, 24, 27, -4),
    mid: orbit(-2.8, 2.4, -2.6, 33, 25, 0),
    left: orbit(-9.6, 2.8, -3.0, 29, 24, -3),
  };
  const cam = { pos: V(0, 0, 0), tgt: V(0, 0, 0) };
  const ZOOM = opts.zoom || (mode === 'deck' ? 1.1 : 1);
  function shotAt(keys, t) { // keys: [[time, shot], ...]
    let a = keys[0], b = keys[0];
    for (let i = 0; i < keys.length; i++) { if (t >= keys[i][0]) { a = keys[i]; b = keys[i + 1] || keys[i]; } }
    if (t < keys[0][0]) { a = keys[0]; b = keys[0]; }
    const u = b === a ? 1 : eio(seg(t, a[0], b[0]));
    const A = typeof a[1] === 'string' ? SHOT[a[1]] : a[1], B = typeof b[1] === 'string' ? SHOT[b[1]] : b[1];
    cam.pos.lerpVectors(A[0], B[0], u); cam.tgt.lerpVectors(A[1], B[1], u);
    if (ZOOM !== 1) cam.pos.sub(cam.tgt).multiplyScalar(ZOOM).add(cam.tgt);
  }

  /* ---------- stage scripts ---------- */
  const DUR = { overview: 3, arrive: 3.4, assemble: 5.2, decide: 5.6, guard: 6.0, erp: 0, docs: 4.2, result: 5.2, reply: 6.2, receipt: 6.6, cycle: 0, write: 0 };
  const svcDur = (n) => 1.4 + Math.min(n, 12) * 0.34 + 1.2;
  const stepEnd = (st) => { let tt = 5.5; for (const c of st.tools) tt += c.services.length ? Math.min(1.6, 0.16 * c.services.length) + 1.2 : 1.4; return tt; };
  const cycleDur = (st) => stepEnd(st) + 1.7 + (st.tools.length - 1) * 0.25 + 0.9;
  S.forEach((s) => {
    s.dur = DUR[s.kind];
    if (s.kind === 'erp') s.dur = svcDur(s.call.services.length) + 0.4;
    if (s.kind === 'cycle') s.dur = s.steps.reduce((a, st) => a + cycleDur(st), 0) + 0.4;
    if (s.kind === 'write') s.dur = 10.8;
    if (s.kind === 'receipt') s.dur = 9.4;
  });
  const prevShot = (k) => (k <= 0 ? ['overview'] : S[k - 1].endShot || ['overview']);

  // per-frame state (reset each frame)
  let F;
  function resetFrame() {
    F = { active: new Set(), hide: new Set(), llmHeat: 0, guard: 0, guardOk: 0, erpHeat: 0, inboxHeat: 0, cart: -1, cartLift: 0, cardsMode: null };
    pkN = 0; ntN = 0; tokUsed = 0;
    packets.forEach((p) => { p.m.visible = false; p.lb.show(0); });
    notes.forEach((n) => n.show(0));
    for (const k in paths) { paths[k].mat.uniforms.uOn.value = 0; }
    [lSys, lHist, lSchema, lCtx, lOut, lGuard, lTool, lERP, lInbox, lDocs].forEach((l) => l.show(0));
  }

  /* cards: stack -> wall (fan out), chosen pulled forward */
  const _qa = new THREE.Quaternion(), _qb = new THREE.Quaternion(), _e = new THREE.Euler();
  function setCards(fan, chosen = [], pick = 0, fold = 0) {
    // fan: 0..1 stack->wall; pick: 0..1 chosen highlight; fold: 0..1 others back to stack, chosen shrinks away
    cards.forEach((c, i) => {
      const st = stackPos(i), w = wallPos(i);
      const isC = chosen.includes(i);
      let f = eio(seg(fan, i * 0.028, i * 0.028 + 0.58));
      if (fold > 0) f = f * (1 - eio(seg(fold, (14 - i) * 0.02, (14 - i) * 0.02 + 0.6)));
      _p.lerpVectors(st.p, w.p, f); _p.y += Math.sin(f * Math.PI) * 1.6; _p.z += Math.sin(f * Math.PI) * 1.0;
      _qa.setFromEuler(_e.set(st.rx, 0, st.rz)); _qb.setFromEuler(_e.set(0, w.ry, 0)); _qa.slerp(_qb, f);
      let sc = 1;
      const mat = c.m.material;
      if (isC && pick > 0) {
        const pk = eio(pick), j = chosen.indexOf(i), spot = V(P.llm.x + 3.7, P.llm.y + 0.1 - (j - (chosen.length - 1) / 2) * 1.75, P.llm.z + 1.9);
        _p.lerp(spot, pk); _qa.slerp(_qb.identity(), pk); sc = 1 + 0.22 * pk;
        mat.emissive.setHex(0x3c90ff); mat.emissiveIntensity = 0.28 + 0.5 * pk; mat.color.setHex(0xdcebff); mat.opacity = 1;
      } else {
        mat.emissive.setHex(0xffffff); mat.emissiveIntensity = 0.28; mat.color.setHex(0xffffff);
        mat.opacity = chosen.length && pick > 0 ? 1 - 0.45 * eo(pick) : 1;
      }
      if (isC && fold > 0) { const g = eio(clamp01(fold * 1.6)); _p.lerp(paths.call.curve.getPointAt(0), g); sc = 1.22 * (1 - g * 0.85); mat.emissive.setHex(0x3c90ff); mat.emissiveIntensity = 0.78; mat.color.setHex(0xdcebff); mat.opacity = 1; }
      c.m.position.copy(_p); c.m.quaternion.copy(_qa); c.m.scale.setScalar(Math.max(sc, 0.001));
      c.m.visible = !(isC && fold > 0.62);
      const lop = clamp01((f - 0.8) / 0.2);
      c.lb.show(c.m.visible ? lop * (chosen.length && pick > 0.3 && !isC ? 0.55 : 1) : 0);
      c.lb.inner.firstChild.classList.toggle('on', isC && pick > 0.3);
    });
  }

  const cardsOf = (calls) => calls.map((c) => toolIx[c.name]).filter((x) => x !== undefined);
  const argsHTML = (call) => `<pre>${jsonBlock(call.args, { width: 50 })}</pre>`;
  function callNote(call, kicker = 'Tool call') {
    return `<div class="f3d-note sky"><div class="k">${kicker} <b>${esc(call.name)}</b></div><pre>${jsonSpan(j1(call.args, 58))}</pre></div>`;
  }
  function resultKeys(call) {
    const r = call.result || {};
    if (r.ok === false) return ['ok', 'error', 'next_step'];
    const pref = { check_stock: ['ok', 'item_code', 'warehouses', 'free_total', 'cover_days', 'reorder_level'],
      find_item: ['ok', 'items'], find_supplier: ['ok', 'matches'], check_budget: ['ok', 'code', 'name', 'open', 'budget_left'],
      create_purchase_request: r.preview ? ['ok', 'preview', 'note'] : ['ok', 'request_no', 'status', 'estimated_value', 'approver', 'next_step'],
      search_policy: ['ok', 'answer_in_documents', 'clauses'] }[call.name];
    return pref || Object.keys(r);
  }
  function resultView(call) {
    const r = call.result || {};
    let obj = r;
    if (call.name === 'search_policy' && Array.isArray(r.clauses)) obj = { ...r, clauses: r.clauses.map((c) => ({ cite: c.cite, heading: c.heading })) };
    if (call.name === 'find_item' && Array.isArray(r.items)) obj = { ...r, items: r.items.map((c) => ({ item_code: c.item_code, description: c.description })) };
    if (call.name === 'find_supplier' && Array.isArray(r.matches)) obj = { ...r, matches: r.matches.map((c) => ({ supplier_code: c.supplier_code, name: c.name, certificate: c.cell_safety_certificate })) };
    if (call.name === 'check_stock' && Array.isArray(r.warehouses)) obj = { ...r, warehouses: r.warehouses.map((w) => ({ warehouse: w.warehouse, on_hand: w.on_hand })) };
    if (r.preview) obj = { ...r, preview: { quantity: r.preview.quantity, estimated_value: r.preview.estimated_value, approver: r.preview.approver } };
    return obj;
  }
  function resultNote(call) {
    const bad = call.result && call.result.ok === false;
    return `<div class="f3d-note ${bad ? 'ember' : 'green'}"><div class="k">Result <b>${esc(call.name)} · ${msf(call.ms)}</b></div><pre>${jsonBlock(resultView(call), { keys: resultKeys(call), max: 6, width: 54, expand: ['preview'] })}</pre></div>`;
  }
  function guardNote(call, p) {
    const g = call.guard || {};
    const rows = (g.checked || []).map((c, i) => {
      const on = p > (i + 1) / ((g.checked || []).length + 1);
      return `<span>${esc(c.arg)}</span><span class="dim">${esc(c.type || '')}</span><span class="${on ? 'ok' : 'dim'}">${on ? 'ok' : '…'}</span>`;
    }).join('');
    const extra = g.writes ? `<div class="t" style="margin-top:6px">Writes. ${call.args.confirm ? '<b>confirm: true</b>, after Emma’s yes.' : '<b>confirm: false</b>, so this is a preview: nothing is saved.'}</div>` : '';
    return `<div class="f3d-note green"><div class="k">Guard <b>schema from tool.json</b></div><div class="row">${rows || '<span class="dim">no arguments</span><span></span><span class="ok">ok</span>'}</div>${extra}</div>`;
  }
  function svcList(call, n) {
    const sv = call.services.slice(0, n), g = [];
    for (const x of sv) { const l = g[g.length - 1]; if (l && l.svc === x.svc) { l.n++; if (x.rc === 'E') l.rc = 'E'; } else g.push({ svc: x.svc, in: x.in, rc: x.rc, n: 1 }); }
    const rows = g.map((x) => `<span>${esc(x.svc)}${x.n > 1 ? ` <span class="dim">×${x.n}</span>` : ''}</span><span class="dim">${esc(j1(x.in, 34))}</span><span class="${x.rc === 'E' ? 'bad' : 'ok'}">rc ${esc(x.rc)}</span>`).join('');
    const ms = call.services.reduce((a, x) => a + x.ms, 0);
    return `<div class="f3d-note ember"><div class="k">Ledgerline services <b>${call.services.length} calls · ${msf(ms)}</b></div><div class="row">${rows}</div><div class="t" style="margin-top:6px">Data in, data out. rc S = success, E = error.</div></div>`;
  }

  function outNote(text, p, sub) {
    const n = Math.round(text.length * clamp01(p));
    return `<div class="f3d-note sky"><div class="k">Tokens out <b>${sub}</b></div><pre>${jsonSpan(text.slice(0, n))}${p < 1 ? '<span style="color:#3c90ff">▍</span>' : ''}</pre></div>`;
  }
  const callText = (calls) => calls.map((c) => `${c.name}(${j1(c.args, 64 - c.name.length)})`).join('\n');
  const llmSub = (e) => `${fmt(e.tokens_in)} in · ${fmt(e.tokens_out)} out · ${secs(e.seconds)}`;

  /* persistent state before stage k: history sheets, context bar, inbox */
  function applyPersistent(k, t) {
    const s = S[k];
    const hist = s.histBefore, ctx = s.ctxBefore;
    setHist(hist); setCtx(ctx);
    const inboxAfter = S.slice(0, k).some((x) => x.kind === 'write');
    setInbox(inboxAfter ? 'after' : 'before');
    setCards(0);
  }
  const histTarget = { n: 0 };
  function setHist(n) { histTarget.n = n; const step = Math.min(0.075, 1.05 / Math.max(n, 1));
    histSheets.forEach((m, i) => { m.visible = i < n; m.position.y = 0.27 + i * step; }); }
  const CTX_MAX = 7000;
  function setCtx(tokens) {
    const f = clamp01(tokens / CTX_MAX), L = Math.max(0.02, f * ctxLen);
    ctxFill.scale.set(L, 1, 1); ctxFill.position.x = ctxStart.x + L / 2; ctxFill.visible = tokens > 0;
    histTarget.ctx = tokens;
  }
  function setInbox(which) {
    const list = ((T.inbox || {})[which] || {}).waiting || [];
    inDocs.forEach((m, i) => (m.visible = i < list.length));
    histTarget.inbox = list;
  }
  const inboxHTML = (list, hi) => `<div class="f3d-note ember"><div class="k">Waiting for Daniel <b>${list.length}</b></div><div class="row">${list.map((d) =>
    `<span style="${hi === d.doc_no ? 'color:#c4511f;font-weight:650' : ''}">${esc(d.doc_no)}</span><span class="dim">${fmt(d.quantity)} × ${esc(d.item_code)}</span><span>${money(d.value)}</span>`).join('')}</div></div>`;

  /* the sub-timeline of one model step with its tool calls (used by cycle and write) */
  function playStep(st, t, k, opts2 = {}) {
    const noReturn = !!opts2.noReturn;
    const calls = st.tools, ch = cardsOf(calls), hasSvc = calls.some((c) => c.services.length);
    const writeC = calls.find(isCommit);
    // 0-1.1 context to the model
    R.ctx.glow(seg(t, 0, 1.1)); if (t < 1.2) tokenStream(R.ctx, t, 0, 0.8, 26, 0.55);
    F.llmHeat = Math.max(F.llmHeat, seg(t, 0.6, 1.2) * (1 - seg(t, 2.6, 3.2)));
    // 0.6-1.9 fan, 1.9 pick
    const fold = seg(t, 2.6, 3.5);
    setCards(seg(t, 0.5, 1.9), ch, seg(t, 1.9, 2.4), fold);
    if (t > 1.9 && t < 3.4) note(V(P.llm.x - 1.6, P.llm.y + 0.3, P.llm.z + 1.2), outNote(callText(calls), seg(t, 1.9, 2.7), llmSub(st.llm)), seg(t, 1.9, 2.1) * (1 - seg(t, 3.1, 3.4)), [1, 0.5]);
    // 2.9-3.9 packet(s) to the guard
    calls.forEach((c, j) => {
      const d = j * 0.22;
      const u1 = seg(t, 2.9 + d, 3.9 + d);
      if (u1 > 0 && u1 < 1) { R.call.glow(u1); packet(R.call.at(eio(u1)), 'req', j === 0 ? callNote(c) : '', 1); }
      // guard 3.9-4.4
      if (t >= 3.9 + d && t < 4.5 + d) { F.guard = 1; F.guardOk = seg(t, 4.0 + d, 4.4 + d); packet(V(P.guard.x - 0.1, P.guard.y, P.guard.z), 'req'); }
      // 4.4-5.3 MCP
      const u2 = seg(t, 4.4 + d, 5.3 + d);
      if (u2 > 0 && u2 < 1) { F.hide.add('mcp'); R.mcp.glow(u2); packet(R.mcp.at(eio(u2)), 'req', j === 0 ? `<div class="f3d-note sky"><div class="k">MCP <b>tools/call</b></div><pre>${jsonSpan(j1({ name: c.name, arguments: c.args }, 60))}</pre></div>` : ''); }
      if (t > 5.1 + d) { F.cart = toolIx[c.name]; F.cartLift = seg(t, 5.1 + d, 5.5 + d); F.active.add('toolbox'); }
    });
    if (t > 3.8 && t < 4.6) note(V(P.guard.x, P.guard.y + 1.3, P.guard.z), guardNote(calls[0], seg(t, 3.9, 4.4)), seg(t, 3.8, 3.95) * (1 - seg(t, 4.45, 4.6)), [0.5, 1]);
    // 5.5-? services or documents
    let tt = 5.5;
    calls.forEach((c, j) => {
      if (c.services.length) {
        const n = c.services.length, span = Math.min(1.6, 0.16 * n);
        for (let i = 0; i < n; i++) {
          const a = tt + (i / n) * span, u = seg(t, a, a + 0.55), ub = seg(t, a + 0.6, a + 1.1);
          if (u > 0 && u < 1) { R.svc.glow(u); packet(R.svc.at(eio(u)), 'svc', '', 0, 0.62); }
          if (ub > 0 && ub < 1) { R.svcBack.glow(ub); packet(R.svcBack.at(eio(ub)), c.services[i].rc === 'E' ? 'svc' : 'res', '', 0, 0.55); }
          if (t > a + 0.5 && t < a + 0.75) F.erpHeat = 1;
        }
        if (t > tt && t < tt + span + 1.3) {
          F.active.add('erp');
          note(ERPN, svcList(c, Math.ceil(seg(t, tt, tt + span + 0.6) * n)), seg(t, tt, tt + 0.2) * (1 - seg(t, tt + span + 1.1, tt + span + 1.3)), [1, 1]);
        }
        if (writeC === c) opts2.onWrite && opts2.onWrite(t, tt, span);
        tt += span + 1.2;
      } else {
        const u = seg(t, tt, tt + 0.6), ub = seg(t, tt + 0.7, tt + 1.3);
        if (u > 0 && u < 1) { R.doc.glow(u); packet(R.doc.at(eio(u)), 'req', '', 0, 0.62); }
        if (ub > 0 && ub < 1) { R.docBack.glow(ub); packet(R.docBack.at(eio(ub)), 'res', '', 0, 0.55); }
        if (t > tt && t < tt + 1.5) { F.active.add('docs'); note(V(P.docs.x - 1.5, 1.2, P.docs.z), docsNote(c), seg(t, tt, tt + 0.2) * (1 - seg(t, tt + 1.3, tt + 1.5)), [1, 0.5]); }
        tt += 1.4;
      }
    });
    // result(s) back to the harness and into the model
    const tb = tt;
    if (!noReturn) calls.forEach((c, j) => {
      const u = seg(t, tb + j * 0.25, tb + 1.6 + j * 0.25);
      if (u > 0 && u < 1) { R.backCtx.glow(u); packet(R.backCtx.at(eio(u)), c.result && c.result.ok === false ? 'svc' : 'res', j === 0 && u < 0.85 ? resultNote(c) : '', j === 0 ? 1 - seg(u, 0.7, 0.85) : 0); }
    });
    if (!noReturn && opts2.last) {
      const ta = tb + 1.6 + (calls.length - 1) * 0.25; if (t > ta - 0.2) F.hide.add('llm');
      if (calls.length > 1) note(V(P.llm.x + 1.8, P.llm.y + 0.3, P.llm.z + 1.2), resultsNote(calls), seg(t, ta, ta + 0.3), [0, 0.5]);
      else calls.forEach((c, j) => note(V(P.llm.x + 1.8, P.llm.y + (calls.length > 1 ? 1.6 - j * 2.7 : 0.3), P.llm.z + 1.2), resultNote(c), seg(t, ta, ta + 0.3), [0, 0.5]));
    }
    return tb + 1.7 + (calls.length - 1) * 0.25;
  }
  function resultsNote(calls) {
    const rows = calls.map((c) => {
      const r = c.result || {}, v = resultView(c);
      const cand = resultKeys(c).filter((k) => !['ok', 'item_code', 'code', 'note'].includes(k) && k in v);
      const scal = cand.filter((k) => v[k] === null || typeof v[k] !== 'object');
      const ks = r.ok === false ? ['error'] : (scal.length ? scal.slice(0, 2) : cand.slice(0, 1));
      const sub = Object.fromEntries(ks.map((k) => [k, v[k]]));
      return `<span>${esc(c.name)}</span><span class="${r.ok === false ? 'bad' : 'ok'}">ok ${r.ok === false ? 'false' : 'true'}</span><span class="dim">${jsonSpan(j1(sub, 52))}</span>`; }).join('');
    return `<div class="f3d-note green"><div class="k">Results <b>${calls.length} tools · ${msf(calls.reduce((a, c) => a + c.ms, 0))}</b></div><div class="row">${rows}</div></div>`;
  }
  function docsNote(c) {
    const cl = ((c.result || {}).clauses || []).slice(0, 2);
    return `<div class="f3d-note sky"><div class="k">search_policy <b>documents, not Ledgerline · ${msf(c.ms)}</b></div><div class="row">${cl.map((x) => `<span>${esc(x.cite)}</span><span class="dim" style="grid-column:span 2">${esc(j1(x.heading || '', 40).replace(/^"|"$/g, ''))}</span>`).join('')}</div></div>`;
  }

  /* the captions: plain words, the numbers from the trace */
  const tur = (ti) => `Turn ${ti + 1} of ${T.turns.length}`;
  const tsum = (ti) => { const e = T.turns[ti].events, l = e.filter((x) => x.kind === 'llm'); return { calls: l.length, tools: e.length - l.length, sec: l.reduce((a, x) => a + x.seconds, 0) + e.filter((x) => x.kind === 'tool').reduce((a, x) => a + x.ms / 1000, 0), tin: l.reduce((a, x) => a + x.tokens_in, 0), tout: l.reduce((a, x) => a + x.tokens_out, 0) }; };
  const chip = (b, s, c = '') => `<span class="${c}"><b>${b}</b>${s}</span>`;
  function caption(s, k) {
    const cs = T.context_split || {};
    switch (s.kind) {
      case 'overview': return { kick: 'One real request, end to end', h: 'How Ask Northbridge works, underneath',
        p: `Emma asks two things. Watch each request go from her chat through <b>the harness</b>, <b>the LLM</b>, <b>the guard</b> and <b>MCP</b> to <b>the toolbox</b>, and from there into <b>Ledgerline ERP 7.2</b>.`,
        chips: chip(fmt(T.turns.length), ' turns') + chip(fmt(T.meta.totals.calls), ' model calls') + chip(fmt(T.turns.reduce((a, tu) => a + tu.events.filter((e) => e.kind === 'tool').length, 0)), ' tool calls') + chip(fmt(tools.length), ' tools over MCP'), shot: [[0, 'overview']] };
      case 'arrive': return { kick: tur(s.ti), h: s.ti === 0 ? 'Emma’s message arrives' : (s.text.length < 30 ? `Emma answers: “${esc(s.text)}”` : 'A new request arrives'),
        p: `The app sends her sentence to the harness as a <b>user message</b>. The model now holds <b>${s.histBefore + 1}</b> message${s.histBefore ? 's' : ''} of chat history.`,
        chips: chip(`${s.text.split(/\s+/).length}`, ' words typed') + chip(s.histBefore + 1, ' messages in the history'), shot: [[0, prevShot(k)], [1.2, 'harness']] };
      case 'assemble': return { kick: tur(s.ti), h: 'The harness assembles the context',
        p: `Every model call is one request: the <b>system prompt</b> with the rules, the <b>chat history</b>, and the <b>${tools.length} tool schemas</b> read from <code>toolbox/*/tool.json</code>.`,
        chips: chip(fmt(cs.system), ' tokens · system prompt') + chip(fmt(cs.history), ' · chat history') + chip(fmt(cs.schemas), ' · 15 tool schemas') + chip(fmt(cs.total), ' tokens in, total'), shot: [[0, prevShot(k)], [1.0, 'harness']] };
      case 'decide': return { kick: tur(s.ti), h: `The LLM reads ${fmt(s.llm.tokens_in)} tokens and picks one tool of ${tools.length}`,
        p: `It does not answer yet. It writes a <b>tool call</b>: the name <code>${esc(s.call.name)}</code> and its arguments as JSON.`,
        chips: chip(fmt(s.llm.tokens_in), ' tokens in') + chip(fmt(s.llm.tokens_out), ' tokens out') + chip(secs(s.llm.seconds), ' model time') + chip('1 of ' + tools.length, ' tools chosen'), shot: [[0, prevShot(k)], [1.2, 'llm']] };
      case 'guard': return { kick: tur(s.ti), h: 'The guard checks the call, then MCP carries it',
        p: `The harness checks every argument against the tool’s <code>tool.json</code> schema. Only then does the call go over <b>MCP</b>, as a JSON-RPC <code>tools/call</code>, to the toolbox.`,
        chips: chip((s.call.guard.checked || []).length, ' argument checked') + chip('passed', '', 'g') + chip('tools/call', ' over MCP'), shot: [[0, prevShot(k)], [1.0, 'guard'], [3.4, 'guard'], [5.0, 'mcp']] };
      case 'erp': return { kick: tur(s.ti), h: `${s.call.name} calls the Ledgerline services`,
        p: `The tool runs as Emma, with her permissions. Ledgerline is a <b>black box</b>: data goes in, data comes out. Here it is ${s.call.services.length} service calls.`,
        chips: chip(s.call.services.length, ' service calls', 'e') + chip(msf(s.call.services.reduce((a, x) => a + x.ms, 0)), ' inside Ledgerline', 'e') + chip(msf(s.call.ms), ' for the whole tool'), shot: [[0, prevShot(k)], [1.2, 'erp']] };
      case 'docs': return { kick: tur(s.ti), h: `${s.call.name} reads the manuals`, p: 'This tool searches documents, not Ledgerline.', chips: chip(msf(s.call.ms), ' search'), shot: [[0, prevShot(k)], [1.0, 'docs']] };
      case 'result': return { kick: tur(s.ti), h: 'The result flows back as JSON',
        p: `The harness adds it to the history and calls the model again. The next request is <b>${fmt(s.next ? s.next.tokens_in : 0)}</b> tokens: the context grows with every step.`,
        chips: chip(msf(s.call.ms), ' tool time') + chip(fmt(s.next ? s.next.tokens_in : 0), ' tokens in, next call') + chip('+2', ' messages: the call and its result'), shot: [[0, prevShot(k)], [0.8, 'mid']] };
      case 'cycle': {
        const names = s.steps.flatMap((st) => st.tools.map((c) => c.name));
        const par = s.steps.some((st) => st.tools.length > 1);
        const bad = s.steps.flatMap((st) => st.tools).find((c) => c.result && c.result.ok === false);
        const all = s.steps.flatMap((st) => st.tools);
        const pre = all.find((c) => c.guard.writes && c.args.confirm === false && c.result && c.result.preview);
        const said = (c) => `<b>\u201c${esc((c.result || {}).error || '')}\u201d</b>${(c.result || {}).next_step ? ` Next step: <b>\u201c${esc(c.result.next_step)}\u201d</b>` : ''}`;
        const NUM = ['', 'One', 'Two', 'Three', 'Four', 'Five'];
        const parN = Math.max(...s.steps.map((st) => st.tools.length));
        let h, p;
        if (pre) { h = `A preview first: ${pre.name} with confirm: false`; p = `The system prompt says: preview before saving. Ledgerline is read, and <b>nothing is saved</b>. Estimated value <b>${money(pre.result.preview.estimated_value)}</b>, approver <b>${esc(pre.result.preview.approver || '-')}</b>.`; }
        else if (par) { const uniq = [...new Set(names)];
          const what = uniq.length < names.length ? `${uniq.join(', ')} on ${all.map((c) => esc(String(Object.values(c.args)[0] ?? ''))).join(' and ')}` : uniq.join(', ');
          h = `${NUM[parN] || parN} tool calls in one model call: ${what}`; p = `The model can ask for several tools at once. The harness runs each one through the guard and MCP and returns every result.${bad ? ` One comes back with <code>ok: false</code>: ${said(bad)}` : ''}`; }
        else if (bad) { h = `${bad.name} says no: ok is false`; p = `A tool can fail cleanly, and the model reads the failure like any other result. Error: ${said(bad)}`; }
        else if (s.steps.length > 1) { h = `The loop goes on: ${names.join(', then ')}`; p = 'Each step is the same path: the model picks, the guard checks, MCP carries, the tool runs, the result comes back.'; }
        else { h = `The model reads the result and calls another tool: ${names[0]}`; p = `Same path again, with new arguments: <code>${esc(j1(s.steps[0].tools[0].args, 56))}</code>. Every step adds the call and its result to the history.`; }
        const st0 = s.steps[0];
        const keys = [[0, prevShot(k)]]; let o = 0;
        for (const st of s.steps) {
          const d = cycleDur(st), svc = st.tools.some((c) => c.services.length);
          keys.push([o + 1.0, 'llm'], [o + 3.0, 'llm'], [o + 4.3, 'guardmcp'], [o + 5.6, svc ? 'erp' : 'docs'], [o + d - 1.6, svc ? 'erp' : 'docs'], [o + d - 0.2, 'mid']);
          o += d;
        }
        return { kick: tur(s.ti), h, p, shotKeys: keys,
          chips: s.steps.map((st) => chip(fmt(st.llm.tokens_in), ' in') + chip(fmt(st.llm.tokens_out), ' out') + chip(secs(st.llm.seconds), ' model')).join('') + chip(msf(s.steps.flatMap((x) => x.tools).reduce((a, c) => a + c.ms, 0)), ' tools'),
          shot: keys };
      }
      case 'reply': {
        const sm = tsum(s.ti), asks = /\?\s*$/.test(s.text.trim());
        return { kick: tur(s.ti), h: asks ? 'No tool this time: it writes a preview and asks Emma' : 'No tool this time: the model writes the answer',
          p: asks ? `The reply is built from the tool results, and it ends with a question. Nothing is saved until Emma says yes.` : `The answer is built from the tool results, not from memory. This turn: <b>${sm.calls}</b> model calls and <b>${sm.tools}</b> tool calls.`,
          chips: chip(fmt(s.llm.tokens_out), ' tokens out') + chip(secs(s.llm.seconds), ' to write it') + chip(sm.calls, ' model calls this turn') + chip(secs(sm.sec), ' model + tool time'), shot: [[0, prevShot(k)], [0.6, 'llm'], [3.0, 'left']] };
      }
      case 'write': {
        const c = s.steps[0].tools.find(isCommit), r = c.result || {};
        return { kick: tur(s.ti), h: `After her yes: ${c.name} with confirm: true`,
          p: `This time the tool saves. Ledgerline raises <b>${esc(r.request_no || r.po_no || '')}</b> and submits it. It is above Emma’s limit, so it lands in <b>Daniel’s approval inbox</b>.`,
          chips: chip(c.services.length, ' service calls', 'e') + chip(esc(r.request_no || ''), '', 'e') + chip(money(r.estimated_value || 0), ' estimated') + chip(esc(r.approver || ''), ' must approve'),
          shot: [[0, prevShot(k)], [1.0, 'llm'], [3.0, 'llm'], [4.3, 'guardmcp'], [5.6, 'erp'], [7.2, 'inbox']] };
      }
      case 'receipt': {
        const r = (s.commit || {}).result || {};
        return { kick: tur(s.ti), h: 'The receipt is read back from Ledgerline and shown to Emma',
          p: `The status is what Ledgerline holds, read with <code>pr_get</code> after the save, not what the model hopes: <b>${esc(r.request_no || '')}</b>, <b>${esc(r.status || '')}</b>, approver <b>${esc(r.approver || '')}</b>.`,
          chips: chip(esc(r.status_code || ''), ' status code', 'g') + chip(fmt(s.llm.tokens_in), ' tokens in') + chip(secs(s.llm.seconds), ' to write it') + chip(fmt(T.meta.totals.calls), ' model calls in all'), shot: [[0, prevShot(k)], [0.9, 'mid'], [3.0, 'llm'], [5.6, 'left']] };
      }
    }
    return { kick: '', h: '', p: '', chips: '', shot: [[0, 'overview']] };
  }
  S.forEach((s, k) => { s.cap = caption(s, k); const sh = s.cap.shot; s.endShot = sh[sh.length - 1][1]; });

  function runStage(k, t) {
    const s = S[k];
    shotAt(s.cap.shot, t);
    switch (s.kind) {
      case 'overview': ['harness', 'llm', 'toolbox', 'erp'].forEach((x) => F.active.add(x)); break;
      case 'arrive': {
        const u = seg(t, 0.7, 2.3);
        R.user.glow(u);
        if (u > 0 && u < 1) packet(R.user.at(eio(u)), 'req', `<div class="f3d-note sky"><div class="k">User message <b>Emma</b></div><div class="t">${esc(s.text)}</div></div>`);
        if (t >= 2.3) setHist(s.histBefore + 1);
        F.active.add('harness');
        lHist.set(histHTML(t >= 2.3 ? s.histBefore + 1 : s.histBefore)).show(seg(t, 1.6, 2.2));
        break;
      }
      case 'assemble': {
        const cs = T.context_split || { system: 1, history: 1, schemas: 1, total: 1 };
        const tot = cs.system + cs.history + cs.schemas;
        const n = (x) => Math.max(3, Math.round(56 * x / tot));
        tokenStream(R.sys, t, 0.8, 1.6, n(cs.system), 0.8); tokenStream(R.hist, t, 1.0, 0.8, n(cs.history), 0.8); tokenStream(R.sch, t, 1.3, 2.4, n(cs.schemas), 0.8);
        R.sys.glow(seg(t, 0.8, 2.8)); R.hist.glow(seg(t, 1.0, 2.6)); R.sch.glow(seg(t, 1.3, 4.0));
        const fill = eio(seg(t, 1.2, 4.3)); setCtx(Math.round(cs.total * fill));
        lSys.set(`<div class="f3d-note sky" style="max-width:calc(380px*var(--u))"><div class="k">System prompt <b>${fmt(cs.system)} tokens</b></div><div class="t">${esc(T.system_prompt.split('\n').slice(0, 1)[0].slice(0, 150))}…</div><div class="t" style="margin-top:4px;color:#121317">${esc((T.system_prompt.split('\n')[2] || '').slice(0, 120))}…</div></div>`).show(seg(t, 0.3, 0.8));
        lHist.set(histHTML(s.histBefore, cs.history)).show(seg(t, 0.5, 1.0));
        lSchema.set(`<div class="f3d-note sky"><div class="k">Tool schemas <b>${tools.length} · ${fmt(cs.schemas)} tokens</b></div><pre>${jsonSpan(j1({ name: tools[1].name, parameters: { item_code: 'string' } }, 58))}</pre><div class="t">… and ${tools.length - 1} more, one per tool.json</div></div>`).show(seg(t, 0.7, 1.2));
        lCtx.set(ctxHTML(Math.round(cs.total * fill), 'Context for this call')).show(seg(t, 1.2, 1.6));
        F.active.add('harness');
        break;
      }
      case 'decide': {
        const e = s.llm;
        R.ctx.glow(seg(t, 0.2, 1.6)); tokenStream(R.ctx, t, 0.2, 1.3, 56, 0.9);
        lCtx.set(ctxHTML(e.tokens_in, 'Sent to the model')).show(1 - seg(t, 1.6, 2.0));
        F.llmHeat = seg(t, 0.8, 1.6);
        setCards(seg(t, 1.1, 2.9), cardsOf([s.call]), seg(t, 3.0, 3.6));
        if (t > 3.3) lOut.set(outNote(callText([s.call]), seg(t, 3.3, 4.7), llmSub(e))).show(seg(t, 3.3, 3.5));
        F.active.add('llm');
        break;
      }
      case 'guard': {
        const c = s.call;
        setCards(1, cardsOf([c]), 1, seg(t, 0, 1.0));
        F.llmHeat = 1 - seg(t, 0, 1);
        const u1 = seg(t, 0.4, 1.9);
        if (u1 > 0 && u1 < 1) { R.call.glow(u1); packet(R.call.at(eio(u1)), 'req', callNote(c)); }
        if (t >= 1.9 && t < 3.6) { packet(V(P.guard.x - 0.15, P.guard.y, P.guard.z), 'req'); }
        F.guard = t >= 1.7 ? 1 : 0; F.guardOk = seg(t, 2.6, 3.2);
        lGuard.set(guardNote(c, seg(t, 2.0, 3.0))).show(seg(t, 1.8, 2.1));
        const u2 = seg(t, 3.6, 5.3);
        if (u2 > 0) { R.mcp.glow(Math.min(u2, 0.999)); packet(R.mcp.at(eio(u2)), 'req', `<div class="f3d-note sky"><div class="k">MCP request <b>JSON-RPC 2.0</b></div><pre>${jsonBlock(c.mcp.request, { width: 56 })}</pre></div>`, 1); }
        if (t > 5.0) { F.cart = toolIx[c.name]; F.cartLift = seg(t, 5.0, 5.6); F.active.add('toolbox');
          lTool.set(`<span class="f3d-tag on"><i></i>${esc(c.name)} <small>tool.py runs</small></span>`).show(seg(t, 5.2, 5.5)); }
        F.active.add('guard'); if (t > 3.0) F.hide.add('mcp');
        break;
      }
      case 'erp': case 'docs': {
        const c = s.call, n = c.services.length;
        F.cart = toolIx[c.name]; F.cartLift = 1; F.active.add(s.kind === 'erp' ? 'erp' : 'docs');
        if (s.kind === 'docs') {
          const u = seg(t, 0.8, 1.6), ub = seg(t, 1.9, 2.7);
          if (u > 0 && u < 1) { R.doc.glow(u); packet(R.doc.at(eio(u)), 'req', '', 0, 0.62); }
          if (ub > 0 && ub < 1) { R.docBack.glow(ub); packet(R.docBack.at(eio(ub)), 'res', '', 0, 0.55); }
          lDocs.set(docsNote(c)).show(seg(t, 1.4, 1.8));
          break;
        }
        const span = Math.min(3.6, 0.34 * n);
        for (let i = 0; i < n; i++) {
          const a = 1.2 + (i / n) * span, u = seg(t, a, a + 0.75), ub = seg(t, a + 0.8, a + 1.5);
          const sv = c.services[i];
          if (u > 0 && u < 1) { R.svc.glow(u); packet(R.svc.at(eio(u)), 'svc', i === 0 || n <= 4 ? `<div class="f3d-note ember"><div class="k">${esc(sv.svc)} <b>data in</b></div><pre>${jsonSpan(j1(sv.in, 44))}</pre></div>` : '', 1, 0.7); }
          if (ub > 0 && ub < 1) { R.svcBack.glow(ub); packet(R.svcBack.at(eio(ub)), sv.rc === 'E' ? 'svc' : 'res', '', 0, 0.6); }
          if (t > a + 0.65 && t < a + 0.95) F.erpHeat = 1;
        }
        lERP.set(svcList(c, Math.ceil(seg(t, 1.2, 1.2 + span + 0.8) * n))).show(seg(t, 1.2, 1.5));
        break;
      }
      case 'result': {
        const c = s.call; if (t > 3.4) F.hide.add('llm');
        F.cart = toolIx[c.name]; F.cartLift = 1 - seg(t, 0.3, 1.0);
        const u = seg(t, 0.2, 3.6);
        R.backCtx.glow(u);
        if (u > 0 && u < 1) packet(R.backCtx.at(eio(u)), c.result.ok === false ? 'svc' : 'res', resultNote(c), 1 - seg(u, 0.8, 0.95));
        note(V(P.llm.x + 1.8, P.llm.y + 0.3, P.llm.z + 1.2), resultNote(c), seg(t, 3.5, 3.8), [0, 0.5]);
        if (t > 2.6) { setHist(s.histBefore + 2); }
        setCtx(t > 2.6 ? s.ctxAfter : s.ctxBefore);
        lCtx.set(ctxHTML(t > 2.6 ? s.ctxAfter : s.ctxBefore, t > 2.6 ? 'Next call' : 'Context')).show(seg(t, 2.6, 3.0));
        F.llmHeat = seg(t, 3.6, 4.4);
        break;
      }
      case 'cycle': {
        let t0 = 0;
        for (const st of s.steps) {
          const d = cycleDur(st);
          const lastSt = st === s.steps[s.steps.length - 1];
          if (t >= t0 && (t < t0 + d || lastSt)) { playStep(st, t - t0, k, { last: lastSt }); }
          if (t >= t0 + d - 1.1) { setCtx((st.next || {}).tokens_in || s.ctxAfter); }
          t0 += d;
        }
        if (t > s.dur - 1.4) lCtx.set(ctxHTML(s.ctxAfter, 'Next call')).show(seg(t, s.dur - 1.4, s.dur - 1.0));
        break;
      }
      case 'write': {
        const st = s.steps[0], c = st.tools.find(isCommit), r = c.result || {};
        let wroteAt = 99;
        const end = playStep(st, t, k, { noReturn: true, onWrite(tt, a, span) {
          const save = c.services.findIndex((x) => x.svc.endsWith('_submit')) / c.services.length;
          wroteAt = a + Math.max(save, 0.5) * span + 0.7;
        } });
        // the saved document drops into Daniel's inbox
        const u = seg(t, wroteAt, wroteAt + 1.4);
        if (u > 0) { R.inbox.glow(Math.min(u, 0.999)); F.active.add('inbox'); }
        if (u > 0 && u < 1) packet(R.inbox.at(eio(u)), 'doc', '', 0, 1);
        const list = (T.inbox.after || {}).waiting || [];
        if (u >= 1) { setInbox('after'); F.inboxHeat = 1 - seg(t, wroteAt + 1.4, wroteAt + 4); }
        lInbox.set(inboxHTML(u >= 1 ? list : ((T.inbox.before || {}).waiting || []), u >= 1 ? (r.request_no || r.po_no) : null)).show(seg(t, wroteAt - 0.6, wroteAt - 0.2));
        if (t > end - 0.5) setCtx(s.ctxAfter);
        break;
      }
      case 'reply': case 'receipt': {
        const e = s.llm;
        if (s.kind === 'receipt') {
          const c = s.commit, u0 = seg(t, 0.2, 2.6);
          R.backCtx.glow(u0);
          if (u0 > 0 && t < 3.0) packet(R.backCtx.at(eio(u0)), 'ok', resultNote(c), 1 - seg(t, 2.7, 3.0));
          setInbox('after'); t -= 2.6;
        }
        R.ctx.glow(seg(t, 0, 1.0)); tokenStream(R.ctx, t, 0, 0.8, 30, 0.6);
        F.llmHeat = seg(t, 0.5, 1.0) * (1 - seg(t, 3.6, 4.2));
        const plain = s.text.replace(/\*\*/g, '').replace(/^\s*[*-]\s+/gm, '').split(/\n+/).map((x) => x.trim()).filter(Boolean).join(' \u00b7 ');
        if (t > 1.0) {
          F.hide.add('llm');
          note(V(P.llm.x + 1.8, P.llm.y + 0.3, P.llm.z + 1.2), `<div class="f3d-note sky" style="max-width:calc(420px*var(--u))"><div class="k">Tokens out <b>${fmt(e.tokens_out)} \u00b7 ${secs(e.seconds)} \u00b7 no tool call</b></div><div class="t" style="color:#121317">${esc(plain.slice(0, Math.round(plain.length * seg(t, 1.0, 2.8))).slice(0, 210))}${plain.length > 210 && t > 2.4 ? '\u2026' : ''}</div></div>`, seg(t, 1.0, 1.2), [0, 0.5]);
        }
        if (s.kind === 'receipt' && t > -2.4) {
          const r = (s.commit || {}).result || {};
          note(V(P.llm.x - 1.7, P.llm.y + 0.3, P.llm.z + 1.2), `<div class="f3d-note green"><div class="k">Receipt <b>read back from Ledgerline with pr_get</b></div><pre>${jsonBlock(r, { keys: ['request_no', 'status', 'status_code', 'estimated_value', 'approver', 'approved_by'], width: 50 })}</pre></div>`, seg(t, 0.2, 0.6), [1, 0.5]);
        }
        const u = seg(t, 2.8, 4.4);
        R.reply.glow(u);
        if (u > 0 && u < 1) packet(R.reply.at(eio(u)), s.kind === 'receipt' ? 'ok' : 'res', '', 0);
        F.active.add('llm');
        break;
      }
    }
  }
  function histHTML(n, tok) {
    return `<div class="f3d-note sky"><div class="k">Chat history <b>${n} message${n === 1 ? '' : 's'}${tok ? ' · ' + fmt(tok) + ' tokens' : ''}</b></div></div>`;
  }
  function ctxHTML(tokens, title) {
    return `<div class="f3d-note sky" style="text-align:center"><div class="k" style="justify-content:center">${esc(title)}</div><div class="cnt">${fmt(tokens)}</div><div class="t" style="text-align:center">tokens in</div></div>`;
  }

  /* chat rail */
  let railKey = '';
  function renderRail(k, t) {
    const items = [];
    for (const m of rail) {
      if (m.k > k) break;
      if (m.k === k && t < m.t) { if (m.who === 'bot' && t > 0.2) items.push({ typing: true }); continue; }
      const p = m.k === k && m.who === 'bot' ? seg(t, m.t, m.t + 1.7) : 1;
      items.push({ ...m, p });
    }
    // while tools run, a typing indicator
    const s = S[k];
    if (!items.some((i) => i.typing) && ['assemble', 'decide', 'guard', 'erp', 'docs', 'result', 'cycle', 'write'].includes(s.kind)) items.push({ typing: true });
    const keyNow = items.map((i) => (i.typing ? 'T' : `${i.who}${i.k}:${i.p.toFixed(2)}`)).join('|');
    if (keyNow === railKey) return; railKey = keyNow;
    const html = items.slice(-5).map((i) => {
      if (i.typing) return '<div class="f3d-typing"><i></i><i></i><i></i></div>';
      if (i.who === 'emma') return `<div class="f3d-who emma">Emma</div><div class="f3d-b emma">${esc(i.text)}</div>`;
      let text = i.text;
      if (i.p < 1) { const plain = i.text; text = plain.slice(0, Math.max(1, Math.round(plain.length * i.p))); }
      const used = (i.used || []).map((c) => `<span class="${c.guard.writes ? 'w' : ''}">${esc(c.name)}</span>`).join('');
      const r = (i.commit || {}).result;
      const rc = r ? `<div class="f3d-rcpt" style="opacity:${seg(i.p, 0.6, 1)}"><b>Receipt, read back from Ledgerline</b><code>${esc(r.request_no || r.po_no)}</code> · ${esc(r.status)} · approver <code>${esc(r.approver || '')}</code></div>` : '';
      return `<div class="f3d-who">Ask Northbridge</div><div class="f3d-b bot">${md(text)}</div>${i.p >= 1 && used ? `<div class="f3d-uses">${used}</div>` : ''}${rc}`;
    }).join('');
    msgsEl.innerHTML = html || '<div class="f3d-empty">Emma\u2019s chat appears here, word for word as it happened in the recorded run.</div>';
    // the newest messages stay; older ones leave the rail rather than spill past its top
    const top = msgsEl.getBoundingClientRect().top + 2;
    while (msgsEl.children.length > 1 && msgsEl.firstElementChild.getBoundingClientRect().top < top) msgsEl.removeChild(msgsEl.firstElementChild);
    while (msgsEl.children.length > 1 && /f3d-(uses|rcpt)/.test(msgsEl.firstElementChild.className)) msgsEl.removeChild(msgsEl.firstElementChild);
  }

  /* HUD */
  let hudK = -1;
  function renderHUD(k) {
    if (hudK === k) return; hudK = k;
    const c = S[k].cap;
    hud.pill.textContent = k === 0 ? `${S.length - 1} steps` : `Step ${k} of ${S.length - 1}`;
    hud.turn.textContent = c.kick; hud.h2.innerHTML = c.h; hud.p.innerHTML = c.p; hud.chips.innerHTML = c.chips || '';
    prog.forEach((p, i) => { p.classList.toggle('cur', i === k); p.classList.toggle('done', i < k); });
  }

  /* apply frame-level effects to the meshes */
  const BLOCK_TAG = { harness: tHarness, llm: tLLM, guard: tGuard, toolbox: tToolbox, erp: tERP, inbox: tInbox, docs: tDocs, mcp: tMCP, app: tApp };
  function applyFrame(clk) {
    coreMat.emissiveIntensity = 0.55 + F.llmHeat * 1.6;
    coreLight.intensity = F.llmHeat * 6;
    core.rotation.set(clk * 0.35, clk * 0.5, 0);
    LL.position.y = P.llm.y + Math.sin(clk * 0.9) * 0.08;
    beam.material.opacity = 0.06 + F.llmHeat * 0.1; haloRing.material.emissiveIntensity = 0.55;
    coreRing.rotation.set(Math.PI / 2 + Math.sin(clk * 0.6) * 0.25, clk * 0.4, 0);
    coreRing2.rotation.set(Math.PI / 2.6, -clk * 0.5, Math.cos(clk * 0.5) * 0.3);
    const sc = 1 + F.llmHeat * 0.08 * (0.6 + 0.4 * Math.sin(clk * 6)); core.scale.setScalar(sc);
    // guard
    const gOk = F.guardOk;
    ringMat.emissive.setHex(gOk > 0 ? C.green : C.sky);
    ringMat.emissiveIntensity = F.guard ? 0.35 + gOk * 0.9 : 0.08;
    scan.material.color.setHex(gOk > 0 ? C.green : C.sky);
    scan.material.opacity = F.guard ? 0.12 + 0.18 * gOk : 0;
    // toolbox cartridge
    carts.forEach((m, i) => { const on = i === F.cart; m.position.y = 0.63 + (on ? F.cartLift * 0.45 : 0); m.material.emissiveIntensity = on ? 0.15 + 0.5 * F.cartLift : 0; });
    // erp
    M.ember.emissiveIntensity = F.erpHeat * 0.22; M.emberDark.emissiveIntensity = F.erpHeat * 0.6;
    slots.forEach((m, i) => (m.material.emissiveIntensity = F.erpHeat * 0.8));
    trayMat.emissiveIntensity = F.inboxHeat * 0.35; inDocMat[1].emissiveIntensity = 0.12 + F.inboxHeat * 0.5;
    // block tags: the active ones lit
    for (const [n, t] of Object.entries(BLOCK_TAG)) { const on = F.active.has(n); t.inner.firstChild.classList.toggle('on', on); t.show(F.hide.has(n) ? 0 : on ? 1 : 0.86); }
    toks.count = tokUsed; toks.instanceMatrix.needsUpdate = true;
  }

  /* label scale with distance, so labels keep some depth */
  const _w = new THREE.Vector3();
  const _n = new THREE.Vector3();
  const FLOOR = { tag: 0.82, note: 0.94, card: 0.92 };
  function scaleLabels() {
    const railR = 470 * (W / 1920);
    for (const L of labelList) {
      if (!L.o.visible) continue;
      L.o.getWorldPosition(_w);
      const d = _w.distanceTo(camera.position);
      const s = Math.max(FLOOR[L.kind] || 0.9, Math.min(1.1, 24 / d));
      if (Math.abs((L._s || 0) - s) > 0.01) { L._s = s; L.inner.style.scale = s.toFixed(3); }
      if (L.kind === 'tag') { // block names stay out of the chat rail, the title and the footer
        _n.copy(_w).project(camera);
        const x = (_n.x + 1) / 2 * W, y = (1 - _n.y) / 2 * Hh;
        const f = clamp01((x - railR) / 60) * clamp01((Hh * 0.885 - y) / 50) * clamp01((y - Hh * 0.2) / 40) * (_n.z < 1 ? 1 : 0);
        L.inner.style.opacity = (L.op * f).toFixed(3);
      }
    }
  }


  /* keep every label inside the figure: notes slide back in, block tags and cards that would cross the edge are hidden */
  function fitLabels() {
    const er = el.getBoundingClientRect(); if (!er.width) return;
    const z = er.width / W, m = 26 * z;
    const box = { l: er.left + m, r: er.right - m, t: er.top + m, b: er.bottom - m };
    // the free stage: right of the chat rail, below the title, above the footer
    const rr0 = railEl.getBoundingClientRect(), hr = hudEl.getBoundingClientRect(), fr = footEl.getBoundingClientRect();
    const free = { l: Math.max(box.l, rr0.right + 10 * z), r: box.r, t: Math.max(box.t, hr.bottom + 8 * z), b: Math.min(box.b, fr.top - 6 * z) };
    const hits = (l, r, t, b) => [rr0, hr, fr].some((o) => l < o.right && r > o.left && t < o.bottom && b > o.top);
    for (const L of labelList) {
      const outer = L.o.element;
      if (!L.o.visible || outer.style.display === 'none') continue;
      if (parseFloat(L.inner.style.opacity || '1') < 0.03) { outer.style.display = 'none'; continue; }
      const tx = L._tx || 0, ty = L._ty || 0;
      const ri = L.inner.getBoundingClientRect(), ro = outer.getBoundingClientRect();
      if (!ri.width) continue;
      // the union of the laid-out box and the scaled box, both moved by the current clamp
      const l = Math.min(ri.left, ro.left) - tx * z, rr = Math.max(ri.right, ro.right) - tx * z;
      const t = Math.min(ri.top, ro.top) - ty * z, b = Math.max(ri.bottom, ro.bottom) - ty * z;
      if (L.kind === 'note') {
        const B = (rr - l <= free.r - free.l && b - t <= free.b - free.t) ? free : box;
        if (rr - l > B.r - B.l || b - t > B.b - B.t) { outer.style.display = 'none'; continue; }
        let dx = 0, dy = 0;
        if (l < B.l) dx = B.l - l; else if (rr > B.r) dx = B.r - rr;
        if (t < B.t) dy = B.t - t; else if (b > B.b) dy = B.b - b;
        const nx = dx / z, ny = dy / z;
        if (Math.abs(nx - tx) > 0.5 || Math.abs(ny - ty) > 0.5) { L._tx = nx; L._ty = ny; outer.style.translate = `${nx.toFixed(1)}px ${ny.toFixed(1)}px`; }
      } else if (l < box.l || rr > box.r || t < box.t || b > box.b || hits(l, rr, t, b)) {
        outer.style.display = 'none';
      }
    }
  }

  /* ---------- layout ---------- */
  let W = 0, Hh = 0;
  function resize() {
    W = el.clientWidth; Hh = el.clientHeight; if (!W || !Hh) return;
    const u = mode === 'deck' ? W / 1660 : W / 1920; el.style.setProperty('--u', u.toFixed(4));
    const rect = el.getBoundingClientRect(); const zoom = rect.width / W || 1;
    renderer.setPixelRatio(Math.min(2, (window.devicePixelRatio || 1) * zoom));
    renderer.setSize(W, Hh, false); renderer.domElement.style.width = '100%'; renderer.domElement.style.height = '100%';
    labels.setSize(W, Hh);
    camera.aspect = W / Hh;
    // centre the picture in the space right of the chat rail and below the title
    const rail = 452 * u, top = (mode === 'deck' ? 250 : 150) * u;
    camera.setViewOffset(W, Hh, -rail / 2, -top / 2 + 40 * u, W, Hh);
    camera.updateProjectionMatrix();
  }
  const ro = new ResizeObserver(() => { resize(); draw(); }); ro.observe(el);

  /* ---------- time ---------- */
  let k = 0, t = 0, playing = false, auto = false, hold = 0, last = performance.now(), clk = 0, raf = 0, dead = false;
  /* narration: one clip per stage (narration.json + audio/), Rajat's recorded voice */
  let NAR = null, voiceOn = true, narrPlay = false, paused = false, clip = null, clipK = -1, rate = 1;
  const audios = [];
  const speakEl = $('.f3d-speak'), bNarr = $('.b-narr'), bVoice = $('.b-voice');
  function stopClip() { if (clip) { clip.pause(); } clip = null; clipK = -1; rate = 1; }
  function playClip(n) {
    stopClip();
    if (!NAR || !voiceOn || !audios[n]) return;
    clip = audios[n]; clipK = n;
    try { clip.currentTime = 0; } catch (e) {}
    const d = NAR.stages[n].duration || clip.duration || S[n].dur;
    rate = Math.max(0.55, Math.min(1, S[n].dur / Math.max(0.1, d * 0.92)));   // stretch the motion towards the voice
    const pr = clip.play(); if (pr && pr.catch) pr.catch((e) => { console.warn('flow3d narration', e.name); });
  }
  const clipDone = () => !clip || clip.ended || (clip.paused && !paused);
  function syncButtons() {
    bNarr.classList.toggle('on', narrPlay);
    bNarr.innerHTML = narrPlay ? `${paused ? ICON.play : ICON.pause}<span>${paused ? 'Resume' : 'Pause'}</span>` : `${ICON.narr}<span>Play with narration</span>`;
    bVoice.classList.toggle('on', voiceOn); bVoice.setAttribute('aria-pressed', String(voiceOn));
    bVoice.innerHTML = `${voiceOn ? ICON.voiceOn : ICON.voiceOff}<span>${voiceOn ? 'Voice on' : 'Voice off'}</span>`;
  }
  function draw() {
    if (!W) resize();
    resetFrame();
    applyPersistent(k, t);
    runStage(k, t);
    applyFrame(clk);
    camera.position.copy(cam.pos);
    if (!still) { camera.position.x += Math.sin(clk * 0.21) * 0.35; camera.position.y += Math.sin(clk * 0.17) * 0.18; }
    camera.lookAt(cam.tgt);
    renderHUD(k); renderRail(k, t);
    renderer.render(scene, camera);
    scaleLabels();
    labels.render(scene, camera);
    fitLabels();
    const speaking = !!clip && clipK === k && !clip.ended;
    if (speakEl.hidden === speaking) speakEl.hidden = !speaking;
    speakEl.classList.toggle('paused', paused);
  }
  function loop(now) {
    if (dead) return;
    const dt = Math.min(0.05, (now - last) / 1000); last = now;
    if (!still) clk += dt;
    // the slide was left (deck): silence
    if ((clip || narrPlay) && !el.getClientRects().length) { stopClip(); narrPlay = false; paused = false; syncButtons(); }
    if (playing && !paused) {
      t += dt * (clipK === k ? rate : 1);
      if (t >= S[k].dur) {
        t = S[k].dur;
        if (narrPlay) {
          if (clipDone()) { hold += dt; if (hold > 0.9) { hold = 0; if (k < S.length - 1) { k++; t = 0; playClip(k); } else { narrPlay = false; playing = false; syncButtons(); } } }
        } else if (auto) { hold += dt; if (hold > 1.6) { hold = 0; k = (k + 1) % S.length; t = 0; } } else playing = false;
      }
    }
    draw();
    raf = requestAnimationFrame(loop);
  }
  const api = {
    get stage() { return k; }, get count() { return S.length; }, stages: S.map((s) => ({ kind: s.kind, title: s.cap.h.replace(/<[^>]+>/g, ''), dur: s.dur })),
    go(n, instant = false) {
      k = Math.max(0, Math.min(S.length - 1, n)); t = instant ? S[k].dur : 0; playing = !instant; hold = 0; paused = false;
      if (instant) { stopClip(); if (narrPlay) { narrPlay = false; } } else playClip(k);
      syncButtons(); draw();
    },
    next() { api.go(k + 1); }, prev() { api.go(k - 1, true); }, replay() { api.go(k, false); },
    autoplay(on = !auto) { if (on) { narrPlay = false; stopClip(); syncButtons(); } auto = on; el.querySelector('.b-auto').classList.toggle('on', auto); el.querySelector('.b-auto').innerHTML = `${auto ? ICON.pause : ICON.play}<span>${auto ? 'Pause' : 'Autoplay'}</span>`; if (auto) { playing = true; if (t >= S[k].dur) { k = (k + 1) % S.length; t = 0; } } else playing = false; },
    /* every stage in order with its clip; again = pause or resume */
    narrate(from) {
      if (!NAR) return false;
      if (narrPlay) { api.togglePause(); return true; }
      if (auto) api.autoplay(false);
      voiceOn = true; narrPlay = true; paused = false;
      k = from !== undefined ? from : (k >= S.length - 1 ? 0 : k); t = 0; hold = 0; playing = true; playClip(k); syncButtons(); return true;
    },
    togglePause() {
      if (!narrPlay && !clip && !playing) return false;
      paused = !paused;
      if (clip) { if (paused) clip.pause(); else if (!clip.ended) { const pr = clip.play(); if (pr && pr.catch) pr.catch(() => {}); } }
      if (!paused && t < S[k].dur) playing = true;
      syncButtons(); return true;
    },
    voice(on = !voiceOn) { voiceOn = on; if (!on) stopClip(); syncButtons(); },
    get narrating() { return narrPlay || (!!clip && !clip.ended); }, get paused() { return paused; },
    audioState() { return audios.map((a, i) => ({ k: i, readyState: a.readyState, duration: a.duration, error: a.error && a.error.code, src: a.currentSrc.split('/').pop() })).concat([{ current: clipK, time: clip ? clip.currentTime : null, playing: !!clip && !clip.paused }]); },
    seek(n, sec) { stopClip(); k = Math.max(0, Math.min(S.length - 1, n)); t = sec === 'end' || sec === undefined ? S[k].dur : Math.min(sec, S[k].dur); playing = false; draw(); },
    render() { draw(); }, resize() { resize(); draw(); },
    destroy() { dead = true; stopClip(); cancelAnimationFrame(raf); ro.disconnect(); renderer.dispose(); removeEventListener('keydown', onKey, true); el.innerHTML = ''; },
  };
  // in the deck, Space pauses and resumes the narration instead of stepping the deck (capture phase runs before plates.js)
  function onKey(e) {
    if (mode !== 'deck' || e.key !== ' ' || !el.getClientRects().length || !api.narrating) return;
    e.preventDefault(); e.stopImmediatePropagation(); api.togglePause();
  }
  addEventListener('keydown', onKey, true);
  el.querySelector('.b-prev').addEventListener('click', (e) => { e.stopPropagation(); api.prev(); });
  el.querySelector('.b-next').addEventListener('click', (e) => { e.stopPropagation(); api.next(); });
  el.querySelector('.b-replay').addEventListener('click', (e) => { e.stopPropagation(); api.replay(); });
  el.querySelector('.b-auto').addEventListener('click', (e) => { e.stopPropagation(); api.autoplay(); });
  bNarr.addEventListener('click', (e) => { e.stopPropagation(); api.narrate(); });
  bVoice.addEventListener('click', (e) => { e.stopPropagation(); api.voice(); });
  prog.forEach((p) => p.addEventListener('click', (e) => { e.stopPropagation(); api.go(+p.dataset.k); }));
  // narration.json must belong to this trace and have one clip per stage; otherwise the figure stays silent
  if (opts.narration !== false) {
    const src = typeof opts.narration === 'object' ? Promise.resolve(opts.narration) : fetch(new URL('narration.json', HERE)).then((r) => (r.ok ? r.json() : null));
    src.then((n) => {
      if (!n || !Array.isArray(n.stages) || n.stages.length !== S.length || n.stages.some((x, i) => x.kind !== S[i].kind)
          || (n.trace_recorded_live && T.meta.recorded_live && n.trace_recorded_live !== T.meta.recorded_live)) {
        if (n) console.warn('flow3d: narration.json does not match this trace; narration off'); return;
      }
      NAR = n;
      n.stages.forEach((x, i) => { const a = new Audio(); a.preload = 'auto'; a.src = new URL(x.audio, HERE).href; audios[i] = a; });
      bNarr.hidden = false; bVoice.hidden = false; syncButtons();
    }).catch(() => {});
  }
  resize();
  if (opts.stage !== undefined) api.seek(opts.stage, opts.t); else draw();
  if (!still) raf = requestAnimationFrame(loop);
  if (opts.autoplay) api.autoplay(true);
  return api;
}

export async function loadTrace(url = new URL('trace.json', HERE)) {
  const r = await fetch(url); if (!r.ok) throw new Error('trace.json: ' + r.status); return r.json();
}
