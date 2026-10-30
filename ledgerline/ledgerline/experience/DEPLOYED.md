# The Northbridge Experience: live

**URL:** https://rajatworkspace--northbridge-experience.us-east.modal.run

Modal app `northbridge-experience` (workspace rajatworkspace), deployed 2026-10-28 from `deploy/experience_modal.py`.

| Page | What it is |
|---|---|
| `/` | The invitation: enter your name, then Henrik Weber's letter to you |
| `/brief` | Your wishlist (4 questions + picks) and the live class wall |
| `/before` | "ERP in 5 minutes", then five missions in the legacy Ledgerline ERP 7.2 client, timed and counted |
| `/after` | Northbridge's AI-native home page: Ask Northbridge chat, Daniel's inbox, order tracker, Before-vs-After scorecard, your brief vs what was built, "How it works" toggle (tool cards) |
| `/after?stage=brain\|knowledge\|hands\|agent` | Ask Northbridge as it is at Lectures 2, 3, 4, 5 |
| `/tools` | The toolbox explorer: every tool.json, tool.py, and a "try it" form |
| `/studio` | The Workflow Studio (studio builder's router, mounted) |
| `/admin` | Operator page: pause/resume Ask Northbridge, daily £ cap, players (admin token) |

Operate it:

    /Users/raj/.venv/bin/modal run deploy/experience_modal.py::admin --cmd status
    /Users/raj/.venv/bin/modal run deploy/experience_modal.py::admin --cmd pause --reason "back in 5 minutes"
    /Users/raj/.venv/bin/modal run deploy/experience_modal.py::admin --cmd resume
    /Users/raj/.venv/bin/modal run deploy/experience_modal.py::admin --cmd cap --cap 3000

The admin token is in Modal secret `northbridge-experience` (NORTHBRIDGE_ADMIN_TOKEN) and in the gitignored
`ledgerline/ledgerline/experience/admin.env`. Do not redeploy during a class: a new container re-seeds every player's Northbridge
(names, briefs and scores survive in the modal.Dict `northbridge-experience-state`).

Tests: `modal run deploy/experience_modal.py::test` (in-process, live model, 66 checks) and
`modal run ledgerline/ledgerline/experience/tests/e2e_modal.py` (Playwright against this URL, desktop + 390 px phone).
Screenshots: `ledgerline/ledgerline/experience/shots/`.
