"""The Langfuse tour of NB6a, on its own (no model call): sessions, scores, the dataset, the prompt's versions, read
through Langfuse's public API with the course project's keys. Writes logs/nb6a_langfuse_tour.json (what NB6a replays)."""
import json

from _common import write

from ledgerline.course.l6.nbkit import langfuse_tour

t = langfuse_tour()
write("nb6a_langfuse_tour.json", t)
print(json.dumps(t, indent=1, ensure_ascii=False)[:3000])
