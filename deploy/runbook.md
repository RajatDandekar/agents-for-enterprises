# Runbook: the Bahi purchasing agent

For whoever is on call. Plain steps, in order. Everything here is the fictional Bahi sandbox; the shape carries
over to a real ERP. The first rule for anything that writes money: **switch writes off first, investigate second.**

## What runs where

| Piece | What it is | Where |
|---|---|---|
| Bahi | the ERP (the sandbox is in-memory in the same process) | `deploy/app.py` via `bahi.server` |
| Agent API | chat endpoint, order endpoints, flags | `deploy/app.py` (FastAPI, one uvicorn worker) |
| Temporal worker | runs `PurchaseOrder` workflows and their activities | same process (sandbox); its own deployment against a real ERP |
| Temporal server | stores every workflow's history and timers | test server in dev; a cluster (`TEMPORAL_ADDRESS`) in staging and prod |
| Flags | kill switch and rollout stage | `BAHI_FLAGS_FILE` on a volume that survives restarts |
| Versions | pinned prompts, tool schemas, workflow, model | `deploy/versions.yaml`, checked at build and at `/version` |

## Staging, as deployed

* **URL:** https://rajatworkspace--bahi-agent-staging.us-east.modal.run (Modal workspace rajatworkspace, app `bahi-agent-staging`).
  The chat is at `/app/chat` (Kavita: KJOSHI / kavita@123), the inbox at `/app/inbox` (Rohit: RMEHTA / rohit@123),
  `/app/slack`, `/app/audit`. The sandbox passwords are public course material; the data is fictional.
* **Temporal:** there is no Temporal Cloud. Staging runs `BAHI_TEMPORAL=local`: an in-process Temporal dev server
  started by `WorkflowEnvironment.start_local()`, with real timers. Its workflows, like the sandbox ERP, live in the
  container's memory: when the container stops (20 idle minutes, a redeploy, a crash) both reset together. That is
  fine for a sandbox and wrong for prod, where `BAHI_TEMPORAL=connect` points at a real cluster.
* **Secrets:** Modal secret `bahi-staging` (GEMINI_API_KEY, BAHI_ADMIN_TOKEN, OPENROUTER_*, LANGFUSE_*). The admin token
  exists only there. Use it through `deploy/admin.py`, which runs inside Modal and never prints it. To rotate it,
  recreate the secret with `--force` and redeploy.
* **Cost controls,** all in front of the model, all in `deploy/app.py`:
  - model switch: `modal run deploy/admin.py --cmd model-off` (chat answers 503; Bahi, the inbox and the pages still work);
  - a daily cap: `BAHI_DAILY_CAP_INR` (₹250 per IST day), estimated from `bahi.llm` list prices, kept in
    `/var/bahi/spend.json`; past it, model routes answer 429 until midnight IST. `GET /spend` shows today's total;
  - rate limits: 20 model-bearing requests a minute in all, 6 per signed-in user;
  - one container at most (`max_containers=1`), scaled to zero after 20 idle minutes.
* **Do not use `/admin/reset` on the reference app:** it replaces Bahi's tenant while the app keeps the old one.
  To reset staging, stop the app (`modal app stop bahi-agent-staging`); the next request starts a fresh sandbox.
* Operator commands: `BAHI_ENV=staging modal run deploy/admin.py --cmd status|kill|revive|model-off|model-on|stage|smoke`.

Useful calls (admin token from the secret store, never pasted into chat):

```
GET  /healthz                 is the process up
GET  /readyz                  can it read Bahi, is the worker running, are writes on, which stage
GET  /version                 what this build runs vs what is pinned
GET  /flags                   kill switches (writes, model) and stage
GET  /spend                   today's model spend against the cap
POST /flags {"kill": true, "reason": "..."}      X-Admin-Token: ...      writes off, everywhere, now
POST /flags {"revive": true}                                             writes back on
POST /flags {"stage": "assist"}                                          move down (or up) the ladder
POST /flags {"model": false}                                             the assistant stops calling the model
GET  /orders/{workflow_id}    a workflow's stage, request, PO, reminders, diary
```

## 1. Bahi is down (or timing out)

What you see: `/readyz` shows `bahi` not `S`; users get "Bahi did not answer"; workflows sit in a stage with
activity retries in Temporal's UI.

1. Do nothing to the workflows. Each write activity retries with back-off (2 s, 4 s, 8 s ... up to 1 min, 6 attempts)
   and every write looks its key up before writing, so retries cannot duplicate.
2. If Bahi will be down longer than a few minutes, switch writes off (`POST /flags {"kill": true, "reason": "Bahi down"}`).
   Workflows then **pause** before their next write instead of using up their retries. Chat still answers reads it can.
3. Tell the purchase team in one line: "Bahi is down; orders you confirm are held, not lost."
4. When Bahi is back: `/readyz` green, then `POST /flags {"revive": true}`. Paused workflows carry on within 10 minutes.
5. Check for duplicates (section 3) once, to be sure.

If an activity exhausted its retries before you switched off, its workflow ends `failed` with the error in its diary.
Restart it with the same order: the workflow id is the key, the activities find whatever was already saved.

## 2. An approval is stuck

What you see: `GET /orders/{id}` shows `waiting for approval` for longer than expected.

1. Read the diary. The workflow reads Bahi every 4 hours and at each deadline; `read back request` lines show what Bahi said.
2. Reminders are automatic: Rohit at 24 h, Anand Patil (plant head) at 48 h plus a second reminder to Rohit.
   At 120 h the workflow stops and tells Kavita; nothing is ordered.
3. If Rohit approved in Bahi and the workflow has not noticed yet, it will at the next poll (at most 4 h). To make it look
   now, send the `recheck` signal (the app does this when Kavita says "Rohit approved it"). Never send `approval_decided`
   on someone's behalf: the approval must exist in Bahi, under the approver's own login.
4. If Rohit is away for days: Anand can approve (his limit covers it). Changing who approves is a Bahi setting, not an
   agent setting.
5. If the workflow says `expired`, it is finished. A new request needs Kavita to ask again.

## 3. Duplicates appear

What you see: two live orders for the same supplier and item on the same day that nobody asked for.

1. **Switch writes off now**: `POST /flags {"kill": true, "reason": "duplicates: <PO numbers>"}`.
2. Find them:
   ```sql
   SELECT h.sup_cd, l.itm_cd, GROUP_CONCAT(h.po_no) pos, COUNT(*) n
   FROM po_hdr h JOIN po_line l ON l.po_no = h.po_no
   WHERE h.created_on >= :today AND h.status NOT IN ('CN','RJ')
   GROUP BY h.sup_cd, l.itm_cd HAVING n > 1;
   ```
3. For each pair, look at `client_ref`. Same key twice should be impossible (the look-up runs first); if you see it, the
   activities were bypassed, so find the code path that wrote without the look-up. Different keys means two different
   requests: find the two chat messages (`ref`) and ask the buyer which one was meant.
4. Cancel the extra order in Bahi (`po_cancel`, with the reason), as the buyer or purchase manager, not as the agent.
   Released orders also need a call to the supplier.
5. Write down what happened, then `revive`. If the cause is code, roll back first (section 4).

## 4. Rolling back

Three kinds of change, three ways back:

* **Prompt, tool or model** (`versions.yaml`). Redeploy the previous image tag. Builds pin every hash, so the old
  image is exactly the old behaviour. Before that, step the ladder down (`{"stage": "assist"}`) so people confirm every
  write while you work.
* **Workflow code.** Careful: Temporal replays running workflows (some have waited days for Rohit) through the code
  that is deployed now. A change that alters the order of activities or timers breaks their replay.
  * Additive change: wrap it in `if workflow.patched("<change-id>"):` so old histories take the old path.
  * Bigger change: register it under a new workflow name (`PurchaseOrderV2`), start new orders on it, and keep the old
    worker code until the last old workflow finishes.
  * Rolling back a workflow change means keeping both versions deployed until the new one's workflows have drained.
* **Bad data written.** Not a rollback: switch off, fix it in Bahi as the people who own it, then revive.

## 5. Before every release (the checklist the build enforces, and the one it cannot)

- [ ] `python -m deploy.versions --check` passes (the image build runs it)
- [ ] the Lecture 6 scenario suite passes on this build, never-events 0
- [ ] the four failure drills pass: timeout after commit, error before commit, crash after commit, kill switch
- [ ] staging ran the same image for a day with real timers
- [ ] the rollout stage in `versions.yaml` for the target environment is the rung you mean to be on
- [ ] someone other than the author has read the diff of any prompt or workflow change
