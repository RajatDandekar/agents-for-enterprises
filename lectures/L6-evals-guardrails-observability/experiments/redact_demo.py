"""What the tracer's redact= hook does to one message before it leaves the process (Presidio; no model call).
Writes logs/redact_demo.json: the text as typed, the text as the trace holds it, what was found, how long it took."""
import json

from _common import write

from ledgerline.course.l6.guards import redact

before = "Voltway wants a deposit. My company card is 4929 1234 5678 9012, expiry 09/28. Note it on the usual request."
redact("warm up")                                    # the first call loads the models
after, found, ms = redact(before)
out = {"before": before, "after": after, "found": found, "ms": ms, "tool": "presidio-analyzer 2.2.366 + spaCy en_core_web_sm"}
write("redact_demo.json", out)
print(json.dumps(out, indent=1))
