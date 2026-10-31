# Agentic Systems Engineering

Course code for **Agentic Systems Engineering** (formerly *AI Agents for Enterprises*), by Vizuara and led by Dr. Rajat Dandekar. It runs as twelve live sessions from 31 Oct to 6 Dec 2026.

One story runs through the whole course:
- **Northbridge Cycles**, an e-bike maker in Manchester, still runs on **Ledgerline ERP 7.2**, a screen-based system from 1998.
- **Emma Clarke**, a buyer, needs 2,000 battery packs from Voltway Cells before the spring launch. In the old system that takes screen after screen, codes and three sign-ins.
- You are the engineer Northbridge hires. Over the course you build **Ask Northbridge**, an AI agent that does the same job from one sentence: safely, as the right person, and with every step checked.

**Everything here is fictional:** the company, its people, suppliers, codes and numbers.

## Lectures
| # | Date (2026) | Lecture |
|---|---|---|
| 1 | Sat 31 Oct | The Before and the After |
| 2 | Sun 1 Nov | The Brain: how an LLM works |
| 3 | Sat 7 Nov | The Memory: giving it knowledge |
| 4 | Sun 8 Nov | The Hands: tools and MCP |
| 5 | Sat 14 Nov | The Loop: what makes it an agent |
| 6 | Sun 15 Nov | The Studio: workflows and your own agents |
| 7 | Sat 21 Nov | Trust: taking it to production |
| 8 | Sun 22 Nov | Agent frameworks in industry |
| 9 | Sat 28 Nov | Protocols and integration |
| 10 | Sun 29 Nov | Observability and evals in industry |
| 11 | Sat 5 Dec | Running agents in production |
| 12 | Sun 6 Dec | Your module: demo day |

Slides open on the course site as each lecture starts.

**A note while the course is being updated:** Lectures 1 and 2 use the Northbridge story. Lectures 3–12 and the capstone kits in `modules/` still use the earlier version of the story (a cookware maker on "Bahi ERP"), and their notebooks install that frozen version (tag `v3.1`). The ideas and the code are the same; each lecture moves to Northbridge before it is taught.

## What is here
- **`ledgerline/`**, the pip package `ledgerline-erp`:
  - the Ledgerline ERP sandbox: legacy services, screens and faults;
  - the 15-tool toolbox, each tool a `tool.json` and a `tool.py`, served over MCP;
  - the reference agent and the code for each lecture;
  - the Northbridge Experience app and the Workflow Studio.
- **`lectures/`**: for each lecture, the slides (`index.html`), the Colab notebook (`NB*.ipynb`), the assignment (`A*.md`) and the experiments that produced every number.
- **`modules/`**: the capstone module briefs and a template.
- **`deploy/`**: how the live app is deployed.

## Run a notebook on Colab
Open a lecture's `NB*.ipynb` in Colab and run all cells. The first cell installs the course package.

No API key is needed: every model call is recorded, and replay mode plays the recordings back. To call models live, set `GEMINI_API_KEY` or `OPENROUTER_API_KEY` in the notebook.

## The live app
The Northbridge Experience: https://rajatworkspace--northbridge-experience.us-east.modal.run. Play the 1998 system, then meet Ask Northbridge.
