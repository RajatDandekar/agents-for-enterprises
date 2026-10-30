"""Make light JPEG copies of the PaperBanana PNGs for the deck (smaller to load; the QA mount skips .png).

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L2-the-brain/experiments/convert_figs.py
"""
import pathlib
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parents[1]
FIGS = HERE / "figs"
srcs = sorted(FIGS.glob("*.png"))
for p in srcs:
    im = Image.open(p).convert("RGB")
    if im.width > 2000:
        im = im.resize((2000, round(im.height * 2000 / im.width)), Image.LANCZOS)
    out = FIGS / (p.stem + ".jpg")
    im.save(out, quality=88, optimize=True)
    print(out.name, im.size, out.stat().st_size // 1024, "KB")
