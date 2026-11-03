"""Contact grid of local JPEG stills (QA only): python grid.py out.jpg a.jpg b.jpg ... (2 columns, 960 px each)."""
import sys
from PIL import Image
out, fs = sys.argv[1], sys.argv[2:]
cols, w = 2, 960
h = w * 9 // 16
rows = (len(fs) + cols - 1) // cols
G = Image.new("RGB", (cols * w, rows * h))
for i, f in enumerate(fs):
    G.paste(Image.open(f).resize((w, h)), ((i % cols) * w, (i // cols) * h))
G.save(out, quality=86)
