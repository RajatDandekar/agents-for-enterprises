# L6 tools research: evals, guardrails and observability for AI agents (Nov 2026)

Compiled 16 Nov 2026 for Lecture 6 (Sat 21 Nov 2026). Audience: working engineers building an ERP procurement agent.
Constraints: we have only an **Anthropic API key** (no OpenAI, no Gemini) and **Langfuse Cloud keys**. Students use free
Google Colab (default Python 3.12 per the Colab Enterprise docs; consumer Colab assumed the same, **unverified**) or a laptop.

**How to read this file**
- **[measured]**: I pulled it myself on 16 Nov 2026 from a primary API (GitHub REST API, PyPI JSON API, pypistats.org,
  npm downloads API). Stars and downloads change daily. Download counts include CI and mirror traffic, so they show
  relative weight, not user counts.
- **[vendor]**: the vendor's own claim. Not independently checked.
- **[secondary]**: a third-party blog, aggregator or press write-up. Treat as indicative.
- **[unverified]**: I could not confirm it. Check before putting it on a slide.

---

## 0. Headline findings

1. **The best tool-level adoption data for 2026 is the Stack Overflow Developer Survey 2026** (published 6 Oct 2026). The
   question was "Have you used any of the following tools for AI agent observability, prompts, or evals in the past year?",
   n = 2,277 respondents who used at least one tool:
   Sentry 26.0%, **LangSmith 17.3%**, **MLflow 15.2%**, **Langfuse 15.2%**, Datadog LLM 11.9%, Weights & Biases 10.7%,
   Arize AI 5.8%, Braintrust 5.8%, **DeepEval 5.8%**, Respan 5.6%, **Promptfoo 5.3%**, Agenta 5.0%, Ragas 4.9%,
   Galileo 4.8%, Portkey 4.8%, LangWatch 4.4%, Helicone 4.2%, Humanloop 4.1%, PromptLayer 4.0%, Patronus 4.0%,
   HoneyHive 4.0%, Confident AI 3.8%, Traceloop 3.8%, Opik 3.7%, and others at 3–3.5%.
   Source: https://survey.stackoverflow.co/2026/ai/data (section "AI agent observability and security").
   - Caveats: these are developers, not companies. The answer was self-reported. Humanloop shows 4.1% even though its
     platform shut down in Sept 2025, which says something about noise in the long tail.
   - The 2025 survey asked a narrower question about "AI agent observability, monitoring or security tools", n = 2,689:
     Grafana+Prometheus 43%, Sentry 31.8%, Snyk 18.2%, New Relic 13%, LangSmith 12.5%, Langfuse 8.8%,
     Honeycomb 8.8%, Galileo 6.2%, Protect AI 5%, Arize 3.7%, Helicone 3.2%, Opik 2.3%.
     Source: https://survey.stackoverflow.co/2025/ai. So between 2025 and 2026, Langfuse went from 8.8% to 15.2% and
     LangSmith from 12.5% to 17.3%. The two questions were worded differently, so this shows direction, not an exact trend.
2. **LangChain "State of Agent Engineering"** surveyed 1,340 people between 18 Nov and 2 Dec 2025 (page dated 12 Jun 2026):
   - 89% have some observability for their agents (94% of teams with agents in production).
   - 62% have step-level tracing (71.5% in production).
   - 52.4% run offline evals and 37.3% run online evals (44.8% in production). 29.5% do no evals at all.
   - 59.8% use human review and 53.3% use LLM-as-judge.
   - Quality is the number one blocker (32%), then latency (20%).
   - 57.3% have agents in production. More than two thirds use OpenAI models.
   Source: https://langchain.com/state-of-agent-engineering. Caveat: LangChain surveyed its own audience and sells
   LangSmith, so read it as direction, not a census.
3. **Gartner, "Market Guide for AI Evaluation and Observability Platforms"**, 2 Feb 2026 (Bhat, Coqueiro, van Ginkel;
   paywalled, https://www.gartner.com/doc/7387730). Strategic planning assumption: by 2028, 60% of software engineering
   teams will use these platforms, up from 18% today [secondary, quoted via vendor posts]. Vendors that say they are named as
   "Representative Vendors" include Comet Opik (https://www.comet.com/site/blog/gartner-market-guide-february2026/),
   Openlayer and HoneyHive (https://www.honeyhive.ai/blog/honeyhive-recognized-in-the-2026-gartner-market-guide-for-ai-evaluation-and-observability-platforms)
   [vendor]. W&B republishes the report: https://wandb.ai/site/resources/whitepapers/gartner-ai-evaluation-observability-platforms.
   The Gartner Peer Insights "trending" list (Logfire, LangSmith, Microsoft Foundry, Braintrust, Langfuse, Maxim, Galileo) is
   a separate review site, not the guide's list: https://gartner.com/reviews/market/ai-evaluation-and-observability-platforms.
4. **2025–2026 brought a wave of consolidation**. Do not teach a tool without checking its status (section 6). The ones that
   matter most for us:
   - ClickHouse bought **Langfuse** (Jan 2026). It stays MIT and self-hostable.
   - OpenAI bought **Promptfoo** (announced 9 Mar 2026). It stays open source.
   - **OpenAI's own Evals platform shuts down on 30 Nov 2026**, and OpenAI points users to Promptfoo.
   - Palo Alto Networks bought Protect AI, and **LLM Guard was archived on GitHub (July 2026)**.
   - Mintlify bought **Helicone**, which is now in maintenance mode.
   - Check Point bought **Lakera**.
   - Snyk bought **Invariant Labs**.
   - Cisco bought **Galileo** (closed 22 May 2026).
   - ServiceNow bought **Traceloop**, the maker of OpenLLMetry.
   - Palo Alto Networks bought **Portkey**.
   - **Humanloop** was sunset and its team joined Anthropic.
5. **The OpenTelemetry GenAI semantic conventions are still "Development"** (not stable) in Nov 2026. In semconv v1.42.0
   (12 Jun 2026) they moved to a dedicated repo, `open-telemetry/semantic-conventions-genai`. Agent spans
   (`create_agent`, `invoke_agent`, `invoke_workflow`, `plan`, `execute_tool`) are defined, but all of them are Development.
6. **OWASP has two current lists:**
   - The **Top 10 for Agentic Applications 2026** (ASI01–ASI10), published 9 Dec 2025.
   - The **2026 edition of the Top 10 for LLM Applications**, published Aug/Sept 2026. It replaces the 2025 list:
     Excessive Agency rises to LLM03, and System Prompt Leakage becomes "Hidden Context Exposure".

---

## 1. Standards

### 1.1 OpenTelemetry GenAI semantic conventions (status Nov 2026)

- **Where:** https://github.com/open-telemetry/semantic-conventions-genai. Since semconv v1.42.0 (12 Jun 2026), the
  GenAI and MCP conventions live here and no longer in the core repo. The old opentelemetry.io pages now show a "Moved"
  notice: https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-metrics/. The move and its date come from
  https://www.dash0.com/knowledge/opentelemetry-genai-semantic-conventions-explained and
  https://pub.towardsai.net/tracing-ai-agents-what-otels-genai-spans-actually-capture-560fafc96de2 [secondary].
  - When I read the repo README, it showed no tagged release and its Schema URL was "TODO". A TrueFoundry post says there
    was no tagged release as of Aug 2026: https://www.truefoundry.com/blog/opentelemetry-genai-semantic-conventions [secondary].
- **Stability:** all GenAI spans, events, metrics and attributes are **Development**. The only Stable attributes on these
  pages are generic ones inherited from core semconv (`error.type`, `server.address`, `server.port`).
  Source: https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md
- **Agent spans** (https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md):
  - `create_agent {gen_ai.agent.name}`: span kind CLIENT.
  - `invoke_agent {gen_ai.agent.name}`: INTERNAL, or CLIENT for a remote agent. Use it when an LLM drives the control flow.
    Use `invoke_workflow` when the application drives the control flow.
  - `plan {gen_ai.agent.name}`: INTERNAL.
  - `execute_tool {gen_ai.tool.name}`: `gen_ai.tool.name` is required.
  - Model calls are `chat {model}` (inference spans).
  - Key attributes: `gen_ai.operation.name`, `gen_ai.provider.name` (this replaced `gen_ai.system` in v1.37),
    `gen_ai.request.model`, `gen_ai.usage.input_tokens` and `gen_ai.usage.output_tokens`, `gen_ai.agent.name`
    (must be low cardinality), `gen_ai.agent.id`, `gen_ai.conversation.id` (set it only when a real id exists; never fall
    back to a UUID or trace id), `gen_ai.tool.name`, `gen_ai.tool.call.id`.
  - Memory operations are now specified too: `create_memory_store`, `search_memory`, `create_memory`, `update_memory`,
    `delete_memory`, and others.
- **Content capture is opt-in:** `OTEL_INSTRUMENTATION_GENAI_CAPTURE_CONTENT` takes `NO_CONTENT` (the default),
  `SPAN_ONLY`, `EVENT_ONLY` or `SPAN_AND_EVENT` (gen-ai-spans.md above). This is useful for the PII and redaction slide.
- **Opt-in for the latest experimental names:** older instrumentations use
  `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`. One source says newer OpenAI instrumentation uses the latest
  conventions unconditionally: https://particula.tech/blog/opentelemetry-genai-semantic-conventions-stable [secondary, unverified].
- **Who reads these names:**
  - Datadog Agent Observability (formerly "LLM Observability") ingests OTel GenAI semconv 1.37+ or OpenInference
    [secondary: https://langfuse.com/resources/engineering/langfuse-vs-datadog, https://kenzo0107.github.io/en/2026/06/11/langfuse-vs-datadog-llm-observability/].
  - Langfuse, Phoenix, MLflow, Logfire, Opik and W&B all accept OTLP.
  - In practice there are two vocabularies: GenAI semconv and Arize's **OpenInference**.
- **Anthropic auto-instrumentation packages** [measured, PyPI, trailing 30 days]:
  - `opentelemetry-instrumentation-anthropic` 0.63.0 (Traceloop/OpenLLMetry): 3.44M downloads/month.
  - `openinference-instrumentation-anthropic` 3.3.5 (Arize): 1.36M/month.
  - `opentelemetry-semantic-conventions` 0.66b2: 338M/month. It is a transitive dependency of everything OTel.

### 1.2 OWASP

**OWASP Top 10 for Agentic Applications 2026.** Published 9 Dec 2025 by the OWASP GenAI Security Project, with more than
100 contributors. Official page: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/.
Titles are taken from https://www.giskard.ai/knowledge/owasp-top-10-for-agentic-application-2026 [secondary; they match
TechRepublic and others]:

| ID | Title | Northbridge example (ours) |
|---|---|---|
| ASI01 | Agent Goal Hijack | the poisoned invoice e-mail redirects the agent |
| ASI02 | Tool Misuse and Exploitation | `create_purchase_request(confirm=true)` with no yes |
| ASI03 | Identity and Privilege Abuse | the agent acts as SVC_AGENT, not as Emma |
| ASI04 | Agentic Supply Chain Vulnerabilities | a third-party MCP server or tool description |
| ASI05 | Unexpected Code Execution (RCE) | (not in our toolbox) |
| ASI06 | Memory & Context Poisoning | a poisoned memory or routine from L5 |
| ASI07 | Insecure Inter-Agent Communication | background agents / A2A |
| ASI08 | Cascading Failures | one bad price propagates into many POs |
| ASI09 | Human-Agent Trust Exploitation | a confident wrong preview that Emma approves |
| ASI10 | Rogue Agents | drift, optimising for the wrong metric |

The two guiding principles are "least agency" and "strong observability"
(https://www.techrepublic.com/article/news-owasp-ai-agent-risk-list/).

**OWASP Top 10 for LLM Applications, 2026 edition.** Version 1.0, released early Aug 2026. Help Net Security covered it on
6 Aug 2026: https://www.helpnetsecurity.com/2026/08/06/owasp-2026-llm-top-10-released/. OWASP's own announcement is dated
1–2 Sept 2026 and also announces the donated **Agent Control Standard (ACS) v0.1**, a runtime-governance spec:
https://genai.owasp.org/announcement/owasp-genai-security-project-unveils-2026-top-10-for-llm-applications-new-agent-control-standard-and-sponsors-as-community-tops-30000-members/.
The list, from the Cloud Security Alliance research note
https://labs.cloudsecurityalliance.org/research/csa-research-note-owasp-genai-top10-2026-agent-control-stand/ [secondary;
check the codes against https://genai.owasp.org/home/resources/owasp-genai-llm-top-10-2026/ before the slide]:

| 2026 | Title | vs 2025 |
|---|---|---|
| LLM01 | Prompt Injection | still #1; now also covers cross-modal injection |
| LLM02 | Sensitive Information Disclosure | still #2 |
| LLM03 | Excessive Agency | up from #6 |
| LLM04 | Supply Chain | |
| LLM05 | Data and Model Poisoning | absorbs fine-tuning subversion |
| LLM06 | Unbounded Consumption | up |
| LLM07 | Misinformation | up from #9 |
| LLM08 | Hidden Context Exposure | renamed and broadened from System Prompt Leakage |
| LLM09 | Vector and Embedding Weaknesses | |
| LLM10 | Improper Output Handling | down from #5 |

Help Net Security's summary of what changed: Excessive Agency rose to 3rd, Misinformation and Unbounded Consumption
climbed, and Output Handling fell to 10th. For reference, the 2025 edition (Nov 2024) was: LLM01 Prompt Injection,
LLM02 Sensitive Info Disclosure, LLM03 Supply Chain, LLM04 Data & Model Poisoning, LLM05 Improper Output Handling,
LLM06 Excessive Agency, LLM07 System Prompt Leakage, LLM08 Vector & Embedding Weaknesses, LLM09 Misinformation,
LLM10 Unbounded Consumption (my background knowledge, consistent with the comparisons above).

---

## 2. Measured repo and package data (16 Nov 2026)

GitHub data comes from `api.github.com/repos/...` [measured]. PyPI data comes from `pypi.org/pypi/<pkg>/json` and
`pypistats.org/api/packages/<pkg>/recent` [measured]. The npm figure comes from `api.npmjs.org` [measured].

| Tool | Repo (stars, licence, last push) | Package latest (date) | Python | Downloads / last month |
|---|---|---|---|---|
| Langfuse | langfuse/langfuse 37,456, MIT core + `ee/` (API reports NOASSERTION), pushed 16 Nov | `langfuse` 5.2.0 (5 Nov 2026) | >=3.11,<4 | 30.4M |
| LangSmith | SDK repo langchain-ai/langsmith-sdk **archived** (moved to langchain-ai/langsmith-python and -javascript; "packages unchanged"); platform closed source | `langsmith` 0.14.17 (2 Nov) | >=3.10 | 91.9M (a LangChain dependency) |
| Arize Phoenix | Arize-ai/phoenix 12,304, Elastic-2.0 | `arize-phoenix` 21.0.0 (30 Oct) | >=3.11,<3.16 | 0.61M (`arize-phoenix-otel` 2.05M; `arize-phoenix-evals` 0.85M) |
| MLflow | mlflow/mlflow 28,823, Apache-2.0 | `mlflow` 3.18.0 (3 Nov) | >=3.10 | 21.4M |
| Comet Opik | comet-ml/opik 23,439, Apache-2.0 | `opik` 2.2.143 (6 Nov) | >=3.10 | 2.67M |
| W&B Weave | wandb/weave 1,147, Apache-2.0 | `weave` 0.54.1 (5 Nov) | >=3.10 | 0.75M |
| Pydantic Logfire | pydantic/logfire 4,553 (SDK only, MIT; server closed) | `logfire` 5.6.0 (11 Nov) | >=3.10 | 18.4M |
| Braintrust | SDKs Apache/MIT; platform closed | `braintrust` 0.50.0 (11 Nov); `autoevals` 0.4.1 | >=3.10 | 8.16M; autoevals 5.24M |
| Helicone | Helicone/helicone 6,281, Apache-2.0 (maintenance mode) | `helicone` PyPI pkg stale (2023) | | n/a (proxy) |
| OpenLLMetry (Traceloop) | traceloop/openllmetry 7,537, Apache-2.0 | `traceloop-sdk` 0.63.0 (5 Nov) | >=3.10 | 2.03M |
| LangWatch | langwatch/langwatch 5,037, Apache-2.0 | 1.4.0 | >=3.10,<3.14 | 0.40M |
| Laminar | lmnr-ai/lmnr 3,492, Apache-2.0 | 0.9.1 | >=3.11 | 4.28M |
| DeepEval | confident-ai/deepeval 19,494, Apache-2.0 | `deepeval` 4.3.4 (11 Nov) | >=3.10,<4 | 3.22M |
| Ragas | vibrantlabsai/ragas (moved from explodinggradients) 16,331, Apache-2.0, pushed 14 Nov | `ragas` 0.4.4 (14 Nov) | >=3.9 | 1.23M |
| promptfoo | promptfoo/promptfoo 27,245, MIT | npm `promptfoo` 0.125.1 (Node >=22.22) | n/a (Node) | **4.63M npm** (16 Oct–14 Nov) |
| Inspect AI | UKGovernmentBEIS/inspect_ai 3,256, MIT | `inspect-ai` 0.3.290 (14 Nov) | >=3.11 | 3.25M |
| OpenAI Evals (OSS) | openai/evals 19,747, last push Apr 2026 | `evals` 3.0.1 (2024) | | ~0 (dormant) |
| TruLens | truera/trulens 3,654, MIT | 2.16.0 | >=3.10,<4 | 25k |
| Evidently | evidentlyai/evidently 8,062, Apache-2.0 | 0.7.23 | >=3.10 | 0.82M |
| NeMo Guardrails | NVIDIA-NeMo/Guardrails 7,502 (Apache-2.0 per PyPI) | `nemoguardrails` 0.24.1 (16 Sep) | >=3.10,<3.14 | 0.48M |
| Guardrails AI | guardrails-ai/guardrails 7,610, Apache-2.0 | `guardrails-ai` 0.11.0 (14 Aug) | >=3.10,<3.14 | 0.12M |
| LLM Guard | protectai/llm-guard 3,216, MIT, **archived** (last push 8 Jul 2026) | 0.3.16 (May 2025) | >=3.10,<3.13 | 0.13M (legacy) |
| Meta PurpleLlama (Llama Guard, Prompt Guard, LlamaFirewall, CyberSecEval) | meta-llama/PurpleLlama 4,480 | `llamafirewall` 1.0.3 (May 2025) | | 9.7k |
| OpenAI Guardrails | openai/openai-guardrails-python 267, MIT | `openai-guardrails` 0.3.6 (26 Oct) | >=3.11 | 0.48M |
| Invariant (Snyk) | invariantlabs-ai/invariant 477, Apache-2.0, last push 12 Jan 2026 | `invariant-ai` 0.3.5 (Jul 2025) | | 2.7k (stale) |
| Presidio (PII) | | `presidio-analyzer` | | 6.0M |
| garak | NVIDIA/garak 10,039, Apache-2.0 | `garak` 0.17.1 (16 Oct) | >=3.11 | 56k |
| PyRIT | microsoft/PyRIT 4,860, MIT (old Azure/PyRIT archived) | `pyrit` 1.2.0 (13 Nov) | >=3.11,<3.15 | 93k |
| (context) anthropic SDK | | 2.8.0 | >=3.10 | 202M |
| (context) claude-agent-sdk | | 0.2.182 | >=3.10 | n/a |
| (context) openai-agents | | 0.24.0 | >=3.10 | 18.9M |

Every package above installs on Colab's Python 3.12. The exception is **llm-guard (<3.13)**, which still works on 3.12 but
is archived.

---

## 3. Tool-by-tool

Table key: **OSS** = open source and its licence. **Self-host** = can you run it yourself. **Local, no sign-in** = can a
student `pip install` it and open a UI on localhost with no account. **Claude** = can it use Anthropic Claude as the
model or judge.

### 3.1 Tracing and observability

**Langfuse** (https://langfuse.com)
- **What:** an open-source LLM engineering platform with tracing (observations, sessions, users), prompt management,
  datasets and experiments, scores, LLM-as-judge and code evaluators, dashboards, and a new AI Gateway.
- **OSS:** MIT for the core; `ee/` directories carry a separate licence.
- **Self-host:** yes. Docker Compose for local and test use; it needs Postgres, Redis/Valkey, ClickHouse and S3/Blob
  storage. Production runs on Helm/Kubernetes. https://langfuse.com/self-hosting
- **Pricing (Cloud, read 4 Nov 2026 by markaicode):** Hobby $0 (50k units, 30 days), Core $29/mo, Pro $199/mo,
  Enterprise $2,499/mo. https://markaicode.com/facts/llm-observability-tools/ [secondary]
- **Ownership:** ClickHouse acquired Langfuse; it was announced 16 Jan 2026 with ClickHouse's $400M Series D. The team says
  it will stay open source and self-hostable, and Cloud continues.
  https://langfuse.com/blog/joining-clickhouse, https://www.orrick.com/en/news/2026/01/open-source-llm-observability-langfuse-acquired-by-clickhouse-inc
- **Versions:** platform **v4** went live Aug 2026 (https://langfuse.com/changelog/2026-08-17-langfuse-v4). It uses an
  observation-centric "events" data model and **observation-level evaluators**. Python SDK v5 was released Oct 2026;
  `langfuse` 5.2.0 needs Python >=3.11. The SDK is OTel-native, so any OTel GenAI or OpenInference instrumentation feeds it.
  - **Gotcha for us (dated today):** on Cloud, **trace-level LLM-as-judge evaluators stop producing results after
    16 Nov 2026**. Use observation-level evaluators.
    https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge
- **Claude:** yes. Anthropic is a native adapter for LLM Connections, used by the playground and by LLM-as-judge.
  https://langfuse.com/docs/administration/llm-connection
  - The judge model should support structured output.
  - Online evaluators run on live production observations and also score dataset experiments.
- **Local, no sign-in:** no, not really. Cloud needs an account, which we already have. Self-hosting needs Docker, which
  free Colab does not have. The local UI asks you to create a user on first visit [my understanding; unverified].
- **Adoption:**
  - SO 2026: 15.2% (tied with MLflow; 2nd among AI-specific tools after LangSmith). SO 2025: 8.8%.
  - 37.5k GitHub stars, the most of any LLM observability repo [measured]. 30.4M PyPI downloads/month [measured].
  - "Trusted by 21 of the Fortune 50 and 129 of the Fortune 500" [vendor; older pages say 19 and 63]:
    https://langfuse.com/press
  - HackerNoon counted 32,778 stars on 10 Aug 2026:
    https://hackernoon.com/two-acquisitions-deep-two-still-standing-whats-really-happening-to-open-source-llm-observability

**LangSmith** (LangChain, https://smith.langchain.com)
- **What:** a closed-source observability, evals and deployment platform. Framework-agnostic, but it fits LangChain and
  LangGraph best.
- **OSS:** no; only the SDKs are open (MIT).
  - The SDK repo was archived and split into langchain-ai/langsmith-python and langsmith-javascript (Oct/Nov 2026):
    https://github.com/langchain-ai/langsmith-sdk
  - The open-source `openevals` and `agentevals` (trajectory evaluators) libraries exist, but I did not verify them this
    pass [unverified].
- **Self-host:** Enterprise add-on only. https://docs.langchain.com/langsmith/self-hosted-changelog/index.html
- **Pricing:** Developer $0 (1 seat, 5k traces, 14-day retention). Plus $39 per seat per month. Enterprise custom,
  metered in "LSUs" (https://www.langchain.com/enterprise-pricing, updated 1 Oct 2026). [secondary for the seat price]
- **Claude:** yes as a model. LangSmith also added TypeSafe's "Jev" non-generative judge model in Sept 2026:
  https://www.langchain.com/blog/jev-is-now-available-in-langsmith-evals
- **Local, no sign-in:** no.
- **Adoption:** SO 2026 17.3%, the highest AI-specific tool (12.5% in 2025). `langsmith` gets 91.9M PyPI downloads/month,
  inflated because langchain depends on it [measured].

**Arize Phoenix** (https://phoenix.arize.com)
- **What:** open-source tracing (OpenInference/OTel), evals, datasets, experiments and a prompt playground. The commercial
  product is Arize AX.
- **OSS:** source-available, Elastic License 2.0, which is not OSI open source.
- **Self-host:** yes. `pip install arize-phoenix && phoenix serve` starts a UI on localhost:6006 with no account. In a
  notebook, `px.launch_app()` works, and the docs say Colab is supported:
  https://arize.com/docs/phoenix/environments.md. Persist data with SQLite (`use_temp_dir=False`) or Postgres.
- **Pricing:** OSS is free. AX Free covers 25k spans; AX Pro is $50/mo [secondary, markaicode].
- **Versions:** 21.0.0 (30 Oct 2026), Python 3.11–3.15.
- **Claude:** yes. `phoenix.evals.LLM(provider="anthropic", model=...)` works with `create_classifier` and
  `evaluate_dataframe`. https://arize.com/docs/ax/integrations/llm-providers/anthropic/anthropic-evals
- **Adoption:** "Arize AI" 5.8% in SO 2026 (3.7% in 2025). 12.3k stars. Arize raised a $70M Series C (Feb 2025)
  [HackerNoon]. The course's old L10 already used it.

**MLflow (3.x) tracing and GenAI evaluation** (https://mlflow.org)
- **What:** the Linux Foundation / Databricks MLOps platform. Version 3 adds OTel-compatible tracing, `mlflow.genai.evaluate`,
  LLM judges (`make_judge`, built-in scorers, agent-as-a-judge over `{{ trace }}`), a prompt registry and feedback.
- **OSS:** Apache-2.0.
- **Self-host:** yes. `mlflow ui` or `mlflow server` uses a local file or SQLite store, with no account.
- **Pricing:** free; managed on Databricks.
- **Version:** 3.18.0 (3 Nov 2026), Python >=3.10.
- **Claude:**
  - Tracing: `mlflow.anthropic.autolog()`. It also traces the Claude Agent SDK (MLflow >=3.5; only `ClaudeSDKClient`
    calls are traced) and Claude Code. https://mlflow.org/docs/3.5.0/genai/tracing/integrations/listing/claude_code
  - Judges: `model="anthropic:/claude-..."`. The **default judge is OpenAI**, so you must override it.
    https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/make-judge
- **Local, no sign-in:** yes. On Colab the UI needs a tunnel or port proxy [unverified for 2026 Colab].
- **Adoption:** SO 2026 15.2% (tied with Langfuse). 28.8k stars. 21.4M downloads/month [measured].

**Datadog Agent Observability (formerly LLM Observability)**
- **What:** a commercial SaaS that is part of Datadog APM.
- **Pricing:** per LLM span, roughly $7.50–9 per 10k LLM spans, with retention billed separately; tool and agent spans are
  reportedly free [secondary]. https://www.truefoundry.com/blog/datadog-llm-observability-pricing,
  https://www.beri.net/article/datadog-vs-arize-vs-langsmith-llm-observability-comparison
- **OTel:** ingests GenAI semconv 1.37+ and OpenInference.
- **Claude:** yes as a traced provider.
- **Local:** no.
- **Adoption:** SO 2026 11.9%. The Datadog State of AI Engineering 2026 report draws on telemetry from 1,000+ customers.
  It reports that agent-framework use roughly doubled year on year, that OpenAI holds a 63% provider share, and that
  Anthropic adoption rose 23 percentage points [secondary write-ups]. https://www.datadoghq.com/state-of-ai-engineering/

**W&B Weave** (https://wandb.ai/site/weave)
- **What:** tracing and evals inside Weights & Biases. CoreWeave acquired W&B (completed 5 May 2025)
  [secondary: https://www.developersdigest.tech/blog/llm-observability-acquisitions-2026].
- **OSS:** the client is Apache-2.0. The server is the W&B SaaS or self-managed W&B (enterprise).
- **Local, no sign-in:** no. `weave.init` needs a W&B API key. https://docs.wandb.ai/weave/guides/core-types/env-vars
- **Claude:** yes (Anthropic integration).
- **Adoption:** SO 2026 "Weights & Biases" 10.7% (this likely includes non-Weave use).

**Comet Opik** (https://www.comet.com/docs/opik)
- **OSS:** Apache-2.0.
- **Self-host:** yes, via Docker Compose (UI on localhost:5173, `opik configure --use_local`, no user management). Docker
  is required, so it does not run on Colab. https://www.comet.com/docs/opik/self-host/local_deployment
- **Pricing:** Cloud free tier 25k spans; Pro $19/mo.
- **Claude:** yes.
- **Adoption:** SO 2026 3.7%. 23.4k stars. 2.67M downloads/month. Named in the Gartner 2026 Market Guide [vendor].

**Pydantic Logfire** (https://pydantic.dev/logfire)
- **OSS:** the OTel SDK is MIT; the server and UI are closed. Self-hosting is Enterprise only.
- **Pricing:** free 10M spans/month; Team $49; Growth $249 (from Jan 2026). https://pydantic.dev/articles/logfire-pricing-change
- **Local, no sign-in:** no.
- **Claude:** yes (instrument_anthropic).
- **Adoption:** 18.4M downloads/month, partly pulled in by pydantic-ai. On the Gartner Peer Insights trending list.

**Braintrust** (https://braintrust.dev)
- **What:** a closed platform that is evals-first, with tracing, a playground and datasets.
- **Funding:** $80M Series B, Feb 2026, at an $800M post-money valuation, led by Iconiq.
  https://www.axios.com/pro/enterprise-software-deals/2026/02/17/ai-observability-braintrust-80-million-800-million
- **Pricing:** Starter $0; Pro $249/mo.
- **Local:** `Eval(..., no_send_logs=True)` or `braintrust eval --no-send-logs` runs locally and prints a summary, but there
  is no local UI. https://braintrust.dev/docs/core/experiments/run
- **Claude:** yes as a task model. `autoevals` LLM scorers default to OpenAI; using them with Claude needs configuration
  [unverified].
- **Adoption:** SO 2026 5.8%. Named customers include Notion, Replit, Cloudflare, Ramp, Dropbox, Vercel, Navan and BILL
  [vendor, via https://geo.sig.ai/brands/braintrust.md].

**Others to mention briefly**
- **Helicone** (Mintlify, Mar 2026; maintenance mode): https://www.helicone.ai/blog/joining-mintlify
- **OpenLLMetry/Traceloop** (ServiceNow, Mar 2026; stays Apache-2.0): https://www.traceloop.com/blog/traceloop-is-joining-servicenow
- **Galileo** (Cisco/Splunk, closed 22 May 2026): https://www.cisco.com/site/us/en/about/corporate-development/acquisitions/galileo/index.html
- **Respan** (formerly Keywords AI; $5M seed, Mar 2026; 5.6% in SO 2026): https://www.respan.ai/blog/introducing-respan
- **LangWatch**, **Laminar**, **HoneyHive**, **Openlayer**, **Agenta**.

### 3.2 Evals (offline, judge, CI, online, agent and trajectory)

**DeepEval** (Confident AI, https://deepeval.com)
- **What:** a pytest-style evaluation framework. It provides `LLMTestCase`, `assert_test` and `deepeval test run`, and its
  failing metrics produce a non-zero exit code, which makes a CI gate.
  - Metrics: GEval and DAG custom judges, RAG metrics, conversational metrics, and agent metrics. The agent metrics include
    **ToolCorrectnessMetric**, which is deterministic name, argument and order matching and needs no LLM unless you pass
    `available_tools`. There is also ArgumentCorrectness and TaskCompletion.
    https://deepeval.com/docs/metrics-tool-correctness
- **OSS:** Apache-2.0. The Confident AI cloud is optional: there is no login unless you call `deepeval login`.
- **Version:** 4.3.4 (11 Nov 2026), Python 3.10–3.x.
- **Claude:** yes. `from deepeval.models import AnthropicModel`, or set `USE_ANTHROPIC_MODEL=1` and pass a model name.
  https://deepeval.com/integrations/models/anthropic. Pin the exact model id.
- **Local, no sign-in:** yes, in a terminal or on Colab. There is no web UI unless you use Confident AI.
- **Adoption:** SO 2026 5.8%. 19.5k stars. 3.2M downloads/month [measured]. Confident AI cloud is listed separately at 3.8%.
- **Note:** the DeepEval site promotes "JevEval" (Jev-as-a-judge, TypeSafe AI's commercial classifier model, Sept 2026). We
  don't need it.

**promptfoo** (https://www.promptfoo.dev)
- **What:** a YAML/CLI eval runner and red-teamer.
  - It compares prompts and models side by side with assertions (deterministic, `llm-rubric`, `factuality`, JS/Python).
  - It has a local web viewer (`promptfoo view`), a GitHub Action for CI, and `promptfoo redteam` (section 3.4).
- **OSS:** MIT. OpenAI announced its acquisition on 9 Mar 2026 and says it will stay open source under the current licence.
  https://openai.com/blog/openai-to-acquire-promptfoo, https://www.techcrunch.com/2026/03/09/openai-acquires-promptfoo-to-secure-its-ai-agents/
- **Version:** npm 0.125.1; needs **Node >=22.22**. Colab's preinstalled Node is probably older, so install Node 22
  first [unverified]. The PyPI `promptfoo` 0.2.0 package is only a thin wrapper.
- **Claude:** yes. `anthropic:messages:<model>` providers. **If only `ANTHROPIC_API_KEY` is set, model-graded assertions
  automatically use Anthropic as the grader.** https://www.promptfoo.dev/docs/providers/anthropic/
- **Local, no sign-in:** yes. "The open-source eval runner runs on your machine" and results are stored locally
  (https://www.promptfoo.dev/docs/faq/). Turn telemetry off with `PROMPTFOO_DISABLE_TELEMETRY=1`.
- **Adoption:**
  - SO 2026 5.3%. 27.2k stars. **4.63M npm downloads per month** [measured].
  - "Used by more than 25% of the Fortune 500" [vendor, repeated in the acquisition coverage].
  - **OpenAI's deprecations page tells Evals users "Migrate to Promptfoo"**: https://developers.openai.com/api/docs/deprecations.md

**Inspect AI** (UK AI Security Institute and Meridian Labs, https://inspect.aisi.org.uk)
- **What:** a research-grade eval framework built from Task, Dataset, Solver and Scorer.
  - Agent evals use a built-in `react()` agent with bash, python, web and computer tools, plus MCP tools and multi-agent
    setups. It can also run external agents: Claude Code, Codex CLI, Gemini CLI.
  - Sandboxes: Docker, Kubernetes, Modal and others.
  - `inspect view` is a local log and transcript viewer.
  - Inspect Evals offers 200+ ready-made benchmarks.
- **OSS:** MIT.
- **Version:** 0.3.290 (14 Nov 2026), Python >=3.11.
- **Claude:** yes, as a first-class provider (`anthropic/<model>`).
- **Local, no sign-in:** yes.
- **Adoption:**
  - 3.25M downloads/month [measured] despite only 3.3k stars.
  - Used by government AI institutes. METR and Apollo reportedly moved onto it [secondary: https://aicoolies.com/reviews/inspect-ai-review].
  - Claims that "Anthropic and DeepMind use it" come only from a personal blog [unverified].
  - Anthropic's open-source auditing tool **Petri** is built on Inspect (section 3.4).
- **Best for:** capability, safety and agentic task evals with sandboxes. Heavier than DeepEval for product regression tests.

**Ragas** (https://github.com/vibrantlabsai/ragas)
- **What:** RAG metrics such as faithfulness, context precision and recall, plus some agent and tool-call metrics.
- **OSS:** Apache-2.0.
- **Status:** 0.4.4 (14 Nov 2026). The repo moved from explodinggradients to vibrantlabsai (a rebrand). One blog claimed
  there had been no commits since Feb 2026, but my measured data (a push on 14 Nov and a release on 14 Nov) contradicts it:
  https://ecorpit.com/rag-evaluation-tools-ragas-deepeval-braintrust-giskard-2026/ [that claim is wrong as of today].
  The same blog mentions CVE-2026-6587 in the multimodal faithfulness module [unverified].
- **Claude:** yes, through LangChain or LiteLLM wrappers.
- **Adoption:** SO 2026 4.9%. 16.3k stars. 1.23M downloads/month.
- **Use in our course:** for retrieval (L3), not as the main agent eval.

**OpenAI Evals (platform) and AgentKit**
- **What it was:** the Oct 2025 AgentKit launch added datasets, trace grading and automated prompt optimisation to the
  OpenAI Evals platform.
- **Status:** **deprecated 3 Jun 2026; it goes read-only, then shuts down 30 Nov 2026. OpenAI's recommended replacement is
  Promptfoo.** Agent Builder and reusable prompts shut down on the same date.
  https://developers.openai.com/api/docs/deprecations.md, https://openai.com/index/introducing-agentkit/
- **The old OSS repo:** openai/evals (19.7k stars) is dormant (last PyPI release 2024).
- **Claude:** no (it is OpenAI-only). **Do not teach it as a tool, but it makes a good story slide.**

**Online evals on production traffic.** The common pattern in 2026 is LLM-as-judge or code evaluators attached to live
traces, with sampling. Tools that do this:
- Langfuse (observation-level evaluators; code evaluators)
- LangSmith (online evaluators)
- Phoenix and Arize AX
- Braintrust (online scoring)
- Datadog
- MLflow (production monitoring)

Per LangChain's survey, 37.3% of all respondents run online evals and 44.8% of teams in production do.

**Agent and trajectory evals, briefly:**
- DeepEval ToolCorrectness and ArgumentCorrectness.
- LangSmith `agentevals` trajectory match [unverified this pass].
- MLflow agent-as-judge over `{{ trace }}`.
- Inspect for full sandboxed tasks.
- Langfuse and Phoenix evaluators over tool-call observations.
- Pass^k reliability, i.e. running each task k times, comes from tau-bench and is taught by hand.

### 3.3 Guardrails

Practice in 2026 has two layers:
- **Deterministic policy in code at the tool boundary.** This covers identity, limits, approvals and allow/deny lists. It is
  where agent security actually lives (OWASP ASI02, ASI03, LLM03 Excessive Agency).
- **Model-based detectors.** These cover prompt injection, PII and content safety, used as defence in depth. Detectors can
  be bypassed. One study bypassed NeMo's jailbreak detector with character injection at 72.5% average attack success rate
  [secondary: https://rubinlake.com/pl/technology-radar/ai-security-and-governance/nemo-guardrails], and
  https://arxiv.org/pdf/2504.11168 shows evasion against several injection classifiers.

**Framework-native guard hooks** (the most-used kind in practice, and they need no extra product):
- **Claude Agent SDK.** Permission processing order: PreToolUse hook → deny rules → allow rules → ask rules → permission
  mode → `canUseTool` → PostToolUse. Put hard denies in **PreToolUse hooks**: `canUseTool` is skipped by allow rules and
  bypass modes. https://docs.claude.com/en/api/agent-sdk/permissions, https://code.claude.com/docs/en/agent-sdk/hooks,
  https://arcjet.com/learn/canusetool-is-not-a-policy-gate [vendor opinion, consistent with the docs].
- **LangChain v1 middleware:** `PIIMiddleware` (redact, mask or block) and `HumanInTheLoopMiddleware` (approve, edit or
  reject per tool). https://docs.langchain.com/oss/python/langchain/guardrails
- **OpenAI Agents SDK:** input, output and tool guardrails with tripwires. It works with non-OpenAI models via LiteLLM.
  Its tracing goes to OpenAI by default unless you replace the processors.
  https://openai.github.io/openai-agents-python/guardrails/

**NeMo Guardrails** (NVIDIA, https://docs.nvidia.com/nemo/guardrails/latest/)
- **What:** programmable rails in Colang 1/2 plus YAML: input, output, dialog, retrieval and execution rails.
  - Built-in self-check input and output rails.
  - Jailbreak heuristics and a NemoGuard JailbreakDetect model.
  - Nemotron Safety Guard content-safety models.
  - Presidio-based PII.
  - The newer IORails engine runs rails in parallel, and tool-call validation arrived in 0.23 [secondary, unverified].
- **OSS:** Apache-2.0.
- **Version:** 0.24.1 (16 Sep 2026), Python 3.10–3.13, so it works on Colab 3.12.
- **Claude:** yes. Engine `anthropic`, but in the current docs the LangChain path is **opt-in**: set
  `NEMOGUARDRAILS_LLM_FRAMEWORK=langchain` and `pip install langchain langchain-anthropic`.
  https://docs.nvidia.com/nemo/guardrails/latest/about-nemo-guardrails-library/supported-llms.md
- **Local, no sign-in:** yes for LLM-based self-check rails, Presidio and the heuristics. The NemoGuard and Nemotron models
  need NIM or a GPU, or an NVIDIA API key.
- **Adoption:** 7.5k stars and 0.48M downloads/month [measured]. NVIDIA-backed, and it ships inside NVIDIA's NeMo
  microservices.

**Guardrails AI** (https://guardrailsai.com)
- **What:** output validation. It provides a `Guard` with validators from the Guardrails Hub (PII, toxic language, regex,
  JSON schema, competitor checks and others) and structured output via Pydantic.
- **OSS:** Apache-2.0.
- **Version:** 0.11.0 (Aug 2026), Python 3.10–3.13.
- **Claude:** yes (via LiteLLM).
- **Local, no sign-in: partly.** Installing Hub validators needs a **free Hub API key** (`guardrails configure --token`).
  https://guardrailsai.com/guardrails/docs/faq.md, https://hub.guardrailsai.com/keys. That is a sign-in for every student.
- **Adoption:** 7.6k stars, 0.12M downloads/month [measured]; lower momentum than NeMo.

**Model-based injection, PII and safety detectors** (all local on Colab CPU or GPU):
- **Llama Prompt Guard 2** (86M mDeBERTa and 22M), from Meta.
  - It is gated on Hugging Face under the Llama 4 Community License, so each student needs to accept the terms and run
    `hf auth login` (a free HF account). It is also served on Groq.
  - https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M, https://docs.mozilla.ai/any-guardrail/api-reference/index/prompt-injection/prompt-guard
- **Llama Guard 4** (12B content-safety classifier) and **LlamaFirewall** (PromptGuard 2 + AlignmentCheck + CodeShield).
  LlamaFirewall is Meta's agent-guard framework (https://arxiv.org/pdf/2505.03574), but its `llamafirewall` package has
  not been updated since May 2025 [measured].
- **ProtectAI `deberta-v3-base-prompt-injection-v2`.** It is ungated (Apache), which makes it the easiest classifier to
  use in a Colab demo. It is not trained on jailbreaks (arXiv 2504.11168), and its parent project LLM Guard is archived.
  The model availability on HF is [unverified this pass].
- **Microsoft Presidio** for PII: 6.0M downloads/month [measured]. NeMo, LangChain and LLM Guard all use it under the hood.
- Also: IBM Granite Guardian and OpenAI's open-weight `gpt-oss-safeguard`. I found no 2026 adoption data for either
  [unverified].

**LLM Guard** (Protect AI → Palo Alto Networks Prisma AIRS)
- The **GitHub repo is archived** (read-only; last push 8 Jul 2026) [measured]. The Protect AI deal closed Jul 2025
  (~$634.5M per an aggregator citing an SEC filing):
  https://guptadeepak.com/agent-security/vendor/protect-ai/ [secondary]
- **Do not teach it as a current tool.** Mention it as an example of consolidation.

**OpenAI Guardrails (`openai-guardrails`)**
- A drop-in wrapper around the OpenAI client that adds checks for jailbreak, PII, moderation, hallucination and others.
  MIT, 0.3.6 (Oct 2026).
- It assumes the OpenAI client or an OpenAI-compatible endpoint. I did not verify whether it works with Claude
  [unverified; Anthropic offers an OpenAI-compatible endpoint, untested]. Its LLM-based checks would need a model.
- 0.48M downloads/month [measured]. https://openai.github.io/openai-guardrails-python/quickstart

**Cloud and commercial guardrails** (paid keys, no local mode; mention only):
- **Amazon Bedrock Guardrails** (ApplyGuardrail API, which works with any model including Claude on Bedrock).
  - Content filters $0.15 and PII $0.10 per 1k text units; contextual grounding and Automated Reasoning are billed
    separately [secondary].
  - https://aws.amazon.com/about-aws/whats-new/2024/12/amazon-bedrock-guardrails-reduces-pricing-85-percent
- **Azure AI Content Safety, Prompt Shields** (direct and indirect injection). It is also a PyRIT target. Pricing was not
  checked [unverified].
- **Lakera Guard** (Check Point, announced 16 Sep 2025; the docs are now titled "Check Point AI Guardrails").
  - Free community tier (limits unverified). Gandalf remains free.
  - https://www.itpro.com/business/acquisition/check-point-buys-lakera-to-secure-the-full-enterprise-ai-lifecycle, https://docs.lakera.ai/docs
- **Palo Alto Prisma AIRS** (Protect AI + Portkey gateway), **Cisco AI Defense**, Google Model Armor.
- **Invariant Guardrails** (Snyk acquired Invariant Labs on 24 Jun 2025). The OSS repo has been stale since Jan 2026
  [measured]. https://snyk.io/news/snyk-acquires-invariant-labs-to-accelerate-agentic-ai-security-innovation
- **Tool-call policy proxies for MCP** (AgentGate, AvaKill, Agent-Airlock and others) are new, small and unproven, so do
  not teach them. Policy engines OPA/Rego and Cerbos are reused for agent authorisation.
  https://wal.sh/research/2026-agent-permission-guardrails [secondary]
- **OWASP Agent Control Standard v0.1** (Sept 2026) is a spec for runtime enforcement points and an Agent Bill of Materials.

### 3.4 Red-teaming

**promptfoo redteam** (the same tool as in 3.2)
- **What:** `promptfoo redteam setup` / `init` / `run` / `report`.
  - Plugins cover harms, PII, BOLA/BFLA, excessive agency, prompt extraction, indirect injection, tool discovery and
    others. Strategies include jailbreak, crescendo, GOAT, base64, multilingual and others.
  - It maps to the OWASP LLM and agentic lists and to NIST/MITRE.
- **Data handling** (https://www.promptfoo.dev/docs/red-team/troubleshooting/data-handling/):
  - The target is always evaluated locally.
  - **Without your own model key, attack generation and grading go to `api.promptfoo.app`**, which also receives your email
    for usage tracking. Set `redteam.provider: anthropic:messages:<model>` to grade with Claude, and set
    `PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION=true` or `PROMPTFOO_DISABLE_REMOTE_GENERATION=true` to keep generation
    local.
  - Some strategies are **remote-only** (goat, jailbreak:composite, jailbreak:hydra, jailbreak:meta, likert, gcg and
    others) and produce nothing when remote generation is disabled.
  - An email prompt appears before `redteam generate`; third parties describe it as lead capture with no verification
    [secondary, https://particula.tech/blog/promptfoo-self-hosted-red-teaming-alternatives].
- **Claude:** yes, as both target and grader. Whether it fully supports Claude as the attack generator is
  [unverified; test it before class].
- **Adoption:** see 3.2. Futurum and others frame the OpenAI acquisition around its share of the Fortune 500 [vendor].

**garak** (NVIDIA AI Red Team, https://github.com/NVIDIA/garak)
- **What:** a Python LLM vulnerability scanner. Probes cover prompt injection, jailbreaks (DAN and others), encoding
  attacks, leakage, malware generation, package hallucination, toxicity and more. Detectors are mostly local classifiers
  or string checks. It writes a JSONL and HTML report.
- **OSS:** Apache-2.0.
- **Version:** 0.17.1 (16 Oct 2026), Python >=3.11.
- **Claude:** **yes, there is a native `anthropic` generator.** I checked the 0.17.1 wheel: `garak/generators/anthropic.py`
  reads `ANTHROPIC_API_KEY`. There are also `litellm`, `function` (to wrap your own agent function), `rest` and others
  [measured].
- **Local, no sign-in:** yes; pip-installable on Colab.
- **Adoption:** 10.0k stars, 56k downloads/month [measured].
- **Limits:** it is mostly single-turn and model-centric, not agent- or tool-aware.

**PyRIT** (Microsoft AI Red Team, https://github.com/microsoft/PyRIT)
- **What:** a framework for orchestrated, multi-turn attacks (Crescendo, TAP, Skeleton Key and others), with converters,
  scorers (Likert, refusal and others, which take a chat target as the judge) and memory (in-memory, SQLite, Azure SQL).
  It also has the `pyrit_scan` CLI and `pyrit_shell`.
- **OSS:** MIT.
- **Version:** 1.2.0 (13 Nov 2026), Python 3.11–3.14. The docs recommend 3.13. https://microsoft.github.io/PyRIT/latest/
- **Claude:** yes, via `LiteLLMChatTarget`. The 1.2.0 wheel has `litellm_chat_target.py` but **no native Anthropic target
  class** [measured], although the docs list Anthropic among supported targets.
- **Azure:** not required.
- **Adoption:** 4.9k stars (repo moved from Azure/PyRIT, now archived), 93k downloads/month [measured].

**Petri and Bloom** (Anthropic; now stewarded by Meridian Labs)
- **Petri** is an open-source auditing agent: an auditor model probes a target model over multi-turn scenarios, and a judge
  scores the transcripts. It runs on Inspect and is MIT. Released Oct 2025:
  https://anthropic.com/research/petri-open-source-auditing
- **Bloom** is automated behavioural evals, released 19 Dec 2025: https://www.anthropic.com/research/bloom
- Stewardship moved to Meridian Labs in May 2026:
  https://itbrief.co.uk/story/anthropic-hands-petri-ai-test-tool-to-meridian-labs [secondary]
- **Claude:** native.
- **Positioning:** model-behaviour auditing (deception, power-seeking and similar), not app-level injection testing. Good
  for an "also used" slide.

**Commercial:**
- **Lakera Red** (Check Point).
- **Prisma AIRS AI Red Teaming** (Palo Alto Networks).
- **Mindgard**, **SPLX** (agentic-radar).
- **HiddenLayer**.

---

## 4. The fit matrix (our constraints)

| Area | Tool | Widely used? (evidence) | Free Colab / local, no sign-in | Claude as model or judge |
|---|---|---|---|---|
| Tracing | **Langfuse** | SO26 15.2%; 37.5k stars; 30M dl/mo | Cloud with our keys works from Colab; self-host needs Docker | Yes (native Anthropic adapter for judges) |
| Tracing | Arize Phoenix | SO26 5.8%; 12.3k stars | **Yes** (`px.launch_app()` / `phoenix serve`) | Yes |
| Tracing | MLflow 3 | SO26 15.2%; 21M dl/mo | **Yes** (`mlflow ui`); Colab UI needs a tunnel | Yes (override the OpenAI default) |
| Tracing | LangSmith | SO26 17.3% (top) | No (account) | Yes |
| Tracing | Datadog | SO26 11.9% | No (paid) | Yes |
| Evals | **DeepEval** | SO26 5.8%; 19.5k stars; 3.2M dl/mo | **Yes** (CLI/pytest) | Yes (`AnthropicModel`) |
| Evals | promptfoo | SO26 5.3%; 27k stars; 4.6M npm/mo; OpenAI's migration target | **Yes** (needs Node 22) | Yes; auto-uses Anthropic as grader if only that key is set |
| Evals | Inspect AI | 3.25M dl/mo; AISI | **Yes** (`inspect view`) | Yes (first-class) |
| Evals | Ragas | SO26 4.9% | Yes | Yes (wrapper) |
| Evals | Braintrust | SO26 5.8%; $800M valuation | Local runs, no UI | Partly |
| Evals | OpenAI Evals | shutting down 30 Nov 2026 | n/a | No |
| CI gate | **pytest + DeepEval in GitHub Actions** | standard pytest; DeepEval docs | **Yes** | Yes |
| CI gate | promptfoo GitHub Action | | Yes | Yes |
| Guardrails | **Deterministic code + Claude Agent SDK PreToolUse hooks** | the pattern every framework ships | **Yes** | n/a (code) |
| Guardrails | **NeMo Guardrails** | 7.5k stars; 0.48M dl/mo; NVIDIA | **Yes** (self-check rails, Presidio) | Yes (opt-in LangChain path) |
| Guardrails | Guardrails AI | 7.6k stars; 0.12M dl/mo | Needs a free Hub token | Yes |
| Guardrails | Llama Prompt Guard 2 | Meta; used inside LlamaFirewall | Needs a free HF login (gated) | n/a (classifier) |
| Guardrails | LLM Guard | archived Jul 2026 | (works, but archived) | n/a |
| Guardrails | Bedrock / Azure / Lakera | enterprise SaaS | No | Bedrock: Claude on Bedrock |
| Red team | **promptfoo redteam** | as above | Yes, but set the Anthropic provider and disable remote generation, otherwise data goes to promptfoo's API | Yes as target and grader |
| Red team | garak | 10k stars; NVIDIA | **Yes** | **Native anthropic generator** |
| Red team | PyRIT | 4.9k stars; Microsoft | Yes | Via LiteLLM |
| Red team | Petri | Anthropic → Meridian | Yes (Inspect) | Native |

---

## 5. Recommended teaching stack (L6, 21 Nov 2026)

Rule used: (1) industry adoption with evidence, (2) runs on free Colab or a laptop without new sign-ups, (3) works with
only an Anthropic key.

| Area | Flagship | Why (evidence) | Also used: mention |
|---|---|---|---|
| **Tracing / observability** | **Langfuse** (Cloud, our keys; SDK 5.x on OTel) | (a) Most-starred open LLM observability repo (37.5k) with 30M monthly downloads. (b) SO 2026 15.2%, nearly doubled from 8.8% in 2025, tied 2nd among AI-specific tools. (c) MIT and self-hostable, which answers Henrik's "no lock-in" (now ClickHouse-backed). (d) Native Anthropic adapter, so the same tool does **online LLM-as-judge on live traces**. (e) Reads the OTel GenAI names we teach. | **Phoenix** as the local, no-account second viewer of the same OTLP spans (ELv2; Colab-supported). **LangSmith** (top in SO 2026, closed). **MLflow 3** (SO 15.2%, fully local). **Datadog**. W&B Weave. Logfire. Opik. |
| **Evals (offline, judge, trajectory)** | **DeepEval** with **Claude as the judge** (`AnthropicModel`) | (a) The most-adopted open-source eval library in SO 2026 (5.8%, tied with Braintrust and ahead of promptfoo and Ragas). (b) 19.5k stars, 3.2M monthly downloads. (c) pytest-native, so it is the CI gate too. (d) `ToolCorrectnessMetric` is deterministic: it checks tool names, arguments and order, which is our "never confirm=true before a yes" trajectory check. GEval for words. (e) Runs on Colab with no account. | **promptfoo** for side-by-side prompt and model comparison. **Langfuse datasets and experiments** (the managed version). **Inspect AI** for sandboxed agent tasks (AISI). **Ragas** for retrieval (L3). Braintrust (closed; $800M valuation). OpenAI Evals: shutting down 30 Nov 2026, users told to migrate to Promptfoo. |
| **CI regression gate** | **pytest + DeepEval in GitHub Actions** (a required check; a non-zero exit blocks the merge) | Plain pytest is what every enterprise CI already runs. No vendor account. Replay mode keeps CI free. | promptfoo GitHub Action. Braintrust CI. LangSmith pytest plugin [unverified]. |
| **Online evals** | **Langfuse observation-level evaluators** with an Anthropic LLM Connection, plus code evaluators | 37.3% of teams run online evals (44.8% in production) per LangChain. We already have Langfuse. Note: trace-level evaluators are retired on Cloud **after 16 Nov 2026**, so build observation-level ones. | Phoenix/AX online evals, LangSmith, Braintrust, Datadog. |
| **Guardrails** | **Deterministic guards in code at the tool boundary** (Claude Agent SDK **PreToolUse** hook, or our own wrapper) **+ NeMo Guardrails** for model-based input and output rails | (a) Tool-boundary code is the pattern every major framework ships: Claude Agent SDK hooks, LangChain HITL/PII middleware, OpenAI Agents SDK tool guardrails. It is the only guard that cannot be talked out of a decision (OWASP ASI02, ASI03, LLM03). (b) NeMo is the most-downloaded open guard framework (0.48M/mo vs Guardrails AI 0.12M). It is Apache-2.0 and NVIDIA-backed, runs on Colab 3.12 and works with Claude. | **Llama Prompt Guard 2** (gated; needs HF login) or the ProtectAI DeBERTa classifier as the injection detector. **Presidio** for PII. **Guardrails AI** (needs a Hub token). **Bedrock Guardrails**, **Azure Prompt Shields**, **Lakera (Check Point)**, **Prisma AIRS**. LLM Guard is **archived**. LlamaFirewall. OpenAI Guardrails. |
| **Red-teaming** | **promptfoo redteam** with Claude as grader (`redteam.provider: anthropic:messages:...`; remote generation disabled; telemetry off) | (a) The most-adopted open red-team tool: 27k stars, 4.6M npm downloads/month, vendor-claimed 25% of the Fortune 500. (b) Agent-aware plugins (excessive agency, BOLA, indirect injection) map to OWASP. (c) OpenAI bought it and points its own Evals users to it. (d) The same tool as the eval comparison, so students learn one config. | **garak** (Python, native Anthropic generator, NVIDIA; the easiest fully-local scan). **PyRIT** (Microsoft; multi-turn Crescendo/TAP; Claude via LiteLLM). **Petri** (Anthropic's auditing agent on Inspect). Lakera Red, Prisma AIRS Red Teaming. |

**Risks to check in rehearsal** (before 21 Nov):
1. **promptfoo needs Node >=22.22.** Colab's preinstalled Node is likely older, so install it in the notebook or run the red
   team from the instructor laptop or Modal. Also confirm which plugins produce attacks once remote generation is off with
   Claude as the provider. If coverage drops too much, run **garak** with `--target_type anthropic` as the Colab-friendly
   fallback.
2. **Langfuse evaluators:** create the Anthropic LLM Connection and confirm the chosen Claude model passes the
   structured-output test request when the evaluator is saved. Use **observation-level** evaluators.
3. **NeMo + Claude:** set `NEMOGUARDRAILS_LLM_FRAMEWORK=langchain` and install `langchain-anthropic`.
4. **Prompt Guard 2 gating:** either pre-download it to the course bucket (check that the licence allows redistribution;
   it is the Llama 4 Community License) or use an ungated classifier in the student notebook.
5. **MLflow, Phoenix and DeepEval default judges are OpenAI.** Always pass the Claude model explicitly. Pin exact model ids:
   the promptfoo docs list current ids such as `claude-sonnet-5`, `claude-opus-5-5` and `claude-haiku-4-5`.

---

## 6. Acquisitions and status changes, 2025–2026 (for the "check before you adopt" slide)

| Date | Event | Status of the open-source part | Source |
|---|---|---|---|
| Jun 24, 2025 | Snyk acquires Invariant Labs | invariant repo stale since Jan 2026 [measured] | https://snyk.io/news/snyk-acquires-invariant-labs-to-accelerate-agentic-ai-security-innovation |
| May 5, 2025 (closed) | CoreWeave acquires Weights & Biases (Weave) | Weave client Apache-2.0 | https://www.developersdigest.tech/blog/llm-observability-acquisitions-2026 |
| Jul 2025 (closed) | Palo Alto Networks acquires Protect AI → Prisma AIRS | **LLM Guard archived (last push 8 Jul 2026)** [measured] | https://guptadeepak.com/agent-security/vendor/protect-ai/ |
| Sep 8, 2025 | Humanloop platform sunset; team joins Anthropic | no product | https://www.developersdigest.tech/blog/llm-observability-acquisitions-2026 |
| Sep 16, 2025 | Check Point acquires Lakera (Guard, Red, Gandalf) | closed product; Gandalf free | https://www.itpro.com/business/acquisition/check-point-buys-lakera-to-secure-the-full-enterprise-ai-lifecycle |
| Jan 16, 2026 | ClickHouse acquires Langfuse | MIT, self-hostable, "no licensing changes planned" | https://langfuse.com/blog/joining-clickhouse |
| Mar 3, 2026 | Mintlify acquires Helicone | maintenance mode | https://www.helicone.ai/blog/joining-mintlify |
| Mar 9, 2026 | OpenAI to acquire Promptfoo | stays open source (MIT) | https://openai.com/blog/openai-to-acquire-promptfoo |
| Mar 2026 (closed ~May 5) | ServiceNow acquires Traceloop (OpenLLMetry) | OpenLLMetry stays Apache-2.0 | https://www.traceloop.com/blog/traceloop-is-joining-servicenow |
| Apr 9 → May 22, 2026 | Cisco acquires Galileo (into Splunk) | commercial | https://www.cisco.com/site/us/en/about/corporate-development/acquisitions/galileo/index.html |
| Apr 30 → May 29, 2026 | Palo Alto Networks acquires Portkey (AI gateway for Prisma AIRS) | closing reported by one outlet | https://nand-research.com/palo-alto-networks-portkey-acquisition-anchors-its-agentic-security-stack/ |
| May 2026 | Anthropic hands Petri (and Bloom) to Meridian Labs | MIT | https://itbrief.co.uk/story/anthropic-hands-petri-ai-test-tool-to-meridian-labs |
| Jun 3 → Nov 30, 2026 | **OpenAI deprecates Evals, Agent Builder and reusable prompts** | Evals → "Migrate to Promptfoo" | https://developers.openai.com/api/docs/deprecations.md |
| 2026 | WhyLabs discontinues operations (platform open-sourced) | | https://markaicode.com/facts/llm-observability-tools/ |
| Feb 2026 | Keywords AI rebrands as Respan | | https://www.respan.ai/blog/introducing-respan |
| Feb 2026 | Braintrust $80M Series B at $800M | | https://siliconangle.com/2026/02/17/braintrust-breaks-80m-series-b-funding-round-become-observability-layer-ai/ |

A good roundup of all of this: https://www.developersdigest.tech/blog/llm-observability-acquisitions-2026 (18 Oct 2026)
[secondary]. Patronus AI's homepage reportedly no longer shows an eval product (same source; unverified).

---

## 7. Market-size and survey context (use with caveats)

- **LLM observability platform market:** $2.69B in 2026, rising to $9.26B by 2030 (The Business Research Company, via
  https://www.morphllm.com/llm-observability-tools) [secondary; a single analyst estimate].
- **Stack Overflow 2026:** 30,000+ respondents. Claude Code is the most-used agent (66%), then GitHub Copilot (59%). Only
  20% use AI to deploy or operate production systems. https://stackoverflow.blog/2026/10/06/the-results-of-the-2026-developer-survey-are-here/
- **Stack Overflow 2026 orchestration:** LangChain 30%, OpenAI Agents SDK 24%. https://survey.stackoverflow.co/2026/ai
- **Datadog State of AI Engineering 2026:** about 1 in 20 AI requests fail in production, and capacity limits are the main
  bottleneck. https://itwire.com/business-it-news/data/in-the-rush-to-scale-ai,-operational-limits-are-emerging,-datadog-report-finds.html
- **Comparison and landscape articles** (vendor-influenced; do not cite their numbers as fact):
  - https://www.marktechpost.com/2026/08/09/top-llm-observability-and-evaluation-platforms-in-2026-langfuse-langsmith-braintrust-arize-and-more-compared/
  - https://laminar.sh/article/top-6-agent-observability-platforms
  - https://grepture.com/blog/llm-observability-tools-comparison
  - https://pub.towardsai.net/the-llm-observability-land-grab-of-2026-477ac3624389

## 8. Things I could not verify (do not put on slides without checking)

- Consumer Colab's default Python in Nov 2026 (the Colab Enterprise docs say 3.12) and its Node version.
- Whether promptfoo red-team attack *generation* fully runs on Claude when remote generation is disabled, and which plugins
  then produce zero tests.
- Whether OpenAI Guardrails works with Claude through Anthropic's OpenAI-compatible endpoint.
- The exact 2026 OWASP LLM Top 10 codes: they come from the CSA note; check the PDF on genai.owasp.org.
- Lakera's free-tier limits after the Check Point deal. Portkey's close date.
- LangSmith `agentevals` and `openevals` current status. Granite Guardian and gpt-oss-safeguard adoption.
- Claims that Anthropic and DeepMind use Inspect internally.
- NeMo Guardrails 0.21 "IORails" and 0.23 tool-call validation release details.
