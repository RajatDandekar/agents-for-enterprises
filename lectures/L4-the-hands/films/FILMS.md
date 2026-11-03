# Lecture 4 films (The Hands)

Three narrated Blender Cycles films for Lecture 4, "The Hands: tools, MCP, two harnesses". They use the same running example the slides teach (Emma Clarke, Northbridge Cycles, Ledgerline). Each plays at the **end** of its section, as the recap after the theory. Every number and every line of JSON or code on screen is read at build time from the recorded runs in `../experiments/logs/` (directly in `build/specs/*.py`, or through `build/data/l4_data.json`, which `build/make_data.py` writes from those logs). Nothing on screen is illustrative except the decorative circuit-board pattern on the tool's floor and the rack's look.

Embed with `<video controls preload="metadata" poster="films/<name>.jpg">` and two `<source>` lines (`.webm` first, then `.mp4`). Never autoplay. Files: `films/<name>.mp4` (H.264, faststart), `films/<name>.webm` (VP9 + Opus) and `films/<name>.jpg` (poster). All are 1920x1080 at 30 fps, mixed to -16 LUFS integrated, true peak about -1.5 dBFS.

| Base name | Plays at the end of section | Duration | mp4 | webm |
|---|---|---|---|---|
| `tool` | 3: open a tool ("Inside a tool") | 2:32 (151.8 s) | 24.2 MB | 22.9 MB |
| `context` | 8: what the LLM sees ("What the model sees") | 2:42 (161.8 s) | 24.2 MB | 23.8 MB |
| `orchestra` | 9: orchestration ("Many tools, one request") | 2:44 (163.6 s) | 24.2 MB | 24.8 MB |

## Look and sound (the same series as L2)

- **World:** the L2 kit, copied unchanged to `build/kit/l2kit.py` (the "midnight slate" studio: blue-grey sweep graded to black, big soft key, cool rim, warm fill, lights hidden from reflections; dark graphite plinths with aluminium trim; ceramic tiles with smoked-glass faces). The model is the L2 sealed machine (24-floor stack behind a frosted window), so the model looks the same as in Lecture 2. New props are in `build/kit/props_l4.py`:
  - a tool as a machined aluminium instrument: an intake gate (tool.json) with a scan sheet and a shutter; a lid that lifts off for the exploded view; inside, on a circuit-board floor, the core, whose 26 light bars are the 26 real lines of `check_stock/tool.py` (each bar as long as its line); four internal light tubes to four service ports; an envelope tray; an output slot;
  - 1998 Ledgerline service cabinets (warm-grey enamel, charcoal front, tape reels, amber status lamps, a fault beacon);
  - request capsules, legacy envelopes, result slabs (green; ember for an error), glass conduits;
  - the context window as a glass vitrine with 1 mm per token; one frosted slab per part, its edge in the part's colour (system slate, tool definitions violet, Emma sky, tool call light sky, tool result green, reply pale sky);
  - the black wall with one slot, and the dark booth behind it (tool, cabinets, database, Emma's session card, a padlock for her password);
  - the 16-tool rack (each small unit shows its own tool.py's real line lengths through its window), the trace strips of L2-style tiles, our harness's open rig with seven control modules, and Claude's harness as a sealed housing.
- **Text:** all readable text is a 2D overlay in Google Sans Flex / Google Sans Code (`build/overlay.py`, copied from L2). It adds a `code` card: real JSON and code with syntax colours, line-by-line reveal and timed line highlights. Film 3's trace panels list every call with its real arguments and a summary of its real result.
- **Sound:** narration by ElevenLabs Daniel (`onwK4e9ZLuTAKqWW03F9`, eleven_multilingual_v2, speed 1.08; the key is read from `/Users/raj/Claude_Brain/cobol-mainframes/.env` and never printed). The music is L1's track, "Observatory" by Out To The World (Epidemic Sound), at the L2 level: about 26 dB under the voice while Daniel speaks and 22 dB under in the gaps, with 0.4 s ramps, then two-pass loudness normalisation to -16 LUFS. The file is in `films/music/`, which is gitignored. The SFX are L2's set plus three new ones (`refuse`, `relay`, `lid`; `build/gen_sfx.py`).

## How to rebuild
```sh
cd lectures/L4-the-hands/films/build
python3 make_data.py                     # build/data/l4_data.json from the logs and the toolbox (stdlib)
python3 narrate.py <film>                # narration + timeline (light HTTP); then python3 tidy_cues.py <film>
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run modal_films.py::style --film <film> --frames 300,900 --tag t1   # style stills with overlays
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run --detach modal_films.py::full_spawn --film <film>              # build + render on L40S (40 chunks in parallel)
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run modal_films.py::full_poll --call-id <id>
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run modal_films.py::comp --film <film>                             # overlays + mix + mp4/webm/jpg -> films/
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run modal_films.py::webm_fit --film <film> --mb 23.5               # if the webm is over ~25 MB
```
The build is a copy of L2's (`narrate.py`, `overlay.py`, `modal_films.py`, `fetch_fonts.py`, `gen_sfx.py`, `tidy_cues.py`, `kit/l2kit.py`, `kit/proj_worker.py`, `kit/props_s789.py`); the L2 files are untouched, so the L2 films stay reproducible. The Modal volume is `video-ad-edit:/l4films` (app `l4-films`, workspace rajatworkspace). Scenes are `build/scenes/<film>.py`, overlay and SFX specs `build/specs/<film>.py`. `::patch_spawn --film <film> --starts a,b,...` re-renders only the given 24-frame chunks. `build/grid.py` makes local contact grids of stills (QA only).

## The films

### `tool`: Inside a tool (section 3)

**Shots.** The sealed model machine, Emma's question as a chat card; a request capsule leaves the machine's slot and slides along a rail (the real tool call as a code card); the intake gate scans it against the input schema (tool.json card) and turns green; a second, ember capsule (`item_code: 500`) is refused: the gate turns ember, the shutter drops, the real refusal JSON, "0 calls reach Ledgerline"; the lid lifts off: the core's 26 bars (tool.py card, lines 7-26, long lines cut, with the lines for each service highlighted as it is named); light runs from each code line through the inner tubes and up four conduits to the three cabinets (`itm_get`, `whs_list`, `stk_query` twice), labelled at the ports; four enamel envelopes come back (the real `{rc, err_cd, msg, data}` replies as cards); they fold into one green result slab (the real 457-byte result), which travels back to the model; the error path (BAT-5000: itm_get's fault beacon, an ember reply down the conduit, ERR-ITM-0010, the structured error with `next_step`); the three parts light in turn, and the other 15 tools of the toolbox drop onto the bench.

**Numbers from.** `experiments/logs/anatomy_check_stock.json`: tool.json and tool.py (the 26 lines, `files`), the model's request (`model_request`, itself from `our_harness.json` run single), the schema check (`checked_at_the_door`), the 4 legacy calls and replies (`legacy_calls`), the result (`tool_result`), the sizes 842 and 457 bytes (`sizes`), the wrong type (`error_path_wrong_type`: 0 Ledgerline calls) and BAT-5000 (`error_path`). The 16 tools and their tool.py line lengths: `ledgerline/ledgerline/toolbox/*/tool.py` via `build/make_data.py`.

**Script** (subtitles; the voice reads the same sentences with the numbers and codes spelled out):

> Emma asks: how many BAT-500 battery packs do we have in Manchester main stores? The model cannot open Ledgerline. It can only write text, so it writes a request.
>
> Here is the request, a tool call: the name check_stock, and one argument, item_code BAT-500. Nothing has happened yet.
>
> First it meets tool.json, the tool's contract. The input schema asks for one field, item_code: a string, required. This request passes. But what if the model sent the number 500? The door refuses it: item_code should be string, got int. Zero calls reach Ledgerline.
>
> Behind the door is tool.py: 26 lines of Python, running in Emma's own Ledgerline session. It calls the legacy services: itm_get for the item, whs_list for the warehouses, then stk_query twice, for Manchester and for Leeds.
>
> Ledgerline answers in terse envelopes. rc: S. err_cd: null. An empty msg, and a data block of short codes. Manchester: 5,400 on hand. Leeds: 1,200.
>
> The tool turns four envelopes into one clean, typed result. Each warehouse with its free stock, 6,600 in total, and 11 days of cover. 842 bytes of legacy replies become 457. Only this goes back to the model.
>
> And when the request is wrong? Ask for BAT-5000, which does not exist. itm_get answers rc E, ERR-ITM-0010, ITEM NOT FOUND. The tool turns that into ok: false, the error in words, and a next step: use find_item with a description.
>
> So every tool has three parts: a contract the request must meet, code that talks to the old system, and one clean result or a clear error. Open any tool in the toolbox, and you will find the same three.

### `context`: What the model sees (section 8)

**Shots.** The model machine faces an empty glass vitrine (the context window); a black wall with one slot stands beyond it. Slabs drop in, each as tall as its real token count (1 mm per token): the system prompt (654, with its first lines as sent), the tool definitions (128, with one definition as sent), while a violet ghost column beside it rises to 1,555 for all 16 tools; Emma's message (17); a scan plane rises through the vitrine as the model reads 799 tokens, and its tool call (23) drops in, shown as the real assistant message. The request capsule leaves through the slot; behind the wall, in a dark booth seen through smoked glass, the tool's code bars light, pulses run to the cabinets, and the database, Emma's session card and the padlock are labelled, with the log's list of what never enters the context. The wall goes dark; a green slab comes back through the slot and the tool result (229, the real tool message) drops in. The second read (1,051) and the reply (57, written). Then Emma's full order: eleven columns, one per model call, each stacked with that call's real context at 0.24 mm per token, rising one by one; the 610-token policy search glows in every later column; the counts 1,916 to 4,035 under the columns; 34,984 read in all.

**Numbers from.** `experiments/logs/our_harness.json`. Run `single` (gemini-3.8-flash, the app's prompt, 2 tools): `context_parts` (654, 128, 17, 23, 229; sum 1,051 = `check_only_tool_returns_in_context.last_prompt_tokens`), `steps[].prompt_tokens` (799, 1,051), `steps[1].completion_tokens` (57), the messages shown (`steps[1].messages`), `what_never_enters_the_context`. Tool definitions for all 16: run `order`, `context_parts` (1,555). The full order: run `order_hands` (the L4 "hands" prompt with no codes, `l4_prompts.HANDS_L4`, 331 tokens): `context_parts` and `steps[].prompt_tokens` (1,916, 2,226, 2,915, 2,966, 3,102, 3,250, 3,404, 3,581, 3,729, 3,860, 4,035; `make_data.py` checks that each step's prompt is exactly a prefix of the parts), `summary.tokens_in` (34,984 = their sum, checked). A user message that the provider measured together with the reply before it is drawn inside that reply slab (the log records it as `None`).

**Script:**

> A common belief: when the model uses a tool, it sees everything inside it, the code, the old system, the database. It does not. It sees one thing: its context window. Let's fill it, part by part, with the real tokens from Emma's question.
>
> First, the system prompt: who Emma is, today's date, and how to work. 654 tokens.
>
> Next, the tool definitions: a name, a description and an input schema for each tool. Two tools: 128 tokens. All 16 tools: 1,555 tokens, sent on every call.
>
> Then Emma's question: 17 tokens. The model reads all 799, and answers with a tool call, not with words: check_stock, BAT-500. 23 tokens.
>
> Now the tool runs, on the other side of this wall. tool.py, four legacy services, the database, Emma's session and her password. None of it enters the context. The model cannot see past the wall.
>
> One thing comes back through the slot: the JSON the tool returned. 229 tokens. The 5,400 is in there, and it is all the model knows about Ledgerline.
>
> The second call reads all 1,051 tokens again, and writes the answer in 57: Manchester main stores has 5,400 packs.
>
> Now Emma's full order, on a prompt with no codes, and all 16 tools. Every call re-sends the whole context, plus each new call and result. One policy search returned 610 tokens, and it rides along on every later call. Over eleven calls the context grows from 1,916 to 4,035 tokens: 34,984 read in all.
>
> So the model never sees inside a tool. It sees what you expose, the calls it makes, and what your tools return. Write those well. They are all it has.

### `orchestra`: Many tools, one request (section 9)

**Shots.** Our model machine stands inside our harness's open rig (seven control modules on the top beam) and faces a two-tier rack of the 16 tools (the list of names as sent). Each call is a capsule flying from the model to its tool; the tool lights; a tile lands on the trace strip in front (green: a result; slate: no answer; ember: the guessed date; sky: the write; pale sky: Emma's turns). A trace panel lists each call with its real arguments and a summary of its real result, in order: three at once (find_item, find_supplier, check_budget), then check_budget(PRD-07) and search_policy, a second search_policy (no clause), check_stock, the preview with the guessed need-by date (the real arguments and the tool's "Nothing has been saved" note, with the logged model error), supplier_certificates, the reply asking for the date, Emma's two answers, the second preview and the write (PR/2026/04417, waiting for DOKAFOR). The flashback: a capsule bounces off create_purchase_order in ember (the earlier run's real refusal JSON), then flies to create_purchase_request. Claude's harness appears as a sealed housing with its own strip and panel: its 8 calls in its own order. The last shots: the housing with the log's list of what is left to Claude, then our rig's modules lighting one by one with what we set, and the counts (calls, tokens, cost) for both, with the note that the two runs use different models.

**Numbers from.** Our harness: `our_harness.json` run `order_hands` (`turns[].cards`: every call's tool, arguments and result, in order; `summary`: 11 tool calls, 11 model calls, 34,984 tokens in, £0.02612 estimated at OpenRouter's list price; `observed_model_errors`: the guessed need_by 2027-02-01; `ledgerline_after`: PR/2026/04417, PA, approver DOKAFOR; `harness`: max 14 rounds; `tools_exposed`: the 16 names). The policy line ("an order this size goes to Daniel") is the returned clause POL-APR-002 §5.1. Claude's harness: `claude_harness.json` `runs.order_hands` (Claude Code 2.1.241 headless + our stdio MCP server, claude-sonnet-5.5, HANDS_L4 appended to its own prompt): `steps` (8 calls and their results), `tool_sequence`, `tokens_in_total` 86,853 (mostly a cached read of Claude Code's own prompt and tools), `cost_usd_reported` $0.0646; `comparison.left_to_claude` (shown verbatim). The flashback: `our_harness.json` run `order` (the app's prompt with codes), the create_purchase_order card (limited to £50,000; this one is £285,600; next_step), and `claude_harness.json` `findings` ("Both harnesses tried a direct order first ...").

**Script:**

> Emma's full order: I need 2,000 of the 36 V 500 Wh battery packs from Voltway for the spring launch run. No codes at all, and sixteen tools on the shelf. Which does the model call, and in what order?
>
> On our harness, the model picks every next call. The first three go out at once: find_item, find_supplier, check_budget. The pack is BAT-500. The supplier, Voltway Cells. The spring launch run, PRD-07.
>
> Then the budget, and the policy: an order this size goes to Daniel. A second search, for a need-by date, finds nothing. Then the stock: 5,400 in Manchester.
>
> Here it slips: it previews the request with a date it made up, 1 February 2027. A preview saves nothing. It checks the UN 38.3 certificate, then asks Emma for the date.
>
> She says 9 November. A second preview, then her yes, and only then does the request go in: PR/2026/04417, waiting for Daniel. Eleven calls.
>
> Tools catch mistakes too. In an earlier run, both harnesses tried a direct order first. The tool refused: a direct order is limited to £50,000; this one is £285,600. Its next step said: raise a purchase request. They did.
>
> Now the same three messages on Claude's harness: Claude Code, on our MCP server. Claude orders the calls itself: 8 calls, no policy search, and the same request at the end.
>
> In both, the model picks the next call. Around it, Claude's harness runs Anthropic's own prompt and loop. In ours, we set the model, the prompt, the tools Emma sees, a battery-safety check before every write, a 14-round limit, and a log of every token: 34,984, about 2.6 pence.
>
> Many tools, one request. The model chooses the next step. The harness decides what it can choose from.

## Credits (on each end card)
- Dr. Rajat Dandekar · Vizuara.
- Narration: ElevenLabs, voice Daniel. Music: "Observatory" by Out To The World, licensed from Epidemic Sound (not redistributed in the repo).
- Models in the recorded runs: google/gemini-3.8-flash via OpenRouter (our harness); anthropic/claude-sonnet-5.5 in Claude Code 2.1.241 (Claude's harness).
- Rendering: Blender 4.2.3 Cycles (96 samples, OIDN) on Modal L40S; composite with Pillow and ffmpeg on Modal.

## Known rough edges
- The two harnesses ran different models (gemini-3.8-flash and claude-sonnet-5.5), so the call and token counts in `orchestra` compare whole setups, not the harness alone; the film says so on screen. Claude's 86,853 tokens include its cached system prompt; our 34,984 do not include anything like it. Our cost is an estimate at list price; Claude's is the figure Claude Code reports.
- On the hands prompt neither harness hit the £50,000 refusal, so `orchestra` shows it as a flashback to the earlier recorded run (the app's prompt, with codes), labelled as such.
- `context` mixes two prompts: the single question uses the app's prompt (654 tokens) and the full order uses the hands prompt (331 tokens). The on-screen chip names the second.
- In `tool`, the tool.py card cuts lines longer than 78 characters (marked "…", and the card says so). The legacy replies were not re-sized individually: 842 bytes is the log's total for the four.
- In `tool` the envelopes return during the narration of the replies (b5), a little after the calls go out (b4), so the replies are seen arriving together rather than one by one as each call ends.
- In `orchestra` the capsules are small and quick; the trace panel carries the detail. Tool names are not labelled on the rack.
- `orchestra.webm` is 24.8 MB (just under the 25 MB mark); the mp4s are 24.2 MB.
