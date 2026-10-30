# Lecture 1 film: How Ask Northbridge works, underneath

**File:** `l1_how_it_works.mp4` (H.264 1080p30, faststart, AAC, 164.8 s = 2:44.8, 23.4 MB), with a `l1_how_it_works.webm` copy (VP9 + Opus, 23.9 MB) and `poster.jpg` (the closing wide shot).

**Where it plays:** at the end of the "How it works, underneath" section, after Rajat has taught the harness, the model, the tools, MCP and Ledgerline, as the cinematic recap of one real request. The interactive three.js version in `../flow3d/` stays as it is, and it is the fallback.

**Embed:** use `<video controls preload="metadata" poster="films/poster.jpg">` with the mp4 and webm sources. Do not autoplay it, and offer a Present (full screen) option. Subtitles are burnt in.

## Script and shots

Voice: Daniel (ElevenLabs `onwK4e9ZLuTAKqWW03F9`, `eleven_multilingual_v2`). It is played 1.08x faster (ffmpeg atempo) to fit 2:45. The subtitle text is below; the spelled-out text sent to the voice is in `build/script.json`.

| # | Time | Narration (subtitles) | Picture |
|---|---|---|---|
| 1 | 0:00.0 to 0:19.4 | Monday morning, Manchester. Emma Clarke buys parts for Northbridge Cycles. She types one question: how many city e-bike battery packs do we have? Seconds later, she has her answer. So what happened in between? | Emma's desk: the display with the Ask Northbridge chat mapped onto the screen (typed question, thinking dots, the real reply). Title typed over the opening. |
| 2 | 0:19.4 to 0:37.5 | Her words don't go to the model first. They go to the harness, the code around the model. Think of an assembly bench. Our rules. Her message. A description of every tool, all fifteen. Stacked together: one request, 2,139 tokens. | The harness bench: a wide shot; then a macro push-in on the jig as the context sheets fly in from the magazine (rules, her message, 15 tool sheets); then the clamp presses them into one request. 2D: the context ledger (196 + 11 + 1,932) and the 2,139 punch. |
| 3 | 0:37.5 to 0:51.6 | The model reads every one of those tokens. And here's the twist: it doesn't answer. It can't see the stock. So it picks one tool of fifteen, find_item, and writes its arguments as JSON. | The model, opened up: covers slide away, 40 token tiles ride in, and three light waves climb the 24 layers. Cut to the tool rack: find_item slides out and lights. Cut to the output port as the call leaves. 2D: the list of 15 tools, 1 of 15, and the tool call JSON. |
| 4 | 0:51.6 to 1:03.6 | Can we trust what it wrote? Not yet. The guard checks it against the tool's schema: the right fields, the right types. Then MCP, the standard plug, carries it to the toolbox. | A macro on the guard ring, which turns green as the schema check passes (2D check marks). A macro on the MCP plug seating. Then the rack. 2D: the JSON-RPC tools/call frame. |
| 5 | 1:03.6 to 1:17.8 | Behind the toolbox sits Ledgerline ERP 7.2, a system from 1998. The tool calls it with Emma's own permissions. We never open this cabinet: data in, data out. | The 1998 Ledgerline cabinet. A macro on the old units blinking behind the smoked glass while the services run. A green packet comes back. 2D: as ECLARKE, 11 service calls in, items out. |
| 6 | 1:17.8 to 1:33.0 | The result goes back into the context, and the loop goes round again. Search the manuals. Check the stock. Each lap, the request grows. Five model calls later: 6,600 packs, eleven days of cover. | A wide shot over the bench, model and rack: results return, sheets add to the stack, cartridges slide out for search_policy and check_stock. 2D: five laps with real token counts, and the 6,600 punch. |
| 7 | 1:33.0 to 1:51.5 | Then Emma asks for more: order 2,000 battery packs from Voltway Cells. The model tries a direct order, and the tool says no. Direct orders stop at £50,000. This one is £285,600. Raise a purchase request first. | The rack: create_purchase_order slides out. A macro on it: the light turns ember, an ember wash falls on the rack, it is pushed back. 2D: Emma's order, the refusal JSON, the REFUSED stamp, the £50,000 punch. |
| 8 | 1:51.5 to 2:05.9 | So the model builds the request, as a preview. Nothing is saved. £273,600: above Emma's limit, so Daniel Okafor must approve. Shall I go ahead? Emma says yes. | Emma's screen again: the real preview reply, then 'Yes, go ahead.' typed and sent. 2D: the £273,600 punch and the approver chip. |
| 9 | 2:05.9 to 2:16.5 | Only now is anything written. Ledgerline saves the request, and PR/2026/04417 lands in Daniel's approval inbox. | Daniel's desk (presence only). A macro on the steel letter tray: PR/2026/04417 drops onto PO/2026/01179 with a soft glow and a ripple. 2D: pr_save and pr_submit, and the PR/2026/04417 punch. |
| 10 | 2:16.5 to 2:26.6 | One last step: the tool reads the record back. Waiting for approval. What Emma sees is what the ERP really holds. | The dot-matrix printer prints the green-bar receipt. 2D: the pr_get read-back and Emma's final reply. |
| 11 | 2:26.6 to 2:44.8 | One sentence in. A receipt out. The harness builds the context. The model picks a tool. The guard checks it. MCP carries it. And Ledgerline does the work. | A slow pull-back from the model to the whole machine. Each station is labelled on its word. Then the end card with credits. |

The end card starts at 2:39.8: "One sentence in. A receipt out.", with credits.

## Provenance: every number comes from the recorded run

All numbers and strings on screen come from `../flow3d/trace.json`. That trace is one real run of `ledgerline.course.l1.AskNorthbridge`, recorded live at 2026-10-30 04:15 UTC with gemini-3.8-flash, as ECLARKE:

- **Tokens:**
  - 2,139 tokens in the first request: system 196, history 11, 15 tool schemas 1,932 (`context_split`).
  - The context grows over the first turn's five model calls: 2,139, 2,507, 2,894, 3,218, 3,325.
  - The first call returns 21 tokens in 2.68 s.
- **The first tool call:**
  - The model picks `find_item({"query": "city e-bike battery pack"})`, 1 of the 15 tools.
  - The guard checks it: query is a string, query is required, writes is false.
  - MCP carries it as a JSON-RPC `tools/call` frame.
  - Ledgerline runs 11 service calls (itm_search x5, itm_get x6).
- **The stock:** check_stock BAT-500 finds 6,600 free (Manchester 5,400 + Leeds 1,200), 11 days of cover. BAT-500-R has no stock record.
- **The second request:** "Order 2,000 battery packs from Voltway Cells for the spring launch run, cost centre PRD-07, needed by 9 November."
- **The refusal:** "A direct order is limited to £50,000; this one is £285,600." The next step: raise a purchase request first.
- **The preview:** £273,600, above Emma's £250,000 limit, with DOKAFOR (Daniel Okafor) as approver. Nothing is saved.
- **The write:** after "Yes, go ahead.", pr_save and pr_submit create PR/2026/04417. It goes into DOKAFOR's inbox next to PO/2026/01179.
- **The receipt:** pr_get reads it back: WAITING FOR APPROVAL, status PA. Emma's final reply is quoted from the trace.

No text is readable in the 3D. Every word on screen is a 2D overlay drawn from these values (`build/overlays.py`).

## How it was made (all heavy work on Modal, workspace rajatworkspace)

| Step | Files | Where |
|---|---|---|
| Script and voice | `build/script.json`, `build/tts.py`, `build/audio/n*.mp3` + `.align.json` (character timings) | ElevenLabs API |
| Master timeline | `build/timeline.py` → `build/timeline.json`: block starts, word frames (after atempo 1.08), 11 shot plates with 10-frame handles | local, JSON only |
| 3D world | `build/blender/lib.py` (graphite studio, materials, primitives), `props.py` (bench, 24-layer model, guard ring, 15-cartridge rack, MCP plug and cable, 1998 cabinet, dot-matrix printer, two desks, glass conduits), `shots.py` (per block: animation keyed to words, cameras switched by markers, 2D anchor export) | Blender 4.2.3 Cycles on Modal L40S (`build/m_blender.py`) |
| Overlays and composite | `build/overlays.py` (timed elements), `build/comp.py` (PIL renderer: pins, punches, JSON cards, chat UI warped onto the screen, stamp, ripple, subtitles, end card) | Modal CPU, 30 chunks (`build/m_comp.py::video`) |
| Mix | narration + music + 18 designed SFX (`build/audio/sfx_spec.json`, `build/gen_sfx.py`), music −15 dB under speech and −7 dB in gaps, two-pass loudnorm to −14 LUFS, TP −2 | Modal (`m_comp.py::audio`) |
| Delivery | `m_comp.py::final` (mux, faststart, webm), `::pull` (downloads the mp4, webm and poster here) | Modal |

**To rebuild:**

1. `cd build`, then run `python3 tts.py && python3 timeline.py`.
2. Render: `modal run m_blender.py::full --shots chat,harness,model,guard,erp,loop,refuse,preview,write,receipt,close --samples 96`.
3. Composite and mix: `modal run m_comp.py::video --tag vN`, then `m_comp.py::audio --tag vN`.
4. Deliver: `m_comp.py::final --tag vN`, then `m_comp.py::pull --tag vN`.

To check one frame on the laptop, use `comp_still.py <shot> <frame>`; it runs PIL on a single still. Frame grabs used for QA are in `build/out/grabs_v2/`, and `build/out/` is gitignored.

## Credits

- Agentic Systems Engineering, Lecture 1. Dr. Rajat Dandekar, Vizuara.
- Narration: Daniel (ElevenLabs).
- Music: *Observatory* by Out To The World (Epidemic Sound), licensed. The file is `music/observatory_out_to_the_world.mp3`, which is gitignored and never committed. It is credited on the end card.
- SFX: designed with ElevenLabs sound generation.
- Type: Google Sans Flex and Google Sans Code (OFL; see `build/fonts/OFL.txt`).
- Rendered in Blender Cycles.
- The reference for the look was Vizuara's *Inside Rubin* film, with the house style in `../../../FILM_STYLE.md`.

## Known rough edges (v2, 30 Oct 2026)

- **Model shot:** the side covers of the model are plain brushed panels, and they sweep through the frame in the first second.
- **Preview and Ledgerline:** the chat text in the wide preview shot is small, and it is carried by the subtitles and the punch. The Ledgerline macro is dark, with only the unit LEDs reading.
- **Mix:** checked by meters only (−14 LUFS, speech windows about −16.5 dB mean, music-only title −17.8 dB); nobody has listened to it on speakers yet.
- **Studio:** it is graphite (Rubin-like) rather than the light studio that FILM_STYLE.md describes. Rajat approved this from the style frames.
