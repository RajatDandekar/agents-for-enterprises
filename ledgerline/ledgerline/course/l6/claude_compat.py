"""Current Claude models refuse sampling parameters ("temperature: Extra inputs are not permitted"). Several eval and guard
libraries send one anyway (NeMo Guardrails' self-check, Ragas, some DeepEval paths). strip_sampling() drops temperature,
top_p and top_k from every request the Anthropic SDK builds in this process, whichever library made the call.
(Argus's LLM gateway does the same on the server side, so notebooks that go through the gateway do not need this.)"""


def strip_sampling():
    import anthropic._base_client as B
    if getattr(B.BaseClient, "_l6_stripped", False):
        return
    orig = B.BaseClient._build_request

    def build(self, options, *a, **kw):
        jd = getattr(options, "json_data", None)
        if isinstance(jd, dict):
            for k in ("temperature", "top_p", "top_k"):
                jd.pop(k, None)
        return orig(self, options, *a, **kw)

    B.BaseClient._build_request = build
    B.BaseClient._l6_stripped = True
