"""Fetch the Rubin reference video on Modal and return a contact sheet of frames (look only)."""
import modal
image = modal.Image.debian_slim(python_version="3.11").apt_install("ffmpeg").pip_install("yt-dlp")
vol = modal.Volume.from_name("l1film", create_if_missing=True)
app = modal.App("l1film-ref")

@app.function(image=image, volumes={"/vol": vol}, timeout=1200, cpu=4)
def grab(url: str, every: int = 10) -> list:
    import subprocess, os, glob
    os.makedirs("/vol/ref", exist_ok=True)
    if not os.path.exists("/vol/ref/rubin.mp4"):
        p = subprocess.run(["yt-dlp", "-f", "bv*[height<=1080][ext=mp4]/b[ext=mp4]/b", "-o", "/vol/ref/rubin.mp4", url], capture_output=True, text=True)
        print(p.stdout[-1500:], p.stderr[-1500:])
    os.makedirs("/tmp/fr", exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "/vol/ref/rubin.mp4", "-vf", f"fps=1/{every},scale=640:-2", "/tmp/fr/r_%03d.jpg"])
    files = sorted(glob.glob("/tmp/fr/*.jpg"))
    sheets = []
    for i in range(0, len(files), 12):
        chunk = files[i:i+12]
        n = len(chunk)
        args = sum([["-i", f] for f in chunk], [])
        lay = "|".join(f"{(j%3)*640}_{(j//3)*360}" for j in range(n))
        out = f"/tmp/sheet_{i//12}.jpg"
        flt = f"xstack=inputs={n}:layout={lay}:fill=white" if n > 1 else "null"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args, "-filter_complex", flt, "-frames:v", "1", "-q:v", "4", out])
        sheets.append(open(out, "rb").read())
    vol.commit()
    return sheets

@app.local_entrypoint()
def main(url: str = "https://www.youtube.com/watch?v=EfYWEXnfXA8", every: int = 10):
    import os
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "ref")
    os.makedirs(d, exist_ok=True)
    for i, b in enumerate(grab.remote(url, every)):
        open(os.path.join(d, f"rubin_sheet_{i}.jpg"), "wb").write(b)
        print("sheet", i)
