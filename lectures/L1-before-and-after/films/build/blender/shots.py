"""Build one shot of the L1 film as a packed .blend (run inside Blender on Modal).

  blender -b --factory-startup -P shots.py -- --shot harness --outdir /vol/l1film/blend

Every shot builds the whole machine (props.build_all), then keys its own camera and
animation to the narration words (lib.Beats), exports the 2D anchor positions per frame
(proj/<shot>.json) for the overlay compositor, and saves <shot>.blend.
"""
import argparse
import json
import math
import os
import random
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib as L  # noqa: E402
import props as P  # noqa: E402

R = random.Random(5)
JIG = Vector((-2.88, 0.0, 0.799))      # world position of the first sheet in the jig
MAG = Vector((-3.42, 0.02, 0.80))      # magazine floor


# ------------------------------------------------------------------ helpers
def send(name, pathname, f0, f1, color=L.SKY_L, size=0.06, hold_end=0, reverse=False):
    pk, m = P.packet(name, color, (size, size * 0.5, size * 0.5))
    L.follow(pk, P.PATHS[pathname], [(f0, 1.0 if reverse else 0.0), (f1, 0.0 if reverse else 1.0)])
    L.vis(pk, [(0, False), (f0, True), (f1 + 1 + hold_end, False)])
    return pk


def tokens(pathname, f0, f1, n=36, spread=None):
    """A stream of small glass token tiles riding a conduit into a station."""
    spread = spread or (f1 - f0) * 0.6
    mats = [L.led("tok_s", L.SKY_L, body=(0.85, 0.9, 1.0, 1), strength=2.5),
            L.led("tok_g", L.GREEN_L, body=(0.85, 1.0, 0.9, 1), strength=2.5),
            L.led("tok_w", (1.0, 0.5, 0.15, 1), body=(1, 0.95, 0.9, 1), strength=2.5)]
    for i in range(n):
        t = L.box(f"tok_{i}", (0.022, 0.022, 0.022), mats[0 if i < 4 else (1 if i > 8 else 2) if i < 12 else 1], bevel=0.003)
        s = f0 + int(i * spread / n)
        e = s + int((f1 - f0) * 0.45)
        L.follow(t, P.PATHS[pathname], [(s, 0.0), (e, 1.0)], follow_axis=False)
        L.vis(t, [(0, False), (s, True), (e + 1, False)])


def stack_sheet(name, kind, n, f_land=None, f_start=None, src=None, show_before=False):
    """Sheet number n in the jig stack. Flies in from src (default: magazine) between f_start and f_land."""
    s, em = P.sheet(name, kind, P.H["M"])
    dst = JIG + Vector((0, 0, n * 0.0056))
    if f_land is None:
        s.location = dst
        return s, em
    src = src or (MAG + Vector((0, 0, 0.1)))
    mid = (src + dst) / 2 + Vector((0, -0.05, 0.22))
    L.key(s, "location", [(f_start, src), ((f_start + f_land) // 2, mid), (f_land, dst)])
    L.key(s, "rotation_euler", [(f_start, (0.0, -0.25, 0.1)), ((f_start + f_land) // 2, (0.05, -0.1, 0.04)), (f_land, (0, 0, 0))])
    if not show_before:
        L.vis(s, [(0, False), (f_start, True)])
    L.em_keys(em, [(f_land - 2, 0.3), (f_land + 2, 4.0), (f_land + 30, 1.6)])
    return s, em


def full_stack(extra=0):
    for k in range(17 + extra):
        kind = "sys" if k == 0 else "msg" if k == 1 else "tool" if k < 17 else "result"
        s, em = stack_sheet(f"st_{k}", kind, k)
        L.em_keys(em, [(0, 1.6)])
    P.H["clamp"].location.z = 1.17 - (1.17 - (0.796 + (17 + extra) * 0.0056 + 0.02))


def layer_glow(start, step=3, peak=3.0, rest=0.8, end_level=None):
    for i, m in enumerate(P.H["layer_mats"]):
        f = start + i * step
        keys = [(0, 0.0), (max(1, f - 6), 0.0), (f, peak), (f + 14, rest)]
        L.em_keys(m, keys)


def layer_level(keys_by_layer):
    for i, m in enumerate(P.H["layer_mats"]):
        L.em_keys(m, keys_by_layer(i))


def covers_open(f0, f1, closed=False):
    for side, cv in zip((-1, 1), P.H["covers"]):
        if closed:
            cv.location.x = 0
            continue
        L.key(cv, "location", [(f0, (0, 0, 0)), (f1, (side * 1.6, -0.9, 0))])


def covers_away():
    for cv in P.H["covers"]:
        for o in [cv] + list(cv.children_recursive):
            o.hide_render = True


def slide(name, f0, f1, back0=None, back1=None, dist=0.24):
    c = P.H["carts"][name]
    z = c.location.z
    keys = [(f0, (0, 0, z)), (f1, (0, -dist, z))]
    if back0 is not None:
        keys += [(back0, (0, -dist, z)), (back1, (0, 0, z))]
    L.key(c, "location", keys)


def blink(m, f0, f1, period=4, hi=3.0, lo=0.0, seed=0):
    rr = random.Random(seed)
    keys = [(f0 - 1, lo)]
    f = f0
    while f < f1:
        keys.append((f, hi if rr.random() < 0.55 else lo))
        f += period + rr.randint(0, 3)
    keys.append((f1, lo))
    L.em_keys(m, keys)
    for fc in m.node_tree.animation_data.action.fcurves:
        if "Emission" not in fc.data_path:
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


def erp_busy(f0, f1, seed=1):
    for i, row in enumerate(P.H["unit_leds"]):
        for k, m in enumerate(row):
            blink(m, f0, f1, period=3 + (k % 3), hi=3.5, lo=0.4, seed=seed * 100 + i * 10 + k)
    blink(P.H["erp_hdd"], f0, f1, period=2, hi=4.0, lo=0.0, seed=seed)
    for i in range(3):
        blink(P.H[f"bay_led_{i}"], f0, f1, period=5, hi=3.0, seed=seed + i)


def erp_idle():
    for i, row in enumerate(P.H["unit_leds"]):
        for k, m in enumerate(row):
            L.em_keys(m, [(0, 1.2 if (i + k) % 3 else 0.3)])


# ------------------------------------------------------------------ cameras (several per block, switched by markers)
CAMS = []


def cam(f0, keys, lens=40, fstop=4.0, lens_keys=None):
    """A camera that takes over at frame f0. keys: [(frame, loc, target)]."""
    sc = bpy.context.scene
    n = len(CAMS)
    d = bpy.data.cameras.new(f"cam{n}")
    d.lens, d.sensor_width, d.clip_start, d.clip_end = lens, 36, 0.02, 200
    d.dof.use_dof, d.dof.aperture_fstop = True, fstop
    c = bpy.data.objects.new(f"cam{n}", d)
    sc.collection.objects.link(c)
    t = L.empty(f"cam{n}_tgt")
    con = c.constraints.new("TRACK_TO")
    con.target, con.track_axis, con.up_axis = t, "TRACK_NEGATIVE_Z", "UP_Y"
    d.dof.focus_object = t
    L.cam_keys(c, t, keys)
    if lens_keys:
        L.key(d, "lens", lens_keys)
    m = sc.timeline_markers.new(f"m{n}", frame=f0)
    m.camera = c
    CAMS.append((f0, c))
    if n == 0:
        sc.camera = c
    return c


def cam_at(f):
    best = CAMS[0][1]
    for f0, c in sorted(CAMS, key=lambda x: x[0]):
        if f >= f0:
            best = c
    return best


def point(name, loc, color, keys):
    d = bpy.data.lights.new(name, "POINT")
    d.color = color[:3]
    d.shadow_soft_size = 0.15
    o = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    L.key(d, "energy", keys)
    return o


# ------------------------------------------------------------------ blocks
def shot_chat(b):
    disp = Vector((-5.6, 0.30, 1.19))
    cam(0, [(0, (-5.05, -1.25, 1.32), disp + Vector((0.02, 0, -0.01))),
            (b.frames - 90, (-5.32, -0.86, 1.24), disp),
            (b.frames - 1, (-5.05, -0.95, 1.26), (-5.35, 0.3, 1.12))], 50, 2.8)
    L.em_keys(P.H["screen_mat"], [(0, 1.0)], scale=False)
    f = b.w("seconds") - 25
    send("pk_q", "c_emma_bench", f, f + 40, L.SKY_L)
    erp_idle()
    covers_away()


def shot_harness(b):
    c = Vector((-2.98, 0.0, 0.86))
    fr, fm, fs = b.w("rules"), b.w("message"), b.w("stacked")
    cam(0, [(0, (-3.85, -1.95, 1.75), c + Vector((-0.22, 0, 0))), (fr - 12, (-3.6, -1.75, 1.6), c)], 42, 3.2)
    # macro: the context sheets stacking in the jig
    cam(fr - 12, [(fr - 12, (-3.32, -0.72, 1.1), (-2.9, 0.0, 0.84)), (fs - 8, (-3.12, -0.5, 0.99), (-2.89, 0.0, 0.83))], 55, 2.4)
    cam(fs - 8, [(fs - 8, (-3.75, -1.7, 1.62), c + Vector((-0.05, 0, 0))), (b.frames - 1, (-3.45, -1.5, 1.48), c + Vector((0.05, 0, -0.02)))], 42, 3.2)
    send("pk_in", "c_emma_bench", 0, 22, L.SKY_L)
    tool_f = [b.w("description") + int(i * (b.w("fifteen") + 12 - b.w("description")) / 15) for i in range(15)]
    starts = [fr - 14, fm - 14] + [t - 10 for t in tool_f]
    lands = [fr + 6, fm + 6] + [t + 6 for t in tool_f]
    kinds = ["sys", "msg"] + ["tool"] * 15
    for n, (k, f0, f1) in enumerate(zip(kinds, starts, lands)):
        src = MAG + Vector((0, 0, 0.0125 + (16 - n) * 0.0056)) if n != 1 else Vector((-3.42, 0.02, 0.95))
        stack_sheet(f"sh_{n}", k, n, f1, f0, src, show_before=(n != 1))
    top = 0.796 + 17 * 0.0056 + 0.02
    L.key(P.H["clamp"], "location", [(fs - 4, (0.12, 0.0, 1.17)), (fs + 14, (0.12, 0.0, top))])
    L.em_keys(P.H["clamp_glow"], [(fs + 10, 0.0), (fs + 16, 4.0), (b.frames - 1, 2.5)])
    ft = b.w("two")
    L.em_keys(P.H["bench_lcd"], [(0, 0.6), (ft - 2, 0.6), (ft + 4, 3.0), (ft + 40, 1.4)])
    covers_away()
    erp_idle()


def shot_model(b):
    fr, ftw, fpk = b.w("reads"), b.w("twist"), b.w("picks")
    ffind, fjs = b.w("find"), b.w("json")
    cam(0, [(0, (-1.25, -2.65, 0.75), (0.0, 0.55, 1.05)), (ftw, (-0.95, -2.45, 1.25), (0.05, 0.55, 1.25)),
            (fpk - 6, (-0.8, -2.4, 1.45), (0.1, 0.55, 1.35))], 32, 4.0)
    # the pick is physical: cut to the rack, find_item slides out and lights
    cam(fpk - 6, [(fpk - 6, (2.72, -0.95, 1.62), (3.3, 0.12, 1.3)), (ffind + 30, (2.85, -0.8, 1.55), (3.3, 0.1, 1.32))], 50, 2.8)
    cam(ffind + 30, [(ffind + 30, (1.15, -1.05, 1.85), (0.6, 0.35, 1.55)), (b.frames - 1, (1.35, -1.2, 1.7), (0.9, 0.3, 1.45))], 40, 3.2)
    covers_open(4, 70)
    tokens("c_bench_model", 0, fr + 40, n=40)
    L.em_keys(P.H["m_intake_led"], [(0, 1.0), (fr + 40, 3.0), (fr + 60, 0.6)])
    waves = [fr + 2, fr + 34, fr + 66]
    def lk(i):
        keys = [(-200, 0.0), (waves[0] - 8, 0.0)]
        for w0 in waves:
            f = w0 + i * 2
            keys += [(f - 3, 0.7), (f, 3.6), (f + 7, 0.7)]
        keys += [(ftw, 0.7), (ftw + 12, 0.3), (fpk - 4, 0.3), (fpk + 2 + NL_TOP(i), 2.4 if i > 15 else 0.9),
                 (b.frames - 1, 1.2 if i > 15 else 0.6)]
        keys.sort(key=lambda k: k[0])
        out = []
        for k in keys:
            if out and k[0] <= out[-1][0]:
                continue
            out.append(k)
        return out
    layer_level(lk)
    fl = b.w("fifteen")
    slide("find_item", fl - 6, fl + 10)
    L.em_keys(P.H["cart_leds"]["find_item"], [(fl - 2, 0.0), (fl + 4, 6.0), (fl + 30, 3.5)])
    for t in P.TOOLS:
        if t != "find_item":
            L.em_keys(P.H["cart_leds"][t], [(fl - 2, 0.6), (fl + 6, 0.15)])
    L.em_keys(P.H["m_port_led"], [(0, 0.3), (ffind + 20, 0.3), (ffind + 34, 4.0), (b.frames - 1, 1.5)])
    send("pk_call", "c_model_guard", ffind + 36, b.frames + 40, L.SKY_L)
    erp_idle()


def NL_TOP(i):
    return max(0, (i - 12)) // 2


def shot_guard(b):
    fin, fc, fty, fthen, fp, ftb = b.w("guard"), b.w("checks"), b.w("types"), b.w("then"), b.w("plug"), b.w("toolbox")
    cam(0, [(0, (1.05, -0.95, 1.38), (1.62, 0.15, 1.15)), (fthen - 6, (1.2, -0.72, 1.3), (1.64, 0.15, 1.16))], 50, 2.8)
    # macro: the MCP plug seats with a click
    cam(fthen - 6, [(fthen - 6, (2.42, -0.42, 0.82), (2.93, 0.4, 0.63)), (ftb - 14, (2.55, -0.28, 0.76), (2.96, 0.4, 0.62))], 55, 2.4)
    cam(ftb - 14, [(ftb - 14, (2.45, -1.95, 1.3), (3.25, 0.35, 0.95)), (b.frames - 1, (2.6, -1.8, 1.2), (3.3, 0.35, 0.95))], 38, 3.2)
    covers_away()
    send("pk_call", "c_model_guard", 0, fin + 6, L.SKY_L)
    hold, hm = P.packet("pk_hold", L.SKY_L, (0.06, 0.03, 0.03))
    L.bsdf(hm).inputs["Base Color"].default_value = (0.05, 0.25, 0.9, 1)
    L.em_keys(hm, [(0, 2.5)])
    hold.location = (1.65, 0.15, 1.16)
    hold.rotation_euler = (0, math.radians(90), 0)
    L.vis(hold, [(-200, False), (fin + 7, True), (fthen, False)])
    L.em_color_keys(P.H["guard_ring"], [(fc - 2, L.SKY_L), (fty + 6, L.GREEN_L)])
    L.em_keys(P.H["guard_ring"], [(0, 0.6), (fc - 2, 0.6), (fc + 6, 3.5), (fty, 3.0), (fty + 8, 5.0), (fthen + 10, 1.0)])
    px = P.H["plug_x"]
    L.key(P.H["plug"], "location", [(0, (px - 0.1, 0.40, 0.62)), (fp - 8, (px - 0.1, 0.40, 0.62)), (fp + 4, (px, 0.40, 0.62))])
    L.em_keys(P.H["plug_ring"], [(fp + 2, 0.0), (fp + 6, 4.0), (b.frames - 1, 2.0)])
    send("pk_mcp", "mcp", fp + 6, ftb + 4, L.SKY_L)
    slide("find_item", -10, -9)
    L.em_keys(P.H["cart_leds"]["find_item"], [(0, 3.5), (ftb, 3.5), (ftb + 6, 7.0), (ftb + 30, 4.0)])
    for t in P.TOOLS:
        if t != "find_item":
            L.em_keys(P.H["cart_leds"][t], [(0, 0.15)])
    erp_idle()


def shot_erp(b):
    fcall, fin, fo = b.w("calls"), b.w("in"), b.w("out")
    fdata = b.w("data")
    cam(0, [(0, (4.6, -2.9, 1.55), (6.2, 0.35, 0.95)), (fcall - 5, (4.85, -2.7, 1.45), (6.2, 0.35, 0.95))], 35, 4.0)
    # macro: the old units blinking behind the smoked glass as the services run
    cam(fcall - 5, [(fcall - 5, (5.72, -0.62, 1.12), (6.08, 0.05, 0.98)), (fdata - 10, (5.84, -0.44, 1.06), (6.1, 0.05, 0.98))], 60, 2.4)
    cam(fdata - 10, [(fdata - 10, (5.2, -2.7, 1.4), (6.55, 0.35, 0.85)), (b.frames - 1, (5.4, -2.5, 1.3), (6.55, 0.35, 0.85))], 32, 4.0)
    covers_away()
    P.H["plug"].location.x = P.H["plug_x"]
    send("pk_in", "legacy", fcall - 30, fcall + 10, L.SKY_L, size=0.05)
    erp_idle()
    erp_busy(fcall + 6, fo + 6, seed=2)
    send("pk_out", "legacy", fo - 6, fo + 40, L.GREEN_L, size=0.05, reverse=True)
    point("erp_inner", (6.1, 0.06, 1.25), (1.0, 0.85, 0.7), [(0, 18.0)])
    point("erp_inner2", (6.1, 0.06, 0.7), (1.0, 0.85, 0.7), [(0, 12.0)])
    bpy.data.materials["smoke"].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.78, 0.78, 0.8, 1)


def shot_loop(b):
    cam(0, [(0, (-0.9, -6.1, 2.6), (-0.05, 0.45, 0.85)), (b.frames - 1, (0.3, -5.8, 2.4), (0.05, 0.45, 0.85))], 26, 6.0)
    covers_away()
    P.H["plug"].location.x = P.H["plug_x"]
    full_stack(0)
    erp_idle()
    laps = [(0, "find_item"), (b.w("manuals") - 30, "search_policy"), (b.w("stock") - 30, "check_stock"), (b.w("grows") + 10, "check_stock")]
    n = 17
    for li, (f, tool) in enumerate(laps):
        if li:
            send(f"pk_call{li}", "c_model_guard", f, f + 22, L.SKY_L, size=0.07)
            send(f"pk_mcp{li}", "mcp", f + 22, f + 40, L.SKY_L, size=0.07)
            slide(tool, f + 34, f + 44, f + 80, f + 92)
            L.em_keys(P.H["cart_leds"][tool], [(f + 34, 0.0), (f + 40, 4.0), (f + 92, 0.4)])
        fr = f + (50 if li else 0)
        send(f"pk_ret{li}", "c_rack_bench", fr, fr + 55, L.GREEN_L, size=0.08)
        stack_sheet(f"res_{li}", "result", n, fr + 72, fr + 52, Vector((-2.8, 0.38, 0.95)))
        n += 1
        send(f"pk_ctx{li}", "c_bench_model", fr + 76, fr + 110, L.SKY_L, size=0.08)
        for i, m in enumerate(P.H["layer_mats"]):
            g = fr + 110 + i
            L.em_keys(m, [(g - 3, 0.6), (g, 2.6), (g + 10, 0.6)])
    clamp_top = 0.796 + n * 0.0056 + 0.02
    L.key(P.H["clamp"], "location", [(0, (0.12, 0, 0.796 + 17 * 0.0056 + 0.02)), (b.frames - 1, (0.12, 0, clamp_top))])
    L.em_keys(P.H["clamp_glow"], [(0, 2.5)])
    slide("find_item", 0, 12)


def shot_refuse(b):
    fd, fn, fraise = b.w("direct", 0), b.w("no"), b.w("raise")
    cam(0, [(0, (2.55, -1.75, 1.45), (3.25, 0.25, 0.95)), (fn - 10, (2.7, -1.6, 1.3), (3.28, 0.25, 0.92))], 42, 3.2)
    # macro on the refusing cartridge: its light turns ember and it is pushed back
    cam(fn - 10, [(fn - 10, (2.78, -0.78, 1.02), (3.22, 0.0, 0.8)), (b.frames - 1, (2.9, -0.62, 0.96), (3.25, 0.05, 0.8))], 55, 2.4)
    covers_away()
    P.H["plug"].location.x = P.H["plug_x"]
    erp_idle()
    send("pk_mcp", "mcp", fd - 24, fd, L.SKY_L)
    slide("create_purchase_order", fd - 4, fd + 12, fraise + 4, fraise + 20)
    led = P.H["cart_leds"]["create_purchase_order"]
    L.em_color_keys(led, [(fn - 2, L.SKY_L), (fn + 2, L.EMBER_L)])
    L.em_keys(led, [(fd - 2, 0.0), (fd + 8, 4.0), (fn - 2, 4.0), (fn + 2, 8.0), (fn + 20, 4.0), (fn + 40, 8.0), (fn + 60, 4.5)])
    point("ember_wash", (3.25, -0.3, 0.86), (1.0, 0.25, 0.06), [(fn - 1, 0.0), (fn + 3, 120.0), (fn + 30, 60.0), (fn + 50, 100.0), (fraise + 20, 40.0)])
    send("pk_no", "c_rack_bench", fn + 4, fn + 80, L.EMBER_L, size=0.08)
    for t in P.TOOLS:
        if t != "create_purchase_order":
            L.em_keys(P.H["cart_leds"][t], [(0, 0.25)])


def shot_preview(b):
    disp = Vector((-5.6, 0.30, 1.19))
    cam(0, [(0, (-6.1, -1.35, 1.32), disp + Vector((0.2, 0, -0.02))), (b.frames - 1, (-5.95, -1.2, 1.28), disp + Vector((0.18, 0, -0.01)))], 42, 2.8)
    L.em_keys(P.H["screen_mat"], [(0, 1.0)], scale=False)
    covers_away()
    fy = b.w("yes")
    send("pk_yes", "c_emma_bench", fy + 6, fy + 46, L.SKY_L)
    erp_idle()


def shot_write(b):
    fs, fl = b.w("saves"), b.w("lands")
    cam(0, [(0, (8.0, -1.75, 1.45), (8.72, -0.12, 0.82)), (fl - 40, (8.15, -1.6, 1.38), (8.73, -0.1, 0.8))], 45, 3.0)
    # macro on the tray: the request settles on top of PO/2026/01179
    cam(fl - 40, [(fl - 40, (8.42, -0.78, 1.18), (8.72, -0.08, 0.82)), (b.frames - 1, (8.5, -0.66, 1.1), (8.72, -0.08, 0.8))], 50, 2.2)
    covers_away()
    erp_busy(fs - 4, fl + 10, seed=7)
    d = P.H["doc_pr"]
    z = d.location.z
    L.key(d, "location", [(fl - 34, (0.02, -0.04, z + 0.42)), (fl - 6, (0.0, -0.01, z + 0.04)), (fl, (0.01, -0.005, z)),
                          (fl + 4, (0.01, -0.005, z + 0.004)), (fl + 8, (0.01, -0.005, z))])
    L.key(d, "rotation_euler", [(fl - 34, (0.25, -0.15, 0.3)), (fl - 6, (0.04, 0.0, 0.02)), (fl, (0, 0, math.radians(-2)))])
    L.vis(d, [(-200, False), (fl - 34, True)])
    point("tray_glow", (8.72, -0.12, 0.98), (0.35, 0.6, 1.0), [(fl - 1, 0.0), (fl + 3, 45.0), (fl + 40, 8.0)])


def shot_receipt(b):
    cam(0, [(0, (6.65, -1.05, 1.2), (7.12, 0.25, 0.98)), (b.frames - 1, (6.8, -0.92, 1.12), (7.12, 0.25, 1.0))], 50, 3.2)
    covers_away()
    erp_idle()
    rr = P.H["receipt_root"]
    fr = b.w("reads")
    L.key(rr, "scale", [(0, (1, 0.001, 1)), (fr - 4, (1, 0.001, 1)), (fr + 70, (1, 1, 1))])
    blink(bpy.data.materials["pr_led_1"], fr - 4, fr + 70, period=2, hi=3.0, seed=3)


def shot_close(b):
    # a slow pull-back that starts on the model and ends on the whole machine
    f1 = b.w("ledgerline") + 10
    cam(0, [(0, (-0.6, -4.3, 1.9), (0.6, 0.4, 1.0)), (f1, (-2.6, -9.6, 2.9), (0.5, 0.4, 0.85)),
            (b.frames - 1, (-2.9, -10.2, 3.1), (0.45, 0.4, 0.85))], 30, 8.0, lens_keys=[(0, 30.0), (f1, 24.0)])
    covers_away()
    P.H["plug"].location.x = P.H["plug_x"]
    full_stack(4)
    L.em_keys(P.H["clamp_glow"], [(0, 2.5)])
    erp_idle()
    erp_busy(10, b.frames - 1, seed=9)
    P.H["receipt_root"].scale = (1, 1, 1)
    for i, m in enumerate(P.H["layer_mats"]):
        L.em_keys(m, [(0, 0.9)])
    period = 75
    for k in range(0, b.frames, period):
        send(f"c1_{k}", "c_emma_bench", k, k + 40)
        send(f"c2_{k}", "c_bench_model", k + 20, k + 60)
        send(f"c3_{k}", "c_model_guard", k + 40, k + 70)
        send(f"c4_{k}", "mcp", k + 70, k + 95)
        send(f"c5_{k}", "legacy", k + 90, k + 130, L.SKY_L, 0.05)
        send(f"c6_{k}", "c_rack_bench", k + 50, k + 110, L.GREEN_L)


SHOTS = {"chat": shot_chat, "harness": shot_harness, "model": shot_model, "guard": shot_guard, "erp": shot_erp,
         "loop": shot_loop, "refuse": shot_refuse, "preview": shot_preview, "write": shot_write,
         "receipt": shot_receipt, "close": shot_close}


# ------------------------------------------------------------------ export + main
def export_proj(sc, path):
    out = {}
    w, h = sc.render.resolution_x, sc.render.resolution_y
    for f in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f)
        c = cam_at(f)
        row = {"_cam": c.name}
        for name, o in P.A.items():
            co = world_to_camera_view(sc, c, o.matrix_world.translation)
            row[name] = [round(co.x * w, 1), round((1 - co.y) * h, 1), round(co.z, 3)]
        out[f] = row
    json.dump(out, open(path, "w"))


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--shot", required=True)
    ap.add_argument("--outdir", default="/tmp/blend")
    a = ap.parse_args(argv)
    b = L.Beats(a.shot)
    sc = L.reset(b.frames)
    L.studio(sc)
    P.build_all()
    SHOTS[a.shot](b)
    L.configure(sc)
    L.smooth_all()
    for f0, c in CAMS:  # camera cuts are hard: make camera keys at a cut frame constant-safe
        pass
    os.makedirs(os.path.join(a.outdir, "proj"), exist_ok=True)
    export_proj(sc, os.path.join(a.outdir, "proj", f"{a.shot}.json"))
    sc.frame_set(0)
    path = os.path.join(a.outdir, f"{a.shot}.blend")
    L.save(sc, path)
    print("SAVED", path, b.frames)


main()
