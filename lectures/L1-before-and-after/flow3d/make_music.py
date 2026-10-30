"""Web version of the music bed, made on Modal with ffmpeg (never on the laptop).

    /Users/raj/.venv/bin/modal run lectures/L1-before-and-after/flow3d/make_music.py --seconds 146

music/envision_amaranth_cove.mp3 ("Envision", Amaranth Cove, Epidemic Sound) -> music/envision_web.mp3:
loudness-normalised to -16 LUFS (the narration's level, so the page can set it about 22 dB under the voice),
cut to the narrated runtime plus a few seconds, 2 s fade-in, 4 s fade-out, 128 kbps mp3.
"""
import pathlib
import subprocess

import modal

HERE = pathlib.Path(__file__).resolve().parent
image = modal.Image.debian_slim().apt_install("ffmpeg").add_local_file(HERE / "music" / "envision_amaranth_cove.mp3", "/in.mp3")
app = modal.App("flow3d-music", image=image)


@app.function(timeout=600)
def make(seconds: float) -> bytes:
    af = f"loudnorm=I=-16:TP=-2:LRA=11,afade=t=in:st=0:d=2,afade=t=out:st={seconds - 4:.2f}:d=4"
    subprocess.run(["ffmpeg", "-y", "-i", "/in.mp3", "-t", f"{seconds:.2f}", "-af", af, "-ar", "44100", "-ac", "2",
                    "-c:a", "libmp3lame", "-b:a", "128k", "/out.mp3"], check=True, capture_output=True)
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "/out.mp3"], capture_output=True, text=True)
    print("duration", p.stdout.strip())
    return open("/out.mp3", "rb").read()


@app.local_entrypoint()
def main(seconds: float = 146.0):
    data = make.remote(seconds)
    (HERE / "music" / "envision_web.mp3").write_bytes(data)
    print("wrote music/envision_web.mp3", len(data), "bytes")
