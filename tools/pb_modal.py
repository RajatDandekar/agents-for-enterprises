"""PaperBanana figures, generated on Modal (the laptop's PaperBanana venv is gone; nothing is installed locally).

    /Users/raj/.venv/bin/modal run tools/pb_modal.py --output lectures/L2-the-brain/figs/transformer.png \
        --description "Architecture diagram of ..."
    /Users/raj/.venv/bin/modal run tools/pb_modal.py --batch lectures/L2-the-brain/figs/figs.json
        # figs.json: [{"output": "lectures/.../a.png", "description": "..."}, ...]  (run in parallel)

Uses the patched pipeline in ai-fde-site/tools/pb_generate_local.py (planner gemini-3.8-flash, renderer
gemini-3-pro-image-preview, 2 critique rounds). The Gemini key comes from wm-lecture6-ijepa/.env as a Modal
secret and is never printed. STYLE below is appended to every description so all course figures match.
"""
import json
import os
import pathlib

import modal

ROOT = pathlib.Path(__file__).resolve().parents[1]
PB_SCRIPT = "/Users/raj/Claude_Brain/ai-fde-site/tools/pb_generate_local.py"
KEY_FILE = "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env"

STYLE = (" Visual style: a clean professional technical diagram on a pure white background, like a figure in a "
         "well-designed engineering textbook. Soft sky-blue (#0b57d0 and light #e6f1ff) as the main accent, warm "
         "ember orange (#c4511f) only for anything legacy or 'before', green (#138a60) sparingly for key terms. "
         "Rounded rectangles, thin dark-grey lines, generous spacing, a modern sans-serif font, every label short, "
         "plain and spelled correctly. No people, no faces, no icons of people, no emoji, no clip art, no 3D, no "
         "gradients on text, no title banner unless asked.")


def _key() -> dict:
    env = {}
    if os.path.exists(KEY_FILE):
        for line in open(KEY_FILE):
            if line.startswith("GEMINI_API_KEY="):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                env = {"GEMINI_API_KEY": v, "GOOGLE_API_KEY": v}
    return env


image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("paperbanana", "structlog", "python-dotenv")
         .add_local_file(PB_SCRIPT, "/pb/pb_generate_local.py"))
app = modal.App("course-paperbanana", image=image)


@app.function(secrets=[modal.Secret.from_dict(_key())], timeout=1500, max_containers=6)
def render(description: str) -> tuple[bytes | None, str]:
    import subprocess
    out = "/tmp/fig.png"
    p = subprocess.run(["python", "/pb/pb_generate_local.py", "--description", description + STYLE, "--output", out],
                       capture_output=True, text=True)
    if p.returncode == 0 and os.path.exists(out):
        return open(out, "rb").read(), ""
    tail = (p.stderr or p.stdout).strip().splitlines()[-3:]
    return None, " | ".join(tail)


@app.local_entrypoint()
def main(output: str = "", description: str = "", batch: str = ""):
    jobs = json.loads(pathlib.Path(batch).read_text()) if batch else [{"output": output, "description": description}]
    for job, (png, err) in zip(jobs, render.map([j["description"] for j in jobs])):
        dest = pathlib.Path(job["output"])
        dest = dest if dest.is_absolute() else ROOT / dest
        if png:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(png)
            print(f"OK   {dest.relative_to(ROOT) if ROOT in dest.parents else dest}  ({len(png)//1024} KB)")
        else:
            print(f"FAIL {job['output']}: {err}")
