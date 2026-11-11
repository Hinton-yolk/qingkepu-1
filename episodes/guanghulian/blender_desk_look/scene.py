"""定妆静帧：「把纸桌拍成真的」。窗边木桌 + 纸条 + 平板 + 红线图钉。
所有东西按真实尺寸（米）。一个主光：窗外的太阳，穿过百叶窗；屏幕自发光；不加别的灯。

用法：
  blender -b -P scene.py -- <tex目录> <贴图下载目录> <输出png> [缩放% 默认25] [采样 默认48] [key=value ...]
可调参数（key=value）：pitch yaw dist lens fstop el az exposure screen sun sky tx ty tz
"""
import bpy, bmesh, sys, math
from math import sin, cos, radians, pi
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
TEX, DL, OUT = argv[0], argv[1], argv[2]
pos = [a for a in argv[3:] if "=" not in a]
SCALE = int(pos[0]) if len(pos) > 0 else 25
SAMPLES = int(pos[1]) if len(pos) > 1 else 48
P = dict(pitch=52, yaw=9, dist=0.82, lens=50, fstop=2.8, el=24, az=12,
         exposure=1.2, screen=0.55, sun=8.0, sky=0.8, tx=0.0, ty=0.012, tz=0.0,
         slat=14, focus=0.0)
for a in argv[3:]:
    if "=" in a:
        k, v = a.split("="); P[k] = float(v)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
col = scene.collection


# ---------- 小工具 ----------
def add_obj(name, mesh):
    o = bpy.data.objects.new(name, mesh); col.objects.link(o); return o


def mesh_from(name, verts, faces, uvs=None, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    if uvs:
        uvl = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            for li in poly.loop_indices:
                uvl.data[li].uv = uvs[me.loops[li].vertex_index]
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


def grid(name, nx, ny, f):
    """f(u,v) -> (x,y,z)；带 UV。"""
    verts, uvs, faces = [], [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            u, v = i / nx, j / ny
            verts.append(f(u, v)); uvs.append((u, v))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    return add_obj(name, mesh_from(name, verts, faces, uvs, smooth=True))


def lathe(name, prof, seg=48, mats=None, ring_mat=None, split=40):
    """prof: [(r,z)...] 绕 z 轴旋转。ring_mat[i] = 第 i 段用第几个材质。"""
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


# ---------- 材质 ----------
def mat_wood():
    m, b = principled("wood")
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / 1.1, 1 / 1.1, 1 / 1.1)
    mp.inputs["Location"].default_value = (0.31, 0.17, 0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    d = img_node(m, f"{DL}/wood_table_001_diff_4k.jpg")
    r = img_node(m, f"{DL}/wood_table_001_rough_4k.jpg", "Non-Color")
    n = img_node(m, f"{DL}/wood_table_001_nor_gl_4k.jpg", "Non-Color")
    for t in (d, r, n):
        t.projection = "BOX"; t.projection_blend = 0.1
        nt.links.new(mp.outputs["Vector"], t.inputs["Vector"])
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 1.0
    nt.links.new(n.outputs["Color"], nm.inputs["Color"])
    nt.links.new(d.outputs["Color"], b.inputs["Base Color"])
    # 桌面用久了有一层薄清漆：粗糙度整体压低一点
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = 0.22; mr.inputs["To Max"].default_value = 0.62
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


def mat_paper(name, path):
    m, b = principled(name, Roughness=0.78)
    t = img_node(m, path)
    m.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Sheen Weight"].default_value = 0.15
    bump(m, b, 2500, 0.25, 0.00004)
    return m


WOOD, WALL = mat_wood(), mat_wall()
M_PLAIN, _ = principled("plain", **{"Base Color": (0.72, 0.70, 0.66, 1), "Roughness": 0.9})
M_SLAT, _ = principled("slat", **{"Base Color": (0.80, 0.77, 0.70, 1), "Roughness": 0.55})

# ---------- 房间（封闭，只有左墙一扇窗） ----------
desk = box("desk", -0.80, 1.00, -0.42, 0.40, -0.032, 0.0, WOOD, bevel=0.0015)
box("wall_back", -1.0, 2.2, 0.40, 0.55, -0.75, 1.75, WALL)
box("wall_right", 2.2, 2.35, -2.6, 0.55, -0.75, 1.75, WALL)
box("wall_front", -1.0, 2.2, -2.75, -2.6, -0.75, 1.75, WALL)
box("floor", -1.0, 2.35, -2.75, 0.55, -0.9, -0.75, M_PLAIN)
box("ceil", -1.0, 2.35, -2.75, 0.55, 1.75, 1.9, M_PLAIN)
WY0, WY1, WZ0, WZ1 = -0.75, 0.38, 0.12, 1.30     # 窗洞
box("wl_low", -0.98, -0.80, -2.6, 0.40, -0.75, WZ0, WALL)
box("wl_top", -0.98, -0.80, -2.6, 0.40, WZ1, 1.75, WALL)
box("wl_front", -0.98, -0.80, -2.6, WY0, WZ0, WZ1, WALL)
box("wl_back", -0.98, -0.80, WY1, 0.40, WZ0, WZ1, WALL)
box("sill", -0.98, -0.775, WY0 - 0.02, WY1, WZ0 - 0.02, WZ0, M_SLAT)
# 百叶：50 mm 叶片，间距 45 mm
z = WZ0 + 0.03
k = 0
while z < WZ1 - 0.01:
    s = box(f"slat{k}", -0.025, 0.025, WY0 + 0.005, WY1 - 0.005, -0.0012, 0.0012, M_SLAT)
    s.location = (-0.89, 0, z); s.rotation_euler = (0, radians(P["slat"]), 0)
    z += 0.045; k += 1

# ---------- 纸条 ----------
def make_strip(name, tex, L, aspect, center, yaw, curlL, curlR, seed=0.0):
    Wd = L / aspect
    def surf(u, v):
        x, y = (u - 0.5) * L, (v - 0.5) * Wd
        zl = curlL * max(0.0, (0.28 - u) / 0.28) ** 2
        zr = curlR * max(0.0, (u - 0.66) / 0.34) ** 2
        tw = (v - 0.5) * 0.0025 * sin(3.0 * u + seed)          # 一点扭
        wav = 0.00035 * sin(9 * u + seed * 2)                    # 纸不会绝对平
        zz = 0.00018 + zl + zr + max(0.0, tw + wav + 0.0003)
        return (x, y, zz)
    o = grid(name, 96, 10, surf)
    o.data.materials.append(mat_paper(name, tex))
    sm = o.modifiers.new("sol", "SOLIDIFY"); sm.thickness = 0.00011; sm.offset = 1
    o.location = (center[0], center[1], 0); o.rotation_euler = (0, 0, radians(yaw))
    def world(u, v):
        p = Vector(surf(u, v))
        return Matrix.Rotation(radians(yaw), 4, "Z") @ p + Vector((center[0], center[1], 0))
    return o, world


AS_MAIN, AS_B = 2448 / 615, 2340 / 615
strip_main, sw = make_strip("strip_main", f"{TEX}/strip_main.png", 0.240, AS_MAIN, (-0.012, -0.060), -3.5, 0.0035, 0.0065, 0.4)
make_strip("strip_b", f"{TEX}/strip_b.png", 0.230, AS_B, (-0.075, -0.150), 8.0, 0.006, 0.002, 1.7)
make_strip("strip_c", f"{TEX}/strip_c.png", 0.230, AS_B, (0.085, -0.235), -13.0, 0.002, 0.008, 2.9)

# ---------- 平板（248.6 × 179.5 × 6.1 mm，斜靠在书上） ----------
def rrect(w, h, r, n=10):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for i in range(n + 1):
            a = radians(a0 + 90 * i / n)
            pts.append((cx + r * cos(a), cy + r * sin(a)))
    return pts


TW, TH, TT = 0.2486, 0.1795, 0.0061
LEAN = 64
pts = rrect(TW, TH, 0.012)
n = len(pts)
verts = [(x, y, -TT / 2) for x, y in pts] + [(x, y, TT / 2) for x, y in pts]
faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
M_ALU, _ = principled("alu", **{"Base Color": (0.62, 0.63, 0.65, 1), "Metallic": 1.0, "Roughness": 0.32})
tab = add_obj("tablet", mesh_from("tablet", verts, faces)); tab.data.materials.append(M_ALU)
bm = tab.modifiers.new("bev", "BEVEL"); bm.width = 0.0012; bm.segments = 4; bm.limit_method = "ANGLE"; bm.angle_limit = radians(50)
for p in tab.data.polygons: p.use_smooth = True
tab.modifiers.new("es", "EDGE_SPLIT").split_angle = radians(35)
gp = rrect(TW - 0.0016, TH - 0.0016, 0.0112)
M_SCR, bs = principled("screen", **{"Base Color": (0.004, 0.004, 0.005, 1), "Roughness": 0.045})
si = img_node(M_SCR, f"{TEX}/screen.png")
M_SCR.node_tree.links.new(si.outputs["Color"], bs.inputs["Emission Color"])
bs.inputs["Emission Strength"].default_value = P["screen"]
gl = add_obj("glass", mesh_from("glass", [(x, y, TT / 2 + 0.00006) for x, y in gp], [tuple(range(len(gp)))],
                                  uvs=[(x / TW + 0.5, y / TH + 0.5) for x, y in gp]))
gl.data.materials.append(M_SCR); gl.parent = tab
TAB_BASE = Vector((0.0, 0.058, 0.0))
Rt = Matrix.Rotation(radians(2.5), 4, "Z") @ Matrix.Rotation(radians(LEAN), 4, "X")
up_t = Rt @ Vector((0, 1, 0)); nrm_t = Rt @ Vector((0, 0, 1))
tab_c = TAB_BASE + up_t * (TH / 2) + Vector((0, 0, 0.0008)) - nrm_t * 0  # 中心
tab.matrix_world = Matrix.Translation(tab_c + nrm_t * (-TT / 2) + Vector((0, 0, TT / 2 * cos(radians(LEAN))))) @ Rt

# ---------- 书（平板靠着） ----------
def book(name, cx, cy, z0, w, d, h, yaw, cover):
    mc, _ = principled(name + "_c", **{"Base Color": cover, "Roughness": 0.6})
    mp_, bp_ = principled(name + "_p", **{"Base Color": (0.86, 0.83, 0.75, 1), "Roughness": 0.85})
    e = bpy.data.objects.new(name, None); col.objects.link(e)
    for nm_, (a, b_, c, d_, zz0, zz1, mm) in {
        "pg": (-w / 2 + 0.004, w / 2 - 0.003, -d / 2 + 0.003, d / 2 - 0.003, 0.0025, h - 0.0025, mp_),
        "c0": (-w / 2, w / 2, -d / 2, d / 2, 0, 0.0025, mc),
        "c1": (-w / 2, w / 2, -d / 2, d / 2, h - 0.0025, h, mc),
        "sp": (-w / 2, -w / 2 + 0.004, -d / 2, d / 2, 0, h, mc)}.items():
        o = box(name + nm_, a, b_, c, d_, zz0, zz1, mm, bevel=0.0006); o.parent = e
    e.location = (cx, cy, z0); e.rotation_euler = (0, 0, radians(yaw))


# 平板背面在高度 z 处的 y：base_y + z/tan(LEAN) + 厚度
def back_y(zz): return TAB_BASE.y + zz / math.tan(radians(LEAN)) + TT / sin(radians(LEAN))
book("bk1", 0.035, back_y(0.034) + 0.085, 0.0, 0.205, 0.165, 0.034, 3, (0.10, 0.16, 0.24, 1))
book("bk2", 0.030, back_y(0.062) + 0.080, 0.034, 0.195, 0.150, 0.028, -4, (0.42, 0.20, 0.12, 1))
book("bk3", 0.040, back_y(0.086) + 0.072, 0.062, 0.185, 0.140, 0.024, 2, (0.70, 0.66, 0.56, 1))

# ---------- 杯子 ----------
M_CER, _ = principled("ceramic", **{"Base Color": (0.80, 0.78, 0.72, 1), "Roughness": 0.22})
M_CER.node_tree.nodes["Principled BSDF"].inputs["Coat Weight"].default_value = 0.6
M_COF, _ = principled("coffee", **{"Base Color": (0.05, 0.025, 0.012, 1), "Roughness": 0.05})
R, Hm = 0.041, 0.092
prof = [(0.0, 0.0), (R - 0.004, 0.0), (R - 0.001, 0.001), (R, 0.004), (R, Hm - 0.002), (R - 0.001, Hm), (R - 0.003, Hm), (R - 0.004, Hm - 0.002),
        (R - 0.004, Hm - 0.016), (0.0, Hm - 0.016)]
mug = lathe("mug", prof, 64, [M_CER, M_COF], [0, 0, 0, 0, 0, 0, 0, 0, 1], split=50)
hv, hf = [], []
NS, NR = 28, 12
for i in range(NS + 1):
    a = -pi / 2 + pi * i / NS
    c = Vector((R - 0.004 + 0.030 * cos(a) * 1.0, 0, Hm * 0.5 + 0.030 * sin(a)))
    for j in range(NR):
        b_ = 2 * pi * j / NR
        nrm = Vector((cos(a), 0, sin(a)))
        hv.append(tuple(c + nrm * 0.0055 * cos(b_) + Vector((0, 0.0045 * sin(b_), 0))))
for i in range(NS):
    for j in range(NR):
        a = i * NR + j; b_ = i * NR + (j + 1) % NR
        hf.append((a, b_, b_ + NR, a + NR))
hd = add_obj("mug_handle", mesh_from("mug_handle", hv, hf, smooth=True)); hd.data.materials.append(M_CER); hd.parent = mug
mug.location = (-0.158, 0.185, 0.0); mug.rotation_euler = (0, 0, radians(100))

# ---------- 图钉 ----------
M_PIN, bpn = principled("pin", **{"Base Color": (0.62, 0.035, 0.03, 1), "Roughness": 0.18})
bpn.inputs["Coat Weight"].default_value = 0.5
M_STEEL, _ = principled("steel", **{"Base Color": (0.75, 0.75, 0.76, 1), "Metallic": 1.0, "Roughness": 0.25})


def pin(name, at, tilt=(10, 6)):
    mm = 0.001
    prof = [(0.0, -6 * mm), (0.45 * mm, -4 * mm), (0.45 * mm, 4.2 * mm),           # 针
            (3.9 * mm, 4.2 * mm), (4.3 * mm, 4.7 * mm), (4.3 * mm, 5.6 * mm), (3.8 * mm, 6.1 * mm),   # 下沿
            (2.3 * mm, 6.8 * mm), (2.1 * mm, 9.5 * mm), (2.6 * mm, 11.4 * mm),       # 腰
            (3.9 * mm, 12.0 * mm), (4.1 * mm, 12.6 * mm), (4.0 * mm, 13.6 * mm), (3.3 * mm, 14.3 * mm), (0.0, 14.5 * mm)]
    o = lathe(name, prof, 40, [M_STEEL, M_PIN], [0, 0, 0] + [1] * 11, split=35)
    o.location = at; o.rotation_euler = (radians(tilt[0]), radians(tilt[1]), 0)
    return o


PA = sw(0.31, 1.0) + Matrix.Rotation(radians(-3.5), 4, "Z") @ Vector((0, 0.0035, 0))   # 贴着主纸条上沿，「五个 1」正上方
PA.z = 0.0
PB = Vector((-0.012, TAB_BASE.y - 0.022, 0.0))  # 平板脚下
pin("pinA", (PA.x, PA.y, PA.z), (9, -7))
pin("pinB", (PB.x, PB.y, 0.0), (-8, 6))

# ---------- 红线：在两枚图钉的针上各绕一圈多，中间拉直 ----------
def thread_pts():
    pts = []
    hz = 0.0030                                # 绕在针上的高度
    dAB = (PB - PA); dAB.z = 0
    ang = math.atan2(dAB.y, dAB.x)
    rw = 0.0011
    # 尾巴（躺在纸条上）
    t0 = PA + Vector((-0.021, 0.006, 0.0008)); t1 = PA + Vector((-0.010, 0.010, 0.0012))
    a_in = ang + pi / 2 + 2.6 * pi
    pa0 = PA + Vector((rw * cos(a_in), rw * sin(a_in), hz - PA.z + PA.z))
    for i in range(14):
        t = i / 14
        pts.append((1 - t) ** 2 * t0 + 2 * t * (1 - t) * t1 + t * t * pa0)
    for i in range(32):                         # 绕 A
        a = a_in - 2.6 * pi * i / 31
        pts.append(Vector((PA.x + rw * cos(a), PA.y + rw * sin(a), hz + 0.0004 * i / 31)))
    s0 = pts[-1].copy()
    b_in = ang + pi / 2
    s1 = Vector((PB.x + rw * cos(b_in), PB.y + rw * sin(b_in), hz))
    for i in range(1, 30):                      # 拉直的一段，略垂
        t = i / 30
        p = s0.lerp(s1, t); p.z -= 0.0007 * sin(pi * t)
        pts.append(p)
    for i in range(36):                         # 绕 B
        a = b_in - 2.9 * pi * i / 35
        pts.append(Vector((PB.x + rw * cos(a), PB.y + rw * sin(a), hz - 0.0006 * i / 35)))
    e0 = pts[-1].copy(); e1 = PB + Vector((0.016, -0.006, 0.0012)); e2 = PB + Vector((0.034, 0.004, 0.00055))
    for i in range(1, 16):
        t = i / 15
        pts.append((1 - t) ** 2 * e0 + 2 * t * (1 - t) * e1 + t * t * e2)
    return pts


cu = bpy.data.curves.new("thread", "CURVE"); cu.dimensions = "3D"
sp = cu.splines.new("NURBS"); tp = thread_pts(); sp.points.add(len(tp) - 1)
for p_, v_ in zip(sp.points, tp): p_.co = (v_.x, v_.y, v_.z, 1)
sp.use_endpoint_u = True; sp.order_u = 3
cu.bevel_depth = 0.00048; cu.bevel_resolution = 3; cu.resolution_u = 4
M_THR, bt = principled("thread", **{"Base Color": (0.50, 0.02, 0.025, 1), "Roughness": 0.85})
bt.inputs["Sheen Weight"].default_value = 0.6
bump(M_THR, bt, 9000, 0.6, 0.0001, 2.0)
th = bpy.data.objects.new("thread", cu); col.objects.link(th); th.data.materials.append(M_THR)

# ---------- 荧光笔（开着盖，放在前景） ----------
M_HY, _ = principled("hl_y", **{"Base Color": (0.95, 0.80, 0.05, 1), "Roughness": 0.35})
M_HK, _ = principled("hl_k", **{"Base Color": (0.02, 0.02, 0.022, 1), "Roughness": 0.4})
mm = 0.001
pen = lathe("pen", [(0, 0), (6.2 * mm, 0), (7.0 * mm, 1 * mm), (7.0 * mm, 88 * mm), (6.4 * mm, 89 * mm), (6.4 * mm, 92 * mm),
                    (5.0 * mm, 104 * mm), (3.2 * mm, 106 * mm), (3.0 * mm, 110 * mm), (2.2 * mm, 113.5 * mm), (0, 113.5 * mm)],
            40, [M_HY, M_HK], [0, 0, 0, 0, 1, 1, 1, 0, 0, 0], split=30)
pen.rotation_euler = (radians(90), 0, radians(294)); pen.location = (0.200, -0.105, 0.0070)
cap = lathe("cap", [(0, 0), (7.2 * mm, 0), (7.6 * mm, 0.8 * mm), (7.6 * mm, 33 * mm), (7.0 * mm, 34 * mm), (0, 34 * mm)], 40, [M_HK], split=30)
cap.rotation_euler = (radians(90), 0, radians(40)); cap.location = (0.060, -0.175, 0.0076)

# ---------- 光：窗外的太阳 + 天空（只从窗进来） ----------
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

# ---------- 相机：真实焦距、浅景深 ----------
T = Vector((P["tx"], P["ty"], P["tz"]))
pt, yw = radians(P["pitch"]), radians(P["yaw"])
cd = bpy.data.cameras.new("cam"); cd.lens = P["lens"]; cd.sensor_width = 36; cd.sensor_fit = "AUTO"
cam = bpy.data.objects.new("cam", cd); col.objects.link(cam); scene.camera = cam
cam.location = T + P["dist"] * Vector((sin(yw) * cos(pt), -cos(yw) * cos(pt), sin(pt)))
view = (T - cam.location).normalized()
cam.rotation_euler = view.to_track_quat("-Z", "Y").to_euler()
# 对焦在主纸条和屏幕中心之间
d_strip = (sw(0.5, 0.5) - cam.location).dot(view)
d_tab = (tab_c - cam.location).dot(view)
cd.dof.use_dof = True; cd.dof.aperture_fstop = P["fstop"]
cd.dof.focus_distance = d_strip + (d_tab - d_strip) * (0.5 + P["focus"])
cd.dof.aperture_blades = 7
print(f"[cam] strip {d_strip:.3f} m, tablet {d_tab:.3f} m, focus {cd.dof.focus_distance:.3f} m")

if P.get("top"):      # 调灯用：正上方俯视整张桌子（x 向右，y 向上）
    cd.type = "ORTHO"; cd.ortho_scale = 1.9; cd.dof.use_dof = False
    cam.location = (0.1, 0.0, 1.2); cam.rotation_euler = (0, 0, 0)

# ---------- 渲染 ----------
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
if "gpu" in P and P["gpu"]:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"; prefs.get_devices()
    for d_ in prefs.devices: d_.use = True
    scene.cycles.device = "GPU"
scene.cycles.samples = SAMPLES
scene.cycles.use_adaptive_sampling = True; scene.cycles.adaptive_threshold = 0.01 if SAMPLES > 200 else 0.05
scene.cycles.use_denoising = True; scene.cycles.denoiser = "OPENIMAGEDENOISE"
scene.cycles.max_bounces = 8; scene.cycles.diffuse_bounces = 5; scene.cycles.glossy_bounces = 4
scene.cycles.sample_clamp_indirect = 8.0
scene.cycles.caustics_reflective = False; scene.cycles.caustics_refractive = False
scene.render.resolution_x = 1080; scene.render.resolution_y = 1920; scene.render.resolution_percentage = SCALE
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "None"
scene.view_settings.exposure = P["exposure"]
scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_depth = "16"
scene.render.filepath = OUT
scene.render.threads_mode = "AUTO"
bpy.ops.render.render(write_still=True)
