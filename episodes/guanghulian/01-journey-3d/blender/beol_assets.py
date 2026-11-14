# 光互连 01（3D 版）· S02 尾段和 S03 共用的「芯片连线层」资产：几何、材质、灯光、环境光、相机路线。
# 状态：v1 粗模（预演用）。连线层数、线宽、串化电路、凸点形状都是简化示意，不能当最终科学结构交付。
# 为什么要共用：S02 → S03 在 23.0 秒不切。两边必须是同一套几何、同一套材质、同一套灯光和同一条相机路线，
#   所以都从这里取；S03 直接用（1 单位 = 1 µm），S02 把整套东西挂在一个「根」下面，缩到 0.001 倍（1 µm = 0.001 mm）放到落点。
# 局部坐标（单位 µm，和 v0 的 S03 一致）：
#   +X = 信号前进方向（并排数据线 → 串化电路 → 输出驱动 → 微凸点）；+Z 朝硅背面（朝相机）；−Z 朝微凸点和硅中介层。
#   z = 0 是细的下层连线（离相机最近），Z_TOP 是上层厚金属，再往下是微凸点，Z_FLOOR 是硅中介层表面。
# 画的东西：
#   · 32 条并排的数据线（示意画 32 条），每条线整体亮（1）或暗（0），一拍（TW 秒）同时换一排；
#   · 五级二选一树：32 → 16 → 8 → 4 → 2 → 1，每过一级节拍快一倍；
#   · 输出驱动把一路信号变成一对互补的线（差分 P / N）：两根并行的粗线 → 两串通孔 → 两个相邻的微凸点 → 中介层表面的一对走线；
#   · 周围的连线（环境）：一块「瓦片」里的两层直角细线，按网格重复铺开；上层电源线、瓦片之间的粗干线、微凸点阵列、中介层表面。
#   · 不画沿线移动的小球：片内导线只有几十微米，同一时刻整条线几乎等电位（FACTS V9）。
import bpy, math, random
from mathutils import Vector
import common as C

rad = math.radians

# ---------- 节拍 ----------
N = 32; TW = 6.4; TB = TW / N            # 并行一拍 6.4 秒；串行一拍 0.2 秒（5 Hz）。参考架构里这是 GPU 自己的高速接口（PCIe）：
                                         # 每条通道约 320 亿比特每秒、两级电平（亮 / 暗两级是实情）→ 片中慢放约 64 亿倍（「几十亿倍」）
T_WORD = 24.7                            # 某一次「换一排」的时刻（全片秒，落在帧上）。并排数据线在 18.3、24.7、31.1、37.5 秒换排：23.0 秒接缝前后它们不变
RAMP = 2                                 # 亮暗之间的过渡帧数
ON, OFF = 0.55, 0.09                     # 亮 / 暗时的发光强度（暗态不全灭）。亮态不能再高：AgX 下发光越强越发白（试过 0.85：米黄色）
GOLD_SIG = (1.0, 0.38, 0.02)             # 信号金：比 common.GOLD 偏橙、更饱和，AgX 显示出来才是金色（实测 0.55 强度约 #b5781f）
WORDS = [[random.Random(3 + k * 7 + i).random() > 0.5 for i in range(N)] for k in range(8)]

# ---------- 尺寸（µm） ----------
STAGE = 8.0                               # 每一级串化电路沿 X 占 8 µm
X_DRV0, X_DRV1 = 46.0, 58.0               # 输出驱动的起止
PITCH = 45.0; BUMP_R = 12.5               # 微凸点：间距画 45 µm、直径约 25 µm（FACTS V12；真实是 40 µm 上下一档）
X_PAD_P, X_PAD_N = 80.0, 80.0 + PITCH     # 差分对落在沿 X 相邻的两个微凸点上（竖屏画面窄，前后排才能同时看见两个）
PAIR_Y = 1.8; PAIR_W = 2.2                # 差分对两根粗线：中心距 3.6 µm、线宽 2.2 µm（示意）
Z_TOP = -9.0                              # 上层厚金属（焊盘顶面）的高度
Z_PAD0 = Z_TOP - 1.6                      # 焊盘底面 = 芯片朝下的那个面
Z_FLOOR = -36.0                           # 硅中介层表面
Z_BUMP = (Z_PAD0 + Z_FLOOR + 1.4) / 2     # 微凸点中心
CLR = 36.0                                # 输出通孔和这一对微凸点周围清出的净空（示意：真实芯片这里同样布满连线，要加角注）
PZ = (20.0, X_PAD_N + CLR)                # 净空在 X 方向的范围：从串化电路末两级起（相机从这里贴着差分对往下走），到 N 凸点后面
BUS_X0 = -1100.0                          # 并排数据线从远处伸过来（毫米尺度上也看得见这一条）
TILE = (520.0, 220.0); TILE_X0 = -330.0   # 环境连线的「瓦片」：x −330…190、y −110…110；瓦片之间是粗干线
FIELD_X = (-2080.0, 1750.0); FIELD_Y = 1650.0   # 铺开的范围：S02 的「透视窗」最大半径 1.5 mm，都落在里面；−X 一头到芯片边缘（落点离边 2 mm）
SEAM_X = -110.0                           # 23.0 秒相机对准的点（S02 的落点 P 就放在这里）

M = {}
def materials():
    """连线层的全部非信号材质。底色深蓝黑；普通连线暗铜色、不发光；金色只给信号线。"""
    if M: return M
    M['wire'] = C.pbr('普通连线', (0.17, 0.10, 0.062), metallic=1.0, rough=0.5)
    M['thick'] = C.pbr('上层厚金属', (0.16, 0.095, 0.055), metallic=1.0, rough=0.55, noise_scale=0.2, noise_rough=0.1)
    M['cell'] = C.pbr('电路单元', (0.03, 0.05, 0.10), metallic=0.2, rough=0.5, coat=0.2)
    M['gate'] = C.pbr('栅条', (0.10, 0.16, 0.28), metallic=0.6, rough=0.4)
    M['spine'] = C.pbr('瓦片之间的粗干线', (0.10, 0.058, 0.034), metallic=1.0, rough=0.65)
    M['bump'] = C.pbr('凸点', (0.30, 0.31, 0.34), metallic=0.7, rough=0.62)         # 哑光：v0 里凸点的高光从数据线缝里露出来，像「移动的光团」
    M['floor'] = C.pbr('硅中介层表面', (0.016, 0.028, 0.065), metallic=0.3, rough=0.6, noise_scale=0.02, noise_rough=0.08)
    return M

# ---------- 信号：按时间亮暗 ----------
def bit_at(m, j, n):
    """第 m 级（共 m 条线）里逻辑编号 j 的线，在第 n 个串行节拍送的是哪一位。
    并行线（m = 32）显示当前这一排；树里和输出线送的是上一排（先存下来再发），依次是第 j, j+m, j+2m… 位，每位持续 m 个串行节拍。"""
    w, q = divmod(n, N)
    return WORDS[w % len(WORDS)][j] if m == N else WORDS[(w - 1) % len(WORDS)][j + (q // m) * m]

def signal_material(name, m, j, t0, t1, invert=False):
    """发光强度打关键帧：每次变化用 RAMP 帧线性过渡。invert = 差分对里的 N 线（和 P 线互补：一根亮时另一根暗）。"""
    mat = C.emit(name, GOLD_SIG, OFF); sock = mat.node_tree.nodes['Emission'].inputs['Strength']
    val = lambda n: (OFF if bit_at(m, j, n) else ON) if invert else (ON if bit_at(m, j, n) else OFF)
    n0 = math.floor((t0 - 0.5 - T_WORD) / TB / m) * m; n1 = math.ceil((t1 + 0.5 - T_WORD) / TB)
    prev = val(n0); sock.default_value = prev; sock.keyframe_insert('default_value', frame=C.F(T_WORD + n0 * TB))
    for n in range(n0 + m, n1 + 1, m):
        v = val(n)
        if v != prev:
            f = C.F(T_WORD + n * TB)
            sock.default_value = prev; sock.keyframe_insert('default_value', frame=f)
            sock.default_value = v; sock.keyframe_insert('default_value', frame=f + RAMP); prev = v
    C.set_interp(mat.node_tree, 'LINEAR'); return mat

def bitrev(a, bits):
    r = 0
    for _ in range(bits): r = (r << 1) | (a & 1); a >>= 1
    return r
def ypos(m, a): return (a - (m - 1) / 2) * (N / m)      # 第 m 级里第 a 个位置的 y

# ---------- 环境连线的瓦片 ----------
def _tile(kind):
    """一块瓦片里的两层直角细线（随机长度，示意）。kind：'A' 主车道（留出信号通道和凸点周围的净空）、'C' 只留信号通道、'B' 不留。
    三种瓦片用同一个随机种子：线的位置相同，只是 A / C 少掉通道里的那些。"""
    rnd = random.Random(31); m = C.Mesh(); x_lo, x_hi = TILE_X0 + 15, TILE_X0 + TILE[0] - 15; y_hi = TILE[1] / 2 - 15
    pz0, pz1 = PZ
    for _ in range(1300):                               # 最靠近相机的一层：沿 X 的细线，走 1 µm 的轨道
        lx = rnd.uniform(8, 90); x = rnd.uniform(x_lo + lx / 2, x_hi - lx / 2); y = round(rnd.uniform(-y_hi, y_hi - 1)) + 0.5
        chan = abs(y) < 21 and (kind == 'C' or (kind == 'A' and x - lx / 2 < pz1))
        pad = kind == 'A' and abs(y) < CLR and pz0 - lx / 2 < x < pz1 + lx / 2
        if not (chan or pad): m.box((lx, 0.45, 0.5), (x, y, 0))
    for _ in range(400):                                # 下一层：沿 Y 的线，走 3 µm 的轨道
        ly = rnd.uniform(15, 120); x = round(rnd.uniform(x_lo, x_hi) / 3) * 3; y = rnd.uniform(-y_hi + ly / 2, y_hi - ly / 2)
        if not (kind == 'A' and pz0 < x < pz1 and abs(y) < CLR + ly / 2): m.box((1.2, ly, 1.0), (x, y, -3.2))
    return m

def build(t0, t1, name='连线层'):
    """建整套连线层（局部坐标 µm），全部挂在返回的 root 下面、放进返回的集合 col。t0 / t1：这个镜头的起止（全片秒），信号关键帧只打这一段。
    返回 dict：root、col、mat_p / mat_n（差分对两根线的材质）、pts（标注用的局部坐标点）。"""
    materials(); col = C.collection(name); root = C.empty(name + '_根', col=col); objs = []
    def keep(o): o.parent = root; objs.append(o); return o

    # --- 信号线：五级树 ---
    levels = [N >> s for s in range(6)]; mat1 = None
    for s, m in enumerate(levels):
        bits = int(math.log2(m)); w = 0.45 * (1 + 0.3 * s)
        x0 = BUS_X0 if s == 0 else STAGE * (s - 1) + 6.7; x1 = STAGE * s + 4.5 if m > 1 else X_DRV0 + 5.5
        for a in range(m):
            j = bitrev(a, bits); mat = signal_material(f'信号_{m}_{j}', m, j, t0, t1)
            keep(C.box(f'线_{m}_{a}', (x1 - x0, w, 0.5), ((x0 + x1) / 2, ypos(m, a), 0 if m > 1 else 0.3), mat, col))
            if m == 1: mat1 = mat
    cells = C.Mesh(); gates = C.Mesh()                  # 二选一单元（每级 m/2 个），压在两条输入线的汇合处
    for s, m in enumerate(levels[:-1]):
        for a in range(m // 2):
            y = ypos(m // 2, a); span = (N / m) + 0.9; x = STAGE * s + 5.6
            cells.box((2.4, span, 0.9), (x, y, -0.1))
            for g in (-0.7, 0.0, 0.7): gates.box((0.16, span + 0.3, 0.2), (x + g, y, 0.5))
    # --- 输出驱动：两级单端 + 两级差分（示意）。从这里起一路信号变成互补的一对 ---
    for k, (x, wy) in enumerate(((X_DRV0 + 1.5, 2.0), (X_DRV0 + 4.5, 3.2))):
        cells.box((2.4, wy, 1.0), (x, 0, -0.35))
        for g in (-0.6, 0.0, 0.6): gates.box((0.18, wy + 0.4, 0.2), (x + g, 0, -0.25 + 0.5))
    for x in (X_DRV0 + 7.5, X_DRV0 + 10.5):
        for sy in (-1, 1):
            cells.box((2.4, 4.2, 1.0), (x, sy * 2.6, -1.0))
            for g in (-0.6, 0.0, 0.6): gates.box((0.18, 4.6, 0.2), (x + g, sy * 2.6, -0.4))
    keep(cells.obj('电路单元', M['cell'], col, bevel=0.06)); keep(gates.obj('栅条', M['gate'], col))
    # --- 差分输出：P / N 两根并行的粗线 → 两串通孔 → 两个相邻的微凸点 → 中介层表面的一对走线。两根的亮暗互补 ---
    mat_p = signal_material('差分_P', 1, 0, t0, t1); mat_n = signal_material('差分_N', 1, 0, t0, t1, invert=True)
    zl = Z_FLOOR + 0.5
    for mat, sy, xp, yt in ((mat_p, 1, X_PAD_P, PITCH / 2 - 1.9), (mat_n, -1, X_PAD_N, PITCH / 2 + 1.9)):
        y = sy * PAIR_Y; net = C.Mesh()
        net.box((xp + 1.0 - (X_DRV0 + 6.0), PAIR_W, 0.9), ((xp + 1.0 + X_DRV0 + 6.0) / 2, y, 0.3))                 # 粗线：驱动 → 通孔
        for k in range(5): net.box((2.2, 2.2, abs(Z_TOP) / 5 * 0.72), (xp, y, -abs(Z_TOP) * (k + 0.5) / 5))          # 通孔叠层：往 −Z
        net.cyl(3.4, 0.3, (xp, y, Z_TOP + 0.1), seg=16)                                                              # 通孔落在焊盘上的亮点
        net.cyl(BUMP_R + 0.5, 1.2, (xp, 0, Z_BUMP), seg=32)                                                          # 微凸点腰上的亮环
        net.cyl(BUMP_R + 1.6, 0.5, (xp, 0, Z_FLOOR + 0.25), seg=32)                                                  # 中介层上的落点
        net.path([(xp, 0, zl), (xp, yt, zl), (FIELD_X[1], yt, zl)], 2.6, 0.9)                                        # 中介层表面的走线：这一对继续往 +X 走
        keep(net.obj('差分输出_' + ('P' if sy > 0 else 'N'), mat, col))

    # --- 环境连线：瓦片按网格铺开（共享网格，省内存） ---
    tiles = {k: keep(_tile(k).obj('连线瓦片_' + k, M['wire'], col)) for k in 'ABC'}
    ix0 = math.ceil((FIELD_X[0] - TILE_X0) / TILE[0]); ix1 = math.ceil((FIELD_X[1] - TILE_X0) / TILE[0]); iy1 = math.ceil((FIELD_Y - TILE[1] / 2) / TILE[1])
    for ix in range(ix0, ix1):
        for iy in range(-iy1, iy1 + 1):
            if (ix, iy) == (0, 0): continue
            src = tiles['C'] if iy == 0 and BUS_X0 < TILE_X0 + (ix + 1) * TILE[0] and ix < 0 else tiles['B']
            keep(C.instance(src, f'瓦片_{ix}_{iy}', (ix * TILE[0], iy * TILE[1], 0), col=col))
    # --- 上层电源线（沿 X，间距 12 µm）+ 瓦片之间的粗干线（毫米尺度上看得见的大格子） ---
    l3 = C.Mesh(); sp = C.Mesh(); fx0, fx1 = FIELD_X; pz0, pz1 = PZ
    for k in range(-int(FIELD_Y // 12), int(FIELD_Y // 12)):
        y = k * 12.0 + 6.0
        if abs((y + TILE[1] / 2) % TILE[1]) < 22 or abs((y + TILE[1] / 2) % TILE[1] - TILE[1]) < 22: continue    # 让开粗干线
        if abs(y) < CLR:
            l3.box((pz0 - fx0, 5.0, 2.0), ((fx0 + pz0) / 2, y, Z_TOP + 1.0)); l3.box((fx1 - pz1, 5.0, 2.0), ((fx1 + pz1) / 2, y, Z_TOP + 1.0))
        else: l3.box((fx1 - fx0, 5.0, 2.0), ((fx0 + fx1) / 2, y, Z_TOP + 1.0))
    for iy in range(-iy1 - 1, iy1 + 1): sp.box((fx1 - fx0, 30.0, 2.0), ((fx0 + fx1) / 2, (iy + 0.5) * TILE[1], Z_TOP + 1.0))
    for ix in range(ix0, ix1 + 1): sp.box((30.0, 2 * FIELD_Y, 2.0), (TILE_X0 + ix * TILE[0], 0, Z_TOP + 1.0))
    keep(l3.obj('上层电源线', M['thick'], col)); keep(sp.obj('粗干线', M['spine'], col))
    # --- 微凸点阵列（顶点实例）+ 中介层表面 ---
    pts = []; pts_cu = []
    for ix in range(math.ceil((fx0 - X_PAD_P) / PITCH), int((fx1 - X_PAD_P) / PITCH) + 1):
        for iy in range(-int(FIELD_Y // PITCH), int(FIELD_Y // PITCH) + 1):
            p = (X_PAD_P + ix * PITCH, iy * PITCH, 0.0); pts.append(p)
            if not (iy == 0 and ix in (0, 1)): pts_cu.append(p)
    def instancer(nm, verts, unit):
        me = bpy.data.meshes.new(nm); me.from_pydata(verts, [], []); g = C.link(bpy.data.objects.new(nm, me), col); g.instance_type = 'VERTS'
        keep(g); unit.parent = g; objs.append(unit); return g
    b = C.Mesh(); b.sphere(BUMP_R, (0, 0, Z_BUMP), (1, 1, (Z_PAD0 - Z_FLOOR - 1.4) / 2 / BUMP_R), seg=16)
    instancer('凸点阵列', pts, b.obj('凸点单元', M['bump'], col, smooth=True))
    cu = C.Mesh(); cu.cyl(13, 1.6, (0, 0, Z_TOP - 0.8), seg=8); cu.cyl(13, 1.4, (0, 0, Z_FLOOR + 0.7), seg=12); cu.box((8, 3, 0.8), (16, 0, Z_FLOOR + 0.4)); cu.cyl(2.6, 0.8, (21, 0, Z_FLOOR + 0.4), seg=10)
    instancer('焊盘阵列', pts_cu, cu.obj('焊盘单元', M['thick'], col))      # 芯片一侧的焊盘（上层金属，铜色）+ 中介层一侧的焊盘和一小段走线
    pp = C.Mesh()
    for xp in (X_PAD_P, X_PAD_N): pp.cyl(13, 1.6, (xp, 0, Z_TOP - 0.8), seg=8); pp.cyl(13, 1.4, (xp, 0, Z_FLOOR + 0.7), seg=12)
    keep(pp.obj('焊盘_差分', M['thick'], col))
    keep(C.box('中介层表面', (fx1 - fx0 + 300, 2 * FIELD_Y + 300, 1.0), ((fx0 + fx1) / 2, 0, Z_FLOOR - 0.5), M['floor'], col))
    return dict(root=root, col=col, objs=objs, mat_p=mat_p, mat_n=mat_n, mat1=mat1,
                pts={'串化电路旁': Vector((30, -13, 1)), '驱动': Vector((X_DRV0 + 9, 0, 0)),
                     'bump_p': Vector((X_PAD_P, 0, Z_BUMP)), 'bump_n': Vector((X_PAD_N, 0, Z_BUMP))})

# ---------- 灯光和环境光（两边同一套） ----------
# 名字、光从哪个方向来、强度、颜色、投不投影。
# 三盏都不投影：① 实测同一个机位、同一套几何，投影的平行光在 S02（mm、缩 0.001 倍）和 S03（µm）里结果不一样
#   （S02 亮约 8%，差别全在平行光的阴影上，原因没查清；关掉投影后两边平均亮度只差 0.0004）；
#   ② 芯片下面（凸点、中介层）被上面的连线挡着，投影的话是一片黑。层次靠环境光的遮挡和信号线自己的光。正式版要换成能投影的打法再核对。
SUNS = (('连线层主光_冷', (-120, -260, 320), 1.05, (0.62, 0.76, 1.0), False), ('连线层逆光_暖', (260, 240, 140), 0.55, (1.0, 0.80, 0.60), False),
        ('连线层补光_低', (-260, 200, 70), 0.6, (0.70, 0.82, 1.0), False))
def lights(root, link_col=None):
    """平行光（太阳灯）：强度和方向不随缩放和位置变，S02（mm）和 S03（µm）里照出来一样。方向按 root 的朝向换算（root 不动，所以不用挂父子）。
    link_col：只照这个集合、也只让这个集合挡光（S02 里用：不照封装，也不被封装和散热器挡住）。"""
    out = []; ll = None
    if link_col:
        ll = bpy.data.collections.new('灯光链接_只照连线层'); ll.children.link(link_col)
    for nm, src, power, color, shadow in SUNS:
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = power; ld.color = color; ld.angle = rad(18); ld.use_shadow = shadow
        d = root.rotation_euler.to_matrix() @ Vector(src)              # 方向跟着 root 的朝向转；不挂成子物体（不让灯跟着缩放）
        o = C.link(bpy.data.objects.new(nm, ld)); o.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
        if ll: o.light_linking.receiver_collection = ll; o.light_linking.blocker_collection = ll
        out.append(o)
    return out

WORLD = dict(color=(0.012, 0.016, 0.026), strength=1.0, hdri='studio_small_09_2k.hdr', hdri_strength=0.35, hdri_rot=rad(40))
def world(local=False):
    """环境光：S02 用原来的设置；S03（local=True）把 HDRI 转 90°，因为连线层在 S02 里是绕 Z 转了 90° 放的。"""
    w = dict(WORLD)
    if local: w['hdri_rot'] += ROOT_ROT
    return C.world(w.pop('color'), w.pop('strength'), **w)
ROOT_ROT = rad(90)                        # S02 里连线层的朝向：局部 +X（信号方向）= S02 的 +Y（画面里朝上）

# ---------- 相机路线（局部坐标 µm；S03 直接用，S02 尾段换算到 mm 后用同一条） ----------
def hermite(knots, t):
    """分段三次埃尔米特插值：knots = [(t, 值, 斜率或 None), …]；斜率为 None 时取两侧差分。端点之外按端点斜率线性外推。
    值可以是数或 Vector。位置和速度都连续。"""
    ts = [k[0] for k in knots]; n = len(knots)
    def slope(i):
        if knots[i][2] is not None: return knots[i][2]
        a = knots[max(i - 1, 0)]; b = knots[min(i + 1, n - 1)]; return (b[1] - a[1]) / (b[0] - a[0])
    if t <= ts[0]: return knots[0][1] + slope(0) * (t - ts[0])
    if t >= ts[-1]: return knots[-1][1] + slope(n - 1) * (t - ts[-1])
    i = max(k for k in range(n - 1) if ts[k] <= t); h = ts[i + 1] - ts[i]; u = (t - ts[i]) / h
    p0, p1, m0, m1 = knots[i][1], knots[i + 1][1], slope(i) * h, slope(i + 1) * h
    return (2 * u**3 - 3 * u**2 + 1) * p0 + (u**3 - 2 * u**2 + u) * m0 + (-2 * u**3 + 3 * u**2) * p1 + (u**3 - u**2) * m1

V_SEAM = 20.0                             # 23.0 秒相机沿数据线前进的速度（µm/s）
K_SEAM = -0.25                            # 23.0 秒相机距离的对数变化率（每秒）：还在往里推，已经减速
APERTURE = 0.012                          # 光圈直径 / 对焦距离：各个尺度上虚化程度一致
T_HOLD0, T_HOLD1 = 27.4, 35.5             # 相机停在串化电路上方的时段（讲工序时相机不动）

def fstop(lens, d): return lens * 1e-3 / (APERTURE * d)

def orbit(t):
    """23 秒前后到 35.5 秒：相机绕着对焦点的参数（对焦点 x、距离、俯角、方位角、焦距）。t < 23 时按 23 秒的速度往回外推，S02 尾段用。"""
    a = C.smoother(C.seg(t, 23.0, T_HOLD0)); h = C.seg(t, T_HOLD0, T_HOLD1)
    fx = hermite([(23.0, SEAM_X, V_SEAM), (T_HOLD0, 20.0, 0.0)], min(t, T_HOLD0)) + 2.0 * h
    d = math.exp(hermite([(23.0, math.log(150.0), K_SEAM), (T_HOLD0, math.log(64.0), 0.0)], min(t, T_HOLD0)) + math.log(0.94) * h)
    return dict(fx=fx, fz=0.0, d=d, el=C.lerp(82, 56, a) - 3 * h, az=180 - 13 * a + 1 * h, lens=C.lerp(50, 35, a))

def orbit_pose(p):
    el, az = rad(p['el']), rad(p['az']); f = Vector((p['fx'], 0, p['fz']))
    return f + p['d'] * Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))), f

# 35.5–39 秒：从串化电路上方，贴着这一对差分线的一侧一直往下：驱动上方 → 穿过连线层的高度（37.9 秒前后）→ 芯片朝下的面以下，
# 从侧面看见「粗线 → 通孔 → 焊盘 → 微凸点 → 中介层」；39.0 秒在 P 凸点旁边、离中介层约 15 µm，仍在往下。
# 路线基本在一个竖直面里（朝向只变几度，不绕圈）。最后一个点在镜头之外，只用来给出 39 秒的速度。
DESCENT = ((36.3, (12, 12, 34), (56, 1, 0)), (37.1, (30, 17, 22), (72, 2, -4)), (37.7, (40, 20, 8), (82, 2, -12)), (38.2, (47, 22, -9), (88, 2, -17)),
           (38.6, (52, 23, -17), (96, 3, -22)), (39.0, (57, 24, -23), (104, 3, -28)), (39.5, (63, 24.5, -31), (112, 3, -35)))
def micro_cam(t):
    """连线层里的相机（局部坐标 µm）：返回 dict(loc, tgt, lens, fstop)。"""
    if t <= T_HOLD1:
        p = orbit(t); loc, tgt = orbit_pose(p); lens = p['lens']
    else:
        l0, g0 = orbit_pose(orbit(T_HOLD1)); l1, g1 = orbit_pose(orbit(T_HOLD1 - 0.1))
        kl = [(T_HOLD1, l0, (l0 - l1) / 0.1)] + [(tt, Vector(a), None) for tt, a, b in DESCENT]
        kg = [(T_HOLD1, g0, (g0 - g1) / 0.1)] + [(tt, Vector(b), None) for tt, a, b in DESCENT]
        loc = hermite(kl, t); tgt = hermite(kg, t); lens = C.lerp(35, 28, C.smooth(C.seg(t, T_HOLD1, 37.6)))
    return dict(loc=loc, tgt=tgt, lens=lens, fstop=fstop(lens, (loc - tgt).length))

def anchor_pair(t):
    """「差分输出」标注的锚点：先在两根粗线中间，相机往下走时跟着移到两串通孔之间，最后到两个凸点之间。"""
    a = Vector((X_DRV0 + 20, 0, 0.8)); b = Vector((X_PAD_P + 8, 0, Z_TOP / 2)); c = Vector(((X_PAD_P + X_PAD_N) / 2, 0, Z_BUMP))
    return a.lerp(b, C.smooth(C.seg(t, 36.8, 37.8))).lerp(c, C.smooth(C.seg(t, 38.0, 38.9)))

def anchor_bus(t):
    """「并行总线」标注的锚点：贴在并排数据线上、跟着相机走（总在对焦点后面一点），到串化电路前停住。"""
    return Vector((min(orbit(t)['fx'] - 6.0, -4.0), 0, 0.3))
