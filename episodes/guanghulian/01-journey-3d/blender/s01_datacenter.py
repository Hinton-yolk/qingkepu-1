# S01 数据中心 → 机柜 → 服务器（0–13 秒）。单位：1 = 1 m。
# 状态：v0 粗模（Animatic 和构图检查用）。机柜、服务器前面板和内部布局都是示例结构，不对应具体机型；不能当最终科学结构交付。
# 坐标：冷通道沿 +X，中心线 y = 0，宽 1.2 m。A 排在 +Y（正面 y = +0.6），B 排在 −Y（正面 y = −0.6，整柜绕 Z 转 180°）。
#       机柜 i 的中心 x = 0.3 + 0.6 i（i = −3 … 17，每排 21 个）。GPU A 在 A 排 i = 4 的第 2 台服务器（自下往上数），GPU B 在 B 排 i = 8 的同一层。
# 镜头：一个连续镜头。0–7 s 沿通道一点透视缓推；7–9.5 s 转向 A 柜；9.5–11 s 柜门、上方那台服务器和上盖淡出；11–13 s 沿 S02 的入射方向压到 GPU A 上方。
# 路径线（视觉隐喻）：GPU A →（金）→ 前面板光口 →（青，贴着一根黄色跳线：上线槽、过桥、到 B 柜）→ 光口 →（金）→ GPU B。1.5–7.5 s 匀速画出。
# 运行：blender -b --python-exit-code 1 --python s01_datacenter.py -- <输出目录> [--times 0.1,3,6,8.5,10.5,12.9] [--res 270x480] [--samples 20] [--anchors]
import sys, os, math, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Matrix
import common as C

T_BUILD = time.time()
shot = C.Shot('S01'); args = C.parse_args(); sc = C.reset(shot); random.seed(1)
rad = math.radians; V = Vector; PI = math.pi

# ---------- 尺寸和位置约定 ----------
N0, N1 = -3, 17                         # 机柜编号范围（每排 21 个）
RACK_W, RACK_D, RACK_H = 0.6, 1.2, 2.1
I_A, I_B = 4, 8                         # GPU A / GPU B 所在机柜的编号
K_HERO = 1                              # 第几台服务器（0 = 最下面）
U = 0.04445                             # 1U
U0 = 0.10 + 2 * U                       # 最下面一台服务器的底（下面留 2U 盲板）
SRV_PITCH = 9 * U                       # 8U 服务器 + 1U 盲板
SRV_Z = [U0 + k * SRV_PITCH for k in range(4)]
SRV_Y = 0.09                            # 服务器前面板在柜内的进深（柜门内侧留走线空间）
SW, SH, SD = 0.447, 0.355, 0.9          # 服务器机箱：宽、高（8U）、深
COLS = [(c - 1.5) * 0.106 for c in range(4)]; ROW_Y = (0.23, 0.49)     # GPU 模组：4 列 × 2 排，列距 106 mm，排距 260 mm
ZB = 0.2620                             # GPU 底板顶面（机箱内，示例：GPU 托盘在上层）
ZM = ZB + 0.0104                        # 模组小电路板顶面
G_LOCAL = V((COLS[1], ROW_Y[0], ZM + 0.00253))       # GPU A 芯片顶面中心（机箱坐标；散热器底座底面在它上方 0.1 mm）
PORT_X = [0.060 + 0.026 * j for j in range(4)]; PORT_Z = 0.052; PORT_HERO = 2      # 前面板 4 个光口；路径线走第 3 个
TRAY_Z = 2.30; TRAY_W = 0.30            # 线槽底面高度、宽度（线槽在机柜正面上方：y = ±0.6 … ±0.9）
X_CROSS = 3.9                           # 路径线过桥（跨通道的线槽）的位置
CROSS = (0.3, 3.9, 7.5)
CEIL_Z = 3.2
FOG = (0.034, 0.062, 0.105)             # 远处的雾色（也是相机直接看到的背景色）
CAM_END_OFFSET = V((-0.0795, -0.1967, 0.2553))      # 13.0 s 相机相对 G 的位置（主 agent 给定，对应 S02 首帧）
V_END = 0.06                            # 13.0 s 时沿入射方向的速度（m/s）；S02 目前从静止起步，见报告

def xc(i): return 0.3 + 0.6 * i
def to_world(row, i, p):
    """柜内坐标 → 世界坐标（B 排整柜转了 180°）"""
    return V((xc(i) + p[0], 0.6 + p[1], p[2])) if row == 'A' else V((xc(i) - p[0], -0.6 - p[1], p[2]))
def srv_to_rack(p, k=K_HERO): return V((p[0], SRV_Y + p[1], SRV_Z[k] + p[2]))
G_A = to_world('A', I_A, srv_to_rack(G_LOCAL)); G_B = to_world('B', I_B, srv_to_rack(G_LOCAL))

# ---------- 材质 ----------
M = {}; _MK = {}
def mk(key, builder, **kw):
    """登记一种材质；MF(key) 取它的可淡出版本（给要透明化的物体用）"""
    _MK[key] = (builder, kw); M[key] = builder(key, **kw); return M[key]
def MF(key):
    k = key + '_fade'
    if k not in M: b, kw = _MK[key]; M[k] = b(k, fade=True, **kw)
    return M[k]

class NT:
    """少写几行节点代码"""
    def __init__(s, m): s.N = m.node_tree.nodes; s.L = m.node_tree.links
    def m(s, op, a, b=None):
        n = s.N.new('ShaderNodeMath'); n.operation = op
        for i, v in enumerate((a, b)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: s.L.new(v, n.inputs[i])
        return n.outputs[0]
    def mix(s, fac, a, b):
        n = s.N.new('ShaderNodeMix'); n.data_type = 'RGBA'
        for key, v in (('Factor', fac), ('A', a), ('B', b)):
            if isinstance(v, (int, float)): n.inputs[key].default_value = v
            elif isinstance(v, tuple): n.inputs[key].default_value = (*v, 1)
            else: s.L.new(v, n.inputs[key])
        return n.outputs['Result']
    def obj_xyz(s):
        tc = s.N.new('ShaderNodeTexCoord'); sep = s.N.new('ShaderNodeSeparateXYZ'); s.L.new(tc.outputs['Object'], sep.inputs[0]); return sep.outputs

def floor_mat(name, fade=False):
    """架空地板：600 mm 方格、板缝；通道里（|y| < 0.6）是通风格栅板（程序纹理，不真打孔）"""
    m = C.pbr(name, (0.17, 0.195, 0.235), rough=0.30); t = NT(m); b = t.N['Principled BSDF']; o = t.obj_xyz()
    def cell(sock):
        a = t.m('DIVIDE', sock, 0.6); f = t.m('FRACT', a); return f, t.m('MINIMUM', f, t.m('SUBTRACT', 1.0, f)), t.m('FLOOR', a)
    u, du, iu = cell(o['X']); v, dv, iv = cell(o['Y']); e = t.m('MINIMUM', du, dv)
    seam = t.m('LESS_THAN', e, 0.004)
    aisle = t.m('LESS_THAN', t.m('ABSOLUTE', o['Y']), 0.6)
    inner = t.m('GREATER_THAN', e, 0.085)
    slots = t.m('LESS_THAN', t.m('FRACT', t.m('MULTIPLY', u, 22.0)), 0.42)
    fb = t.m('FRACT', t.m('MULTIPLY', v, 3.0)); bands = t.m('GREATER_THAN', t.m('MINIMUM', fb, t.m('SUBTRACT', 1.0, fb)), 0.07)
    slot = t.m('MULTIPLY', t.m('MULTIPLY', inner, slots), t.m('MULTIPLY', bands, aisle))
    dark = t.m('MAXIMUM', seam, slot)
    wn = t.N.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '2D'; cmb = t.N.new('ShaderNodeCombineXYZ'); t.L.new(iu, cmb.inputs['X']); t.L.new(iv, cmb.inputs['Y'])
    t.L.new(cmb.outputs[0], wn.inputs['Vector']); tint = t.m('ADD', 0.92, t.m('MULTIPLY', wn.outputs['Value'], 0.16))
    base = t.N.new('ShaderNodeMix'); base.data_type = 'RGBA'; base.blend_type = 'MULTIPLY'; base.inputs['Factor'].default_value = 1.0
    base.inputs['A'].default_value = (0.17, 0.195, 0.235, 1); cc = t.N.new('ShaderNodeCombineColor')
    for k in ('Red', 'Green', 'Blue'): t.L.new(tint, cc.inputs[k])
    t.L.new(cc.outputs[0], base.inputs['B'])
    t.L.new(t.mix(dark, base.outputs['Result'], (0.03, 0.033, 0.04)), b.inputs['Base Color'])
    t.L.new(t.m('ADD', 0.27, t.m('MULTIPLY', dark, 0.5)), b.inputs['Roughness'])
    bp = t.N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.6; bp.inputs['Distance'].default_value = 0.004
    t.L.new(t.m('SUBTRACT', 1.0, dark), bp.inputs['Height']); t.L.new(bp.outputs[0], b.inputs['Normal'])
    return m

def door_mat(name, fade=False):
    """冲孔网门：圆孔方阵（孔距 6 mm，开孔率约 60%），用透明度做，不真打孔；掠射角时看不穿（孔有厚度）"""
    m = C.pbr(name, (0.035, 0.037, 0.042), metallic=0.75, rough=0.40); t = NT(m); b = t.N['Principled BSDF']; o = t.obj_xyz()
    cmb = t.N.new('ShaderNodeCombineXYZ'); t.L.new(o['X'], cmb.inputs['X']); t.L.new(o['Z'], cmb.inputs['Y'])
    vo = t.N.new('ShaderNodeTexVoronoi'); vo.voronoi_dimensions = '2D'; vo.feature = 'F1'; vo.inputs['Scale'].default_value = 1 / 0.006; vo.inputs['Randomness'].default_value = 0.0
    t.L.new(cmb.outputs[0], vo.inputs['Vector'])
    hole = t.m('LESS_THAN', vo.outputs['Distance'], 0.44)
    lw = t.N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5
    mr = t.N.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'                # 看穿的程度 = 1 − smoothstep(0.80, 0.985, 掠射程度)
    mr.inputs['From Min'].default_value = 0.80; mr.inputs['From Max'].default_value = 0.985; mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = 0.0
    t.L.new(lw.outputs['Facing'], mr.inputs['Value'])
    alpha = t.m('SUBTRACT', 1.0, t.m('MULTIPLY', hole, mr.outputs['Result']))
    if fade:
        oi = t.N.new('ShaderNodeObjectInfo'); alpha = t.m('MULTIPLY', alpha, oi.outputs['Alpha'])
    t.L.new(alpha, b.inputs['Alpha']); return m

mk('floor', floor_mat)
mk('door', door_mat)
mk('rack', C.pbr, color=(0.040, 0.042, 0.048), metallic=0.6, rough=0.42, noise_scale=6, noise_rough=0.08)
mk('rail', C.pbr, color=(0.50, 0.51, 0.52), metallic=1.0, rough=0.45)
mk('blank', C.pbr, color=(0.030, 0.031, 0.034), metallic=0.3, rough=0.5)
mk('steel', C.pbr, color=(0.55, 0.56, 0.58), metallic=1.0, rough=0.42, noise_scale=8, noise_rough=0.1)
mk('lid', C.pbr, color=(0.55, 0.56, 0.58), metallic=1.0, rough=0.40, noise_scale=8, noise_rough=0.1)
mk('panel', C.pbr, color=(0.20, 0.21, 0.225), metallic=0.8, rough=0.48, noise_scale=20, noise_rough=0.06)
mk('black', C.pbr, color=(0.018, 0.018, 0.02), rough=0.5)
mk('fan', C.pbr, color=(0.006, 0.006, 0.007), rough=0.7)
mk('blade', C.pbr, color=(0.07, 0.072, 0.078), rough=0.42)
mk('wire', C.pbr, color=(0.75, 0.76, 0.78), metallic=1.0, rough=0.25)
mk('silver', C.pbr, color=(0.70, 0.71, 0.73), metallic=1.0, rough=0.35)
mk('drive', C.pbr, color=(0.10, 0.105, 0.115), metallic=0.7, rough=0.5)
mk('label', C.pbr, color=(0.75, 0.75, 0.73), rough=0.6)
mk('led', C.emit, color=(0.10, 1.0, 0.22), strength=6.0, aov=False)            # 指示灯：绿色（金 / 青只给路径线）
mk('yellow', C.pbr, color=(0.86, 0.76, 0.03), rough=0.48)                      # 单模跳线的黄色护套（不发光）
mk('yellow2', C.pbr, color=(0.74, 0.64, 0.05), rough=0.55)
mk('tray', C.pbr, color=(0.62, 0.63, 0.65), metallic=1.0, rough=0.38)
mk('ceil', C.pbr, color=(0.10, 0.105, 0.115), rough=0.8)
mk('wall', C.pbr, color=(0.30, 0.32, 0.35), rough=0.7)
mk('glass', C.emit, color=(0.62, 0.80, 1.0), strength=1.6, aov=False)          # 通道尽头门上的玻璃（门外的光）
mk('lightbar', C.emit, color=(0.74, 0.87, 1.0), strength=9.0, aov=False)      # 顶部灯带：冷白
mk('pcb', C.pbr, color=(0.010, 0.050, 0.036), rough=0.40, coat=0.4, noise_scale=60, noise_rough=0.08)
mk('substrate', C.pbr, color=(0.015, 0.085, 0.055), rough=0.42, coat=0.35)
mk('silicon', C.pbr, color=(0.30, 0.32, 0.37), metallic=0.92, rough=0.14)
mk('alu', C.pbr, color=(0.80, 0.81, 0.83), metallic=1.0, rough=0.34, noise_scale=300, noise_rough=0.1, stretch=(1, 1, 30))
mk('nickel', C.pbr, color=(0.78, 0.74, 0.66), metallic=1.0, rough=0.25)
mk('ferrite', C.pbr, color=(0.10, 0.10, 0.105), rough=0.7)
mk('can', C.pbr, color=(0.72, 0.73, 0.75), metallic=1.0, rough=0.3)
mk('dimm', C.pbr, color=(0.012, 0.03, 0.022), rough=0.45, coat=0.3)
mk('path_gold', C.emit, color=C.GOLD, strength=1.8)                             # 路径线：金 = 电（强度低一点，AgX 下才不发白）
mk('path_cyan', C.emit, color=C.CYAN, strength=1.8)                             # 路径线：青 = 光

# ---------- 建模小工具 ----------
def disc(m, r, loc, seg=20):
    """朝 −Y 的圆片"""
    vs = [m.bm.verts.new((loc[0] + r * math.cos(2 * PI * k / seg), loc[1], loc[2] + r * math.sin(2 * PI * k / seg))) for k in range(seg)]
    m.bm.faces.new(vs)
def annulus(m, r, w, loc, seg=24):
    """朝 −Y 的圆环（风扇格栅的钢丝圈）"""
    a = [m.bm.verts.new((loc[0] + (r - w) * math.cos(2 * PI * k / seg), loc[1], loc[2] + (r - w) * math.sin(2 * PI * k / seg))) for k in range(seg)]
    b = [m.bm.verts.new((loc[0] + (r + w) * math.cos(2 * PI * k / seg), loc[1], loc[2] + (r + w) * math.sin(2 * PI * k / seg))) for k in range(seg)]
    for k in range(seg): m.bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
def fillet(pts, r=0.02, n=4):
    """折线拐角倒圆（二次贝塞尔近似），跳线和路径线用同一条折线，保证路径线贴着跳线"""
    pts = [V(p) for p in pts]; out = [pts[0]]
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        da = a - b; dc = c - b; t = min(r, 0.45 * da.length, 0.45 * dc.length)
        if t < 1e-5: out.append(b); continue
        p1 = b + da.normalized() * t; p2 = b + dc.normalized() * t
        for k in range(n + 1):
            s = k / n; out.append((1 - s) ** 2 * p1 + 2 * s * (1 - s) * b + s * s * p2)
    out.append(pts[-1]); return out
def plen(pts): return sum((V(b) - V(a)).length for a, b in zip(pts, pts[1:]))
def tubes(name, lines, r, mat, col, nurbs=False, res=2):
    """一个曲线物体里放多条管（跳线束）。lines 的元素是点列，或 (点列, 半径倍数)，半径倍数也可以逐点给"""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = res; cu.use_fill_caps = True; cu.resolution_u = 3
    cu.bevel_factor_mapping_start = 'SPLINE'; cu.bevel_factor_mapping_end = 'SPLINE'
    for ln in lines:
        pts, rf = ln if isinstance(ln, tuple) else (ln, 1.0)
        sp = cu.splines.new('NURBS' if nurbs else 'POLY'); sp.points.add(len(pts) - 1)
        for i, (p, c) in enumerate(zip(sp.points, pts)): p.co = (c[0], c[1], c[2], 1); p.radius = rf[i] if isinstance(rf, list) else rf
        if nurbs: sp.use_endpoint_u = True; sp.order_u = min(4, len(pts))
    if mat: cu.materials.append(mat)
    return C.link(bpy.data.objects.new(name, cu), col)
def finish(meshes, col, prefix, bevel=None):
    """把按材质分组的 Mesh 变成物体，记下材质键（淡出时换成可淡出版本）"""
    out = []
    for key, m in meshes.items():
        if not len(m.bm.verts): m.bm.free(); continue
        o = m.obj(f'{prefix}_{key}', M[key], col, bevel=(bevel or {}).get(key, 0.0), smooth=key in ('can',)); o['mkey'] = key; out.append(o)
    return out

# ---------- 8U 风冷 AI 服务器（实例源）：原点在前面板底边中点，+Y 往机箱里 ----------
def build_server():
    col = C.collection('SRC_服务器'); g = {k: C.Mesh() for k in ('steel', 'lid', 'panel', 'black', 'fan', 'blade', 'wire', 'silver', 'drive', 'label', 'led')}
    # 机箱：底、侧壁、后壁；上盖单独一个物体（GPU A 那台要淡出）
    g['steel'].box((SW, SD, 0.0012), (0, SD / 2, 0.0006))
    for s in (-1, 1): g['steel'].box((0.0012, SD, SH), (s * (SW / 2 - 0.0006), SD / 2, SH / 2))
    g['steel'].box((SW, 0.0012, SH), (0, SD, SH / 2))
    g['lid'].box((SW, SD - 0.004, 0.0012), (0, SD / 2 + 0.002, SH - 0.0006))
    g['panel'].box((SW, 0.003, SH), (0, 0.0015, SH / 2))
    for s in (-1, 1):                                   # 挂耳、把手、松不脱螺钉
        ex = s * (SW / 2 + 0.0095)
        g['panel'].box((0.019, 0.003, SH), (ex, 0.0015, SH / 2))
        g['black'].box((0.010, 0.010, 0.130), (ex, -0.030, 0.205))
        for dz in (-0.058, 0.058): g['black'].box((0.008, 0.028, 0.008), (ex, -0.014, 0.205 + dz))
        for z in (0.030, SH - 0.030): g['silver'].cyl(0.005, 0.007, (ex, -0.0035, z), rot=(PI / 2, 0, 0), seg=12)
    # 风扇墙：3 排 × 5 个 80 mm 风扇模块（热插拔模块：外框、叶轮、钢丝格栅、指示灯）
    for r in range(3):
        for c in range(5):
            fx = (c - 2) * 0.0865; fz = 0.135 + r * 0.0865
            g['black'].box((0.083, 0.006, 0.083), (fx, -0.003, fz)); g['black'].box((0.081, 0.052, 0.081), (fx, 0.030, fz))
            disc(g['fan'], 0.0375, (fx, -0.0062, fz))
            g['blade'].cyl(0.014, 0.004, (fx, -0.0085, fz), rot=(PI / 2, 0, 0), seg=16)
            for k in range(7):
                a = 2 * PI * k / 7 + r + c
                g['blade'].box((0.023, 0.0012, 0.013), (fx + 0.0255 * math.cos(a), -0.0075, fz + 0.0255 * math.sin(a)), rot=(0.45, -a, 0))
            for rr in (0.0125, 0.0210, 0.0295, 0.0372): annulus(g['wire'], rr, 0.0009, (fx, -0.0108, fz))
            for a in (PI / 4, -PI / 4): g['wire'].box((0.078, 0.0010, 0.0018), (fx, -0.0112, fz), rot=(0, a, 0))
            for sx in (-1, 1):
                for sz in (-1, 1): g['silver'].cyl(0.0022, 0.002, (fx + sx * 0.0365, -0.0065, fz + sz * 0.0365), rot=(PI / 2, 0, 0), seg=8)
            g['panel'].box((0.022, 0.004, 0.005), (fx, -0.008, fz - 0.0385))
            g['led'].box((0.003, 0.001, 0.003), (fx + 0.030, -0.0066, fz + 0.0385))
    # 下面 2U：硬盘位、进风栅、I/O 区（4 个光模块端口等）
    for i in range(8):
        dx = -0.2035 + i * 0.017
        g['drive'].box((0.0155, 0.005, 0.076), (dx, -0.0025, 0.046)); g['silver'].box((0.005, 0.003, 0.030), (dx, -0.0062, 0.030))
        g['black'].box((0.011, 0.001, 0.034), (dx, -0.0054, 0.064)); g['led'].box((0.002, 0.001, 0.002), (dx + 0.004, -0.0054, 0.085 - 0.004))
    g['black'].box((0.100, 0.001, 0.070), (-0.020, -0.0005, 0.046))
    for k in range(9): g['panel'].box((0.100, 0.003, 0.0030), (-0.020, -0.0015, 0.014 + k * 0.008))
    g['panel'].box((0.172, 0.002, 0.078), (0.130, -0.001, 0.046))
    for j, px in enumerate(PORT_X):
        g['silver'].box((0.0215, 0.0015, 0.0125), (px, -0.0026, PORT_Z)); g['black'].box((0.0190, 0.0012, 0.0100), (px, -0.0036, PORT_Z))
        g['led'].box((0.002, 0.001, 0.002), (px - 0.006, -0.0026, PORT_Z + 0.0095))
        if j in (0, PORT_HERO):                         # 插着的光模块 + 拉环
            g['silver'].box((0.0183, 0.020, 0.0085), (px, -0.010, PORT_Z)); g['label'].box((0.011, 0.026, 0.0012), (px, -0.031, PORT_Z - 0.003))
    for px in (0.060, 0.080): g['silver'].box((0.0165, 0.0015, 0.0135), (px, -0.0026, 0.022)); g['black'].box((0.0140, 0.0012, 0.0100), (px, -0.0036, 0.0215))
    for pz in (0.017, 0.027): g['black'].box((0.0130, 0.0012, 0.0055), (0.106, -0.0026, pz))
    g['silver'].cyl(0.0045, 0.003, (0.200, -0.0035, 0.072), rot=(PI / 2, 0, 0), seg=12)
    for k in range(3): g['led'].box((0.0025, 0.001, 0.0025), (0.170 + k * 0.008, -0.0026, 0.072))
    g['label'].box((0.034, 0.0006, 0.009), (0.165, -0.0024, 0.020))
    finish(g, col, '服务器'); return col

# ---------- 服务器内部（实例源，只放在 A、B 两台里）：示例布局，上层是 GPU 托盘 ----------
def build_internals():
    col = C.collection('SRC_服务器内部'); g = {k: C.Mesh() for k in ('steel', 'pcb', 'substrate', 'silicon', 'nickel', 'alu', 'ferrite', 'can', 'black', 'dimm', 'label', 'silver')}
    g['steel'].box((SW - 0.004, SD - 0.066, 0.0015), (0, 0.066 + (SD - 0.066) / 2, ZB - 0.0038))        # 托盘钣金
    g['pcb'].box((0.432, 0.550, 0.003), (0, 0.345, ZB - 0.0015))                                          # GPU 底板
    for cx in COLS:
        for ry in ROW_Y:
            g['pcb'].box((0.102, 0.200, 0.0024), (cx, ry, ZM - 0.0012))                                   # 模组小电路板
            for sx in (-1, 1): g['black'].box((0.006, 0.150, 0.008), (cx + sx * 0.044, ry, ZB + 0.004))   # 板间连接器
            g['substrate'].box((0.072, 0.072, 0.0016), (cx, ry, ZM + 0.0008)); g['silicon'].box((0.026, 0.031, 0.00078), (cx, ry, ZM + 0.00214))
            g['nickel'].box((0.100, 0.100, 0.005), (cx, ry, ZM + 0.00263 + 0.0025))                       # 散热器底座
            for k in range(-24, 25): g['alu'].box((0.0005, 0.096, 0.040), (cx + k * 0.002, ry, ZM + 0.00763 + 0.020))   # 鳍片：面垂直于 X，风沿 Y 吹
            for sy in (-1, 1):                                                                            # 供电：电感、铝壳电容
                for k in range(8): g['ferrite'].box((0.010, 0.010, 0.007), (cx + (k - 3.5) * 0.0122, ry + sy * 0.062, ZM + 0.0035))
                for k in range(9): g['can'].cyl(0.00315, 0.0075, (cx + (k - 4) * 0.0105, ry + sy * 0.078, ZM + 0.00375), seg=10)
    # 后段：主板、2 个处理器散热器、内存条排、电源（都是示例）
    g['pcb'].box((0.432, 0.170, 0.003), (0, 0.715, ZB - 0.0015))
    for sx in (-1, 1):
        g['nickel'].box((0.090, 0.110, 0.005), (sx * 0.070, 0.715, ZB + 0.008))
        for k in range(-17, 18): g['alu'].box((0.0006, 0.108, 0.034), (sx * 0.070 + k * 0.0025, 0.715, ZB + 0.0105 + 0.017))
    dimm_x = [s * (0.128 + k * 0.0098) for s in (-1, 1) for k in range(9)] + [(k - 1) * 0.0098 for k in range(3)]
    for dx in dimm_x:
        g['black'].box((0.0060, 0.142, 0.006), (dx, 0.715, ZB + 0.003)); g['dimm'].box((0.0014, 0.1333, 0.031), (dx, 0.715, ZB + 0.006 + 0.0155))
        g['label'].box((0.0016, 0.050, 0.012), (dx, 0.705, ZB + 0.022))
        for sy in (-1, 1): g['label'].box((0.0050, 0.006, 0.012), (dx, 0.715 + sy * 0.071, ZB + 0.008))
    for k in range(4):
        px = (k - 1.5) * 0.105; g['steel'].box((0.100, 0.085, 0.041), (px, 0.853, ZB + 0.0205)); g['black'].box((0.060, 0.002, 0.030), (px, 0.8095, ZB + 0.0205))
    for sx in (-1, 1): g['black'].box((0.012, 0.76, 0.016), (sx * 0.2135, 0.50, ZB + 0.012))            # 两侧的供电线束（示意）
    g['steel'].box((SW - 0.006, 0.012, 0.030), (0, 0.36, ZB + 0.018))                                    # 两排模组之间的横梁（低于散热器顶，不挡镜头）
    finish(g, col, '内部', bevel={'nickel': 0.0006, 'ferrite': 0.0008}); return col

# ---------- 1U 交换机（实例源）：原点同服务器 ----------
def build_switch():
    col = C.collection('SRC_交换机'); g = {k: C.Mesh() for k in ('panel', 'black', 'silver', 'led', 'label')}
    g['panel'].box((0.440, 0.45, 0.0435), (0, 0.225, U / 2))
    for s in (-1, 1): g['panel'].box((0.021, 0.003, 0.0435), (s * 0.2305, 0.0015, U / 2)); g['silver'].cyl(0.004, 0.006, (s * 0.2305, -0.003, U / 2), rot=(PI / 2, 0, 0), seg=10)
    for j in range(16):
        px = -0.185 + j * 0.0215
        for z in (0.0135, 0.0300):
            g['black'].box((0.0190, 0.0012, 0.0100), (px, -0.0006, z)); g['led'].box((0.0016, 0.001, 0.0016), (px - 0.006, -0.0006, z + 0.0068))
        if j % 3 == 1: g['silver'].box((0.0183, 0.018, 0.0085), (px, -0.009, 0.0300)); g['label'].box((0.011, 0.022, 0.0012), (px, -0.028, 0.027))
    g['label'].box((0.030, 0.0006, 0.008), (0.185, -0.0004, 0.022))
    finish(g, col, '交换机'); return col

SRV = build_server(); INTL = build_internals(); SWT = build_switch()

# ---------- 机柜里的跳线走法（柜内坐标）：光口 → 柜门内侧的理线区 → 向上出柜顶 → 翻过线槽边沿 → 落到线槽里 ----------
RISER_X = 0.257
def jumper_route(px, z, lane, tail=0.35):
    y = 0.040 + lane * 0.0035
    pts = [(px, SRV_Y - 0.020, z), (px, y, z), (RISER_X, y, z), (RISER_X, y, 2.17), (RISER_X, -0.032, 2.25), (RISER_X, -0.032, 2.405),
           (RISER_X, 0.035 + lane * 0.004, 2.405), (RISER_X, 0.035 + lane * 0.004, TRAY_Z + 0.008)]
    if tail: pts.append((RISER_X + tail, 0.045 + lane * 0.004, TRAY_Z + 0.008))
    return fillet(pts, 0.022)
LANE_HERO = 3
def hero_route(): return jumper_route(PORT_X[PORT_HERO], SRV_Z[K_HERO] + PORT_Z, LANE_HERO, tail=0)

def place_server(col, k, mode, parent=None):
    """mode：'inst' 整台实例；'lid' 只有上盖可淡出；'all' 整台可淡出。返回可淡出的物体"""
    loc = (0, SRV_Y, SRV_Z[k]); fades = []
    if mode == 'inst':
        o = C.instance_collection(SRV, f'服务器{k}', loc, col=col); o.parent = parent; return fades
    for s in SRV.objects:
        o = C.instance(s, f'A_{s.name}_{k}', loc, col=col); o.parent = parent
        if mode == 'all' or s['mkey'] == 'lid':
            o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = MF(s['mkey']); fades.append(o)
    return fades

def assemble_rack(col, hero=False, parent=None):
    """一个机柜（柜内坐标：x ∈ ±0.3，y = 0 是柜门外表面，往 +y 是柜深）。hero=True 时返回要淡出的物体（柜门、上方服务器、上盖）"""
    fd = {'door': [], 'upper': [], 'lid': []}; objs = []
    g = {k: C.Mesh() for k in ('rack', 'rail')}
    g['rack'].box((RACK_W, RACK_D, 0.06), (0, RACK_D / 2, 0.03))
    for s in (-1, 1):
        g['rack'].box((0.028, 0.040, RACK_H - 0.06), (s * 0.286, 0.045, RACK_H / 2 + 0.03)); g['rack'].box((0.04, 0.04, RACK_H - 0.06), (s * 0.28, RACK_D - 0.02, RACK_H / 2 + 0.03))
        g['rack'].box((0.002, RACK_D - 0.03, RACK_H - 0.08), (s * 0.299, RACK_D / 2 + 0.015, RACK_H / 2 + 0.03))
        g['rail'].box((0.030, 0.003, 1.90), (s * 0.2405, SRV_Y + 0.0035, 1.05))
    g['rack'].box((RACK_W, RACK_D - 0.14, 0.02), (0, 0.14 + (RACK_D - 0.14) / 2, RACK_H - 0.01)); g['rack'].box((RACK_W, 0.03, 0.04), (0, 0.015, RACK_H - 0.02))
    g['rack'].box((RACK_W - 0.01, 0.01, RACK_H - 0.1), (0, RACK_D - 0.005, RACK_H / 2 + 0.02))
    objs += finish(g, col, '机柜')
    # 柜门：门框 + 冲孔网 + 把手
    d = C.Mesh()
    for s in (-1, 1): d.box((0.035, 0.02, 2.0), (s * 0.2825, 0.01, 1.06))
    for z in (0.0775, 2.0425): d.box((0.53, 0.02, 0.035), (0, 0.01, z))
    d.box((0.018, 0.012, 0.16), (-0.283, -0.006, 1.05))
    o = d.obj('柜门框', MF('rack') if hero else M['rack'], col); objs.append(o); fd['door'].append(o)
    o = C.box('柜门网', (0.53, 0.003, 1.93), (0, 0.010, 1.06), MF('door') if hero else M['door'], col); objs.append(o); fd['door'].append(o)
    # 设备：4 台 8U 服务器 + 盲板 + 柜顶 2 台 1U 交换机
    for k in range(4):
        mode = 'inst' if not hero else ('lid' if k == K_HERO else 'all' if k == K_HERO + 1 else 'inst')
        f = place_server(col, k, mode, parent); fd['lid' if k == K_HERO else 'upper'] += f
    b = C.Mesh(); bz = [0.10 + U / 2, 0.10 + 1.5 * U] + [SRV_Z[k] + 8 * U + U / 2 for k in range(4)] + [0.10 + (39 + j) * U + U / 2 for j in (0,)]
    for z in bz:
        if hero and abs(z - (SRV_Z[K_HERO] + 8.5 * U)) < 1e-6: continue
        b.box((0.4826, 0.003, U - 0.001), (0, SRV_Y + 0.0015, z))
    objs.append(b.obj('盲板', M['blank'], col))
    if hero:
        o = C.box('盲板_淡出', (0.4826, 0.003, U - 0.001), (0, SRV_Y + 0.0015, SRV_Z[K_HERO] + 8.5 * U), MF('blank'), col); objs.append(o); fd['upper'].append(o)
    pm = C.Mesh(); pz = 0.10 + 38 * U + U / 2                    # 理线架（1U）：横梁 + 一排理线环
    pm.box((0.4826, 0.003, U - 0.001), (0, SRV_Y + 0.0015, pz))
    for j in range(12): pm.box((0.004, 0.045, 0.030), (-0.20 + j * 0.036, SRV_Y - 0.022, pz))
    objs.append(pm.obj('理线架', M['blank'], col))
    for j in (40, 41): objs.append(C.instance_collection(SWT, f'交换机U{j + 1}', (0, SRV_Y, 0.10 + j * U), col=col))
    # 黄色跳线：每台服务器 2 根、交换机若干根，汇到右侧理线区向上出柜
    lines = []; lines_up = []; lane = 0
    for k in range(4):
        for j in (0, PORT_HERO): (lines_up if hero and k == K_HERO + 1 else lines).append(jumper_route(PORT_X[j], SRV_Z[k] + PORT_Z, lane)); lane += 1
    for j in (1, 4, 7, 10, 13):
        lines.append(jumper_route(-0.185 + j * 0.0215, 0.10 + 41 * U + 0.030, lane, tail=0.3)); lane += 1
        r = jumper_route(-0.185 + j * 0.0215, 0.10 + 40 * U + 0.030, lane, tail=0.3); lane += 1; lines.append(r)
    objs.append(tubes('跳线', lines, 0.0016, M['yellow'], col, res=1))
    if lines_up: o = tubes('跳线_淡出', lines_up, 0.0016, MF('yellow'), col, res=1); objs.append(o); fd['upper'].append(o)     # 上方服务器淡出时，它的跳线一起淡出
    # 柜内一点暖光（柜门和设备之间，从上往下擦着前面板）
    ld = bpy.data.lights.new('柜内暖光', 'AREA'); ld.energy = 6.0; ld.color = (1.0, 0.66, 0.38); ld.shape = 'RECTANGLE'; ld.size = 0.42; ld.size_y = 0.03
    lo = C.link(bpy.data.objects.new('柜内暖光', ld), col); lo.location = (0, 0.05, 2.02); lo.visible_camera = False; objs.append(lo)
    if parent:
        for o in objs:
            if o.parent is None: o.parent = parent
    return fd

RACK = C.collection('SRC_机柜'); assemble_rack(RACK)
racks = C.collection('机柜')
hero = C.empty('机柜A', (xc(I_A), 0.6, 0), racks); FD = assemble_rack(racks, hero=True, parent=hero)
C.instance_collection(INTL, 'A内部', (0, SRV_Y, SRV_Z[K_HERO]), col=racks).parent = hero
for i in range(N0, N1 + 1):
    if i != I_A: C.instance_collection(RACK, f'A{i}', (xc(i), 0.6, 0), col=racks)
    C.instance_collection(RACK, f'B{i}', (xc(i), -0.6, 0), rot=(0, 0, PI), col=racks)
C.instance_collection(INTL, 'B内部', to_world('B', I_B, (0, SRV_Y, SRV_Z[K_HERO])), rot=(0, 0, PI), col=racks)
for c in (SRV, INTL, SWT, RACK): C.hide_collection(c)

# ---------- 机房：地板、顶、尽头的门、线槽、跳线束、灯带 ----------
room = C.collection('机房')
X0, X1 = xc(N0) - 0.3, xc(N1) + 0.3                    # 机柜排的两端
C.box('地板', (X1 - X0 + 6, 9.6, 0.04), ((X0 + X1) / 2, 0, -0.02), M['floor'], room)
C.box('顶', (X1 - X0 + 6, 9.6, 0.1), ((X0 + X1) / 2, 0, CEIL_Z + 0.05), M['ceil'], room)
w = C.Mesh()
for x in (X0 - 1.6, X1 + 1.2): w.box((0.1, 9.6, CEIL_Z), (x, 0, CEIL_Z / 2))
for s in (-1, 1): w.box((X1 - X0 + 6, 0.1, CEIL_Z), ((X0 + X1) / 2, s * 4.8, CEIL_Z / 2))
w.obj('墙', M['wall'], room)
dm = C.Mesh(); gl = C.Mesh(); xd = X1 + 0.02                # 通道尽头的封闭门：门框 + 两扇带玻璃的门
dm.box((0.06, 1.2, 0.12), (xd, 0, 2.16)); dm.box((0.04, 1.2, 0.5), (xd, 0, 0.25)); dm.box((0.05, 0.05, 2.1), (xd, 0, 1.05))
for s in (-1, 1): dm.box((0.05, 0.06, 2.1), (xd, s * 0.57, 1.05)); dm.box((0.04, 0.52, 0.5), (xd, s * 0.285, 1.85)); gl.box((0.01, 0.50, 1.10), (xd, s * 0.285, 1.05))
dm.obj('通道门', M['rack'], room); gl.obj('通道门玻璃', M['glass'], room)

def build_tray(m, a, b, width):
    """网格桥架：沿 a → b（平行于 X 或 Y）的一段。纵丝 + 每 100 mm 一道 U 形横丝，钢丝 5 mm"""
    a = V(a); b = V(b); d = b - a; L = d.length; ax = 0 if abs(d.x) > abs(d.y) else 1; wd = 0.005
    def P(s, t, z): return (a.x + s, a.y + t, z) if ax == 0 else (a.x + t, a.y + s, z)
    def S(ls, lt, lz): return (ls, lt, lz) if ax == 0 else (lt, ls, lz)
    sg = 1 if d[ax] > 0 else -1
    for t in [(k / 4 - 0.5) * width for k in range(5)]: m.box(S(L, wd, wd), P(sg * L / 2, t, TRAY_Z))
    for t in (-width / 2, width / 2):
        for z in (TRAY_Z + 0.04, TRAY_Z + 0.08): m.box(S(L, wd, wd), P(sg * L / 2, t, z))
    for k in range(int(L / 0.1) + 1):
        s = sg * k * 0.1; m.box(S(wd, width, wd), P(s, 0, TRAY_Z))
        for t in (-width / 2, width / 2): m.box(S(wd, wd, 0.08), P(s, t, TRAY_Z + 0.04))
tr = C.Mesh(); hg = C.Mesh()
for s in (-1, 1):
    build_tray(tr, (X0, s * 0.75, 0), (X1, s * 0.75, 0), TRAY_W)
    for k in range(int((X1 - X0) / 1.2) + 1):              # 吊杆 + 托臂
        x = X0 + 0.3 + k * 1.2; hg.box((0.03, TRAY_W + 0.08, 0.03), (x, s * 0.75, TRAY_Z - 0.02))
        for t in (-1, 1): hg.cyl(0.005, CEIL_Z - TRAY_Z + 0.02, (x, s * 0.75 + t * (TRAY_W / 2 + 0.03), (CEIL_Z + TRAY_Z - 0.02) / 2), seg=6)
for x in CROSS: build_tray(tr, (x, -0.6, 0), (x, 0.6, 0), TRAY_W)
tr.obj('线槽', M['tray'], room); hg.obj('吊杆', M['tray'], room)

def wavy(a, b, n, amp, z_amp=0.004):
    a = V(a); b = V(b); d = (b - a).normalized(); side = V((-d.y, d.x, 0)); out = []
    for k in range(n + 1):
        p = a.lerp(b, k / n) + side * random.uniform(-amp, amp) + V((0, 0, random.uniform(0, z_amp))); out.append(p)
    return out
bund = []; bund2 = []
for s in (-1, 1):
    for j in range(5): bund.append((wavy((X0, s * (0.70 + j * 0.036), TRAY_Z + 0.022), (X1, s * (0.70 + j * 0.036), TRAY_Z + 0.022), 40, 0.006), random.uniform(5.5, 8.0)))
    for j in range(14):
        y = s * random.uniform(0.67, 0.88); (bund if j % 3 else bund2).append((wavy((X0, y, TRAY_Z + 0.046), (X1, y, TRAY_Z + 0.046), 46, 0.018, 0.012), 1.0))
for x in CROSS:
    for j in range(3): bund.append((wavy((x - 0.02 + j * 0.05, -0.74, TRAY_Z + 0.02), (x - 0.02 + j * 0.05, 0.74, TRAY_Z + 0.02), 8, 0.006), random.uniform(4.5, 6.5)))
    for j in range(5): xx = x + random.uniform(-0.06, 0.11); bund2.append((wavy((xx, -0.72, TRAY_Z + 0.042), (xx, 0.72, TRAY_Z + 0.042), 8, 0.012, 0.01), 1.0))
tubes('线槽跳线束', bund, 0.0026, M['yellow'], room, nurbs=True, res=2); tubes('线槽跳线束2', bund2, 0.0026, M['yellow2'], room, nurbs=True, res=1)

lb = C.Mesh(); lf = C.Mesh(); LIGHT_X = [X0 + 0.9 + k * 1.2 for k in range(int((X1 - X0) / 1.2))]
for x in LIGHT_X:                                          # 顶部灯带：横跨通道，每 1.2 m 一条
    lb.box((0.07, 1.00, 0.012), (x, 0, 2.760)); lf.box((0.10, 1.06, 0.05), (x, 0, 2.792))
    for t in (-0.45, 0.45): lf.cyl(0.004, CEIL_Z - 2.81, (x, t, (CEIL_Z + 2.81) / 2), seg=6)
lb.obj('灯带', M['lightbar'], room); lf.obj('灯具', M['rack'], room)

# ---------- 路径线：金 → 青 → 金（视觉隐喻，贴着真实走线） ----------
def gold_route():
    """机箱坐标：GPU A 模组前沿 → 底板前沿 → 沿前沿横到光口那一列 → 风扇墙后面向下 → 光口（模组尾端）"""
    gx = COLS[1]; px = PORT_X[PORT_HERO]
    return fillet([(gx, ROW_Y[0] - 0.052, ZM + 0.011), (gx, ROW_Y[0] - 0.110, ZM + 0.011), (gx, ROW_Y[0] - 0.110, ZB + 0.004), (gx, 0.082, ZB + 0.004),
                   (px, 0.082, ZB + 0.004), (px, 0.070, ZB + 0.004), (px, 0.070, PORT_Z), (px, -0.020, PORT_Z)], 0.008)
pa = [to_world('A', I_A, srv_to_rack(p)) for p in gold_route()]
pb = [to_world('B', I_B, srv_to_rack(p)) for p in reversed(gold_route())]
ra = [to_world('A', I_A, p) for p in hero_route()]; rb = [to_world('B', I_B, p) for p in reversed(hero_route())]
zt = ra[-1].z; ya = ra[-1].y; yb = rb[0].y; xk = X_CROSS - 0.10
tray_run = fillet([ra[-1], (xk, ya, zt), (xk, yb, zt), rb[0]], 0.06, n=6)
pc = ra[:-1] + tray_run + rb[1:]
segs = [('路径_金A', pa, 0.0020, 'path_gold'), ('路径_青', pc, 0.0100, 'path_cyan'), ('路径_金B', pb, 0.0020, 'path_gold')]
L_TOTAL = sum(plen(p) for _, p, _, _ in segs); T_P0, T_P1 = 1.5, 7.5; s0 = 0.0; PATH_T = {}
for name, pts, r, key in segs:
    rf = 1.0
    if key == 'path_gold':                                 # 金色段：靠近 GPU 的一头细（特写里不抢画面），往光口方向渐粗（中景里看得见）
        d = [0.0]
        for a, b in zip(pts, pts[1:]): d.append(d[-1] + (V(b) - V(a)).length)
        if name.endswith('B'): d = [d[-1] - x for x in d]
        rf = [C.lerp(1.0, 2.0, C.smooth(C.seg(x, 0.06, 0.22))) for x in d]
    o = tubes(name, [(pts, rf)], r, M[key], None, res=3); cu = o.data; L = plen(pts)
    ta = C.lerp(T_P0, T_P1, s0 / L_TOTAL); tb = C.lerp(T_P0, T_P1, (s0 + L) / L_TOTAL); s0 += L; PATH_T[name] = (round(ta, 2), round(tb, 2), round(L, 3))
    cu.bevel_factor_end = 0.0; cu.keyframe_insert('bevel_factor_end', frame=C.F(ta)); cu.bevel_factor_end = 1.0; cu.keyframe_insert('bevel_factor_end', frame=C.F(tb)); C.set_interp(cu, 'LINEAR')
    o.hide_render = True; o.keyframe_insert('hide_render', frame=shot.f0); o.hide_render = False; o.keyframe_insert('hide_render', frame=C.F(ta) + 1)
# 线槽里那一段的中点（过桥正中附近）
acc = 0.0; half = plen(tray_run) / 2; PATH_MID = V(tray_run[0])
for a, b in zip(tray_run, tray_run[1:]):
    d = (V(b) - V(a)).length
    if acc + d >= half: PATH_MID = V(a).lerp(V(b), (half - acc) / d); break
    acc += d

# ---------- 淡出：柜门 → 上方那台服务器和盲板 → 上盖 ----------
def fade_out(objs, t0, t1):
    for o in objs:
        C.key_fade(o, [(shot.t0, 1), (t0, 1), (t1, 0)])
        o.hide_render = False; o.keyframe_insert('hide_render', frame=C.F(t1) - 1); o.hide_render = True; o.keyframe_insert('hide_render', frame=C.F(t1))
fade_out(FD['door'], 9.5, 10.0); fade_out(FD['upper'], 9.5, 10.2); fade_out(FD['lid'], 9.7, 10.45)

# ---------- 相机 ----------
E = G_A + CAM_END_OFFSET; UDIR = CAM_END_OFFSET.normalized(); D_END = CAM_END_OFFSET.length
KEYS = [(0.0, V((-0.30, 0, 1.32))), (3.5, V((0.30, 0, 1.32))), (7.0, V((0.90, 0, 1.32))), (9.5, V((xc(I_A) - 0.34, -0.40, 1.40))), (11.0, V((xc(I_A) - 0.19, 0.25, 1.41))),
        (12.0, G_A + UDIR * 0.52), (12.5, G_A + UDIR * 0.41), (13.0, E)]
def cam_pos(t):
    """分段三次埃尔米特样条（切线取相邻关键点的差分）：速度连续，不在关键点上停顿。末端切线 = 沿入射方向、速度 V_END"""
    n = len(KEYS); t = max(KEYS[0][0], min(KEYS[-1][0], t))
    def tan(i):
        if i == n - 1: return -UDIR * V_END
        if i == 0: return (KEYS[1][1] - KEYS[0][1]) / (KEYS[1][0] - KEYS[0][0])
        return (KEYS[i + 1][1] - KEYS[i - 1][1]) / (KEYS[i + 1][0] - KEYS[i - 1][0])
    i = max(k for k in range(n - 1) if KEYS[k][0] <= t); (t0, p0), (t1, p1) = KEYS[i], KEYS[i + 1]; h = t1 - t0; s = (t - t0) / h
    return (2 * s ** 3 - 3 * s ** 2 + 1) * p0 + (s ** 3 - 2 * s ** 2 + s) * h * tan(i) + (-2 * s ** 3 + 3 * s ** 2) * p1 + (s ** 3 - s ** 2) * h * tan(i + 1)
def piece(t, pts):
    for (ta, va), (tb, vb) in zip(pts, pts[1:]):
        if t <= tb: return C.lerp(va, vb, C.smooth(C.seg(t, ta, tb)))
    return pts[-1][1]
def cam_fn(t):
    p = cam_pos(t); far = V((p.x + 9.0, p.y, 0.25))
    tg = far.lerp(G_A, C.smoother(C.seg(t, 7.0, 9.6)))
    return dict(loc=p, tgt=tg, lens=C.loglerp(24, 50, C.smooth(C.seg(t, 9.8, 13.0))), fstop=piece(t, [(0, 8.0), (7.0, 8.0), (9.5, 2.8), (11.5, 2.8), (13.0, 6.3)]))
cam, tgt = C.add_camera('cam_S01', lens=24, fstop=8.0, clip=(0.01, 200))
C.animate_camera(cam, tgt, cam_fn, shot)

# ---------- 灯光 ----------
C.world(FOG, 1.0, hdri='studio_small_09_2k.hdr', hdri_strength=0.14, hdri_rot=rad(90))
lights = C.collection('灯光')
def no_cam(o): o.visible_camera = False; return o
for x in LIGHT_X[::2]: no_cam(C.area_light(f'顶灯{x:.1f}', (x, 0, 2.74), (x, 0, 0), 0.9, 34, (0.64, 0.82, 1.0), size_y=0.25, col=lights))
no_cam(C.area_light('逆光', (X1 - 0.4, 0, 2.55), (X1 - 4.5, 0, 0.6), 1.4, 120, (0.64, 0.82, 1.0), size_y=0.6, col=lights))
# 转向 A 柜时的正面补光（冷白，从通道一侧照向柜面）；7 s 前关着，走廊全景不受影响
o = no_cam(C.area_light('A柜正面补光', (xc(I_A) - 0.5, -0.50, 1.75), G_A, 0.8, 30, (0.70, 0.85, 1.0), col=lights)); ld = o.data
for t, e in ((shot.t0, 0.0), (7.0, 0.0), (9.3, 30.0)): ld.energy = e; ld.keyframe_insert('energy', frame=C.F(t))
C.set_interp(ld, 'LINEAR')
# 上盖淡出后给机箱里补的光：暖色逆光（从后上方）+ 冷色正面补光；9.5 s 前关着
for name, off, power, color, size in (('箱内暖逆光', (-0.10, 0.34, 0.30), 6, (1.0, 0.78, 0.55), 0.30), ('箱内冷补光', (0.16, -0.30, 0.34), 1.5, (0.62, 0.78, 1.0), 0.30)):
    o = no_cam(C.area_light(name, G_A + V(off), G_A, size, power, color, col=lights)); ld = o.data
    for t, e in ((shot.t0, 0.0), (9.5, 0.0), (10.45, power)): ld.energy = e; ld.keyframe_insert('energy', frame=C.F(t))
    C.set_interp(ld, 'LINEAR')

# ---------- 远处渐隐（v0 的替身：按相机距离把材质混向雾色；正式制作换体积雾或合成里的深度雾） ----------
def add_fog(m, d0=3.5, scale=8.0):
    nt = m.node_tree; N = nt.nodes; L = nt.links; out = next((n for n in N if n.type == 'OUTPUT_MATERIAL'), None)
    if not out or not out.inputs['Surface'].is_linked: return
    src = out.inputs['Surface'].links[0].from_socket; t = NT(m); cd = N.new('ShaderNodeCameraData')
    x = t.m('MAXIMUM', t.m('DIVIDE', t.m('SUBTRACT', cd.outputs['View Distance'], d0), scale), 0.0)
    fac = t.m('SUBTRACT', 1.0, t.m('POWER', 2.718281828, t.m('MULTIPLY', x, -1.0)))
    em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*FOG, 1); mx = N.new('ShaderNodeMixShader')
    L.new(fac, mx.inputs[0]); L.new(src, mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs['Surface'])
for key, m in M.items():
    if not key.endswith('_fade') and not key.startswith('path_'): add_fog(m)

# ---------- 渲染 ----------
dev = C.setup_render(args, exposure=0.0)
sc.cycles.transparent_max_bounces = 64                  # 淡出中的物体层数多（风扇格栅、叶片、面板……），16 层不够会出黑块
ANCHORS = {'gpu_a': G_A, 'gpu_b': G_B, 'rack_a': to_world('A', I_A, (0, 0, 1.05)), 'rack_b': to_world('B', I_B, (0, 0, 1.05)), 'path_mid': PATH_MID,
           'aisle_floor': V((KEYS[0][1].x + 3.0, 0, 0)), 'port_a': pa[-1], 'port_b': pb[0], 'server_a': to_world('A', I_A, srv_to_rack((0, 0, SH / 2)))}
print('G_A', tuple(round(v, 4) for v in G_A), '| G_B', tuple(round(v, 4) for v in G_B), '| CAM_END', tuple(round(v, 4) for v in cam_fn(13.0)['loc']), '| E', tuple(round(v, 4) for v in E))
for t in (12.0, 12.5, 12.9, 12.99):
    vel = (cam_pos(t + 0.005) - cam_pos(t - 0.005)) / 0.01; print(f'CAM t={t} 速度 {vel.length:.3f} m/s，与入射方向夹角 {math.degrees(vel.angle(-UDIR)):.1f}°，到 G 距离 {(cam_pos(t) - G_A).length:.3f}')
print('CAM 每秒速度 (m/s):', ' '.join(f'{t}s={((cam_pos(t + 0.01) - cam_pos(t - 0.01)) / 0.02).length:.2f}' for t in range(1, 13)))
print('PATH', PATH_T, '| 总长', round(L_TOTAL, 2), '| path_mid', tuple(round(v, 3) for v in PATH_MID))
print('BUILD_SEC', round(time.time() - T_BUILD, 2), '| 物体数', len(bpy.data.objects))
if args.anchors:
    os.makedirs(args.out, exist_ok=True); C.export_anchors(os.path.join(args.out, f'anchors_{shot.id}.json'), shot, cam, ANCHORS)
C.render(args, shot, dev)
