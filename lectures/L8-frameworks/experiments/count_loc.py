"""Lines of code for each Ask Rasoi implementation (stdlib only; safe on the laptop).

    python3 lectures/L8-frameworks/experiments/count_loc.py   -> logs/loc.json

A line counts if it is not blank, not a comment and not inside a docstring. For the framework ports we count the
'# --- port ---' section of each file: the code you write to define the agent and run one message. For our own
harness we count all of harness.py (the loop and its seven parts) and, separately, the loop alone.
"""
import io
import json
import pathlib
import tokenize

ROOT = pathlib.Path(__file__).resolve().parents[3]
FW = ROOT / "bahi/bahi/course/frameworks"
L5 = ROOT / "bahi/bahi/course/l5"


def code_lines(src: str) -> list[str]:
    doc_lines = set()
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    prev = None
    for t in toks:
        if t.type == tokenize.STRING and (prev is None or prev.type in (tokenize.INDENT, tokenize.DEDENT, tokenize.NEWLINE,
                                                                         tokenize.NL)):
            doc_lines.update(range(t.start[0], t.end[0] + 1))
        if t.type not in (tokenize.COMMENT, tokenize.NL):
            prev = t
    out = []
    for i, line in enumerate(src.splitlines(), 1):
        s = line.strip()
        if s and not s.startswith("#") and i not in doc_lines:
            out.append(line)
    return out


def section(path, start="# --- port", end="# --- end port"):
    src = path.read_text()
    a = src.index(start)
    b = src.index(end)
    return src[a:b]


res = {}
for name, f in [("openai_agents", "openai_agents.py"), ("adk", "adk.py"), ("langgraph", "langgraph_react.py")]:
    sec = section(FW / f)
    lines = code_lines(sec)
    res[name] = {"file": f"bahi/bahi/course/frameworks/{f}", "port_lines": len(lines),
                 "imports": sum(1 for l in lines if l.strip().startswith(("from ", "import ")))}
h = (L5 / "harness.py").read_text()
res["ours"] = {"file": "bahi/bahi/course/l5/harness.py", "port_lines": len(code_lines(h)),
               "imports": sum(1 for l in code_lines(h) if l.strip().startswith(("from ", "import ")))}
loop = h[h.index("    def _loop(self)"):h.index("    def _stop(")]
res["ours"]["loop_only_lines"] = len(code_lines(loop))
g = (L5 / "graph.py").read_text()
res["control"] = {"file": "bahi/bahi/course/l5/graph.py", "port_lines": len(code_lines(g))}
d = (FW / "desks.py").read_text()
gd = d[d.index("def food_grade_problem"):d.index("SKIP = re.compile")]
res["guardrail_checks_lines"] = len(code_lines(gd))
out = pathlib.Path(__file__).parent / "logs" / "loc.json"
out.write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
