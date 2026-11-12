# S01 数据中心 → 机柜 → 服务器（0–13 秒）。单位：1 = 1 m。
# 状态：v1 粗模（Animatic 和构图检查用）。机柜、服务器面板和内部布局都是示例结构，只按「主流风冷 8-GPU 机型」的大致分区摆放，
#       不对应具体机型；不能当最终科学结构交付。「光口在机箱后部」是推荐方案，用户还没确认：相关尺寸集中在下面「后部光口」几行，方便替换。
# 坐标：冷通道沿 +X，中心线 y = 0，宽 1.2 m。A 排在 +Y（正面 y = +0.6），B 排在 −Y（正面 y = −0.6，整柜绕 Z 转 180°）。
#       机柜 i 的中心 x = 0.3 + 0.6 i（i = −3 … 17，每排 21 个）。GPU A 在 A 排 i = 4 的第 2 台服务器（自下往上数），GPU B 在 B 排 i = 8 的同一层。
# 机箱分区（机箱坐标，+Y 朝机箱后方）：前 = 风扇墙；中上 = GPU 托盘（8 个模组，4 列 × 2 排）；后段 = 主板（处理器散热器、内存）、电源、平放的网卡和后面板光口。
# 镜头：一个连续镜头，第 0 帧就在动。0–4.5 s 在高机位（约 2 m）沿通道前推（约 0.4 m/s），越过柜顶能看到背面上方的线槽；4.5–7 s 转向 A 柜；
#       7–8.5 s 柜门、GPU A 那台服务器上方的全部设备、上盖淡出；8.5–13 s 从上方压到 GPU A，13.0 s 机位 = G + CAM_END_OFFSET（S02 首帧）。
# 路径线（视觉隐喻，0.3–3.0 s 匀速画出，之后保持）：
#       金（电）A：GPU A 封装 +Y 边 → 模组小板 → 底板（两排模组之间横移到列间通道）→ 主板 → 网卡芯片 → 后面板光口；
#       青（光）：后面板光口 → 机柜背面向上 → 翻进柜顶背面上方的线槽 → 沿线槽 → 过桥 → B 排线槽 → B 柜背面向下 → B 柜服务器后面板光口（全程贴着一根黄色跳线）；
#       金（电）B：和 A 段镜像。
# 运行：blender -b --python-exit-code 1 --python s01_datacenter.py -- <输出目录> [--times 0.1,1.5,3,5.5,8,10.5,12,12.97] [--res 270x480] [--samples 16] [--anchors] [--no-render]
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
ZM = 0.2724                             # 模组小电路板顶面（机箱内，示例：GPU 托盘在上层）
ZB = ZM - 0.004                         # GPU 底板 / 主板顶面：比模组小板顶面低 4 mm（和 S02 一致）
G_LOCAL = V((COLS[1], ROW_Y[0], ZM + 0.00253))       # GPU A 芯片顶面中心（机箱坐标；散热器底座底面在它上方 0.1 mm）
# --- 后部光口（推荐方案，待用户确认；要换回别的方案，改这几行和 gold_route() / jumper_route() 即可） ---
LANE_X = (COLS[0] + COLS[1]) / 2        # 路径线在底板上走的列间通道（第 1、2 列模组之间），也是网卡芯片和光口所在的 x
GAP_Y = (ROW_Y[0] + ROW_Y[1]) / 2       # 两排模组之间
ZC = ZB + 0.008                         # 网卡板顶面（平放在主板上方，示例）
NIC_Y = (0.792, 0.899); NIC_CX = LANE_X + 0.013; CHIP_Y = 0.822; CHIP = 0.025; CHIP_H = 0.003     # 网卡板前后沿、中心 x；网卡芯片位置、边长、高
PORT_X = [LANE_X, LANE_X + 0.026]; PORT_Z = ZC + 0.00625; PORT_HERO = 0             # 后面板 2 个光口（网卡上的两个笼子）；路径线走第 1 个
PORT_TIP = SD + 0.018                   # 光模块尾端（跳线插口）伸出后面板的位置
TRAY_Z = 2.40; TRAY_W = 0.30; TRAY_Y = 0.93     # 线槽底面高度、宽度；线槽在机柜背面上方（柜内坐标 y = 0.78 … 1.08，世界坐标 y = ±1.38 … ±1.68）
X_CROSS = 3.9                           # 路径线过桥（跨通道的线槽）的位置
CROSS = (0.3, 3.9, 7.5)
CEIL_Z = 3.2
FOG = (0.034, 0.062, 0.105)             # 远处的雾色（也是相机直接看到的背景色）
CAM_END_OFFSET = V((-0.0795, -0.1967, 0.2528))      # 13.0 s 相机相对 G（芯片顶面中心）的位置 = S02 首帧：330 mm，俯角 50°，方位 −112°
V_END = 0.08                            # 13.0 s 时沿入射方向的速度（m/s）；S02 目前从静止起步，见报告

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
mk('led', C.emit, color=(0.10, 1.0, 0.22), strength=9.0, aov=False)            # 指示灯：绿色（金 / 青只给路径线）
mk('yellow', C.pbr, color=(0.78, 0.88, 0.07), rough=0.48)                      # 单模跳线的黄色护套：偏柠檬黄、不发光，和「金 = 电」分开
mk('yellow2', C.pbr, color=(0.62, 0.72, 0.09), rough=0.55)
mk('tray', C.pbr, color=(0.62, 0.63, 0.65), metallic=1.0, rough=0.38)
mk('ceil', C.pbr, color=(0.10, 0.105, 0.115), rough=0.8)
mk('wall', C.pbr, color=(0.30, 0.32, 0.35), rough=0.7)
mk('glass', C.emit, color=(0.62, 0.80, 1.0), strength=1.6, aov=False)          # 通道尽头门上的玻璃（门外的光）
mk('lightbar', C.emit, color=(0.74, 0.87, 1.0), strength=9.0, aov=False)      # 顶部灯带：冷白
mk('pcb', C.pbr, color=(0.007, 0.036, 0.027), rough=0.40, coat=0.4)             # 电路板：素的深绿阻焊色，不画走线纹
mk('mlcc', C.pbr, color=(0.50, 0.38, 0.25), rough=0.55)
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
    g['black'].box((0.080, 0.001, 0.034), (0.110, -0.0021, 0.054))                                      # 前面板不放光口：这里是进风栅（v1：光口改到后面板）
    for k in range(4): g['panel'].box((0.080, 0.003, 0.0030), (0.110, -0.0030, 0.042 + k * 0.008))
    for px in (0.060, 0.080): g['silver'].box((0.0165, 0.0015, 0.0135), (px, -0.0026, 0.022)); g['black'].box((0.0140, 0.0012, 0.0100), (px, -0.0036, 0.0215))
    for pz in (0.017, 0.027): g['black'].box((0.0130, 0.0012, 0.0055), (0.106, -0.0026, pz))
    g['silver'].cyl(0.0045, 0.003, (0.200, -0.0035, 0.072), rot=(PI / 2, 0, 0), seg=12)
    for k in range(3): g['led'].box((0.0025, 0.001, 0.0025), (0.170 + k * 0.008, -0.0026, 0.072))
    g['label'].box((0.034, 0.0006, 0.009), (0.165, -0.0024, 0.020))
    for px in PORT_X:                                   # 后面板光口：笼子口 + 插着的光模块尾端（跳线从这里出去）
        g['silver'].box((0.0215, 0.0030, 0.0125), (px, SD + 0.0015, PORT_Z)); g['silver'].box((0.0183, 0.016, 0.0085), (px, SD + 0.009, PORT_Z))
        g['led'].box((0.002, 0.001, 0.002), (px - 0.006, SD + 0.0012, PORT_Z + 0.0095))
    finish(g, col, '服务器'); return col

# ---------- 服务器内部（实例源，只放在 A、B 两台里）：示例布局，按参考机型的大致分区 ----------
# 前：风扇墙（在服务器外壳那个集合里）；中上：GPU 托盘，8 个模组 4 列 × 2 排；后段：主板（处理器散热器、内存）、电源、平放的网卡和后面板光口。
# 模组上的器件尺寸和排布照 S02（散热器 96 × 96 底座 + 47 片鳍片、7 个电感、9 个铝壳电容、成排贴片电容），13.0 s 接缝两边才对得上。
def build_internals():
    col = C.collection('SRC_服务器内部')
    g = {k: C.Mesh() for k in ('steel', 'pcb', 'substrate', 'silicon', 'nickel', 'alu', 'ferrite', 'can', 'black', 'dimm', 'label', 'silver', 'mlcc')}
    g['steel'].box((SW - 0.004, SD - 0.066, 0.0015), (0, 0.066 + (SD - 0.066) / 2, ZB - 0.0038))        # 托盘钣金
    g['pcb'].box((0.432, 0.550, 0.003), (0, 0.345, ZB - 0.0015))                                          # GPU 底板
    for cx in COLS:
        for ry in ROW_Y:
            g['pcb'].box((0.102, 0.200, 0.0024), (cx, ry, ZM - 0.0012))                                   # 模组小电路板
            for sx in (-1, 1): g['black'].box((0.006, 0.150, 0.0016), (cx + sx * 0.040, ry, ZB + 0.0008)) # 板间连接器（示意）
            g['substrate'].box((0.072, 0.072, 0.0016), (cx, ry, ZM + 0.0008)); g['silicon'].box((0.026, 0.031, 0.00078), (cx, ry, ZM + 0.00214))
            g['nickel'].box((0.096, 0.096, 0.005), (cx, ry, ZM + 0.00263 + 0.0025))                       # 散热器底座
            for k in range(-23, 24): g['alu'].box((0.0005, 0.092, 0.040), (cx + k * 0.002, ry, ZM + 0.00763 + 0.020))   # 鳍片：面垂直于 X，风沿 Y 吹
            for sy in (-1, 1):                                                                            # 供电：电感、供电芯片、铝壳电容、两排贴片电容
                def free(x): return not (sy > 0 and abs(x) < 0.004)                                      # +Y 一侧正中让出约 8 mm，给路径线走（示意；S02 的这一侧在接缝帧被散热器挡住）
                for k in range(-3, 4):
                    if free(k * 0.0122): g['ferrite'].box((0.010, 0.010, 0.007), (cx + k * 0.0122, ry + sy * 0.062, ZM + 0.0035)); g['black'].box((0.005, 0.006, 0.0009), (cx + k * 0.0122, ry + sy * 0.0515, ZM + 0.00045))
                for k in range(-4, 5):
                    if free(k * 0.0096): g['can'].cyl(0.00315, 0.0075, (cx + k * 0.0096, ry + sy * 0.078, ZM + 0.00375), seg=10)
                for k in range(-19, 20):
                    for yy in (0.088, 0.091):
                        if free(k * 0.0025): g['mlcc'].box((0.0008, 0.0016, 0.0008), (cx + k * 0.0025, ry + sy * yy, ZM + 0.0004))
            for sx in (-1, 1):                                                                            # 封装两侧的贴片电容
                for k in range(-16, 17, 2):
                    for j in range(3): g['mlcc'].box((0.0016, 0.0008, 0.0008), (cx + sx * (0.042 + j * 0.0032), ry + k * 0.0022, ZM + 0.0004))
    # 后段：主板、2 个处理器散热器、内存条排、电源、网卡（都是示例）。第 1、2 列之间的通道（x = LANE_X）一直通到网卡，不放东西
    g['pcb'].box((0.432, 0.268, 0.003), (0, 0.765, ZB - 0.0015))
    for sx in (-1, 1):
        g['nickel'].box((0.090, 0.110, 0.005), (sx * 0.052, 0.715, ZB + 0.008))
        for k in range(-17, 18): g['alu'].box((0.0006, 0.108, 0.034), (sx * 0.052 + k * 0.0025, 0.715, ZB + 0.0105 + 0.017))
    for dx in [s * (0.130 + k * 0.0098) for s in (-1, 1) for k in range(8)]:
        g['black'].box((0.0060, 0.142, 0.006), (dx, 0.715, ZB + 0.003)); g['dimm'].box((0.0014, 0.1333, 0.031), (dx, 0.715, ZB + 0.006 + 0.0155))
        g['label'].box((0.0016, 0.050, 0.012), (dx, 0.705, ZB + 0.022))
        for sy in (-1, 1): g['label'].box((0.0050, 0.006, 0.012), (dx, 0.715 + sy * 0.071, ZB + 0.008))
    for k in range(4):                                                                                    # 电源：在后段 +X 一侧
        px = 0.002 + k * 0.060; g['steel'].box((0.055, 0.085, 0.041), (px, 0.853, ZB + 0.0205)); g['black'].box((0.040, 0.002, 0.030), (px, 0.8095, ZB + 0.0205))
    # 网卡：平放在后段 −X 一侧的一块小板，上面一颗芯片（示例；真实的网卡芯片上有散热片，这里省略），后沿两个光模块笼子伸到后面板
    g['pcb'].box((0.076, NIC_Y[1] - NIC_Y[0], 0.0016), (NIC_CX, (NIC_Y[0] + NIC_Y[1]) / 2, ZC - 0.0008))
    g['black'].box((0.060, 0.008, 0.0064), (NIC_CX, NIC_Y[0] + 0.010, ZB + 0.0032))                       # 板下的连接器
    g['substrate'].box((CHIP, CHIP, 0.0012), (LANE_X, CHIP_Y, ZC + 0.0006)); g['silver'].box((CHIP - 0.006, CHIP - 0.006, CHIP_H - 0.0012), (LANE_X, CHIP_Y, ZC + 0.0012 + (CHIP_H - 0.0012) / 2))
    for px in PORT_X: g['silver'].box((0.0205, 0.049, 0.0125), (px, SD - 0.0245, PORT_Z))                 # 光模块笼子
    for sx in (-1, 1): g['black'].box((0.010, 0.76, 0.010), (sx * 0.2165, 0.50, ZB + 0.005))             # 两侧的供电线束（示意）
    finish(g, col, '内部', bevel={'nickel': 0.0006, 'ferrite': 0.0008}); return col

# ---------- 1U 交换机（实例源）：原点在端口面底边中点。v1：端口面朝机柜背面（和服务器后部光口同侧），在机柜里转 180° 放 ----------
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

# ---------- 机柜里的跳线走法（柜内坐标）：后面板光口 → 机柜背面的理线区 → 向上出柜顶 → 翻过线槽边沿 → 落到线槽里 ----------
RISER_X = 0.250; Y_REAR = SRV_Y + PORT_TIP              # 竖向理线的位置；光模块尾端在柜内的进深
def jumper_route(px, z, lane, tail=0.35):
    y = 1.095 + lane * 0.003; yt = TRAY_Y - 0.13 + lane * 0.004         # 竖向这一段的进深；落进线槽后的位置（靠通道一侧）
    pts = [(px, Y_REAR, z), (px, y, z), (RISER_X, y, z), (RISER_X, y, 2.17), (RISER_X, 1.16, 2.25), (RISER_X, 1.16, TRAY_Z + 0.105),
           (RISER_X, yt, TRAY_Z + 0.105), (RISER_X, yt, TRAY_Z + 0.008)]
    if tail: pts.append((RISER_X + tail, yt + 0.010, TRAY_Z + 0.008))
    return fillet(pts, 0.022)
LANE_HERO = 2 * K_HERO + PORT_HERO
def hero_route(): return jumper_route(PORT_X[PORT_HERO], SRV_Z[K_HERO] + PORT_Z, LANE_HERO, tail=0)

def place_parts(src, name, loc, col, parent=None, rot=(0, 0, 0)):
    """把一个实例源集合拆成逐个物体的实例，全部换成可淡出材质。返回这些物体"""
    out = []
    for s in src.objects:
        o = C.instance(s, f'{name}_{s.name}', loc, rot=rot, col=col); o.parent = parent
        o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = MF(s['mkey']); out.append(o)
    return out

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
    """一个机柜（柜内坐标：x ∈ ±0.3，y = 0 是柜门外表面，往 +y 是柜深）。
    hero=True 时返回要淡出的物体：柜门、GPU A 那台服务器上方的全部设备（服务器、盲板、交换机和它们的跳线）、上盖；以及柜内暖光的灯。"""
    fd = {'door': [], 'upper': [], 'lid': [], 'light': None}; objs = []
    g = {k: C.Mesh() for k in ('rack', 'rail')}
    g['rack'].box((RACK_W, RACK_D, 0.06), (0, RACK_D / 2, 0.03))
    for s in (-1, 1):
        g['rack'].box((0.028, 0.040, RACK_H - 0.06), (s * 0.286, 0.045, RACK_H / 2 + 0.03)); g['rack'].box((0.04, 0.04, RACK_H - 0.06), (s * 0.28, RACK_D - 0.02, RACK_H / 2 + 0.03))
        g['rack'].box((0.002, RACK_D - 0.03, RACK_H - 0.08), (s * 0.299, RACK_D / 2 + 0.015, RACK_H / 2 + 0.03))
        g['rail'].box((0.030, 0.003, 1.90), (s * 0.2405, SRV_Y + 0.0035, 1.05))
    g['rack'].box((RACK_W, 1.08, 0.02), (0, 0.54, RACK_H - 0.01)); g['rack'].box((RACK_W, 0.03, 0.04), (0, 0.015, RACK_H - 0.02))     # 顶板：背面留 0.1 m 的出线口
    g['rack'].box((RACK_W, 0.02, 0.04), (0, RACK_D - 0.01, RACK_H - 0.02))
    g['rack'].box((RACK_W - 0.01, 0.01, RACK_H - 0.1), (0, RACK_D - 0.005, RACK_H / 2 + 0.02))
    objs += finish(g, col, '机柜')
    # 柜门：门框 + 冲孔网 + 把手
    d = C.Mesh()
    for s in (-1, 1): d.box((0.035, 0.02, 2.0), (s * 0.2825, 0.01, 1.06))
    for z in (0.0775, 2.0425): d.box((0.53, 0.02, 0.035), (0, 0.01, z))
    d.box((0.018, 0.012, 0.16), (-0.283, -0.006, 1.05))
    o = d.obj('柜门框', MF('rack') if hero else M['rack'], col); objs.append(o); fd['door'].append(o)
    o = C.box('柜门网', (0.53, 0.003, 1.93), (0, 0.010, 1.06), MF('door') if hero else M['door'], col); objs.append(o); fd['door'].append(o)
    # 设备：4 台 8U 服务器 + 盲板 + 柜顶 2 台 1U 交换机（端口面朝后，正面是盲板）
    for k in range(4):
        mode = 'inst' if not hero else ('lid' if k == K_HERO else 'all' if k > K_HERO else 'inst')
        f = place_server(col, k, mode, parent); fd['lid' if k == K_HERO else 'upper'] += f
    b = C.Mesh(); bu = C.Mesh(); z_up = SRV_Z[K_HERO] + 8 * U
    bz = [0.10 + U / 2, 0.10 + 1.5 * U] + [SRV_Z[k] + 8 * U + U / 2 for k in range(4)] + [0.10 + (38 + j) * U + U / 2 for j in range(4)]
    for z in bz: (bu if hero and z > z_up else b).box((0.4826, 0.003, U - 0.001), (0, SRV_Y + 0.0015, z))
    objs.append(b.obj('盲板', M['blank'], col))
    if hero: o = bu.obj('盲板_淡出', MF('blank'), col); objs.append(o); fd['upper'].append(o)
    else: bu.bm.free()
    for j in (40, 41):
        loc = (0, SRV_Y + SD, 0.10 + j * U)
        if hero: f = place_parts(SWT, f'交换机U{j + 1}', loc, col, parent, rot=(0, 0, PI)); fd['upper'] += f
        else: objs.append(C.instance_collection(SWT, f'交换机U{j + 1}', loc, rot=(0, 0, PI), col=col))
    # 黄色跳线：每台服务器 2 根、交换机若干根，在机柜背面汇到一侧向上出柜
    lines = []; lines_up = []; lane = 0
    for k in range(4):
        for j in range(2): (lines_up if hero and k > K_HERO else lines).append(jumper_route(PORT_X[j], SRV_Z[k] + PORT_Z, lane)); lane += 1
    for j in (1, 4, 7, 10, 13):
        for u in (41, 40): (lines_up if hero else lines).append(jumper_route(0.185 - j * 0.0215, 0.10 + u * U + 0.030, lane, tail=0.3)); lane += 1
    objs.append(tubes('跳线', lines, 0.0016, M['yellow'], col, res=1))
    if lines_up: o = tubes('跳线_淡出', lines_up, 0.0016, MF('yellow'), col, res=1); objs.append(o); fd['upper'].append(o)     # 上方设备淡出时，它们的跳线一起淡出
    # 柜内暖光（柜门和设备之间，从上往下擦着前面板）：给走廊画面一层暖色，和冷白的顶灯分开
    ld = bpy.data.lights.new('柜内暖光', 'AREA'); ld.energy = WARM_W; ld.color = (1.0, 0.60, 0.30); ld.shape = 'RECTANGLE'; ld.size = 0.42; ld.size_y = 0.03
    lo = C.link(bpy.data.objects.new('柜内暖光', ld), col); lo.location = (0, 0.05, 2.02); lo.visible_camera = False; objs.append(lo); fd['light'] = ld
    if parent:
        for o in objs:
            if o.parent is None: o.parent = parent
    return fd

WARM_W = 12.0
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
tr = C.Mesh(); hg = C.Mesh(); YT = 0.6 + TRAY_Y            # 线槽中心线（世界坐标 |y|）：在机柜背面上方
for s in (-1, 1):
    build_tray(tr, (X0, s * YT, 0), (X1, s * YT, 0), TRAY_W)
    for k in range(int((X1 - X0) / 1.2) + 1):              # 吊杆 + 托臂
        x = X0 + 0.3 + k * 1.2; hg.box((0.03, TRAY_W + 0.08, 0.03), (x, s * YT, TRAY_Z - 0.02))
        for t in (-1, 1): hg.cyl(0.005, CEIL_Z - TRAY_Z + 0.02, (x, s * YT + t * (TRAY_W / 2 + 0.03), (CEIL_Z + TRAY_Z - 0.02) / 2), seg=6)
for x in CROSS:                                            # 过桥：跨过两排机柜的柜顶和中间的通道
    build_tray(tr, (x, -YT - TRAY_W / 2, 0), (x, YT + TRAY_W / 2, 0), TRAY_W)
    for t in (-1, 1):
        for y in (-0.45, 0.45): hg.cyl(0.005, CEIL_Z - TRAY_Z + 0.02, (x + t * (TRAY_W / 2 + 0.01), y, (CEIL_Z + TRAY_Z - 0.02) / 2), seg=6)
tr.obj('线槽', M['tray'], room); hg.obj('吊杆', M['tray'], room)

def wavy(a, b, n, amp, z_amp=0.004):
    a = V(a); b = V(b); d = (b - a).normalized(); side = V((-d.y, d.x, 0)); out = []
    for k in range(n + 1):
        p = a.lerp(b, k / n) + side * random.uniform(-amp, amp) + V((0, 0, random.uniform(0, z_amp))); out.append(p)
    return out
bund = []; bund2 = []
for s in (-1, 1):                                          # 成捆的跳线放在线槽靠外的一侧；靠通道的一侧留给各柜上来的跳线（路径线走这一侧，从通道里看得见）
    for j in range(5): bund.append((wavy((X0, s * (YT - 0.03 + j * 0.036), TRAY_Z + 0.022), (X1, s * (YT - 0.03 + j * 0.036), TRAY_Z + 0.022), 40, 0.006), random.uniform(5.5, 8.0)))
    for j in range(14):
        y = s * random.uniform(YT - 0.06, YT + 0.13); (bund if j % 3 else bund2).append((wavy((X0, y, TRAY_Z + 0.046), (X1, y, TRAY_Z + 0.046), 46, 0.018, 0.012), 1.0))
for x in CROSS:
    for j in range(3): bund.append((wavy((x - 0.02 + j * 0.05, -YT - 0.10, TRAY_Z + 0.02), (x - 0.02 + j * 0.05, YT + 0.10, TRAY_Z + 0.02), 14, 0.006), random.uniform(4.5, 6.5)))
    for j in range(5): xx = x + random.uniform(-0.06, 0.11); bund2.append((wavy((xx, -YT - 0.08, TRAY_Z + 0.042), (xx, YT + 0.08, TRAY_Z + 0.042), 14, 0.012, 0.01), 1.0))
tubes('线槽跳线束', bund, 0.0026, M['yellow'], room, nurbs=True, res=2); tubes('线槽跳线束2', bund2, 0.0026, M['yellow2'], room, nurbs=True, res=1)

lb = C.Mesh(); lf = C.Mesh(); LIGHT_X = [X0 + 0.9 + k * 1.2 for k in range(int((X1 - X0) / 1.2))]
for x in LIGHT_X:                                          # 顶部灯带：横跨通道，每 1.2 m 一条
    lb.box((0.07, 1.00, 0.012), (x, 0, 2.760)); lf.box((0.10, 1.06, 0.05), (x, 0, 2.792))
    for t in (-0.45, 0.45): lf.cyl(0.004, CEIL_Z - 2.81, (x, t, (CEIL_Z + 2.81) / 2), seg=6)
lb.obj('灯带', M['lightbar'], room); lf.obj('灯具', M['rack'], room)

# ---------- 路径线：金 → 青 → 金（视觉隐喻，贴着真实走线） ----------
R_GOLD = 0.00125                                           # 金线半径：在模组小板上宽约 2.5 mm（示意，不是真实走线宽度），往后渐宽到约 4 mm
def gold_route():
    """机箱坐标，返回 (点列, 每点的半径倍数)。GPU A 封装 +Y 边 → 沿模组小板顶面到小板后沿 → 下到底板 → 在两排模组之间横移到列间通道
    → 沿通道向后，上主板 → 爬上网卡板 → 越过网卡芯片 → 笼子顶面 → 后面板光口（光模块尾端）。"""
    gx, gy = COLS[1], ROW_Y[0]; zt = ZM + 0.00053; zb = ZB + 0.0015; zc = ZC + 0.0016; zh = ZC + CHIP_H + 0.0016; zg = PORT_Z + 0.00625 + 0.0016
    y0 = NIC_Y[0] - 0.003; c0 = CHIP_Y - CHIP / 2 - 0.002; c1 = CHIP_Y + CHIP / 2 + 0.002; g0 = SD - 0.049 - 0.002
    pts = fillet([(gx, gy + 0.036, zt), (gx, gy + 0.100, zt), (gx, gy + 0.1035, zt), (gx, gy + 0.1035, zb), (gx, GAP_Y, zb), (LANE_X, GAP_Y, zb), (LANE_X, y0, zb), (LANE_X, y0, zc),
                  (LANE_X, c0, zc), (LANE_X, c0, zh), (LANE_X, c1, zh), (LANE_X, c1, zc), (LANE_X, g0, zc), (LANE_X, g0, zg), (LANE_X, SD + 0.001, zg), (LANE_X, PORT_TIP, PORT_Z)], 0.003, n=3)
    rf = [C.lerp(1.0, 1.2, C.smooth(C.seg(p.y, gy + 0.100, GAP_Y))) + 0.4 * C.smooth(C.seg(p.y, 0.60, 0.66)) for p in pts]
    return pts, rf
def resample(pts, n):
    """沿折线按弧长均匀取 n 个点（含两端）"""
    pts = [V(p) for p in pts]; d = [0.0]; out = []; j = 0
    for a, b in zip(pts, pts[1:]): d.append(d[-1] + (b - a).length)
    for k in range(n):
        x = d[-1] * k / (n - 1)
        while j < len(pts) - 2 and d[j + 1] < x: j += 1
        out.append(pts[j].lerp(pts[j + 1], (x - d[j]) / max(d[j + 1] - d[j], 1e-9)))
    return out
def taper(pts, r0, d1):
    """半径倍数：两端（光口附近）细，离开光口 d1 以后到 1"""
    d = [0.0]
    for a, b in zip(pts, pts[1:]): d.append(d[-1] + (V(b) - V(a)).length)
    return [C.lerp(r0, 1.0, C.smooth(C.seg(min(x, d[-1] - x), 0.03, d1))) for x in d]
gp, grf = gold_route()
pa = [to_world('A', I_A, srv_to_rack(p)) for p in gp]
pb = [to_world('B', I_B, srv_to_rack(p)) for p in reversed(gp)]
ra = [to_world('A', I_A, p) for p in hero_route()]; rb = [to_world('B', I_B, p) for p in reversed(hero_route())]
zt = ra[-1].z; ya = ra[-1].y; yb = rb[0].y; xk = X_CROSS - 0.10
tray_run = fillet([ra[-1], (xk, ya, zt), (xk, yb, zt), rb[0]], 0.06, n=6)
pc = ra[:-1] + tray_run + rb[1:]
tubes('路径下的跳线', [pc], 0.0016, M['yellow'], room, res=1)       # 青色管里面的那根真实跳线（从 A 柜光口一直到 B 柜光口）
NIC_A = to_world('A', I_A, srv_to_rack((LANE_X, CHIP_Y, ZC + CHIP_H))); NIC_B = to_world('B', I_B, srv_to_rack((LANE_X, CHIP_Y, ZC + CHIP_H)))
segs = [('路径_金A', 'e1', pa, R_GOLD, 'path_gold', grf), ('路径_青', 'o', pc, 0.0120, 'path_cyan', taper(pc, 0.3, 0.6)), ('路径_金B', 'e2', pb, R_GOLD, 'path_gold', grf[::-1])]
L_TOTAL = sum(plen(p) for _, _, p, _, _, _ in segs); T_P0, T_P1 = 0.3, 3.0; s0 = 0.0; PATH_T = {}
for name, tag, pts, r, key, rf in segs:
    o = tubes(name, [(pts, rf)], r, M[key], None, res=3); cu = o.data; L = plen(pts)
    ta = C.lerp(T_P0, T_P1, s0 / L_TOTAL); tb = C.lerp(T_P0, T_P1, (s0 + L) / L_TOTAL); s0 += L; PATH_T[name] = (round(ta, 2), round(tb, 2), round(L, 3))
    cu.bevel_factor_end = 0.0; cu.keyframe_insert('bevel_factor_end', frame=C.F(ta)); cu.bevel_factor_end = 1.0; cu.keyframe_insert('bevel_factor_end', frame=C.F(tb)); C.set_interp(cu, 'LINEAR')
    o.hide_render = True; o.keyframe_insert('hide_render', frame=shot.f0); o.hide_render = False; o.keyframe_insert('hide_render', frame=C.F(ta) + 1)
# 路径采样锚点：沿整条路线取 32 个点（三段按长度比例分，每段至少 3 个，含各段两端），Remotion 沿这些点画线
N_PATH = 32; PATH_N = [max(3, round(N_PATH * plen(sg[2]) / L_TOTAL)) for sg in segs]; PATH_N[1] += N_PATH - sum(PATH_N)
PATH_PTS = {f'path_{sg[1]}_{k:02d}': p for sg, n in zip(segs, PATH_N) for k, p in enumerate(resample(sg[2], n))}
# 线槽里那一段的中点（过桥正中附近）
acc = 0.0; half = plen(tray_run) / 2; PATH_MID = V(tray_run[0])
for a, b in zip(tray_run, tray_run[1:]):
    d = (V(b) - V(a)).length
    if acc + d >= half: PATH_MID = V(a).lerp(V(b), (half - acc) / d); break
    acc += d

# ---------- 淡出（7–8.5 s）：柜门 → GPU A 那台服务器上方的全部设备 → 上盖 ----------
def fade_out(objs, t0, t1):
    for o in objs:
        C.key_fade(o, [(shot.t0, 1), (t0, 1), (t1, 0)])
        o.hide_render = False; o.keyframe_insert('hide_render', frame=C.F(t1) - 1); o.hide_render = True; o.keyframe_insert('hide_render', frame=C.F(t1))
fade_out(FD['door'], 7.0, 7.6); fade_out(FD['upper'], 7.0, 8.1); fade_out(FD['lid'], 7.6, 8.5)

# ---------- 相机 ----------
E = G_A + CAM_END_OFFSET; UDIR = CAM_END_OFFSET.normalized(); D_END = CAM_END_OFFSET.length
XL = xc(I_A) + LANE_X                                   # 列间通道所在的竖直面：8.5–11 s 机位留在这个面里，才能从散热器之间看到底板上的金线
T_MID = to_world('A', I_A, srv_to_rack((-0.08, 0.47, ZM)))        # 机箱中部（转向 A 柜以后先看整台机箱）
CAM_Z0 = 2.0                                            # 走廊段的机位高度：高于人眼、低于柜顶线槽，越过柜顶能看到背面上方的线槽
KEYS = [(0.0, V((-0.30, 0, CAM_Z0))), (4.5, V((1.45, 0, CAM_Z0))), (7.0, V((2.36, -0.36, 1.80))), (8.5, V((XL, 0.40, 1.68))), (10.5, V((XL, 0.56, 1.42))),
        (12.0, G_A + UDIR * 0.50 + V((0.03, 0, 0))), (12.5, G_A + UDIR * 0.40), (13.0, E)]
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
    p = cam_pos(t); far = V((p.x + 9.0, p.y, 0.6))
    tg = far.lerp(T_MID, C.smoother(C.seg(t, 4.5, 7.2))).lerp(G_A, C.smoother(C.seg(t, 10.8, 12.7)))       # 12.7 s 以后朝向固定在 G_A（S02 开头也不动）
    return dict(loc=p, tgt=tg, lens=C.loglerp(24, 50, C.smooth(C.seg(t, 7.0, 13.0))),
                fstop=piece(t, [(0, 8.0), (4.5, 8.0), (7.5, 4.0), (11.0, 4.0), (13.0, 15.2)]))        # 13.0 s 的 f/15.2 = S02 首帧的光圈（S02 按 mm 建模，换算后孔径约 3.3 mm）
cam, tgt = C.add_camera('cam_S01', lens=24, fstop=8.0, clip=(0.01, 200))
C.animate_camera(cam, tgt, cam_fn, shot)

# ---------- 灯光 ----------
C.world(FOG, 1.0, hdri='studio_small_09_2k.hdr', hdri_strength=0.14, hdri_rot=rad(90))
lights = C.collection('灯光')
def no_cam(o): o.visible_camera = False; return o
def key_energy(ld, keys):
    for t, e in keys: ld.energy = e; ld.keyframe_insert('energy', frame=C.F(t))
    C.set_interp(ld, 'LINEAR')
T_L0, T_L1 = 11.0, 12.8                                 # 机箱内的光往 S02 首帧过渡的时间段
ROOM_END = 0.25                                         # 13.0 s 时机房顶灯剩下的比例（镜头已经在机箱里，机房不入画）
for x in LIGHT_X[::2]:
    o = no_cam(C.area_light(f'顶灯{x:.1f}', (x, 0, 2.74), (x, 0, 0), 0.9, 34, (0.64, 0.82, 1.0), size_y=0.25, col=lights))
    if abs(x - xc(I_A)) < 4.0: key_energy(o.data, [(shot.t0, 34), (T_L0, 34), (T_L1, 34 * ROOM_END)])
no_cam(C.area_light('逆光', (X1 - 0.4, 0, 2.55), (X1 - 4.5, 0, 0.6), 1.4, 120, (0.64, 0.82, 1.0), size_y=0.6, col=lights))
# 转向 A 柜时的正面补光（冷白，从通道一侧照向柜面）；4.5 s 前关着，走廊全景不受影响；最后 2 秒关掉
o = no_cam(C.area_light('A柜正面补光', (xc(I_A) - 0.5, -0.50, 1.95), G_A, 0.8, 30, (0.70, 0.85, 1.0), col=lights))
key_energy(o.data, [(shot.t0, 0.0), (4.5, 0.0), (6.8, 30.0), (T_L0, 30.0), (T_L1, 0.0)])
key_energy(FD['light'], [(shot.t0, WARM_W), (T_L0, WARM_W), (T_L1, 0.0)])                               # A 柜自己的柜内暖光：最后 2 秒关掉
# 机箱里的三盏灯：位置、颜色、大小照 S02（S02 单位是 mm，原点在 GPU A 模组小板顶面中心）；功率按 1 W ≈ S02 的 1e6 换算。
# 上盖淡出时亮起（先亮一些，中景看得清），11–12.8 s 过渡到 S02 首帧的强度
O_MOD = G_A - V((0, 0, 0.00253))
BOX_LIGHTS = (('箱内暖逆光', (-0.180, 0.260, 0.240), 0.26, (1.0, 0.82, 0.62), 6.0, 2.6), ('箱内冷补光', (0.240, -0.200, 0.160), 0.30, (0.62, 0.78, 1.0), 1.6, 0.7),
              ('箱内顶光', (0.0, -0.020, 0.320), 0.20, (1.0, 1.0, 1.0), 1.0, 0.4))
for name, off, size, color, e_mid, e_end in BOX_LIGHTS:
    o = no_cam(C.area_light(name, O_MOD + V(off), O_MOD, size, e_mid, color, col=lights))
    key_energy(o.data, [(shot.t0, 0.0), (7.6, 0.0), (8.5, e_mid), (T_L0, e_mid), (T_L1, e_end)])

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
ANCHORS = {'gpu_a': G_A, 'gpu_b': G_B, 'nic_a': NIC_A, 'nic_b': NIC_B, 'port_a': pa[-1], 'port_b': pb[0],
           'rack_a': to_world('A', I_A, (0, 0, 1.05)), 'rack_b': to_world('B', I_B, (0, 0, 1.05)), 'path_mid': PATH_MID,
           'aisle_floor': V((KEYS[0][1].x + 3.0, 0, 0)), 'server_a': to_world('A', I_A, srv_to_rack((0, 0, SH / 2)))}
ANCHORS.update(PATH_PTS)
print('G_A', tuple(round(v, 4) for v in G_A), '| G_B', tuple(round(v, 4) for v in G_B), '| CAM_END', tuple(round(v, 4) for v in cam_fn(13.0)['loc']), '| E', tuple(round(v, 4) for v in E))
for t in (12.0, 12.5, 12.9, 12.99):
    vel = (cam_pos(t + 0.005) - cam_pos(t - 0.005)) / 0.01; print(f'CAM t={t} 速度 {vel.length:.3f} m/s，与入射方向夹角 {math.degrees(vel.angle(-UDIR)):.1f}°，到 G 距离 {(cam_pos(t) - G_A).length:.3f}')
print('CAM 每秒速度 (m/s):', ' '.join(f'{t}s={((cam_pos(t + 0.01) - cam_pos(t - 0.01)) / 0.02).length:.2f}' for t in range(1, 13)))
print('PATH', PATH_T, '| 总长', round(L_TOTAL, 2), '| path_mid', tuple(round(v, 3) for v in PATH_MID), '| 采样点数 e1/o/e2', PATH_N)
print('NIC_A', tuple(round(v, 4) for v in NIC_A), '| PORT_A', tuple(round(v, 4) for v in pa[-1]), '| NIC_B', tuple(round(v, 4) for v in NIC_B), '| PORT_B', tuple(round(v, 4) for v in pb[0]))
print('BUILD_SEC', round(time.time() - T_BUILD, 2), '| 物体数', len(bpy.data.objects))
if args.anchors:
    os.makedirs(args.out, exist_ok=True); C.export_anchors(os.path.join(args.out, f'anchors_{shot.id}.json'), shot, cam, ANCHORS)
C.render(args, shot, dev)
