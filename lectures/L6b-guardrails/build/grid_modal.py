"""Screenshots with a coordinate grid, made on Modal, to choose `data-crop` rectangles exactly (no image library locally).

    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run lectures/L6b-guardrails/build/grid_modal.py --names figs/argus/chat_guard_off.png,figs/promptfoo/pf_redteam_eval.png
    ... --crops "figs/argus/chat_guard_off.png:1222,553,1742,923"     # also writes that crop, to check it

Writes qa/grid-<name>.png: the image scaled to 1600 px wide with a line and a label every 200 image pixels."""
import io
import pathlib

import modal

DECK = pathlib.Path(__file__).resolve().parents[1]
image = modal.Image.debian_slim(python_version="3.11").pip_install("pillow==10.4.0").add_local_dir(DECK / "figs", "/figs")
app = modal.App("l7-deck-grid", image=image)


@app.function(timeout=600, cpu=2, memory=4096)
def grid(names: list, crops: list) -> dict:
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    out = {}
    for n in names:
        im = Image.open("/" + n).convert("RGB")
        s = 1600 / im.width
        sm = im.resize((1600, int(im.height * s)), Image.LANCZOS)
        d = ImageDraw.Draw(sm)
        for x in range(0, im.width, 200):
            d.line([(x * s, 0), (x * s, sm.height)], fill=(255, 0, 80), width=1)
            for y in range(0, im.height, 400):
                d.text((x * s + 3, y * s + 3), f"{x},{y}", fill=(255, 0, 80), font=font)
        for y in range(0, im.height, 200):
            d.line([(0, y * s), (1600, y * s)], fill=(0, 120, 255), width=1)
        b = io.BytesIO(); sm.save(b, "PNG"); out["grid-" + n.split("/")[-1]] = b.getvalue()
    for c in crops:
        n, r = c.split(":")
        x, y, w, h = [int(v) for v in r.split(",")]
        im = Image.open("/" + n).convert("RGB").crop((x, y, x + w, y + h))
        im.thumbnail((1400, 1400))
        b = io.BytesIO(); im.save(b, "PNG"); out[f"crop-{n.split('/')[-1][:-4]}-{x}_{y}_{w}_{h}.png"] = b.getvalue()
    return out


@app.local_entrypoint()
def main(names: str = "", crops: str = ""):
    res = grid.remote([n for n in names.split(",") if n], [c for c in crops.split(";") if c])
    for name, data in res.items():
        (DECK / "qa" / name).write_bytes(data)
    print("written:", sorted(res))
