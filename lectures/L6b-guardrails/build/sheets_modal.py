"""Contact sheets of the QA screenshots, made on Modal (no image library on the laptop).

    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run lectures/L6b-guardrails/build/sheets_modal.py

Reads lectures/L6b-guardrails/qa/slide-NN.png (written by qa_full_modal.py --slides all) and writes
qa/sheet-NN.png: six slides a sheet (2 across, 3 down), each with its number, for the reading pass."""
import io
import pathlib

import modal

QA = pathlib.Path(__file__).resolve().parents[1] / "qa"
image = modal.Image.debian_slim(python_version="3.11").pip_install("pillow==10.4.0").add_local_dir(QA, "/qa", ignore=["sheet-*.png"])
app = modal.App("l7-deck-sheets", image=image)


@app.function(timeout=600, cpu=2, memory=4096)
def sheets(per: int = 6, cols: int = 2, w: int = 800) -> dict:
    from PIL import Image, ImageDraw, ImageFont
    files = sorted(pathlib.Path("/qa").glob("slide-*.png"), key=lambda p: int(p.stem.split("-")[1]))
    out, h = {}, int(w * 940 / 1600)
    rows = -(-per // cols)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    for s in range(0, len(files), per):
        sheet = Image.new("RGB", (cols * w + (cols + 1) * 8, rows * (h + 8) + 8), "#30343c")
        d = ImageDraw.Draw(sheet)
        for i, f in enumerate(files[s:s + per]):
            im = Image.open(f).convert("RGB").resize((w, h), Image.LANCZOS)
            x, y = 8 + (i % cols) * (w + 8), 8 + (i // cols) * (h + 8)
            sheet.paste(im, (x, y))
            n = f.stem.split("-")[1]
            d.rectangle([x, y, x + 58, y + 30], fill="#c4511f")
            d.text((x + 8, y + 3), n, fill="white", font=font)
        b = io.BytesIO()
        sheet.save(b, "PNG", optimize=True)
        out[f"sheet-{s // per + 1:02d}.png"] = b.getvalue()
    return out


@app.local_entrypoint()
def main(per: int = 6, cols: int = 2, w: int = 800):
    for f in QA.glob("sheet-*.png"):
        f.unlink()
    res = sheets.remote(per, cols, w)
    for name, data in res.items():
        (QA / name).write_bytes(data)
    print("sheets:", sorted(res))
