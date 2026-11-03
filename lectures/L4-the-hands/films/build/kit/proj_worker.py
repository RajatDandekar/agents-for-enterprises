"""Run inside Blender on a saved film .blend: export the pins' 2D positions for frames [F0, F1) every STEP frames."""
import json
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l2kit as K  # noqa: E402

sc = bpy.context.scene
pins = json.load(open(os.environ["PINS"]))
f0, f1, step = int(os.environ["F0"]), int(os.environ["F1"]), int(os.environ["STEP"])
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
objs = {n: bpy.data.objects[n] for n in pins if n in bpy.data.objects}
first = sc.camera
out = {"frames": [], "cams": [], "pins": {n: [] for n in objs}}
for f in range(f0, f1, step):
    sc.frame_set(f)
    best, bf = None, -1
    for mk in sc.timeline_markers:
        if mk.camera and bf <= mk.frame <= f:
            best, bf = mk.camera, mk.frame
    cam = best or first
    out["frames"].append(f)
    out["cams"].append(cam.name)
    for n, o in objs.items():
        p = world_to_camera_view(sc, cam, o.matrix_world.translation)
        out["pins"][n].append([round(p.x * 1920, 1), round((1 - p.y) * 1080, 1), round(p.z, 2)])
json.dump(out, open(os.environ["OUT"], "w"), separators=(",", ":"))
print("PROJ", f0, f1)
