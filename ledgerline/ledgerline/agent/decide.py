"""Lecture 4: typed decisions with a confidence.

Some steps in the route are not lookups and not rules, they are judgements:
    "Is this upload a UN 38.3 certificate or a quotation?"
    "Is 'Voltway Polymer Industries' the existing Voltway Cells?"
    "Is Emma placing an order, or asking about the policy?"
    "Did she just say yes to the preview?"

decide() turns each into a TYPED decision: a fixed set of options (an enum), optional typed fields, and a confidence.
When the confidence is below the threshold, the route asks the human instead of guessing.

    d = decide("document_kind", text, k=5)
    d.choice, d.confidence, d.fields, d.sure      # 'quotation', 0.8, {...}, True

Backends. The interface is the one a dedicated decision-model service offers (for example Jev, TypeSafe's public
decision API): a decision name, the options, the input and context in; a choice, typed fields and a confidence out.
    GeminiBackend   structured JSON output from a general model, sampled k times at temperature 1.0; the confidence
                    is the share of samples that agree (self-consistency). This is what the course runs.
    ServiceBackend  a slot for a dedicated service: give it a function that calls your service and returns
                    {"choice", "confidence", ...fields}. We did not have Jev access, so no Jev client ships here and
                    no Jev numbers appear in the course; wire your own client into ServiceBackend to try one.
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable

from ..llm import LLM


@dataclass(frozen=True)
class DecisionSpec:
    name: str
    question: str
    options: tuple
    fields: dict = field(default_factory=dict)  # name -> description (all strings; "" when absent)
    guide: str = ""


SPECS: dict[str, DecisionSpec] = {s.name: s for s in [
    DecisionSpec("intent", "What does the user want from this message?",
                 ("order", "policy_question", "order_status", "stock_question", "other"),
                 guide="order = she wants something bought, reordered or changed in an order, or she is answering a "
                       "question about an order. policy_question = she asks what the rules allow, even if she names "
                       "an item or supplier, and does not ask you to place anything. order_status = she asks about an "
                       "existing PO/PR. stock_question = she asks how much stock or cover there is."),
    DecisionSpec("pick_supplier", "Which existing supplier did the user mean, if any?", (),
                 guide="Pick a candidate only if her words name that company (abbreviations, a dropped or added "
                       "'Industries'/'Pvt Ltd', the same city). If she names a different business, or her words fit "
                       "two candidates equally, answer 'none of these' or the closest with less certainty."),
    DecisionSpec("document_kind", "What has the user given us for the supplier's UN 38.3 certificate?",
                 ("cell_safety_certificate", "quotation", "other_document", "no_document"),
                 {"doc_ref": "the certificate's reference number, exactly as written",
                  "valid_to": "expiry date as YYYY-MM-DD",
                  "issued_to": "the company the certificate is issued to"},
                 guide="A UN 38.3 certificate is issued by a lab or authority, names the supplier, says the material "
                       "is fit for lithium cells and has a reference and an expiry date. A quotation offers prices, "
                       "even when it says the material is battery safety. If she says she has none, or does not give one, "
                       "answer no_document."),
    DecisionSpec("confirmation", "Has the user confirmed the preview shown to her?",
                 ("yes", "no", "change"),
                 guide="yes = she agrees to go ahead as shown. no = she does not want it now. change = she wants "
                       "something different (quantity, date, supplier, cost centre ...)."),
]}


@dataclass
class Decision:
    name: str
    choice: str
    confidence: float
    fields: dict
    votes: dict
    k: int
    threshold: float
    backend: str
    reason: str = ""

    @property
    def sure(self) -> bool:
        return self.confidence >= self.threshold

    def as_dict(self) -> dict:
        return {"name": self.name, "choice": self.choice, "confidence": self.confidence, "sure": self.sure,
                "fields": self.fields, "votes": self.votes, "k": self.k, "threshold": self.threshold,
                "backend": self.backend, "reason": self.reason}


class GeminiBackend:
    """k independent samples of a structured JSON answer; confidence = agreement. Uses the agent's own LLM, so the
    tokens count towards the agent's bill and every sample is recorded in its cassette."""

    name = "gemini self-consistency"

    def __init__(self, llm: LLM | None = None, temperature: float = 1.0):
        self.llm = llm or LLM(cassette="L4_decide")
        self.temperature = temperature

    def sample(self, spec: DecisionSpec, text: str, context: dict, options: tuple, k: int) -> list[dict]:
        props = {"choice": {"type": "string", "enum": list(options)}, "reason": {"type": "string"}}
        props.update({f: {"type": "string", "description": d} for f, d in spec.fields.items()})
        schema = {"type": "object", "properties": props, "required": list(props)}
        rf = {"type": "json_schema", "json_schema": {"name": spec.name, "schema": schema, "strict": True}}
        out = []
        for i in range(k):
            sys = (f"You make one typed decision for a purchasing assistant at Northbridge Cycles, Manchester. Today is "
                   f"Monday 26 October 2026.\nDecision: {spec.question}\n{spec.guide}\nAnswer only with the JSON "
                   f"object; give a one-sentence reason. (Independent judgement {i + 1} of {k}.)")
            user = json.dumps({"options": list(options), "context": context, "input": text}, ensure_ascii=False)
            r = self.llm.chat([{"role": "system", "content": sys}, {"role": "user", "content": user}],
                              response_format=rf, temperature=self.temperature)
            out.append(parse_json(r.content, options))
        return out


class ServiceBackend:
    """A slot for a dedicated decision-model service (Jev or your own). `call` receives
    {"decision", "question", "options", "fields", "input", "context"} and must return
    {"choice": <one of options>, "confidence": <0..1>, ...fields}. One call, no sampling: the service's confidence is used."""

    def __init__(self, call: Callable[[dict], dict], name: str = "decision service"):
        self.call, self.name = call, name

    def sample(self, spec: DecisionSpec, text: str, context: dict, options: tuple, k: int) -> list[dict]:
        r = self.call({"decision": spec.name, "question": spec.question, "options": list(options),
                       "fields": spec.fields, "input": text, "context": context})
        return [{**r, "_confidence": float(r.get("confidence", 0.0))}]


def parse_json(content: str | None, options: tuple) -> dict:
    """Parse a model's JSON answer; anything unparsable becomes an 'invalid' vote (it lowers the confidence)."""
    s = (content or "").strip()
    if s.startswith("```"):
        s = s.strip("`").split("\n", 1)[-1]
    try:
        d = json.loads(s[s.find("{"): s.rfind("}") + 1])
    except (ValueError, TypeError):
        return {"choice": "_invalid", "reason": (content or "")[:120]}
    if d.get("choice") not in options:
        d["choice"] = "_invalid"
    return d


def decide(name: str, text: str, context: dict | None = None, options: tuple | list | None = None, k: int = 5,
           threshold: float = 0.8, backend=None, llm: LLM | None = None) -> Decision:
    """Make the typed decision `name` about `text`. options overrides the spec's (pick_supplier passes candidates)."""
    spec = SPECS[name]
    opts = tuple(options or spec.options)
    be = backend or GeminiBackend(llm)
    samples = be.sample(spec, text, context or {}, opts, k)
    votes = Counter(s["choice"] for s in samples)
    choice, n = sorted(votes.items(), key=lambda kv: (-kv[1], kv[0] == "_invalid", kv[0]))[0]
    conf = samples[0]["_confidence"] if len(samples) == 1 and "_confidence" in samples[0] else round(n / len(samples), 3)
    first = next(s for s in samples if s["choice"] == choice)
    fields = {f: (first.get(f) or "").strip() for f in spec.fields}
    return Decision(name, choice, conf, fields, dict(sorted(votes.items())), len(samples), threshold,
                    getattr(be, "name", type(be).__name__), (first.get("reason") or "")[:200])
