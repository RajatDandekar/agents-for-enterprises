# The Rasoi Experience: live

**URL:** https://rajatworkspace--rasoi-experience.us-east.modal.run

Modal app `rasoi-experience` (workspace rajatworkspace), deployed 2026-10-28 from `deploy/experience_modal.py`.

| Page | What it is |
|---|---|
| `/` | The invitation: enter your name, then Anand Patil's letter to you |
| `/brief` | Your wishlist (4 questions + picks) and the live class wall |
| `/before` | "ERP in 5 minutes", then five missions in the legacy Bahi ERP 7.2 client, timed and counted |
| `/after` | Rasoi's AI-native home page: Ask Rasoi chat, Rohit's inbox, order tracker, Before-vs-After scorecard, your brief vs what was built, "How it works" toggle (tool cards) |
| `/after?stage=brain\|knowledge\|hands\|agent` | Ask Rasoi as it is at Lectures 2, 3, 4, 5 |
| `/tools` | The toolbox explorer: every tool.json, tool.py, and a "try it" form |
| `/studio` | The Workflow Studio (studio builder's router, mounted) |
| `/admin` | Operator page: pause/resume Ask Rasoi, daily ₹ cap, players (admin token) |

Operate it:

    /Users/raj/.venv/bin/modal run deploy/experience_modal.py::admin --cmd status
    /Users/raj/.venv/bin/modal run deploy/experience_modal.py::admin --cmd pause --reason "back in 5 minutes"
    /Users/raj/.venv/bin/modal run deploy/experience_modal.py::admin --cmd resume
    /Users/raj/.venv/bin/modal run deploy/experience_modal.py::admin --cmd cap --cap 3000

The admin token is in Modal secret `rasoi-experience` (RASOI_ADMIN_TOKEN) and in the gitignored
`bahi/bahi/experience/admin.env`. Do not redeploy during a class: a new container re-seeds every player's Rasoi
(names, briefs and scores survive in the modal.Dict `rasoi-experience-state`).

Tests: `modal run deploy/experience_modal.py::test` (in-process, live model, 66 checks) and
`modal run bahi/bahi/experience/tests/e2e_modal.py` (Playwright against this URL, desktop + 390 px phone).
Screenshots: `bahi/bahi/experience/shots/`.
