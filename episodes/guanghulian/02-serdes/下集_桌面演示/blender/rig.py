"""光互连 02 下集 · 桌面演示版：演示装置场景 + y6 试镜头（长黑带上盖出五个蓝点）。
房间、太阳、相机、渲染设置沿用 ../../../blender_desk_look/scene.py；所有东西按真实尺寸（米）。
纸带、摆锤、盖点臂、蓝点、小灯、计数轮、纸签都是关键帧动画，在 3D 里真的动、真的投影。

用法：
  blender -b -P rig.py -- <tex目录> <贴图下载目录> <输出> [缩放% 默认25] [采样 默认32] [key=value ...]
  still=<帧>        只渲一帧，<输出> 是 png 路径
  fs=<帧> fe=<帧>   渲一段，<输出> 是目录（f_0000.png …），同目录写 times.txt（每帧秒数）
  anchors=1         不渲染，只把每帧的屏幕锚点写到 <输出>（json），给合成贴字用
  cam=E             整套装置的横屏全景（看布局用）；默认是 y6 的机位 C1 → C2
  glow=1            发光信号那一段：纸带前面放一块真电路板（model=<模型目录>），走线上跑金色脉冲；百叶放下、房间变暗；用自己的机位
  其它：gpu=1 thr=<自适应阈值> mb=0（关运动模糊） el az sun sky exposure fstop blind=<百叶下沿高度>

时间（24 帧 / 秒，共 216 帧 = 9 秒）：一格 20 帧。黑白交界过窄缝在第 0、20、40、60、80（进长黑带）、180（出长黑带）帧；
盖点在每格正中：第 10、30、50、70 帧（黑白相间的四格），第 90、110、130、150、170 帧（长黑带，五个），第 190、210 帧（白格）。
"""
import bpy, sys, math, json, os, time, random
from math import sin, cos, radians, pi
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
TEX, DL, OUT = argv[0], argv[1], argv[2]
pos = [a for a in argv[3:] if "=" not in a]
SCALE = int(pos[0]) if len(pos) > 0 else 25
SAMPLES = int(pos[1]) if len(pos) > 1 else 32
P = dict(el=24, az=-18, exposure=0.55, sun=8.0, sky=0.8, fstop=4.0, lens=50, blind=0.66, mb=1, slat=14)
GLOW_DEFAULTS = dict(blind=0.15, slat=-50, exposure=2.9, fstop=5.6)     # 发光信号那一段：百叶放下来合上，只剩窗缝里的天光；金色的光才照得出周围的元件
S = {}
for a in argv[3:]:
    if "=" in a:
        k, v = a.split("=")
        try: P[k] = float(v)
        except ValueError: S[k] = v
G = bool(P.get("glow"))
if G:
    for k, v in GLOW_DEFAULTS.items():
        if not any(a.startswith(k + "=") for a in argv[3:]): P[k] = v

FPS, NF, TB = 24, 216, 20            # 帧率、总帧数、一格（一个比特）占几帧
CELL = 0.024                          # 一格 24 mm
V = CELL / TB                         # 纸带每帧走多远
SLIT_X, YR = 0.10, -0.06              # 窄缝的 x；导轨中线的 y
RAIL_H = 0.008
Z_TAPE = RAIL_H + 0.00012
Y_NEAR, Y_M, Y_F, Y_FAR = YR - 0.021, YR - 0.008, YR + 0.018, YR + 0.021   # 纸带：近侧白边 | 数据道 | 远侧窄白边
Y_DOT = YR - 0.0145
TH_MAX = radians(22)                  # 摆幅
BAND = range(4, 9)                    # 长黑带是第 4–8 格


def bit(j):
    if j in BAND: return 1
    if 9 <= j <= 11: return 0
    return 1 if j % 2 == 0 else 0


def theta(f):                         # 摆锤：右头（+）在每格正中，左头在交界
    return TH_MAX * cos(2 * pi * (f - TB / 2) / TB)


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
col = scene.collection
EDIT = bpy.context.preferences.edit


def interp(kind): EDIT.keyframe_new_interpolation_type = kind


def set_interp(idb, kind):
    """把 idb（物体或节点树）上所有关键帧的插值设成 kind。偏好设置里的「新关键帧插值」在后台模式下不生效，所以显式设。"""
    ad = idb.animation_data
    for layer in ad.action.layers:
        for strip in layer.strips:
            for fc in strip.channelbag(ad.action_slot).fcurves:
                for kp in fc.keyframe_points: kp.interpolation = kind


# ---------- 小工具 ----------
def add_obj(name, mesh):
    o = bpy.data.objects.new(name, mesh); col.objects.link(o); return o


def empty(name, loc, rot=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); col.objects.link(e); e.location = loc; e.rotation_euler = rot; return e


def child(o, parent, parent_loc):
    """o 的网格是按世界坐标建的；挂到 parent（静止时位于 parent_loc、无旋转）下面，位置不变。"""
    o.parent = parent; o.matrix_parent_inverse = Matrix.Translation(parent_loc).inverted(); return o


def mesh_from(name, verts, faces, uvs=None, smooth=False, loop_uvs=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    if uvs or loop_uvs:
        uvl = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            for k, li in enumerate(poly.loop_indices):
                uvl.data[li].uv = loop_uvs[poly.index][k] if loop_uvs else uvs[me.loops[li].vertex_index]
    if smooth:
        for p in me.polygons: p.use_smooth = True
    me.update()
    return me


def box(name, x0, x1, y0, y1, z0, z1, mat=None, bevel=0.0):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    o = add_obj(name, mesh_from(name, v, f))
    if mat: o.data.materials.append(mat)
    if bevel:
        m = o.modifiers.new("bev", "BEVEL"); m.width = bevel; m.segments = 3
    return o


def cyl(name, p0, p1, r, mat, seg=20, r1=None):
    """从 p0 到 p1 的圆柱（r1 给了就是圆台），两头封口。"""
    p0, p1 = Vector(p0), Vector(p1); ax = (p1 - p0).normalized()
    u = ax.orthogonal().normalized(); w = ax.cross(u)
    r1 = r if r1 is None else r1
    verts = [tuple(p0 + r * (cos(2 * pi * s / seg) * u + sin(2 * pi * s / seg) * w)) for s in range(seg)]
    verts += [tuple(p1 + r1 * (cos(2 * pi * s / seg) * u + sin(2 * pi * s / seg) * w)) for s in range(seg)]
    faces = [(s, (s + 1) % seg, seg + (s + 1) % seg, seg + s) for s in range(seg)]
    faces += [tuple(range(seg - 1, -1, -1)), tuple(range(seg, 2 * seg))]
    o = add_obj(name, mesh_from(name, verts, faces))
    for p in o.data.polygons[:seg]: p.use_smooth = True
    o.data.materials.append(mat)
    return o


def lathe(name, prof, seg=48, mats=None, ring_mat=None, split=40):
    verts, faces, fm = [], [], []
    n = len(prof)
    for (r, z) in prof:
        for s in range(seg):
            a = 2 * pi * s / seg
            verts.append((r * cos(a), r * sin(a), z))
    for i in range(n - 1):
        for s in range(seg):
            a, b = i * seg + s, i * seg + (s + 1) % seg
            faces.append((a, b, b + seg, a + seg)); fm.append(ring_mat[i] if ring_mat else 0)
    me = mesh_from(name, verts, faces, smooth=True)
    o = add_obj(name, me)
    for m in (mats or []): me.materials.append(m)
    for p, k in zip(me.polygons, fm): p.material_index = k
    if split:
        m = o.modifiers.new("es", "EDGE_SPLIT"); m.split_angle = radians(split)
    return o


def principled(name, **kw):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    for k, v in kw.items():
        b.inputs[k].default_value = v
    return m, b


def img_node(m, path, colorspace="sRGB"):
    n = m.node_tree.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(path)
    n.image.colorspace_settings.name = colorspace
    return n


def bump(m, b, scale, strength, dist=0.0002, detail=4.0):
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    no = nt.nodes.new("ShaderNodeTexNoise")
    no.inputs["Scale"].default_value = scale; no.inputs["Detail"].default_value = detail
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = strength; bp.inputs["Distance"].default_value = dist
    nt.links.new(tc.outputs["Object"], no.inputs["Vector"])
    nt.links.new(no.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])


def mat_pbr(name, prefix, res, scale, rough=(0.3, 0.7), nor=1.0, tint=None, offset=(0, 0, 0)):
    """Poly Haven 的 diff / rough / nor_gl 三张图，按物体坐标盒式投影。scale = 贴图一个周期对应几米。"""
    m, b = principled(name)
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / scale,) * 3
    mp.inputs["Location"].default_value = offset
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    d = img_node(m, f"{DL}/{prefix}_diff_{res}.jpg")
    r = img_node(m, f"{DL}/{prefix}_rough_{res}.jpg", "Non-Color")
    n = img_node(m, f"{DL}/{prefix}_nor_gl_{res}.jpg", "Non-Color")
    for t in (d, r, n):
        t.projection = "BOX"; t.projection_blend = 0.1
        nt.links.new(mp.outputs["Vector"], t.inputs["Vector"])
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = nor
    nt.links.new(n.outputs["Color"], nm.inputs["Color"])
    if tint:
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"
        mx.inputs[0].default_value = 1.0; mx.inputs[7].default_value = (*tint, 1)
        nt.links.new(d.outputs["Color"], mx.inputs[6]); nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    else:
        nt.links.new(d.outputs["Color"], b.inputs["Base Color"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = rough[0]; mr.inputs["To Max"].default_value = rough[1]
    nt.links.new(r.outputs["Color"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
    nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_wall():
    m, b = principled("wall", Roughness=0.9)
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.5, 0.5, 0.5)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    d = img_node(m, f"{DL}/painted_plaster_wall_diff_2k.jpg")
    n = img_node(m, f"{DL}/painted_plaster_wall_nor_gl_2k.jpg", "Non-Color")
    for t in (d, n):
        t.projection = "BOX"; t.projection_blend = 0.2
        nt.links.new(mp.outputs["Vector"], t.inputs["Vector"])
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.6
    nt.links.new(n.outputs["Color"], nm.inputs["Color"])
    nt.links.new(d.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_paper_tex(name, path):
    m, b = principled(name, Roughness=0.78)
    t = img_node(m, path)
    m.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Sheen Weight"].default_value = 0.15
    bump(m, b, 2500, 0.25, 0.00004)
    return m


def cut_outside(m, x0, x1):
    """世界坐标 x 在 [x0, x1] 之外的部分变透明（纸带藏进印带器里、右端出画的那一段）。"""
    nt = m.node_tree
    out = nt.nodes["Material Output"]; b = nt.nodes["Principled BSDF"]
    geo = nt.nodes.new("ShaderNodeNewGeometry"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    g = nt.nodes.new("ShaderNodeMath"); g.operation = "GREATER_THAN"; g.inputs[1].default_value = x0
    l = nt.nodes.new("ShaderNodeMath"); l.operation = "LESS_THAN"; l.inputs[1].default_value = x1
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = "MULTIPLY"
    nt.links.new(sep.outputs["X"], g.inputs[0]); nt.links.new(sep.outputs["X"], l.inputs[0])
    nt.links.new(g.outputs[0], mu.inputs[0]); nt.links.new(l.outputs[0], mu.inputs[1])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mu.outputs[0], mix.inputs[0]); nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(b.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])


# ---------- 材质 ----------
WOOD = mat_pbr("desk_wood", "wood_table_001", "4k", 1.1, (0.22, 0.62), offset=(0.31, 0.17, 0))
WALL = mat_wall()
PLY = mat_pbr("plywood", "plywood", "2k", 0.45, (0.45, 0.8), nor=0.7)
WALNUT = mat_pbr("walnut", "american_walnut_veneer", "2k", 0.35, (0.25, 0.55), nor=0.6, tint=(0.62, 0.52, 0.46))
M_PLAIN, _ = principled("plain", **{"Base Color": (0.72, 0.70, 0.66, 1), "Roughness": 0.9})
M_SLAT, _ = principled("slat", **{"Base Color": (0.80, 0.77, 0.70, 1), "Roughness": 0.55})
M_BRASS, _b = principled("brass", **{"Base Color": (0.80, 0.58, 0.26, 1), "Metallic": 1.0, "Roughness": 0.28})
bump(M_BRASS, _b, 900, 0.05, 0.00002, 2.0)
M_STEEL, _ = principled("steel", **{"Base Color": (0.72, 0.72, 0.74, 1), "Metallic": 1.0, "Roughness": 0.3})
M_RAIL, _b = principled("rail", **{"Base Color": (0.035, 0.036, 0.04, 1), "Metallic": 1.0, "Roughness": 0.42})
bump(M_RAIL, _b, 1400, 0.06, 0.00002, 2.0)
M_BLACK, _ = principled("black_plastic", **{"Base Color": (0.02, 0.02, 0.022, 1), "Roughness": 0.38})
M_FELT, _b = principled("felt", **{"Base Color": (0.03, 0.03, 0.032, 1), "Roughness": 0.95})
_b.inputs["Sheen Weight"].default_value = 0.5
M_PAPER, _b = principled("tape_paper", **{"Base Color": (0.84, 0.82, 0.76, 1), "Roughness": 0.8})
_b.inputs["Sheen Weight"].default_value = 0.15
bump(M_PAPER, _b, 2500, 0.25, 0.00004)
M_INK, _b = principled("tape_ink", **{"Base Color": (0.012, 0.012, 0.014, 1), "Roughness": 0.6})
bump(M_INK, _b, 1800, 0.2, 0.00003)
M_BLUE, _ = principled("dot_ink", **{"Base Color": (0.015, 0.11, 0.62, 1), "Roughness": 0.42})
M_PAD, _b = principled("stamp_pad", **{"Base Color": (0.02, 0.09, 0.42, 1), "Roughness": 0.95})
_b.inputs["Sheen Weight"].default_value = 0.4
M_CER, _b = principled("ceramic", **{"Base Color": (0.80, 0.78, 0.72, 1), "Roughness": 0.22})
_b.inputs["Coat Weight"].default_value = 0.6
M_COF, _ = principled("coffee", **{"Base Color": (0.05, 0.025, 0.012, 1), "Roughness": 0.05})

# ---------- 房间（和定妆静帧同一间；只有左墙一扇窗） ----------
box("desk", -0.80, 1.00, -0.42, 0.40, -0.032, 0.0, WOOD, bevel=0.0015)
box("wall_back", -1.0, 2.2, 0.40, 0.55, -0.75, 1.75, WALL)
box("wall_right", 2.2, 2.35, -2.6, 0.55, -0.75, 1.75, WALL)
box("wall_front", -1.0, 2.2, -2.75, -2.6, -0.75, 1.75, WALL)
box("floor", -1.0, 2.35, -2.75, 0.55, -0.9, -0.75, M_PLAIN)
box("ceil", -1.0, 2.35, -2.75, 0.55, 1.75, 1.9, M_PLAIN)
WY0, WY1, WZ0, WZ1 = -0.75, 0.38, 0.12, 1.30
box("wl_low", -0.98, -0.80, -2.6, 0.40, -0.75, WZ0, WALL)
box("wl_top", -0.98, -0.80, -2.6, 0.40, WZ1, 1.75, WALL)
box("wl_front", -0.98, -0.80, -2.6, WY0, WZ0, WZ1, WALL)
box("wl_back", -0.98, -0.80, WY1, 0.40, WZ0, WZ1, WALL)
box("sill", -0.98, -0.775, WY0 - 0.02, WY1, WZ0 - 0.02, WZ0, M_SLAT)
# 百叶拉起一半：下沿在 P["blind"]。桌上演示的那一段在整片阳光里，叶片的影子落在桌子右半边和右墙上
z = max(WZ0 + 0.03, P["blind"]); k = 0
box("blind_rail", -0.915, -0.865, WY0 + 0.005, WY1 - 0.005, z - 0.03, z - 0.012, M_SLAT)
while z < WZ1 - 0.01:
    s = box(f"slat{k}", -0.025, 0.025, WY0 + 0.005, WY1 - 0.005, -0.0012, 0.0012, M_SLAT)
    s.location = (-0.89, 0, z); s.rotation_euler = (0, radians(P["slat"]), 0)
    z += 0.045; k += 1

# ---------- 导轨（纸带走在上面） ----------
RX0, RX1 = -0.62, 0.76
box("rail", RX0, RX1, YR - 0.027, YR + 0.027, 0, RAIL_H, M_RAIL, bevel=0.0006)
box("rail_lip_n", RX0, RX1, YR - 0.027, YR - 0.0235, RAIL_H, RAIL_H + 0.0022, M_RAIL, bevel=0.0005)
box("rail_lip_f", RX0, RX1, YR + 0.0235, YR + 0.027, RAIL_H, RAIL_H + 0.0022, M_RAIL, bevel=0.0005)

# ---------- 纸带：黑格 = 1，白格 = 0；近侧一条白边；不画格线 ----------
PRN_X = SLIT_X - 24.5 * CELL            # 印带器的印头
TAPE_CUT = (PRN_X - 0.03, 0.74)
M_PAPER_T, M_INK_T = M_PAPER.copy(), M_INK.copy()
cut_outside(M_PAPER_T, *TAPE_CUT); cut_outside(M_INK_T, *TAPE_CUT)
J0, J1 = -28, 36
verts, faces, fmat = [], [], []
ys = [Y_NEAR, Y_M, Y_F, Y_FAR]
for j in range(J0, J1 + 1):
    xa, xb = SLIT_X - CELL * (j + 1), SLIT_X - CELL * j
    for r in range(3):
        n = len(verts)
        verts += [(xa, ys[r], Z_TAPE), (xb, ys[r], Z_TAPE), (xb, ys[r + 1], Z_TAPE), (xa, ys[r + 1], Z_TAPE)]
        faces.append((n, n + 1, n + 2, n + 3)); fmat.append(1 if (r == 1 and bit(j)) else 0)
tape = add_obj("tape", mesh_from("tape", verts, faces))
tape.data.materials.append(M_PAPER_T); tape.data.materials.append(M_INK_T)
for p, k in zip(tape.data.polygons, fmat): p.material_index = k
interp("LINEAR")
tape.location.x = 0.0; tape.keyframe_insert("location", frame=0)
tape.location.x = V * NF; tape.keyframe_insert("location", frame=NF)
set_interp(tape, "LINEAR")

# ---------- 蓝点：盖在近侧白边上，每格正中一个 ----------
random.seed(3)


def dot(j):
    seg, verts = 28, [(0, 0, 0)]
    ph = [random.uniform(0, 6.28) for _ in range(3)]
    for s in range(seg):
        a = 2 * pi * s / seg
        r = 0.0040 * (1 + 0.035 * sin(3 * a + ph[0]) + 0.025 * sin(5 * a + ph[1]) + 0.015 * sin(9 * a + ph[2]))
        verts.append((r * cos(a), r * sin(a), 0))
    if bit(j):                                       # 读到 1：实心点
        faces = [(0, 1 + s, 1 + (s + 1) % seg) for s in range(seg)]
    else:                                            # 读到 0：空心圈（用户 11-11 同意：长黑带下面的五个实心点才好数）
        verts += [(0.72 * x, 0.72 * y, 0) for x, y, _ in verts[1:]]
        faces = [(1 + s, 1 + (s + 1) % seg, 1 + seg + (s + 1) % seg, 1 + seg + s) for s in range(seg)]
    o = add_obj(f"dot{j}", mesh_from(f"dot{j}", verts, faces)); o.data.materials.append(M_BLUE)
    f_st = TB * j + TB // 2
    o.location = (SLIT_X - V * f_st + random.uniform(-0.0003, 0.0003), Y_DOT + random.uniform(-0.0003, 0.0003), Z_TAPE + 0.00003)
    o.parent = tape
    if f_st > 0:
        interp("CONSTANT")
        o.scale = (0, 0, 0); o.keyframe_insert("scale", frame=0)
        o.scale = (1, 1, 1); o.keyframe_insert("scale", frame=f_st)
        set_interp(o, "CONSTANT")
    return o


for j in range(J0, NF // TB + 1):
    dot(j)

# ---------- 读带口：从远侧伸出来的一块黄铜板，中间一道窄缝；近侧白边露在外面 ----------
SW = 0.0025                               # 窄缝半宽（缝宽 5 mm）
GX0, GX1 = SLIT_X - 0.024, SLIT_X + 0.024
PZ0, PZ1 = RAIL_H + 0.0030, RAIL_H + 0.0045
box("gate_block", GX0, GX1, YR + 0.0275, YR + 0.060, 0, PZ0, PLY, bevel=0.0008)
PY0, PY1 = Y_M - 0.0005, YR + 0.058
SY0, SY1 = Y_M + 0.0015, Y_F - 0.0015
for nm_, (a, b_, c, d_) in {"l": (GX0, SLIT_X - SW, PY0, PY1), "r": (SLIT_X + SW, GX1, PY0, PY1),
                            "n": (SLIT_X - SW, SLIT_X + SW, PY0, SY0), "f": (SLIT_X - SW, SLIT_X + SW, SY1, PY1)}.items():
    box("gate_plate_" + nm_, a, b_, c, d_, PZ0, PZ1, M_BRASS)
for sx in (GX0 + 0.005, GX1 - 0.005):       # 两颗螺丝
    cyl("gate_screw", (sx, YR + 0.044, PZ1), (sx, YR + 0.044, PZ1 + 0.0012), 0.0024, M_STEEL, 16)

# 小灯：缝边一只琥珀色的小灯，黑白交界过窄缝时闪一下
LAMP = Vector((SLIT_X + 0.0125, YR + 0.005, PZ1))
cyl("lamp_bezel", LAMP, LAMP + Vector((0, 0, 0.0018)), 0.0046, M_STEEL, 24)
M_LAMP, bl = principled("lamp", **{"Base Color": (0.75, 0.33, 0.04, 1), "Roughness": 0.25})
bl.inputs["Emission Color"].default_value = (1.0, 0.50, 0.10, 1)
bl.inputs["Emission Strength"].default_value = 0.0
dome = lathe("lamp_dome", [(0.0034 * cos(radians(a)), 0.0034 * sin(radians(a))) for a in range(0, 91, 10)], 24, [M_LAMP], split=0)
dome.location = LAMP + Vector((0, 0, 0.0016))
EDGES = [f for f in range(0, NF + 1, TB) if bit(f // TB) != bit(f // TB - 1)]
interp("LINEAR")
es = bl.inputs["Emission Strength"]
for f in EDGES:
    for df, val in ((-1, 0.0), (0, 90.0), (1, 55.0), (2, 18.0), (4, 0.0)):
        if f + df >= 0:
            es.default_value = val; es.keyframe_insert("default_value", frame=f + df)
set_interp(M_LAMP.node_tree, "LINEAR")

# ---------- 计数器：一只数字轮（0–9），这一段黑带数到第几个 ----------
CX, CY, CZ, WR, WW = SLIT_X + 0.085, YR + 0.056, 0.040, 0.026, 0.024   # 离窄缝 85 mm：再近，盖点臂抬起时的影子会扫到数字
PHI_W = radians(138)                                    # 朝相机的那个方向（窗口）
seg = 90
verts, luv, faces = [], [], []
for s in range(seg + 1):
    a = 2 * pi * s / seg
    for xx in (-WW / 2, WW / 2):
        verts.append((xx, WR * cos(a), WR * sin(a)))
for s in range(seg):
    a0, a1 = s * 2, (s + 1) * 2
    faces.append((a0, a0 + 1, a1 + 1, a1))
    v0, v1 = 0.95 - s / seg, 0.95 - (s + 1) / seg
    luv.append([(0, v0), (1, v0), (1, v1), (0, v1)])
M_DIG, bd = principled("digits", Roughness=0.4)
td = img_node(M_DIG, f"{TEX}/digits.png"); M_DIG.node_tree.links.new(td.outputs["Color"], bd.inputs["Base Color"])
wheel = add_obj("wheel", mesh_from("wheel", verts, faces, loop_uvs=luv, smooth=True)); wheel.data.materials.append(M_DIG)
whub = empty("wheel_hub", (CX, CY, CZ)); wheel.parent = whub
for sx in (-1, 1):
    c = cyl("wheel_cap", (sx * WW / 2, 0, 0), (sx * (WW / 2 + 0.0004), 0, 0), WR, M_BLACK, 48); c.parent = whub


def wheel_rot(n): return PHI_W - radians(36) * n


count_keys = []                                         # (帧, 数字)
run = 0
for j in range(0, NF // TB + 1):
    if bit(j) and not bit(j - 1):
        run = 0; count_keys.append((TB * j, 0))         # 新的一段黑带进来：清零
    if bit(j):
        run += 1; count_keys.append((TB * j + TB // 2, run))
interp("BEZIER")
prev = 1 if bit(-1) else (1 if bit(-2) else 0)          # 开场前那一小段黑格数到 1
whub.rotation_euler = (wheel_rot(prev), 0, 0); whub.keyframe_insert("rotation_euler", frame=-10)
for f, n in count_keys:
    whub.rotation_euler = (wheel_rot(prev), 0, 0); whub.keyframe_insert("rotation_euler", frame=max(f, 0))
    whub.rotation_euler = (wheel_rot(n), 0, 0); whub.keyframe_insert("rotation_euler", frame=max(f, 0) + 3)
    prev = n
# 外壳：两片侧板 + 底座 + 背板 + 顶盖 + 窗口上下两块挡板
HX0, HX1 = CX - WW / 2 - 0.0012, CX + WW / 2 + 0.0012
HT = CZ + WR + 0.006
for nm_, (a, b_) in {"l": (HX0 - 0.006, HX0), "r": (HX1, HX1 + 0.006)}.items():   # 侧板：窗口那一角不挡，太阳才照得到数字
    box("cnt_cheek_" + nm_, a, b_, CY - 0.006, CY + 0.034, 0, HT, PLY, bevel=0.0008)
    box("cnt_cheek_lo_" + nm_, a, b_, CY - 0.034, CY - 0.006, 0, CZ - 0.008, PLY, bevel=0.0008)
box("cnt_back", HX0, HX1, CY + 0.029, CY + 0.034, 0, HT, PLY)
box("cnt_top", HX0, HX1, CY - 0.006, CY + 0.034, HT - 0.005, HT, PLY)
box("cnt_front", HX0, HX1, CY - 0.034, CY - 0.029, 0, CZ - 0.012, PLY)
cyl("cnt_axle", (HX0 - 0.0075, CY, CZ), (HX1 + 0.0075, CY, CZ), 0.0028, M_BRASS, 20)


def tangent_plate(name, a0, a1, mat, rad=WR + 0.0022, th=0.0018):
    am = (a0 + a1) / 2; ln = 2 * rad * math.tan((a1 - a0) / 2)
    o = box(name, HX0, HX1, -ln / 2, ln / 2, 0, th, mat)
    o.location = (0, CY + rad * cos(am), CZ + rad * sin(am)); o.rotation_euler = (am - pi / 2, 0, 0)


tangent_plate("cnt_mask_up", PHI_W - radians(58), PHI_W - radians(19), M_BLACK)
tangent_plate("cnt_mask_dn", PHI_W + radians(19), PHI_W + radians(62), M_BLACK)

# ---------- 纸签：立在计数器上，第 10–22 帧翻面（读带口 → 收货的芯片） ----------
SGW, SGH = 0.066, 0.0242
SG = Vector((CX, CY + 0.014, HT + 0.021))
t_ = 0.00025
v = [(-SGW / 2, -t_, -SGH / 2), (SGW / 2, -t_, -SGH / 2), (SGW / 2, -t_, SGH / 2), (-SGW / 2, -t_, SGH / 2),
     (-SGW / 2, t_, -SGH / 2), (-SGW / 2, t_, SGH / 2), (SGW / 2, t_, SGH / 2), (SGW / 2, t_, -SGH / 2)]
card = add_obj("sign_card", mesh_from("sign_card", v, [(0, 1, 2, 3), (4, 5, 6, 7)],
                                      loop_uvs=[[(0, 0), (1, 0), (1, 1), (0, 1)], [(0, 1), (0, 0), (1, 0), (1, 1)]]))
card.data.materials.append(mat_paper_tex("sign_a", f"{TEX}/sign_reader.png"))
card.data.materials.append(mat_paper_tex("sign_b", f"{TEX}/sign_chip.png"))
card.data.polygons[1].material_index = 1
sg = empty("sign_pivot", SG, (radians(-22), 0, 0)); card.parent = sg
for sx in (-1, 1):                                    # 两端各一根短销，不从字上穿过去
    cyl("sign_pin", SG + Vector((sx * (SGW / 2 - 0.0005), 0, 0)), SG + Vector((sx * (SGW / 2 + 0.004), 0, 0)), 0.0007, M_STEEL, 10)
for sx in (-1, 1):
    px = CX + sx * (SGW / 2 + 0.004)
    cyl("sign_post", (px, SG.y, HT - 0.001), (px, SG.y, SG.z + 0.002), 0.0013, M_BRASS, 12)
box("sign_base", CX - SGW / 2 - 0.008, CX + SGW / 2 + 0.008, SG.y - 0.006, SG.y + 0.006, HT, HT + 0.003, M_BRASS, bevel=0.0006)
interp("BEZIER")
sg.keyframe_insert("rotation_euler", frame=10)
sg.rotation_euler = (radians(-22 + 180), 0, 0); sg.keyframe_insert("rotation_euler", frame=22)


# ---------- 节拍器：木壳机械节拍器（底 110 mm 见方，高 215 mm），摆杆在正面 ----------
def metronome(name, cx, y_front, crank_to=None):
    b, t, H = 0.055, 0.019, 0.215
    cy = y_front + b
    v = [(cx - b, cy - b, 0), (cx + b, cy - b, 0), (cx + b, cy + b, 0), (cx - b, cy + b, 0),
         (cx - t, cy - t, H), (cx + t, cy - t, H), (cx + t, cy + t, H), (cx - t, cy + t, H)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    body = add_obj(name + "_body", mesh_from(name + "_body", v, f)); body.data.materials.append(WALNUT)
    bm = body.modifiers.new("bev", "BEVEL"); bm.width = 0.002; bm.segments = 3
    box(name + "_plinth", cx - b - 0.004, cx + b + 0.004, cy - b - 0.004, cy + b + 0.004, 0, 0.012, WALNUT, bevel=0.0015)
    cyl(name + "_cap", (cx, cy, H), (cx, cy, H + 0.004), 0.011, M_BRASS, 24)
    sl = (b - t) / H                                    # 正面每升高 1 m 向后退多少

    def face_quad(nm, z0, z1, hw0, hw1, off, mat, uv=None):
        q = [(cx - hw0, y_front + sl * z0 - off, z0), (cx + hw0, y_front + sl * z0 - off, z0),
             (cx + hw1, y_front + sl * z1 - off, z1), (cx - hw1, y_front + sl * z1 - off, z1)]
        o = add_obj(nm, mesh_from(nm, q, [(0, 1, 2, 3)], uvs=uv)); o.data.materials.append(mat); return o
    face_quad(name + "_panel", 0.030, 0.203, 0.031, 0.0125, 0.0012, M_FELT)
    M_SC = mat_paper_tex(name + "_scale", f"{TEX}/scale.png")
    face_quad(name + "_scaleplate", 0.078, 0.198, 0.0075, 0.0075, 0.0016, M_SC, uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
    PV = Vector((cx, y_front - 0.007, 0.060))            # 摆轴
    cyl(name + "_boss", (cx, PV.y - 0.003, PV.z), (cx, y_front + sl * PV.z, PV.z), 0.0045, M_BRASS, 24)
    pend = empty(name + "_pend", PV)
    rod = box(name + "_rod", cx - 0.0016, cx + 0.0016, PV.y - 0.0006, PV.y + 0.0006, PV.z - 0.012, PV.z + 0.150, M_STEEL)
    child(rod, pend, PV)
    wz = PV.z + 0.096
    wv = [(cx - 0.0125, PV.y - 0.0035, wz), (cx + 0.0125, PV.y - 0.0035, wz), (cx + 0.0125, PV.y + 0.0035, wz), (cx - 0.0125, PV.y + 0.0035, wz),
          (cx - 0.0085, PV.y - 0.0035, wz + 0.018), (cx + 0.0085, PV.y - 0.0035, wz + 0.018), (cx + 0.0085, PV.y + 0.0035, wz + 0.018), (cx - 0.0085, PV.y + 0.0035, wz + 0.018)]
    wt = add_obj(name + "_weight", mesh_from(name + "_weight", wv, f)); wt.data.materials.append(M_BRASS)
    wt.modifiers.new("bev", "BEVEL").width = 0.0006
    child(wt, pend, PV)
    if crank_to is not None:
        # 盖点臂：和摆杆同轴、固定在一起。摆到右头时，臂端的小印章正好落在窄缝正前方的白边上。
        # 下面的零件按「摆到右头」的姿态建，挂在 crank 上（crank 相对摆杆转 −TH_MAX）。
        crank = empty(name + "_crank", (0, 0, 0), (0, -TH_MAX, 0)); crank.parent = pend
        E = Vector((crank_to, PV.y - 0.0035, 0.026))
        A = Vector((cx, PV.y - 0.0035, PV.z))
        parts = [cyl(name + "_arm", A, E, 0.0019, M_STEEL, 14),
                 cyl(name + "_hub", A + Vector((0, -0.0025, 0)), A + Vector((0, 0.0025, 0)), 0.006, M_BRASS, 24),
                 cyl(name + "_bar", E + Vector((0, 0.0019, 0)), Vector((E.x, Y_DOT - 0.0016, E.z)), 0.0016, M_STEEL, 14),
                 cyl(name + "_drop", (E.x, Y_DOT, E.z + 0.0016), (E.x, Y_DOT, Z_TAPE + 0.011), 0.0016, M_STEEL, 14),
                 cyl(name + "_stamp", (E.x, Y_DOT, Z_TAPE + 0.012), (E.x, Y_DOT, Z_TAPE + 0.0022), 0.0046, M_BRASS, 24),
                 cyl(name + "_pad", (E.x, Y_DOT, Z_TAPE + 0.0022), (E.x, Y_DOT, Z_TAPE + 0.0002), 0.0042, M_PAD, 24)]
        for o in parts: child(o, crank, PV)
    interp("BEZIER")
    for f_ in range(-1, NF + 2):
        pend.rotation_euler = (0, theta(f_), 0); pend.keyframe_insert("rotation_euler", frame=f_)
    return pend


metronome("metro", SLIT_X - 0.070, YR + 0.075, crank_to=SLIT_X)

# ---------- 印带器（桌子左端）：托盘里的小卡 → 一摆印一格。y6 里不入画，全景里看得到 ----------
box("prn_foot_n", PRN_X - 0.06, PRN_X + 0.06, YR - 0.052, YR - 0.030, 0, 0.0135, PLY, bevel=0.0008)
box("prn_foot_f", PRN_X - 0.06, PRN_X + 0.06, YR + 0.030, YR + 0.052, 0, 0.0135, PLY, bevel=0.0008)
box("prn_body", PRN_X - 0.06, PRN_X + 0.06, YR - 0.052, YR + 0.052, 0.0135, 0.078, PLY, bevel=0.0012)
box("prn_slot", PRN_X + 0.0595, PRN_X + 0.0603, YR - 0.024, YR + 0.024, 0.0135, 0.0175, M_BLACK)
cyl("prn_collar", (PRN_X, YR, 0.078), (PRN_X, YR, 0.082), 0.009, M_BRASS, 24)
plg = empty("prn_plunger", (PRN_X, YR, 0.078))
child(cyl("prn_rod", (PRN_X, YR, 0.060), (PRN_X, YR, 0.112), 0.004, M_STEEL, 20), plg, plg.location)
kn = lathe("prn_knob", [(0.012 * sin(radians(a)), 0.012 - 0.012 * cos(radians(a))) for a in range(0, 181, 12)], 32, [WALNUT], split=0)
kn.location = (0, 0, 0.034); kn.parent = plg
interp("BEZIER")
for f_ in range(0, NF + 1, TB):
    for df, dz in ((-3, 0.0), (0, -0.013), (5, 0.0)):
        plg.location.z = 0.078 + dz; plg.keyframe_insert("location", frame=f_ + df)
# 托盘 + 八张小卡（接下来要印的八格）
TX0 = PRN_X - 0.095
box("tray", TX0 - 0.006, TX0 + 0.19, YR - 0.128, YR - 0.086, 0, 0.004, WALNUT, bevel=0.001)
for i in range(8):
    j = 25 + i
    x0 = TX0 + 0.004 + i * 0.023
    box(f"card{i}", x0, x0 + 0.020, YR - 0.122, YR - 0.092, 0.004, 0.0048, M_INK if bit(j) else M_PAPER)
metronome("metro2", PRN_X + 0.135, YR + 0.075)

# ---------- 透明尺：一格一道刻度。y6 里已经被拿走，放在桌子前沿 ----------
M_ACR, ba = principled("acrylic", **{"Base Color": (0.93, 0.97, 0.96, 1), "Roughness": 0.03, "IOR": 1.49})
ba.inputs["Transmission Weight"].default_value = 1.0
nt = M_ACR.node_tree; lp = nt.nodes.new("ShaderNodeLightPath"); tr = nt.nodes.new("ShaderNodeBsdfTransparent")
tr.inputs["Color"].default_value = (0.86, 0.92, 0.90, 1); mix = nt.nodes.new("ShaderNodeMixShader")
nt.links.new(lp.outputs["Is Shadow Ray"], mix.inputs[0]); nt.links.new(ba.outputs[0], mix.inputs[1]); nt.links.new(tr.outputs[0], mix.inputs[2])
nt.links.new(mix.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
ruler = empty("ruler", (-0.22, -0.27, 0), (0, 0, radians(7)))
RL = CELL * 8 + 0.012
box("ruler_body", -RL / 2, RL / 2, -0.016, 0.016, 0.0002, 0.0027, M_ACR, bevel=0.0004).parent = ruler
for i in range(9):
    x = -CELL * 4 + i * CELL
    box(f"ruler_tick{i}", x - 0.0003, x + 0.0003, -0.016, 0.004, 0.0027, 0.00274, M_BLACK).parent = ruler

# ---------- 杯子（远处，虚掉，帮画面落地） ----------
R_, Hm = 0.041, 0.092
prof = [(0.0, 0.0), (R_ - 0.004, 0.0), (R_ - 0.001, 0.001), (R_, 0.004), (R_, Hm - 0.002), (R_ - 0.001, Hm), (R_ - 0.003, Hm), (R_ - 0.004, Hm - 0.002),
        (R_ - 0.004, Hm - 0.016), (0.0, Hm - 0.016)]
mug = lathe("mug", prof, 64, [M_CER, M_COF], [0, 0, 0, 0, 0, 0, 0, 0, 1], split=50)
mug.location = (0.40, 0.21, 0.0)


# ---------- 发光信号（glow=1）：纸带前面放一块真电路板，走线上跑金色脉冲，进到一颗芯片的引脚 ----------
# 电路板：Poly Haven「Circuit Board」（CC0，Benny Weimer），缩到 0.6（约 24 cm 见方，接近 microATX）。
# 金色 = 电信号（系列配色）；电信号本身不发光，角注「金色发光为示意」。
PIN = None
if G:
    BS = 0.6
    BO = Vector((SLIT_X - BS * 0.024, YR - 0.040 - BS * 0.1986, BS * 0.006 + 0.0004))   # 芯片引脚的 x 对齐窄缝
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f"{S.get('model', DL + '/circuit_board')}/circuit_board_2k.gltf")
    for o in set(bpy.data.objects) - before:
        if o.parent is None:
            o.scale = (BS, BS, BS); o.location = BO

    def bw(x, y, z=0.0): return BO + BS * Vector((x, y, z))
    LZ = P.get("lanez", 0.0019)                              # 模型里板面在 z = 0.0015，走线贴在上面
    route = [(-0.196, -0.060), (0.000, -0.060), (0.014, -0.074), (0.0235, -0.074)]   # 模型坐标：沿电容和芯片之间的空道走，斜下去进方形芯片左侧的引脚
    pts = [bw(x, y, LZ) for x, y in route]
    seglen = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(seglen)
    hw = P.get("lanew", 0.0011) / 2
    verts, faces, luv = [], [], []
    acc = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; d = (b - a).normalized(); nrm = Vector((-d.y, d.x, 0)) * hw
        ext = d * hw * 0.42 if i < len(pts) - 2 else Vector((0, 0, 0))      # 拐角处多伸一点，接上下一段
        n0 = len(verts)
        verts += [tuple(a - nrm), tuple(a + nrm), tuple(b + ext + nrm), tuple(b + ext - nrm)]
        faces.append((n0, n0 + 3, n0 + 2, n0 + 1))
        d0, d1 = (total - acc) / CELL, (total - acc - seglen[i]) / CELL     # 离引脚还有几格
        luv.append([(d0, 0), (d1, 0), (d1, 1), (d0, 1)])
        acc += seglen[i]
    Q0, Q1 = -2, 24
    img = bpy.data.images.new("bits", (Q1 - Q0) * 16, 1)
    px = []
    for k in range((Q1 - Q0) * 16):
        vv = float(bit(Q0 + k // 16)); px += [vv, vv, vv, 1.0]
    img.pixels = px; img.update(); img.pack()               # 不打包的话 Cycles 读到的是一张空图
    M_SIG, bsg = principled("signal", **{"Base Color": (0.55, 0.30, 0.10, 1), "Metallic": 1.0, "Roughness": 0.35})
    nt = M_SIG.node_tree
    uvn = nt.nodes.new("ShaderNodeUVMap"); mpn = nt.nodes.new("ShaderNodeMapping")
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img; tx.interpolation = "Linear"; tx.extension = "EXTEND"
    img.colorspace_settings.name = "Non-Color"
    mpn.inputs["Scale"].default_value = (1 / (Q1 - Q0), 1, 1)
    nt.links.new(uvn.outputs["UV"], mpn.inputs["Vector"]); nt.links.new(mpn.outputs["Vector"], tx.inputs["Vector"])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = P.get("sig", 9.0)
    nt.links.new(tx.outputs["Color"], mul.inputs[0]); nt.links.new(mul.outputs[0], bsg.inputs["Emission Strength"])
    bsg.inputs["Emission Color"].default_value = (1.0, 0.56, 0.14, 1)
    loc = mpn.inputs["Location"]
    for f_ in (0, NF):                                         # 图样跟纸带同速往引脚走
        loc.default_value = ((f_ / TB - Q0) / (Q1 - Q0), 0, 0); loc.keyframe_insert("default_value", frame=f_)
    lane = add_obj("signal_lane", mesh_from("signal_lane", verts, faces, loop_uvs=luv)); lane.data.materials.append(M_SIG)
    # 引脚上的两个小发光点：跳变到达时金色闪一下（鼓点）；每个节拍正中蓝色亮一下（清点一次）
    PIN = pts[-1]

    def blip(name, at, rad, color, frames, peak):
        m, b = principled(name, **{"Base Color": (0.02, 0.02, 0.02, 1), "Roughness": 0.3})
        b.inputs["Emission Color"].default_value = (*color, 1); e = b.inputs["Emission Strength"]; e.default_value = 0.0
        cyl(name, at, at + Vector((0, 0, 0.0005)), rad, m, 20)
        for f_ in frames:
            for df, val in ((-1, 0.0), (0, peak), (1, peak * 0.6), (2, peak * 0.2), (4, 0.0)):
                if f_ + df >= 0:
                    e.default_value = val; e.keyframe_insert("default_value", frame=f_ + df)
        set_interp(m.node_tree, "LINEAR")
    blip("pin_flash", PIN + Vector((0.0016, 0, 0.0002)), 0.0016, (1.0, 0.56, 0.14), EDGES, P.get("sig", 9.0) * 4)
    blip("chip_sample", bw(0.042, -0.0775, P.get("chipz", 0.0066)), 0.0022, (0.03, 0.22, 1.0),
         list(range(TB // 2, NF, TB)), P.get("smp", 3.0))
    set_interp(nt, "LINEAR")

# ---------- 光：窗外的太阳 + 天空（只从窗进来），和定妆静帧一样 ----------
el, az = radians(P["el"]), radians(P["az"])
travel = Vector((cos(az) * cos(el), -sin(az) * cos(el), -sin(el)))
sd = bpy.data.lights.new("sun", "SUN"); sd.energy = P["sun"]; sd.angle = radians(0.53); sd.color = (1.0, 0.86, 0.70)
so = bpy.data.objects.new("sun", sd); col.objects.link(so)
so.rotation_euler = travel.to_track_quat("-Z", "Y").to_euler()
w = bpy.data.worlds.new("w"); scene.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (0.50, 0.68, 1.0, 1); bg.inputs["Strength"].default_value = P["sky"]
pd = bpy.data.lights.new("portal", "AREA"); pd.shape = "RECTANGLE"; pd.size = WY1 - WY0; pd.size_y = WZ1 - WZ0
pd.cycles.is_portal = True
po = bpy.data.objects.new("portal", pd); col.objects.link(po)
po.location = (-0.95, (WY0 + WY1) / 2, (WZ0 + WZ1) / 2); po.rotation_euler = (0, radians(-90), 0)

# ---------- 相机：50 mm、浅景深。y6 一个连续镜头，从读带口中景（C1）慢推到窄缝近景（C2） ----------
C1 = dict(t=(SLIT_X - 0.012, YR + 0.045, 0.062), dist=0.84, pitch=31, yaw=5)
C2 = dict(t=(SLIT_X + 0.058, YR + 0.022, 0.040), dist=0.66, pitch=40, yaw=3)
for k_ in ("dist", "pitch", "yaw"):
    for nm_, C in (("c1", C1), ("c2", C2)):
        if f"{nm_}{k_}" in P: C[k_] = P[f"{nm_}{k_}"]
MOVE = (P.get("m0", 52), P.get("m1", 178))               # 推镜的起止帧
if G:                                                     # 发光信号那一段：上半是纸带和读带口，下半是电路板；慢推
    # 近、低：走线横贯画面下半，纸带和读带口在后面略虚（第一版机位太远，板子小、走线只是一条细线）
    gt = Vector((SLIT_X + P.get("gtx", -0.020), YR + P.get("gty", -0.118), 0.0))
    C1 = dict(t=tuple(gt), dist=P.get("gdist", 0.66), pitch=P.get("gpitch", 45), yaw=P.get("gyaw", 5))
    C2 = dict(t=tuple(gt + Vector((0.010, -0.006, 0))), dist=P.get("gdist", 0.66) - 0.05, pitch=P.get("gpitch", 45) + 1, yaw=P.get("gyaw", 5) - 1.5)
    MOVE = (0, 96)


def cam_pose(f):
    u = min(1.0, max(0.0, (f - MOVE[0]) / (MOVE[1] - MOVE[0]))); u = u * u * (3 - 2 * u)
    u = 0.94 * u + 0.06 * f / NF                         # 全程带一点很慢的推进，镜头不完全停死
    T = Vector(C1["t"]).lerp(Vector(C2["t"]), u)
    d = C1["dist"] + (C2["dist"] - C1["dist"]) * u
    pt = radians(C1["pitch"] + (C2["pitch"] - C1["pitch"]) * u); yw = radians(C1["yaw"] + (C2["yaw"] - C1["yaw"]) * u)
    loc = T + d * Vector((sin(yw) * cos(pt), -cos(yw) * cos(pt), sin(pt)))
    return loc, (T - loc).normalized().to_track_quat("-Z", "Y").to_euler()


cd = bpy.data.cameras.new("cam"); cd.lens = P["lens"]; cd.sensor_width = 36; cd.sensor_fit = "AUTO"
cam = bpy.data.objects.new("cam", cd); col.objects.link(cam); scene.camera = cam
foc = empty("focus", (SLIT_X + 0.03, YR, 0.012) if not G else (SLIT_X - 0.02, YR - 0.19, 0.004))
cd.dof.use_dof = True; cd.dof.aperture_fstop = P["fstop"]; cd.dof.focus_object = foc; cd.dof.aperture_blades = 7
RES = (1080, 1920)
if S.get("cam") == "E":                                   # 全景：横屏，看整套装置的布局
    RES = (1920, 1080); cd.lens = 35; cd.dof.aperture_fstop = 8
    T = Vector((-0.15, -0.03, 0.03)); pt, yw = radians(P.get("epitch", 38)), radians(P.get("eyaw", 0))
    cam.location = T + P.get("edist", 1.25) * Vector((sin(yw) * cos(pt), -cos(yw) * cos(pt), sin(pt)))
    cam.rotation_euler = (T - cam.location).normalized().to_track_quat("-Z", "Y").to_euler()
else:
    interp("LINEAR")
    for f_ in range(-1, NF + 2):
        cam.location, cam.rotation_euler = cam_pose(f_)
        cam.keyframe_insert("location", frame=f_); cam.keyframe_insert("rotation_euler", frame=f_)
    set_interp(cam, "LINEAR")

# ---------- 渲染 ----------
scene.render.fps = FPS; scene.frame_start = 0; scene.frame_end = NF - 1
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
if P.get("gpu"):
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"; prefs.get_devices()
    for d_ in prefs.devices: d_.use = True
    optix = [d_.name for d_ in prefs.devices if d_.type == "OPTIX"]
    print("[gpu]", optix)
    if not optix: raise SystemExit("gpu=1 但没有可用的 OptiX 设备：不要退回 CPU 慢慢渲（2026-11-11 一台 RTX 5090 上每帧 290 秒）")
    scene.cycles.device = "GPU"
scene.cycles.samples = SAMPLES
scene.cycles.use_adaptive_sampling = True; scene.cycles.adaptive_threshold = P.get("thr", 0.01 if SAMPLES > 200 else 0.05)
scene.cycles.use_denoising = True; scene.cycles.denoiser = "OPENIMAGEDENOISE"
scene.cycles.max_bounces = 8; scene.cycles.diffuse_bounces = 5; scene.cycles.glossy_bounces = 4
scene.cycles.transparent_max_bounces = 8
scene.cycles.sample_clamp_indirect = 8.0
scene.cycles.caustics_reflective = False; scene.cycles.caustics_refractive = False
scene.render.use_motion_blur = bool(P["mb"]); scene.render.motion_blur_shutter = 0.5
scene.render.use_persistent_data = True
scene.render.resolution_x, scene.render.resolution_y = RES; scene.render.resolution_percentage = SCALE
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "None"
scene.view_settings.exposure = P["exposure"]
scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_depth = "8"
scene.render.image_settings.compression = 30
scene.render.threads_mode = "AUTO"

if P.get("anchors"):
    from bpy_extras.object_utils import world_to_camera_view
    pts = {"lamp": LAMP + Vector((0, 0, 0.004)), "slit": Vector((SLIT_X, YR + 0.005, PZ1)), "count": Vector((CX, CY, CZ + WR)),
           "sign": SG.copy(), "metro_top": Vector((SLIT_X - 0.07, YR + 0.13, 0.215))}
    if PIN is not None: pts["pin"] = PIN.copy()
    out = {"fps": FPS, "frames": NF, "pts": {k: [] for k in list(pts) + ["band_l", "band_r"]}}
    for f_ in range(NF):
        scene.frame_set(f_)
        bl_, br_ = SLIT_X - CELL * (BAND[-1] + 1) + V * f_, SLIT_X - CELL * BAND[0] + V * f_
        allp = dict(pts, band_l=Vector((bl_, Y_NEAR, Z_TAPE)), band_r=Vector((br_, Y_NEAR, Z_TAPE)))
        for k_, p_ in allp.items():
            c = world_to_camera_view(scene, cam, p_)
            out["pts"][k_].append([round(c.x, 4), round(1 - c.y, 4)])
    json.dump(out, open(OUT, "w"))
    print("[anchors]", OUT)
elif "fs" in P:
    os.makedirs(OUT, exist_ok=True)
    scene.frame_start, scene.frame_end = int(P["fs"]), int(P["fe"])
    scene.render.filepath = os.path.join(OUT, "f_####")
    T0 = {}
    log = open(os.path.join(OUT, f"times_{int(P['fs']):04d}.txt"), "w")
    bpy.app.handlers.render_pre.append(lambda *a: T0.__setitem__("t", time.time()))

    def _post(*a):
        log.write(f"{scene.frame_current} {time.time() - T0['t']:.2f}\n"); log.flush()
    bpy.app.handlers.render_post.append(_post)
    t_all = time.time()
    bpy.ops.render.render(animation=True)
    log.write(f"total {time.time() - t_all:.1f}\n"); log.close()
else:
    scene.frame_set(int(P.get("still", 0)))
    scene.render.filepath = OUT
    bpy.ops.render.render(write_still=True)
