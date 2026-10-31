"""Props for the L2 finale (v5), "The whole machine", on top of l2kit (owned by the finale; nothing else imports it).

  Book            collects light keys per material (base levels + pulses, combined by max) and writes them once, so
                  overlapping passes up the stack never fight over the same keyframe
  block_tower_f   the 24-floor block stack of the "structure" film (attention bay with 14 heads, MLP fin bank, lens),
                  with optional per-head LED materials so single heads can light on their own
  cache_shelves   the KV cache: one slim shelf per block beside the stack, two strips of 120 slots (keys violet,
                  values warm white); a keyable 'reveal' per strip fills the slots in position order
  light_bar       a thin emissive bar (keyable 'glow')
"""
import math

import bpy
from mathutils import Vector

import l2kit as K


class Book:
    """Per-material light envelopes. base(mat, [(f, v)]) sets a piecewise-linear floor; pulse(mat, f, peak, ...) adds
    a triangle. write() samples max(base, pulses) at every key time and keys the 'glow' (or another) value node."""

    def __init__(self):
        self.base, self.pulses, self.node = {}, {}, {}

    def set_base(self, m, keys, node="glow"):
        self.base.setdefault(m.name, (m, []))[1].extend(keys)
        self.node[m.name] = node

    def pulse(self, m, f, peak, rise=3, hold=2, fall=10, node="glow"):
        self.pulses.setdefault(m.name, (m, []))[1].append((f - rise, f, f + hold, f + hold + fall, peak))
        self.node[m.name] = node
        self.base.setdefault(m.name, (m, []))

    @staticmethod
    def _pw(keys, t):
        if not keys:
            return 0.0
        ks = sorted(keys)
        if t <= ks[0][0]:
            return ks[0][1]
        for (a, va), (b, vb) in zip(ks, ks[1:]):
            if a <= t <= b:
                return va if b == a else va + (vb - va) * (t - a) / (b - a)
        return ks[-1][1]

    def write(self):
        for name, (m, bkeys) in self.base.items():
            ps = self.pulses.get(name, (m, []))[1]
            times = {int(f) for f, _ in bkeys}
            for p in ps:
                times.update(int(x) for x in p[:4])
            times = sorted(t for t in times if t >= 0)
            if not times:
                continue
            out = []
            for t in times:
                v = self._pw(bkeys, t)
                for a, b, c, d, pk in ps:
                    if a <= t <= d:
                        e = (t - a) / max(1, b - a) if t < b else (1.0 if t <= c else 1 - (t - c) / max(1, d - c))
                        v = max(v, self._pw(bkeys, t) + (pk - self._pw(bkeys, t)) * max(0.0, min(1.0, e)))
                out.append((t, v))
            K.keyval(m.node_tree.nodes[self.node[name]].outputs[0], out)


def block_tower_f(name, loc, floors=24, pitch=0.16, w=1.6, d=0.62, heads=14, fins=36, head_mats=()):
    """props_s456.block_tower, plus own LED materials for the heads in `head_mats` ({(floor, head)}, 1-based floor,
    0-based head) -> out["head"][(k, j)]. Pins as block_tower, plus <name>_f<k>_h<j>_pin for those heads."""
    root = K.empty(name, loc)
    out = {"root": root, "floors": [], "att": [], "mlp": [], "lens": [], "z": [], "head": {}}
    xa0, xa1 = -w / 2 + 0.06, 0.12
    xm0, xm1 = 0.2, w / 2 - 0.06
    for k in range(1, floors + 1):
        z = 0.08 + (k - 1) * pitch
        fr = K.empty(f"{name}_f{k}", (0, 0, z), parent=root)
        K.rbox(f"{name}_f{k}_slab", (w, d, 0.03), bevel=0.009, seg=4, mat=K.M("alu_dark"), loc=(0, 0, 0.015), parent=fr)
        K.rbox(f"{name}_f{k}_trim", (w + 0.004, 0.006, 0.008), bevel=0.002, seg=2, mat=K.M("alu"), loc=(0, -d / 2, 0.024), parent=fr)
        am = K.glow_mat(f"att_{k}", K.SKY, 0.0)
        mm = K.glow_mat(f"mlp_{k}", K.lin("#ffe2a8"), 0.0)
        lm = K.light_mat(f"lens_{k}", K.SKY, 0.0)
        sp = (xa1 - xa0) / heads
        for j in range(heads):
            x = xa0 + (j + 0.5) * sp
            K.rbox(f"{name}_f{k}_h{j}", (sp * 0.74, d * 0.62, 0.04), bevel=0.006, seg=3, mat=K.M("graphite"), loc=(x, 0.02, 0.05), parent=fr)
            hm = am
            if (k, j) in head_mats:
                hm = K.glow_mat(f"head_{k}_{j}", K.SKY, 0.0)
                out["head"][(k, j)] = hm
                K.empty(f"{name}_f{k}_h{j}_pin", (x, -d * 0.29, 0.075), parent=fr)
            K.rbox(f"{name}_f{k}_h{j}_led", (sp * 0.5, 0.01, 0.008), bevel=0.002, seg=2, mat=hm, loc=(x, -d * 0.29, 0.064), parent=fr)
        fs = (xm1 - xm0) / fins
        for j in range(fins):
            x = xm0 + (j + 0.5) * fs
            K.rbox(f"{name}_f{k}_fin{j}", (fs * 0.42, d * 0.7, 0.07), bevel=0.0015, seg=2, mat=K.M("alu"), loc=(x, 0.0, 0.065), parent=fr)
        K.rbox(f"{name}_f{k}_mlpled", (xm1 - xm0, 0.01, 0.008), bevel=0.002, seg=2, mat=mm, loc=((xm0 + xm1) / 2, -d * 0.36, 0.035), parent=fr)
        barrel = K.cyl(f"{name}_f{k}_lens", 0.03, 0.05, K.M("alu"), loc=(-w / 2 - 0.07, -d / 2 + 0.06, 0.05), verts=32, bevel=0.003, parent=fr)
        barrel.rotation_euler = (math.pi / 2, 0, 0)
        core = K.cyl(f"{name}_f{k}_lenscore", 0.021, 0.054, lm, loc=(-w / 2 - 0.07, -d / 2 + 0.06, 0.05), verts=24, parent=fr)
        core.rotation_euler = (math.pi / 2, 0, 0)
        K.empty(f"{name}_att{k}", ((xa0 + xa1) / 2, -d / 2, 0.07), parent=fr)
        K.empty(f"{name}_mlp{k}", ((xm0 + xm1) / 2, -d / 2, 0.07), parent=fr)
        K.empty(f"{name}_side{k}", (w / 2 + 0.05, -d / 2, 0.04), parent=fr)
        out["floors"].append(fr)
        out["att"].append(am)
        out["mlp"].append(mm)
        out["lens"].append(lm)
        out["z"].append(z)
    H = 0.08 + (floors - 1) * pitch + 0.1
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.cyl(f"{name}_post{sx}{sy}", 0.016, H, K.M("alu"), loc=(sx * (w / 2 + 0.025), sy * (d / 2 - 0.04), H / 2), verts=24, parent=root)
    out["H"] = H
    return out


def cache_shelves(name, tower, x0, length=0.8, slots=120, depth=0.26, y=0.0):
    """One shelf per floor of `tower`, from local x0 to x0+length beside it: a dark slab with two slot strips on its
    front (keys on top, values below). out["k"][k], out["v"][k]: the strips' materials (keyable 'reveal' 0..1 = filled
    slots / slots, and 'glow'). Pins: <name>_k<k> (left end of the shelf front)."""
    out = {"k": {}, "v": {}}
    root = tower["root"]
    for k, fr in enumerate(tower["floors"], start=1):
        sh = K.empty(f"{name}_s{k}", (x0, y, 0.0), parent=fr)
        K.rbox(f"{name}_s{k}_slab", (length, depth, 0.022), bevel=0.006, seg=3, mat=K.M("alu_dark"),
               loc=(length / 2, 0, 0.03), parent=sh)
        K.rbox(f"{name}_s{k}_face", (length + 0.004, 0.008, 0.05), bevel=0.003, seg=2, mat=K.M("graphite"),
               loc=(length / 2, -depth / 2 - 0.002, 0.055), parent=sh)
        for row, (col, key) in enumerate(((K.K_COL, "k"), (K.V_COL, "v"))):
            m = K.cells_mat(f"{name}_{key}{k}", [1.0] * slots, slots, 1, col, vmax=1.0, strength=0.0, reveal=0.0, dim=0.0)
            K.plane(f"{name}_{key}{k}_strip", length - 0.02, 0.016, m, loc=(length / 2, -depth / 2 - 0.0075, 0.066 - row * 0.021), parent=sh)
            out[key][k] = m
        K.empty(f"{name}_k{k}", (0.0, -depth / 2 - 0.01, 0.06), parent=sh)
        K.empty(f"{name}_e{k}", (length, -depth / 2 - 0.01, 0.06), parent=sh)
    # two thin posts carry the shelves
    H = tower["H"]
    for sx, xx in enumerate((x0 + 0.02, x0 + length - 0.02)):
        K.cyl(f"{name}_post{sx}", 0.012, H, K.M("alu"), loc=(xx, y + depth / 2 - 0.03, H / 2), verts=20, parent=root)
    return out


def light_bar(name, size, loc, color, parent=None, strength=0.0):
    m = K.light_mat(name + "_m", color, strength)
    o = K.rbox(name, size, bevel=min(size) * 0.45, seg=2, mat=m, loc=loc, parent=parent)
    o.visible_shadow = False
    return o, m
