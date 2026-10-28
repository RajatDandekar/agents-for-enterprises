"""DeepEval's judge model, reached through the course's LLM shim, so every judgement is recorded and replays with no key.

    from bahi.course.obs.judges import CassetteJudge
    judge = CassetteJudge("openrouter:openai/gpt-6.1-terra", cassette="IND10_ci_judge")
    GEval(name="Honest status", criteria=..., evaluation_params=[...], model=judge, async_mode=False)

DeepEval calls judge.generate(prompt, schema): the prompt is DeepEval's own rubric text; schema is a pydantic model
it wants back. We ask for JSON in that shape and validate it. Same prompt, same cassette key: replay is exact.
"""
from __future__ import annotations

import json

from deepeval.models import DeepEvalBaseLLM

from ...llm import LLM


class CassetteJudge(DeepEvalBaseLLM):
    def __init__(self, model: str = "openrouter:openai/gpt-6.1-terra", cassette: str = "IND10_ci_judge"):
        self.llm = LLM(model, cassette=cassette, max_tokens=1200)
        self.calls = 0
        super().__init__(model)

    def load_model(self, *a, **kw):
        return self.llm

    def get_model_name(self, *a, **kw):
        return self.llm.model

    def _ask(self, prompt: str, schema=None):
        msgs = [{"role": "user", "content": prompt}]
        if schema is not None:
            msgs.insert(0, {"role": "system", "content": "Reply with one JSON object only, no prose, matching this JSON "
                            "schema:\n" + json.dumps(schema.model_json_schema())})
        r = self.llm.chat(msgs)
        self.calls += 1
        txt = (r.content or "").strip()
        if schema is None:
            return txt
        body = txt[txt.find("{"):txt.rfind("}") + 1] if "{" in txt else txt
        return schema.model_validate_json(body)

    def generate(self, prompt: str, schema=None, *a, **kw):
        return self._ask(prompt, schema)

    async def a_generate(self, prompt: str, schema=None, *a, **kw):
        return self._ask(prompt, schema)

    @property
    def cost_inr(self) -> float:
        return round(sum(r.cost_inr for r in self.llm.log), 4)
