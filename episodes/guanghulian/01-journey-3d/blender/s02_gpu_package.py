# S02 贴近 GPU 封装 → 进入芯片（13–23 秒）。单位：1 = 1 mm。
# 状态：v1 粗模（预演用）。封装排布为示例结构，不对应具体产品；不能当最终科学结构交付。
# 结构（倒装）：电路板 → 有机基板 → 硅中介层 → 微凸点 → 大芯片（连线层朝下、硅背面朝上）+ 两侧各 4 颗存储芯片；四周金属加强环；上面压散热器。
# 镜头：散热器升起淡出 → 对数推进，贴着大芯片的边缘落向靠边 2 mm 的落点 → 硅背面上以落点为圆心开一个越来越大的「透视窗」，
#   露出下面的连线层 → 相机顺着窗口下到连线层，接上 S03。
# 连线层（并排数据线、串化电路、周围连线、微凸点、中介层表面）、它的材质、灯光和 22.3 秒以后的相机路线都来自 beol_assets.py，
#   和 S03 是同一套：这里缩到 0.001 倍（1 µm = 0.001 mm）放在落点，所以 23.0 秒两边画面一致，不用切。
# 示意、要在屏幕上加注的：硅和绝缘层透明化；连线为简化示意；硅背面的打标内容是示例字符；没画底部填充胶和塑封（为了看见微凸点和侧壁分层）。
# 运行：blender -b --python-exit-code 1 --python s02_gpu_package.py -- <输出目录> [--times 13.2,16.5,19,22.5] [--res 270x480] [--samples 24]
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix, Euler
import common as C
import beol_assets as B

shot = C.Shot('S02'); args = C.parse_args(); sc = C.reset(shot); random.seed(2)
rad = math.radians

# ---------- 尺寸（mm） ----------
SUB = (72, 72, 1.6)                    # 有机基板
INT = (48, 42, 0.1)                    # 硅中介层
DIE = (26, 31, 0.78)                   # 大芯片（约 800 mm²，示例）
HBM = (8, 10, 0.72)                    # 存储芯片（示例画 8 颗）
UM = 0.001                             # 1 µm = 0.001 mm
Z_SUB = SUB[2]; Z_INT = Z_SUB + INT[2]
Z_BEOL = Z_INT - B.Z_FLOOR * UM        # 连线层局部坐标 z = 0 的高度：中介层表面往上 36 µm（微凸点 + 上层金属，见 beol_assets）
Z_DIE0 = Z_BEOL + 1 * UM               # 硅本体的底面（晶体管那一面），紧贴在最细的连线上方
Z_DIE1 = 2.53                          # 硅背面（和 v0 相同：13.0 秒的相机对着它，不能动）；硅本体厚约 0.79 mm
P = Vector((9.5, -DIE[1] / 2 + 2.0, 0))   # 落点：大芯片靠边 2 mm、离右侧存储芯片约 5 mm（串化电路通常在芯片边缘一带）
R_MAX = 1.5                            # 「透视窗」的最大半径（mm）；连线层铺开的范围比它大（beol_assets.FIELD_X / FIELD_Y）

# ---------- 材质 ----------
M = {}
M['silicon'] = C.pbr('硅背面', (0.22, 0.24, 0.30), metallic=0.92, rough=0.22)          # 研磨纹和透视窗在下面 grind_marks()、add_window() 里加
M['laser'] = C.pbr('激光打标', (0.50, 0.52, 0.56), metallic=0.3, rough=0.85)             # 激光打过的地方：发白、哑光
M['cut'] = C.pbr('透视窗的窗壁', (0.07, 0.09, 0.14), metallic=0.2, rough=0.6, emission=(0.45, 0.60, 0.85), emission_strength=0.10)
M['hbm'] = C.pbr('存储芯片', (0.20, 0.21, 0.25), metallic=0.85, rough=0.22, noise_scale=30, noise_rough=0.06)
MB = B.materials()                     # 连线层的材质（和 S03 同一套）
M['interposer'] = MB['floor']          # 硅中介层用连线层里「中介层表面」的同一个材质：近看和远看是同一块东西
M['substrate'] = C.pbr('有机基板', (0.008, 0.055, 0.036), rough=0.42, coat=0.35, noise_scale=1.5, noise_rough=0.08, bump=0.05)
M['ring'] = C.pbr('加强环', (0.74, 0.73, 0.70), metallic=1.0, rough=0.30, noise_scale=6, noise_rough=0.1, stretch=(1, 40, 1))
M['alu'] = C.pbr('铝鳍片', (0.80, 0.81, 0.83), metallic=1.0, rough=0.34, noise_scale=3, noise_rough=0.1, stretch=(1, 1, 30), fade=True)
M['nickel'] = C.pbr('镀镍铜底座', (0.78, 0.74, 0.66), metallic=1.0, rough=0.25, noise_scale=4, noise_rough=0.1, fade=True)
M['alu_n'] = C.pbr('铝鳍片（邻）', (0.80, 0.81, 0.83), metallic=1.0, rough=0.34, noise_scale=3, noise_rough=0.1, stretch=(1, 1, 30))
M['epoxy'] = C.pbr('黑色塑封', (0.018, 0.018, 0.02), rough=0.45, noise_scale=20, noise_rough=0.08, bump=0.02)
M['ferrite'] = C.pbr('电感', (0.10, 0.10, 0.105), rough=0.7, noise_scale=8, noise_rough=0.1, bump=0.08)
M['mlcc'] = C.pbr('电容体', (0.50, 0.38, 0.25), rough=0.55)
M['tin'] = C.pbr('焊端', (0.82, 0.82, 0.80), metallic=1.0, rough=0.38)
M['can'] = C.pbr('电容铝壳', (0.72, 0.73, 0.75), metallic=1.0, rough=0.3)
M['steel'] = C.pbr('机箱钢板', (0.30, 0.31, 0.33), metallic=1.0, rough=0.45, noise_scale=0.05, noise_rough=0.1)
M['label'] = C.emit('尺度字', (0.95, 0.92, 0.86), 2.2, aov=False, fade=True)
M['route'] = C.emit('电的路（接 S01）', C.GOLD, 1.0, fade=True)

def pcb_material(name, base):
    """电路板：素的阻焊色。不画程序条纹冒充布线（外部审阅意见）；真实布线等正式资产再做。"""
    return C.pbr(name, base, rough=0.38, coat=0.5, noise_scale=0.6, noise_rough=0.05)

def grind_marks(m, center=(-70.0, -95.0), strength=1.0):
    """硅背面的研磨纹：减薄时砂轮留下的同心弧形细纹。圆心在芯片外面很远（晶圆比芯片大得多），所以在芯片上看是一组近乎平行的弧线。
    做法：到圆心的距离 → 一维噪声（粗细两档）→ 扰动粗糙度、明暗和一点凹凸。"""
    N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
    cmb = N.new('ShaderNodeCombineXYZ'); L.new(sep.outputs['X'], cmb.inputs['X']); L.new(sep.outputs['Y'], cmb.inputs['Y'])
    dist = N.new('ShaderNodeVectorMath'); dist.operation = 'DISTANCE'; L.new(cmb.outputs[0], dist.inputs[0]); dist.inputs[1].default_value = (*center, 0)
    acc = None
    for scale, gain in ((0.7, 0.55), (9.0, 0.45)):
        nz = N.new('ShaderNodeTexNoise'); nz.noise_dimensions = '1D'; nz.inputs['Scale'].default_value = scale; nz.inputs['Detail'].default_value = 7.0
        nz.inputs['Roughness'].default_value = 0.65; L.new(dist.outputs['Value'], nz.inputs['W'])
        g = N.new('ShaderNodeMath'); g.operation = 'MULTIPLY'; g.inputs[1].default_value = gain; L.new(nz.outputs['Fac'], g.inputs[0])
        if acc is None: acc = g.outputs[0]
        else:
            ad = N.new('ShaderNodeMath'); ad.operation = 'ADD'; L.new(acc, ad.inputs[0]); L.new(g.outputs[0], ad.inputs[1]); acc = ad.outputs[0]
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.3; mr.inputs['From Max'].default_value = 0.7
    mr.inputs['To Min'].default_value = 0.14; mr.inputs['To Max'].default_value = 0.14 + 0.36 * strength; L.new(acc, mr.inputs['Value']); L.new(mr.outputs[0], b.inputs['Roughness'])
    mc = N.new('ShaderNodeMapRange'); mc.inputs['From Min'].default_value = 0.3; mc.inputs['From Max'].default_value = 0.7
    mc.inputs['To Min'].default_value = 1.0 - 0.45 * strength; mc.inputs['To Max'].default_value = 1.0 + 0.25 * strength; L.new(acc, mc.inputs['Value'])
    base = b.inputs['Base Color'].default_value[:3]; mul = N.new('ShaderNodeVectorMath'); mul.operation = 'SCALE'; mul.inputs[0].default_value = base
    L.new(mc.outputs[0], mul.inputs['Scale']); L.new(mul.outputs[0], b.inputs['Base Color'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.05; L.new(acc, bp.inputs['Height']); L.new(bp.outputs[0], b.inputs['Normal'])

WINDOW_NODES = []
def add_window(m, rim=True):
    """「透视窗」：以落点 P 为轴的圆柱范围内，这个材质完全透明；半径由节点 window_R 决定（打关键帧）。
    rim：窗沿画一圈发亮的细边（中性的冷白，不用金 / 青 / 珊瑚），让观众看清窗口的边界在往外扩。"""
    N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    geo = N.new('ShaderNodeNewGeometry'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs[0])
    cmb = N.new('ShaderNodeCombineXYZ'); L.new(sep.outputs['X'], cmb.inputs['X']); L.new(sep.outputs['Y'], cmb.inputs['Y'])
    dist = N.new('ShaderNodeVectorMath'); dist.operation = 'DISTANCE'; L.new(cmb.outputs[0], dist.inputs[0]); dist.inputs[1].default_value = (P.x, P.y, 0)
    rv = N.new('ShaderNodeValue'); rv.name = 'window_R'; WINDOW_NODES.append(rv)
    gt = N.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; L.new(dist.outputs['Value'], gt.inputs[0]); L.new(rv.outputs[0], gt.inputs[1])
    L.new(gt.outputs[0], b.inputs['Alpha'])
    if rim:
        r2 = N.new('ShaderNodeMath'); r2.operation = 'MULTIPLY_ADD'; L.new(rv.outputs[0], r2.inputs[0]); r2.inputs[1].default_value = 1.035; r2.inputs[2].default_value = 0.004
        lt = N.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; L.new(dist.outputs['Value'], lt.inputs[0]); L.new(r2.outputs[0], lt.inputs[1])
        pos = N.new('ShaderNodeMath'); pos.operation = 'GREATER_THAN'; L.new(rv.outputs[0], pos.inputs[0]); pos.inputs[1].default_value = 1e-4
        e = N.new('ShaderNodeMath'); e.operation = 'MULTIPLY'; L.new(lt.outputs[0], e.inputs[0]); L.new(pos.outputs[0], e.inputs[1])
        e2 = N.new('ShaderNodeMath'); e2.operation = 'MULTIPLY'; e2.inputs[1].default_value = 1.6; L.new(e.outputs[0], e2.inputs[0])
        b.inputs['Emission Color'].default_value = (0.70, 0.85, 1.0, 1); L.new(e2.outputs[0], b.inputs['Emission Strength'])

M['board'] = pcb_material('电路板', (0.005, 0.030, 0.022))
grind_marks(M['silicon']); add_window(M['silicon']); add_window(M['laser'], rim=False)

# ---------- 机箱底和主板（环境，避免「黑色虚空里孤零零一块」） ----------
env = C.collection('环境')
CX, CY = 53, 130                       # 机箱中心相对 GPU A 的位置（mm）
C.box('机箱底板', (447, 900, 1.2), (CX, CY + 150, -14), M['steel'], env)
C.box('主板', (430, 560, 2.4), (CX, CY, -1.2 - 4), pcb_material('主板', (0.006, 0.028, 0.024)), env, bevel=0.3)
for sx in (-1, 1): C.box(f'机箱侧板{sx}', (1.2, 900, 170), (CX + sx * 223, CY + 150, 71), M['steel'], env)
C.box('机箱前挡', (447, 1.2, 170), (CX, CY - 300, 71), M['steel'], env)

# ---------- GPU 模组：小板 + 封装 ----------
mod = C.collection('GPU模组A')
C.box('模组电路板', (102, 200, 2.4), (0, 0, -1.2), M['board'], mod, bevel=0.3)
C.box('有机基板', SUB, (0, 0, SUB[2] / 2), M['substrate'], mod, bevel=0.15)
ring = C.Mesh(); t = 9.0; rz = Z_SUB + 0.5
ring.box((SUB[0] - 2, t, 1.0), (0, (SUB[1] - 2 - t) / 2, rz)); ring.box((SUB[0] - 2, t, 1.0), (0, -(SUB[1] - 2 - t) / 2, rz))
ring.box((t, SUB[1] - 2 - 2 * t, 1.0), ((SUB[0] - 2 - t) / 2, 0, rz)); ring.box((t, SUB[1] - 2 - 2 * t, 1.0), (-(SUB[0] - 2 - t) / 2, 0, rz))
ring.obj('加强环', M['ring'], mod, bevel=0.12)
C.box('硅中介层', (INT[0], INT[1], INT[2] - 0.5 * UM), (0, 0, Z_SUB + (INT[2] - 0.5 * UM) / 2), M['interposer'], mod)   # 顶面让出 0.5 µm：落点附近由连线层自带的「中介层表面」盖住
# 没画底部填充胶（真实封装里微凸点之间和芯片四周有一圈胶，这里省掉，侧面才看得见「硅 → 连线层 → 微凸点 → 中介层」的分层）
die = C.box('大芯片', (DIE[0], DIE[1], Z_DIE1 - Z_DIE0), (0, 0, (Z_DIE0 + Z_DIE1) / 2), M['silicon'], mod, bevel=0.02)
rim = C.Mesh(); zr = (Z_DIE0 + Z_BEOL + B.Z_PAD0 * UM) / 2; hr = Z_DIE0 - (Z_BEOL + B.Z_PAD0 * UM); wr = 0.10   # 连线层在芯片四边的侧面（约 12 µm 厚的一条铜色）
for sy in (-1, 1): rim.box((DIE[0], wr, hr), (0, sy * (DIE[1] - wr) / 2, zr)); rim.box((wr, DIE[1] - 2 * wr, hr), (sy * (DIE[0] - wr) / 2, 0, zr))
rim.obj('连线层侧面', MB['thick'], mod)
hb = C.Mesh()
for sx in (-1, 1):
    for k in range(4): hb.box(HBM, (sx * (DIE[0] / 2 + 1.2 + HBM[0] / 2), (k - 1.5) * (HBM[1] + 0.35), Z_DIE0 + HBM[2] / 2 + 0.03))
hb.obj('存储芯片', M['hbm'], mod, bevel=0.02)
# 基板边上的去耦电容（小贴片）
cb = C.Mesh(); ct = C.Mesh()
def mlcc(x, y, z, L=1.0, W=0.5, H=0.5, along='X'):
    sx, sy = (L, W) if along == 'X' else (W, L)
    cb.box((sx * 0.6 if along == 'X' else sx, sy if along == 'X' else sy * 0.6, H), (x, y, z + H / 2))
    for s in (-1, 1):
        if along == 'X': ct.box((L * 0.2, W * 1.02, H * 1.02), (x + s * L * 0.4, y, z + H / 2))
        else: ct.box((W * 1.02, L * 0.2, H * 1.02), (x, y + s * L * 0.4, z + H / 2))
for k in range(-14, 15):
    for row in (0, 1):
        mlcc(k * 1.6, -(INT[1] / 2 + 1.2 + row * 1.0), Z_SUB, 1.0, 0.5, 0.5); mlcc(k * 1.6, (INT[1] / 2 + 1.2 + row * 1.0), Z_SUB, 1.0, 0.5, 0.5)
# 模组小板上的供电：电感、供电芯片、铝壳电容、成片的贴片电容
ind = C.Mesh(); drm = C.Mesh(); can = C.Mesh()
for sy in (-1, 1):
    for k in range(-3, 4):
        x = k * 12.2; y = sy * 62
        ind.box((10, 10, 7), (x, y, 3.5)); drm.box((5, 6, 0.9), (x, y - sy * 10.5, 0.45))
        for j in (-1, 0, 1): mlcc(x + j * 2.4, y - sy * 16.5, 0, 2.0, 1.2, 1.2, 'Y')
    for k in range(-4, 5): can.cyl(3.15, 7.5, (k * 9.6, sy * 78, 3.75));
    for k in range(-19, 20): mlcc(k * 2.5, sy * 88, 0, 1.6, 0.8, 0.8, 'Y'); mlcc(k * 2.5, sy * 91, 0, 1.6, 0.8, 0.8, 'Y')
for sx in (-1, 1):
    for k in range(-16, 17):
        for j in range(3): mlcc(sx * (42 + j * 3.2), k * 2.2, 0, 1.6, 0.8, 0.8, 'X')
ind.obj('电感', M['ferrite'], mod, bevel=0.6); drm.obj('供电芯片', M['epoxy'], mod, bevel=0.08); can.obj('铝壳电容', M['can'], mod, smooth=True)
cb.obj('贴片电容体', M['mlcc'], mod); ct.obj('贴片电容焊端', M['tin'], mod)

# ---------- 散热器（GPU A 的会升起淡出；邻居的留着） ----------
def heatsink(name, mat_fin, mat_base, col):
    base = C.box(name + '_底座', (96, 96, 5), (0, 0, Z_DIE1 + 0.1 + 2.5), mat_base, col, bevel=0.5)
    f = C.Mesh()
    for k in range(-23, 24): f.box((0.5, 92, 40), (k * 2.0, 0, Z_DIE1 + 5.1 + 20))
    fins = f.obj(name + '_鳍片', mat_fin, col); fins.parent = base; fins.matrix_parent_inverse = base.matrix_world.inverted(); return base, fins
hs_base, hs_fins = heatsink('散热器A', M['alu'], M['nickel'], mod)
# 邻居模组：2 列 × 4 排里的另外 7 个（只放电路板和散热器，共享网格）
nb = C.collection('邻居模组'); src_col = C.collection('邻居源'); nb_base, nb_fins = heatsink('散热器邻', M['alu_n'], M['nickel'], src_col)
nb_board = C.box('邻居电路板', (102, 200, 2.4), (0, 0, -1.2), M['board'], src_col, bevel=0.3)
PX, PY = 106, 260                      # 4 列 × 2 排（和 S01 的服务器内部一致）；GPU A = 从 −X 数第 2 列、前排
for ix in range(4):
    for iy in range(2):
        if (ix, iy) == (1, 0): continue
        C.instance_collection(src_col, f'邻居{ix}{iy}', ((ix - 1) * PX, iy * PY, 0), col=nb)
C.hide_collection(src_col)

# ---------- 连线层（和 S03 同一套几何，缩到 0.001 倍放在落点；硅透明化之后才看得见） ----------
beol = B.build(shot.t0, shot.t1)
beol['root'].location = (P.x, P.y - B.SEAM_X * UM, Z_BEOL); beol['root'].rotation_euler = (0, 0, B.ROOT_ROT); beol['root'].scale = (UM, UM, UM)
TOW = Matrix.LocRotScale(beol['root'].location, Euler(beol['root'].rotation_euler), beol['root'].scale)   # 连线层局部坐标（µm）→ 这里的坐标（mm）

# ---------- 硅背面的线索：激光打标（二维码样的点阵 + 两行示例字符）和「透视窗」的窗壁 ----------
zt = Z_DIE1 + 0.002; mk = C.Mesh(); rm = random.Random(11); NQ = 14; q = 0.075; qx0 = P.x + 0.9; qy0 = P.y + 1.15
for i in range(NQ):
    for j in range(NQ):
        if i == 0 or j == 0 or (j == NQ - 1 and i % 2 == 0) or (i == NQ - 1 and j % 2 == 0) or (0 < i < NQ - 1 and 0 < j < NQ - 1 and rm.random() > 0.5):
            mk.cyl(q * 0.42, 0.002, (qx0 + i * q, qy0 + j * q, zt), seg=8)
mk.obj('打标_点阵', M['laser'], mod)
for k, body in enumerate(('SAMPLE 001', 'LOT 00000 A')):          # 示例字符：不对应任何厂商、型号或批号
    cu = bpy.data.curves.new(f'打标_字{k}', 'FONT'); cu.body = body; cu.size = 0.42; cu.extrude = 0.001; cu.align_x = 'RIGHT'; cu.materials.append(M['laser'])
    o = C.link(bpy.data.objects.new(f'打标_字{k}', cu), mod); o.location = (qx0 - 0.25, qy0 + 0.60 - k * 0.56, zt)
wb = bmesh.new(); bmesh.ops.create_cone(wb, cap_ends=False, segments=96, radius1=1.0, radius2=1.0, depth=Z_DIE1 - Z_DIE0 - 0.002)
me = bpy.data.meshes.new('透视窗窗壁'); wb.to_mesh(me); wb.free(); me.materials.append(M['cut'])
for pl in me.polygons: pl.use_smooth = True
wall = C.link(bpy.data.objects.new('透视窗窗壁', me), mod); wall.location = (P.x, P.y, (Z_DIE0 + Z_DIE1) / 2)

# ---------- 「电的路」（接 S01 的尾帧）：金线从封装的 +Y 边沿模组小板往机箱后方走；13.3–14.8 秒淡出 ----------
rt = C.Mesh(); rt.path([(0, SUB[1] / 2, 0.2), (0, 100, 0.2)], 2.5, 0.3)
rt.path([(0, 101.25, 0.2), (0, 101.25, -3.85), (0, 160, -3.85)], 2.5, 0.3)      # 小板边缘以后：下到主板、继续往后（S01 的走法待对齐）
route = rt.obj('电的路', M['route'], mod); C.key_fade(route, [(13.0, 1), (13.3, 1), (14.8, 0)])
route.hide_render = False; route.keyframe_insert('hide_render', frame=C.F(14.8)); route.hide_render = True; route.keyframe_insert('hide_render', frame=C.F(14.8) + 1)

# ---------- 3D 尺度字：约 3 cm ----------
zt = Z_DIE1 + 0.25
lab = C.text3d('尺度字_约3cm', '约 3 cm', 2.6, (0, -4.6, zt), M['label'], rot=(0, 0, 0), col=mod)
ar = C.Mesh(); ar.box((DIE[0] - 3, 0.22, 0.12), (0, -8, zt))
for s in (-1, 1): ar.cyl(0.0, 1.8, (s * (DIE[0] / 2 - 0.9), -8, zt), rot=(0, s * rad(90), 0), seg=3, r2=0.9)
arrow = ar.obj('尺度箭头', M['label'], mod)
for o in (lab, arrow): C.key_fade(o, [(shot.t0, 0), (14.9, 0), (15.4, 1), (16.5, 1), (17.0, 0)])   # 整颗芯片还在画面里的时候给尺度

# ---------- 动画 ----------
for f_t, dz in ((13.0, 0), (13.4, 0), (15.6, 130)):
    hs_base.location.z = Z_DIE1 + 2.6 + dz; hs_base.keyframe_insert('location', frame=C.F(f_t))
for o in (hs_base, hs_fins): C.key_fade(o, [(13.0, 1), (14.3, 1), (15.5, 0)])
# 「透视窗」：17.5 秒从落点打开，半径跟着画面一起变（先占画面一小块，再比画面大）；20.2 秒到 R_MAX。
# 21.0 秒以后相机已经在窗口里面、画面里只剩连线层，这时把窗口扩到整颗芯片（硅全部透明），窗壁同时撤掉。
R_KEYS = [(17.5, 0.0, 0.0), (17.9, 0.22, None), (18.4, 0.58, None), (19.0, 1.0, None), (19.6, 1.35, None), (20.2, R_MAX, 0.0)]
def window_R(t):
    if t >= 21.0: return C.lerp(R_MAX, 60.0, C.smooth(C.seg(t, 21.0, 21.7)))
    return max(0.0, B.hermite(R_KEYS, min(t, 20.2)))
for f in range(C.F(17.4), C.F(21.8) + 1):
    r = window_R((f - 1) / C.FPS)
    for nd in WINDOW_NODES: nd.outputs[0].default_value = r; nd.outputs[0].keyframe_insert('default_value', frame=f)
    wall.scale = (max(r, 1e-5), max(r, 1e-5), 1); wall.keyframe_insert('scale', frame=f)
for m in (M['silicon'], M['laser']): C.set_interp(m.node_tree, 'LINEAR')
C.set_interp(wall, 'LINEAR')
for o, t_on, t_off in ((wall, 17.5, 21.0),):
    o.hide_render = True; o.keyframe_insert('hide_render', frame=shot.f0); o.hide_render = False; o.keyframe_insert('hide_render', frame=C.F(t_on))
    o.hide_render = True; o.keyframe_insert('hide_render', frame=C.F(t_off))

# 相机：对数推进，一个连续镜头。13.0 秒的位置、朝向、焦距、速度和 v0 相同（S01 的尾帧对着它）。
#   13–16 秒：散热器升起，推向封装；16–17.5 秒：加速甩过没什么可看的量级，俯角保持在 60° 上下，芯片的边缘和侧壁留在画面下方；
#   17.5–20.5 秒：透视窗打开，俯角压到接近正俯视，相机顺着窗口下到连线层；
#   20.8–22.3 秒：过渡到连线层自己的相机路线（beol_assets.orbit），之后和 S03 是同一条路线，23.0 秒位置、朝向、速度都连续。
cam, tgt = C.add_camera('cam_S02', lens=50, fstop=1.0, clip=(0.0005, 5000))
K0 = math.log(190 / 330) / 2.2                                             # 起步的对数速度（约 83 mm/s，接 S01 末端的 0.08 m/s）
T_JOIN = 22.3; D_JOIN = B.orbit(T_JOIN)['d'] * UM
LND = [(13.0, math.log(330), K0), (14.0, math.log(330) + K0, K0)] + [(t, math.log(d), None) for t, d in
       ((15.2, 172), (16.2, 78), (17.0, 24), (17.6, 11.5), (18.2, 6.6), (18.8, 4.1), (19.4, 2.6), (20.0, 1.55), (20.8, 0.66), (21.6, 0.31))] + [(T_JOIN, math.log(D_JOIN), B.K_SEAM)]
P_EDGE = P + Vector((0, -0.8, 0))                                          # 先对准落点和芯片边缘之间，让边缘和侧壁多留一会儿
def cam_params(t):
    """返回 对焦点、距离、俯角、方位角（度）、光圈比。22.3 秒以后完全等于连线层的相机路线。"""
    f = Vector((0, 0, 0)).lerp(P_EDGE, C.smooth(C.seg(t, 13.5, 17.0))).lerp(P, C.smooth(C.seg(t, 17.6, 19.4)))
    f.z = C.lerp(Z_DIE1, Z_BEOL, C.smooth(C.seg(t, 18.8, 20.6)))
    lnd = B.hermite(LND, t); el = C.lerp(50, 62, C.smooth(C.seg(t, 13.0, 17.6))) + C.lerp(0, 20, C.smooth(C.seg(t, 18.0, 21.4)))
    az = C.lerp(-112, -90, C.smooth(C.seg(t, 13.0, 21.5))); ap = 0.010
    w = C.smoother(C.seg(t, 20.8, T_JOIN))
    if w > 0:
        mp = B.orbit(t); fm = TOW @ Vector((mp['fx'], 0, mp['fz']))
        f = f.lerp(fm, w); lnd = C.lerp(lnd, math.log(mp['d'] * UM), w); el = C.lerp(el, mp['el'], w); az = C.lerp(az, mp['az'] + math.degrees(B.ROOT_ROT) - 360, w)
        ap = C.lerp(ap, B.APERTURE, w)
    return f, math.exp(lnd), el, az, ap
def cam_fn(t):
    f, d, el, az, ap = cam_params(t); el = rad(el); az = rad(az)
    loc = f + d * Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    return dict(loc=loc, tgt=f, fstop=50e-3 / (ap * d))                    # 光圈随距离缩放：虚化程度在各个尺度上看起来一致
C.animate_camera(cam, tgt, cam_fn, shot)
for tt in (13.0, 13.0 + 1 / C.FPS, 22.9, shot.t1 - 1 / C.FPS, shot.t1):   # 接缝核对用：13.0 秒对 v0，23.0 秒对 S03（换算回连线层局部坐标 µm）
    d = cam_fn(tt); li = TOW.inverted() @ d['loc']; gi = TOW.inverted() @ d['tgt']
    print('CAMCHK S02 t=%.4f loc=(%.4f, %.4f, %.4f) tgt=(%.4f, %.4f, %.4f) | 局部µm loc=(%.3f, %.3f, %.3f) tgt=(%.3f, %.3f, %.3f) fstop=%.5f' % (tt, *d['loc'], *d['tgt'], *li, *gi, d['fstop'] * UM))

# 标注锚点「大芯片」：贴在硅背面上、跟着画面走（始终落在画面左上方的芯片表面），推近以后标签也不会跑出画面
lab_anchor = C.empty('锚点_大芯片', (-6, 6, Z_DIE1))
for f in range(shot.f0, shot.f1 + 1):
    fo, d, el, az, ap = cam_params((f - 1) / C.FPS); a = rad(az)
    v = Vector((fo.x, fo.y, 0)) + 0.07 * d * Vector((-math.sin(a), math.cos(a), 0)) * -1 + 0.20 * d * Vector((-math.cos(a), -math.sin(a), 0))
    lab_anchor.location = (max(-DIE[0] / 2 + 1, min(DIE[0] / 2 - 1, v.x)), max(-DIE[1] / 2 + 1, min(DIE[1] / 2 - 1, v.y)), Z_DIE1); lab_anchor.keyframe_insert('location', frame=f)

# ---------- 灯光 ----------
# 封装：暖色逆光勾边 + 冷色补光（和 v0 相同），不照连线层。连线层：beol_assets 的两盏平行光，只照连线层，也不被封装挡住。
# 这样连线层在这里和在 S03 里受的光完全一样（剩下的差别只有环境光被周围封装挡掉的那一点）。
B.world()
macro_lights = [C.area_light('主光_暖逆光', (-180, 260, 240), (0, 0, 0), 260, 2.6e6, (1.0, 0.82, 0.62)),
                C.area_light('补光_冷', (240, -200, 160), (0, 0, 0), 300, 7.0e5, (0.62, 0.78, 1.0)),
                C.area_light('顶光', (0, -20, 320), (0, 0, 0), 200, 4.0e5, (1, 1, 1)),
                C.area_light('芯片近光', (P.x - 6, P.y - 8, 14), (P.x, P.y, Z_DIE0), 10, 2.5e2, (0.66, 0.78, 1.0))]
ll = bpy.data.collections.new('灯光链接_不照连线层'); ll.children.link(beol['col']); ll.collection_children[0].light_linking.link_state = 'EXCLUDE'
for o in macro_lights: o.light_linking.receiver_collection = ll
B.lights(beol['root'], beol['col'])

dev = C.setup_render(args, exposure=0.0)
if args.anchors:
    C.export_anchors(os.path.join(args.out, f'anchors_{shot.id}.json'), shot, cam,
                     {'大芯片': lab_anchor, 'package': Vector((0, SUB[1] / 2, Z_SUB)), 'bus': Vector((P.x, P.y, Z_BEOL))})
C.render(args, shot, dev)
