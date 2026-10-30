"""Local check of the 2D layer on one rendered still (tiny, PIL only): comp_still.py <shot> <local_frame>"""
import json, sys, os
from PIL import Image
import comp, overlays
HERE = os.path.dirname(os.path.abspath(__file__))
shot, lf = sys.argv[1], int(sys.argv[2])
tl = overlays.TL()
S = json.load(open(os.path.join(HERE, "script.json")))
E = overlays.build(tl, S)
s = tl.shot(shot)
g = s["r0"] + lf
proj = {x["shot"]: json.load(open(os.path.join(HERE, "out", f"proj_{x['shot']}.json"))) for x in tl.shots if os.path.exists(os.path.join(HERE, "out", f"proj_{x['shot']}.json"))}
ctx = {"proj": proj, "r0": {x["shot"]: x["r0"] for x in tl.shots}}
img = Image.open(os.path.join(HERE, "out", f"still_{shot}_{lf:04d}.jpg")).convert("RGBA")
out = comp.compose(g, lambda g: img, [e for e in E if e.get("shot", shot) == shot or "shot" not in e], ctx)
p = os.path.join(HERE, "out", f"comp_{shot}_{lf:04d}.jpg")
out.convert("RGB").save(p, quality=90)
print(p, "global", g)
