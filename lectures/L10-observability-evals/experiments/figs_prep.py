"""Make the deck's JPGs from the PaperBanana PNGs and the headless screenshots (PIL, on Modal; nothing is generated).

    tools/mrun.sh lectures/L10-observability-evals/experiments/l10_modal.py --script lectures/L10-observability-evals/experiments/figs_prep.py
"""
import pathlib
import subprocess
import sys

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pillow"], check=True)
from PIL import Image  # noqa: E402

F = pathlib.Path(__file__).parents[1] / "figs"
PB = ["otel_pipeline", "langfuse_model", "ci_gate", "ragas_metrics", "redteam_loop", "offline_online", "arch_obs_lit"]
SHOTS = {"lf_turn3": ["langfuse_r3_turn3", "langfuse_r2_turn3"], "lf_gen": ["langfuse_r3_turn3_gen", "langfuse_r2_turn3_gen"],
         "lf_release": ["langfuse_r3_turn3_release", "langfuse_r2_turn3_release"],
         "phoenix_trace": ["phoenix_r3_trace_last", "phoenix_r2_trace_last"], "phoenix_run1": ["phoenix_trace_turn3"], "lf_timeline": ["lf_r3_timeline"]}


def save(src, dst, width):
    im = Image.open(src).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dst, "JPEG", quality=86, optimize=True)
    print(dst.name, im.size, dst.stat().st_size // 1024, "KB", "from", src.name)


for n in PB:
    if (F / f"{n}.png").exists():
        save(F / f"{n}.png", F / f"{n}.jpg", 1920)
im = Image.open(F / "lf_r3_timeline.png").convert("RGB")       # the timeline half of the Langfuse view, readable
w, h = im.size
im.crop((0, 0, int(w * 0.575), int(h * 0.8))).save(F / "lf_timeline_crop.jpg", "JPEG", quality=88, optimize=True)
print("lf_timeline_crop.jpg", int(w * 0.575), int(h * 0.8))
for dst, srcs in SHOTS.items():
    for s in srcs:
        if (F / f"{s}.png").exists():
            save(F / f"{s}.png", F / f"{dst}.jpg", 2000)
            break
