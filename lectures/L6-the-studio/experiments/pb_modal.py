"""Generate Lecture 6's PaperBanana figures on Modal (the laptop venv for PaperBanana is gone).

    /Users/raj/.venv/bin/modal run lectures/L6-the-studio/experiments/pb_modal.py --names wf_vs_agent,triggers

Runs /Users/raj/Claude_Brain/ai-fde-site/tools/pb_generate_local.py (planner gemini-3.8-flash, renderer
gemini-3-pro-image-preview) once per brief in pb_briefs.py, in parallel, and writes ../figs/<name>.png.
The Gemini key is read from the env file and passed as a Modal secret; it is never printed."""
import pathlib
import sys

import modal

HERE = pathlib.Path(__file__).resolve().parent
FIGS_DIR = HERE.parent / "figs"
PB = "/Users/raj/Claude_Brain/ai-fde-site/tools/pb_generate_local.py"
ENV = "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env"


def _key():
    for line in open(ENV):
        if line.startswith("GEMINI_API_KEY="):
            v = line.split("=", 1)[1].strip().strip('"').strip("'")
            return {"GEMINI_API_KEY": v, "GOOGLE_API_KEY": v}
    return {}


image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("paperbanana==0.3.0", "python-dotenv", "structlog")
         .add_local_file(PB, "/pb/pb_generate_local.py"))
app = modal.App("l6-paperbanana", image=image)


@app.function(secrets=[modal.Secret.from_dict(_key())], timeout=1500, cpu=1, memory=2048)
def gen(name: str, desc: str) -> tuple:
    import subprocess
    out = f"/tmp/out/{name}.png"
    log = ""
    for attempt in range(2):
        p = subprocess.run([sys.executable, "/pb/pb_generate_local.py", "--description", desc, "--output", out],
                           capture_output=True, text=True, timeout=1400)
        log = (p.stdout[-1500:] + "\n" + p.stderr[-2500:])
        if p.returncode == 0 and pathlib.Path(out).exists():
            return name, pathlib.Path(out).read_bytes(), log[-600:]
    return name, b"", log


@app.local_entrypoint()
def main(names: str = ""):
    sys.path.insert(0, str(HERE))
    import pb_briefs as B
    want = [n for n in (names.split(",") if names else B.FIGS) if n]
    FIGS_DIR.mkdir(exist_ok=True)
    for name, data, log in gen.starmap([(n, B.FIGS[n] + B.STYLE) for n in want]):
        if data:
            (FIGS_DIR / f"{name}.png").write_bytes(data)
            print("ok", name, len(data))
        else:
            print("FAIL", name, log[-1200:])
