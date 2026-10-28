"""PaperBanana briefs for Lecture 6 · The Studio. Generated on Modal by pb_modal.py into ../figs/<name>.png.
Plain labels, the Sky palette, no people, no icons. Every label is spelled exactly as it must appear."""

STYLE = (" STYLE: a clean, professional engineering diagram for a lecture slide, wide 16:9 landscape composition. "
 "Background pure white #FFFFFF, flat, no gradient, no texture. Palette only: ink #121317 for text and lines, "
 "sky blue #0B57D0 for the new AI-native parts, ember orange #C4511F for the old ERP, failures and waits, "
 "green #138A60 for data and definitions, mid grey #6B6E76 for secondary text, plus very light tints of these "
 "(#E6F1FF, #FFF1E8, #E8F7F0, #F0F4F9) for box fills. Rounded rectangles with 24px corners, no outlines or thin 1.5px "
 "outlines, very soft shadows, thin arrows with small heads, a modern geometric sans-serif font (like Google Sans) "
 "with all labels spelled exactly as given and large enough to read on a projector. Code-like labels (with braces, "
 "underscores or slashes) in a monospace font. No people, no cartoons, no clip-art, no 3D, no stock icons, no emoji, "
 "no title at the top, no extra text beyond the labels given. Generous whitespace; everything aligned to a clear grid.")

FIGS = {
"wf_vs_agent": "A two-panel side-by-side comparison of equal size. LEFT panel, header 'WORKFLOW' in sky blue with a "
 "small subtitle 'a path you draw'. Inside it, a single horizontal row of six small rounded boxes joined by straight "
 "arrows, left to right: 'Check stock' -> 'Raise PR' -> 'Rohit approves' -> 'Create PO' -> 'Release' -> 'Message "
 "Rohit'. The six boxes are in two rows of three if needed to fit (snake layout), arrows clear. Under the chain a "
 "thin caption line 'Same steps, same order, every run'. RIGHT panel, header 'AGENT' in sky blue with a small "
 "subtitle 'a model picks the path'. In its centre one larger rounded box 'Model'. Around it a ring of six small "
 "monospace tags: 'check_stock', 'find_supplier', 'create_purchase_request', 'create_purchase_order', "
 "'release_purchase_order', 'send_message'. A circular arrow loops from 'Model' out to the tags and back, labelled "
 "'choose a tool -> run it -> read the result'. Under it a thin caption line 'The next step is decided at run time'. "
 "Both panels are light grey-blue cards #F0F4F9 with identical size and alignment.",

"triggers": "A left-to-right diagram. On the LEFT, a vertical column of five equal rounded cards, each with a bold "
 "first word and a short second line: 'Manual' / 'the Run button'; 'Schedule' / 'every Monday 09:00'; 'Event' / "
 "'stock falls below reorder level'; 'Form' / 'Neha fills: goods arrived'; 'Chat or email' / 'a dealer writes in'. "
 "Five thin arrows converge from the cards into ONE rounded box on the RIGHT labelled 'Trigger node' with a "
 "subtitle 'starts one run, with its data'. From that box one arrow continues right into a short chain of two faint "
 "boxes 'Node' -> 'Node' to suggest the rest of the workflow. Cards in light sky tint, the trigger box solid sky "
 "blue with white text.",

"anatomy": "An annotated workflow diagram, left to right, with callout labels in green pointing at each part. The "
 "workflow: a rounded pill 'Monday 09:00' (callout 'Trigger') -> box 'Check stock' (callout 'Node') -> a diamond "
 "'Below reorder?' (callout 'Condition') with two exits labelled 'true' and 'false'; the 'false' exit goes down to a "
 "small grey box 'Skip'. The 'true' exit goes to box 'Raise PR' -> box 'Rohit approves' drawn in ember tint with a "
 "small pause symbol made of two short vertical bars (callout 'Approval: a saved wait') -> box 'Create PO' -> box "
 "'Release'. The arrow between 'Raise PR' and 'Rohit approves' carries a small monospace label "
 "'{{nodes.pr.request_no}}' (callout 'Data mapping'). One arrow (callout 'Edge') is plain. From 'Create PO' a thin "
 "ember dashed arrow labelled 'error' leads down to a box 'Message Kavita' (callout 'Error path'). Keep the callouts "
 "outside the chain so nothing overlaps.",

"approval_wait": "A horizontal timeline with two lanes. TOP lane labelled 'Run' shows rounded boxes left to right: "
 "'Mon 10:02 · run starts' -> 'Raise PR · PR/2026/04417' -> 'Approval node · status: waiting' (ember tint) -> a long "
 "gap drawn as a dotted line labelled 'hours or days · nothing held in memory' -> 'Resume · re-read status from Bahi' "
 "-> 'Create PO · PO/2026/01182' -> 'Release'. BOTTOM lane labelled 'Rohit' shows a single box 'Approves in his "
 "inbox' positioned under the right end of the dotted gap, with a thin arrow up into 'Resume'. Under the 'Approval "
 "node' box a downward arrow into a cylinder 'Run store · one JSON document', and from the cylinder an arrow up into "
 "'Resume'. Calm, precise, plenty of whitespace.",

"idempotency": "Two horizontal rows, one above the other, sharing a single box on the right. TOP row labelled "
 "'Run 1': box 'Raise PR' -> box 'key = hash(KJOSHI, GSK-SIL-05L, 20000, PRD-07, 2026-11-09)' in monospace green "
 "tint -> box 'No PR with this key · save PR/2026/04417'. BOTTOM row labelled 'Run 2 · same workflow, same Rasoi': "
 "box 'Raise PR' -> the same key box -> box 'Found PR/2026/04417 · already_done: true' in sky tint. Both rows end in "
 "one shared box on the far right 'Bahi: exactly one PR'. A small note under the bottom row: 'Re-running must not "
 "double-order'.",

"agent_node": "A diagram that zooms into one node. TOP: a small horizontal workflow strip of three boxes 'Chat "
 "trigger' -> 'Agent node' -> 'Message Rohit', where 'Agent node' is solid sky blue. From 'Agent node' two thin "
 "lines fan down to a large rounded panel below that shows its inside. Inside the panel, on the LEFT, three stacked "
 "input cards: 'Instructions' / 'plain words: what it is for', 'Tools' / 'a chosen few of the 15', 'Model' / "
 "'gemini-3.8-flash'. They feed into the CENTRE, a loop drawn as a circle of three labelled arcs: 'model reads' -> "
 "'calls a tool' -> 'reads the result' -> back to 'model reads', with a small label 'max 12 steps'. On the RIGHT an "
 "output card 'Reply + list of tool calls'. A small green label under the panel: 'The Lecture 5 loop, inside one "
 "node'.",

"engine_inside": "A left-to-right architecture diagram. LEFT: a document card 'Workflow JSON' with two monospace "
 "lines 'nodes: [...]' and 'edges: [...]'. CENTRE: a large rounded box 'Engine' containing four stacked numbered "
 "steps: '1  Find the ready nodes', '2  Fill templates from earlier outputs', '3  Run the node', '4  Write the run "
 "log', with a curved arrow from step 4 back up to step 1 labelled 'until nothing is ready'. A side exit from the "
 "Engine box, in ember, labelled 'Approval waiting: save the run, stop'. RIGHT: two boxes stacked with an arrow "
 "between them: 'Toolbox · 15 tools · as Kavita, Rohit or Neha' (sky tint) above 'Bahi ERP 7.2' (ember tint, grey "
 "window style). BELOW the Engine: a cylinder 'Run store' with arrows to and from the Engine.",

"studio_arch": "A left-to-right system diagram with four columns. Column 1: a rounded browser-window shape labelled "
 "'Workflow Studio' containing three small labelled regions 'Palette', 'Canvas', 'Run panel'. Column 2: a document "
 "card 'Workflow JSON' with arrows to and from column 1 labelled 'save' and 'run'. Column 3: a box 'Studio engine' "
 "with a small cylinder beneath it 'Runs and waits'. Column 4: a box 'Toolbox · the same 15 tools as Ask Rasoi' "
 "above a box 'Your own Rasoi · Bahi ERP 7.2' (ember tint). Along the bottom, a thin green line spanning columns 3-4 "
 "labelled 'every write: preview, confirm, idempotency key, the person's own permissions'. Sky blue for the new "
 "parts.",

"map_studio": "The architecture of an enterprise assistant called 'Ask Rasoi', drawn as a layered stack, top to "
 "bottom. TOP row: three small labels for people 'Kavita', 'Rohit', 'Neha' (text only, no figures) with arrows down "
 "into a row of three rounded boxes: 'Ask Rasoi chat', 'Workflow Studio', 'Approvals inbox'. 'Workflow Studio' is "
 "highlighted: solid sky blue fill with white text and a soft glow; everything else is pale and muted grey. BELOW: a "
 "large rounded box 'Harness · the loop' containing two boxes 'LLM · brain' and 'Knowledge · RAG + wiki'; along its "
 "right edge small text 'system prompt · history · tool registry · stop rules · budget'. An arrow labelled 'MCP' "
 "down into a box 'Toolbox · one tool per activity · tool.json + tool.py'. Beside the Toolbox on the right, a "
 "highlighted sky-blue tag 'Workflows and your own agents' with a thin line from 'Workflow Studio' down to the "
 "Toolbox, bypassing the harness, to show workflows call tools directly. A second muted tag 'Trust: identity, "
 "approvals, evals, traces'. BOTTOM: a grey window-style box 'Bahi ERP 7.2 (1998)' with an arrow from the Toolbox "
 "labelled 'services (black boxes)'.",
}
