# From Forms to Agents

Course code for **AI Agents for Enterprises** (Vizuara, led by Dr. Rajat Dandekar).

One story runs through the whole course:
- **Bahi ERP:** a 1998 form-based ERP.
- **Rasoi Steel Works:** the pressure-cooker maker in Pune that runs it.
- **Kavita's order:** her 20,000-gasket reorder goes from seven legacy screens to one sentence to an agent.
- **The spine:** the form was doing nine jobs, and each lecture rebuilds one of them.

**Everything here is fictional:** the company, its people, suppliers, codes and numbers.

## What is here
- `bahi/`: the pip package `bahi-erp`.
  - The Bahi ERP sandbox: 38 legacy services, stored procedures, screens, faults.
  - A legacy Windows-style client.
  - The reference agent, one layer per lecture: tools, MCP, control graph, authority, evals, durable workflows.
  - Eight capstone module kits.
- `lectures/`: per lecture, the slides (`index.html`), the Colab notebook (`NB*.ipynb`), the assignment (`A*.md`) and the experiments with their logs.
- `modules/`: the capstone module briefs and a template.
- `deploy/`: Dockerfile, Modal app, rollout ladder, runbook.

## Run a notebook on Colab
Open any `lectures/*/NB*.ipynb` in Colab and run all cells. The first cell installs the sandbox:

```
pip install "bahi-erp[all] @ git+https://github.com/VizuaraAI/agents-for-enterprises.git#subdirectory=bahi"
```

No API key is needed. Every model call is recorded, and replay mode plays the recordings back. To call models live, set `GEMINI_API_KEY` or `OPENROUTER_API_KEY`.
