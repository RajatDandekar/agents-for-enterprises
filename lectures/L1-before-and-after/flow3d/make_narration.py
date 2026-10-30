"""Narrate the 3D slide: one mp3 per narrated stage, plus subtitle cues and number-punch times.

    python3 lectures/L1-before-and-after/flow3d/make_narration.py

Reads flow3d/narration.json. Each narrated stage has `text` (shown as subtitles) and `say` (the same sentences,
spelled for the voice); stages with say=null play fast and silent. First it checks that every number the script
quotes is in flow3d/trace.json. Then it writes flow3d/audio/stage-XX.mp3 with the ElevenLabs voice named in
narration.json, and fills in each clip's duration, its subtitle cues (one per sentence, from the character
timings) and the moment its number punches in. Unchanged clips are not synthesized again; clips of stages that
are no longer narrated are deleted. Light HTTP only, so it runs on the laptop. The key is never printed.
"""
import base64
import hashlib
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
KEY_FILE = "/Users/raj/Claude_Brain/cobol-mainframes/.env"
SETTINGS = {"stability": 0.55, "similarity_boost": 0.8, "style": 0.05, "use_speaker_boost": True}


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
    stock = next(e for e in tools if e["name"] == "check_stock" and e["result"].get("ok"))
    refusal = next(e for e in tools if e["name"] == "create_purchase_order" and e["result"].get("ok") is False)
    preview = next(e for e in tools if e["name"] == "create_purchase_request" and e["result"].get("preview"))
    commit = next(e for e in tools if e["name"] == "create_purchase_request" and e["args"].get("confirm") is True)
    got = {
        "tools": len(trace["tools"]), "tokens": cs["total"], "first_tool": llm[0]["tool_calls"][0]["name"],
        "free": stock["result"]["free_total"], "cover": stock["result"]["cover_days"],
        "limit_and_value": ["£50,000" in refusal["result"]["error"], "£285,600" in refusal["result"]["error"]],
        "preview": preview["result"]["preview"]["estimated_value"], "approver": preview["result"]["preview"]["approver"],
        "request": commit["result"]["request_no"], "inbox": commit["result"]["approver"],
    }
    want = {"tools": 15, "tokens": 2139, "first_tool": "find_item", "free": 6600, "cover": 11,
            "limit_and_value": [True, True], "preview": 273600.0, "approver": "DOKAFOR",
            "request": "PR/2026/04417", "inbox": "DOKAFOR"}
    bad = {k: (want[k], got[k]) for k in want if want[k] != got[k]}
    if bad:
        raise SystemExit(f"the narration quotes numbers the trace does not have (said, trace): {bad}")
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


SENT = re.compile(r"[^.!?]+[.!?]+\s*|[^.!?]+$")


def cues(text, say, al):
    """One subtitle per sentence: shown text from `text`, timing from the same sentence in `say`."""
    ts, ss = SENT.findall(text), SENT.findall(say)
    if len(ts) != len(ss):
        raise SystemExit(f"text and say need the same sentences: {text!r}")
    starts, ends = al["character_start_times_seconds"], al["character_end_times_seconds"]
    out, pos = [], 0
    for a, b in zip(ts, ss):
        i, j = pos, min(pos + len(b.rstrip()) - 1, len(ends) - 1)
        out.append({"t": round(starts[min(i, len(starts) - 1)], 2), "end": round(ends[j], 2), "text": a.strip()})
        pos += len(b)
    return out


def main():
    nar = json.load(open(HERE / "narration.json"))
    trace = json.load(open(HERE / "trace.json"))
    check_facts(nar, trace)
    (HERE / "audio").mkdir(exist_ok=True)
    key = api_key()
    st = nar["stages"]
    spoken = [s for s in st if s.get("say")]
    keep = {s["audio"].split("/")[-1] for s in spoken}
    for f in (HERE / "audio").glob("*.mp3"):   # clips of stages that are no longer narrated, or an older voice
        if f.name not in keep:
            f.unlink()
    chars = 0
    for i, s in enumerate(spoken):
        sha = hashlib.sha1((nar["voice_id"] + nar["model"] + json.dumps(SETTINGS) + s["say"] + s["text"]).encode()).hexdigest()
        mp3 = HERE / s["audio"]
        if s.get("sha") == sha and mp3.exists():
            continue
        prev = spoken[i - 1]["say"] if i else ""
        nxt = spoken[i + 1]["say"] if i + 1 < len(spoken) else ""
        r = synth(key, nar["voice_id"], nar["model"], s["say"], prev, nxt)
        data = base64.b64decode(r["audio_base64"])
        mp3.write_bytes(data)
        al = r["alignment"]
        s.update(sha=sha, speech_end=round(al["character_end_times_seconds"][-1], 2),
                 duration=round(len(data) * 8 / 128000, 2), cues=cues(s["text"], s["say"], al))
        if s.get("punch"):
            at = s["say"].find(s["punch"]["cue"])
            if at < 0:
                raise SystemExit(f"stage {s['k']}: punch cue {s['punch']['cue']!r} is not in the words")
            s["punch"]["t"] = round(al["character_start_times_seconds"][at], 2)
        chars += len(s["say"])
        print(f"stage {s['k']:02d}: {s['duration']:5.1f} s  {s['text'][:64]}", flush=True)
    nar["speech_seconds"] = round(sum(s["duration"] for s in spoken), 1)
    json.dump(nar, open(HERE / "narration.json", "w"), indent=1, ensure_ascii=False)
    print(f"{len(spoken)} clips, {nar['speech_seconds']} s of speech, {chars} characters synthesized this run")


if __name__ == "__main__":
    sys.exit(main())
