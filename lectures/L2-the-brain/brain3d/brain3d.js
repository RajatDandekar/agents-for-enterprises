/* brain3d.js — "The Brain": one question followed through a real language model, in one 3D scene.
   Agentic Systems Engineering, Lecture 2 (Vizuara, Dr. Rajat Dandekar).

   import { mountBrain3D } from './brain3d/brain3d.js';
   const b = mountBrain3D(el, { trace, section: 3, mode: 'deck' | 'standalone' });
   b.go(k, instant)          // show step k of the current section (0 = the section's first state)
   b.setSection(n, k, inst)  // jump to section n (1..9), step k
   b.next(); b.prev(); b.replay(); b.autoplay(on); b.seek(n, k, seconds|'end'); b.attach(newEl); b.setTemperature(T)
   b.sections                // [{n, title, steps}] ; b.count = states in the current section

   Earlier sections stay in the scene, dimmed, so the whole trace so far is on screen.
   Every number on screen is read from trace.json, recorded by capture_trace.py on Modal from
   Qwen/Qwen2.5-0.5B-Instruct. Needs an import map for "three" and "three/addons/" (three@0.160.0). */
import * as THREE from 'three';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const HERE = new URL('./', import.meta.url);
const C = { sky: 0x3c90ff, skyDeep: 0x0b57d0, ember: 0xc4511f, green: 0x1e8e5a, ink: 0x121317, slate: 0x5d6b85 };

/* ------------------------------------------------------------------ small helpers */
const clamp01 = (x) => Math.max(0, Math.min(1, x));
const seg = (t, a, b) => clamp01((t - a) / (b - a));
const eio = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const eo = (x) => 1 - Math.pow(1 - x, 3);
const lerp = (a, b, t) => a + (b - a) * t;
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const fmt = (n) => Number(n).toLocaleString('en-GB');
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const pct = (p) => { const v = p * 100; return (v >= 99.95 ? '100' : v >= 9.95 ? v.toFixed(0) : v >= 0.995 ? v.toFixed(0) : v >= 0.1 ? v.toFixed(1) : v.toFixed(2)) + '%'; };
const vis = (s) => String(s).replace(/\r/g, '').replace(/\n/g, '⏎').replace(/\t/g, '⇥');
/* a token as text in a label: quotes, a visible leading space, long ones cut */
function tq(s, max = 14) {
  let v = vis(s);
  const lead = v.startsWith(' ');
  if (lead) v = v.slice(1);
  if (v.length > max) v = v.slice(0, max - 1) + '…';
  return `<span class="b3d-tq">${lead ? '<i class="sp">␣</i>' : ''}${esc(v) || '<i class="sp">␣</i>'}</span>`;
}
const isWordish = (s) => /^\s?[A-Za-z0-9][A-Za-z0-9,.'-]*$/.test(s);
function hasWebGL() {
  try { const c = document.createElement('canvas'); return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl'))); }
  catch (e) { return false; }
}

/* ------------------------------------------------------------------ styles */
const CSS = `
.brain3d{position:absolute;inset:0;overflow:hidden;--u:1;--f:"Google Sans Flex","Google Sans","Segoe UI",Roboto,Arial,sans-serif;
  --mono:"Google Sans Code","IBM Plex Mono",ui-monospace,Menlo,monospace;font-family:var(--f);font-size:calc(16px*var(--u));line-height:1.4;text-align:left;color:#121317;
  background:radial-gradient(52% 60% at 92% 0%,rgba(125,184,255,.30) 0%,rgba(125,184,255,0) 70%),
             radial-gradient(40% 50% at 22% 100%,rgba(188,220,255,.32) 0%,rgba(188,220,255,0) 70%),
             linear-gradient(180deg,#eef5ff 0%,#f9fbff 55%,#ffffff 100%);-webkit-font-smoothing:antialiased;user-select:none}
.brain3d canvas{display:block;position:absolute;inset:0}
.b3d-vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(120% 90% at 60% 45%,rgba(255,255,255,0) 62%,rgba(214,228,246,.38) 100%)}
.b3d-labels{position:absolute;inset:0;pointer-events:none;z-index:1;isolation:isolate}
.b3d-rail,.b3d-hud,.b3d-foot{z-index:3}
.b3d-l{will-change:opacity}
.b3d-tq{font-family:var(--mono);font-weight:560;letter-spacing:-.02em;white-space:pre}
.b3d-tq .sp{font-style:normal;color:#9aa0aa;font-weight:400;margin-right:1px}
.b3d-tag{display:inline-flex;align-items:center;gap:calc(9px*var(--u));padding:calc(8px*var(--u)) calc(15px*var(--u));border-radius:999px;
  background:rgba(255,255,255,.88);border:1px solid rgba(18,19,23,.10);box-shadow:0 6px 20px rgba(18,19,23,.08);
  font:540 calc(18px*var(--u))/1.1 var(--f);white-space:nowrap;color:#121317;letter-spacing:-.005em}
.b3d-tag i.d{width:calc(10px*var(--u));height:calc(10px*var(--u));border-radius:50%;background:#3c90ff;flex:none}
.b3d-tag small{font:400 calc(16px*var(--u))/1.1 var(--f);color:#5f636b}
.b3d-tag.green i.d{background:#1e8e5a}.b3d-tag.ember i.d{background:#c4511f}.b3d-tag.slate i.d{background:#8a93a6}
.b3d-tag.on{background:#fff;border-color:rgba(60,144,255,.55);box-shadow:0 0 0 4px rgba(60,144,255,.14),0 10px 26px rgba(11,87,208,.14)}
.b3d-tag.green.on{border-color:rgba(30,142,90,.55);box-shadow:0 0 0 4px rgba(30,142,90,.13),0 10px 26px rgba(30,142,90,.14)}
.b3d-tag.ember.on{border-color:rgba(196,81,31,.55);box-shadow:0 0 0 4px rgba(196,81,31,.13),0 10px 26px rgba(196,81,31,.14)}
.b3d-chip{display:inline-flex;align-items:baseline;gap:calc(7px*var(--u));padding:calc(6px*var(--u)) calc(11px*var(--u));border-radius:calc(10px*var(--u));
  background:rgba(255,255,255,.94);border:1px solid rgba(18,19,23,.10);box-shadow:0 4px 14px rgba(18,19,23,.08);font:500 calc(16px*var(--u))/1.1 var(--f);white-space:nowrap}
.b3d-chip b{font:650 calc(16px*var(--u))/1 var(--f);color:#0b57d0}
.b3d-chip.dim{opacity:.92}.b3d-chip.dim b{color:#6b6e76}
.b3d-chip.ember{border-color:rgba(196,81,31,.45)}.b3d-chip.ember b{color:#c4511f}
.b3d-chip.green{border-color:rgba(30,142,90,.45)}.b3d-chip.green b{color:#1e8e5a}
.b3d-note{background:#fff;border-radius:calc(16px*var(--u));padding:calc(12px*var(--u)) calc(15px*var(--u)) calc(13px*var(--u));
  box-shadow:0 12px 34px rgba(18,19,23,.13),0 1px 2px rgba(18,19,23,.06);border:1px solid rgba(18,19,23,.08);
  font:400 calc(16px*var(--u))/1.42 var(--f);width:max-content;max-width:calc(520px*var(--u));color:#121317}
.b3d-note .k{font:650 calc(14px*var(--u))/1.2 var(--f);letter-spacing:.08em;text-transform:uppercase;color:#0b57d0;margin-bottom:calc(6px*var(--u))}
.b3d-note .k b{font-weight:600;color:#6b6e76;letter-spacing:.03em;text-transform:none}
.b3d-note .k .b3d-tq{text-transform:none;letter-spacing:-.01em}
.b3d-note.green{border-left:calc(4px*var(--u)) solid #1e8e5a}.b3d-note.green .k{color:#1e8e5a}
.b3d-note.ember{border-left:calc(4px*var(--u)) solid #c4511f}.b3d-note.ember .k{color:#c4511f}
.b3d-note.sky{border-left:calc(4px*var(--u)) solid #3c90ff}
.b3d-note .t{font:420 calc(16px*var(--u))/1.42 var(--f);color:#45474d;max-width:calc(420px*var(--u));white-space:normal}
.b3d-note .big{font:600 calc(30px*var(--u))/1.05 var(--f);letter-spacing:-.02em;color:#0b57d0}
.b3d-note .big.ember{color:#c4511f}.b3d-note .big.green{color:#1e8e5a}
.b3d-vals{display:grid;grid-template-columns:repeat(4,auto);gap:calc(4px*var(--u)) calc(12px*var(--u));font:520 calc(16px*var(--u))/1.35 var(--mono);color:#121317;margin-top:calc(2px*var(--u))}
.b3d-vals span.n{color:#5d6b85}
.b3d-tbl{display:grid;grid-template-columns:auto auto 1fr;gap:calc(3px*var(--u)) calc(12px*var(--u));align-items:center;font:450 calc(16px*var(--u))/1.35 var(--f)}
.b3d-tbl .r{color:#6b6e76;font:500 calc(14px*var(--u))/1.35 var(--f)}
.b3d-tbl .p{font:600 calc(15px*var(--u))/1.3 var(--f);color:#0b57d0;text-align:right}
.b3d-tbl .junk{color:#8a8f99}.b3d-tbl .junk .b3d-tq{font-weight:450}
.b3d-tbl .hit{color:#0b57d0}
.b3d-cut{display:flex;flex-wrap:wrap;align-items:center;gap:calc(5px*var(--u));margin:calc(3px*var(--u)) 0 calc(7px*var(--u))}
.b3d-cut .w{font:500 calc(15px*var(--u))/1 var(--f);color:#45474d;min-width:calc(104px*var(--u))}
.b3d-cut .tk{display:inline-flex;flex-direction:column;align-items:center;padding:calc(4px*var(--u)) calc(7px*var(--u));border-radius:calc(7px*var(--u));
  background:#e6f1ff;border:1px solid rgba(60,144,255,.35);font:560 calc(15px*var(--u))/1.1 var(--mono);color:#0b57d0}
.b3d-cut .tk small{font:450 calc(13px*var(--u))/1.1 var(--mono);color:#5f636b;margin-top:calc(2px*var(--u))}
.b3d-cut .tk.dg{background:#fff1e8;border-color:rgba(196,81,31,.35);color:#c4511f}
.b3d-cut .tk.dt{background:#f0f1f4;border-color:rgba(18,19,23,.12);color:#45474d}
.b3d-samp{display:grid;grid-template-columns:auto 1fr;gap:calc(4px*var(--u)) calc(10px*var(--u));font:420 calc(15.5px*var(--u))/1.35 var(--f);max-width:calc(560px*var(--u))}
.b3d-samp .s{color:#6b6e76;font:500 calc(14px*var(--u))/1.35 var(--f);white-space:nowrap}
.b3d-samp b{color:#c4511f;font-weight:650}.b3d-samp b.gr{color:#1e8e5a}
.b3d-spark{display:block;margin-top:calc(6px*var(--u))}
/* chat + trace rail */
.b3d-rail{position:absolute;left:calc(26px*var(--u));top:calc(26px*var(--u));bottom:calc(26px*var(--u));width:calc(372px*var(--u));
  border-radius:calc(26px*var(--u));background:rgba(255,255,255,.74);border:1px solid rgba(255,255,255,.95);
  box-shadow:0 1px 2px rgba(18,19,23,.05),0 18px 48px rgba(18,19,23,.10);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);
  display:flex;flex-direction:column;overflow:hidden}
.b3d-rail header{padding:calc(17px*var(--u)) calc(20px*var(--u)) calc(13px*var(--u));border-bottom:1px solid rgba(18,19,23,.07)}
.b3d-rail header b{display:flex;align-items:center;gap:calc(9px*var(--u));font:560 calc(20px*var(--u))/1.2 var(--f);letter-spacing:-.01em}
.b3d-rail header b i{width:calc(11px*var(--u));height:calc(11px*var(--u));border-radius:50%;background:#3c90ff;box-shadow:0 0 0 4px rgba(60,144,255,.16)}
.b3d-rail header span{display:block;font:400 calc(15px*var(--u))/1.35 var(--f);color:#5f636b;margin-top:calc(3px*var(--u))}
.b3d-chat{display:flex;flex-direction:column;gap:calc(9px*var(--u));padding:calc(14px*var(--u)) calc(16px*var(--u)) calc(10px*var(--u))}
.b3d-who{font:600 calc(14px*var(--u))/1 var(--f);letter-spacing:.06em;text-transform:uppercase;color:#6b6e76;margin:0 calc(4px*var(--u)) calc(-3px*var(--u))}
.b3d-who.emma{align-self:flex-end}
.b3d-b{max-width:90%;border-radius:calc(18px*var(--u));padding:calc(10px*var(--u)) calc(14px*var(--u));font:400 calc(16.5px*var(--u))/1.42 var(--f);box-shadow:0 1px 2px rgba(18,19,23,.05)}
.b3d-b.emma{align-self:flex-end;background:#0b57d0;color:#fff;border-bottom-right-radius:calc(6px*var(--u))}
.b3d-b.bot{align-self:flex-start;background:#fff;border:1px solid rgba(18,19,23,.08);border-bottom-left-radius:calc(6px*var(--u));min-height:calc(23px*var(--u))}
.b3d-b.bot .n{color:#c4511f;font-weight:650}.b3d-b.bot .n.gr{color:#1e8e5a}
.b3d-b.bot .cur{display:inline-block;width:calc(9px*var(--u));height:calc(17px*var(--u));background:#3c90ff;border-radius:2px;vertical-align:-2px;margin-left:2px}
.b3d-b.bot .wait{color:#8a8d94}
.b3d-b.bot.facts{border-color:rgba(30,142,90,.45);box-shadow:0 0 0 3px rgba(30,142,90,.10)}
.b3d-tr{flex:1;border-top:1px solid rgba(18,19,23,.07);padding:calc(12px*var(--u)) calc(16px*var(--u)) calc(12px*var(--u));display:flex;flex-direction:column;gap:calc(2px*var(--u));overflow:hidden}
.b3d-tr h4{margin:0 0 calc(5px*var(--u)) calc(4px*var(--u));font:650 calc(14px*var(--u))/1.2 var(--f);letter-spacing:.08em;text-transform:uppercase;color:#6b6e76}
.b3d-tr .r{display:grid;grid-template-columns:calc(26px*var(--u)) 1fr;gap:calc(2px*var(--u)) calc(8px*var(--u));padding:calc(5px*var(--u)) calc(6px*var(--u));border-radius:calc(10px*var(--u));align-items:baseline}
.b3d-tr .r .n{font:650 calc(15px*var(--u))/1.25 var(--f);color:#9aa0aa;text-align:right}
.b3d-tr .r .x{font:500 calc(15.5px*var(--u))/1.25 var(--f);color:#9aa0aa}
.b3d-tr .r .c{font:450 calc(14.5px*var(--u))/1.3 var(--f)}
.b3d-tr .r .v{font:450 calc(14.5px*var(--u))/1.3 var(--f);color:#5f636b}.b3d-tr .r .v:not(:empty)::before{content:' · ';color:#9aa0aa}
.b3d-tr .r .v b{font-weight:620;color:#0b57d0}.b3d-tr .r .v b.e{color:#c4511f}.b3d-tr .r .v b.gr{color:#1e8e5a}
.b3d-tr .r.done .n{color:#3c90ff}.b3d-tr .r.done .x{color:#121317}
.b3d-tr .r.cur{background:#e6f1ff}.b3d-tr .r.cur .n{color:#0b57d0}.b3d-tr .r.cur .x{color:#0b57d0;font-weight:600}
/* hud */
.b3d-hud{position:absolute;left:calc(430px*var(--u));top:calc(28px*var(--u));right:calc(40px*var(--u));pointer-events:none}
.b3d-kick{display:flex;align-items:center;gap:calc(12px*var(--u));font:500 calc(16px*var(--u))/1.2 var(--f);color:#45474d}
.b3d-pill{display:inline-flex;align-items:center;height:calc(30px*var(--u));padding:0 calc(12px*var(--u));border-radius:999px;background:rgba(255,255,255,.7);
  border:1px solid rgba(18,19,23,.12);font:560 calc(14.5px*var(--u))/1 var(--f);color:#121317}
.b3d-hud h2{margin:calc(11px*var(--u)) 0 calc(6px*var(--u));font:470 calc(38px*var(--u))/1.08 var(--f);letter-spacing:-.025em;color:#121317;max-width:calc(1100px*var(--u))}
.b3d-hud p{margin:0;font:400 calc(20px*var(--u))/1.42 var(--f);color:#45474d;max-width:calc(1020px*var(--u))}
.b3d-hud p b{color:#121317;font-weight:560}.b3d-hud p em{font-style:normal;color:#1e8e5a;font-weight:600}
.b3d-hud p .b3d-tq{font-size:.92em;color:#0b57d0}
.b3d-foot{position:absolute;left:calc(430px*var(--u));right:calc(30px*var(--u));bottom:calc(22px*var(--u));display:flex;align-items:flex-end;gap:calc(16px*var(--u));pointer-events:none}
.b3d-prov{flex:1;font:400 calc(14.5px*var(--u))/1.45 var(--f);color:#6b6e76}
.b3d-prov b{font-weight:560;color:#45474d}.b3d-prov code{font:500 1em var(--mono)}
.b3d-leg{display:flex;flex-wrap:wrap;gap:calc(14px*var(--u));margin-bottom:calc(5px*var(--u));font:500 calc(14px*var(--u))/1 var(--f);color:#45474d}
.b3d-leg span{display:inline-flex;align-items:center;gap:calc(6px*var(--u))}
.b3d-leg i{width:calc(10px*var(--u));height:calc(10px*var(--u));border-radius:3px;background:#3c90ff}
.b3d-ctl{pointer-events:auto;display:flex;flex-direction:column;align-items:flex-end;gap:calc(10px*var(--u))}
.b3d-btns{display:flex;gap:calc(6px*var(--u));padding:calc(6px*var(--u));border-radius:999px;background:rgba(255,255,255,.80);border:1px solid rgba(18,19,23,.10);
  box-shadow:0 8px 24px rgba(18,19,23,.08);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px)}
.b3d-btns button{all:unset;cursor:pointer;display:inline-flex;align-items:center;gap:calc(7px*var(--u));height:calc(38px*var(--u));padding:0 calc(14px*var(--u));border-radius:999px;
  font:540 calc(15px*var(--u))/1 var(--f);color:#121317}
.b3d-btns button:hover{background:#e6f1ff;color:#0b57d0}
.b3d-btns button.on{background:#0b57d0;color:#fff}
.b3d-btns svg{width:calc(16px*var(--u));height:calc(16px*var(--u))}
.b3d-prog{display:flex;gap:calc(8px*var(--u))}
.b3d-prog span{display:flex;gap:calc(3px*var(--u))}
.b3d-prog i{width:calc(12px*var(--u));height:calc(5px*var(--u));border-radius:3px;background:rgba(18,19,23,.12);cursor:pointer}
.b3d-prog i.done{background:#9cc4ff}.b3d-prog i.cur{background:#0b57d0}
.b3d-temp{pointer-events:auto;display:none;align-items:center;gap:calc(12px*var(--u));padding:calc(8px*var(--u)) calc(16px*var(--u));border-radius:999px;background:rgba(255,255,255,.86);
  border:1px solid rgba(18,19,23,.10);box-shadow:0 8px 24px rgba(18,19,23,.08);font:540 calc(15px*var(--u))/1 var(--f)}
.b3d-temp input{width:calc(220px*var(--u));accent-color:#0b57d0}
.b3d-temp b{min-width:calc(44px*var(--u));font:650 calc(17px*var(--u))/1 var(--f);color:#0b57d0}
.brain3d.has-temp .b3d-temp{display:inline-flex}
.brain3d.deck .b3d-hud{top:calc(92px*var(--u))}
.brain3d.deck .b-prev,.brain3d.deck .b-next,.brain3d.deck .b3d-prog,.brain3d.deck .b3d-temp{display:none}
.brain3d.deck .b3d-rail{top:calc(92px*var(--u));bottom:calc(60px*var(--u))}
.brain3d.deck .b3d-foot{bottom:calc(60px*var(--u))}
.b3d-poster{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.brain3d canvas{cursor:grab;touch-action:none}.brain3d canvas.pt{cursor:pointer}.brain3d canvas:active{cursor:grabbing}
.b3d-hint{font:500 calc(14px*var(--u))/1.2 var(--f);color:#45474d;background:rgba(255,255,255,.86);border:1px solid rgba(18,19,23,.10);border-radius:999px;
  padding:calc(7px*var(--u)) calc(13px*var(--u));box-shadow:0 6px 18px rgba(18,19,23,.07);transition:opacity .8s;white-space:nowrap}
.b3d-hint.off{opacity:0}
.b3d-btns button.b-reset{display:none}.b3d-btns button.b-reset.on{display:inline-flex}
.b3d-info{position:absolute;left:calc(430px*var(--u));bottom:calc(108px*var(--u));z-index:6;display:none;pointer-events:auto;margin:0;
  background:#fff;border-radius:calc(16px*var(--u));padding:calc(13px*var(--u)) calc(16px*var(--u)) calc(14px*var(--u));width:calc(430px*var(--u));
  box-shadow:0 16px 40px rgba(18,19,23,.16),0 1px 2px rgba(18,19,23,.06);border:1px solid rgba(18,19,23,.08);border-left:calc(4px*var(--u)) solid #0b57d0;
  font:420 calc(15.5px*var(--u))/1.42 var(--f);color:#121317;flex-direction:column;align-items:stretch;gap:0}
.b3d-info.on{display:flex}
.b3d-info .hd{display:flex;align-items:baseline;gap:calc(10px*var(--u));margin-bottom:calc(6px*var(--u))}
.b3d-info .hd .b3d-tq{font-size:calc(22px*var(--u));color:#0b57d0}
.b3d-info .hd small{font:500 calc(14px*var(--u))/1.3 var(--f);color:#6b6e76}
.b3d-info .hd button{all:unset;cursor:pointer;margin-left:auto;font:500 calc(20px*var(--u))/1 var(--f);color:#6b6e76;padding:0 calc(4px*var(--u))}
.b3d-info .sec{font:650 calc(13px*var(--u))/1.2 var(--f);letter-spacing:.08em;text-transform:uppercase;color:#6b6e76;margin:calc(8px*var(--u)) 0 calc(4px*var(--u))}
.b3d-info .lk{display:grid;grid-template-columns:1fr auto;gap:calc(2px*var(--u)) calc(14px*var(--u));font:450 calc(15px*var(--u))/1.35 var(--f)}
.b3d-info .lk .p{font-weight:620;color:#0b57d0;text-align:right}
.b3d-tip{position:absolute;z-index:7;display:none;pointer-events:none;background:#fff;border-radius:calc(12px*var(--u));padding:calc(9px*var(--u)) calc(12px*var(--u));
  box-shadow:0 12px 30px rgba(18,19,23,.16);border:1px solid rgba(18,19,23,.08);font:420 calc(14.5px*var(--u))/1.4 var(--f);color:#121317;width:max-content;max-width:calc(320px*var(--u))}
.b3d-tip.on{display:block}
.b3d-tip .k{font:650 calc(13px*var(--u))/1.2 var(--f);letter-spacing:.06em;text-transform:uppercase;color:#0b57d0;margin-bottom:calc(4px*var(--u))}
.b3d-tip .lk{display:grid;grid-template-columns:1fr auto;gap:calc(1px*var(--u)) calc(12px*var(--u))}.b3d-tip .lk .p{font-weight:620;color:#0b57d0;text-align:right}
.b3d-tip .lk .j{color:#8a8f99}
.brain3d.deck .b3d-info{bottom:calc(150px*var(--u))}
`;
function injectCSS() {
  if (document.getElementById('brain3d-css')) return;
  const s = document.createElement('style'); s.id = 'brain3d-css'; s.textContent = CSS; document.head.appendChild(s);
}
const ICON = {
  prev: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 3 5 8l5 5"/></svg>',
  next: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m6 3 5 5-5 5"/></svg>',
  play: '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M4.5 2.8v10.4L13 8z"/></svg>',
  pause: '<svg viewBox="0 0 16 16" fill="currentColor"><rect x="3.5" y="2.8" width="3" height="10.4" rx="1"/><rect x="9.5" y="2.8" width="3" height="10.4" rx="1"/></svg>',
  view: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="5.2"/><path d="M8 1.5v3M8 11.5v3M1.5 8h3M11.5 8h3"/></svg>',
  replay: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2.8 8a5.2 5.2 0 1 0 1.6-3.8"/><path d="M2.6 2.6v3h3"/></svg>',
};

/* ------------------------------------------------------------------ the sections (titles match STORY_V4.md) */
export const SECTION_TITLES = [
  'The game: predict the next token',
  'What you send, cut into tokens',
  'Each token becomes a vector',
  'Attention: tokens look back',
  'A block, then 24 of them',
  'From a vector to a choice',
  'The loop: one token at a time',
  'Where the weights came from',
  'Why it made the number up, and what fixes it',
];
export const SECTION_STATES = [3, 4, 4, 8, 4, 5, 5, 4, 4];
const SHORT = ['The game', 'Tokens', 'Vectors', 'Attention', 'The blocks', 'The choice', 'The loop', 'Training', 'Why, and the fix'];

/* ------------------------------------------------------------------ the numbers, read from the trace */
function readTrace(T) {
  const meta = T.meta, toks = T.tokens, N = toks.length, G = T.generation, F = T.facts;
  const ans = G.greedy.filter((s) => s.text !== '<|endoftext|>');
  const ansF = F.greedy.filter((s) => s.text !== '<|endoftext|>');
  const lensLast = T.logit_lens.last;
  const finalTok = T.final.last['1.0'][0];
  const low = (s) => s.trim().toLowerCase();
  const firstLoose = (lensLast.find((r) => low(r.top[0].text) === low(finalTok.text)) || {}).layer;
  let exactFrom = 24; for (let l = 23; l >= 0; l--) { if (lensLast[l].top[0].id === finalTok.id) exactFrom = l + 1; else break; }
  const dig = G.digits, digF = F.digits;
  const numStr = dig.map((d) => d.token).join(''), numStrF = digF.map((d) => d.token).join('');
  const inputDigits = toks.filter((t) => t.digit).map((t) => t.i);
  const heads = Object.fromEntries(T.attention.heads.map((h) => [h.looks_at, h]));
  const fa = F.attention_to_fact;
  const sampF = F.samples_t07;
  return { meta, toks, N, ans, ansF, lensLast, finalTok, firstLoose, exactFrom, dig, digF, numStr, numStrF, inputDigits, heads, fa, sampF,
    sysN: T.prompt.counts.system, userN: T.prompt.counts.user, tplN: T.prompt.counts.template, kp: T.key_positions };
}

/* ------------------------------------------------------------------ the component */
export function mountBrain3D(host, opts = {}) {
  injectCSS();
  const T = opts.trace || window.BRAIN_TRACE;
  const mode = opts.mode || 'standalone';
  const still = !!opts.still;
  const root = document.createElement('div');
  root.className = 'brain3d' + (mode === 'deck' ? ' deck' : '');
  if (getComputedStyle(host).position === 'static') host.style.position = 'relative';
  host.appendChild(root);
  if (!T || !hasWebGL() || opts.forcePoster) {
    const s = opts.section || 1;
    root.innerHTML = `<img class="b3d-poster" src="${new URL(`poster-s${s}.png`, HERE)}" alt="The Brain, section ${s}: ${esc(SECTION_TITLES[s - 1])}">`;
    const noop = () => {};
    return { go: noop, next: noop, prev: noop, replay: noop, autoplay: noop, seek: noop, setSection: noop, attach(el) { el.appendChild(root); }, count: 1, sections: [], destroy() { root.remove(); }, poster: true };
  }
  const D = readTrace(T);
  const M = D.meta;

  /* ---------- DOM ---------- */
  root.innerHTML = `
    <div class="b3d-vig"></div>
    <aside class="b3d-rail"><header><b><i></i>Ask Northbridge</b><span>the brain alone: ${esc(M.model.replace('Qwen/', ''))}, no tools</span></header>
      <div class="b3d-chat"><div class="b3d-who emma">${esc(T.prompt.person ? T.prompt.person.name : 'Emma Clarke')}</div><div class="b3d-b emma">${esc(T.prompt.question)}</div>
        <div class="b3d-who">Ask Northbridge</div><div class="b3d-b bot"></div></div>
      <div class="b3d-tr"><h4>The trace so far</h4>${SHORT.map((s, i) => `<div class="r" data-s="${i + 1}"><span class="n">${i + 1}</span><span class="c"><span class="x">${esc(s)}</span><span class="v"></span></span></div>`).join('')}</div></aside>
    <div class="b3d-hud"><div class="b3d-kick"><span class="b3d-pill"></span><span class="b3d-sec"></span></div><h2></h2><p></p></div>
    <div class="b3d-foot"><div class="b3d-prov"><div class="b3d-leg"><span><i></i>the model and its numbers</span><span><i style="background:#c4511f"></i>invented by the model</span><span><i style="background:#1e8e5a"></i>a fact from Ledgerline</span><span><i style="background:#c9ced8"></i>template markers</span></div>
      <b>Recorded run.</b> ${esc(M.model)} (rev ${esc(String(M.revision).slice(0, 7))}), ${esc(M.dtype)}, on CPU on Modal · ${esc(M.recorded_at)} · transformers ${esc(M.transformers)} · numbers from <code>brain3d/trace.json</code></div>
      <div class="b3d-ctl ctl"><div class="b3d-hint">Drag to look around · scroll to zoom · click a token</div><label class="b3d-temp">Temperature <input type="range" min="0" max="2" step="0.05" value="1"><b>1.00</b></label><div class="b3d-btns">
        <button class="b-prev" aria-label="Previous step">${ICON.prev}</button>
        <button class="b-auto" aria-label="Autoplay">${ICON.play}<span>Autoplay</span></button>
        <button class="b-replay" aria-label="Replay this step">${ICON.replay}<span>Replay</span></button>
        <button class="b-reset" aria-label="Reset the view">${ICON.view}<span>Reset view</span></button>
        <button class="b-next" aria-label="Next step">${ICON.next}</button></div>
        <div class="b3d-prog">${SECTION_STATES.map((n, s) => `<span>${Array.from({ length: n }, (_, k) => `<i data-s="${s + 1}" data-k="${k}"></i>`).join('')}</span>`).join('')}</div></div></div>`;
  root.insertAdjacentHTML('beforeend', '<div class="b3d-info ctl" role="dialog"></div><div class="b3d-tip"></div>');
  const $ = (q) => root.querySelector(q);
  const hud = { pill: $('.b3d-pill'), sec: $('.b3d-sec'), h2: $('.b3d-hud h2'), p: $('.b3d-hud p') };
  const railEl = $('.b3d-rail'), hudEl = $('.b3d-hud'), footEl = $('.b3d-foot'), botEl = $('.b3d-b.bot');
  const trRows = [...root.querySelectorAll('.b3d-tr .r')];
  const progDots = [...root.querySelectorAll('.b3d-prog i')];
  const tempIn = $('.b3d-temp input'), tempOut = $('.b3d-temp b');

  /* ---------- renderer, scene, camera ---------- */
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance', preserveDrawingBuffer: still });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.setClearColor(0x000000, 0);
  root.insertBefore(renderer.domElement, root.firstChild);
  const labels = new CSS2DRenderer();
  labels.domElement.className = 'b3d-labels';
  root.insertBefore(labels.domElement, railEl);
  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;
  const camera = new THREE.PerspectiveCamera(30, 16 / 9, 0.5, 500);
  scene.add(new THREE.HemisphereLight(0xf4f8ff, 0xd5dde8, 0.45));
  const key = new THREE.DirectionalLight(0xffffff, 1.8);
  key.position.set(-12, 30, 18); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -30, right: 30, top: 22, bottom: -22, near: 1, far: 90 });
  key.shadow.bias = -0.0005; key.shadow.normalBias = 0.03; key.shadow.radius = 4;
  key.target.position.set(0, 0, 0); scene.add(key, key.target);
  const rim = new THREE.DirectionalLight(0xcfe3ff, 0.55); rim.position.set(20, 12, -22); scene.add(rim);

  const RB = (w, h, d, r = 0.12, s = 4) => new RoundedBoxGeometry(w, h, d, s, Math.min(r, w / 2 - 0.001, h / 2 - 0.001, d / 2 - 0.001));
  const phys = (o) => new THREE.MeshPhysicalMaterial(Object.assign({ color: 0xfbfcfe, roughness: 0.4, metalness: 0, clearcoat: 0.6, clearcoatRoughness: 0.28, envMapIntensity: 0.7, transparent: true }, o));
  const mesh = (geo, mat, pos, parent = scene, shadow = true) => {
    const m = new THREE.Mesh(geo, mat); if (pos) m.position.copy(pos); m.castShadow = shadow; m.receiveShadow = true; parent.add(m); return m;
  };
  /* every material of a "part" fades together: op(part, a) scales each material's own base opacity */
  const parts = {};
  function partMat(name, mat) { (parts[name] = parts[name] || []).push([mat, mat.opacity]); mat.transparent = true; return mat; }
  function op(name, a) { const l = parts[name]; if (!l) return; for (const [m, b] of l) { m.opacity = b * a; m.visible = a > 0.004; m.depthWrite = a > 0.98 && b > 0.98; } }

  /* floor: shadow catcher + a soft dot grid */
  const floorGeo = new THREE.PlaneGeometry(200, 140); floorGeo.rotateX(-Math.PI / 2);
  const shadowFloor = new THREE.Mesh(floorGeo, new THREE.ShadowMaterial({ color: 0x1b3a66, opacity: 0.18 }));
  shadowFloor.receiveShadow = true; scene.add(shadowFloor);
  const grid = new THREE.Mesh(floorGeo.clone(), new THREE.ShaderMaterial({
    transparent: true, depthWrite: false,
    uniforms: { uC: { value: new THREE.Color(0x8fb6e8) }, uT: { value: new THREE.Color(0xdde8f5) } },
    vertexShader: 'varying vec3 vP; void main(){ vP = (modelMatrix*vec4(position,1.)).xyz; gl_Position = projectionMatrix*viewMatrix*vec4(vP,1.); }',
    fragmentShader: `uniform vec3 uC; uniform vec3 uT; varying vec3 vP;
      void main(){ vec2 g = abs(fract(vP.xz/1.0 - .5) - .5); float d = length(g); float dt = 1. - smoothstep(.035,.06,d);
        vec2 q = vP.xz / vec2(30., 15.); float r = length(q);
        float fade = 1. - smoothstep(0.55, 1.05, r); float tint = (1. - smoothstep(0.35, 1.0, r)) * .5;
        gl_FragColor = vec4(mix(uT, uC, dt), max(tint, dt*fade*.32));
        #include <colorspace_fragment>
      }`,
  }));
  grid.position.y = 0.006; scene.add(grid);
  const blobTex = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
    const r = g.createRadialGradient(64, 64, 4, 64, 64, 64); r.addColorStop(0, 'rgba(20,45,90,0.34)'); r.addColorStop(1, 'rgba(20,45,90,0)');
    g.fillStyle = r; g.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c);
  })();
  const blob = (x, z, w, d, part) => {
    const mat = new THREE.MeshBasicMaterial({ map: blobTex, transparent: true, depthWrite: false });
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), mat); m.rotation.x = -Math.PI / 2; m.position.set(x, 0.008, z); scene.add(m);
    if (part) partMat(part, mat); return m;
  };

  /* ---------- labels ---------- */
  const labelList = [];
  function label(html, pos, { center = [0.5, 1], parent = scene, kind = 'note' } = {}) {
    const outer = document.createElement('div');
    const inner = document.createElement('div'); inner.className = 'b3d-l'; inner.innerHTML = html;
    inner.style.transformOrigin = `${center[0] * 100}% ${center[1] * 100}%`;
    outer.appendChild(inner);
    const o = new CSS2DObject(outer); o.center.set(center[0], center[1]); if (pos) o.position.copy(pos); parent.add(o);
    const L = { o, inner, html, op: 0, kind,
      set(h) { if (h !== L.html) { L.html = h; inner.innerHTML = h; } return L; },
      show(a = 1) { L.op = Math.max(L.op, a); return L; },
      at(p, c) { o.position.copy(p); if (c) { o.center.set(c[0], c[1]); inner.style.transformOrigin = `${c[0] * 100}% ${c[1] * 100}%`; } return L; } };
    labelList.push(L); return L;
  }
  const tagHTML = (text, sub, cls = '') => `<span class="b3d-tag ${cls}"><i class="d"></i>${text}${sub ? ` <small>${sub}</small>` : ''}</span>`;
  const tag = (text, sub, pos, cls = '', center = [0.5, 1]) => label(tagHTML(text, sub, cls), pos, { center, kind: 'tag' });
  const chip = (pos, center = [0.5, 1]) => label('', pos, { center, kind: 'chip' });
  const note = (pos, center = [0.5, 1]) => label('', pos, { center, kind: 'note' });

  /* =========================================================== the world */
  /* ---------- token tiles: the prompt, the answer, the with-facts prompt and answer ---------- */
  const PX = 220;               // canvas px per world unit
  const TD = 0.66, TH = 0.2, GAP = 0.1, PITCH = 0.92, MAXW = 15.2;
  const isSpecial = (s) => /^<\|.*\|>$/.test(s);
  const tileW = (s) => (isSpecial(s) ? 1.62 : Math.max(0.6, Math.min(2.2, 0.36 + 0.122 * vis(s).replace(/^ /, '').length + (s.startsWith(' ') ? 0.12 : 0))));
  function layout(list) {
    const out = []; let x = 0, row = 0;
    list.forEach((t, i) => {
      const w = tileW(t.text);
      if (i > 0 && (t.text === '<|im_start|>' || x + w > MAXW)) { row++; x = 0; }
      out.push({ x: x + w / 2 - MAXW / 2, row, w }); x += w + GAP;
    });
    return { pos: out, rows: row + 1 };
  }
  const baseList = [...D.toks.map((t) => ({ ...t, kind: t.role })), ...D.ans.map((s, j) => ({ text: s.text, id: s.id, p: s.p, kind: 'answer', j }))];
  const factList = [...T.facts.tokens.map((t) => ({ ...t, kind: t.fact ? 'fact' : t.role })), ...D.ansF.map((s, j) => ({ text: s.text, id: s.id, p: s.p, kind: 'answerF', j }))];
  const LB = layout(baseList), LF = layout(factList);
  const zOf = (row, rows) => (row - (rows - 1) / 2) * PITCH + 0.2;
  const digitSet = new Set(T.generation.digit_steps), digitSetF = new Set(T.facts.digit_steps);
  // match the with-facts prompt to the base prompt: same prefix, same suffix
  const nP = D.N, nPF = T.facts.tokens.length;
  let pre = 0; while (pre < nP && T.facts.tokens[pre].id === D.toks[pre].id) pre++;
  let suf = 0; while (suf < nP - pre && T.facts.tokens[nPF - 1 - suf].id === D.toks[nP - 1 - suf].id) suf++;
  const baseToF = (i) => (i < pre ? i : i >= nP - suf ? i + (nPF - nP) : -1);

  function tileTexture(t, w) {
    const cw = Math.round(w * PX), ch = Math.round(TD * PX);
    const c = document.createElement('canvas'); c.width = cw; c.height = ch; const g = c.getContext('2d');
    const kind = t.kind;
    const special = isSpecial(t.text);
    let txt = vis(t.text); const lead = txt.startsWith(' ') && txt.length > 1; if (lead) txt = txt.slice(1);
    if (txt === ' ') txt = '␣';
    const inkC = { system: '#121317', user: '#0b57d0', template: '#5f636b', answer: '#ffffff', answerF: '#ffffff', fact: '#156e45' }[kind];
    const digitAns = (kind === 'answer' && digitSet.has(t.j)) || (kind === 'answerF' && digitSetF.has(t.j));
    let fs = special ? 30 : 50;
    g.font = `${special ? 560 : 600} ${fs}px ${special ? '"Google Sans Code", ui-monospace, monospace' : '"Google Sans Flex", "Google Sans", Arial, sans-serif'}`;
    const avail = cw - (lead ? 40 : 22);
    while (g.measureText(txt).width > avail && fs > 22) { fs -= 2; g.font = g.font.replace(/\d+px/, fs + 'px'); }
    const tw = g.measureText(txt).width;
    const x0 = (cw - tw + (lead ? 18 : 0)) / 2, y0 = ch * 0.47;
    g.fillStyle = inkC; g.textBaseline = 'middle'; g.fillText(txt, x0, y0);
    if (lead) { // a visible space: a small bracket before the text
      g.strokeStyle = kind === 'answer' || kind === 'answerF' ? 'rgba(255,255,255,.7)' : 'rgba(95,99,107,.55)'; g.lineWidth = 3.2;
      const bx = x0 - 22, by = y0 + fs * 0.3; g.beginPath(); g.moveTo(bx, by - 9); g.lineTo(bx, by); g.lineTo(bx + 13, by); g.lineTo(bx + 13, by - 9); g.stroke();
    }
    const sub = kind === 'answer' || kind === 'answerF' ? pct(t.p) : String(t.id);
    g.font = `500 ${special ? 24 : 26}px "Google Sans Code", ui-monospace, monospace`;
    g.fillStyle = kind === 'answer' || kind === 'answerF' ? 'rgba(255,255,255,.86)' : kind === 'fact' ? 'rgba(21,110,69,.75)' : 'rgba(95,99,107,.85)';
    const sw = g.measureText(sub).width; g.fillText(sub, (cw - sw) / 2, ch * 0.83);
    const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
    return { tex, digitAns };
  }
  const BODY = { system: 0xffffff, user: 0xeaf3ff, template: 0xe4e7ee, answer: 0x1f6fe5, answerF: 0x1f6fe5, fact: 0xdff3e8 };
  const tileGeoCache = new Map();
  const tileGeo = (w) => { const k = w.toFixed(3); if (!tileGeoCache.has(k)) tileGeoCache.set(k, RB(w, TH, TD, 0.07, 3)); return tileGeoCache.get(k); };
  const tiles = [];
  function makeTile(t, w, home) {
    const g = new THREE.Group(); scene.add(g);
    const { tex, digitAns } = tileTexture(t, w);
    let body = BODY[t.kind];
    if (digitAns) body = t.kind === 'answer' ? C.ember : C.green;
    const mat = phys({ color: body, roughness: 0.38, clearcoat: 0.7, emissive: body, emissiveIntensity: 0.0 });
    const m = mesh(tileGeo(w), mat, V(0, TH / 2, 0), g);
    const face = new THREE.Mesh(new THREE.PlaneGeometry(w * 0.98, TD * 0.98), new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false }));
    face.rotation.x = -Math.PI / 2; face.position.y = TH + 0.004; g.add(face);
    const tile = { t, w, g, mat, face, digitAns, home, x: home.x, z: home.z, op: 0, glow: 0, lift: 0, kind: t.kind, col: 1 };
    m.userData.tile = tile; tile.body = m; tiles.push(tile); return tile;
  }
  const tB = baseList.map((t, i) => makeTile(t, LB.pos[i].w, { x: LB.pos[i].x, z: zOf(LB.pos[i].row, LB.rows) }));
  tB.forEach((x) => (x.base = true));
  const tPrompt = tB.slice(0, nP), tAns = tB.slice(nP);
  // the with-facts run: tiles that differ from the base prompt, and its own answer
  const tF = factList.map((t, i) => {
    const home = { x: LF.pos[i].x, z: zOf(LF.pos[i].row, LF.rows) };
    if (i < nPF) { const bi = i < pre ? i : i >= nPF - suf ? i - (nPF - nP) : -1; if (bi >= 0) { tB[bi].fhome = home; return tB[bi]; } }
    return makeTile(t, LF.pos[i].w, home);
  });
  const tFNew = tF.filter((x, i) => i < nPF && tB.indexOf(x) < 0), tFAns = tF.slice(nPF);
  const tFactTiles = tF.filter((x) => x.kind === 'fact');
  const allZ = [...tB, ...tF].map((x) => [x.home.z, x.fhome ? x.fhome.z : x.home.z]).flat();
  const PAGE = { x0: -MAXW / 2 - 0.5, x1: MAXW / 2 + 0.5, z0: Math.min(...allZ) - 0.75, z1: Math.max(...allZ) + 0.75 };
  const PW = PAGE.x1 - PAGE.x0, PD = PAGE.z1 - PAGE.z0, PCX = (PAGE.x0 + PAGE.x1) / 2, PCZ = (PAGE.z0 + PAGE.z1) / 2;
  // the page: a low satin plinth the tiles sit on
  const plinthMat = partMat('plinth', phys({ color: 0xf6f8fc, roughness: 0.5, clearcoat: 0.4 }));
  const plinth = mesh(RB(PW + 0.6, 0.12, PD + 0.4, 0.1), plinthMat, V(PCX, -0.02, PCZ));
  plinth.receiveShadow = true; plinth.castShadow = false;
  blob(PCX, PCZ, PW + 6, PD + 5, 'plinth');
  const tilePos = (tile, mix = 0) => { const h = tile.home, f = tile.fhome || h; return V(lerp(h.x, f.x, mix), 0, lerp(h.z, f.z, mix)); };

  /* ---------- vector columns (12 of 896 numbers per token) ---------- */
  const NC = 12, CELL = 0.13, COL0 = TH + 0.16, COLTOP = COL0 + NC * CELL + 0.06;
  const vals = Object.fromEntries(T.embeddings.values.map((v) => [v.i, v.v16]));
  const absAll = T.embeddings.values.flatMap((v) => v.v16.slice(0, NC).map(Math.abs)).sort((a, b) => a - b);
  const vScale = absAll[Math.floor(absAll.length * 0.8)] || 0.05;
  const cellGeo = RB(0.24, CELL * 0.78, 0.24, 0.04, 2);
  const colMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.35, metalness: 0, transparent: true, opacity: 1, emissive: 0x000000 });
  const colIM = new THREE.InstancedMesh(cellGeo, colMat, tiles.length * NC); colIM.frustumCulled = false; colIM.castShadow = true; scene.add(colIM);
  const cPos = new THREE.Color(0x3c90ff), cPosL = new THREE.Color(0xeaf3ff), cNeg = new THREE.Color(0x4b5873), cNegL = new THREE.Color(0xf1f3f7), _c = new THREE.Color();
  // a token's 12 cells: its real input-embedding values for prompt tokens, the row of its id for answer tokens if known
  const idVals = Object.assign({}, T.embeddings.id_values || {}); for (const t of D.toks) idVals[t.id] = vals[t.i];
  tiles.forEach((tile, ti) => {
    const v = (tile.t.i !== undefined && tile.kind !== 'answer' && tile.kind !== 'answerF' && tile.kind !== 'fact' ? vals[tile.t.i] : idVals[tile.t.id]) || null;
    tile.v = v;
    for (let k = 0; k < NC; k++) {
      const x = v ? v[k] / vScale : Math.sin(ti * 7.1 + k * 3.3) * 0.6;
      const a = clamp01(Math.abs(x));
      if (x >= 0) _c.copy(cPosL).lerp(cPos, a); else _c.copy(cNegL).lerp(cNeg, a);
      colIM.setColorAt(ti * NC + k, _c);
    }
  });
  colIM.instanceColor.needsUpdate = true;

  /* ---------- the stack: 24 blocks ---------- */
  const NL = M.layers;
  const S0 = COLTOP + 0.55, SP = 0.34;
  const slabY = (l) => S0 + l * SP; // l = 0..23
  const STOP = slabY(NL - 1) + 0.25;
  const slabGeo = new THREE.PlaneGeometry(PW + 0.2, PD); slabGeo.rotateX(-Math.PI / 2);
  const slabShader = (layer) => new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, side: THREE.DoubleSide,
    uniforms: { uOp: { value: 0 }, uFill: { value: 0 }, uMode: { value: 0 }, uLayer: { value: layer }, uHi: { value: 0 }, uW: { value: (PW + 0.2) / PD } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: `uniform float uOp, uFill, uMode, uLayer, uHi, uW; varying vec2 vUv;
      float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      void main(){
        vec2 cell = floor(vUv * vec2(150., 150. / uW));
        float r = h(cell + uLayer * 13.1);
        float s = h(floor(cell / vec2(6., 2.)) + uLayer * 3.7);
        vec3 glass = vec3(0.90, 0.95, 1.0);
        vec3 rnd = mix(vec3(0.90, 0.91, 0.94), vec3(0.62, 0.66, 0.73), r);
        float tw = pow(r, 2.2) * (0.35 + 0.65 * s);
        vec3 trn = mix(vec3(0.90, 0.95, 1.0), vec3(0.16, 0.50, 0.98), tw);
        float sw = smoothstep(uFill - 0.02, uFill, vUv.x);
        vec3 w = mix(trn, rnd, sw);
        float on = step(0.5, uMode);
        vec3 col = mix(glass, uMode > 1.5 ? w : rnd, on);
        float a = uOp * mix(0.06, 0.62, on);
        vec2 e = min(vUv, 1. - vUv) * vec2(uW, 1.); float edge = 1. - smoothstep(0.0, 0.012, min(e.x, e.y));
        col = mix(col, vec3(0.24, 0.56, 1.0), edge * 0.7 + uHi * 0.5);
        a = max(a, uOp * edge * 0.5) + uOp * uHi * 0.3;
        gl_FragColor = vec4(col, a);
        #include <colorspace_fragment>
      }`,
  });
  const slabs = Array.from({ length: NL }, (_, l) => {
    const m = new THREE.Mesh(slabGeo, slabShader(l)); m.position.set(PCX, slabY(l), PCZ); m.renderOrder = 2; m.userData.layer = l; scene.add(m); return m;
  });
  // the residual streams: one vertical line per token, from its column up through the blocks
  const strGeo = new THREE.BufferGeometry(); strGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(tiles.length * 6), 3));
  const strMat = new THREE.LineBasicMaterial({ color: 0x3c90ff, transparent: true, opacity: 0.14, depthWrite: false });
  const streams = new THREE.LineSegments(strGeo, strMat); streams.frustumCulled = false; scene.add(streams);
  const hotMat = new THREE.MeshBasicMaterial({ color: 0x3c90ff, transparent: true, opacity: 0, depthWrite: false });
  const hot = mesh(new THREE.CylinderGeometry(0.06, 0.06, 1, 16, 1, true), hotMat, V(0, 0, 0), scene, false);
  // the pulse rising through the stack (one per token)
  const pulseMat = new THREE.MeshBasicMaterial({ color: 0x9cc4ff, transparent: true, opacity: 0.9, depthWrite: false });
  const pulses = new THREE.InstancedMesh(new THREE.SphereGeometry(0.09, 12, 8), pulseMat, tiles.length); pulses.frustumCulled = false; scene.add(pulses);
  // the logit-lens readouts: a dot where the hot stream crosses each block, and a leader out to its label
  const lensDots = new THREE.InstancedMesh(new THREE.SphereGeometry(0.11, 14, 10), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.95, depthWrite: false }), NL);
  lensDots.frustumCulled = false; scene.add(lensDots);
  const leadGeo = new THREE.BufferGeometry(); leadGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(NL * 6), 3));
  const leaders = new THREE.LineSegments(leadGeo, new THREE.LineBasicMaterial({ color: 0x3c90ff, transparent: true, opacity: 0.55, depthWrite: false })); leaders.frustumCulled = false; scene.add(leaders);
  // block 1, exploded: attention + MLP
  const exAtt = mesh(RB(PW * 0.98, 0.07, PD * 0.96, 0.05), partMat('ex', phys({ color: 0xcfe2ff, opacity: 0.75, roughness: 0.2, clearcoat: 1, emissive: 0x3c90ff, emissiveIntensity: 0.25 })), V(PCX, S0, PCZ), scene, false);
  const exMlp = mesh(RB(PW * 0.98, 0.07, PD * 0.96, 0.05), partMat('ex', phys({ color: 0xe6e2ff, opacity: 0.75, roughness: 0.2, clearcoat: 1, emissive: 0x8a7dff, emissiveIntensity: 0.22 })), V(PCX, S0, PCZ), scene, false);

  const tExA = tag('Attention', 'look back', V(PAGE.x1 + 0.2, S0 - 0.35, PAGE.z1 - 0.3), '', [0, 0.5]);
  const tExM = tag('MLP', 'each token alone', V(PAGE.x1 + 0.2, S0 + 0.65, PAGE.z1 - 0.3), '', [0, 0.5]);
  /* ---------- attention arcs ---------- */
  const arcSets = {};
  function arcSet(name, q, row, { n = 18, color = C.sky, skip0 = false, from = 'base' } = {}) {
    const cand = row.map((w, j) => [w, j]).filter(([w, j]) => j !== q && !(skip0 && j === 0)).sort((a, b) => b[0] - a[0]).slice(0, n);
    const wmax = Math.max(1e-6, ...cand.filter(([, j]) => j !== 0).map(([w]) => w));
    const list = from === 'facts' ? tF : tB;
    const arcs = cand.map(([w, j]) => {
      const a = list[q], b = list[j];
      const rel = j === 0 ? Math.min(1, w / wmax) : w / wmax;
      const mat = new THREE.MeshBasicMaterial({ color: j === 0 ? 0x8a93a6 : color, transparent: true, opacity: 0, depthWrite: false });
      const m = new THREE.Mesh(new THREE.BufferGeometry(), mat); m.renderOrder = 3; scene.add(m);
      return { w, j, rel, m, mat, a, b, r: 0.014 + 0.1 * Math.pow(rel, 0.8), key: '' };
    });
    arcSets[name] = { q, arcs, from };
    return arcSets[name];
  }
  function buildArc(arc, mix) {
    const k = mix.toFixed(2); if (arc.key === k) return; arc.key = k;
    const pa = tilePos(arc.a, mix), pb = tilePos(arc.b, mix);
    pa.y = TH + 0.06; pb.y = TH + 0.06;
    const d = pa.distanceTo(pb);
    const mid = pa.clone().add(pb).multiplyScalar(0.5); mid.y += 0.7 + 0.42 * Math.pow(d, 0.85);
    const curve = new THREE.QuadraticBezierCurve3(pa, mid, pb);
    arc.m.geometry.dispose(); arc.m.geometry = new THREE.TubeGeometry(curve, 56, arc.r, 8, false);
    arc.count = arc.m.geometry.index.count;
  }
  const qLast = D.kp.last;
  arcSet('avg', qLast, T.attention.last.avg[0].map((_, j) => T.attention.last.avg.reduce((s, r) => s + r[j], 0) / NL));
  const H = D.heads;
  arcSet('man', qLast, H.Manchester.row_last);
  arcSet('bat', qLast, H.battery.row_last);
  arcSet('start', qLast, H.start.row_last, { n: 6 });
  const qDig = T.attention.digit.query_pos;
  arcSet('digit', qDig, T.attention.digit.avg[0].map((_, j) => T.attention.digit.avg.reduce((s, r) => s + r[j], 0) / NL), { n: 22 });
  arcSet('fact', D.fa.query_pos, D.fa.best_head.row, { n: 8, color: C.green, from: 'facts' });

  /* ---------- query, key, value of block 24, head 2 (section 4) ---------- */
  const QK = T.attention.qkv || null;
  const qkTop = QK ? QK.weights.map((w, j) => [w, j]).sort((a, b) => b[0] - a[0]).map((x) => x[1]) : [];
  const sMin = QK ? Math.min(...QK.scores) : 0, sMax = QK ? Math.max(...QK.scores) : 1;
  const scoreH = (j) => 0.12 + 2.2 * (QK.scores[j] - sMin) / (sMax - sMin);
  const weightH = (j) => 0.04 + 3.4 * QK.weights[j];
  const KTOP = COL0 + NC * CELL, QB = KTOP + 0.55, QN = 16, QC = 0.14, QTOP = QB + QN * QC;
  const scaleOf = (arrs) => { const a = arrs.flat().map(Math.abs).sort((x, y) => x - y); return a[Math.floor(a.length * 0.85)] || 1; };
  const qS = QK ? scaleOf([QK.q.slice(0, QN)]) : 1, kS = QK ? scaleOf(QK.k.map((r) => r.slice(0, NC))) : 1, vS = QK ? scaleOf(QK.v.map((r) => r.slice(0, NC))) : 1;
  const hueQ = new THREE.Color(0x3c90ff), hueK = new THREE.Color(0x7c5cf0), hueV = new THREE.Color(0xd08a12), lite = new THREE.Color(0xf4f6fb), neg = new THREE.Color(0x4b5873);
  const cellCol = (x, sc, hue) => { const a = clamp01(Math.abs(x) / sc); return x >= 0 ? _c.copy(lite).lerp(hue, a) : _c.copy(lite).lerp(neg, a); };
  const mkIM = (geo, n, hex = 0xffffff) => { const m = new THREE.InstancedMesh(geo, new THREE.MeshStandardMaterial({ color: hex, roughness: 0.35, transparent: true, opacity: 1 }), n); m.frustumCulled = false; m.castShadow = true; m.visible = false; scene.add(m); return m; };
  const qIM = mkIM(RB(0.36, QC * 0.8, 0.36, 0.05, 2), QN), kIM = mkIM(cellGeo, nP * NC), vIM = mkIM(cellGeo, 5 * NC);
  const barGeo = RB(0.34, 1, 0.34, 0.08, 2); barGeo.translate(0, 0.5, 0);
  const sIM = mkIM(barGeo, nP);
  if (QK) {
    for (let c = 0; c < QN; c++) qIM.setColorAt(c, cellCol(QK.q[c], qS, hueQ));
    for (let i = 0; i <= QK.query_pos; i++) for (let c = 0; c < NC; c++) kIM.setColorAt(i * NC + c, cellCol(QK.k[i][c], kS, hueK));
    qkTop.slice(0, 4).forEach((j, r) => { for (let c = 0; c < NC; c++) vIM.setColorAt(r * NC + c, cellCol(QK.v[j][c], vS, hueV)); });
    for (let c = 0; c < NC; c++) vIM.setColorAt(4 * NC + c, cellCol(QK.out[c], vS * 0.6, hueV));
    for (let i = 0; i < nP; i++) sIM.setColorAt(i, _c.setHex(i === qkTop[0] ? 0x0b57d0 : 0x7fb2ff));
    [qIM, kIM, vIM, sIM].forEach((m) => { if (m.instanceColor) m.instanceColor.needsUpdate = true; });
  }
  function applyQKV() {
    [qIM, kIM, vIM, sIM].forEach((m) => (m.visible = false));
    const Q = F.qkv; if (!Q || !QK) return;
    const { k, t } = Q; const lt = tB[qLast].g.position; const NQ = QK.query_pos;
    // the query column above the last position
    const qOn = k === 0 ? seg(t, 0.2, 1.4) : 1;
    for (let c = 0; c < QN; c++) { const on = clamp01(qOn * QN - c); _p.set(lt.x, QB + c * QC + QC / 2, lt.z); _s.set(on, on > 0 ? 1 : 0.001, on); _m4.compose(_p, _q.identity(), _s); qIM.setMatrixAt(c, _m4); }
    qIM.instanceMatrix.needsUpdate = true; qIM.visible = true;
    // the keys, one column per token
    const kA = k === 0 ? 1 : k === 1 ? 1 - seg(t, 0, 0.7) : 0;
    if (kA > 0.01) {
      const kOn = k === 0 ? seg(t, 0.8, 2.8) : 1;
      for (let i = 0; i <= NQ; i++) {
        const tp = tB[i].g.position, r = seg(kOn, (i / (NQ + 1)) * 0.6, (i / (NQ + 1)) * 0.6 + 0.4);
        for (let c = 0; c < NC; c++) { const on = clamp01(r * NC - c); _p.set(tp.x, tp.y + COL0 + c * CELL + CELL / 2, tp.z); _s.set(on, on > 0 ? 1 : 0.001, on); _m4.compose(_p, _q.identity(), _s); kIM.setMatrixAt(i * NC + c, _m4); }
      }
      kIM.instanceMatrix.needsUpdate = true; kIM.visible = true; kIM.material.opacity = kA; kIM.material.depthWrite = kA > 0.98;
    }
    // the scores, then the weights, as bars on the tiles
    if (k >= 1) {
      for (let i = 0; i <= NQ; i++) {
        const h = k === 1 ? lerp(0.02, scoreH(i), eo(seg(t, 0.4, 2.0))) : k === 2 ? lerp(scoreH(i), weightH(i), eo(seg(t, 0.3, 1.8))) : weightH(i);
        const tp = tB[i].g.position; _p.set(tp.x, tp.y + TH, tp.z); _s.set(1, Math.max(0.001, h), 1); _m4.compose(_p, _q.identity(), _s); sIM.setMatrixAt(i, _m4);
      }
      sIM.count = NQ + 1; sIM.instanceMatrix.needsUpdate = true; sIM.visible = true; sIM.material.opacity = k === 3 ? 0.4 : 1; sIM.material.depthWrite = k !== 3;
    }
    // the values of the top four tokens fly to the last position and add up to the output
    if (k === 3) {
      const out0 = V(lt.x + 0.55, QB, lt.z);
      qkTop.slice(0, 4).forEach((j, r) => {
        const tp = tB[j].g.position, w = QK.weights[j];
        const u = eio(seg(t, 0.5 + r * 0.3, 2.3 + r * 0.3));
        const sc = lerp(1, Math.max(0.25, Math.sqrt(w)), u) * (u >= 1 ? 0 : 1);
        for (let c = 0; c < NC; c++) {
          _p.set(lerp(tp.x, out0.x, u), lerp(tp.y + TH + weightH(j) + 0.08 + c * CELL, out0.y + c * QC, u) + Math.sin(u * Math.PI) * 1.2, lerp(tp.z, out0.z, u));
          _s.set(sc, sc > 0 ? 1 : 0.001, sc); _m4.compose(_p, _q.identity(), _s); vIM.setMatrixAt(r * NC + c, _m4);
        }
      });
      const oOn = seg(t, 2.4, 3.4);
      for (let c = 0; c < NC; c++) { const on = clamp01(oOn * NC - c); _p.set(out0.x, out0.y + c * QC + QC / 2, out0.z); _s.set(on * 1.3, on > 0 ? 1 : 0.001, on * 1.3); _m4.compose(_p, _q.identity(), _s); vIM.setMatrixAt(4 * NC + c, _m4); }
      vIM.instanceMatrix.needsUpdate = true; vIM.visible = true;
    }
  }

  /* ---------- section 1: the sealed box, the text card, the output board ---------- */
  const BOX = { x0: PAGE.x0 - 0.6, x1: PAGE.x1 + 0.6, y1: STOP + 0.7, z0: PAGE.z0 - 0.5, z1: PAGE.z1 + 0.5 };
  const BW = BOX.x1 - BOX.x0, BHt = BOX.y1, BDp = BOX.z1 - BOX.z0;
  const boxMat = partMat('box', phys({ color: 0xf7f9fd, roughness: 0.42, clearcoat: 0.7, opacity: 1 }));
  const box = mesh(RB(BW, BHt, BDp, 0.6, 6), boxMat, V(PCX, BHt / 2, PCZ));
  box.renderOrder = 4;
  const seamMat = partMat('seam', new THREE.MeshStandardMaterial({ color: 0x3c90ff, emissive: 0x3c90ff, emissiveIntensity: 0.6, roughness: 0.4 }));
  // the front face: 24 faint lines, one per block inside (not yet explained)
  const faceMat = partMat('seam', new THREE.MeshStandardMaterial({ color: 0x9cc4ff, emissive: 0x3c90ff, emissiveIntensity: 0.35, roughness: 0.4, transparent: true, opacity: 0.55 }));
  const faceGeo = RB(BW - 2.4, 0.045, 0.04, 0.02);
  for (let l = 0; l < NL; l++) mesh(faceGeo, faceMat, V(PCX, slabY(l), BOX.z1 + 0.02), scene, false).renderOrder = 6;
  const seam = mesh(RB(BW - 1.0, 0.06, 0.06, 0.03), seamMat, V(PCX, 1.2, BOX.z1 + 0.01), scene, false);
  const shellMat = partMat('shell', new THREE.MeshBasicMaterial({ color: 0x3c90ff, transparent: true, opacity: 0.5, depthWrite: false }));
  const shellLines = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(BW, BHt, BDp)), new THREE.LineBasicMaterial({ color: 0x8fb8f0, transparent: true, opacity: 0.75, depthWrite: false }));
  shellLines.position.set(PCX, BHt / 2, PCZ); scene.add(shellLines); partMat('shell', shellLines.material);
  void shellMat;
  const tModel = tag('The model', `${esc(M.model.replace('Qwen/', ''))} · ${fmt(Math.round(M.params / 1e6))} million weights`, V(PCX, BHt + 0.35, PCZ), '', [0.5, 1]);
  // the input card (left)
  const IN = V(BOX.x0 - 5.4, 0, PCZ + 1.0);
  const inMat = partMat('input', phys({ color: 0xffffff, roughness: 0.35 }));
  mesh(RB(3.6, 0.3, 2.6, 0.14), inMat, V(IN.x, 0.15, IN.z));
  const inGlass = mesh(RB(3.4, 2.4, 0.1, 0.06), partMat('input', phys({ color: 0xdcebff, opacity: 0.4, roughness: 0.06, clearcoat: 1, envMapIntensity: 1.5 })), V(IN.x, 1.75, IN.z - 0.6), scene, false);
  inGlass.rotation.x = -0.12;
  blob(IN.x, IN.z, 5.5, 4.5, 'input');
  const lIn = note(V(IN.x, 3.15, IN.z - 0.6), [0.5, 1]);
  const pipeCurve = new THREE.CatmullRomCurve3([V(IN.x + 1.8, 1.0, IN.z - 0.3), V(IN.x + 3.2, 1.6, IN.z - 0.4), V(BOX.x0 - 0.4, 1.4, IN.z - 0.6), V(BOX.x0 + 0.2, 1.2, IN.z - 0.6)]);
  const pipe = mesh(new THREE.TubeGeometry(pipeCurve, 60, 0.26, 20), partMat('input', phys({ color: 0xe2efff, roughness: 0.1, clearcoat: 1, opacity: 0.3, envMapIntensity: 1.4 })), null, scene, false);
  const packetMat = new THREE.MeshPhysicalMaterial({ color: 0x3c90ff, emissive: 0x3c90ff, emissiveIntensity: 0.45, roughness: 0.3, clearcoat: 0.8, transparent: true });
  const packet = mesh(RB(0.7, 0.34, 0.34, 0.13), packetMat, V(0, 0, 0)); packet.visible = false;
  void pipe;
  // the output board (right): 10 bars, the vocabulary strip above them, the temperature dial in front
  const OB = V(BOX.x1 + 5.0, 0, PCZ + 0.6);
  const BY = (i) => 5.05 - i * 0.5;
  const boardG = new THREE.Group(); boardG.position.copy(OB); boardG.rotation.y = -0.3; boardG.scale.setScalar(1.3); scene.add(boardG);
  mesh(RB(6.8, 0.3, 2.6, 0.14), partMat('board', phys({ color: 0xffffff, roughness: 0.35 })), V(0.4, 0.15, 0.2), boardG);
  const boardBack = mesh(RB(6.4, 5.8, 0.14, 0.1), partMat('board', phys({ color: 0xf4f7fc, roughness: 0.45, clearcoat: 0.5 })), V(0.4, 3.2, -0.55), boardG);
  void boardBack;
  blob(OB.x, OB.z, 9, 5, 'board');
  const barMat = (hex) => partMat('bars', phys({ color: hex, roughness: 0.32, clearcoat: 0.8, emissive: hex, emissiveIntensity: 0.12 }));
  const bars = Array.from({ length: 10 }, (_, i) => {
    const m = mesh(RB(1, 0.34, 0.34, 0.12), barMat(0x3c90ff), V(-1.6, BY(i), -0.3), boardG);
    const lt = label('', null, { center: [1, 0.5], kind: 'bar', parent: boardG }); lt.o.position.set(-1.78, BY(i), -0.3);
    const lp = label('', null, { center: [0, 0.5], kind: 'bar', parent: boardG });
    return { m, lt, lp, len: 0.001, p: 0, txt: '' };
  });
  [[BOX.x0 - 0.02, 1.2, IN.z - 0.6], [BOX.x1 + 0.02, 4.2, OB.z - 0.4]].forEach(([x, y, z]) => {
    const r = mesh(new THREE.TorusGeometry(0.46, 0.08, 16, 56), seamMat, V(x, y, z), scene, false); r.rotation.y = Math.PI / 2;
    const d = mesh(new THREE.CircleGeometry(0.4, 40), partMat('seam', new THREE.MeshBasicMaterial({ color: 0x0b57d0, transparent: true, opacity: 0.85 })), V(x + (x < 0 ? -0.01 : 0.01), y, z), scene, false); d.rotation.y = x < 0 ? -Math.PI / 2 : Math.PI / 2;
  });
  const tBoard = tag('Next token', 'probabilities', null, '', [0.5, 1]); boardG.add(tBoard.o); tBoard.o.position.set(0.4, 6.55, -0.5);
  // the vocabulary strip (unembedding): 151,936 scores, drawn as 260 thin bars
  const VN = 260;
  const vocMat = partMat('vocab', new THREE.MeshStandardMaterial({ color: 0xbcd6fb, roughness: 0.5, emissive: 0x3c90ff, emissiveIntensity: 0.08 }));
  const vocIM = new THREE.InstancedMesh(new THREE.BoxGeometry(0.018, 1, 0.05), vocMat, VN); vocIM.frustumCulled = false; boardG.add(vocIM);
  const vocH = Array.from({ length: VN }, (_, i) => { const r = Math.abs(Math.sin(i * 12.9898) * 43758.5453) % 1; return 0.06 + 0.32 * r * r; });
  [37, 120, 201, 66, 158].forEach((i, k) => (vocH[i] = 1.35 - k * 0.2));
  const unMat = partMat('vocab', phys({ color: 0xdcebff, opacity: 0.45, roughness: 0.06, clearcoat: 1, envMapIntensity: 1.5 }));
  const unPlate = mesh(RB(6.2, 0.1, 1.0, 0.04), unMat, V(0.4, 6.9, -0.3), boardG, false); void unPlate;
  const tVocab = tag('Unembedding', `896 → ${fmt(M.vocab)} scores → softmax`, null, '', [0.5, 1]); boardG.add(tVocab.o); tVocab.o.position.set(0.4, 8.7, -0.3);
  // the beam from the top of the stack into the board
  boardG.updateMatrixWorld(true);
  const vocEnd = boardG.localToWorld(V(-2.95, 7.35, -0.3)), flyFrom = boardG.localToWorld(V(-1.6, BY(0), 0.2));
  const beamCurve = () => { const a = tilePos(tB[qLast], 0); return new THREE.CatmullRomCurve3([V(a.x, STOP + 0.1, a.z), V(a.x + 2.5, STOP + 2.0, a.z + 0.2), V(vocEnd.x - 2.5, vocEnd.y + 1.6, vocEnd.z), vocEnd]); };
  const beamMat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false,
    uniforms: { uC: { value: new THREE.Color(C.sky) }, uHead: { value: 0 }, uOn: { value: 0 }, uOp: { value: 0 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: `uniform vec3 uC; uniform float uHead, uOn, uOp; varying vec2 vUv;
      void main(){ float d = uHead - vUv.x; float comet = d >= 0. ? exp(-d / .2) : exp(d / .01);
        gl_FragColor = vec4(mix(uC, vec3(1.), comet*uOn*.3), uOp * (0.22 + uOn * comet * .78));
        #include <colorspace_fragment>
      }`,
  });
  const beam = mesh(new THREE.TubeGeometry(beamCurve(), 120, 0.05, 8), beamMat, null, scene, false);
  // the temperature dial
  const DL = V(OB.x - 4.6, 0, OB.z + 3.6);
  const dialG = new THREE.Group(); dialG.position.copy(DL); scene.add(dialG);
  mesh(new THREE.CylinderGeometry(1.25, 1.35, 0.22, 64), partMat('dial', phys({ color: 0xffffff, roughness: 0.35 })), V(0, 0.11, 0), dialG);
  const knob = mesh(new THREE.CylinderGeometry(0.78, 0.86, 0.5, 64), partMat('dial', phys({ color: 0xeef3fa, roughness: 0.3, clearcoat: 0.9 })), V(0, 0.47, 0), dialG);
  const pointer = mesh(RB(0.12, 0.08, 0.72, 0.03), partMat('dial', new THREE.MeshStandardMaterial({ color: 0x0b57d0, emissive: 0x3c90ff, emissiveIntensity: 0.5 })), V(0, 0.76, 0), dialG, false);
  pointer.geometry.translate(0, 0, -0.36);
  const dialAng = (Tm) => lerp(2.2, -2.2, clamp01(Tm / 2));
  const dialTicks = [0, 0.7, 1.0, 1.2, 2.0].map((Tm) => { const a = dialAng(Tm); const lb = label(`<span class="b3d-chip dim"><b>${Tm.toFixed(1)}</b></span>`, V(DL.x + Math.sin(a) * -1.75, 0.35, DL.z + Math.cos(a) * -1.75), { center: [0.5, 0.5], kind: 'chip' }); return { Tm, lb }; });
  const tDial = tag('Temperature', '', V(DL.x, 0.15, DL.z + 1.45), '', [0.5, 0]);
  blob(DL.x, DL.z, 3.4, 3.4, 'dial');

  /* ---------- section 3: the embedding map (PCA) ---------- */
  const MAPC = V(BOX.x0 - 5.6, 6.6, PCZ - 2.6), MS = 4.4;
  const mapG = new THREE.Group(); mapG.position.copy(MAPC); mapG.rotation.y = 0.32; scene.add(mapG);
  const mapBox = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(MS, MS, MS)), new THREE.LineBasicMaterial({ color: 0x9cc4ff, transparent: true, opacity: 0.9, depthWrite: false }));
  mapG.add(mapBox); partMat('map', mapBox.material);
  const mapFloor = mesh(RB(MS, 0.06, MS, 0.04), partMat('map', phys({ color: 0xeaf3ff, opacity: 0.55, roughness: 0.2, clearcoat: 1 })), V(0, -MS / 2, 0), mapG, false);
  void mapFloor;
  mesh(new THREE.CylinderGeometry(0.08, 0.08, MAPC.y - MS / 2, 12), partMat('map', phys({ color: 0xdfe6f2, roughness: 0.4 })), V(0, -(MAPC.y - MS / 2) / 2 - MS / 2, 0), mapG);
  mesh(new THREE.CylinderGeometry(1.0, 1.15, 0.2, 48), partMat('map', phys({ color: 0xffffff, roughness: 0.35 })), V(0, -MAPC.y + 0.1, 0), mapG);
  const GROUPC = { 'bike parts': 0x3c90ff, places: 0x1e8e5a, purchasing: 0x8a5cf6, time: 0xd08a12, numbers: 0x5d6b85, animals: 0xc4511f };
  const pcaW = T.embeddings.pca.words;
  const ext = [0, 1, 2].map((k) => Math.max(...pcaW.map((w) => Math.abs(w.xyz[k]))));
  const mapP = (xyz) => V((xyz[0] / ext[0]) * MS * 0.44, (xyz[1] / ext[1]) * MS * 0.44, (xyz[2] / ext[2]) * MS * 0.44);
  const dotGeo = new THREE.SphereGeometry(0.1, 20, 14);
  const dots = pcaW.map((w) => {
    const mat = partMat('map', new THREE.MeshStandardMaterial({ color: GROUPC[w.group], emissive: GROUPC[w.group], emissiveIntensity: 0.25, roughness: 0.4 }));
    const m = mesh(dotGeo, mat, mapP(w.xyz), mapG, false);
    return { w, m, p: mapP(w.xyz) };
  });
  const mapLbl = {};
  ['battery', 'charger', 'pedal', 'Manchester', 'Leeds', 'London', 'Monday', 'October', 'two', 'order', 'invoice', 'dog'].forEach((w) => {
    const d = dots.find((x) => x.w.word === w); if (!d) return;
    const l = label(`<span class="b3d-chip"><b style="color:#${GROUPC[d.w.group].toString(16).padStart(6, '0')}">${esc(w)}</b></span>`, null, { center: [0.5, 1.25], parent: d.m, kind: 'chip' });
    mapLbl[w] = l;
  });
  const tMap = tag('Embedding map', '896 numbers squeezed to 3 (PCA)', V(MAPC.x, MAPC.y + MS / 2 + 0.5, MAPC.z), '', [0.5, 1]);
  const lMapKey = note(V(MAPC.x - MS * 0.2, MAPC.y - MS / 2 - 0.3, MAPC.z + 1.2), [0.5, 0]);
  const nbLines = new THREE.LineSegments(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0x0b57d0, transparent: true, opacity: 0, depthWrite: false })); mapG.add(nbLines);
  {
    const pts = [];
    const link = (a, list) => { const da = dots.find((x) => x.w.word === a); list.forEach((b) => { const db = dots.find((x) => x.w.word === b); if (da && db) pts.push(da.p.x, da.p.y, da.p.z, db.p.x, db.p.y, db.p.z); }); };
    const inRef = (nm) => T.embeddings.neighbours[nm].neighbours.map((n) => n.text.trim()).filter((w) => pcaW.some((x) => x.word === w));
    link('battery', inRef('battery')); link('Manchester', inRef('Manchester'));
    nbLines.geometry.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  }

  /* ---------- section 8: the training timeline ---------- */
  const TLz = PAGE.z1 + 2.3, TLx0 = BOX.x0 - 3, TLx1 = OB.x + 2.4;
  const tlMat = partMat('tl', phys({ color: 0xffffff, roughness: 0.4 }));
  mesh(RB(TLx1 - TLx0, 0.12, 0.9, 0.08), tlMat, V((TLx0 + TLx1) / 2, 0.06, TLz));
  const tlSeg = [[0, 0.46], [0.46, 0.58], [0.58, 0.66]].map(([a, b], i) => {
    const x0 = lerp(TLx0 + 0.4, TLx1 - 0.4, a), x1 = lerp(TLx0 + 0.4, TLx1 - 0.4, b);
    const mat = partMat('tl', phys({ color: [0x3c90ff, 0x6aa8ff, 0x9cc4ff][i], roughness: 0.35, emissive: 0x3c90ff, emissiveIntensity: 0.15 }));
    const m = mesh(RB(Math.max(0.05, x1 - x0 - 0.06), 0.1, 0.5, 0.05), mat, V((x0 + x1) / 2, 0.17, TLz));
    return { m, x0, x1 };
  });
  const tlX = (u) => lerp(TLx0 + 0.4, TLx1 - 0.4, u);
  const stopMat = partMat('tl', new THREE.MeshStandardMaterial({ color: 0x0b57d0, emissive: 0x3c90ff, emissiveIntensity: 0.4 }));
  const tlStop = mesh(RB(0.08, 1.3, 0.08, 0.03), stopMat, V(tlX(0.66), 0.65, TLz), scene, false);
  const askMat = partMat('tl', new THREE.MeshStandardMaterial({ color: 0xc4511f, emissive: 0xc4511f, emissiveIntensity: 0.4 }));
  const tlAsk = mesh(RB(0.08, 1.3, 0.08, 0.03), askMat, V(tlX(0.98), 0.65, TLz), scene, false);
  void tlStop; void tlAsk;
  const tr = T.training || { stages: [], released: '2024-09-19', asked: '2026-10-26' };
  const dstr = (s) => new Date(s + 'T12:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  const tlL = [
    tag(esc(tr.stages[0] ? tr.stages[0].name : 'Pretraining'), esc(tr.stages[0] ? tr.stages[0].size : ''), V((tlSeg[0].x0 + tlSeg[0].x1) / 2, 0.3, TLz + 0.5), '', [0.5, 0]),
    tag(esc(tr.stages[1] ? tr.stages[1].name : 'Instruction tuning'), '', V((tlSeg[1].x0 + tlSeg[1].x1) / 2 - 0.4, 0.3, TLz + 0.5), '', [0.5, 0]),
    tag(esc(tr.stages[2] ? tr.stages[2].name : 'Preference tuning'), '', V((tlSeg[2].x0 + tlSeg[2].x1) / 2 + 1.5, 1.5, TLz - 0.2), '', [0.5, 1]),
    tag('Last training day', `released ${dstr(tr.released)}`, V(tlX(0.66), 1.4, TLz), '', [0.5, 1]),
    tag('Emma asks', dstr(tr.asked), V(tlX(0.98), 1.4, TLz), 'ember', [0.5, 1]),
  ];
  const lTiny = note(V(tlX(0.25), 1.6, TLz - 0.4), [0.5, 1]);

  /* ---------- section 9: the two sockets ---------- */
  const fz = tFactTiles.length ? tFactTiles[0].home.z : PCZ;
  const SK = V(PAGE.x0 - 3.4, 0, fz);
  const sockets = [0, 1].map((i) => {
    const g = new THREE.Group(); g.position.set(SK.x - i * 0.4, 0, SK.z - 1.3 + i * 2.6); scene.add(g);
    mesh(RB(1.7, 0.28, 1.7, 0.14), partMat('sock', phys({ color: 0xffffff, roughness: 0.35 })), V(0, 0.14, 0), g);
    const ringMat = partMat('sock', phys({ color: 0xffffff, roughness: 0.3, clearcoat: 0.9, emissive: 0x1e8e5a, emissiveIntensity: 0.1 }));
    const ring = mesh(new THREE.TorusGeometry(0.52, 0.11, 20, 64), ringMat, V(0, 0.42, 0), g); ring.rotation.x = Math.PI / 2;
    const core = mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.12, 40), partMat('sock', new THREE.MeshStandardMaterial({ color: 0x1e8e5a, emissive: 0x1e8e5a, emissiveIntensity: 0.3, roughness: 0.4 })), V(0, 0.36, 0), g);
    blob(g.position.x, g.position.z, 2.6, 2.6, 'sock');
    const lb = label(`<span class="b3d-tag green" style="flex-direction:column;align-items:flex-start;gap:2px;border-radius:14px"><span style="display:flex;align-items:center;gap:8px"><i class="d"></i>${i === 0 ? 'Knowledge' : 'Tools'}</span><small>${i === 0 ? 'Lecture 3 · search the documents' : 'Lecture 4 · ask Ledgerline'}</small></span>`, V(g.position.x - 1.05, 0.3, g.position.z), { center: [1, 0.5], kind: 'note' });
    return { g, ringMat, core, lb };
  });
  const sockPipe = sockets.map((s, i) => {
    const ft = tFactTiles[0];
    const p = ft ? (ft.fhome || ft.home) : { x: 0, z: 0 };
    const x0 = s.g.position.x, z0 = s.g.position.z, xe = p.x - ft.w / 2 - 0.1;
    const curve = new THREE.CatmullRomCurve3([V(x0, 0.55, z0), V(x0 + 1.0, 0.9, z0), V(xe - 1.0, 0.6, lerp(z0, p.z, 0.8)), V(xe, TH + 0.1, p.z)]);
    const mat = partMat('sockp', new THREE.MeshBasicMaterial({ color: 0x1e8e5a, transparent: true, opacity: 0.55, depthWrite: false }));
    return mesh(new THREE.TubeGeometry(curve, 80, 0.045, 8), mat, null, scene, false);
  });
  void sockPipe;

  /* ---------- notes (transient callouts, one set reused) ---------- */
  const notes = Array.from({ length: 7 }, () => note(V(0, 0, 0)));
  const chips = Array.from({ length: 28 }, () => chip(V(0, 0, 0)));
  const lensTags = Array.from({ length: NL }, () => label('', V(0, 0, 0), { center: [1, 0.5], kind: 'lens' }));

  /* =========================================================== stages */
  const LENS = D.lensLast, LDIG = T.logit_lens.digits;
  const nm = (s) => tq(s);
  const fin = T.final.last, finD = T.final.digit;
  const top5 = (arr, n = 5) => arr.slice(0, n).map((x) => `${nm(x.text)} ${pct(x.p)}`).join(', ');
  const ans = D.ans, ansN = ans.length, dIdx = T.generation.digit_steps;
  const firstDigitAt = dIdx[0];
  const wordList = (nb, n = 5) => nb.neighbours.slice(0, n).map((x) => esc(x.text.trim())).join(', ');
  const vb = T.embeddings.values.find((v) => v.i === D.kp.battery).v16, vm = T.embeddings.values.find((v) => v.i === D.kp.Manchester).v16;
  const samp = T.generation.samples_t07;
  const sampN = samp.map((s) => s.numbers[0]).filter((x) => x !== undefined);
  const truth = T.facts.truth;
  const userText = T.prompt.question;
  const facts5 = D.sampF.filter((s) => s.numbers.includes(truth)).length;
  const CAP = {
    1: [
      ['A language model is a sealed box', `Text goes in: Ask Northbridge's system prompt and Emma's question, exactly as the app sends them with its tools taken away. What comes out?`],
      ['Out comes a guess for the next token', `Not an answer: a probability for every possible next piece of text. After Emma's question the top guess is ${nm(fin['1.0'][0].text)} at <b>${pct(fin['1.0'][0].p)}</b>.`],
      ['Every word of the reply is the same game', `A few turns later the reply reads “${esc(ans.slice(0, firstDigitAt).map((s) => s.text).join('').trim())}”. Now the box chooses the first digit of the stock: ${top5(finD['1.0'], 4)}. Nothing is looked up.`],
    ],
    2: [
      [`The box opens: the text becomes ${D.N} tokens`, `The chat template wraps each message in markers, and the tokenizer cuts everything into pieces from a fixed list of ${fmt(M.tokenizer_len)}. Each piece is a <em>token</em>.`],
      ['Every token is a number', `System prompt <b>${D.sysN}</b> tokens, Emma's question <b>${D.userN}</b>, template markers <b>${D.tplN}</b>. The model never sees letters, only ids: ${nm(' Manchester')} is ${D.toks[D.kp.Manchester].id}, ${nm(' battery')} is ${D.toks[D.kp.battery].id}.`],
      ['How words and numbers are cut', `Common words are one token. ${nm(' e-bike')} is three. Numbers are cut digit by digit, so <b>5,400</b> is five tokens. The date in the system prompt is digits too.`],
      ['Tokens are what you pay for', `Requests are counted and billed in tokens: <b>${D.N}</b> in for this question, <b>${ansN}</b> out for the reply. This model can read at most ${fmt(M.context)} tokens at once: its <em>context window</em>.`],
    ],
    3: [
      ['Each token id picks a row of 896 numbers', `The first layer is a lookup table: ${fmt(M.vocab)} rows of ${M.d_model} numbers (${Math.round(M.embedding_params / 1e6)} million of the ${Math.round(M.params / 1e6)} million weights). Each tile rises into its <em>vector</em>; 12 of the 896 cells are drawn.`],
      [`${nm(' battery')}, as the model first sees it`, 'The first 8 of its 896 numbers. No single number means anything on its own; the pattern does.'],
      ['Similar words get similar vectors', `The 896 numbers squeezed to 3 (<em>PCA</em>) for ${pcaW.length} words: cities sit together, days and months together, bike parts together. Nobody labelled them; training did.`],
      ['Nearest neighbours', `The closest vectors in the whole vocabulary: ${nm(' battery')} → ${wordList(T.embeddings.neighbours.battery)}. ${nm(' Manchester')} → ${wordList(T.embeddings.neighbours.Manchester)}.`],
    ],
    4: [
      ['Three vectors per token: query, key, value', `In block ${QK.layer}, head ${QK.head}, every token's vector is multiplied by three learned matrices: a <em>query</em> (what this position is looking for), a <em>key</em> (what each token offers) and a <em>value</em> (what it passes on). ${QK.head_dim} numbers each; 12 are drawn.`],
      ['Score: how well each key matches the query', `score = query · key ÷ √${QK.head_dim}, one number per earlier token. Emma's ${nm(' Manchester')} scores highest, <b>${QK.scores[qkTop[0]].toFixed(2)}</b>; next is ${nm(tB[qkTop[1]].t.text)} at ${QK.scores[qkTop[1]].toFixed(2)}.`],
      ['Softmax turns scores into weights', `Each weight = e<sup>score</sup> ÷ the sum over all ${QK.query_pos + 1} tokens. A lead of ${(QK.scores[qkTop[0]] - QK.scores[qkTop[1]]).toFixed(1)} points becomes <b>${pct(QK.weights[qkTop[0]])}</b> on ${nm(' Manchester')}; the runner-up gets ${pct(QK.weights[qkTop[1]])}.`],
      ['The output: a weighted sum of values', `The head's output for the last position = Σ weight × value: ${qkTop.slice(0, 3).map((j) => `${pct(QK.weights[j])} · v(${nm(tB[j].t.text)})`).join(' + ')} + … ${QK.head_dim} numbers, sent on up the stack.`],
      ['All heads, all blocks, averaged', `The same look-back in all 14 heads of all 24 blocks, averaged: thickness = the real weight. A third (${pct(T.attention.last.avg.reduce((s, r) => s + r[0], 0) / NL)}) rests on the very first token.`],
      [`Another head mixes ${nm(' battery')} in`, `Block ${H.battery.layer}, head ${H.battery.head}: ${pct(H.battery.weight_last)} on ${nm(' battery')}, the rest on ${nm(' Manchester')}, ${nm(' packs')} and the markers. One head usually mixes several words.`],
      ['Some heads just rest', `Block ${H.start.layer}, head ${H.start.head} puts ${pct(H.start.weight_last)} on the first token: a head with nothing to add parks its weight there.`],
      ['Only backwards, never forward', `A token sees itself and earlier tokens only. When the model read ${nm(' battery')}, the words after it did not exist for it yet. That is what lets it write left to right.`],
    ],
    5: [
      ['One block = attention + MLP', `Attention mixes in what earlier tokens carry; then a small network, the <em>MLP</em> (${M.d_model} → ${fmt(M.mlp_hidden)} → ${M.d_model}), updates each token's vector on its own. The vector keeps its size: 896 numbers.`],
      [`${NL} blocks, one on top of the other`, `Every token's vector passes up through all ${NL} <em>blocks</em>; ${Math.round(M.params / 1e6)} million weights in all. Each block adds a little to the vector, nothing more.`],
      ['What would it say, block by block?', 'The <em>logit lens</em>: decode the last position after every block, as if the model stopped there. The early blocks give fragments of code and other languages.'],
      ['The answer forms near the top', `${nm(LENS[D.firstLoose - 1].top[0].text)} first appears after block ${D.firstLoose}; ${nm(D.finalTok.text)} holds from block ${D.exactFrom} and reaches <b>${pct(LENS[NL - 1].top[0].p)}</b> at block ${NL}. Most of the deciding happens in the last few blocks.`],
    ],
    6: [
      ['The top vector meets the whole vocabulary', `One more multiplication gives a score for each of the ${fmt(M.vocab)} tokens; <em>softmax</em> turns the scores into probabilities that add up to 1. At temperature 1: ${top5(fin['1.0'], 3)}.`],
      ['Temperature 0: always the top token', `<em>Greedy</em> decoding takes ${nm(fin['0'][0].text)} every time. Same input, same output.`],
      ['Temperature 0.7: sharper', `Dividing the scores by 0.7 before softmax: ${top5(fin['0.7'], 3)}.`],
      ['Temperature 1.2: flatter, more surprises', `Dividing by 1.2: ${top5(fin['1.2'], 3)}. Higher temperature, more often a less likely token.`],
      ['One token is picked', `At temperature 0 the pick is ${nm(fin['0'][0].text)}. One full pass through ${Math.round(M.params / 1e6)} million weights produced exactly one token.`],
    ],
    7: [
      ['The pick joins the text, and the whole pass runs again', `${nm(ans[0].text)} is appended; ${D.N + 1} tokens go back in. The next guess: ${nm(ans[1].text)} ${pct(ans[1].p)}.`],
      ['Token by token', `${ans.slice(1, firstDigitAt).map((s) => `${nm(s.text)} ${pct(s.p)}`).join(' → ')}. Each turn is a full pass through all ${NL} blocks.`],
      ['Now it writes a number', `First digit: ${top5(finD['1.0'], 5)}. In the logit lens the digit was ${nm(LDIG[0].lens[20].top[0].text)} after block 21, ${nm(LDIG[0].lens[22].top[0].text)} after block 23, and ${nm(LDIG[0].lens[23].top[0].text)} only after block 24.`],
      [`“${D.numStr}”, one digit at a time`, `${D.dig.map((d) => `${nm(d.token)} ${pct(d.p)}`).join(' → ')}. The rest is near certain: ${nm(' battery')} ${pct(ans.find((s) => s.text === ' battery').p)}. ${ansN} tokens, ${ansN} passes.`],
      ['Ask again, get another number', `Five samples at temperature 0.7 (seeds 0 to 4): ${sampN.map(fmt).join(', ')}. Each one sounds just as sure.`],
    ],
    8: [
      ['Before training, the weights are random', `${Math.round(M.params / 1e6)} million numbers set at random. A box like that turns any question into noise.`],
      ['Pretraining: predict the next token, again and again', `${esc(tr.stages[0] ? tr.stages[0].size : '')}: web text, books, code and maths. After each guess, every weight is nudged a little towards the right next token.${T.tinygpt ? ' Our tiny GPT in NB2 does the same on Northbridge\'s own documents.' : ''}`],
      ['Then it learns to chat, and to please', `<em>Instruction tuning</em>: ${esc(tr.stages[1] ? tr.stages[1].size : '')} of worked chats. Then <em>preference tuning</em>: ${esc(tr.stages[2] ? tr.stages[2].size : '')}, towards the answers people rate higher.`],
      ['And then training stops', `Qwen2.5 was released on ${dstr(tr.released)}, its weights frozen. Emma asked on ${dstr(tr.asked)}. Northbridge's stock was never in the training text, and could not have been.`],
    ],
    9: [
      [`It said ${D.numStr}. Ledgerline says ${fmt(truth)}.`, `The digits were picked at ${D.dig.map((d) => pct(d.p)).join(', ')}, and the reply reads like a fact.`],
      ['Trace it back: no input token carried the stock', `At the first digit the model looks back over ${qDig + 1} tokens. The only digits it can see are today's date, 26 October 2026. The stock was not in the input, so it produced a plausible number.`],
      ['Put the fact in, and the right number comes out', `Same model, same question, one added line: “${esc(T.facts.line)}”. Greedy answer: <b>${fmt(D.numStrF.replace(/,/g, ''))}</b>. Block ${D.fa.best_head.layer}, head ${D.fa.best_head.head} puts ${pct(D.fa.best_head.row[D.fa.fact_number_positions[0]])} on the fact's “5”.`],
      ['Who puts the facts in? Lectures 3 and 4', `<em>Knowledge</em>: search Northbridge's documents and add the passages to the prompt. <em>Tools</em>: ask Ledgerline itself. Even with the fact, at temperature 0.7 only ${facts5} of 5 samples said ${fmt(truth)}.`],
    ],
  };
  const TRACE_V = {
    1: `${nm(fin['1.0'][0].text)} <b>${pct(fin['1.0'][0].p)}</b> · first digit ${nm(finD['1.0'][0].text)} <b>${pct(finD['1.0'][0].p)}</b>`,
    2: `<b>${D.N}</b> tokens · 5,400 = 5 tokens`,
    3: `<b>896</b> numbers per token`,
    4: `<b>${pct(H.Manchester.weight_last)}</b> on ${nm(' Manchester')} (block ${H.Manchester.layer})`,
    5: `<b>${NL}</b> blocks · ${nm(D.finalTok.text)} forms at block ${D.exactFrom}`,
    6: `T = 0 picks ${nm(fin['0'][0].text)}`,
    7: `<b>${ansN}</b> tokens · <b class="e">${esc(D.numStr)}</b> at ${D.dig.map((d) => pct(d.p)).join(', ')}`,
    8: `frozen <b>${dstr(tr.released)}</b>`,
    9: `with the fact: <b class="gr">${esc(D.numStrF)}</b>`,
  };
  const DUR = {
    1: [5.2, 4.6, 5.0], 2: [6.4, 3.6, 4.2, 3.4], 3: [5.6, 3.8, 4.6, 4.0], 4: [4.6, 4.0, 4.0, 4.6, 5.0, 3.6, 3.4, 4.0],
    5: [4.8, 6.4, 5.6, 4.6], 6: [5.0, 2.8, 2.8, 2.8, 3.4], 7: [5.0, 5.0, 5.4, 8.0, 4.2], 8: [3.6, 5.6, 4.0, 4.2], 9: [3.6, 5.6, 6.8, 4.6],
  };
  const stages = []; const secStart = {};
  for (let s = 1; s <= 9; s++) { secStart[s] = stages.length; CAP[s].forEach((c, k) => stages.push({ s, k, h: c[0], p: c[1], dur: DUR[s][k] })); }

  /* ---------- camera shots ---------- */
  const orbit = (tx, ty, tz, dist, pitch, yaw = 0) => { const p = pitch * Math.PI / 180, y = yaw * Math.PI / 180;
    return [V(tx + dist * Math.cos(p) * Math.sin(y), ty + dist * Math.sin(p), tz + dist * Math.cos(p) * Math.cos(y)), V(tx, ty, tz)]; };
  const qx = tB[qLast].home.x, qz = tB[qLast].home.z;
  const userRow = tB[D.kp.battery].home.z;
  const ansZ = tAns[0].home.z, ansZF = tFAns[0].home.z;
  const SHOT = {
    1: [orbit(PCX + 1.5, 5.0, PCZ, 56, 13, 3), orbit(PCX + 2.5, 4.8, PCZ, 52, 13, 5), orbit(PCX + 3.0, 4.6, PCZ, 50, 13, 6)],
    2: [orbit(PCX, 0.4, PCZ + 0.8, 29, 50, 0), orbit(PCX + 1.0, 0.3, userRow, 19, 52, 0), orbit(PCX + 2.0, 0.3, userRow - 0.6, 21, 52, 0), orbit(PCX + 1.0, 0.4, PCZ + 0.6, 28, 50, 0)],
    3: [orbit(PCX, 1.4, PCZ + 0.4, 29, 44, 0), orbit(tB[D.kp.battery].home.x + 2.4, 1.3, userRow, 15, 30, -6), orbit(MAPC.x + 3.8, MAPC.y - 0.9, MAPC.z, 22, 14, 8), orbit(MAPC.x + 4.2, MAPC.y - 0.9, MAPC.z, 22, 14, 8)],
    4: [orbit(PCX + 1.0, 1.4, PCZ + 0.9, 26, 36, 0), orbit(PCX + 1.0, 1.2, PCZ + 0.9, 26, 38, 0), orbit(PCX + 1.0, 1.2, PCZ + 0.9, 26, 40, 0), orbit(PCX + 0.5, 1.6, PCZ + 1.2, 25, 34, 0),
        orbit(PCX + 0.5, 0.8, PCZ + 0.6, 28, 50, 0), orbit(PCX + 0.5, 0.8, PCZ + 0.8, 26, 52, 0), orbit(PCX - 1.0, 0.8, PCZ + 0.4, 27, 52, 0), orbit(PCX + 0.5, 0.6, userRow - 1, 24, 52, 0)],
    5: [orbit(PCX + 1.0, S0 - 0.2, PCZ, 31, 24, 0), orbit(PCX + 1.0, STOP * 0.52, PCZ, 45, 12, 0), orbit(PCX - 2.0, STOP * 0.56, PCZ, 43, 8, -12), orbit(PCX - 3.6, slabY(17), PCZ, 31, 5, -16)],
    6: [orbit(OB.x - 5.5, 6.0, OB.z, 37, 12, -6), orbit(OB.x - 2.4, 4.4, OB.z + 1.2, 29, 12, -14), orbit(OB.x - 2.4, 4.4, OB.z + 1.2, 29, 12, -14), orbit(OB.x - 2.4, 4.4, OB.z + 1.2, 29, 12, -14), orbit(OB.x - 2.4, 4.4, OB.z + 1.2, 29, 12, -14)],
    7: [orbit(PCX + 5.0, 3.6, PCZ + 1, 46, 22, 4), orbit(PCX + 5.0, 3.6, PCZ + 1, 46, 22, 4), orbit(PCX + 5.0, 3.6, PCZ + 1, 46, 22, 4), orbit(PCX + 1.5, 0.4, ansZ - 1.5, 25, 48, 0), orbit(PCX + 1.5, 0.4, ansZ - 1.5, 26, 48, 0)],
    8: [orbit(PCX + 2, STOP * 0.42, PCZ + 3, 50, 16, 0), orbit(PCX + 2, STOP * 0.42, PCZ + 3, 50, 16, 0), orbit(PCX + 2, STOP * 0.42, PCZ + 3, 50, 16, 0), orbit(PCX + 3, 2.4, TLz - 2, 44, 22, 0)],
    9: [orbit(PCX + 1.0, 0.4, ansZ - 0.8, 22, 54, 0), orbit(PCX + 0.5, 0.4, PCZ + 0.6, 29, 58, 0), orbit(PCX + 0.5, 0.4, PCZ + 0.8, 31, 56, 0), orbit(PCX - 3.0, 0.6, PCZ + 0.8, 35, 50, -4)],
  };
  const ZOOM = opts.zoom || (mode === 'deck' ? 1.1 : 1);
  const DECKZ = { 5: 1.16, 6: 1.08, 7: 1.06, 8: 1.06 }, DECKY = { 6: -1.2 }; // the deck's free stage is shorter: these scenes step back a little more
  const cam = { pos: V(0, 30, 60), tgt: V(0, 0, 0), want: [V(0, 30, 60), V(0, 0, 0)], snap: true };

  /* =========================================================== the frame: every section writes its state, in order */
  let F;
  const DIM = 0.34;
  function reset() {
    F = { box: 0, seam: 0, shell: 0, input: 0, packet: -1, board: 0, bars: null, barsOp: 0, vocab: 0, beam: 0, beamHead: -1, dial: 0, dialT: 1,
      plinth: 0, tileOp: 0, tileGlow: new Map(), tileOpMap: new Map(), tileLift: new Map(), dropU: 1, ansN: 0, ansOp: 0, mix: 0, factOp: 0, ansFN: 0, ansFOp: 0, baseAnsOp: 1,
      col: 0, colRise: 1, colHi: new Map(), colAns: 0, map: 0, nb: 0, arcs: {}, slabs: 0, slabOp: 0, slabMode: 0, slabFill: 0, slabWave: -1, ex: 0, exSplit: 0,
      qkv: null, streams: 0, hot: 0, pulse: -1, lens: null, lensOp: 0, tl: 0, tlSeg: [0, 0, 0], tlStop: 0, tlAsk: 0, sock: 0, mask: -1, bot: { n: 0, facts: false, cursor: false } };
    for (const L of labelList) L.op = 0;
  }
  const show = (L, a) => L && L.show(a);

  function setBars(list, a, { hl = -1, color = 0x3c90ff, n = 10 } = {}) { F.bars = { list: list.slice(0, n), hl, color }; F.barsOp = Math.max(F.barsOp, a); }
  function distAt(Tm, which = 'last') { // exact probabilities from the recorded logits and log Z(T)
    const d = T.final[which === 'last' ? 'dial_last' : 'dial_digit'];
    if (!d) return T.final[which][Tm.toFixed(1)] || T.final[which]['1.0'];
    if (Tm < 0.05) return [{ text: d.top[0].text, p: 1 }];
    let i = d.T.findIndex((x) => x >= Tm - 1e-6); if (i < 0) i = d.T.length - 1;
    const t0 = d.T[i], z = d.logZ[i];
    return d.top.slice(0, 10).map((x) => ({ text: x.text, p: Math.exp(x.logit / t0 - z) }));
  }

  /* section 1: the box */
  function sec1(k, t, a) {
    F.box = 1; F.seam = 1; F.input = a; show(tModel, a);
    if (a === 1) show(lIn.set(`<div class="b3d-note sky" style="max-width:calc(330px*var(--u))"><div class="k">Text in <b>· the brain stage, no tools</b></div><div class="t" style="font-size:calc(14.5px*var(--u));color:#6b6e76">System: “${esc(T.prompt.system.split('\n')[0].slice(0, 62))}…”</div><div class="t" style="margin-top:calc(5px*var(--u));color:#0b57d0;font-weight:560">Emma: “${esc(userText)}”</div></div>`), a);
    if (k === 0 && a === 1) F.packet = seg(t, 1.2, 3.8);
    F.board = k >= 1 ? a : 0.4; if (k === 0) show(tBoard, 0.5);
    if (k >= 1) {
      if (k === 1 || a < 1) setBars(fin['1.0'], a * (k === 1 ? eo(seg(t, 0.3, 1.6)) : 1), { n: 5 });
      if (k === 2 && a === 1) setBars(finD['1.0'], 1, { n: 5, color: 0xc4511f });
      show(tBoard, a);
      F.beam = 0;
    }
    if (a === 1) F.bot = { n: k === 2 ? firstDigitAt : 0, cursor: true };
  }
  /* section 2: tokens */
  function sec2(k, t, a) {
    F.box = a === 1 && k === 0 ? 1 - eo(seg(t, 0.2, 1.6)) : 0; F.seam = F.box; F.shell = 1;
    F.plinth = 1; F.tileOp = 1; F.dropU = a === 1 && k === 0 ? seg(t, 1.0, 4.8) : 1;
    if (a < 1) return;
    if (k === 1) { tPrompt.forEach((x, i) => { if (x.kind === 'user') F.tileGlow.set(x, 0.5); }); chipAt(0, tB[D.kp.Manchester], `<span class="b3d-chip"><b>${D.toks[D.kp.Manchester].id}</b> ${nm(' Manchester')}</span>`, 1, 1.35);
      chipAt(1, tB[D.kp.battery], `<span class="b3d-chip"><b>${D.toks[D.kp.battery].id}</b> ${nm(' battery')}</span>`, 1, 1.35);
      chipAt(2, tB[3], `<span class="b3d-chip dim"><b>${D.sysN}</b> system prompt tokens</span>`, 1, 1.2);
      chipAt(3, tB[78], `<span class="b3d-chip dim"><b>${D.tplN}</b> template markers</span>`, 1, 1.2);
      chipAt(4, tB[D.kp.battery + 4], `<span class="b3d-chip"><b>${D.userN}</b> Emma's question</span>`, 1, 2.3);
    }
    if (k === 2) {
      const eb = D.toks.filter((x) => x.role === 'user' && ['e', '-b', 'ike'].includes(x.text.trim())).map((x) => tB[x.i]);
      eb.forEach((x) => F.tileGlow.set(x, 1));
      D.inputDigits.forEach((i) => F.tileGlow.set(tB[i], 0.7));
      const cut = (w, arr, cls = '') => `<div class="b3d-cut"><span class="w">${esc(w)}</span>${arr.map((x) => `<span class="tk ${cls}">${esc(vis(x.text).replace(/^ /, '␣'))}<small>${x.id}</small></span>`).join('')}</div>`;
      const nc = T.number_cuts;
      noteAt(0, V(PCX + 4.2, 1.4, tB[D.kp.battery].home.z - 2.2), `<div class="b3d-note"><div class="k">How text is cut</div>${cut('Manchester', nc[' Manchester'])}${cut('e-bike', nc[' e-bike'])}${cut('Northbridge', nc[' Northbridge'])}${cut('5,400', nc['5,400'], 'dg')}${cut('2026', nc[' 2026'].filter((x) => x.text.trim()), 'dt')}</div>`, 1, [0, 1]);
    }
    if (k === 3) {
      chipAt(0, tB[0], `<span class="b3d-chip"><b>${D.N}</b> tokens in</span>`, 1, 1.3);
      noteAt(0, V(PCX + 5.0, 1.0, PAGE.z1 + 0.3), `<div class="b3d-note"><div class="k">Counted in tokens</div><div class="b3d-tbl"><span>In</span><span class="p">${D.N}</span><span class="r">system ${D.sysN} · question ${D.userN} · markers ${D.tplN}</span><span>Out</span><span class="p">${ansN}</span><span class="r">the reply, one token per pass</span><span>Window</span><span class="p">${fmt(M.context)}</span><span class="r">the most it can read at once</span></div></div>`, 1, [0, 0]);
    }
  }
  /* section 3: vectors and the map */
  function sec3(k, t, a) {
    F.col = a === 1 ? 1 : 0.45; F.colRise = a === 1 && k === 0 ? seg(t, 0.3, 4.6) : 1;
    F.map = k >= 2 || a < 1 ? (a < 1 ? a : eo(seg(k === 2 ? t : 9, 0.2, 1.6))) : 0;
    if (a < 1) { show(tMap, a); return; }
    if (k === 1) {
      F.colHi.set(tB[D.kp.battery], 1); F.colHi.set(tB[D.kp.Manchester], 0.6);
      const vv = (v) => `<div class="b3d-vals">${v.slice(0, 8).map((x) => `<span class="${x < 0 ? 'n' : ''}">${x >= 0 ? '+' : '−'}${Math.abs(x).toFixed(4)}</span>`).join('')}</div>`;
      noteAt(0, V(tB[D.kp.battery].home.x + 1.4, COLTOP + 0.2, tB[D.kp.battery].home.z), `<div class="b3d-note sky"><div class="k">${nm(' battery')} <b>· id ${D.toks[D.kp.battery].id} · first 8 of 896</b></div>${vv(vb)}</div>`, eo(seg(t, 0.4, 1.4)), [0, 1]);
      noteAt(1, V(tB[D.kp.Manchester].home.x + 1.4, COLTOP - 0.9, tB[D.kp.Manchester].home.z + 0.4), `<div class="b3d-note"><div class="k">${nm(' Manchester')} <b>· id ${D.toks[D.kp.Manchester].id}</b></div>${vv(vm)}</div>`, eo(seg(t, 1.2, 2.2)), [0, 0]);
    }
    if (k >= 2) {
      show(tMap, 1);
      for (const [w, l] of Object.entries(mapLbl)) show(l, eo(seg(k === 2 ? t : 9, 0.8 + 0.08 * Object.keys(mapLbl).indexOf(w), 1.8 + 0.08 * Object.keys(mapLbl).indexOf(w))));
      const leg = Object.entries(GROUPC).map(([g, c]) => `<span style="display:inline-flex;align-items:center;gap:6px;margin-right:12px"><i style="width:10px;height:10px;border-radius:50%;background:#${c.toString(16).padStart(6, '0')}"></i>${esc(g)}</span>`).join('');
      noteAt(0, lMapKey.o.position, `<div class="b3d-note" style="max-width:calc(470px*var(--u))"><div class="k">${pcaW.length} words <b>· their input vectors, 3 of the PCA directions</b></div><div class="t" style="max-width:calc(450px*var(--u));line-height:1.9">${leg}</div></div>`, eo(seg(k === 2 ? t : 9, 1.6, 2.6)), [0.5, 0]);
    }
    if (k === 3) {
      F.nb = eo(seg(t, 0.2, 1.4));
      const nb = (nmw) => T.embeddings.neighbours[nmw].neighbours.slice(0, 6).map((x) => `<span>${tq(x.text)}</span><span class="p">${x.cos.toFixed(2)}</span><span></span>`).join('');
      noteAt(1, V(MAPC.x + MS * 0.5 + 1.0, MAPC.y + 1.8, MAPC.z + 1.6), `<div class="b3d-note sky"><div class="k">Closest to ${nm(' battery')} <b>· cosine, all ${fmt(M.tokenizer_len)} tokens</b></div><div class="b3d-tbl">${nb('battery')}</div></div>`, eo(seg(t, 0.4, 1.4)), [0, 1]);
      noteAt(2, V(MAPC.x + MS * 0.5 + 1.0, MAPC.y - 1.6, MAPC.z + 1.6), `<div class="b3d-note green"><div class="k">Closest to ${nm(' Manchester')}</div><div class="b3d-tbl">${nb('Manchester')}</div></div>`, eo(seg(t, 1.0, 2.0)), [0, 0]);
    }
  }
  /* section 4: attention */
  function sec4(k, t, a) {
    if (a < 1) { F.arcs.avg = Math.max(F.arcs.avg || 0, 0.1); return; }
    F.tileGlow.set(tB[qLast], 1); F.colHi.set(tB[qLast], 1);
    if (k <= 3 && QK) { secQKV(k, t); return; }
    const set = ['avg', 'bat', 'start', null][k - 4];
    if (set) {
      const grow = eo(seg(t, 0.2, 2.2));
      F.arcs[set] = { op: 1, grow };
      const S = arcSets[set];
      const top = S.arcs.filter((x) => x.j !== 0).slice(0, set === 'start' ? 0 : 3);
      top.forEach((x, i) => { F.tileGlow.set(x.b, 0.8); chipAt(i, x.b, `<span class="b3d-chip"><b>${pct(x.w)}</b> ${nm(x.b.t.text)}</span>`, seg(t, 1.4 + i * 0.3, 2.0 + i * 0.3), 1.0 + i * 0.45); });
      const z0 = S.arcs.find((x) => x.j === 0);
      if (z0) chipAt(4, tB[0], `<span class="b3d-chip dim"><b>${pct(z0.w)}</b> rests on the first token</span>`, seg(t, 1.8, 2.4), 2.6);
      const who = { avg: 'all heads, all blocks', man: `block ${H.Manchester.layer} · head ${H.Manchester.head}`, bat: `block ${H.battery.layer} · head ${H.battery.head}`, start: `block ${H.start.layer} · head ${H.start.head}` }[set];
      chipAt(5, tB[qLast], `<span class="b3d-chip"><b>from here</b> ${nm(tB[qLast].t.text)} · ${who}</span>`, 1, -0.2, [0.5, 0]);
    } else {
      F.arcs.avg = 0.1;
      const b = D.kp.battery;
      F.tileGlow.set(tB[b], 1); F.colHi.set(tB[b], 1); F.mask = b;
      chipAt(0, tB[b], `<span class="b3d-chip"><b>${nm(' battery')}</b> sees these ${b + 1} tokens</span>`, eo(seg(t, 0.5, 1.4)), 2.5);
      chipAt(1, tB[Math.min(nP - 1, b + 5)], `<span class="b3d-chip dim"><b>not yet</b> written when ${nm(' battery')} was read</span>`, eo(seg(t, 1.2, 2.0)), 1.1);
    }
  }
  /* section 4, first four states: query, key, value of block 24, head 2 (the head that finds Manchester) */
  function secQKV(k, t) {
    F.col = 0; F.qkv = { k, t };
    const who = `block ${QK.layer} · head ${QK.head}`;
    const v6 = (arr) => `<div class="b3d-vals">${arr.slice(0, 8).map((x) => `<span class="${x < 0 ? 'n' : ''}">${x >= 0 ? '+' : '−'}${Math.abs(x).toFixed(2)}</span>`).join('')}</div>`;
    const jm = qkTop[0];
    if (k === 0) {
      noteAt(0, V(PAGE.x1 + 0.4, 3.2, PCZ), `<div class="b3d-note sky"><div class="k">Query <b>· ${nm(tB[qLast].t.text)}, the last position · ${who}</b></div>${v6(QK.q)}<div class="k" style="margin-top:8px;color:#7c5cf0">Key <b>· ${nm(tB[jm].t.text)}</b></div>${v6(QK.k[jm])}<div class="k" style="margin-top:8px;color:#b7791f">Value <b>· ${nm(tB[jm].t.text)}</b></div>${v6(QK.v[jm])}<div class="t" style="margin-top:6px">First 8 of ${QK.head_dim} numbers each.</div></div>`, eo(seg(t, 1.6, 2.6)), [0, 0.5]);
      chipAt(5, tB[qLast], `<span class="b3d-chip"><b>query</b> ${nm(tB[qLast].t.text)} · ${who}</span>`, eo(seg(t, 0.8, 1.6)), QTOP + 0.35, [0.5, 1]);
      chipAt(0, tB[jm], `<span class="b3d-chip" style="border-color:rgba(124,92,240,.45)"><b style="color:#7c5cf0">key</b> ${nm(tB[jm].t.text)}</span>`, eo(seg(t, 1.2, 2.0)), KTOP + 0.35);
    }
    if (k === 1 || k === 2) {
      const rows = qkTop.slice(0, 5).map((j) => `<span>${tq(tB[j].t.text)} <span style="color:#6b6e76;font-size:.85em">#${j}</span></span><span class="p">${QK.scores[j].toFixed(2)}</span><span class="p" style="color:${k === 2 ? '#0b57d0' : '#c3c8d2'}">${pct(QK.weights[j])}</span>`).join('');
      const lo = QK.scores.reduce((m, x) => Math.min(m, x), 99);
      noteAt(0, V(PAGE.x1 + 0.4, 2.8, PCZ), `<div class="b3d-note sky"><div class="k">${k === 1 ? 'q · k ÷ √64' : 'softmax'} <b>· ${who}</b></div><div class="b3d-tbl"><span class="r">token</span><span class="r" style="text-align:right">score</span><span class="r" style="text-align:right">weight</span>${rows}</div><div class="t" style="margin-top:6px">${QK.query_pos + 1} scores in all, the lowest ${lo.toFixed(2)}. ${k === 2 ? 'The weights add up to 100%.' : ''}</div></div>`, eo(seg(t, 1.2, 2.2)), [0, 0.5]);
      qkTop.slice(0, 3).forEach((j, i) => chipAt(i, tB[j], `<span class="b3d-chip"><b>${k === 1 ? QK.scores[j].toFixed(2) : pct(QK.weights[j])}</b> ${nm(tB[j].t.text)}</span>`, eo(seg(t, 1.0 + i * 0.25, 1.8 + i * 0.25)), 0.5 + (k === 1 ? scoreH(j) : weightH(j))));
      if (k === 2) F.arcs.man = { op: 1, grow: eo(seg(t, 0.8, 2.6)) };
      chipAt(5, tB[qLast], `<span class="b3d-chip"><b>query</b> ${nm(tB[qLast].t.text)} · ${who}</span>`, 1, QTOP + 0.35, [0.5, 1]);
    }
    if (k === 3) {
      F.arcs.man = { op: 0.35, grow: 1 };
      const terms = qkTop.slice(0, 4).map((j) => `<span>${pct(QK.weights[j])} ×</span><span>v(${tq(tB[j].t.text)})</span><span></span>`).join('');
      noteAt(0, V(PAGE.x1 + 0.4, 3.0, PCZ), `<div class="b3d-note" style="border-left:calc(4px*var(--u)) solid #d08a12"><div class="k" style="color:#b7791f">Output <b>· Σ weight × value</b></div><div class="b3d-tbl">${terms}</div><div class="t" style="margin-top:4px">+ ${QK.query_pos + 1 - 4} more, each tiny. The result, first 8 of ${QK.head_dim}:</div>${v6(QK.out)}</div>`, eo(seg(t, 2.6, 3.4)), [0, 0.5]);
      chipAt(5, tB[qLast], `<span class="b3d-chip" style="border-color:rgba(208,138,18,.5)"><b style="color:#b7791f">output</b> for ${nm(tB[qLast].t.text)}</span>`, eo(seg(t, 2.8, 3.6)), QTOP + 0.35, [0.5, 1]);
    }
  }
  /* section 5: the blocks and the logit lens */
  function sec5(k, t, a) {
    F.slabs = k === 0 ? 1 : NL; F.slabOp = a === 1 ? 1 : 0.42; F.slabMode = 0; F.streams = k >= 1 ? (a === 1 ? 1 : 0.5) : 0;
    if (a === 1 && k === 1) F.slabs = Math.max(1, Math.ceil(NL * eo(seg(t, 0.3, 3.4))));
    if (a < 1) { F.lensOp = 0; return; }
    F.hot = 1;
    if (k === 0) {
      F.ex = 1; F.exSplit = eo(seg(t, 0.8, 2.2)); F.pulse = seg(t, 2.4, 4.4) * 0.12;
      show(tExA, eo(seg(t, 1.4, 2.2))); show(tExM, eo(seg(t, 1.6, 2.4)));
      noteAt(0, V(PAGE.x1 + 0.4, S0 + 3.2, PCZ), `<div class="b3d-note sky"><div class="k">Block 1</div><div class="b3d-tbl"><span>Attention</span><span class="p">14 heads</span><span class="r">each token looks back</span><span>MLP</span><span class="p">${fmt(M.mlp_hidden)}</span><span class="r">each token on its own</span></div></div>`, eo(seg(t, 1.6, 2.6)), [0, 0.5]);
    }
    if (k === 1) { F.pulse = seg(t, 2.6, 6.2); F.slabWave = seg(t, 2.6, 6.2);
      noteAt(0, V(PAGE.x1 + 0.4, STOP - 1.2, PCZ), `<div class="b3d-note sky"><div class="k">${NL} blocks</div><div class="b3d-tbl"><span>Heads</span><span class="p">${M.heads}</span><span class="r">per block</span><span>Vector</span><span class="p">${M.d_model}</span><span class="r">numbers, all the way up</span><span>Weights</span><span class="p">${Math.round(M.params / 1e6)} M</span><span class="r">in all</span></div></div>`, eo(seg(t, 3.4, 4.4)), [0, 0.5]);
    }
    if (k >= 2) { F.lens = { rows: LENS, from: 0, upto: k === 2 ? Math.ceil(NL * seg(t, 0.4, 4.6)) : NL, focus: k === 3, gap: k === 3 && mode === 'deck' ? 0.5 : 0 }; F.lensOp = 1; F.pulse = k === 2 ? seg(t, 0.4, 4.6) : -1; }
    if (k === 3) {
      const sp = sparkline(LENS.map((r) => r.final_p), D.finalTok.text);
      noteAt(0, V(PAGE.x1 + 0.4, slabY(16), PCZ), `<div class="b3d-note sky"><div class="k">${nm(D.finalTok.text)} <b>· its probability after each block</b></div>${sp}</div>`, eo(seg(t, 0.6, 1.6)), [0, 0.5]);
    }
  }
  function sparkline(ps, word, w = 300, h = 86, lab = null) {
    const n = ps.length, pmax = Math.max(...ps, 0.05);
    const x = (i) => 6 + (i / (n - 1)) * (w - 12), y = (p) => h - 18 - (p / pmax) * (h - 30);
    const d = ps.map((p, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(p).toFixed(1)}`).join('');
    return `<svg class="b3d-spark" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="width:calc(${w}px*var(--u));height:calc(${h}px*var(--u))"><path d="${d}" fill="none" stroke="#3c90ff" stroke-width="2.4"/>
      ${ps.map((p, i) => `<circle cx="${x(i)}" cy="${y(p)}" r="2.6" fill="${p > 0.01 ? '#0b57d0' : '#c3c8d2'}"/>`).join('')}
      <text x="6" y="${h - 3}" font-size="13" fill="#6b6e76" font-family="Google Sans Flex,Arial">${lab ? lab[0] : 'block 1'}</text><text x="${w - 6}" y="${h - 3}" font-size="13" fill="#6b6e76" text-anchor="end" font-family="Google Sans Flex,Arial">${lab ? lab[1] : `block ${n}: ${pct(ps[n - 1])}`}</text></svg>`;
  }
  /* section 6: unembedding and temperature */
  let userT = null;
  function sec6(k, t, a) {
    F.vocab = a; F.beam = a; F.dial = a; F.board = Math.max(F.board, a);
    show(tVocab, a); if (a === 1) show(tDial, a); show(tBoard, a);
    const Tm = [1.0, 0, 0.7, 1.2, 0][k];
    F.dialT = a < 1 ? 0 : (userT !== null ? userT : Tm);
    if (a === 1 && userT === null && tempIn && +tempIn.value !== Tm) { tempIn.value = Tm; tempOut.textContent = Tm.toFixed(2); }
    if (a < 1) { setBars(distAt(0), a, { n: 1 }); return; }
    if (k === 0) { F.beamHead = seg(t, 0.2, 2.0); setBars(distAt(1.0), eo(seg(t, 1.8, 3.2))); }
    else setBars(distAt(F.dialT), 1, { hl: k === 4 ? 0 : -1 });
    if (k === 4) F.pickLift = eo(seg(t, 0.3, 1.4));
    dialTicks.forEach((x) => show(x.lb, 1));
  }
  /* section 7: the loop */
  function sec7(k, t, a) {
    F.colAns = 1;
    if (a < 1) { F.ansN = ansN; F.ansOp = 1; F.bot = { n: ansN }; return; }
    // timeline of tokens over the section's states
    let n = 0, live = 0, cur = -1;
    if (k === 0) { n = t >= 2.0 ? 1 : 0; cur = t > 0.4 && t < 2.0 ? 0 : -1; live = seg(t, 0.4, 2.0); F.pulse = seg(t, 2.0, 4.2); F.slabWave = seg(t, 2.0, 4.2); }
    if (k === 1) { const u = seg(t, 0.3, 4.4) * (firstDigitAt - 1); n = 1 + Math.floor(u); cur = n; live = u % 1; if (n >= firstDigitAt) { n = firstDigitAt; cur = -1; } F.slabWave = live; }
    if (k === 2) { n = firstDigitAt + (t >= 4.8 ? 1 : 0); cur = t > 3.6 && t < 4.8 ? firstDigitAt : -1; live = seg(t, 3.6, 4.8); F.slabWave = seg(t, 0.2, 2.4);
      F.lens = { rows: LDIG[0].lens, upto: NL, focus: true, n: 5, gap: mode === 'deck' ? 0.8 : 0.62, q: tAns[firstDigitAt - 1], digit: true }; F.lensOp = eo(seg(t, 0.6, 1.4)); F.hotTile = tAns[firstDigitAt - 1]; }
    if (k === 3) { const u = seg(t, 0.3, 6.6) * (ansN - firstDigitAt - 1); n = firstDigitAt + 1 + Math.floor(u); cur = n; live = u % 1; if (n >= ansN) { n = ansN; cur = -1; } F.slabWave = live; }
    if (k === 4) { n = ansN; }
    F.ansN = n; F.ansOp = 1; F.ansLive = cur >= 0 && cur < ansN ? { j: cur, u: live } : null;
    F.bot = { n: Math.min(ansN, n + (F.ansLive && live > 0.85 ? 1 : 0)), cursor: k < 4 };
    // the bars: the distribution that produced the token being written
    const j = Math.max(0, Math.min(ansN - 1, cur >= 0 ? cur : n - 1));
    const st = ans[j];
    if (k === 2) setBars(finD['1.0'], 1, { hl: 0, color: 0xc4511f });
    else if (k < 4) setBars(st.alts, 1, { hl: st.alts.findIndex((x) => x.id === st.id), color: digitSet.has(j) ? 0xc4511f : 0x3c90ff, n: 5 });
    else setBars(st.alts, DIM, { n: 5 });
    F.beam = 1; F.beamHead = k < 4 ? (F.ansLive ? F.ansLive.u : -1) : -1;
    if (k === 2) noteAt(1, V(PAGE.x1 + 0.4, slabY(19), PCZ), `<div class="b3d-note ember"><div class="k">The first digit <b>· block by block</b></div>${sparkline(LDIG[0].lens.map((r) => r.final_p), '1')}</div>`, eo(seg(t, 1.0, 2.0)), [0, 0.5]);
    if (k === 4) {
      const rows = samp.map((s) => `<span class="s">seed ${s.seed}</span><span>${esc(s.text).replace(/(\d[\d,]*)/, '<b>$1</b>')}</span>`).join('');
      noteAt(0, V(PAGE.x1 + 0.5, 4.2, PAGE.z1 - 0.5), `<div class="b3d-note ember"><div class="k">Five samples <b>· temperature 0.7</b></div><div class="b3d-samp">${rows}</div></div>`, eo(seg(t, 0.4, 1.4)), [0, 0.5]);
    }
  }
  /* section 8: training */
  function sec8(k, t, a) {
    F.tl = a; if (a === 1) tlL.forEach((l, i) => show(l, i < 3 ? (k >= Math.min(i + 1, 2) ? 1 : 0) : (k >= 3 ? 1 : 0)));
    F.slabMode = a === 1 ? 2 : 0; F.slabFill = 1;
    F.tlSeg = [1, 1, 1]; F.tlStop = 1; F.tlAsk = 1;
    if (a < 1) return;
    if (k === 0) { F.slabMode = 1; F.slabFill = 0; F.tlSeg = [0, 0, 0]; F.tlStop = 0; F.tlAsk = 0; }
    if (k === 1) { F.slabFill = eo(seg(t, 0.5, 4.8)); F.tlSeg = [eo(seg(t, 0.3, 4.6)), 0, 0]; F.tlStop = 0; F.tlAsk = 0; }
    if (k === 2) { F.tlSeg = [1, eo(seg(t, 0.3, 1.6)), eo(seg(t, 1.6, 2.9))]; F.tlStop = 0; F.tlAsk = 0; F.slabWave = seg(t, 0.3, 2.9); }
    if (k === 3) { F.tlStop = eo(seg(t, 0.2, 1.0)); F.tlAsk = eo(seg(t, 1.2, 2.2)); }
    if (T.tinygpt) {
      const g = T.tinygpt, c = g.curve, sm0 = g.samples || {};
      const pr = Object.keys(sm0)[0] || '', sm = typeof sm0[pr] === 'object' ? sm0[pr] : sm0;
      const cont = (txt) => esc(txt.slice(pr.length).split('\n')[0].slice(0, 70)).replace(/(\d[\d,]*)/, '<b>$1</b>');
      const head = `<div class="k">The tiny GPT from NB2 <b>· ${fmt(g.params)} weights · Northbridge's own documents</b></div>`;
      const start = `<span style="color:#45474d;font-weight:560">${esc(pr)}</span>`;
      if (k === 0) noteAt(0, lTiny.o.position, `<div class="b3d-note">${head}<div class="t" style="max-width:calc(470px*var(--u))">Untrained: ${start}<span style="font-family:var(--mono);color:#9aa0aa">${esc((g.sample_untrained || '').slice(pr.length, pr.length + 46))}…</span></div></div>`, eo(seg(t, 0.6, 1.6)));
      if (k === 1) noteAt(0, lTiny.o.position, `<div class="b3d-note">${head}${sparkline(c.map((r) => r.val), 'loss', 300, 76, [`step ${c[0].step}: loss ${c[0].val.toFixed(2)}`, `step ${fmt(c[c.length - 1].step)}: ${c[c.length - 1].val.toFixed(2)}`])}<div class="t">Validation loss, ${fmt(c[c.length - 1].step)} steps, ${Math.round(g.train_seconds_cpu2)} s on 2 CPUs.</div></div>`, eo(seg(t, 1.0, 2.0)));
      if (k === 2 && sm['0.5']) noteAt(0, lTiny.o.position, `<div class="b3d-note ember">${head}<div class="t" style="max-width:calc(470px*var(--u))">Trained, temperature 0.5: ${start}${cont(sm['0.5'])}…</div><div class="t" style="margin-top:4px">The right shape of a stock line, with a made-up number.</div></div>`, eo(seg(t, 0.6, 1.6)));
    }
  }
  /* section 9: why, and the fix */
  function sec9(k, t, a) {
    if (a < 1) return;
    F.slabOp = Math.min(F.slabOp, 0.3); F.streams = Math.min(F.streams, 0.3);
    if (k <= 1) {
      tAns.forEach((x, j) => { if (digitSet.has(j)) F.tileGlow.set(x, 1); });
      const dt = tAns[dIdx[1]];
      chipAt(0, dt, `<span class="b3d-chip ember"><b>${esc(D.numStr)}</b> invented · ${D.dig.map((d) => pct(d.p)).join(' · ')}</span>`, eo(seg(t, 0.3, 1.2)), 1.2);
      chipAt(1, tAns[dIdx[2] + 3] || dt, `<span class="b3d-chip green"><b>${fmt(truth)}</b> in Ledgerline, BAT-500 at Manchester main stores</span>`, eo(seg(t, 0.9, 1.8)), -0.1, [0.5, 0]);
    }
    if (k === 1) {
      F.arcs.digit = { op: 1, grow: eo(seg(t, 0.6, 2.6)) };
      F.scan = seg(t, 1.6, 4.4);
      D.inputDigits.forEach((i) => { if (seg(t, 3.2, 3.8) > 0) F.tileGlow.set(tB[i], 0.9); });
      chipAt(2, tB[D.inputDigits[0]], `<span class="b3d-chip dim"><b>the only digits</b> in the input: the date</span>`, eo(seg(t, 3.6, 4.4)), 1.3);
    }
    if (k >= 2) {
      const u = k === 2 ? eo(seg(t, 0.4, 2.4)) : 1;
      F.mix = u; F.factOp = eo(seg(k === 2 ? t : 9, 1.4, 2.6)); F.baseAnsOp = 1 - eo(seg(k === 2 ? t : 9, 0.2, 1.0));
      F.ansFN = k === 2 ? Math.floor(seg(t, 2.6, 4.8) * (D.ansF.length + 0.99)) : D.ansF.length; F.ansFOp = 1;
      tFactTiles.forEach((x) => F.tileGlow.set(x, 0.5));
      F.bot = { n: F.ansFN, facts: true };
      if (k === 2) { F.arcs.fact = { op: 1, grow: eo(seg(t, 4.6, 6.0)) };
        chipAt(0, tFAns[digitSetF.values().next().value + 1], `<span class="b3d-chip green"><b>${esc(D.numStrF)}</b> · ${D.digF.map((d) => pct(d.p)).join(' · ')}</span>`, eo(seg(t, 4.4, 5.2)), 1.2);
        chipAt(1, tFactTiles[Math.floor(tFactTiles.length / 2)], `<span class="b3d-chip green"><b>the added line</b> · ${tFactTiles.length} tokens</span>`, eo(seg(t, 1.8, 2.6)), 1.25);
        const bh = arcSets.fact.arcs[0];
        if (bh) chipAt(2, bh.b, `<span class="b3d-chip green"><b>${pct(bh.w)}</b> block ${D.fa.best_head.layer} · head ${D.fa.best_head.head}</span>`, eo(seg(t, 5.4, 6.2)), 2.3);
      }
    }
    if (k === 3) {
      F.sock = eo(seg(t, 0.3, 1.8)); sockets.forEach((s) => show(s.lb, eo(seg(t, 0.8, 1.8))));
      const rows = D.sampF.map((s) => `<span class="s">seed ${s.seed}</span><span>${esc(s.text).replace(/(\d[\d,]*)/, (m) => `<b class="${m.replace(/,/g, '') == truth ? 'gr' : ''}">${m}</b>`)}</span>`).join('');
      noteAt(0, V(PAGE.x1 + 0.5, 3.6, PAGE.z1 - 0.6), `<div class="b3d-note green"><div class="k">With the fact <b>· five samples at 0.7</b></div><div class="b3d-samp">${rows}</div><div class="t" style="margin-top:6px">Greedy is right; sampling still slips (“5”, and “500” from BAT-500).</div></div>`, eo(seg(t, 1.6, 2.6)), [0, 0.5]);
    }
  }
  const SEC = [null, sec1, sec2, sec3, sec4, sec5, sec6, sec7, sec8, sec9];

  /* transient labels placed per frame */
  let chipN = 0, noteN = 0;
  function chipAt(i, tile, html, a, dy = 1.2, center = [0.5, 1]) {
    if (!tile || a <= 0.01) return; const c = chips[i + chipN]; if (!c) return;
    const p = tilePos(tile, F.mix); p.y = TH + dy; c.at(p, center).set(html).show(a);
  }
  function noteAt(i, pos, html, a = 1, center = [0.5, 1]) {
    if (a <= 0.01) return; const n = notes[i + noteN]; if (!n) return; n.at(pos, center).set(html).show(a);
  }

  /* =========================================================== apply the frame to the meshes */
  const _m4 = new THREE.Matrix4(), _q = new THREE.Quaternion(), _s = new THREE.Vector3(), _p = new THREE.Vector3(), _e = new THREE.Euler();
  function applyFrame(clk, S, K) {
    op('box', F.box); op('seam', F.seam); box.visible = F.box > 0.01; seam.visible = F.seam > 0.01;
    op('shell', 0);
    op('input', F.input); op('plinth', F.plinth); op('map', F.map); op('board', F.board); op('vocab', F.vocab); op('dial', F.dial);
    op('tl', F.tl); op('sock', Math.max(F.sock, 0)); op('sockp', F.sock); op('ex', F.ex);
    tlSeg.forEach((sg, i) => { const u = F.tlSeg[i]; sg.m.scale.x = Math.max(0.001, u); sg.m.position.x = sg.x0 + (sg.x1 - sg.x0) * u / 2; sg.m.visible = u > 0.01 && F.tl > 0.01; });
    tlStop.visible = F.tlStop > 0.01 && F.tl > 0.01; tlStop.scale.y = Math.max(0.01, F.tlStop);
    tlAsk.visible = F.tlAsk > 0.01 && F.tl > 0.01; tlAsk.scale.y = Math.max(0.01, F.tlAsk);
    sockets.forEach((s) => { s.ringMat.emissiveIntensity = 0.1 + F.sock * 0.6; s.core.material.emissiveIntensity = 0.2 + F.sock * 0.6 + Math.sin(clk * 3) * 0.1 * F.sock; });
    // the packet travelling into the box
    packet.visible = F.packet >= 0 && F.packet < 1;
    if (packet.visible) { pipeCurve.getPointAt(eio(F.packet), packet.position); }
    // tiles
    const mix = F.mix;
    let ti = 0;
    for (const tile of tiles) {
      const isBase = !!tile.base;
      let a = 0;
      if (isBase) {
        const j = tile.kind === 'answer' ? tile.t.j : -1;
        if (j < 0) a = F.tileOp * (mix > 0 && !tile.fhome ? 1 - mix : 1);
        else a = (j < F.ansN || (F.ansLive && F.ansLive.j === j)) ? F.ansOp * F.baseAnsOp : 0;
      } else {
        const j = tile.kind === 'answerF' ? tile.t.j : -1;
        a = j < 0 ? F.factOp : (j < F.ansFN ? F.ansFOp : 0);
      }
      let pos = tilePos(tile, mix), lift = 0;
      // drop-in (section 2): in reading order
      if (isBase && tile.kind !== 'answer' && F.dropU < 1) { const i = tile.t.i, u = seg(F.dropU, (i / nP) * 0.78, (i / nP) * 0.78 + 0.22); a *= u; lift = (1 - eo(u)) * 2.2; }
      // a new answer token flies in from the board
      if (F.ansLive && tile.kind === 'answer' && tile.t.j === F.ansLive.j) {
        const u = eio(F.ansLive.u); const from = flyFrom.clone();
        const to = tilePos(tile, mix); pos = from.lerp(to, u); lift = Math.sin(u * Math.PI) * 3.5 + (1 - u) * 0; a = F.ansOp;
      }
      tile.op = a;
      tile.g.visible = a > 0.01;
      tile.g.position.set(pos.x, pos.y + lift, pos.z);
      tile.mat.opacity = a; tile.face.material.opacity = a; tile.mat.depthWrite = a > 0.98;
      const glow = F.tileGlow.get(tile) || 0;
      tile.mat.emissiveIntensity = glow * (tile.kind === 'answer' || tile.kind === 'answerF' || tile.digitAns ? 0.35 : 0.5) + (tile.digitAns ? 0.12 : 0);
      if (glow && !tile.digitAns && tile.kind !== 'answer' && tile.kind !== 'answerF') tile.mat.emissive.setHex(tile.kind === 'fact' ? C.green : C.sky); else tile.mat.emissive.setHex(tile.digitAns ? (tile.kind === 'answer' ? C.ember : C.green) : BODY[tile.kind]);
      // the mask (section 4, last state): tiles after the masked position are frosted
      if (F.mask >= 0 && isBase && tile.kind !== 'answer' && tile.t.i > F.mask) { tile.mat.opacity = a * 0.28; tile.face.material.opacity = a * 0.28; }
      // its column of numbers
      const colA = F.col * a * (tile.kind === 'answer' || tile.kind === 'answerF' ? F.colAns : 1);
      const rise = tile.kind === 'answer' || tile.kind === 'answerF' ? 1 : (tile.t.i !== undefined ? seg(F.colRise, (tile.t.i / nP) * 0.7, (tile.t.i / nP) * 0.7 + 0.3) : 1);
      const hi = F.colHi.get(tile) || 0;
      for (let k = 0; k < NC; k++) {
        const on = colA > 0.02 ? clamp01(rise * NC - k) : 0;
        _p.set(pos.x, pos.y + lift + COL0 + k * CELL + CELL / 2, pos.z);
        const sc = on * (1 + hi * 0.25);
        _s.set(sc, on > 0 ? 1 : 0.001, sc);
        _m4.compose(_p, _q.identity(), _s); colIM.setMatrixAt(ti * NC + k, _m4);
      }
      ti++;
    }
    colIM.instanceMatrix.needsUpdate = true;
    colMat.opacity = F.col; colIM.visible = F.col > 0.01; colMat.depthWrite = F.col > 0.98;
    // streams + the hot stream of the current position
    const sp = strGeo.attributes.position.array; ti = 0;
    for (const tile of tiles) {
      const on = F.streams > 0.01 && tile.op > 0.5 && tile.g.position.y < 0.5;
      const x = tile.g.position.x, z = tile.g.position.z;
      sp.set(on ? [x, COLTOP, z, x, STOP, z] : [0, -5, 0, 0, -5, 0], ti * 6); ti++;
    }
    strGeo.attributes.position.needsUpdate = true; strMat.opacity = 0.14 * F.streams; streams.visible = F.streams > 0.01;
    const hotT = F.hotTile || (F.ansLive && F.ansLive.u > 0.95 ? tAns[F.ansLive.j] : null) || (S >= 7 && F.ansN > 0 && S === 7 ? tAns[Math.max(0, F.ansN - 1)] : tB[qLast]);
    hot.visible = F.hot > 0.01 || (S >= 5 && F.streams > 0.01);
    if (hot.visible) { const x = hotT.g.position.x, z = hotT.g.position.z; const top = F.slabs >= NL ? STOP : slabY(Math.max(0, F.slabs - 1)) + 0.5; hot.position.set(x, (COLTOP + top) / 2, z); hot.scale.set(1, top - COLTOP, 1); hotMat.opacity = 0.55 * Math.max(F.hot, F.streams); }
    // pulses rising
    ti = 0; let np = 0;
    if (F.pulse >= 0 && F.pulse < 1) {
      for (const tile of tiles) {
        if (tile.op < 0.5 || tile.g.position.y > 0.5) continue;
        const u = clamp01(F.pulse * 1.15 - (Math.abs(Math.sin(ti * 91.7)) * 0.15)); ti++;
        if (u <= 0 || u >= 1) continue;
        _p.set(tile.g.position.x, lerp(COLTOP, STOP, u), tile.g.position.z); _s.setScalar(tile === hotT ? 1.6 : 1); _m4.compose(_p, _q.identity(), _s); pulses.setMatrixAt(np++, _m4);
      }
    }
    pulses.count = np; pulses.instanceMatrix.needsUpdate = true; pulses.visible = np > 0;
    // slabs
    slabs.forEach((m, l) => {
      const u = m.material.uniforms; const vis1 = l < F.slabs && F.slabOp > 0.01;
      m.visible = vis1; u.uOp.value = F.slabOp * (F.ex > 0.01 && l === 0 ? 1 - F.exSplit : 1); u.uMode.value = F.slabMode; u.uFill.value = F.slabFill;
      u.uHi.value = (F.slabWave >= 0 ? Math.exp(-Math.pow(l / (NL - 1) - F.slabWave, 2) / 0.004) : 0) + (l === hoverLayer ? 0.9 : 0);
    });
    exAtt.visible = exMlp.visible = F.ex > 0.01;
    exAtt.position.y = S0 - 0.05 - F.exSplit * 0.3; exMlp.position.y = S0 + 0.05 + F.exSplit * 0.6;
    // arcs
    for (const [name, S2] of Object.entries(arcSets)) {
      const st = F.arcs[name]; const o = typeof st === 'number' ? st : st ? st.op : 0; const grow = typeof st === 'object' ? st.grow : 1;
      for (const arc of S2.arcs) {
        arc.m.visible = o > 0.01;
        if (!arc.m.visible) continue;
        buildArc(arc, S2.from === 'facts' ? 1 : F.mix);
        arc.mat.opacity = o * (0.28 + 0.72 * Math.pow(arc.rel, 0.7));
        arc.m.geometry.setDrawRange(0, Math.floor(arc.count * clamp01(grow * 1.15 - (1 - arc.rel) * 0.15) / 6) * 6);
      }
    }
    // bars
    const B = F.bars;
    bars.forEach((b, i) => {
      const it = B && B.list[i];
      const target = it ? Math.max(0.02, it.p * 4.6) : 0.001;
      b.len = target;
      b.m.visible = !!it && F.barsOp > 0.01;
      b.m.scale.x = b.len; b.m.position.x = -1.6 + b.len / 2;
      b.m.position.z = -0.3 + (B && B.hl === i ? (F.pickLift || 0) * 0.5 : 0);
      if (it) {
        const hl = B.hl === i;
        b.m.material.color.setHex(i === 0 || hl ? B.color : 0x9cc4ff); b.m.material.emissive.setHex(i === 0 || hl ? B.color : 0x9cc4ff);
        b.m.material.opacity = F.barsOp;
        if (F.barsOp > 0.5) b.lt.set(`<span class="b3d-chip${hl ? '' : ' dim'}" style="background:rgba(255,255,255,.9)">${tq(it.text, 12)}</span>`).show(F.barsOp);
        b.lp.o.position.set(-1.6 + b.len + 0.14, BY(i), -0.3); if (F.barsOp > 0.5) b.lp.set(`<span class="b3d-chip ${B.color === 0xc4511f && (i === 0 || hl) ? 'ember' : ''}"><b>${pct(it.p)}</b></span>`).show(F.barsOp);
      }
    });
    // vocabulary strip
    for (let i = 0; i < VN; i++) {
      const h = vocH[i] * (F.vocab > 0.01 ? 1 : 0) * (F.beamHead >= 0 ? clamp01(F.beamHead * 1.4 - 0.4) : 1);
      _p.set(-2.7 + (i / (VN - 1)) * 6.2, 7.0 + Math.max(0.001, h) / 2, -0.3); _s.set(1, Math.max(0.001, h), 1); _m4.compose(_p, _q.identity(), _s); vocIM.setMatrixAt(i, _m4);
    }
    vocIM.instanceMatrix.needsUpdate = true; vocIM.visible = F.vocab > 0.01;
    beamMat.uniforms.uOp.value = F.beam; beam.visible = F.beam > 0.01;
    beamMat.uniforms.uOn.value = F.beamHead >= 0 ? 1 : 0; beamMat.uniforms.uHead.value = Math.max(0, F.beamHead) * 1.2;
    // dial
    const ang = dialAng(F.dialT); pointer.rotation.y = ang; knob.rotation.y = ang;
    tDial.set(tagHTML('Temperature', F.dialT.toFixed(2))); dialTicks.forEach((x) => { x.lb.inner.firstChild && x.lb.inner.firstChild.classList.toggle('dim', Math.abs(x.Tm - F.dialT) > 0.01); });
    // map neighbour lines
    nbLines.material.opacity = 0.7 * F.nb * F.map;
    dots.forEach((d) => { const hi = F.nb > 0 && ['battery', 'Manchester'].includes(d.w.word); d.m.scale.setScalar(hi ? 1.7 : 1); });
    // logit lens ladder (right edge of the stack, at the slab heights)
    let nd = 0; const la = leadGeo.attributes.position.array; la.fill(0);
    if (F.lens && F.lensOp > 0.01) {
      const rows = F.lens.rows, focus = F.lens.focus;
      const qt = F.lens.q || tB[qLast];
      const finalId = rows[NL - 1].top[0].id;
      const qx2 = qt.g.position.x, qz2 = qt.g.position.z;
      for (let l = 0; l < NL; l++) {
        const L = lensTags[l];
        const shown = l < F.lens.upto && (focus ? l >= NL - (F.lens.n || 8) : (l % 3 === 2 || l === NL - 1));
        const ly = F.lens.gap ? slabY(NL - 1) + 0.4 - (NL - 1 - l) * F.lens.gap : slabY(l);
        if (l < F.lens.upto) {
          const hit0 = rows[l].top[0].id === finalId, junk0 = !isWordish(rows[l].top[0].text);
          _p.set(qx2, slabY(l), qz2); _s.setScalar(shown ? 1.15 : 0.7); _m4.compose(_p, _q.identity(), _s); lensDots.setMatrixAt(nd, _m4);
          lensDots.setColorAt(nd, _c.setHex(hit0 ? (F.lens.digit ? C.ember : C.skyDeep) : junk0 ? 0xb4bac6 : 0x6aa8ff)); nd++;
          if (shown) la.set([qx2, slabY(l), qz2, PAGE.x0 - 0.2, ly, qz2], l * 6);
        }
        if (!shown) continue;
        const r = rows[l].top[0];
        const junk = !isWordish(r.text);
        const hit = r.id === finalId;
        L.at(V(PAGE.x0 - 0.2, ly, qz2), [1, 0.5]);
        L.set(`<span class="b3d-chip${junk ? ' dim' : ''} ${hit ? (F.lens.digit ? 'ember' : '') : ''}" style="${hit ? 'border-color:rgba(60,144,255,.6)' : ''}"><span style="color:#6b6e76;font-weight:500">block ${l + 1}</span> ${tq(r.text, 11)} <b>${pct(r.p)}</b></span>`);
        L.show(F.lensOp);
      }
    }
    lensDots.count = nd; lensDots.instanceMatrix.needsUpdate = true; if (lensDots.instanceColor) lensDots.instanceColor.needsUpdate = true; lensDots.visible = nd > 0;
    leadGeo.attributes.position.needsUpdate = true; leaders.visible = nd > 0; leaders.material.opacity = 0.55 * F.lensOp;
    applyQKV();
    // the scan (section 9): a sweep line across the input
    scanMesh.visible = F.scan > 0 && F.scan < 1;
    if (scanMesh.visible) { scanMesh.position.set(PCX, TH + 0.05, lerp(PAGE.z0, PAGE.z1, F.scan)); }
  }
  const scanMesh = mesh(new THREE.PlaneGeometry(PW + 0.4, 0.5).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ color: 0xc4511f, transparent: true, opacity: 0.18, depthWrite: false }), V(0, 0, 0), scene, false);

  /* ---------- the rail and the HUD ---------- */
  let railKey = '';
  function renderRail(S) {
    const b = F.bot; const list = b.facts ? D.ansF : ans; const n = Math.min(b.n, list.length);
    const dset = b.facts ? digitSetF : digitSet;
    const txt = list.slice(0, n).filter((s) => !isSpecial(s.text)).map((s, j) => (dset.has(list.indexOf(s)) ? `<span class="n${b.facts ? ' gr' : ''}">${esc(s.text)}</span>` : esc(s.text))).join('');
    const k = `${S}|${n}|${b.facts}|${b.cursor}`;
    if (k !== railKey) {
      railKey = k;
      botEl.classList.toggle('facts', !!b.facts);
      botEl.innerHTML = n ? `${txt}${b.cursor ? '<span class="cur"></span>' : ''}` : `<span class="wait">${S === 1 ? 'the box is about to answer' : '…'}</span>${b.cursor ? '<span class="cur"></span>' : ''}`;
      trRows.forEach((r, i) => { const s = i + 1; r.classList.toggle('done', s < S); r.classList.toggle('cur', s === S); r.querySelector('.v').innerHTML = s <= S ? TRACE_V[s] : ''; });
    }
  }
  let hudKey = '';
  function renderHUD(gi) {
    if (hudKey === gi) return; hudKey = gi;
    const st = stages[gi];
    hud.pill.textContent = `Section ${st.s} of 9`;
    hud.sec.textContent = `${SECTION_TITLES[st.s - 1]} · step ${st.k + 1} of ${SECTION_STATES[st.s - 1]}`;
    hud.h2.innerHTML = st.h; hud.p.innerHTML = st.p;
    progDots.forEach((d) => { const s = +d.dataset.s, k = +d.dataset.k; const g = secStart[s] + k; d.classList.toggle('cur', g === gi); d.classList.toggle('done', g < gi); });
    root.classList.toggle('has-temp', st.s === 6 && mode === 'standalone');
  }

  /* ---------- labels: scale with distance, keep inside the free stage ---------- */
  const _w = new THREE.Vector3(), _n = new THREE.Vector3();
  const FLOOR = { tag: 0.84, note: 0.94, chip: 0.9, bar: 0.92, lens: 0.88 };
  function scaleLabels() {
    for (const L of labelList) {
      const vis1 = L.op > 0.01; L.o.visible = vis1;
      if (!vis1) continue;
      L.o.getWorldPosition(_w);
      const d = _w.distanceTo(camera.position);
      const s = Math.max(FLOOR[L.kind] || 0.9, Math.min(1.08, 26 / d));
      if (Math.abs((L._s || 0) - s) > 0.01) { L._s = s; L.inner.style.scale = s.toFixed(3); }
      _n.copy(_w).project(camera);
      L.inner.style.opacity = (_n.z < 1 ? L.op * settle : 0).toFixed(3);
    }
  }
  function fitLabels() {
    const er = root.getBoundingClientRect(); if (!er.width) return;
    const z = er.width / W, m = 24 * z;
    const box2 = { l: er.left + m, r: er.right - m, t: er.top + m, b: er.bottom - m };
    const rr0 = railEl.getBoundingClientRect(), hr = hudEl.getBoundingClientRect(), fr = footEl.getBoundingClientRect();
    const free = { l: Math.max(box2.l, rr0.right + 10 * z), r: box2.r, t: Math.max(box2.t, hr.bottom + 8 * z), b: Math.min(box2.b, fr.top - 6 * z) };
    for (const L of labelList) {
      const outer = L.o.element;
      if (!L.o.visible || outer.style.display === 'none') continue;
      if (parseFloat(L.inner.style.opacity || '1') < 0.03) { outer.style.display = 'none'; continue; }
      const tx = L._tx || 0, ty = L._ty || 0;
      const ri = L.inner.getBoundingClientRect(), ro = outer.getBoundingClientRect();
      if (!ri.width) continue;
      const l = Math.min(ri.left, ro.left) - tx * z, rr = Math.max(ri.right, ro.right) - tx * z;
      const t = Math.min(ri.top, ro.top) - ty * z, b = Math.max(ri.bottom, ro.bottom) - ty * z;
      if (L.kind === 'note' || L.kind === 'lens' || L.kind === 'tag' || L.kind === 'chip') {
        const B = free;
        if (rr - l > B.r - B.l || b - t > B.b - B.t) { outer.style.display = 'none'; continue; }
        let dx = 0, dy = 0;
        if (l < B.l) dx = B.l - l; else if (rr > B.r) dx = B.r - rr;
        if (t < B.t) dy = B.t - t; else if (b > B.b) dy = B.b - b;
        // tags and chips that would have to move far are hidden instead (they belong to a place)
        if (L.kind !== 'note' && L.kind !== 'lens' && (Math.abs(dx) > 70 * z || Math.abs(dy) > 50 * z)) { outer.style.display = 'none'; continue; }
        const nx = dx / z, ny = dy / z;
        if (Math.abs(nx - tx) > 0.5 || Math.abs(ny - ty) > 0.5) { L._tx = nx; L._ty = ny; outer.style.translate = `${nx.toFixed(1)}px ${ny.toFixed(1)}px`; }
        if (L.kind === 'note') outer.style.zIndex = String(1000000 + (+outer.style.zIndex || 0));
      } else if (l < free.l || rr > free.r || t < free.t || b > free.b) {
        outer.style.display = 'none';
      }
    }
  }

  /* ---------- interaction: orbit and zoom, click a token, hover a block ---------- */
  const controls = new OrbitControls(camera, renderer.domElement);
  Object.assign(controls, { enableDamping: false, rotateSpeed: 0.55, zoomSpeed: 0.9, panSpeed: 0.9, minDistance: 5, maxDistance: 150, screenSpacePanning: true, maxPolarAngle: Math.PI * 0.49 });
  let userCam = false, sel = null, hoverLayer = -1, lastHover = 0;
  const hintEl = $('.b3d-hint'), resetEl = $('.b-reset'), infoEl = $('.b3d-info'), tipEl = $('.b3d-tip');
  controls.addEventListener('start', () => { if (!userCam) { userCam = true; resetEl.classList.add('on'); } hintEl.classList.add('off'); dirty = true; });
  controls.addEventListener('change', () => { dirty = true; });
  function giveBackCamera() { // the authored shot takes over again, gliding from wherever the user left the camera
    if (!userCam) return; userCam = false; resetEl.classList.remove('on');
    cam.pos.copy(camera.position); cam.tgt.copy(controls.target); dirty = true;
  }
  resetEl.addEventListener('click', (e) => { e.stopPropagation(); giveBackCamera(); select(null); });
  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
  function pick(e, list) {
    const r = renderer.domElement.getBoundingClientRect(); if (!r.width) return null;
    ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ndc, camera); return ray.intersectObjects(list, false)[0] || null;
  }
  const tileBodies = () => tiles.filter((x) => x.g.visible && x.op > 0.3).map((x) => x.body);
  const slabBodies = () => slabs.filter((m) => m.visible && m.material.uniforms.uOp.value > 0.2);
  const rowsAvg = (T.attention.rows || {}).avg, avgLastTo = (i) => T.attention.last.avg.reduce((s2, r) => s2 + (r[i] || 0), 0) / NL;
  const ROLE = { system: 'system prompt', user: "Emma's question", template: 'chat template marker', fact: 'the added Ledgerline line', answer: 'the reply', answerF: 'the reply, with the fact' };
  // arcs from the selected token to where it looks
  const selArcs = Array.from({ length: 6 }, () => { const mat = new THREE.MeshBasicMaterial({ color: 0x0b57d0, transparent: true, opacity: 0.8, depthWrite: false }); const m = new THREE.Mesh(new THREE.BufferGeometry(), mat); m.visible = false; m.renderOrder = 3; scene.add(m); return m; });
  function select(tile) {
    sel = tile; dirty = true; selArcs.forEach((m) => (m.visible = false));
    if (!tile) { infoEl.classList.remove('on'); return; }
    const t0 = tile.t, isAns = tile.kind === 'answer' || tile.kind === 'answerF';
    const v = tile.v || idVals[t0.id];
    const vec = v ? `<div class="sec">Its vector · first 8 of ${M.d_model}</div><div class="b3d-vals">${v.slice(0, 8).map((x) => `<span class="${x < 0 ? 'n' : ''}">${x >= 0 ? '+' : '−'}${Math.abs(x).toFixed(4)}</span>`).join('')}</div>` : '';
    let body = '';
    if (isAns) {
      const st = (tile.kind === 'answer' ? D.ans : D.ansF)[t0.j];
      body = `<div class="sec">Picked at ${pct(st.p)} · the other guesses</div><div class="lk">${st.alts.slice(0, 5).map((x) => `<span>${tq(x.text)}</span><span class="p">${pct(x.p)}</span>`).join('')}</div>`;
    } else if (tile.base && rowsAvg && rowsAvg[t0.i]) {
      const row = rowsAvg[t0.i].filter(([j]) => j !== t0.i).slice(0, 4);
      body = `<div class="sec">Where it looks · all heads, all blocks</div><div class="lk">${row.map(([j, w]) => `<span>${tq(tB[j].t.text)} <span style="color:#8a8f99;font-size:.85em">#${j}</span></span><span class="p">${pct(w)}</span>`).join('')}</div>`
        + `<div class="sec">The last token's look at it</div><div class="lk"><span>all heads, all blocks</span><span class="p">${pct(avgLastTo(t0.i))}</span>${QK && t0.i <= QK.query_pos ? `<span>block ${QK.layer}, head ${QK.head}</span><span class="p">${pct(QK.weights[t0.i])}</span>` : ''}</div>`;
      row.slice(0, 4).forEach(([j, w], r) => {
        const a2 = tilePos(tile, 0), b2 = tilePos(tB[j], 0); a2.y = b2.y = TH + 0.06;
        const d = a2.distanceTo(b2), mid = a2.clone().add(b2).multiplyScalar(0.5); mid.y += 0.7 + 0.42 * Math.pow(d, 0.85);
        const m = selArcs[r]; m.geometry.dispose(); m.geometry = new THREE.TubeGeometry(new THREE.QuadraticBezierCurve3(a2, mid, b2), 48, 0.03 + 0.12 * Math.sqrt(w / (row[0][1] || 1)), 8, false); m.visible = true;
      });
    }
    const where = isAns ? `reply token ${t0.j + 1}` : `position ${t0.i}`;
    infoEl.innerHTML = `<div class="hd">${tq(t0.text, 18)}<small>id ${t0.id} · ${where} · ${ROLE[tile.kind] || ''}</small><button aria-label="Close">×</button></div>${vec}${body}`;
    infoEl.querySelector('button').addEventListener('click', (e) => { e.stopPropagation(); select(null); });
    infoEl.classList.add('on');
  }
  function applySelection() {
    if (sel) { F.tileGlow.set(sel, 1); F.colHi.set(sel, 1); }
    selArcs.forEach((m) => { if (m.visible && F.mix > 0.01) m.visible = false; });
  }
  let down = null, swallow = false;
  const cv = renderer.domElement;
  cv.addEventListener('pointerdown', (e) => { down = { x: e.clientX, y: e.clientY }; tipEl.classList.remove('on'); });
  cv.addEventListener('pointerup', (e) => {
    if (!down) return; const moved = Math.hypot(e.clientX - down.x, e.clientY - down.y) > 5; down = null;
    if (moved) { swallow = true; return; }
    const hit = pick(e, tileBodies());
    if (hit) { select(hit.object.userData.tile); hintEl.classList.add('off'); swallow = true; }
    else if (sel) { select(null); swallow = true; }
    else swallow = false; // a plain click on empty space still steps the deck
  });
  // a drag, a token click or closing the card never reaches the deck's click-to-step; nor do touch drags reach its swipe
  root.addEventListener('click', (e) => { if (swallow || e.target.closest('.b3d-info')) { e.stopPropagation(); swallow = false; } });
  ['touchstart', 'touchend'].forEach((n) => cv.addEventListener(n, (e) => e.stopPropagation(), { passive: true }));
  cv.addEventListener('pointerleave', () => { tipEl.classList.remove('on'); if (hoverLayer >= 0) { hoverLayer = -1; dirty = true; } });
  cv.addEventListener('pointermove', (e) => {
    if (e.buttons) return;
    const now = performance.now(); if (now - lastHover < 60) return; lastHover = now;
    const ht = pick(e, tileBodies()); cv.classList.toggle('pt', !!ht);
    const hs = ht ? null : pick(e, slabBodies());
    const l = hs ? hs.object.userData.layer : -1;
    if (l !== hoverLayer) { hoverLayer = l; dirty = true; }
    if (l < 0) { tipEl.classList.remove('on'); return; }
    const dig = section === 7 && api.step >= 2;
    const rows = dig ? LDIG[0].lens : LENS;
    const r = rows[l];
    tipEl.innerHTML = `<div class="k">Block ${l + 1} · the logit lens</div><div style="color:#6b6e76;font-size:.92em;margin-bottom:4px">What ${dig ? 'the first digit' : 'the last position'} would say if the model stopped here</div><div class="lk">${r.top.slice(0, 5).map((x) => `<span class="${isWordish(x.text) ? '' : 'j'}">${tq(x.text, 14)}</span><span class="p">${pct(x.p)}</span>`).join('')}</div>`;
    const rr = root.getBoundingClientRect(), zz = rr.width / W;
    tipEl.classList.add('on');
    const tw = tipEl.offsetWidth * zz, th = tipEl.offsetHeight * zz;
    let x = e.clientX - rr.left + 18 * zz, y = e.clientY - rr.top + 14 * zz;
    if (x + tw > rr.width - 24 * zz) x = e.clientX - rr.left - tw - 18 * zz;
    if (y + th > rr.height - 24 * zz) y = rr.height - 24 * zz - th;
    tipEl.style.left = (x / zz) + 'px'; tipEl.style.top = (Math.max(24 * zz, y) / zz) + 'px';
  });

  function toScreen(p) { const r = renderer.domElement.getBoundingClientRect(); p.project(camera); return [r.left + (p.x + 1) / 2 * r.width, r.top + (1 - p.y) / 2 * r.height]; }
  /* ---------- layout ---------- */
  let W = 0, Hh = 0;
  function resize() {
    W = root.clientWidth; Hh = root.clientHeight; if (!W || !Hh) return;
    const u = mode === 'deck' ? W / 1660 : W / 1920; root.style.setProperty('--u', u.toFixed(4));
    const rect = root.getBoundingClientRect(); const zoom = rect.width / W || 1;
    renderer.setPixelRatio(Math.min(2, (window.devicePixelRatio || 1) * zoom));
    renderer.setSize(W, Hh, false); renderer.domElement.style.width = '100%'; renderer.domElement.style.height = '100%';
    labels.setSize(W, Hh);
    camera.aspect = W / Hh;
    const rail = 420 * u, top = (mode === 'deck' ? 300 : 210) * u, foot = 70 * u;
    camera.setViewOffset(W, Hh, -rail / 2, -(top - foot) / 2, W, Hh);
    camera.updateProjectionMatrix();
  }
  const ro = new ResizeObserver(() => { resize(); dirty = true; draw(); }); ro.observe(root);

  /* ---------- time ---------- */
  let gi = 0, t = 0, playing = false, auto = false, hold = 0, last = performance.now(), clk = 0, raf = 0, dead = false, dirty = true, settle = 1;
  let section = Math.max(1, Math.min(9, opts.section || 1));
  const secOf = (g) => stages[g].s;
  function draw() {
    if (!W) resize();
    reset(); chipN = 0; noteN = 0;
    const st = stages[gi];
    for (let s = 1; s <= st.s; s++) {
      if (s < st.s) SEC[s](SECTION_STATES[s - 1] - 1, 99, DIM);
      else { for (let k = 0; k < st.k; k++) { /* earlier steps of this section are summarised by the current one */ } SEC[s](st.k, t, 1); }
    }
    // the bars always show something once section 1 is done
    if (!F.bars && st.s > 1) setBars(fin['1.0'], DIM, { n: 5 });
    if (st.s > 1 && F.board < DIM) F.board = DIM;
    if (st.s > 1) F.shell = 1;
    applySelection();
    applyFrame(clk, st.s, st.k);
    // camera
    const sh = SHOT[st.s][st.k];
    cam.want[0].copy(sh[0]); cam.want[1].copy(sh[1]);
    const zm = ZOOM * (mode === 'deck' ? (DECKZ[st.s] || 1) : 1);
    if (mode === 'deck' && DECKY[st.s]) { cam.want[0].y += DECKY[st.s]; cam.want[1].y += DECKY[st.s]; }
    if (zm !== 1) cam.want[0].sub(cam.want[1]).multiplyScalar(zm).add(cam.want[1]);
    if (cam.snap || still) { cam.pos.copy(cam.want[0]); cam.tgt.copy(cam.want[1]); cam.snap = false; }
    if (!userCam) {
      camera.position.copy(cam.pos);
      if (!still && mode === 'standalone') { camera.position.x += Math.sin(clk * 0.21) * 0.3; camera.position.y += Math.sin(clk * 0.17) * 0.15; }
      camera.lookAt(cam.tgt); controls.target.copy(cam.tgt);
    }
    // labels wait for the camera: hidden while it glides, back in as it arrives (the user's own orbit never hides them)
    const glide = userCam ? 0 : cam.pos.distanceTo(cam.want[0]) + cam.tgt.distanceTo(cam.want[1]);
    settle = clamp01((1.0 - glide) / 0.8);
    renderHUD(gi); renderRail(st.s);
    renderer.render(scene, camera);
    scaleLabels();
    labels.render(scene, camera);
    fitLabels();
  }
  function loop(now) {
    if (dead) return;
    const real = Math.max(0, (now - last) / 1000), dt = Math.min(0.05, real); last = now;
    clk += dt;
    // the camera glides to the wanted shot (in real time, so a slow machine still arrives in about 2 s)
    const kf = 1 - Math.exp(-Math.min(0.25, real) * 2.6);
    const moving = !userCam && cam.pos.distanceTo(cam.want[0]) + cam.tgt.distanceTo(cam.want[1]) > 0.003;
    cam.pos.lerp(cam.want[0], kf); cam.tgt.lerp(cam.want[1], kf);
    if (!moving) { cam.pos.copy(cam.want[0]); cam.tgt.copy(cam.want[1]); }
    if (playing) {
      t += Math.min(0.5, real);
      if (t >= stages[gi].dur) {
        t = stages[gi].dur;
        if (auto) { hold += dt; if (hold > 1.8) { hold = 0; if (gi < stages.length - 1 && (mode === 'standalone' || secOf(gi + 1) === section)) { gi++; section = secOf(gi); t = 0; } else auto = false; } }
        else playing = false;
      }
    }
    // deck mode draws only while something moves, and never while its slide is hidden
    const shown = root.offsetParent !== null || getComputedStyle(root).position === 'fixed';
    if (shown && (mode === 'standalone' || playing || auto || moving || dirty)) { dirty = moving; draw(); }
    raf = requestAnimationFrame(loop);
  }
  const clampK = (k) => Math.max(0, Math.min(SECTION_STATES[section - 1] - 1, k));
  const api = {
    get section() { return section; }, get step() { return gi - secStart[section]; },
    get count() { return SECTION_STATES[section - 1]; },
    sections: SECTION_TITLES.map((title, i) => ({ n: i + 1, title, states: SECTION_STATES[i], steps: SECTION_STATES[i] - 1 })),
    stages: stages.map((s) => ({ section: s.s, step: s.k, title: s.h.replace(/<[^>]+>/g, ''), dur: s.dur })),
    go(k, instant = false) {
      const ng = secStart[section] + clampK(k);
      if (ng < gi && secOf(gi) === section) instant = true; // stepping back shows the end state
      if (ng !== gi) { userT = null; select(null); }
      giveBackCamera();
      gi = ng; t = instant ? stages[gi].dur : 0; playing = !instant; hold = 0; dirty = true; draw();
    },
    setSection(n, k = 0, instant = true) { section = Math.max(1, Math.min(9, n)); api.go(k, instant); },
    next() { const k = api.step; if (k < api.count - 1) api.go(k + 1); else if (mode === 'standalone' && section < 9) { section++; api.go(0); } },
    prev() { const k = api.step; if (k > 0) api.go(k - 1, true); else if (mode === 'standalone' && section > 1) { section--; api.go(SECTION_STATES[section - 1] - 1, true); } },
    replay() { api.go(api.step, false); },
    autoplay(on = !auto) { auto = on; const b = root.querySelector('.b-auto'); b.classList.toggle('on', auto); b.innerHTML = `${auto ? ICON.pause : ICON.play}<span>${auto ? 'Pause' : 'Autoplay'}</span>`; if (auto) { playing = true; if (t >= stages[gi].dur) api.next(); } else playing = false; },
    seek(n, k, sec) { userCam = false; select(null); section = Math.max(1, Math.min(9, n)); gi = secStart[section] + clampK(k); t = sec === 'end' || sec === undefined ? stages[gi].dur : Math.min(+sec, stages[gi].dur); playing = false; cam.snap = true; draw(); },
    setTemperature(Tm) { userT = Tm === null ? null : Math.max(0, Math.min(2, +Tm)); if (tempIn) { tempIn.value = userT ?? 1; tempOut.textContent = (userT ?? 1).toFixed(2); } draw(); },
    attach(el) { if (root.parentNode !== el) { if (getComputedStyle(el).position === 'static') el.style.position = 'relative'; el.appendChild(root); } resize(); cam.snap = false; },
    render() { draw(); }, resize() { resize(); draw(); },
    _tilePoint(i) { const p = tB[i].g.position.clone(); p.y += TH; return toScreen(p); },          // QA: where a tile is on screen
    _slabPoint(l) { return toScreen(V(PAGE.x1 - 2.5, slabY(l), PCZ + PD * 0.3)); },
    destroy() { dead = true; cancelAnimationFrame(raf); ro.disconnect(); renderer.dispose(); root.remove(); },
  };
  root.querySelector('.b-prev').addEventListener('click', (e) => { e.stopPropagation(); api.prev(); });
  root.querySelector('.b-next').addEventListener('click', (e) => { e.stopPropagation(); api.next(); });
  root.querySelector('.b-replay').addEventListener('click', (e) => { e.stopPropagation(); api.replay(); });
  root.querySelector('.b-auto').addEventListener('click', (e) => { e.stopPropagation(); api.autoplay(); });
  progDots.forEach((d) => d.addEventListener('click', (e) => { e.stopPropagation(); api.setSection(+d.dataset.s, +d.dataset.k, false); }));
  tempIn.addEventListener('input', (e) => { e.stopPropagation(); userT = +tempIn.value; tempOut.textContent = userT.toFixed(2); dirty = true; });
  tempIn.addEventListener('keydown', (e) => e.stopPropagation());
  // fonts arrive late: redraw the tile faces once they are in
  if (document.fonts && document.fonts.load) {
    Promise.all([document.fonts.load('600 50px "Google Sans Flex"'), document.fonts.load('500 26px "Google Sans Code"')]).then(() => {
      for (const tile of tiles) { const { tex } = tileTexture(tile.t, tile.w); tile.face.material.map.dispose(); tile.face.material.map = tex; tile.face.material.needsUpdate = true; }
      draw();
    }).catch(() => {});
  }
  resize();
  gi = secStart[section] + clampK(opts.step || 0);
  if (opts.t !== undefined || opts.step !== undefined) api.seek(section, opts.step || 0, opts.t); else { t = stages[gi].dur; draw(); }
  if (!still) raf = requestAnimationFrame(loop);
  if (opts.autoplay) api.autoplay(true);
  return api;
}

export async function loadTrace(url = new URL('trace.json', HERE)) {
  const r = await fetch(url); if (!r.ok) throw new Error('trace.json: ' + r.status); return r.json();
}
