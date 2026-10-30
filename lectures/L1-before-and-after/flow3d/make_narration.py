"""Narrate the 3D slide in Rajat's cloned voice (ElevenLabs), one mp3 per stage.

    python3 lectures/L1-before-and-after/flow3d/make_narration.py

Reads flow3d/narration.json (text = what is said, say = the same words spelled for the voice), first checks that every
number the script quotes is in flow3d/trace.json, then writes flow3d/audio/stage-XX.mp3 and fills in each stage's
duration. A clip whose words, voice and settings are unchanged is not synthesized again. Light HTTP only, so it runs
on the laptop. The key is read from the env file and never printed.
"""
import base64
import hashlib
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
KEY_FILE = "/Users/raj/Claude_Brain/cobol-mainframes/.env"
SETTINGS = {"stability": 0.5, "similarity_boost": 0.8, "style": 0.1, "use_speaker_boost": True}  # as pods-videos/pipeline/tts.py


def api_key():
    for line in open(KEY_FILE):
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("ELEVENLABS_API_KEY not found")


def check_facts(nar, trace):
    """Every number the narration quotes must come from the recorded run."""
    cs = trace["context_split"]
    tools = [e for tu in trace["turns"] for e in tu["events"] if e["kind"] == "tool"]
    llm = [e for tu in trace["turns"] for e in tu["events"] if e["kind"] == "llm"]
    t1 = trace["turns"][0]["events"]
    stock = next(e for e in tools if e["name"] == "check_stock" and e["result"].get("ok"))
    refusal = next(e for e in tools if e["name"] == "create_purchase_order" and e["result"].get("ok") is False)
    preview = next(e for e in tools if e["name"] == "create_purchase_request" and e["result"].get("preview"))
    commit = next(e for e in tools if e["name"] == "create_purchase_request" and e["args"].get("confirm") is True)
    facts = {
        1: [], 2: [(cs["system"], "196"), (cs["history"], "11"), (cs["schemas"], "1,932"), (cs["total"], "2,139")],
        3: [(llm[0]["tokens_in"], "2,139"), (llm[0]["tool_calls"][0]["name"], "find_item"), (llm[0]["tokens_out"], "21"),
            (llm[0]["seconds"] < 3, "under three seconds"), (llm[0]["tool_calls"][0]["arguments"]["query"], "city e-bike battery pack")],
        5: [(len(tools[0]["services"]), "eleven")], 6: [(llm[1]["tokens_in"], "2,507")],
        8: [([w["on_hand"] for w in stock["result"]["warehouses"]], "5,400 / 1,200"), (stock["result"]["free_total"], "6,600"),
            (stock["result"]["cover_days"], "11")],
        10: [(sum(e["kind"] == "llm" for e in t1), "Five model calls"), (sum(e["kind"] == "tool" for e in t1), "four tool calls")],
        14: [("£50,000" in refusal["result"]["error"] and "£285,600" in refusal["result"]["error"], "£50,000 / £285,600")],
        16: [(preview["result"]["preview"]["estimated_value"], "£273,600"), (preview["result"]["preview"]["approver"], "DOKAFOR")],
        19: [(commit["result"]["request_no"], "PR/2026/04417")], 20: [(commit["result"]["status"], "WAITING FOR APPROVAL")],
    }
    want = {2: [196, 11, 1932, 2139], 3: [2139, "find_item", 21, True, "city e-bike battery pack"], 5: [11], 6: [2507],
            8: [[5400, 1200], 6600, 11], 10: [5, 4], 14: [True], 16: [273600.0, "DOKAFOR"], 19: ["PR/2026/04417"],
            20: ["WAITING FOR APPROVAL"]}
    for k, vals in want.items():
        got = [f[0] for f in facts[k]]
        if got != vals:
            raise SystemExit(f"stage {k}: the narration says {[f[1] for f in facts[k]]} but the trace has {got}")
    if nar["trace_recorded_live"] != trace["meta"]["recorded_live"]:
        raise SystemExit("narration.json was written for another recording of the trace")


def synth(key, voice, model, text, prev_text, next_text):
    body = {"text": text, "model_id": model, "voice_settings": SETTINGS,
            "previous_text": prev_text[-300:], "next_text": next_text[:300]}
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128"
    for attempt in range(4):
        req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                     headers={"xi-api-key": key, "Content-Type": "application/json"})
        try:
            return json.load(urllib.request.urlopen(req, timeout=180))
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise SystemExit(f"ElevenLabs {e.code}: {msg}")


def main():
    nar = json.load(open(HERE / "narration.json"))
    trace = json.load(open(HERE / "trace.json"))
    check_facts(nar, trace)
    (HERE / "audio").mkdir(exist_ok=True)
    key = api_key()
    st = nar["stages"]
    chars = 0
    for i, s in enumerate(st):
        sha = hashlib.sha1((nar["voice_id"] + nar["model"] + json.dumps(SETTINGS) + s["say"]).encode()).hexdigest()
        mp3 = HERE / s["audio"]
        if s.get("sha") == sha and mp3.exists():
            continue
        r = synth(key, nar["voice_id"], nar["model"], s["say"], st[i - 1]["say"] if i else "", st[i + 1]["say"] if i + 1 < len(st) else "")
        data = base64.b64decode(r["audio_base64"])
        mp3.write_bytes(data)
        al = r["alignment"]
        s.update(sha=sha, speech_end=round(al["character_end_times_seconds"][-1], 2),
                 duration=round(len(data) * 8 / 128000, 2), bytes=len(data))
        chars += len(s["say"])
        print(f"stage {i:02d}: {s['duration']:5.1f} s  {s['text'][:60]}", flush=True)
    nar["total_seconds"] = round(sum(s["duration"] for s in st), 1)
    json.dump(nar, open(HERE / "narration.json", "w"), indent=1, ensure_ascii=False)
    print(f"{len(st)} clips, {nar['total_seconds']} s of speech, {chars} characters synthesized this run")


if __name__ == "__main__":
    sys.exit(main())
