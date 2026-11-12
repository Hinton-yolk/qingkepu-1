# S03 SerDes：并排 → 一列（23–39 秒）· 第一站 出发。单位：1 = 1 µm。
# 状态：v0 粗模（预演用）。连线层数、线宽、串化电路结构都是简化示意，不能当最终科学结构交付。
# 朝向（倒装芯片，接 S02）：相机从硅背面一侧往下看。+Z 朝硅背面（朝相机），−Z 朝凸点和封装基板。
#   所以离相机最近的是细的下层连线，往下是粗的上层金属，再往下是凸点。输出信号离开芯片 = 往 −Z 走，和相机推进同向。
# 画法：
#   · 32 条并排的数据线（「一大排」，示意画 32 条），每条线整体亮（1）或暗（0），一拍（TW 秒）同时换一排。
#   · 串化电路画成五级二选一树：32 → 16 → 8 → 4 → 2 → 1，每过一级节拍快一倍。
#   · 最后只剩一条线，节拍是并行线的 32 倍；它经输出驱动、通孔，到微凸点（直径约 25 µm、间距约 45 µm，示意），下面是硅中介层。
#     真实叠层：芯片 → 微凸点 → 硅中介层 → C4 凸点 → 有机基板 → 焊球 → 电路板（FACTS V12）。
#   · 不画沿线移动的小球：片内导线只有几十微米，一个符号对应毫米级长度，同一时刻整条线几乎等电位（FACTS V9）。
# 运行：blender -b --python-exit-code 1 --python s03_serdes.py -- <输出目录> [--times 23.2,26,30,34,37,38.8] [--res 270x480] [--samples 24]
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import common as C

shot = C.Shot('S03'); args = C.parse_args(); sc = C.reset(shot); rnd = random.Random(3); rad = math.radians

N = 32; TW = 3.2; TB = TW / N            # 并行一拍 3.2 秒；串行一拍 0.1 秒（3 帧）。真实约每秒上百亿拍，这里慢放约百亿倍
ON, OFF = 1.15, 0.06                       # 亮 / 暗时的发光强度
STAGE = 8.0                               # 每一级串化电路沿 X 占 8 µm
X_DRV0, X_DRV1, X_PAD = 46.0, 58.0, 72.0  # 输出驱动的起止、凸点的位置
Z_TOP, Z_BUMP = -9.0, -24.0               # 上层厚金属的高度、凸点中心的高度
words = [[rnd.random() > 0.5 for _ in range(N)] for _ in range(8)]

def bitrev(a, bits):
    r = 0
    for _ in range(bits): r = (r << 1) | (a & 1); a >>= 1
    return r
def ypos(m, a): return (a - (m - 1) / 2) * (N / m)      # 第 m 级（m 条线）里第 a 个位置的 y

# ---------- 材质 ----------
M = {}
M['wire'] = C.pbr('普通连线', (0.20, 0.115, 0.065), metallic=1.0, rough=0.45)
M['thick'] = C.pbr('上层厚金属', (0.16, 0.095, 0.055), metallic=1.0, rough=0.5, noise_scale=0.2, noise_rough=0.1)
M['cell'] = C.pbr('电路单元', (0.03, 0.05, 0.10), metallic=0.2, rough=0.45, coat=0.3)
M['gate'] = C.pbr('栅条', (0.10, 0.16, 0.28), metallic=0.6, rough=0.35)
M['bump'] = C.pbr('凸点', (0.62, 0.63, 0.64), metallic=1.0, rough=0.32, noise_scale=0.08, noise_rough=0.12)
M['floor'] = C.pbr('硅中介层表面', (0.012, 0.016, 0.03), metallic=0.4, rough=0.5, noise_scale=0.02, noise_rough=0.1)

def signal_material(name, m, j):
    """第 m 级里逻辑编号 j 的那条线：按时间亮暗。它依次送出第 j, j+m, j+2m… 位，每位持续 m 个串行节拍。"""
    mat = C.emit(name, C.GOLD, OFF); sock = mat.node_tree.nodes['Emission'].inputs['Strength']; keys = []
    for w in range(-1, 6):
        src = words[(w if m == N else w - 1) % len(words)]      # 并行线显示当前这一排；树里和输出线送的是上一排（先存下来再发）
        for q in range(N // m):
            t = shot.t0 + w * TW + q * m * TB
            if shot.t0 - 0.2 <= t <= shot.t1 + 0.2: keys.append((t, ON if src[j + q * m] else OFF))
    if not keys or keys[0][0] > shot.t0: keys.insert(0, (shot.t0, OFF))
    C.key_value(sock, keys, 'CONSTANT'); return mat

# ---------- 信号线：五级树 ----------
sig = C.collection('信号')
levels = [N >> s for s in range(6)]        # 32, 16, 8, 4, 2, 1
out_mat = None
for s, m in enumerate(levels):
    bits = int(math.log2(m)); w = 0.45 * (1 + 0.3 * s)
    x0 = -320.0 if s == 0 else STAGE * (s - 1) + 6.7
    x1 = STAGE * s + 4.5 if m > 1 else X_DRV0
    for a in range(m):
        j = bitrev(a, bits); mat = signal_material(f'信号_{m}_{j}', m, j); y = ypos(m, a)
        C.box(f'线_{m}_{a}', (x1 - x0, w, 0.5), ((x0 + x1) / 2, y, 0), mat, sig)
        if m == 1: out_mat = mat
# 二选一单元（每级 m/2 个），压在两条输入线的汇合处
cells = C.Mesh(); gates = C.Mesh()
for s, m in enumerate(levels[:-1]):
    for a in range(m // 2):
        y = ypos(m // 2, a); span = (N / m) + 0.9; x = STAGE * s + 5.6
        cells.box((2.4, span, 0.9), (x, y, -0.1))
        for g in (-0.7, 0.0, 0.7): gates.box((0.16, span + 0.3, 0.2), (x + g, y, 0.5))
cells.obj('二选一单元', M['cell'], sig, bevel=0.06); gates.obj('栅条', M['gate'], sig)
# 输出驱动（一排越来越大的反相器，示意）→ 厚金属 → 通孔 → 焊盘 → 凸点。整条输出网络同亮同暗。
drv = C.Mesh(); dg = C.Mesh()
for k in range(4):
    wy = 2.0 + 2.2 * k; x = X_DRV0 + 1.5 + 3.0 * k
    drv.box((2.4, wy, 1.0), (x, 0, -0.1))
    for g in (-0.6, 0.0, 0.6): dg.box((0.18, wy + 0.4, 0.2), (x + g, 0, 0.55))
drv.obj('输出驱动', M['cell'], sig, bevel=0.06); dg.obj('驱动栅条', M['gate'], sig)
net = C.Mesh()
net.box((X_DRV1 - X_DRV0, 0.9, 0.5), ((X_DRV0 + X_DRV1) / 2, 0, 0.75))                 # 驱动上方的连接线
net.box((X_PAD - X_DRV1 + 2, 2.4, 0.9), ((X_DRV1 + X_PAD) / 2 - 1, 0, 0))               # 驱动 → 通孔
for k in range(5): net.box((2.0, 2.0, abs(Z_TOP) / 5 * 0.72), (X_PAD, 0, -abs(Z_TOP) * (k + 0.5) / 5))   # 通孔叠层
net.obj('输出网络', out_mat, sig)
bump_sig = C.Mesh(); bump_sig.sphere(12.5, (X_PAD, 0, Z_BUMP), (1, 1, 0.85)); bump_sig.obj('凸点_信号', C.pbr('凸点（信号）', (0.62, 0.63, 0.64), metallic=1.0, rough=0.3), sig, smooth=True)
pad = C.Mesh(); pad.cyl(13, 1.6, (X_PAD, 0, Z_TOP - 0.8), seg=8); pad.obj('焊盘_信号', M['bump'], sig)
halo = C.Mesh(); halo.cyl(3.2, 0.3, (X_PAD, 0, Z_TOP + 0.1), seg=16); halo.cyl(12.7, 1.2, (X_PAD, 0, Z_BUMP), seg=32); halo.obj('信号落点亮环', out_mat, sig)

# ---------- 周围的连线（环境）：三层直角走线 + 凸点阵列 + 下方的中介层表面 ----------
env = C.collection('环境'); l1 = C.Mesh(); l2 = C.Mesh(); l3 = C.Mesh(); bumps = C.Mesh()
CLR = 36.0                      # 输出通孔和微凸点周围清出一块，观众才看得见信号从哪里离开芯片（示意：真实芯片这里同样布满连线）
def keepout(x, y, lx):          # 信号线和串化电路周围留空
    return ((x - lx / 2 < X_PAD + 16) and abs(y) < 21) or (abs(x - X_PAD) < CLR + lx / 2 and abs(y) < CLR)
for _ in range(1400):
    lx = rnd.uniform(8, 90); x = rnd.uniform(-330, 190); y = round(rnd.uniform(-110, 110)) + 0.5
    if not keepout(x, y, lx): l1.box((lx, 0.45, 0.5), (x, y, 0))
for _ in range(420):
    ly = rnd.uniform(15, 120); x = round(rnd.uniform(-330, 190) / 3) * 3; y = rnd.uniform(-110, 110)
    if not (abs(x - X_PAD) < CLR and abs(y) < CLR + ly / 2): l2.box((1.2, ly, 1.0), (x, y, -3.2))
for k in range(-9, 10):
    y = k * 12.0 + 6.0
    if abs(y) < CLR:
        xa, xb = -350.0, X_PAD - CLR; l3.box((xb - xa, 5.0, 2.0), ((xa + xb) / 2, y, Z_TOP + 1.0))
        xa, xb = X_PAD + CLR, 210.0; l3.box((xb - xa, 5.0, 2.0), ((xa + xb) / 2, y, Z_TOP + 1.0))
    else: l3.box((560, 5.0, 2.0), (-70, y, Z_TOP + 1.0))
for ix in range(-8, 6):
    for iy in range(-3, 4):
        if (ix, iy) == (0, 0): continue
        bumps.sphere(12.5, (X_PAD + ix * 45, iy * 45, Z_BUMP), (1, 1, 0.85), seg=16); bumps.cyl(13, 1.6, (X_PAD + ix * 45, iy * 45, Z_TOP - 0.8), seg=8)
l1.obj('下层细线', M['wire'], env); l2.obj('中层线', M['wire'], env); l3.obj('上层电源线', M['thick'], env); bumps.obj('凸点阵列', M['bump'], env, smooth=True)
C.box('中介层表面', (900, 500, 1.0), (-60, 0, Z_BUMP - 12.5), M['floor'], env)

# ---------- 相机 ----------
# 23.0 s 接 S02 的尾帧：几乎正俯视，数据线在画面里竖着（相机在 −X 一侧朝 +X 看）。
# 23–27.4：沿数据线推到串化电路；27.4–35.5：基本停住（只留很慢的漂移）；35.5–39：跟着输出线到通孔，朝凸点压下去。
cam, tgt = C.add_camera('cam_S03', lens=50, fstop=1.0, clip=(0.05, 5000))
def cam_fn(t):
    a = C.smoother(C.seg(t, 23.0, 27.4)); h = C.seg(t, 27.4, 35.5); b = C.smoother(C.seg(t, 35.5, 38.9))
    fx = C.lerp(-110, 20, a) + 2.0 * h + C.lerp(0, X_PAD - 22, b); fz = C.lerp(0, Z_BUMP + 8, b)
    d = C.loglerp(150, 78, a) * C.lerp(1.0, 0.94, h) * C.loglerp(1.0, 1.25, b)
    el = rad(C.lerp(82, 56, a) + C.lerp(0, -3, h) + C.lerp(0, -22, b)); az = rad(180 + C.lerp(0, -14, a) + C.lerp(0, -6, h) + C.lerp(0, -50, b))
    focus = Vector((fx, 0, fz)); loc = focus + d * Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    return dict(loc=loc, tgt=focus, fstop=50e-3 / (2 * 0.006 * d))
C.animate_camera(cam, tgt, cam_fn, shot)

# ---------- 灯光：冷色主光 + 暖色逆光，底色深蓝（金色只留给信号） ----------
C.world((0.006, 0.010, 0.022), 1.0, hdri='studio_small_09_2k.hdr', hdri_strength=0.18, hdri_rot=rad(120))
C.area_light('主光_冷', (-120, -260, 320), (0, 0, 0), 300, 2.6e6, (0.62, 0.76, 1.0))
C.area_light('逆光_暖', (260, 240, 140), (20, 0, 0), 240, 2.0e6, (1.0, 0.80, 0.60))
C.area_light('底部补光', (X_PAD, -120, 40), (X_PAD, 0, Z_BUMP), 120, 4.0e5, (0.7, 0.8, 1.0))

dev = C.setup_render(args, exposure=0.0)
if args.anchors:
    C.export_anchors(os.path.join(args.out, f'anchors_{shot.id}.json'), shot, cam,
                     {'bus': Vector((-60, 0, 0)), 'serializer': Vector((20, 16, 0)), 'output': Vector((X_DRV1 + 6, 0, 0)), 'bump': Vector((X_PAD, 0, Z_BUMP))})
C.render(args, shot, dev)
