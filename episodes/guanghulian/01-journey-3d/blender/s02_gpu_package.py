# S02 贴近 GPU 封装 → 进入芯片（13–23 秒）。单位：1 = 1 mm。
# 状态：v0 粗模（预演用）。封装排布为示例结构，不对应具体产品；不能当最终科学结构交付。
# 结构（倒装）：电路板 → 有机基板 → 硅中介层 → 大芯片（背面朝上）+ 两侧各 4 颗存储芯片；四周金属加强环；上面压散热器。
# 镜头：散热器升起淡出 → 对数匀速推向大芯片靠边的位置 → 硅背面透明化，露出下面的金属连线层和 32 条并排的数据线。
# 运行：blender -b --python-exit-code 1 --python s02_gpu_package.py -- <输出目录> [--times 13.2,16.5,19,22.5] [--res 270x480] [--samples 24]
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import common as C

shot = C.Shot('S02'); args = C.parse_args(); sc = C.reset(shot); random.seed(2)
rad = math.radians

# ---------- 尺寸（mm） ----------
SUB = (72, 72, 1.6)                    # 有机基板
INT = (48, 42, 0.1)                    # 硅中介层
DIE = (26, 31, 0.78)                   # 大芯片（约 800 mm²，示例）
HBM = (8, 10, 0.72)                    # 存储芯片（示例画 8 颗）
Z_SUB = SUB[2]; Z_INT = Z_SUB + INT[2]; Z_DIE0 = Z_INT + 0.05; Z_DIE1 = Z_DIE0 + DIE[2]
P = Vector((4.0, -DIE[1] / 2 + 2.0, 0))   # 落点：大芯片靠边 2 mm 处（串化电路通常在芯片边缘一带）
Z_BEOL = Z_DIE0 + 0.012                # 金属连线层（在芯片朝下的一面）
BUS_N = 32; BUS_PITCH = 0.001; BUS_W = 0.00045   # 32 条并排的数据线：间距 1 µm（示意）

# ---------- 材质 ----------
M = {}
M['silicon'] = C.pbr('硅背面', (0.22, 0.24, 0.30), metallic=0.92, rough=0.22, noise_scale=6, noise_rough=0.12, stretch=(1, 60, 1), bump=0.04, fade=True)
M['hbm'] = C.pbr('存储芯片', (0.20, 0.21, 0.25), metallic=0.85, rough=0.22, noise_scale=30, noise_rough=0.06)
M['interposer'] = C.pbr('硅中介层', (0.10, 0.11, 0.14), metallic=0.8, rough=0.3)
M['underfill'] = C.pbr('底部填充胶', (0.035, 0.03, 0.028), rough=0.35, coat=0.4)
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
M['copper'] = C.pbr('铜连线', (0.75, 0.42, 0.20), metallic=1.0, rough=0.35)
M['label'] = C.emit('尺度字', (0.95, 0.92, 0.86), 2.2, aov=False, fade=True)
M['bus_on'] = C.emit('数据线（亮 = 1）', C.GOLD, 1.7)
M['bus_off'] = C.pbr('数据线（暗 = 0）', (0.55, 0.32, 0.16), metallic=1.0, rough=0.4, emission=C.GOLD, emission_strength=0.10)

def pcb_material(name, base, trace, scale):
    """电路板：阻焊层颜色 + 走线纹（两个方向的细条纹按区块交替），带一点凹凸"""
    m = C.pbr(name, base, rough=0.38, coat=0.5); N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale,) * 3; L.new(tc.outputs['Object'], mp.inputs['Vector'])
    blk = N.new('ShaderNodeTexVoronoi'); blk.feature = 'F1'; blk.distance = 'CHEBYCHEV'; blk.inputs['Scale'].default_value = 0.35; L.new(mp.outputs[0], blk.inputs['Vector'])
    sep = N.new('ShaderNodeSeparateXYZ'); L.new(mp.outputs[0], sep.inputs[0])
    def stripes(sock):
        f = N.new('ShaderNodeMath'); f.operation = 'FRACT'; L.new(sock, f.inputs[0]); g = N.new('ShaderNodeMath'); g.operation = 'LESS_THAN'; g.inputs[1].default_value = 0.42
        L.new(f.outputs[0], g.inputs[0]); return g.outputs[0]
    sx = stripes(sep.outputs['X']); sy = stripes(sep.outputs['Y'])
    pick = N.new('ShaderNodeMath'); pick.operation = 'GREATER_THAN'; pick.inputs[1].default_value = 0.5
    sc2 = N.new('ShaderNodeSeparateColor'); L.new(blk.outputs['Color'], sc2.inputs[0]); L.new(sc2.outputs['Red'], pick.inputs[0])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'FLOAT'; L.new(pick.outputs[0], mx.inputs['Factor']); L.new(sx, mx.inputs['A']); L.new(sy, mx.inputs['B'])
    gate = N.new('ShaderNodeMath'); gate.operation = 'GREATER_THAN'; gate.inputs[1].default_value = 0.35; L.new(sc2.outputs['Green'], gate.inputs[0])
    tr = N.new('ShaderNodeMath'); tr.operation = 'MULTIPLY'; L.new(mx.outputs['Result'], tr.inputs[0]); L.new(gate.outputs[0], tr.inputs[1])
    col = N.new('ShaderNodeMix'); col.data_type = 'RGBA'; col.inputs['A'].default_value = (*base, 1); col.inputs['B'].default_value = (*trace, 1)
    L.new(tr.outputs[0], col.inputs['Factor']); L.new(col.outputs['Result'], b.inputs['Base Color'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.15; bp.inputs['Distance'].default_value = 0.02; L.new(tr.outputs[0], bp.inputs['Height']); L.new(bp.outputs[0], b.inputs['Normal'])
    return m

def beol_material():
    """金属连线层（简化示意）：三个尺度的直角走线，区块里横竖交替。铜色，不发金色光（金色只给信号）。"""
    m = C.pbr('金属连线层', (0.03, 0.035, 0.05), metallic=0.3, rough=0.4); N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); acc = None
    for scale, duty, blocks, gain in ((1.5, 0.30, 0.4, 1.0), (40, 0.45, 6, 0.7), (350, 0.35, 30, 0.45)):
        mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale,) * 3; L.new(tc.outputs['Object'], mp.inputs['Vector'])
        sep = N.new('ShaderNodeSeparateXYZ'); L.new(mp.outputs[0], sep.inputs[0])
        blk = N.new('ShaderNodeTexVoronoi'); blk.distance = 'CHEBYCHEV'; blk.inputs['Scale'].default_value = blocks / scale; L.new(mp.outputs[0], blk.inputs['Vector'])
        sc2 = N.new('ShaderNodeSeparateColor'); L.new(blk.outputs['Color'], sc2.inputs[0])
        outs = []
        for ax in ('X', 'Y'):
            f = N.new('ShaderNodeMath'); f.operation = 'FRACT'; L.new(sep.outputs[ax], f.inputs[0]); g = N.new('ShaderNodeMath'); g.operation = 'LESS_THAN'; g.inputs[1].default_value = duty
            L.new(f.outputs[0], g.inputs[0]); outs.append(g.outputs[0])
        pick = N.new('ShaderNodeMath'); pick.operation = 'GREATER_THAN'; pick.inputs[1].default_value = 0.5; L.new(sc2.outputs['Red'], pick.inputs[0])
        mx = N.new('ShaderNodeMix'); mx.data_type = 'FLOAT'; L.new(pick.outputs[0], mx.inputs['Factor']); L.new(outs[0], mx.inputs['A']); L.new(outs[1], mx.inputs['B'])
        g2 = N.new('ShaderNodeMath'); g2.operation = 'MULTIPLY'; g2.inputs[1].default_value = gain; L.new(mx.outputs['Result'], g2.inputs[0])
        if acc is None: acc = g2.outputs[0]
        else:
            mxm = N.new('ShaderNodeMath'); mxm.operation = 'MAXIMUM'; L.new(acc, mxm.inputs[0]); L.new(g2.outputs[0], mxm.inputs[1]); acc = mxm.outputs[0]
    col = N.new('ShaderNodeMix'); col.data_type = 'RGBA'; col.inputs['A'].default_value = (0.010, 0.016, 0.034, 1); col.inputs['B'].default_value = (0.30, 0.17, 0.09, 1)
    L.new(acc, col.inputs['Factor']); L.new(col.outputs['Result'], b.inputs['Base Color']); L.new(acc, b.inputs['Metallic'])
    em = N.new('ShaderNodeMix'); em.data_type = 'RGBA'; em.inputs['A'].default_value = (0, 0, 0, 1); em.inputs['B'].default_value = (0.75, 0.42, 0.20, 1)
    L.new(acc, em.inputs['Factor']); L.new(em.outputs['Result'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 0.035
    return m

M['board'] = pcb_material('电路板', (0.005, 0.030, 0.022), (0.012, 0.07, 0.05), 0.9)
M['beol'] = beol_material()

# ---------- 机箱底和主板（环境，避免「黑色虚空里孤零零一块」） ----------
env = C.collection('环境')
CX, CY = 53, 130                       # 机箱中心相对 GPU A 的位置（mm）
C.box('机箱底板', (447, 900, 1.2), (CX, CY + 150, -14), M['steel'], env)
C.box('主板', (430, 560, 2.4), (CX, CY, -1.2 - 4), pcb_material('主板', (0.006, 0.028, 0.024), (0.012, 0.06, 0.045), 0.35), env, bevel=0.3)
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
C.box('硅中介层', INT, (0, 0, Z_SUB + INT[2] / 2), M['interposer'], mod)
C.box('底部填充胶', (INT[0] - 1.0, INT[1] - 1.0, 0.04), (0, 0, Z_INT + 0.02), M['underfill'], mod)
die = C.box('大芯片', DIE, (0, 0, (Z_DIE0 + Z_DIE1) / 2), M['silicon'], mod, bevel=0.02)
hb = C.Mesh()
for sx in (-1, 1):
    for k in range(4): hb.box(HBM, (sx * (DIE[0] / 2 + 1.2 + HBM[0] / 2), (k - 1.5) * (HBM[1] + 0.35), Z_DIE0 + HBM[2] / 2))
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

# ---------- 金属连线层 + 32 条并排数据线（硅透明化后才看得见） ----------
C.box('金属连线层', (DIE[0] - 0.1, DIE[1] - 0.1, 0.004), (0, 0, Z_BEOL), M['beol'], mod)
on = C.Mesh(); off = C.Mesh(); zb = Z_BEOL + 0.004
bits = [random.random() > 0.5 for _ in range(BUS_N)]
for i in range(BUS_N):
    (on if bits[i] else off).box((BUS_W, 1.2, 0.0005), (P.x + (i - (BUS_N - 1) / 2) * BUS_PITCH, P.y + 0.3, zb))
on.obj('数据线亮', M['bus_on'], mod); off.obj('数据线暗', M['bus_off'], mod)
C.box('数据线通道', (BUS_N * BUS_PITCH + 0.012, 1.3, 0.0003), (P.x, P.y + 0.3, Z_BEOL + 0.0023), C.pbr('通道底', (0.006, 0.008, 0.014), rough=0.6), mod)

# ---------- 3D 尺度字：约 3 cm ----------
zt = Z_DIE1 + 0.25
lab = C.text3d('尺度字_约3cm', '约 3 cm', 2.6, (2.5, -5.0, zt), M['label'], rot=(0, 0, 0), col=mod)
ar = C.Mesh(); ar.box((DIE[0] - 3, 0.22, 0.12), (0, -8, zt))
for s in (-1, 1): ar.cyl(0.0, 1.8, (s * (DIE[0] / 2 - 0.9), -8, zt), rot=(0, s * rad(90), 0), seg=3, r2=0.9)
arrow = ar.obj('尺度箭头', M['label'], mod)
for o in (lab, arrow): C.key_fade(o, [(shot.t0, 0), (15.3, 0), (15.8, 1), (17.4, 1), (17.9, 0)])

# ---------- 动画 ----------
for f_t, dz in ((13.0, 0), (13.4, 0), (15.6, 130)):
    hs_base.location.z = Z_DIE1 + 2.6 + dz; hs_base.keyframe_insert('location', frame=C.F(f_t))
for o in (hs_base, hs_fins): C.key_fade(o, [(13.0, 1), (14.3, 1), (15.5, 0)])
C.key_fade(die, [(13.0, 1), (17.5, 1), (19.3, 0.0)])

# 相机：对数匀速推进。落点 P；俯角由 52° 压到 82°；方位缓慢转 22°。
cam, tgt = C.add_camera('cam_S02', lens=50, fstop=1.0, clip=(0.0005, 5000))
def dist_at(t):
    if t < 15.2: return C.loglerp(330, 190, C.seg(t, 13.0, 15.2))      # 起步速度约 83 mm/s，接 S01 末端的 0.08 m/s
    if t < 18.5: return C.loglerp(190, 3.0, C.seg(t, 15.2, 18.5))
    return C.loglerp(3.0, 0.15, C.seg(t, 18.5, 22.4) ** 0.9 if t < 22.4 else 1.0)
def cam_fn(t):
    d = dist_at(t); u = C.seg(t, 13.0, 21.0)
    el = rad(C.lerp(50, 82, C.smooth(u))); az = rad(C.lerp(-112, -90, C.smooth(C.seg(t, 13.0, 23.0))))
    focus = Vector((C.lerp(0, P.x, C.smooth(C.seg(t, 13.5, 17.0))), C.lerp(0, P.y, C.smooth(C.seg(t, 13.5, 17.0))), C.lerp(Z_DIE1, Z_BEOL, C.smooth(C.seg(t, 18.6, 20.2)))))
    loc = focus + d * Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    return dict(loc=loc, tgt=focus, fstop=50e-3 / (2 * 0.005 * d))       # 光圈随距离缩放：虚化程度在各个尺度上看起来一致
C.animate_camera(cam, tgt, cam_fn, shot)

# ---------- 灯光：暖色逆光勾边 + 冷色补光 ----------
C.world((0.012, 0.016, 0.026), 1.0, hdri='studio_small_09_2k.hdr', hdri_strength=0.35, hdri_rot=rad(40))
C.area_light('主光_暖逆光', (-180, 260, 240), (0, 0, 0), 260, 2.6e6, (1.0, 0.82, 0.62))
C.area_light('补光_冷', (240, -200, 160), (0, 0, 0), 300, 7.0e5, (0.62, 0.78, 1.0))
C.area_light('顶光', (0, -20, 320), (0, 0, 0), 200, 4.0e5, (1, 1, 1))
C.area_light('芯片近光', (P.x - 6, P.y - 8, 14), (P.x, P.y, Z_DIE0), 10, 2.5e2, (0.66, 0.78, 1.0))

dev = C.setup_render(args, exposure=0.0)
if args.anchors:
    C.export_anchors(os.path.join(args.out, f'anchors_{shot.id}.json'), shot, cam,
                     {'大芯片': Vector((-6, 6, Z_DIE1)), 'package': Vector((0, SUB[1] / 2, Z_SUB)), 'bus': Vector((P.x, P.y, Z_BEOL))})
C.render(args, shot, dev)
