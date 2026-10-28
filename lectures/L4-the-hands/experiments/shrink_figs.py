"""Make light JPEG copies of the PaperBanana PNGs for the deck (the PNGs stay as the sources). Run on Modal."""
import pathlib
from PIL import Image

FIGS = pathlib.Path(__file__).resolve().parents[1] / "figs"
srcs = sorted(FIGS.glob("*.png")) + [pathlib.Path("/course/figures/ask_rasoi_architecture_wide.png")]
for p in srcs:
    im = Image.open(p).convert("RGB")
    im.thumbnail((2000, 2000))
    out = FIGS / ("arch_wide.jpg" if p.name.startswith("ask_rasoi") else p.with_suffix(".jpg").name)
    im.save(out, quality=86, optimize=True)
    print(out.name, im.size, out.stat().st_size // 1024, "KB")
