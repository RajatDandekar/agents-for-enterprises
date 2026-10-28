# Logs copied from v2 (measured 2026-10-27), used on L7 plates with this provenance

| File | From | What it measured |
|---|---|---|
| identity_loop.json, identity_graph.json | archive/v2/lectures/L5-the-signature/experiments/logs/ | Kavita's ₹2,80,840 order, 4 wordings × 3 Gemini tiers × 2 identities, v2 graph and loop agents: service account NE1 24/24, passthrough 0/24 |
| readback_default.json | same | silent Draft on PRD-05, 10 wordings: bare agent caught 3/10, with read-back 10/10 (gemini-3.8-flash) |
| approval_wait_50h.json, approval_wait_no_answer.json, crash_while_waiting.json, kill_switch.json | archive/v2/lectures/L7-the-night-shift/experiments/logs/ | Temporal time-skipping drills (bahi/durable): reminder at 24 h, escalation at 48 h, Rohit at 50 h; worker killed while waiting resumes |
| suite_*_summary.json | archive/v2/lectures/L6-the-inspector/experiments/logs/ (summary block only) | the 60-case suite on the v2 graph (56/60), loop (40/60) and naive (3/60) agents |

These were measured on the v2 agents (bahi/agent/graph.py, loop.py with IntentTools), not on the v3 Ask Rasoi. Plates say so.
