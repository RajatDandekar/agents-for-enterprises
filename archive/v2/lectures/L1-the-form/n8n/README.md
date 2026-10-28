# Lecture 1 lab · automate Kavita's reorder in n8n

A fixed workflow is the second way forward (after "train more people"): draw the happy path once, run it forever. This lab draws it in [n8n](https://n8n.io), runs it against the Bahi sandbox, and then counts what happens to the drawing when the variants arrive.

## 1. Run Bahi

```bash
pip install "bahi-erp[server] @ git+https://github.com/RajatDandekar/agents-for-enterprises.git#subdirectory=bahi"
python -m bahi.server            # http://127.0.0.1:8077   (legacy client at /legacy)
```

In Colab, NB1 starts the same server with `serve()`; for n8n, run it on your own machine so n8n can reach it.

## 2. Run n8n

Either `npx n8n` (Node 20) or Docker:

```bash
docker run -it --rm -p 5678:5678 n8nio/n8n
```

Open http://localhost:5678, then **Workflows → Import from file → `bahi_happy_path.json`**.

In the **Order** node, set `bahi_url`:
- n8n on your machine (npx): `http://127.0.0.1:8077`
- n8n in Docker: `http://host.docker.internal:8077`

## 3. The happy path

`bahi_happy_path.json` has 8 nodes, 6 of them HTTP requests, each sending the same `X-Screen` / `X-Task` headers the legacy client sends, so Bahi's live run (`GET /live-run`) shows which "screen" n8n pressed:

```
Start → Order (Set) → Login Kavita → PR Save → PR Submit → PO Fetch → PO Save → PO Release
```

Press **Execute workflow**. With the shipped order (15,000 gaskets, PRD-07) Bahi answers:

| # | Screen | Button | Service | Bahi says |
|---|---|---|---|---|
| 1 | SYS-LGN-01 | Sign in | usr_get | S |
| 2 | PUR-PR-01 | Save | pr_save | PR/2026/04417 SAVED |
| 3 | PUR-PR-01 | Submit | pr_submit | PR/2026/04417 APPROVED (WITHIN LIMIT) |
| 4 | PUR-PO-01 | Fetch | po_fetch | S |
| 5 | PUR-PO-01 | Save | po_save | PO/2026/01182 SAVED |
| 6 | PUR-POR-05 | Release | po_release | PO/2026/01182 RELEASED |

(We ran exactly this in n8n 1.64.3; log: `../experiments/logs/n8n_real.json`.)

Notice what the drawing already knows that no screen tells you: `tax_cd` is set to `GST18-INTER` in the Order node, overriding Fetch's `GST18-INTRA`, because Deccan is in Gujarat.

### Now change one number

Set `qty` to **20,000**, Kavita's real order, and run again. Gross is ₹2,80,840, above her ₹2,50,000 limit:

- PR Submit: `SUBMITTED FOR APPROVAL` (it waits for Rohit)
- PO Save: `ERR-PO-0603 SOURCE PR NOT APPROVED (PA)`
- PO Release: `ERR-SYS-0421 PO_NO MANDATORY`

Every reply is HTTP 200, so **n8n reports the execution as `success`**. Bahi's errors live inside the reply body; the workflow does not read them unless you draw a check.

## 4. Exercise · add the variants, count the branches

Add three yes/no variants with IF nodes:

1. **Direct or request?** A direct order (`po_type: DIR`, no PR) is allowed only up to ₹50,000 gross. Above that, raise a request first.
2. **Cost centre closed?** Check it with `cc_get` before anything else. A closed cost centre saves silently as Draft.
3. **Approval needed?** If PR Submit returns status `PA`, someone with a big enough limit must approve (`pr_approve`, signed in as Rohit, `RMEHTA` / `rohit@123`). In a real workflow this is a Wait node; here, sign in as Rohit and approve inline.

Then answer:
- How many combinations of the three variants are there? How many can actually happen in Bahi?
- How many end-to-end paths did you draw? How many IF nodes, how many nodes in all?
- With the six variants on the Lecture 1 plate (add: price changed, new supplier, reply lost), how many combinations?

Our solution is `bahi_variants_solution.json`. We ran it on every combination against Bahi (`check_workflows.py`, log `../experiments/logs/n8n_check.json`) and in real n8n for 15,000 and 20,000 (`n8n_real.py`):

| | |
|---|---|
| Variants | 3 |
| Combinations | 2³ = 8 |
| Can happen | 6 (a direct order is at most ₹50,000, always within Kavita's limit, so "direct + needs approval" is impossible) |
| Paths drawn in our solution | 4 (closed cost centre stops for a person; handling it instead needs one path per feasible combination: 6) |
| Nodes / IF nodes / HTTP nodes | 19 / 3 / 12 (happy path: 8 / 0 / 6) |
| Six variants | 2⁶ = 64 combinations |

Each yes/no variant doubles the combinations someone must think through and, unless it is impossible or ends in "stop", draw. An agent with a harness handles variants as they come; that is the rest of the course.

## Files

| File | What it is |
|---|---|
| `bahi_happy_path.json` | the happy path, importable into n8n 1.x |
| `bahi_variants_solution.json` | the exercise solution (three IF nodes) |
| `build_workflows.py` | writes both JSON files (standard library only) |
| `check_workflows.py` | runs them on every variant combination against a fresh Bahi (Modal) |
| `n8n_real.py` | installs Node 20 + n8n 1.64.3 on Modal, imports and executes them for real |

Note for the n8n CLI: `n8n import:workflow` wants a JSON **list** of workflows; the UI's Import from file takes the single workflow object in these files.
