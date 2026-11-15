"""PROJECT LIGHTPATH — 一次跨越 · 30 s cinematic Blender blockout (V1.0)

Six shots × 150 frames, 720×1280 (9:16), 30 fps, global frames 1–900, Workbench grey-box.
Story: one packet leaves GPU A as an electrical signal, is converted to light in the TX transceiver,
crosses a fiber, is detected in the RX transceiver and arrives at GPU B.

Usage (run from this directory):
  blender -b --factory-startup --python-exit-code 1 --python build_scene.py -- save
  blender -b --factory-startup --python-exit-code 1 --python build_scene.py -- stills 1,75,150,...   [--half]
  blender -b --factory-startup --python-exit-code 1 --python build_scene.py -- anim [first] [last]
Frames go to out/frames/f####.png (global frame numbers). scene.blend is saved every run.

Units: 1 BU = 1 cm. +Z up, floor z = 0. Rack fronts face +Y (the aisle where the cameras are).
Both servers are the same model: GPU at the back of the board (−Y), NIC in the middle,
OSFP-style cages at the front I/O edge (+Y). TX data flows +Y on board A, RX data flows −Y on board B.
Sizes are plausible proportions, not engineering drawings. Inside the transceiver the optical lane is
drawn hugely enlarged (see REVIEW_REPORT.md, "Deliberate simplifications").
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, SHOT_LEN, N_SHOTS = 30, 150, 6
RES_X, RES_Y = 720, 1280
SHOTS = [('S01', 'departure'), ('S02', 'electrical'), ('S03', 'modulation'),
         ('S04', 'fiber'), ('S05', 'reception'), ('S06', 'arrival')]


def G(shot, local):
    """global frame of shot (1-based) local frame (1..150)"""
    return (shot - 1) * SHOT_LEN + local


# ------------------------------------------------------------------ colours (Workbench object colour, linear)
C_AMBER = (1.00, 0.50, 0.08, 1)          # electrical signal (restrained amber)
C_CYAN = (0.08, 0.85, 1.00, 1)           # optical signal (infrared, shown as cyan)
C_CYAN_DIM = (0.05, 0.42, 0.52, 1)       # steady laser carrier (unmodulated)
C_PCB = (0.055, 0.15, 0.075, 1)          # muted green
C_TRACE = (0.13, 0.27, 0.15, 1)          # copper under solder mask: lighter green, NOT copper-coloured
C_PKG = (0.22, 0.22, 0.23, 1)            # package substrate
C_DIE = (0.10, 0.10, 0.115, 1)           # silicon die
C_DIE_ACTIVE = (0.30, 0.30, 0.34, 1)     # GPU die while computing (neutral, no signal colour)
C_HBM = (0.32, 0.32, 0.33, 1)
C_METAL = (0.55, 0.55, 0.56, 1)          # cages, module shell
C_METAL_DK = (0.36, 0.36, 0.37, 1)
C_CHASSIS = (0.40, 0.40, 0.41, 1)
C_RACK = (0.24, 0.24, 0.25, 1)
C_SERVER = (0.34, 0.34, 0.35, 1)
C_FACE = (0.27, 0.27, 0.28, 1)
C_FLOOR = (0.13, 0.13, 0.135, 1)
C_SI = (0.30, 0.31, 0.34, 1)             # photonic chip (PIC)
C_WG = (0.48, 0.50, 0.54, 1)             # waveguide ridge (inactive)
C_PAD = (0.62, 0.62, 0.60, 1)            # metal pads / electrodes / bond wires
C_FIBER = (0.70, 0.74, 0.78, 0.28)       # translucent fiber jacket / coating
C_CABLE = (0.62, 0.66, 0.72, 0.30)
C_PLUG = (0.42, 0.44, 0.47, 1)
C_BOOT = (0.30, 0.31, 0.33, 1)

# ------------------------------------------------------------------ layout constants (cm)
CX_A, CX_B = -32.0, 32.0                 # rack / server centre x
LANE_DX = -6.0                           # the used lane (GPU, NIC, cage) sits at server cx + LANE_DX
XL_A, XL_B = CX_A + LANE_DX, CX_B + LANE_DX
SRV_Z0 = 186.0                           # chassis floor bottom (top server slot)
PCB_TOP = 187.5
FACE_Y0, FACE_Y1 = 43.6, 44.4            # chassis I/O faceplate
GPU_Y, NIC_Y = 0.0, 13.0
GPU_HALF, NIC_HALF = 3.75, 2.0
CAGE_Y0, CAGE_Y1, CAGE_HW, CAGE_TOP = 36.5, 45.6, 1.25, 189.05
CONN_Y1 = 37.4                           # cage connector front = module rear
MOD_Y0, MOD_LEN = 37.4, 10.0
MOD_HW, MOD_Z0, MOD_Z1 = 1.13, 187.60, 188.90
MPCB_TOP = 187.84
PIC_TOP = 187.91
WG_R = 0.0125                            # drawn waveguide radius (hugely enlarged; see report)
WG_Z = PIC_TOP + WG_R
FIB_Z = 188.25                           # MPO / cable centre height
CABLE_R = 0.18
PAIR_DX = [-1.05, -0.35, 0.35, 1.05]     # board diff pairs relative to lane x; index 1 is the story lane
PAIR_HALF = 0.09                         # half spacing of the two lines of a pair
REP = 1                                  # representative pair index
BITS = [1, 0, 1, 1, 0, 0, 1, 0]          # the same 8-bit pattern in every representation

# ------------------------------------------------------------------ helpers
_unit_cube = None
_unit_cyl = None


def unit_cube():
    global _unit_cube
    if _unit_cube is None:
        me = bpy.data.meshes.new('UnitCube')
        v = [(x, y, z) for x in (-.5, .5) for y in (-.5, .5) for z in (-.5, .5)]
        f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        me.from_pydata(v, [], f)
        me.update()
        _unit_cube = me
    return _unit_cube


def unit_cyl(n=24):
    global _unit_cyl
    if _unit_cyl is None:
        me = bpy.data.meshes.new('UnitCylinderZ')
        v, f = [], []
        for i in range(n):
            a = 2 * math.pi * i / n
            v += [(math.cos(a), math.sin(a), -.5), (math.cos(a), math.sin(a), .5)]
        for i in range(n):
            j = (i + 1) % n
            f.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
        f.append(tuple(2 * i for i in reversed(range(n))))
        f.append(tuple(2 * i + 1 for i in range(n)))
        me.from_pydata(v, [], f)
        for p in me.polygons:
            p.use_smooth = len(p.vertices) == 4
        me.update()
        _unit_cyl = me
    return _unit_cyl


COLLS = {}


def coll(name, parent=None):
    if name in COLLS:
        return COLLS[name]
    c = bpy.data.collections.new(name)
    if parent is None:
        parent = COLLS.get('LIGHTPATH', bpy.context.scene.collection)
    parent.children.link(c)
    COLLS[name] = c
    return c


def _link(o, c, color):
    c.objects.link(o)
    o.color = color
    return o


def box(name, c, x0, x1, y0, y1, z0, z1, color):
    o = bpy.data.objects.new(name, unit_cube())
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    o.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    return _link(o, c, color)


def boxc(name, c, cx, cy, cz, sx, sy, sz, color):
    return box(name, c, cx - sx / 2, cx + sx / 2, cy - sy / 2, cy + sy / 2, cz - sz / 2, cz + sz / 2, color)


def cyl(name, c, center, r, h, color, axis='Z'):
    o = bpy.data.objects.new(name, unit_cyl())
    o.location = center
    o.scale = (r, r, h)
    if axis == 'Y':
        o.rotation_euler = (math.radians(90), 0, 0)
    elif axis == 'X':
        o.rotation_euler = (0, math.radians(90), 0)
    return _link(o, c, color)


def fillet(points, r, n=10):
    """polyline with circular-ish fillets of radius r at the inner corners"""
    P = [Vector(p) for p in points]
    out = [P[0]]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]
        d1, d2 = (b - a), (c - b)
        l1, l2 = d1.length, d2.length
        d1n, d2n = d1.normalized(), d2.normalized()
        ang = d1n.angle(d2n) if 0 < l1 and 0 < l2 else 0
        if ang < 1e-3:
            out.append(b)
            continue
        t = min(r * math.tan(ang / 2), 0.45 * l1, 0.45 * l2)
        p0, p2 = b - d1n * t, b + d2n * t
        for k in range(n + 1):           # quadratic Bezier through the corner (close to an arc)
            u = k / n
            out.append((1 - u) ** 2 * p0 + 2 * (1 - u) * u * b + u ** 2 * p2)
    out.append(P[-1])
    return out


def path_len(pts):
    return sum((Vector(pts[i + 1]) - Vector(pts[i])).length for i in range(len(pts) - 1))


def curve_obj(name, c, pts, radius, color, flat=None):
    """POLY curve along pts; radius = round tube; flat=(w,h) for a flat strip (traces)."""
    cd = bpy.data.curves.new(name, 'CURVE')
    cd.dimensions = '3D'
    sp = cd.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1)
    if flat:
        prof = bpy.data.curves.new(name + '_prof', 'CURVE')
        prof.dimensions = '2D'
        ps = prof.splines.new('POLY')
        w, h = flat
        ps.points.add(3)
        for i, (u, v) in enumerate([(-w / 2, 0), (w / 2, 0), (w / 2, h), (-w / 2, h)]):
            ps.points[i].co = (u, v, 0, 1)
        ps.use_cyclic_u = True
        po = bpy.data.objects.new(name + '_profile', prof)
        COLLS['_PROFILES'].objects.link(po)
        cd.bevel_mode = 'OBJECT'
        cd.bevel_object = po
        cd.use_fill_caps = True
    else:
        cd.bevel_depth = radius
        cd.bevel_resolution = 3
        cd.use_fill_caps = True
    cd.bevel_factor_mapping_start = 'SPLINE'
    cd.bevel_factor_mapping_end = 'SPLINE'
    o = bpy.data.objects.new(name, cd)
    return _link(o, c, color)


# ------------------------------------------------------------------ animation helpers
def key(idb, path, frame, value=None, index=-1):
    if value is not None:
        setattr(idb, path, value)
    idb.keyframe_insert(path, frame=frame, index=index)


def fcurves_of(idb):
    ad = idb.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, 'fcurves'):
        try:
            return list(act.fcurves)
        except Exception:
            pass
    try:
        from bpy_extras import anim_utils
        cb = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
        if cb:
            return list(cb.fcurves)
    except Exception:
        pass
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                out += list(cb.fcurves)
    return out


def set_interp(idb, kind, handle=None):
    for fc in fcurves_of(idb):
        for kp in fc.keyframe_points:
            kp.interpolation = kind
            if handle:
                kp.handle_left_type = kp.handle_right_type = handle
        fc.update()


def key_visible_ranges(o, ranges):
    """o is rendered only inside the given global frame ranges [(f0, f1), ...]"""
    key(o, 'hide_render', 1, not any(a <= 1 <= b for a, b in ranges))
    key(o, 'hide_viewport', 1, o.hide_render)
    for a, b in ranges:
        if a > 1:
            key(o, 'hide_render', a, False)
            key(o, 'hide_viewport', a, False)
        key(o, 'hide_render', b + 1, True)
        key(o, 'hide_viewport', b + 1, True)


# ------------------------------------------------------------------ signal model
class Packet:
    """A finite 8-bit packet moving along a chain of path segments at constant speed.
    head(f) = v * (f - f0) is the arc-length position of the leading edge of bit 0.
    Bit k occupies [head - k*slot - duty*slot, head - k*slot]."""

    def __init__(self, f0, v, slot, duty=0.7, bits=BITS):
        self.f0, self.v, self.slot, self.duty, self.bits = f0, v, slot, duty, bits

    def head(self, f):
        return self.v * (f - self.f0)

    def dash(self, k, f):
        h = self.head(f) - k * self.slot
        return h - self.duty * self.slot, h

    def any_on(self, f, s0, s1):
        """1 if any '1'-dash overlaps arc-length interval [s0, s1] at frame f"""
        for k, b in enumerate(self.bits):
            if not b:
                continue
            t, h = self.dash(k, f)
            if h > s0 and t < s1:
                return 1
        return 0


def pulse_curves(prefix, c, pts, s_offset, packet, frames, radius, color, flat=None):
    """One curve per '1' bit drawn on path pts, whose arc length starts at packet coordinate s_offset."""
    L = path_len(pts)
    objs = []
    for k, b in enumerate(packet.bits):
        if not b:
            continue
        o = curve_obj(f'{prefix}_bit{k}', c, pts, radius, color, flat)
        cd = o.data
        prev_vis = None
        for f in frames:
            t, h = packet.dash(k, f)
            a = min(max((t - s_offset) / L, 0.0), 1.0)
            e = min(max((h - s_offset) / L, 0.0), 1.0)
            vis = (e - a) > 1e-4
            cd.bevel_factor_start = a if vis else 0.0
            cd.bevel_factor_end = e if vis else 0.0001
            cd.keyframe_insert('bevel_factor_start', frame=f)
            cd.keyframe_insert('bevel_factor_end', frame=f)
            if vis != prev_vis:
                o.hide_render = not vis
                o.hide_viewport = not vis
                o.keyframe_insert('hide_render', frame=f)
                o.keyframe_insert('hide_viewport', frame=f)
                prev_vis = vis
        f_last = frames[-1] + 1
        o.hide_render = o.hide_viewport = True
        o.keyframe_insert('hide_render', frame=f_last)
        o.keyframe_insert('hide_viewport', frame=f_last)
        if frames[0] > 1:
            o.keyframe_insert('hide_render', frame=1)
            o.keyframe_insert('hide_viewport', frame=1)
        set_interp(cd, 'LINEAR')
        objs.append(o)
    return objs


def color_track(o, frames, fn, base_color):
    """keys object colour every frame from fn(f) -> colour; base_color before/after"""
    o.color = base_color
    o.keyframe_insert('color', frame=1)
    for f in frames:
        o.color = fn(f)
        o.keyframe_insert('color', frame=f)
    o.color = base_color
    o.keyframe_insert('color', frame=frames[-1] + 1)
    set_interp(o, 'LINEAR')


def mix(c0, c1, k):
    k = min(max(k, 0.0), 1.0)
    return tuple(a + (b - a) * k for a, b in zip(c0, c1))


def frange(shot, a=1, b=SHOT_LEN):
    return list(range(G(shot, a), G(shot, b) + 1))


# ------------------------------------------------------------------ environment
def build_floor_and_room():
    c = coll('ENV')
    box('ENV_floor', c, -400, 400, -300, 400, -1, 0, C_FLOOR)
    for i in range(-6, 7):                                # floor tile seams every 60 cm (scale cue)
        box(f'ENV_tile_seam_x{i}', c, i * 60 - 0.3, i * 60 + 0.3, -300, 400, 0, 0.05, (0.13, 0.13, 0.14, 1))
    for j in range(-5, 7):
        box(f'ENV_tile_seam_y{j}', c, -400, 400, j * 60 - 0.3, j * 60 + 0.3, 0, 0.05, (0.13, 0.13, 0.14, 1))


def build_rack(tag, cx, c, top_server=True, hcm=True):
    """open-frame four-post rack (60 wide, 100 deep, ~197 tall), filled with 2U servers."""
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(f'{tag}_post_{"L" if sx < 0 else "R"}{"F" if sy > 0 else "B"}', c,
                cx + sx * 28.5 - 1.5, cx + sx * 28.5 + 1.5, sy * 44.5 - 1.5, sy * 44.5 + 1.5, 0, 197.5, C_RACK)
    for sy in (-1, 1):
        box(f'{tag}_topbar_{"F" if sy > 0 else "B"}', c, cx - 30, cx + 30, sy * 44.5 - 1.5, sy * 44.5 + 1.5,
            195.5, 197.5, C_RACK)
        box(f'{tag}_basebar_{"F" if sy > 0 else "B"}', c, cx - 30, cx + 30, sy * 44.5 - 1.5, sy * 44.5 + 1.5,
            0, 6, C_RACK)
    z = 8.0
    i = 0
    top_limit = 176.6 if hcm else 186.0
    rnd = random.Random(hash(tag) & 0xffff)
    while z + 8.9 <= top_limit + 0.01:
        blank = rnd.random() < 0.12
        box(f'{tag}_srv{i:02d}', c, cx - 22, cx + 22, -42, 44.4, z + 0.1, z + 8.8, C_SERVER if not blank else C_RACK)
        if not blank:
            box(f'{tag}_srv{i:02d}_face', c, cx - 22, cx + 22, 44.4, 44.9, z + 0.3, z + 8.6, C_FACE)
            for hx in (-20.5, 20.5):
                box(f'{tag}_srv{i:02d}_handle{"L" if hx < 0 else "R"}', c, cx + hx - 0.5, cx + hx + 0.5, 44.9, 46.0,
                    z + 2.0, z + 6.8, C_METAL_DK)
            for k in range(4):                           # port row / vents, purely for scale
                box(f'{tag}_srv{i:02d}_port{k}', c, cx - 6 + k * 3.2 - 1.2, cx - 6 + k * 3.2 + 1.2, 44.9, 45.2,
                    z + 3.6, z + 5.0, C_METAL_DK)
        z += 8.9
        i += 1
    if hcm:   # 1U horizontal cable manager: tray directly below the top server, fiber runs inside it
        box(f'{tag}_HCM_tray', c, cx - 30, cx + 30, 46.0, 53.0, 179.8, 180.4, C_METAL_DK)
        box(f'{tag}_HCM_back', c, cx - 30, cx + 30, 46.0, 46.4, 179.8, 184.2, C_METAL_DK)
        box(f'{tag}_HCM_lip', c, cx - 30, cx + 30, 52.6, 53.0, 179.8, 181.6, C_METAL_DK)
    if not top_server:
        box(f'{tag}_srv_top', c, cx - 22, cx + 22, -42, 44.4, 186.1, 194.8, C_SERVER)
        box(f'{tag}_srv_top_face', c, cx - 22, cx + 22, 44.4, 44.9, 186.3, 194.6, C_FACE)


# ------------------------------------------------------------------ server (board) — same model for A and B
def build_server(S, cx):
    """S = 'A' or 'B'. Returns dict of key world points."""
    xl = cx + LANE_DX
    top = coll(f'SERVER_{S}')
    ch = coll(f'CHASSIS_{S}', top)
    z0 = SRV_Z0
    box(f'CHASSIS_{S}_floor', ch, cx - 22, cx + 22, -42, FACE_Y0, z0, z0 + 0.3, C_CHASSIS)
    for sx in (-1, 1):
        box(f'CHASSIS_{S}_wall_{"L" if sx < 0 else "R"}', ch, cx + sx * 22 - 0.2, cx + sx * 22 + 0.2, -42, FACE_Y1,
            z0, z0 + 8.9, C_CHASSIS)
    box(f'CHASSIS_{S}_wall_back', ch, cx - 22, cx + 22, -42.4, -42, z0, z0 + 8.9, C_CHASSIS)
    # I/O faceplate with three cage openings (lane cage in the middle)
    cage_xs = [xl - 3.2, xl, xl + 3.2]
    box(f'CHASSIS_{S}_face_bottom', ch, cx - 22, cx + 22, FACE_Y0, FACE_Y1, z0, PCB_TOP - 0.05, C_CHASSIS)
    box(f'CHASSIS_{S}_face_top_L', ch, cx - 22, xl - 1.6, FACE_Y0, FACE_Y1, CAGE_TOP + 0.1, z0 + 8.9, C_CHASSIS)
    face_cut = box(f'CHASSIS_{S}_face_top_lane', ch, xl - 1.6, xl + 1.6, FACE_Y0, FACE_Y1, CAGE_TOP + 0.1, z0 + 8.9,
                   C_CHASSIS)
    box(f'CHASSIS_{S}_face_top_R', ch, xl + 1.6, cx + 22, FACE_Y0, FACE_Y1, CAGE_TOP + 0.1, z0 + 8.9, C_CHASSIS)
    edges = [cx - 22] + sum([[x - CAGE_HW - 0.05, x + CAGE_HW + 0.05] for x in cage_xs], []) + [cx + 22]
    for i in range(0, len(edges), 2):
        box(f'CHASSIS_{S}_face_mid{i // 2}', ch, edges[i], edges[i + 1], FACE_Y0, FACE_Y1, PCB_TOP - 0.05,
            CAGE_TOP + 0.1, C_CHASSIS)
    # fans at the back
    fc = coll(f'FANS_{S}', top)
    for i in range(6):
        fx = cx - 18.3 + i * 7.3
        box(f'FAN_{S}_{i}', fc, fx - 3.4, fx + 3.4, -41.5, -35.5, z0 + 0.3, z0 + 8.2, C_METAL_DK)
        cyl(f'FAN_{S}_{i}_hub', fc, (fx, -35.3, z0 + 4.25), 1.2, 0.5, C_FACE, axis='Y')

    # ---- board
    bd = coll(f'BOARD_{S}', top)
    box(f'PCB_{S}', bd, cx - 21, cx + 21, -33, 43.4, PCB_TOP - 0.2, PCB_TOP, C_PCB)
    for i in range(10):                                 # standoffs
        pass
    # host CPUs with heatsinks and DIMM rows (system context, back half of the board)
    hc = coll(f'HOST_{S}', bd)
    for k, hx in enumerate((cx - 11, cx + 9)):
        box(f'HOST_{S}_cpu{k}_heatsink', hc, hx - 4.5, hx + 4.5, -26, -17, PCB_TOP, PCB_TOP + 5.6, C_METAL_DK)
        for f in range(9):
            box(f'HOST_{S}_cpu{k}_fin{f}', hc, hx - 4.5 + f * 1.1, hx - 4.5 + f * 1.1 + 0.25, -26, -17, PCB_TOP + 5.6,
                PCB_TOP + 6.6, C_METAL_DK)
        for d in range(4):
            for side in (-1, 1):
                dx = hx + side * (5.6 + d * 0.9)
                box(f'HOST_{S}_cpu{k}_dimm{"L" if side < 0 else "R"}{d}', hc, dx - 0.2, dx + 0.2, -29, -14,
                    PCB_TOP, PCB_TOP + 3.2, C_HBM)

    # GPU (lane GPU = GPU_S; neighbour accelerator beside it)
    def gpu(name, gx, gy, cc):
        box(f'{name}_substrate', cc, gx - GPU_HALF, gx + GPU_HALF, gy - GPU_HALF, gy + GPU_HALF, PCB_TOP,
            PCB_TOP + 0.3, C_PKG)
        die = box(f'{name}_die', cc, gx - 1.8, gx + 1.8, gy - 1.5, gy + 1.5, PCB_TOP + 0.3, PCB_TOP + 0.42, C_DIE)
        for sx in (-1, 1):
            for sy in (-1, 1):
                box(f'{name}_HBM_{"L" if sx < 0 else "R"}{"F" if sy > 0 else "B"}', cc, gx + sx * 2.2,
                    gx + sx * 3.1, gy + sy * 0.1, gy + sy * 1.45, PCB_TOP + 0.3, PCB_TOP + 0.6, C_HBM)
        box(f'{name}_stiffener_F', cc, gx - GPU_HALF, gx + GPU_HALF, gy + GPU_HALF - 0.25, gy + GPU_HALF,
            PCB_TOP + 0.3, PCB_TOP + 0.45, C_METAL_DK)
        box(f'{name}_stiffener_B', cc, gx - GPU_HALF, gx + GPU_HALF, gy - GPU_HALF, gy - GPU_HALF + 0.25,
            PCB_TOP + 0.3, PCB_TOP + 0.45, C_METAL_DK)
        return die
    gpu_c = coll(f'GPU_{S}', bd)
    die = gpu(f'GPU_{S}', xl, GPU_Y, gpu_c)
    nb_c = coll(f'GPU_{S}_neighbor', bd)
    gpu(f'GPU_{S}_neighbor', cx + 10, GPU_Y, nb_c)
    # VRM inductors around the GPUs
    vr = coll(f'VRM_{S}', bd)
    for i in range(8):
        box(f'VRM_{S}_L{i}', vr, xl - 6.2, xl - 5.4, -4.4 + i * 1.15 - 0.4, -4.4 + i * 1.15 + 0.4, PCB_TOP,
            PCB_TOP + 0.65, C_METAL_DK)
        box(f'VRM_{S}_B{i}', vr, xl - 4.2 + i * 1.15 - 0.4, xl - 4.2 + i * 1.15 + 0.4, -6.4, -5.6, PCB_TOP,
            PCB_TOP + 0.65, C_METAL_DK)
        box(f'VRM_{S}_N{i}', vr, cx + 10 - 4.2 + i * 1.15 - 0.4, cx + 10 - 4.2 + i * 1.15 + 0.4, -6.4, -5.6,
            PCB_TOP, PCB_TOP + 0.65, C_METAL_DK)
    # NIC
    nic_c = coll(f'NIC_{S}', bd)
    box(f'NIC_{S}_package', nic_c, xl - NIC_HALF, xl + NIC_HALF, NIC_Y - NIC_HALF, NIC_Y + NIC_HALF, PCB_TOP,
        PCB_TOP + 0.25, C_PKG)
    nic_die = box(f'NIC_{S}_die', nic_c, xl - 0.9, xl + 0.9, NIC_Y - 0.9, NIC_Y + 0.9, PCB_TOP + 0.25, PCB_TOP + 0.35,
                  C_DIE)
    # passive components (deterministic), kept off the lane corridor
    pc = coll(f'PASSIVES_{S}', bd)
    rnd = random.Random(7 if S == 'A' else 7)
    n = 0
    for _ in range(900):
        px = rnd.uniform(cx - 20, cx + 20)
        py = rnd.uniform(-12, 34)
        if abs(px - xl) < 2.0 and -5 < py < 37:
            continue
        if abs(px - xl) < GPU_HALF + 0.3 and abs(py - GPU_Y) < GPU_HALF + 0.3:
            continue
        if abs(px - cx - 10) < GPU_HALF + 0.3 and abs(py - GPU_Y) < GPU_HALF + 0.3:
            continue
        if abs(px - xl) < 6.6 and -6.9 < py < 5:
            continue
        if py > 34 and abs(px - xl) < 6:
            continue
        w, d = rnd.choice([(0.2, 0.1), (0.1, 0.2), (0.32, 0.16), (0.16, 0.32), (0.6, 0.6)])
        h = 0.1 if w < 0.5 else 0.35
        box(f'PASSIVE_{S}_{n:03d}', pc, px - w / 2, px + w / 2, py - d / 2, py + d / 2, PCB_TOP, PCB_TOP + h,
            C_METAL_DK if w > 0.5 else C_HBM)
        n += 1
        if n >= 220:
            break
    # background trace bundles (context only)
    bt = coll(f'BG_TRACES_{S}', bd)
    for k in range(10):
        y = -9 - k * 0.35
        curve_obj(f'BG_TRACE_{S}_{k}', bt, [(xl - 3.5, y, PCB_TOP), (cx + 6.5, y, PCB_TOP)], 0, C_TRACE,
                  flat=(0.07, 0.006))
    for k in range(8):
        x = cx + 4 + k * 0.35
        curve_obj(f'BG_TRACE_{S}_v{k}', bt, [(x, 5.0, PCB_TOP), (x, 30.0 - k * 0.3, PCB_TOP),
                                             (x + 3, 33.0 - k * 0.3, PCB_TOP), (x + 3, 36.0, PCB_TOP)], 0, C_TRACE,
                  flat=(0.07, 0.006))

    # ---- lane traces: GPU -> NIC (4 pairs) and NIC -> cage (4 pairs)
    pname = 'TX_ELECTRICAL_PATH' if S == 'A' else 'RX_ELECTRICAL_PATH'
    tp = coll(pname, top)
    y_g, y_n0, y_n1, y_c = GPU_Y + GPU_HALF, NIC_Y - NIC_HALF, NIC_Y + NIC_HALF, CAGE_Y0 + 0.3
    lines = {}
    for i, dx in enumerate(PAIR_DX):
        for j, sgn in enumerate((-1, 1)):
            x = xl + dx + sgn * PAIR_HALF
            tag = f'pair{i}_{"N" if sgn < 0 else "P"}'
            p1 = [(x, y_g, PCB_TOP), (x, y_n0, PCB_TOP)]
            # NIC -> cage pairs: small 45° jog halfway (typical routing), then straight into the connector
            jog = 0.25 * (1 if i < 2 else -1) * 0
            p2 = [(x, y_n1, PCB_TOP), (x, y_c, PCB_TOP)]
            curve_obj(f'{pname}_gpu_nic_{tag}', tp, p1, 0, C_TRACE, flat=(0.07, 0.006))
            curve_obj(f'{pname}_nic_cage_{tag}', tp, p2, 0, C_TRACE, flat=(0.07, 0.006))
            lines[(i, sgn)] = (p1, p2)
            # AC-coupling capacitor on each line of the NIC->cage pairs (series element, sits on the trace)
            box(f'{pname}_ACcap_{tag}', tp, x - 0.06, x + 0.06, 23.9, 24.15, PCB_TOP, PCB_TOP + 0.07, C_HBM)
        # vias where the pairs leave the package fields
        for yv in (y_g + 0.5, y_n1 + 0.5):
            for sgn in (-1, 1):
                cyl(f'{pname}_via_{i}_{"N" if sgn < 0 else "P"}_{yv:.0f}', tp, (xl + dx + sgn * PAIR_HALF, yv, PCB_TOP + 0.004),
                    0.05, 0.01, C_PAD)

    # ---- cages (lane cage + two neighbours). top plate is a separate object so it can be cut away.
    cage_name = 'TX_CAGE' if S == 'A' else 'RX_CAGE'
    cg = coll(cage_name, top)
    cage_tops = []
    for ci, x in enumerate(cage_xs):
        nm = cage_name if ci == 1 else f'{cage_name}_neighbor{ci}'
        box(f'{nm}_floor', cg, x - CAGE_HW, x + CAGE_HW, CAGE_Y0, CAGE_Y1, PCB_TOP, PCB_TOP + 0.06, C_METAL)
        box(f'{nm}_side_L', cg, x - CAGE_HW, x - CAGE_HW + 0.06, CAGE_Y0, CAGE_Y1, PCB_TOP, CAGE_TOP, C_METAL)
        box(f'{nm}_side_R', cg, x + CAGE_HW - 0.06, x + CAGE_HW, CAGE_Y0, CAGE_Y1, PCB_TOP, CAGE_TOP, C_METAL)
        box(f'{nm}_rear', cg, x - CAGE_HW, x + CAGE_HW, CAGE_Y0, CAGE_Y0 + 0.06, PCB_TOP, CAGE_TOP, C_METAL)
        t = box(f'{nm}_top', cg, x - CAGE_HW, x + CAGE_HW, CAGE_Y0, CAGE_Y1, CAGE_TOP - 0.06, CAGE_TOP, C_METAL)
        if ci == 1:
            cage_tops.append(t)
        box(f'{nm}_connector', cg, x - 1.1, x + 1.1, CAGE_Y0 + 0.1, CONN_Y1, PCB_TOP + 0.06, PCB_TOP + 0.9, C_METAL_DK)
        if ci != 1:   # empty neighbour ports carry a dust plug at the opening
            box(f'{nm}_dustplug', cg, x - 1.1, x + 1.1, CAGE_Y1 - 0.6, CAGE_Y1 + 0.4, PCB_TOP + 0.15, CAGE_TOP - 0.15,
                C_FACE)
    return dict(xl=xl, die=die, nic_die=nic_die, lines=lines, cage_tops=cage_tops + [face_cut])


# ------------------------------------------------------------------ transceiver (identical design for A and B)
def build_transceiver(S, xl):
    """OSFP-style pluggable, linear-drive (no DSP) for clarity. Contains one TX lane (x = xl-0.45)
    and one RX lane (x = xl+0.45). In module A only the TX lane is active, in module B only the RX lane."""
    name = 'TX_TRANSCEIVER' if S == 'A' else 'RX_TRANSCEIVER'
    top = coll(name)
    Y = lambda u: MOD_Y0 + u                            # module local y -> world y
    sh = coll(f'{name}_shell', top)
    box(f'{name}_shell_floor', sh, xl - MOD_HW, xl + MOD_HW, Y(0), Y(MOD_LEN), MOD_Z0, MOD_Z0 + 0.08, C_METAL)
    for sx in (-1, 1):
        box(f'{name}_shell_side_{"L" if sx < 0 else "R"}', sh, xl + sx * MOD_HW - (0.07 if sx > 0 else 0),
            xl + sx * MOD_HW + (0.07 if sx < 0 else 0), Y(0), Y(MOD_LEN), MOD_Z0, MOD_Z1, C_METAL)
    lid = box(f'{name}_shell_lid', sh, xl - MOD_HW, xl + MOD_HW, Y(0), Y(MOD_LEN), MOD_Z1 - 0.07, MOD_Z1, C_METAL)
    box(f'{name}_shell_rear_upper', sh, xl - MOD_HW, xl + MOD_HW, Y(0), Y(0.12), 188.35, MOD_Z1, C_METAL)
    # front face with MPO receptacle opening (1.3 wide × 0.6 tall, centred at FIB_Z)
    fy0, fy1 = Y(MOD_LEN - 0.1), Y(MOD_LEN)
    box(f'{name}_shell_front_bottom', sh, xl - MOD_HW, xl + MOD_HW, fy0, fy1, MOD_Z0, FIB_Z - 0.3, C_METAL)
    box(f'{name}_shell_front_top', sh, xl - MOD_HW, xl + MOD_HW, fy0, fy1, FIB_Z + 0.3, MOD_Z1, C_METAL)
    box(f'{name}_shell_front_L', sh, xl - MOD_HW, xl - 0.65, fy0, fy1, FIB_Z - 0.3, FIB_Z + 0.3, C_METAL)
    box(f'{name}_shell_front_R', sh, xl + 0.65, xl + MOD_HW, fy0, fy1, FIB_Z - 0.3, FIB_Z + 0.3, C_METAL)
    box(f'{name}_pull_tab', sh, xl - 0.5, xl + 0.5, fy1, fy1 + 1.6, MOD_Z1 - 0.12, MOD_Z1 - 0.04, C_FACE)
    # internal PCB with edge fingers
    ib = coll(f'{name}_pcb', top)
    box(f'{name}_module_PCB', ib, xl - 1.0, xl + 1.0, Y(-0.25), Y(6.4), MPCB_TOP - 0.08, MPCB_TOP, C_PCB)
    for k in range(12):
        fx = xl - 0.85 + k * 0.155
        box(f'{name}_edge_finger{k}', ib, fx - 0.05, fx + 0.05, Y(-0.25), Y(0.3), MPCB_TOP, MPCB_TOP + 0.004, C_PAD)
    # module PCB traces (TX pair to driver, RX pair from TIA)
    tr = {}
    for lane, lx in (('TX', xl - 0.3), ('RX', xl + 0.3)):
        for sgn in (-1, 1):
            p = [(lx + sgn * 0.05, Y(0.3), MPCB_TOP), (lx + sgn * 0.05, Y(3.42), MPCB_TOP)]
            curve_obj(f'{name}_{lane}_trace_{"N" if sgn < 0 else "P"}', ib, p, 0, C_TRACE, flat=(0.04, 0.004))
            tr[(lane, sgn)] = p
    # electronics: TX driver and RX TIA
    dname = 'TX_DRIVER' if S == 'A' else 'TX_DRIVER_idle_B'
    rname = 'RX_ELECTRONICS_idle_A' if S == 'A' else 'RX_ELECTRONICS'
    dc = coll(dname, top)
    rc = coll(rname, top)
    drv = box(f'{dname}_chip', dc, xl - 0.3 - 0.225, xl - 0.3 + 0.225, Y(3.42), Y(3.87), MPCB_TOP, MPCB_TOP + 0.08,
              C_DIE)
    tia = box(f'{rname}_TIA_chip', rc, xl + 0.3 - 0.225, xl + 0.3 + 0.225, Y(3.42), Y(3.87), MPCB_TOP,
              MPCB_TOP + 0.08, C_DIE)
    # PIC
    pc = coll(f'{name}_PIC', top)
    box(f'{name}_PIC_chip', pc, xl - 0.85, xl + 0.85, Y(4.1), Y(5.9), MPCB_TOP, PIC_TOP, C_SI)
    # ---------------- TX lane on the PIC
    lname = 'LASER' if S == 'A' else 'LASER_idle_B'
    mname = 'MODULATOR' if S == 'A' else 'MODULATOR_idle_B'
    lc = coll(lname, top)
    mc = coll(mname, top)
    tx = xl - 0.45
    laser = box(f'{lname}_die', lc, tx - 0.07, tx + 0.07, Y(4.18), Y(4.42), PIC_TOP, PIC_TOP + 0.06, C_METAL_DK)
    # waveguides (TX): laser -> splitter -> two arms -> combiner -> output edge
    a_sep = 0.07
    wg_in = [(tx, Y(4.42), WG_Z), (tx, Y(4.58), WG_Z)]
    arm_L = fillet([(tx, Y(4.58), WG_Z), (tx - a_sep, Y(4.70), WG_Z), (tx - a_sep, Y(5.32), WG_Z),
                    (tx, Y(5.44), WG_Z)], 0.08, 6)
    arm_R = fillet([(tx, Y(4.58), WG_Z), (tx + a_sep, Y(4.70), WG_Z), (tx + a_sep, Y(5.32), WG_Z),
                    (tx, Y(5.44), WG_Z)], 0.08, 6)
    wg_out = [(tx, Y(5.44), WG_Z), (tx, Y(5.9), WG_Z)]
    for nm, p in (('input', wg_in), ('arm_L', arm_L), ('arm_R', arm_R), ('output', wg_out)):
        curve_obj(f'{mname}_waveguide_{nm}', mc, p, WG_R, C_WG)
    # electrodes: signal electrode along the right arm, ground along the left arm (single-drive, schematic)
    sig_el = box(f'{mname}_electrode_signal', mc, tx + 0.105, tx + 0.155, Y(4.74), Y(5.30), PIC_TOP, PIC_TOP + 0.012,
                 C_PAD)
    box(f'{mname}_electrode_ground', mc, tx - 0.155, tx - 0.105, Y(4.74), Y(5.30), PIC_TOP, PIC_TOP + 0.012, C_PAD)
    # on-chip feed from the RF pad to the signal electrode, and the bond wire from the driver
    feed = [(xl - 0.22, Y(4.22), PIC_TOP + 0.006), (xl - 0.22, Y(4.74), PIC_TOP + 0.006),
            (tx + 0.13, Y(4.74), PIC_TOP + 0.006)]
    curve_obj(f'{mname}_RF_feed', mc, feed, 0, C_PAD, flat=(0.03, 0.006))
    box(f'{mname}_RF_pad', mc, xl - 0.26, xl - 0.18, Y(4.16), Y(4.26), PIC_TOP, PIC_TOP + 0.008, C_PAD)
    bond = [(xl - 0.26, Y(3.84), MPCB_TOP + 0.08)]
    for k in range(1, 8):
        u = k / 8
        bond.append((xl - 0.26 + 0.04 * u, Y(3.84 + 0.37 * u), MPCB_TOP + 0.08 + 0.12 * math.sin(math.pi * u)
                     + (PIC_TOP - MPCB_TOP - 0.08 + 0.008) * u))
    bond.append((xl - 0.22, Y(4.21), PIC_TOP + 0.008))
    curve_obj(f'{dname}_bondwire', dc, bond, 0.006, C_PAD)
    # ---------------- RX lane on the PIC
    pname = 'PHOTODETECTOR' if S == 'B' else 'PHOTODETECTOR_idle_A'
    pdc = coll(pname, top)
    rx = xl + 0.45
    pd = box(f'{pname}_Ge_PD', pdc, rx - 0.06, rx + 0.06, Y(4.38), Y(4.62), PIC_TOP, PIC_TOP + 0.04, C_METAL_DK)
    wg_rx = [(rx, Y(5.9), WG_Z), (rx, Y(4.62), WG_Z)]
    curve_obj(f'{pname}_waveguide_input', pdc, wg_rx, WG_R, C_WG)
    pd_out = [(rx - 0.06, Y(4.5), PIC_TOP + 0.006), (xl + 0.22, Y(4.5), PIC_TOP + 0.006),
              (xl + 0.22, Y(4.22), PIC_TOP + 0.006)]
    curve_obj(f'{pname}_output_trace', pdc, pd_out, 0, C_PAD, flat=(0.03, 0.006))
    box(f'{pname}_pad', pdc, xl + 0.18, xl + 0.26, Y(4.16), Y(4.26), PIC_TOP, PIC_TOP + 0.008, C_PAD)
    bond_rx = [(xl + 0.22, Y(4.21), PIC_TOP + 0.008)]
    for k in range(1, 8):
        u = k / 8
        bond_rx.append((xl + 0.22 + 0.04 * u, Y(4.21 - 0.37 * u), PIC_TOP + 0.008 + 0.12 * math.sin(math.pi * u)
                        - (PIC_TOP - MPCB_TOP - 0.08 + 0.008) * u))
    bond_rx.append((xl + 0.26, Y(3.84), MPCB_TOP + 0.08))
    curve_obj(f'{rname}_bondwire', rc, bond_rx, 0.006, C_PAD)
    # ---------------- coupling: fiber array block at the PIC edge, internal fibers to the MPO receptacle
    cname = 'OPTICAL_COUPLING_TX' if S == 'A' else 'OPTICAL_COUPLING_RX'
    cc = coll(cname, top)
    box(f'{cname}_fiber_array_base', cc, xl - 0.75, xl + 0.75, Y(5.9), Y(6.35), MPCB_TOP, WG_Z - 0.03, C_METAL_DK)
    box(f'{cname}_fiber_array_lid', cc, xl - 0.75, xl + 0.75, Y(5.95), Y(6.35), WG_Z + 0.035, WG_Z + 0.09, C_METAL_DK)
    fibers = {}
    for lane, fx, mx in (('TX', tx, xl - 0.15), ('RX', rx, xl + 0.15)):
        p = fillet([(fx, Y(5.9), WG_Z), (fx, Y(6.6), WG_Z), (fx, Y(7.4), WG_Z + 0.05),
                    (mx, Y(8.6), FIB_Z), (mx, Y(9.3), FIB_Z)], 0.6, 8)
        curve_obj(f'{cname}_fiber_{lane}', cc, p, 0.03, C_FIBER)
        fibers[lane] = p
    box(f'{cname}_MPO_receptacle', cc, xl - 0.65, xl + 0.65, Y(9.3), Y(9.9), FIB_Z - 0.3, FIB_Z + 0.3, C_PLUG)
    return dict(lid=lid, traces=tr, drv=drv, tia=tia, laser=laser, sig_el=sig_el, pd=pd, feed=feed, bond=bond,
                wg_in=wg_in, arm_L=arm_L, arm_R=arm_R, wg_out=wg_out, wg_rx=wg_rx, pd_out=pd_out, bond_rx=bond_rx,
                fibers=fibers, Y=Y)


# ------------------------------------------------------------------ fiber route
def build_fiber():
    c = coll('FIBER_ROUTE')
    ends = {}
    for S, xl in (('A', XL_A), ('B', XL_B)):
        y0 = MOD_Y0 + MOD_LEN
        box(f'FIBER_MPO_plug_{S}', c, xl - 0.62, xl + 0.62, y0, y0 + 1.5, FIB_Z - 0.28, FIB_Z + 0.28, C_PLUG)
        box(f'FIBER_MPO_boot_{S}', c, xl - 0.4, xl + 0.4, y0 + 1.5, y0 + 3.0, FIB_Z - 0.2, FIB_Z + 0.2, C_BOOT)
        ends[S] = (xl, y0 + 3.0, FIB_Z)
    (xa, ya, za), (xb, yb, zb) = ends['A'], ends['B']
    route = fillet([(xa, ya, za), (xa, 54.5, za), (xa, 54.5, 184.0), (xa + 7, 49.5, 181.2), (xb - 7, 49.5, 181.2),
                    (xb, 54.5, 184.0), (xb, 54.5, zb), (xb, yb, zb)], 3.5, 14)
    cable = curve_obj('FIBER_ROUTE_cable', c, route, CABLE_R, C_CABLE)
    return route, cable


# ------------------------------------------------------------------ cameras
def make_camera(shot, keys, sensor=24.0):
    """keys: list of (local_frame, (x,y,z) cam, (x,y,z) target, lens). Bezier auto-clamped in Blender,
    so the motion stays editable. local frames may lie outside 1..150 (pre/post-roll keep the cut moving)."""
    tag = f'{SHOTS[shot - 1][0]}_{SHOTS[shot - 1][1]}'
    c = coll('CAMERAS')
    cd = bpy.data.cameras.new(f'CAM_{tag}')
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_height = sensor
    cd.clip_start = 0.004
    cd.clip_end = 3000
    cam = bpy.data.objects.new(f'CAM_{tag}', cd)
    tgt = bpy.data.objects.new(f'CAM_{tag}_target', None)
    tgt.empty_display_size = 0.3
    c.objects.link(cam)
    c.objects.link(tgt)
    con = cam.constraints.new('TRACK_TO')
    con.target = tgt
    con.track_axis, con.up_axis = 'TRACK_NEGATIVE_Z', 'UP_Y'
    for lf, p, t, lens in keys:
        f = G(shot, lf)
        cam.location = p
        cam.keyframe_insert('location', frame=f)
        tgt.location = t
        tgt.keyframe_insert('location', frame=f)
        cd.lens = lens
        cd.keyframe_insert('lens', frame=f)
    for idb in (cam, tgt, cd):
        set_interp(idb, 'BEZIER', 'AUTO_CLAMPED')
    return cam


# ------------------------------------------------------------------ build everything
def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = 'LIGHTPATH_master'
    root = coll('LIGHTPATH')
    prof = coll('_PROFILES')
    prof.hide_render = True
    prof.hide_viewport = True

    build_floor_and_room()
    env = coll('ENV')
    build_rack('RACK_A', CX_A, env)
    build_rack('RACK_B', CX_B, env)
    for k, x in enumerate((-96, -160, 96, 160)):
        build_rack(f'RACK_bg{k}', x, env, top_server=False)
    srvA = build_server('A', CX_A)
    srvB = build_server('B', CX_B)
    trxA = build_transceiver('A', XL_A)
    trxB = build_transceiver('B', XL_B)
    route, cable = build_fiber()

    sig = coll('SIGNALS')
    # ---------------------------------------------------------- S01/S02: GPU A -> NIC A -> cage (board A, +Y)
    xl = XL_A
    pk_board = Packet(f0=G(1, 100), v=0.17, slot=0.8)
    s_nic0 = NIC_Y - NIC_HALF - (GPU_Y + GPU_HALF)                # 7.25: packet coordinate where NIC begins
    s_nic1 = s_nic0 + 2 * NIC_HALF
    fr12 = frange(1, 95) + frange(2)
    for sgn in (-1, 1):
        p1, p2 = srvA['lines'][(REP, sgn)]
        lift = lambda p: [(x, y, z + 0.035) for x, y, z in p]
        pulse_curves(f'SIG_E_A_gpu_nic_{"N" if sgn < 0 else "P"}', sig, lift(p1), 0.0, pk_board, fr12, 0.045, C_AMBER)
        pulse_curves(f'SIG_E_A_nic_cage_{"N" if sgn < 0 else "P"}', sig, lift(p2), s_nic1, pk_board, fr12, 0.045,
                     C_AMBER)
    # launch indicator at the GPU edge (PHY) where the lane leaves the package
    phy = box('SIG_E_A_launch_PHY', sig, xl - 0.35 - 0.25, xl - 0.35 + 0.25, GPU_Y + GPU_HALF - 0.55,
              GPU_Y + GPU_HALF - 0.3, PCB_TOP + 0.3, PCB_TOP + 0.36, C_AMBER)

    def phy_col(f):
        lf = f - G(1, 0)
        if lf < 52:
            return (*C_AMBER[:3], 0.0)
        k = min((lf - 52) / 12, 1.0)
        pulse = 0.75 + 0.25 * math.sin((lf - 52) / 5.0)
        a = k * (pulse if lf < 100 else max(0.0, 1 - (lf - 100) / 25))
        return (*C_AMBER[:3], a)
    color_track(phy, frange(1), phy_col, (*C_AMBER[:3], 0.0))
    key_visible_ranges(phy, [(G(1, 1), G(1, 150))])
    # GPU A die: computing (lighter) at the start, finishes around F040
    color_track(srvA['die'], frange(1), lambda f: mix(C_DIE_ACTIVE, C_DIE, (f - G(1, 30)) / 18), C_DIE)
    # NIC A die: amber tint while the packet is inside it (the NIC/SerDes is re-driving the bits)
    color_track(srvA['nic_die'], frange(1) + frange(2),
                lambda f: mix(C_DIE, C_AMBER, 0.3 * pk_board.any_on(f, s_nic0, s_nic1)), C_DIE)

    # ---------------------------------------------------------- S03: TX transceiver cutaway (module A)
    T = trxA
    Y = T['Y']
    v_e3, Tb3 = 0.09, 8                                            # electrical: 0.09 cm/frame, 8 frames/bit
    L_tr = path_len(T['traces'][('TX', 1)])
    L_drv = 0.45
    L_feed = path_len(T['bond']) + path_len(T['feed'])
    el0 = L_tr + L_drv + L_feed                                    # packet coordinate of electrode start
    el1 = el0 + 0.56
    pk3e = Packet(f0=G(3, 40) - el0 / v_e3, v=v_e3, slot=v_e3 * Tb3)
    fr3 = frange(3)
    for sgn in (-1, 1):
        p = [(x, y, z + 0.02) for x, y, z in T['traces'][('TX', sgn)]]
        pulse_curves(f'SIG_E_TXmod_trace_{"N" if sgn < 0 else "P"}', sig, p, 0.0, pk3e, fr3, 0.022, C_AMBER)
    feed_path = [(x, y, z + 0.008) for x, y, z in T['bond']] + [(x, y, z + 0.01) for x, y, z in T['feed'][1:]]
    pulse_curves('SIG_E_TXmod_feed', sig, feed_path, L_tr + L_drv, pk3e, fr3, 0.016, C_AMBER)
    color_track(T['drv'], fr3, lambda f: mix(C_DIE, C_AMBER, 0.38 * pk3e.any_on(f, L_tr, L_tr + L_drv)), C_DIE)
    color_track(T['sig_el'], fr3, lambda f: mix(C_PAD, C_AMBER, pk3e.any_on(f, el0, el1)), C_PAD)
    # laser carrier: steady, unmodulated (dim cyan) laser -> splitter -> both arms
    car = coll('SIGNALS_carrier', sig)
    for nm, p in (('input', T['wg_in']), ('arm_L', T['arm_L']), ('arm_R', T['arm_R'])):
        o = curve_obj(f'SIG_O_TX_carrier_{nm}', car, [(x, y, z + 0.004) for x, y, z in p], WG_R * 1.25, C_CYAN_DIM)
        key_visible_ranges(o, [(G(3, 1), G(3, 150))])
    o = boxc('SIG_O_TX_laser_emitting_facet', car, XL_A - 0.45, Y(4.425), PIC_TOP + 0.03, 0.1, 0.012, 0.05, C_CYAN_DIM)
    key_visible_ranges(o, [(G(3, 1), G(3, 150))])
    # modulated optical output: same bits, same 8 frames/bit, slower in the waveguide/fiber (0.03 cm/frame)
    v_o3 = 0.03
    out_path = [(x, y, z + 0.004) for x, y, z in T['wg_out']] + list(T['fibers']['TX'][1:])
    f_emit = pk3e.f0 + (el0 + 0.28) / v_e3                          # bit 0 reaches the electrode centre
    pk3o = Packet(f0=f_emit, v=v_o3, slot=v_o3 * Tb3)
    pulse_curves('SIG_O_TX_out', sig, out_path, 0.0, pk3o, fr3, WG_R * 1.6, C_CYAN)

    # ---------------------------------------------------------- S04: fiber route A -> B
    L_route = path_len(route)
    pk4 = Packet(f0=G(4, 1) - 3.0 / 0.72, v=0.72, slot=0.72 * 4.2)
    pulse_curves('SIG_O_fiber', sig, route, 0.0, pk4, frange(4), CABLE_R * 0.45, C_CYAN)
    # link-established core line, fades in during the S06 pull-back (closure)
    link = curve_obj('SIG_O_fiber_link_core', sig, route, CABLE_R * 0.32, C_CYAN)
    color_track(link, frange(6), lambda f: (*C_CYAN[:3], min(max((f - G(6, 108)) / 28, 0), 1) * 0.85),
                (*C_CYAN_DIM[:3], 0.0))
    key_visible_ranges(link, [(G(6, 100), G(6, 150))])

    # ---------------------------------------------------------- S05: RX transceiver cutaway (module B)
    R = trxB
    Yb = R['Y']
    v_o5, Tb5 = 0.05, 8
    rx_in = list(reversed(R['fibers']['RX'])) + [(x, y, z + 0.004) for x, y, z in R['wg_rx'][1:]]
    L_in = path_len(rx_in)
    pk5o = Packet(f0=G(5, 45) - L_in / v_o5, v=v_o5, slot=v_o5 * Tb5)
    fr5 = frange(5)
    pulse_curves('SIG_O_RX_in', sig, rx_in, 0.0, pk5o, fr5, WG_R * 1.6, C_CYAN)
    color_track(R['pd'], fr5, lambda f: mix(C_METAL_DK, C_CYAN, pk5o.any_on(f, L_in - 0.02, L_in + 0.24)),
                C_METAL_DK)
    v_e5 = 0.09
    out5 = [(x, y, z + 0.01) for x, y, z in R['pd_out']] + [(x, y, z + 0.008) for x, y, z in R['bond_rx'][1:]]
    L_out5 = path_len(out5)
    pk5e = Packet(f0=G(5, 45) + 0.12 / v_o5, v=v_e5, slot=v_e5 * Tb5)   # starts when bit 0 is half-way into the PD
    pulse_curves('SIG_E_RXmod_pd_tia', sig, out5, 0.0, pk5e, fr5, 0.016, C_AMBER)
    color_track(R['tia'], fr5, lambda f: mix(C_DIE, C_AMBER, 0.38 * pk5e.any_on(f, L_out5, L_out5 + 0.45)), C_DIE)
    for sgn in (-1, 1):
        p = list(reversed([(x, y, z + 0.02) for x, y, z in R['traces'][('RX', sgn)]]))
        pulse_curves(f'SIG_E_RXmod_trace_{"N" if sgn < 0 else "P"}', sig, p, L_out5 + 0.45, pk5e, fr5, 0.022, C_AMBER)

    # ---------------------------------------------------------- S06: board B, cage -> NIC B -> GPU B (−Y)
    pk6 = Packet(f0=G(6, 1) - 5.0 / 0.30, v=0.30, slot=0.8)
    L_cn = (CAGE_Y0 + 0.3) - (NIC_Y + NIC_HALF)
    fr6 = frange(6)
    for sgn in (-1, 1):
        p1, p2 = srvB['lines'][(REP, sgn)]
        lift = lambda p: [(x, y, z + 0.035) for x, y, z in reversed(p)]
        pulse_curves(f'SIG_E_B_cage_nic_{"N" if sgn < 0 else "P"}', sig, lift(p2), 0.0, pk6, fr6, 0.045, C_AMBER)
        pulse_curves(f'SIG_E_B_nic_gpu_{"N" if sgn < 0 else "P"}', sig, lift(p1), L_cn + 2 * NIC_HALF, pk6, fr6,
                     0.045, C_AMBER)
    color_track(srvB['nic_die'], fr6, lambda f: mix(C_DIE, C_AMBER, 0.3 * pk6.any_on(f, L_cn, L_cn + 2 * NIC_HALF)),
                C_DIE)
    L_to_gpu = L_cn + 2 * NIC_HALF + (NIC_Y - NIC_HALF) - (GPU_Y + GPU_HALF)
    rcv = box('SIG_E_B_arrival_PHY', sig, XL_B - 0.35 - 0.25, XL_B - 0.35 + 0.25, GPU_Y + GPU_HALF - 0.55,
              GPU_Y + GPU_HALF - 0.3, PCB_TOP + 0.3, PCB_TOP + 0.36, C_AMBER)
    f_hold = pk6.f0 + (L_to_gpu + 6 * 0.8) / 0.30
    color_track(rcv, fr6, lambda f: (*C_AMBER[:3], 0.65 if f >= f_hold else
                                     0.9 * pk6.any_on(f, L_to_gpu - 0.6, L_to_gpu + 0.3)), (*C_AMBER[:3], 0.0))
    key_visible_ranges(rcv, [(G(6, 1), G(6, 150))])
    f_arrive_end = pk6.f0 + (L_to_gpu + 7 * 0.8) / 0.30                # last slot has passed the package edge
    color_track(srvB['die'], fr6, lambda f: mix(C_DIE, C_DIE_ACTIVE, (f - f_arrive_end) / 15), C_DIE)

    # ---------------------------------------------------------- cutaways (only during S03 / S05)
    for o in [trxA['lid']] + srvA['cage_tops']:
        key_visible_ranges(o, [(1, G(3, 0)), (G(4, 1), 900)])
    for o in [trxB['lid']] + srvB['cage_tops']:
        key_visible_ranges(o, [(1, G(5, 0)), (G(6, 1), 900)])

    # ---------------------------------------------------------- cameras
    cams = build_cameras()

    # ---------------------------------------------------------- scenes, markers, render settings
    sc.frame_start, sc.frame_end = 1, N_SHOTS * SHOT_LEN
    setup_render(sc)
    sc.camera = cams[0]
    for i, cam in enumerate(cams):
        m = sc.timeline_markers.new(f'{SHOTS[i][0]}_{SHOTS[i][1]}', frame=G(i + 1, 1))
        m.camera = cam
    for i, cam in enumerate(cams):                    # per-shot scenes sharing the same collections
        s2 = bpy.data.scenes.new(f'SHOT_{SHOTS[i][0]}_{SHOTS[i][1]}')
        for ch in sc.collection.children:
            s2.collection.children.link(ch)
        s2.frame_start, s2.frame_end = G(i + 1, 1), G(i + 1, SHOT_LEN)
        s2.camera = cam
        s2.world = sc.world
        setup_render(s2)
    bpy.context.window_manager  # noqa
    return sc


def setup_render(sc):
    sc.render.fps = FPS
    sc.render.resolution_x, sc.render.resolution_y = RES_X, RES_Y
    sc.render.resolution_percentage = 100
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'OBJECT'
    sh.show_object_outline = True
    sh.object_outline_color = (0.0, 0.0, 0.0)
    sh.show_cavity = True
    sh.cavity_type = 'WORLD'
    sh.cavity_ridge_factor = 0.6
    sh.cavity_valley_factor = 1.0
    sh.show_shadows = True
    sh.shadow_intensity = 0.3
    sh.background_type = 'WORLD'
    sc.display.light_direction = (0.35, -0.35, 0.87)
    sc.display.render_aa = '8'
    sc.render.use_motion_blur = False
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format = 'PNG'
    if sc.world is None:
        w = bpy.data.worlds.new('World_LIGHTPATH')
        w.color = (0.035, 0.037, 0.042)
        sc.world = w


# ------------------------------------------------------------------ the six camera moves (director-locked beats)
def build_cameras():
    A, B = XL_A, XL_B
    lp = A - 0.35                       # board A story pair x
    lpb = B - 0.35
    cams = []
    # S01 DEPARTURE — three-quarter macro of GPU A, diagonal dolly to the departure point, settle on outgoing traces
    cams.append(make_camera(1, [
        (-10, (A - 15.2, -14.5, 201.0), (A + 0.4, 0.6, 187.8), 30),
        (1, (A - 14.6, -13.6, 200.6), (A + 0.3, 0.9, 187.8), 30),
        (30, (A - 13.0, -11.4, 199.6), (A + 0.1, 1.6, 187.8), 30),
        (105, (A - 4.6, -1.2, 193.0), (lp, 7.8, 187.6), 30),
        (135, (lp - 1.3, 1.6, 190.2), (lp, 9.0, 187.5), 30),
        (150, (lp - 0.95, 2.2, 189.95), (lp, 9.6, 187.5), 30),
        (162, (lp - 0.8, 2.45, 189.88), (lp, 9.9, 187.5), 30),
    ]))
    # S02 THE ELECTRICAL PATH — low over the pair, forward tracking past NIC A, reveal and settle at the cage
    cams.append(make_camera(2, [
        (-10, (lp - 0.6, 4.4, 188.75), (lp, 11.0, 187.5), 24),
        (1, (lp - 0.58, 5.1, 188.75), (lp, 11.8, 187.5), 24),
        (25, (lp - 0.75, 7.6, 189.3), (lp, 14.5, 187.5), 24),
        (48, (lp - 0.8, 12.6, 190.1), (lp, 19.5, 187.5), 24),
        (100, (lp - 1.0, 24.5, 189.3), (lp + 0.1, 32.0, 187.6), 24),
        (130, (lp - 1.6, 29.0, 190.0), (A, 37.0, 188.2), 24),
        (150, (lp - 1.7, 30.6, 190.2), (A, 37.4, 188.2), 24),
        (162, (lp - 1.72, 30.9, 190.22), (A, 37.5, 188.2), 24),
    ]))
    # S03 E→O CONVERSION — cutaway module A: driver, laser/modulator, coupling; lateral move + modest orbit
    Y = lambda u: MOD_Y0 + u
    cams.append(make_camera(3, [
        (-10, (A - 1.05, Y(1.75), 189.85), (A - 0.38, Y(4.65), PIC_TOP), 30),
        (1, (A - 1.0, Y(1.85), 189.8), (A - 0.38, Y(4.7), PIC_TOP), 30),
        (40, (A - 0.8, Y(2.15), 189.6), (A - 0.38, Y(4.8), PIC_TOP), 30),
        (105, (A + 0.55, Y(2.55), 189.35), (A - 0.42, Y(5.2), PIC_TOP), 30),
        (130, (A + 0.35, Y(3.6), 189.05), (A - 0.45, Y(5.9), PIC_TOP), 30),
        (150, (A + 0.2, Y(4.0), 188.95), (A - 0.42, Y(6.6), WG_Z), 30),
        (162, (A + 0.17, Y(4.1), 188.93), (A - 0.41, Y(6.75), WG_Z), 30),
    ]))
    # S04 THE OPTICAL PATH — from TX connector, accelerate along the cable, reveal racks, arrive at RX connector
    cams.append(make_camera(4, [
        (-10, (A - 2.6, 44.6, 191.3), (A + 0.2, 50.5, 187.6), 30),
        (1, (A - 2.6, 45.0, 191.2), (A + 0.2, 51.2, 187.4), 30),
        (30, (A - 4.0, 49.0, 193.0), (A + 0.6, 54.0, 185.5), 30),
        (70, (A - 34.0, 100.0, 216.0), (A + 22.0, 49.0, 184.0), 22),
        (100, (-30.0, 108.0, 218.0), (B - 26.0, 49.5, 183.5), 22),
        (135, (B - 9.0, 64.0, 195.5), (B, 50.0, 186.8), 28),
        (150, (B - 3.4, 56.6, 192.6), (B, 48.6, 188.1), 30),
        (162, (B - 3.0, 56.1, 192.4), (B, 48.3, 188.15), 30),
    ]))
    # S05 OPTICAL RECEPTION — cutaway module B, mirror of S03 (looking −Y): PD, then the electrical departure
    cams.append(make_camera(5, [
        (-10, (B + 1.05, Y(8.25), 189.85), (B + 0.38, Y(5.35), PIC_TOP), 30),
        (1, (B + 1.0, Y(8.15), 189.8), (B + 0.38, Y(5.3), PIC_TOP), 30),
        (35, (B + 0.85, Y(7.75), 189.6), (B + 0.4, Y(5.0), PIC_TOP), 30),
        (95, (B + 0.75, Y(6.6), 189.15), (B + 0.42, Y(4.5), PIC_TOP), 30),
        (125, (B - 0.25, Y(6.4), 189.2), (B + 0.15, Y(3.9), PIC_TOP), 30),
        (150, (B - 0.2, Y(5.6), 189.05), (B + 0.3, Y(1.6), MPCB_TOP), 30),
        (162, (B - 0.2, Y(5.45), 189.03), (B + 0.3, Y(1.3), MPCB_TOP), 30),
    ]))
    # S06 ARRIVAL — follow the board path to GPU B, then rise and pull back into the closing composition
    cams.append(make_camera(6, [
        (-10, (lpb + 1.0, 39.0, 190.6), (lpb, 31.5, 187.5), 24),
        (1, (lpb + 1.0, 38.4, 190.5), (lpb, 30.8, 187.5), 24),
        (35, (lpb + 1.0, 32.0, 190.3), (lpb, 22.0, 187.5), 24),
        (100, (lpb + 1.6, 15.5, 190.4), (B, 2.0, 187.8), 24),
        (125, (B + 26.0, 14.0, 212.0), (B - 6.0, 6.0, 187.0), 20),
        (150, (84.0, 12.0, 250.0), (2.0, 22.0, 186.0), 16.5),
        (162, (86.5, 12.0, 252.5), (1.2, 22.3, 186.0), 16.5),
    ]))
    return cams


# ------------------------------------------------------------------ main
def check(sc, frames_per_shot=None):
    """camera-inside-geometry test (every frame) and key-subject framing report."""
    from bpy_extras.object_utils import world_to_camera_view
    boxes = [o for o in bpy.data.objects if o.type == 'MESH' and o.data.name == 'UnitCube']
    probs = []
    for f in range(1, N_SHOTS * SHOT_LEN + 1):
        sc.frame_set(f)
        cam = [m.camera for m in sc.timeline_markers if m.frame <= f][-1]
        p = cam.matrix_world.translation
        for o in boxes:
            if o.hide_render:
                continue
            c, s_ = o.location, o.scale
            m = 0.02
            if all(abs(p[i] - c[i]) < s_[i] / 2 + m for i in range(3)):
                probs.append((f, cam.name, o.name))
    seen = {}
    for f, c, o in probs:
        seen.setdefault((c, o), []).append(f)
    print('CHECK camera-inside/near(<0.02cm) geometry:', 'none' if not seen else '')
    for (c, o), fs in seen.items():
        print(f'  {c}: {o} frames {fs[0]}-{fs[-1]} ({len(fs)})')


def proj(sc, frames, names):
    from bpy_extras.object_utils import world_to_camera_view
    for f in frames:
        sc.frame_set(f)
        cam = [m.camera for m in sc.timeline_markers if m.frame <= f][-1]
        out = []
        for n in names:
            o = bpy.data.objects.get(n)
            if o is None:
                continue
            v = world_to_camera_view(sc, cam, o.matrix_world.translation)
            out.append(f'{n.split("_")[0]}..{n[-10:]}=({v.x:.2f},{v.y:.2f},{v.z:.0f})')
        print('PROJ', f, ' '.join(out))


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['save']
    mode = argv[0]
    half = '--half' in argv
    sc = build()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'lightpath_blockout.blend'), compress=True)
    if half:
        sc.render.resolution_percentage = 50
    if mode == 'check':
        check(sc)
    if mode == 'proj':
        proj(sc, [int(x) for x in argv[1].split(',')], argv[2].split(','))
    if mode == 'stills':
        frames = [int(x) for x in argv[1].split(',')]
        d = os.path.join(HERE, 'out', 'stills')
        os.makedirs(d, exist_ok=True)
        for f in frames:
            sc.frame_set(f)
            sc.camera = [m.camera for m in sc.timeline_markers if m.frame <= f][-1]
            sc.render.filepath = os.path.join(d, f'f{f:04d}.png')
            bpy.ops.render.render(write_still=True)
    elif mode == 'anim':
        a = int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else 1
        b = int(argv[2]) if len(argv) > 2 and argv[2].isdigit() else N_SHOTS * SHOT_LEN
        d = os.path.join(HERE, 'out', 'frames')
        os.makedirs(d, exist_ok=True)
        for f in range(a, b + 1):
            p = os.path.join(d, f'f{f:04d}.png')
            if os.path.exists(p):
                continue
            sc.frame_set(f)
            sc.camera = [m.camera for m in sc.timeline_markers if m.frame <= f][-1]
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)


main()
