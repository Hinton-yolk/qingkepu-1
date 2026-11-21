# 一语道破 EP01 · AUDIENCE-FIRST V03：观众吸引力优先的重剪（在 V02 的场景、字块、模型、相机系统上改）。
# 场景时间（本文件里的时间）≠ 成片时间：v03_time.py 把成片时间映射到场景时间（第二幕、第四幕前半压紧）。
# 叙事：
#   钩子（场景 4.4–10.4）  空位上「去 / 睡」抢同一个位置 →「AI 的下一个字，还没定？」→ 镜头拉开：候选和分数是模型刚算出来的
#   第二幕（10.4–19.6）    倒回去：每个字变成一串数 → 穿过大模型 → 下一个位置的候选
#   第三幕（18.4–28.4）    分叉：两条未来从同一个前缀长出来（出门的一句往远处、往高处走；睡懒觉的一句往回卷、躺下）→ 选定「去」
#   第四幕（28.4–49.6）    逐步生成：第 1 步完整；第 2 步强调「海」进了上下文、候选整组换掉；第 3 步缩短 →「下一步，要等上一步确定。」
#                          → 收回，回到同一个起点 →「既然要一步步来，能不能先猜几步？」
#   第五幕（49.6–64.6）    小模型先猜「海边吃饭」→ 同一个大模型一趟带走 4 串数（每个位置只看它前面的字）→ 一趟出来 4 个首选
#                          → 逐位对照：海、边一致；吃 ≠ 看 → 吃、饭退回小模型，「看」从大模型的结果落进空位
#   对照（65.0–74.6）      两排小账本：一步一步 = 大模型 3 轮；先猜再验 = 小模型 4 步 + 大模型 1 轮
#   收尾（74.6–79.0）      回到托盘：周末我想去海边看 + 下一个空位，又有两个候选在抢
# 所有主角从第一帧到最后一帧都是同一批物体；pose(t) 是场景时间的纯函数（每个物体每帧都重新摆）。
import os, math, sys
ANIM_DIR = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(ANIM_DIR, 'lib.py'), encoding='utf-8').read())
sys.path.insert(0, ANIM_DIR)
import v03_time

DUR = 79.0
S, STEP = 0.6, 0.74
TRAY_Z = 0.06; ZT = TRAY_Z + S / 2
ZG = 0.09 + 0.0125 + S / 2
PREFIX = '周末我想'
PX = [-2.96, -2.22, -1.48, -0.74]
OX = [0.0, 0.74, 1.48, 2.22, 2.96]                # 去 海 边 看 （下一个）

# ---------------- 模型 ----------------
NC, CELL, CG = 6, 0.17, 0.19
PLATE_C = (-1.85, 1.45)
GATES = [3.1, 4.0, 4.9]
GXC, GW = 0.0, 7.4                                 # V03：大模型的三道层加宽，左右盖住前缀和后面 4 个位置（推测解码时 4 串数也从这里过）
CY_STOP1, CY_END = 3.1, 5.75
PARKY = CY_END                                     # 算过的一串数停放的那一排（y）
PILX, PILY = [-0.3, 0.45, 1.2], 1.6
CANDS = [('去', 1.0), ('睡', 0.62), ('出', 0.25)]  # 分数为示意
CELL_TO = [0, 0, 0, 1, 1, 2]

# ---------------- 分叉（V03：两条路在空间里走向不同） ----------------
SC = 1.0
def _up_path():
    a = math.radians(34); c, n = math.cos(a), math.sin(a); pts = [(0, 0, ZG), (0.3, 0.05, ZG), (0.62, 0.24, ZG)]
    for d in (0.8, 1.6, 2.4, 3.2, 4.0, 4.7): pts.append((0.62 + c * d, 0.24 + n * d, ZG + 0.17 * max(0, d - 0.6)))   # 出门的一句：往远处、往高处走（像走向海边的坡道）
    return Path(pts)
def _dn_path():
    pts = [(0, 0, ZG), (0.3, -0.05, ZG), (0.6, -0.26, ZG), (1.05, -0.82, ZG), (1.62, -1.28, ZG), (2.28, -1.38, ZG), (2.72, -1.1, ZG), (2.78, -0.62, ZG)]
    return Path(pts)                                 # 睡懒觉的一句：往镜头这边拐，再往回卷（不往远处去）
UP, DN = _up_path(), _dn_path()
def _lower(p, z): return Path([(q[0], q[1], q[2] - (ZG - z)) for q in p.pts[::8]] + [tuple(p.pts[-1])])
UPS, DNS = _lower(UP, 0.09), _lower(DN, 0.13)          # 轨道本身（字块底下的玻璃条）
FUT_U, FUT_D = '海边看日落', '个懒觉'

# ---------------- 第五幕：小模型 ----------------
SMX = (3.3, -1.5)                                  # 小模型：托盘右前方，出字口朝左
SM_OUT = 7.8                                       # 出场前停在画面右外侧
DRAFT = '海边吃饭'; PICKS = '海边看鱼'                # 小模型的草稿 / 大模型每一位的首选（第 4 位接着「吃」算，示意）
ACC = 2

# ---------------- 时间表（场景时间） ----------------
H0 = 4.4                                           # 钩子：第一帧
H_PIL = (7.0, 8.1); H_TOP = [(7.05, 8.05), (7.2, 8.2)]; H_SINK = (8.9, 9.9)
T_UNF = (10.4, 12.0); T_GO1 = (11.9, 12.9); T_REACH = (13.0, 13.6); T_RESP = (13.5, 13.9); T_BACK = (13.8, 14.5); T_UPD = (14.4, 14.9)
T_GO2 = (14.9, 15.9); T_EXIT = (15.9, 17.2); T_PIL = (17.0, 18.3)
T_TRK = (18.4, 19.6); T_C2F = [(18.7, 20.0), (18.95, 20.25)]; T_PDN = (19.6, 20.4)
T_FUT0 = 20.3; T_FU = [20.3, 20.72, 21.1, 21.45, 21.77]; T_FD = [20.55, 21.0, 21.55]; T_FDUR = 0.75
T_SLEEP = (22.2, 22.9)                             # 「觉」躺下
T_PICK = (24.0, 24.8); T_DRET = (24.6, 26.0); T_QU = (25.4, 26.8); T_URET = (27.4, 28.5)
T4_UNF = (28.6, 29.6); T4_GO = (29.5, 31.0); T4_REACH = (31.0, 31.5); T4_RESP = (31.4, 31.8); T4_BACK = (31.6, 32.2); T4_UPD = (32.1, 32.5)
T4_EXIT = (32.5, 33.6); T4_PIL = (33.5, 34.5)
C_LAND = [34.9, 38.1, 40.5]; LAND_D = 0.6          # 三步：海、边、看 落进正式输出
CTXG = [(35.55, 36.5), (38.7, 39.3)]               # 新写定的字并进上下文：前缀和新字一起亮
COLT = [(35.9, 36.9), (38.8, 39.5)]                # 海 / 边 的一串数进大模型
OUTB = [(36.85, 37.45), (39.45, 39.85)]            # 结果从模型出来，回到候选区
SDN = [(37.15, 37.5), (39.65, 39.9), (44.9, 45.4)] # 一组候选沉下去
SUP = [(37.45, 38.0), (39.85, 40.3)]               # 下一组候选长出来（整组都换了）
T_CHAIN = (41.3, 42.7)
T_RW0 = 43.8                                       # 收回：看 → 边 → 海 依次回去
T_SAME = (45.3, 46.9)
SM_IN = (47.3, 48.7)
S5 = 49.6
T_PUSH = [S5 + 0.26 * j for j in range(4)]; PUSH_D = 0.75
T_UNF5 = (S5 + 2.0, S5 + 2.8); T_P2 = (S5 + 2.9, S5 + 4.3)
T_ARC = (S5 + 4.35, S5 + 4.95); T_ARC_OFF = (S5 + 5.8, S5 + 6.2); T_PULSE = S5 + 5.25
T_OUT5 = (S5 + 5.7, S5 + 6.9); T_PK5 = (S5 + 6.75, S5 + 7.2)
T_CMP = [S5 + 8.2, S5 + 8.9, S5 + 9.6]
T_REJ = (S5 + 10.6, S5 + 11.8); T_KAN = (S5 + 11.7, S5 + 12.4)
E0 = S5 + 15.4; EB = E0 + 3.6
T_CLOSE = S5 + 25.0

# ---------------- 第六部分：账本 ----------------
ROWY = [-1.85, -3.35]
GIX, SIX = -1.05, -1.9
LSX = [-0.2, 0.46, 1.12, 1.78]
TALX = GIX                                         # 计数块叠在图标顶上（大模型算一轮叠一块琥珀，小模型算一步叠一块灰）

def hide(o, h):
    o.hide_render = h
    for c in o.children: c.hide_render = h
def off(tk): tk.put((0, 0, -5), scale=0.001); tk.look(alpha=0.0)
def bez(p0, p1, p2, p3, u):
    p0, p1, p2, p3 = Vector(p0), Vector(p1), Vector(p2), Vector(p3)
    return tuple((1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * p1 + 3 * (1 - u) * u ** 2 * p2 + u ** 3 * p3)
def land(z_rest, t, t_land): return z_rest + 0.12 * (1 - back_out(sstep(t_land - 0.1, t_land + 0.25, t)))
def bump(t, c, w): return math.exp(-((t - c) / w) ** 2)

import random
rnd = random.Random(5)
VAL = [[[rnd.uniform(0.14, 0.6) for j in range(NC)] for k in range(4)] for g in range(4)]
UPD = [rnd.uniform(0.2, 0.68) for j in range(NC)]
VD = [[rnd.uniform(0.14, 0.6) for j in range(NC)] for k in range(6)]          # 海 / 边 / 4 个草稿 的一串数（示意）
VD2 = [[rnd.uniform(0.14, 0.6) for j in range(NC)] for k in range(6)]
def shade_col(v):
    s_ = clamp((v - 0.14) / 0.46); a, b = hex3('#E3D6C2'), hex3('#4F535A'); return tuple(a[i] + (b[i] - a[i]) * s_ for i in range(3))

class Col:
    """一串数（6 个小方块）"""
    def __init__(self, name):
        self.c = [(lambda m: (rbox((CELL, CELL, 1.0), (0, 0, 0), bevel=0.03, mat=m), m))(state_mat(f'{name}{j}', '#D9C7AE')) for j in range(NC)]
    def put(self, xc, yc, vals, unf=1.0, glow=0.0, gcol=AMBER_L, sq=1.0, from_y=None, z0=0.065, dz=0.0):
        for j, (c, m) in enumerate(self.c):
            uj = sstep(0.12 * j, 0.5 + 0.1 * j, unf); v = vals[j]; h = max(0.01, v * uj) * sq + 0.001
            y = yc - 0.5 + j * CG
            if from_y is not None: y = lerp(from_y, y, uj)
            c.location = (xc, y, z0 + dz + h / 2); s_ = lerp(0.4, 1, uj) * sq; c.scale = (s_, s_, h)
            c.hide_render = uj < 0.01 or sq < 0.02
            set_state(m, col=shade_col(v), glow=glow, glow_col=gcol, alpha=1.0)
    def at_path(self, path, u, vals, glow=0.0, gcol=AMBER_L, sq=1.0, dx=0.0):
        p = path.at(u * path.L)
        for j, (c, m) in enumerate(self.c):
            h = max(0.01, vals[j]) * sq + 0.001
            c.location = (p[0] + dx, p[1] + (j - 2.5) * CG, p[2] + h / 2 - 0.3); c.scale = (sq, sq, h); c.hide_render = sq < 0.02
            set_state(m, col=shade_col(vals[j]), glow=glow, glow_col=gcol, alpha=1.0)
    def hide(self):
        for c, m in self.c: c.hide_render = True; c.location = (0, 0, -5)
    def to_pillars(self, path, ex, tp, t, vals, glow=0.6):
        """模型的输出：沿外侧路径出来，分头落进三根柱脚，压扁消失（柱子从这里长出来）"""
        for j, (c, m) in enumerate(self.c):
            h = max(0.01, vals[j]); w = Vector(path.at(ex * path.L)) + Vector((0, (j - 2.5) * CG, h / 2 - 0.3)); sc = (1, 1, h); hid = False
            if t > tp:
                uf = sstep(tp + 0.07 * j, tp + 0.07 * j + 0.6, t); pk = CELL_TO[j]; nth = sum(1 for i in range(j) if CELL_TO[i] == pk)
                w = w.lerp(Vector((PILX[pk], PILY, 0.09 + nth * 0.2)), uf); w.z += 0.5 * math.sin(math.pi * uf)
                sq = 1 - sstep(tp + 0.75, tp + 1.05, t); sc = (sq, sq, h * sq + 0.001); hid = sq < 0.02
            c.location = tuple(w); c.scale = sc; c.hide_render = hid
            set_state(m, col=shade_col(vals[j]), glow=glow, glow_col=AMBER_L, alpha=1.0)

def build():
    global rig, prefix, plate, cells, gate_tiles, gate_panes, tubes, beads, pillars, cands, strip_u, strip_d, fut_u, fut_d, slot, slot_m, carrier
    new_scene(); studio_lights((0.2, 0.6, 0.4)); desk(0.0)
    rbox((6.9, 0.95, TRAY_Z * 2), (0.05, 0, 0), bevel=0.04, mat=m_metal('#C9CDD2', 0.42))        # 正式输出托盘
    prefix = [Tok(ch, S, f'p{k}') for k, ch in enumerate(PREFIX)]
    slot = bpy.data.objects.new('slot', None); bpy.context.collection.objects.link(slot)
    slot_m = state_mat('slot', AMBER)
    for (sx, sy, dx, dy) in ((0.66, 0.05, 0, 0.33), (0.66, 0.05, 0, -0.33), (0.05, 0.66, 0.33, 0), (0.05, 0.66, -0.33, 0)):
        b = rbox((sx, sy, 0.03), (dx, dy, 0), bevel=0.012, mat=slot_m); b.parent = slot
    carrier = bpy.data.objects.new('carrier', None); bpy.context.collection.objects.link(carrier)
    gm = state_mat('plate', '#E8E1D6'); set_state(gm, draft=0.22)
    plate = rbox((3.0, 1.35, 0.06), (0, 0, 0.035), bevel=0.03, mat=gm); plate.parent = carrier
    cells = [[(lambda m: (rbox((CELL, CELL, 1.0), (0, 0, 0), bevel=0.03, mat=m), m))(state_mat(f'c{k}{j}', '#D9C7AE')) for j in range(NC)] for k in range(4)]
    for row in cells:
        for c, m in row: c.parent = carrier
    gate_tiles, gate_panes = [], []
    NT = 12
    for gi, gy in enumerate(GATES):
        gmat = m_metal('#BFC4CA', 0.38)
        for dx in (-GW / 2, GW / 2): rbox((0.12, 0.12, 2.4), (GXC + dx, gy, 1.2), bevel=0.04, mat=gmat)
        rbox((GW + 0.12, 0.12, 0.12), (GXC, gy, 2.4), bevel=0.04, mat=gmat)
        pm = state_mat(f'pane{gi}', '#EEF0F0'); set_state(pm, draft=0.7)
        rbox((GW - 0.2, 0.05, 0.85), (GXC, gy, 1.92), bevel=0.02, mat=pm); gate_panes.append(pm)
        tl = []
        for r in range(2):
            for c in range(NT):
                tm = state_mat(f't{gi}{r}{c}', '#575B62' if (r + c + gi) % 3 == 0 else '#D9C7AE')
                rbox((0.3, 0.06, 0.2), (GXC - GW / 2 + 0.5 + c * (GW - 1.0) / (NT - 1), gy - 0.05, 1.72 + r * 0.38), bevel=0.04, mat=tm); tl.append(tm)
        gate_tiles.append(tl)
    tubes, beads = [], []
    for k in range(3):
        x0, x1 = PX[3] - PLATE_C[0], PX[k] - PLATE_C[0]
        pth = Path([(x0, 0.0, 0.62), ((x0 + x1) / 2, 0.0, 1.05 + 0.12 * (3 - k)), (x1, 0.0, 0.62)], n=60)
        am = state_mat(f'tube{k}', TEAL); tb = curve_tube(pth.pts[::2] + [pth.pts[-1]], 0.022, am, poly=True); tb.parent = carrier
        bm = state_mat(f'bead{k}', AMBER_L); bd = sphere(0.075, (0, 0, 0), bm); bd.parent = carrier
        tubes.append((tb, am, pth)); beads.append((bd, bm))
    pillars = []
    for k in range(3):
        pm = state_mat(f'pil{k}', AMBER if k == 0 else '#D6CBB9'); p = rbox((0.5, 0.5, 1.0), (0, 0, 0), bevel=0.06, mat=pm); pillars.append((p, pm))
    cands = [Tok(ch, S, f'cand{k}') for k, (ch, _) in enumerate(CANDS)]
    gu, gd = state_mat('strip_u', '#E4E7E8'), state_mat('strip_d', '#E4E7E8'); set_state(gu, draft=0.55); set_state(gd, draft=0.55)
    strip_u = Grow(UPS, 0.84, gu, thick=0.025, name='strip_u', z=None, s0=0.5)
    strip_d = Grow(DNS, 0.84, gd, thick=0.025, name='strip_d', z=None, s0=0.5)
    fut_u = [Tok(ch, S, f'u{k}') for k, ch in enumerate(FUT_U)]
    fut_d = [Tok(ch, S, f'd{k}') for k, ch in enumerate(FUT_D)]
    rig = Rig(fstop=3.2)
    build_extra()

CS = [[('海', 1.0), ('爬', 0.45), ('吃', 0.3)], [('边', 1.0), ('滩', 0.5), ('上', 0.3)], [('看', 1.0), ('玩', 0.5), ('走', 0.35)]]   # 每一步的候选（分数为示意）
NEWX = 0.0
GO4 = Path([(0.0, 1.0, 0.4), (-0.2, 1.8, 0.9), (NEWX, 2.6, 0.5), (NEWX, PARKY, 0.4)], n=200)
EP4 = Path([(NEWX, PARKY, 0.4), (-0.4, PARKY + 0.2, 2.9), (0.0, 3.9, 3.05), (0.45, 2.5, 1.7), (0.45, 1.9, 0.9)], n=200)
EP = Path([(PX[3], PARKY, 0.4), (-0.6, PARKY + 0.2, 2.9), (0.0, 3.9, 3.05), (0.45, 2.5, 1.7), (0.45, 1.9, 0.9)], n=200)
def go_path(x): return Path([(x, 0.8, 0.4), (x, 1.25, 1.7), (x, 2.2, 2.05), (x, 2.75, 0.6), (x, PARKY, 0.4)], n=200)   # 从候选柱上方越过去
GOS = [go_path(OX[1]), go_path(OX[2])]
def ob_path(x): return Path([(x, PARKY, 0.9), (x - 0.2, PARKY + 0.1, 2.9), (0.5 * (x + PILX[0]), 3.9, 3.05), (PILX[0] + 0.2, 2.4, 1.8), (PILX[0], PILY, 0.5)], n=200)
OBS = [ob_path(OX[1]), ob_path(OX[2])]
def ep5(x): return Path([(x, PARKY, 0.4), (x - 0.25, PARKY + 0.2, 2.9), (x, 3.9, 3.1), (x, 2.2, 2.1), (x, 0.95, ZT + 0.75)], n=200)
EP5 = [ep5(OX[j + 1]) for j in range(4)]
PK = [(OX[j + 1], 0.95, ZT + 0.75) for j in range(4)]

def build_extra():
    global cs, cells4, outs2, outs4, tubes4, beads4, loopbead, loopbead_m, colS, colD, outD, plate2, small, port_m, smlight_m
    global drafts, picks, arcs, ctx_tubes, led, led_panes, led_small_m, ledA, ledB, ledK, tallA, tallB, close_c
    cs = [[Tok(ch, S, f'cs{i}_{k}') for k, (ch, _) in enumerate(row)] for i, row in enumerate(CS)]
    cells4 = Col('n4'); outs2 = Col('o2'); outs4 = Col('o4')
    tubes4, beads4 = [], []
    for k in range(4):
        pth = Path([(NEWX, PARKY, 0.62), ((NEWX + PX[k]) / 2, PARKY, 1.0 + 0.1 * (4 - k)), (PX[k], PARKY, 0.62)], n=60)
        am = state_mat(f'tube4{k}', TEAL); tb = curve_tube(pth.pts[::2] + [pth.pts[-1]], 0.022, am, poly=True)
        bm = state_mat(f'bead4{k}', AMBER_L); bd = sphere(0.075, (0, 0, 0), bm)
        tubes4.append((tb, am, pth)); beads4.append((bd, bm))
    loopbead_m = state_mat('loopbead', AMBER_L); loopbead = sphere(0.11, (0, 0, -5), loopbead_m)
    colS = [Col('s0'), Col('s1')]
    colD = [Col(f'd{j}') for j in range(4)]; outD = [Col(f'od{j}') for j in range(4)]
    g2 = state_mat('plate2', '#E8E1D6'); set_state(g2, draft=0.22); plate2 = rbox((3.0, 1.35, 0.06), (0, 0, 0.035), bevel=0.03, mat=g2)
    # 小模型：一个更小的金属盒子，出字口朝左；顶上一盏灯（每猜一步亮一下：小模型自己也要算）
    small = bpy.data.objects.new('small', None); bpy.context.collection.objects.link(small)
    b = rbox((0.9, 0.9, 0.9), (0, 0, 0.45), bevel=0.14, mat=m_metal('#B9BEC5', 0.32)); b.parent = small
    port_m = state_mat('port', '#3A3D43'); b = rbox((0.05, 0.66, 0.66), (-0.46, 0, 0.42), bevel=0.03, mat=port_m); b.parent = small
    smlight_m = state_mat('smlight', '#D9D4CB'); b = rbox((0.5, 0.5, 0.06), (0, 0, 0.92), bevel=0.03, mat=smlight_m); b.parent = small
    drafts = [Tok(ch, S, f'dr{j}') for j, ch in enumerate(DRAFT)]
    picks = [Tok(ch, S, f'pk{j}') for j, ch in enumerate(PICKS)]
    arcs = []                      # 推测解码：每个位置连到它前面的字（前文 + 它前面的草稿）
    for j in range(4):
        for i in [-1] + list(range(j)):
            x0 = NEWX if i < 0 else OX[i + 1]; x1 = OX[j + 1]; h = 0.95 + 0.22 * abs(x1 - x0)
            pth = Path([(x1, PARKY - 0.05, 0.72), (x1 - 0.15 * (x1 - x0), PARKY - 0.05, h * 0.9), ((x0 + x1) / 2, PARKY - 0.05, h), (x0 + 0.15 * (x1 - x0), PARKY - 0.05, h * 0.9), (x0, PARKY - 0.05, 0.72)], n=80)
            am = state_mat(f'arc{j}{i}', TEAL); tb = curve_tube(pth.pts[::2] + [pth.pts[-1]], 0.02, am, poly=True); arcs.append((j, i, tb, am))
    # 账本：两排，各一个大模型小图标（三道层的缩影）、产出的字、计数块
    led = bpy.data.objects.new('ledger', None); bpy.context.collection.objects.link(led)
    bm_ = state_mat('ledbase', '#E9E4DB'); set_state(bm_, draft=0.15)
    fm = m_metal('#BFC4CA', 0.36); led_panes = []
    for r, y in enumerate(ROWY):
        b = rbox((4.6, 0.9, 0.04), (-0.05, y, 0.02), bevel=0.02, mat=bm_); b.parent = led
        for dx in (-0.34, 0.34):
            b = rbox((0.06, 0.06, 0.72), (GIX + dx, y, 0.36), bevel=0.02, mat=fm); b.parent = led
        b = rbox((0.74, 0.06, 0.06), (GIX, y, 0.72), bevel=0.02, mat=fm); b.parent = led
        pm = state_mat(f'ledpane{r}', '#EEF0F0'); set_state(pm, draft=0.6); b = rbox((0.6, 0.03, 0.42), (GIX, y, 0.44), bevel=0.01, mat=pm); b.parent = led; led_panes.append(pm)
    led_small_m = state_mat('ledsmall', '#D9D4CB')
    b = rbox((0.4, 0.4, 0.4), (SIX, ROWY[1], 0.2), bevel=0.07, mat=m_metal('#B9BEC5', 0.32)); b.parent = led
    b = rbox((0.24, 0.24, 0.04), (SIX, ROWY[1], 0.41), bevel=0.02, mat=led_small_m); b.parent = led
    LS = S
    ledA = [Tok(ch, LS, f'la{k}') for k, ch in enumerate('海边看')]
    ledB = [Tok(ch, LS, f'lb{k}') for k, ch in enumerate('海边吃饭')]; ledK = Tok('看', LS, 'lk')
    tallA = [(lambda m: (rbox((0.26, 0.26, 0.1), (0, 0, 0), bevel=0.03, mat=m), m))(state_mat(f'ta{k}', AMBER)) for k in range(3)]
    tallB = [(lambda m: (rbox((0.26, 0.26, 0.1), (0, 0, 0), bevel=0.03, mat=m), m))(state_mat('tb0', AMBER))] + \
            [(lambda m: (rbox((0.15, 0.15, 0.07), (0, 0, 0), bevel=0.02, mat=m), m))(state_mat(f'tb{k}', '#9AA1A9')) for k in range(1, 5)]
    close_c = [Tok('日', S, 'cl0'), Tok('浪', S, 'cl1')]

def tracked():
    d = {'想': prefix[3].root, '去': cands[0].root, '睡': cands[1].root}
    d.update({f'草稿{ch}': t.root for ch, t in zip(DRAFT, drafts)}); d['首选看'] = picks[2].root; d['小模型'] = small
    return d

def carrier_y(t):
    y = lerp(PLATE_C[1], CY_STOP1, sstep(*T_GO1, t)); return lerp(y, CY_END, sstep(*T_GO2, t))
def cell_val(k, j, cy, t):
    v = VAL[0][k][j]
    if k == 3: v = lerp(v, UPD[j], sstep(*T_UPD, t))
    for gi in (1, 2): v = lerp(v, VAL[gi + 1][k][j], sstep(GATES[gi] - 0.1, GATES[gi] + 0.25, cy))
    return v
def p2_y(t): return lerp(PLATE_C[1], PARKY, sstep(*T_P2, t))

# ======================================================================
def pose(t):
    ANCH.clear()
    for k, tk in enumerate(prefix): tk.put((PX[k], 0, ZT)); tk.look()
    flows = []                                                     # 正在穿过大模型的东西的 y（层被穿过时亮）

    # ---------- 第二幕：每个字变成一串数 → 进模型 → 回看前文 → 穿过各层（「想」那串留在模型里，结果另走） ----------
    cy = carrier_y(t); carrier.location = (PLATE_C[0], cy, 0.0)
    if T_GO1[0] < t < T_GO2[1]: flows.append(cy)
    unf = [sstep(T_UNF[0] + 0.25 * k, T_UNF[0] + 0.25 * k + 0.9, t) for k in range(4)]
    pv = sstep(T_UNF[0], T_UNF[0] + 0.4, t); plate.scale = (lerp(0.2, 1, pv), lerp(0.2, 1, pv), 1); plate.hide_render = pv < 0.01
    for k in range(4):
        for j in range(NC):
            c, m = cells[k][j]
            uj = sstep(0.12 * j, 0.5 + 0.1 * j, unf[k]); v = cell_val(k, j, cy, t); h = max(0.01, v * uj)
            loc = Vector((PX[k] - PLATE_C[0], lerp(0.3 - cy, -0.5 + j * CG, uj), 0.065 + h / 2)); sc = (lerp(0.4, 1, uj), lerp(0.4, 1, uj), h)
            glow, gcol = 0.0, AMBER_L
            for gy in GATES[1:]: glow += 1.4 * math.exp(-((cy - gy) / 0.3) ** 2)
            if k < 3: glow += 1.6 * math.sin(math.pi * sstep(*T_RESP, t))
            if k == 3:
                glow += 2.2 * math.sin(math.pi * sstep(*T_UPD, t)); gcol = TEAL if T_UPD[0] < t < T_UPD[1] else AMBER_L
                if T_UPD[0] < t < T_UPD[1]: sc = (sc[0] * (1 + 0.15 * math.sin(math.pi * sstep(*T_UPD, t))), sc[1], sc[2])
            if k < 3 and T_RESP[0] < t < T_RESP[1]: sc = (sc[0], sc[1], sc[2] * (1 + 0.18 * math.sin(math.pi * sstep(*T_RESP, t))))
            # 之后被连到时（第四幕回看前文 / 第五幕集中评估）亮一下
            glow += 1.6 * math.sin(math.pi * sstep(*T4_RESP, t)) + 1.4 * bump(t, T_PULSE, 0.3) * (1 if k == 3 else 0.6)
            if T4_RESP[0] < t < T4_RESP[1] or abs(t - T_PULSE) < 0.6: gcol = TEAL if t > S5 else AMBER_L
            c.location = loc; c.scale = sc; c.hide_render = uj < 0.01
            set_state(m, col=shade_col(v), glow=glow, glow_col=gcol, alpha=1.0)
    if t >= T_EXIT[0] and t < T_PIL[1] + 0.2: outs2.to_pillars(EP, sstep(*T_EXIT, t), T_PIL[0], t, [cell_val(3, j, CY_END, t) for j in range(NC)])
    else: outs2.hide()
    for k, ((tb, am, pth), (bd, bm)) in enumerate(zip(tubes, beads)):
        grow = sstep(T_REACH[0] + 0.12 * k, T_REACH[1] + 0.12 * k, t); ret = sstep(T_UPD[0] - 0.05, T_UPD[1], t)
        tb.data.bevel_factor_end = max(0.001, grow); tb.data.bevel_factor_start = min(0.999, ret * grow); tb.hide_render = grow < 0.01 or ret > 0.99
        set_state(am, glow=1.6, glow_col=TEAL)
        ub = sstep(T_BACK[0] + 0.1 * k, T_BACK[1] - 0.2 + 0.1 * k, t); bd.location = pth.at((1 - ub) * pth.L); bd.hide_render = not (0.0 < ub < 1.0)
        set_state(bm, glow=3.0, glow_col=AMBER_L)

    pose_pillars(t)
    pose_hook_and_fork(t)
    pose_act4(t, flows)
    pose_act5(t, flows)
    pose_ledger(t)
    pose_close(t)

    # 层：有东西穿过时亮
    for gi, gy in enumerate(GATES):
        near = sum(math.exp(-((y - gy) / 0.5) ** 2) for y in flows)
        if gi == 0: near += (0.4 + 0.6 * sstep(T_REACH[0], T_UPD[1], t) * (1 - sstep(T_UPD[1], T_GO2[0] + 0.4, t))) * math.exp(-((cy - gy) / 0.5) ** 2) * (T_GO1[0] < t < T_GO2[1])
        near += 0.5 * sstep(H_PIL[0], H_PIL[0] + 0.4, t) * (1 - sstep(H_SINK[0], H_SINK[1], t))      # 钩子：候选出现时，后面的模型微微亮
        near += 1.2 * bump(t, T_PULSE, 0.35)
        for i, tm in enumerate(gate_tiles[gi]): set_state(tm, glow=1.5 * min(1.3, near) * (0.6 + 0.4 * math.sin(t * 9 + i)), glow_col=AMBER_L)

    # 「下一个位置」框
    idx = sstep(T_QU[1] - 0.2, T_QU[1] + 0.3, t)
    for i in range(3): idx += sstep(C_LAND[i] + LAND_D - 0.2, C_LAND[i] + LAND_D + 0.3, t) - sstep(T_RW0 + 0.25 * (2 - i), T_RW0 + 0.25 * (2 - i) + 0.4, t)
    idx += sstep(T_CMP[0] + 0.6, T_CMP[0] + 1.0, t) + sstep(T_CMP[1] + 0.6, T_CMP[1] + 1.0, t) + sstep(T_KAN[1] - 0.2, T_KAN[1] + 0.3, t)
    slot.location = (OX[0] + idx * STEP, 0, TRAY_Z + 0.015)
    pulse = 0.5 + 0.5 * math.sin(t * 4)
    set_state(slot_m, glow=(1.0 + 0.8 * pulse), alpha=1.0)

    anchors(t, cy)
    rig.set(*cam(t))

# ---------------------------------------------------------------- 柱子（钩子 / 第二幕 / 第四幕三组）
def set_heights(t):
    """返回 (当前是哪组候选, [三根柱子的高度], 柱子是否在) """
    if t < 10.4:
        g = back_out(sstep(*H_PIL, t), 1.1) if t > H_PIL[0] else 0.0; d = sstep(*H_SINK, t)
        return 'h', [1.5 * CANDS[k][1] * g * (1 - d) for k in range(3)], g * (1 - d)
    if t < 28.0:
        g = back_out(sstep(T_PIL[0] + 0.55, T_PIL[1], t), 1.1) if t > T_PIL[0] + 0.55 else 0.0; pd = sstep(*T_PDN, t)
        return 'b', [1.5 * CANDS[k][1] * g * (1 - pd) for k in range(3)], g * (1 - pd)
    if t < SUP[0][0]:
        g = back_out(sstep(T4_PIL[0] + 0.4, T4_PIL[1], t), 1.1) if t > T4_PIL[0] + 0.4 else 0.0; s, d = 0, sstep(*SDN[0], t)
    elif t < SUP[1][0]:
        g = back_out(sstep(*SUP[0], t), 1.1); s, d = 1, sstep(*SDN[1], t)
    else:
        g = back_out(sstep(*SUP[1], t), 1.1); s, d = 2, sstep(*SDN[2], t)
    return s, [1.5 * CS[s][k][1] * g * (1 - d) for k in range(3)], g * (1 - d)

def pose_pillars(t):
    s, H, vis = set_heights(t)
    for k, (p, pm) in enumerate(pillars):
        h = max(0.02, H[k]); p.location = (PILX[k], PILY, h / 2)
        b = 0.0
        if isinstance(s, int) and k == 0: b = sum(bump(t, C_LAND[i] + 0.05, 0.15) for i in range(3))
        p.scale = (1 + 0.1 * b, 1 + 0.1 * b, h); p.hide_render = H[k] < 0.03
        set_state(pm, glow=(0.8 + 1.6 * b) * (k == 0) * min(1, vis * 1.5), glow_col=AMBER)

# ---------------------------------------------------------------- 钩子 + 第二幕的候选 + 分叉
def hover(k, t, cx):
    """两个候选抢同一个空位：轮流往空位里探，又被另一个挤开（谁也没落定）"""
    ph = 2 * math.pi * 0.85 * (t - H0) + (0 if k == 0 else math.pi)
    lean = 0.5 + 0.5 * math.sin(ph)
    side = -1 if k == 0 else 1
    rx, ry = 0.75, 0.66                                            # 镜头的「右」方向：两个候选在画面上一左一右
    d = side * lerp(0.62, 0.22, lean)
    x = cx + 0.32 + d * rx; y = -0.55 + d * ry + 0.06 * math.sin(ph * 0.5 + k)          # 悬在空位的正上方偏前，不和前一个字叠在一起
    z = ZT + lerp(1.15, 0.7, lean) + 0.06 * math.sin(2 * ph)
    return (x, y, z), side * lerp(0.0, -0.3, lean)

def pose_hook_and_fork(t):
    s, H, vis = set_heights(t)
    pick = sstep(*T_PICK, t)
    for k, tk in enumerate(cands):
        top = (PILX[k], PILY, (H[k] if isinstance(s, str) else 0) + S / 2 + 0.03)
        if t < 10.4:                                               # ---- 钩子 ----
            if k == 2:
                g = sstep(H_TOP[0][0] + 0.3, H_TOP[0][1], t) * (1 - sstep(H_SINK[0], H_SINK[0] + 0.5, t))
                if g < 0.01: off(tk)
                else: tk.put(top, scale=g); tk.look(draft=1.0)
                continue
            hp, roll = hover(k, t, OX[0])
            u = sstep(*H_TOP[k], t)
            pos = bez(hp, (hp[0], hp[1] + 0.3, hp[2] + 0.6), (top[0], top[1] - 0.3, top[2] + 0.9), top, u) if u > 0 else hp
            sq = 1 - sstep(H_SINK[0] + 0.1 * k, H_SINK[0] + 0.1 * k + 0.6, t)
            if sq < 0.02: off(tk); continue
            tk.put(pos, roll=roll * (1 - u), scale=sq); tk.look(draft=1.0, glow=0.5 * (1 - u) * (0.5 + 0.5 * math.sin(t * 6 + k * 3)), glow_col=AMBER_L)
            continue
        if t < T_PIL[0] + 0.55: off(tk); continue
        if t >= 28.0 and k != 0: off(tk); continue
        g = sstep(T_PIL[0] + 0.55, T_PIL[1], t)
        if k == 2:
            sc_ = g * (1 - sstep(T_PDN[0] + 0.4, T_PDN[1], t))
            if sc_ < 0.01: off(tk)
            else: tk.put(top, scale=sc_); tk.look(draft=1.0)
            continue
        path = UP if k == 0 else DN
        u = sstep(*T_C2F[k], t)
        if u <= 0: tk.put(top, scale=max(0.001, g)); tk.look(draft=1.0); continue
        fs = path.at(SC)
        pos = bez(top, (top[0], top[1] - 0.2, top[2] + 0.9), (fs[0], fs[1] + 0.3 * (1 if k == 0 else -1), fs[2] + 0.9), fs, u)
        yaw = yaw_of(path.tan(SC)) * 0.35 * u
        if k == 0:
            bq = sstep(*T_QU, t)
            if t >= T_QU[0]:
                s_ = SC * (1 - bq); pp = path.at(s_); hop = 0.4 * math.sin(math.pi * bq)
                pos = (pp[0], pp[1], pp[2] + hop) if bq < 0.85 else (0.0, 0.0, land(ZT, t, T_QU[1]))
                yaw = yaw_of(path.tan(max(s_, 0.01))) * 0.35 * (1 - bq)
            # 之后一直是正式输出里的「去」；第四幕和第五幕的「同一个起点」会亮
            if t > T_QU[1] + 0.5: pos = (0.0, 0.0, ZT); yaw = 0.0
            gl = 1.4 * pick * (1 - 0.8 * bq) + same_glow(4, t)
            tk.put(pos, yaw=yaw); tk.look(draft=1.0 - bq, glow=gl, glow_col=AMBER_L if t > 28 else AMBER)
        else:
            r = sstep(T_DRET[0] + 0.7, T_DRET[1], t)
            if r >= 0.999: off(tk); continue
            if r > 0:
                hole = (PILX[1], PILY, ZT - 0.1)
                pos = bez(fs, (fs[0], fs[1] - 0.3, fs[2] + 0.9), (hole[0], hole[1] - 0.2, hole[2] + 1.2), hole, r)
                if r > 0.85: pos = (hole[0], hole[1], lerp(hole[2], -0.6, sstep(0.85, 1.0, r)))
                yaw *= 1 - r
            tk.put(pos, yaw=yaw); tk.look(draft=1.0)

    # ---- 分叉：两条路从同一个分叉口长出去；每个字从前一个字里「冒」出来，沿各自的路往前跳 ----
    gtr = sstep(*T_TRK, t); dret = sstep(*T_DRET, t); uret = sstep(*T_URET, t)
    su = 0.55 + gtr * (UPS.L - 0.55); sd = 0.55 + gtr * (DNS.L - 0.55)
    if t > T_URET[0]: su = 0.55 + (UPS.L - 0.55) * (1 - uret)
    if t > T_DRET[0]: sd = 0.55 + (DNS.L - 0.55) * (1 - dret)
    strip_u.show(su if gtr > 0 and uret < 0.999 else 0); strip_d.show(sd if gtr > 0 and dret < 0.999 else 0)
    set_state(strip_u.mat, glow=0.35 * pick * (1 - sstep(*T_QU, t)), glow_col=AMBER_L)
    for path, toks, side, T0 in ((UP, fut_u, 0, T_FU), (DN, fut_d, 1, T_FD)):
        for k, tok in enumerate(toks):
            t0 = T0[k]
            if t < t0: off(tok); continue
            u = sstep(t0, t0 + T_FDUR, t)
            s0, s1 = SC + k * STEP, SC + (k + 1) * STEP
            a = Vector(path.at(s0)); b = Vector(path.at(s1))
            lift = 0.75 if side == 0 else 0.5
            p = bez(a, a + Vector((0, 0, lift)), b + Vector((0, 0, lift * 0.7)), b, back_out(u, 0.9) if u < 1 else 1.0)
            scl = lerp(0.3, 1.0, back_out(sstep(t0, t0 + 0.45, t), 2.0))
            yaw = yaw_of(path.tan(lerp(s0, s1, u))) * 0.35; pitch = 0.0; roll = 0.0
            if side == 0:                                            # 爬坡：字块跟着路面微微仰起
                pitch = -0.1 * min(1.0, k / 3)
            if side == 1 and k == 2:                                 # 「觉」躺下
                roll = -1.35 * back_out(sstep(*T_SLEEP, t), 1.2)
            rt = sstep(T_DRET[0] + 0.12 * (len(toks) - 1 - k), T_DRET[0] + 0.12 * (len(toks) - 1 - k) + 0.5, t) if side else \
                 sstep(T_URET[0] + 0.1 * (len(toks) - 1 - k), T_URET[0] + 0.1 * (len(toks) - 1 - k) + 0.7, t)
            if rt >= 0.999: off(tok); continue
            if rt > 0:
                back = Vector(path.at(SC)); p = tuple(Vector(p).lerp(back, ease(rt))); scl *= 1 - 0.95 * sstep(0.3, 0.95, rt); roll *= 1 - rt
            tok.put(tuple(p), yaw=yaw, pitch=pitch, roll=roll, scale=max(0.001, scl))
            gl = 0.0
            if side == 0 and k == 3: gl = 1.2 * sstep(t0 + 0.4, t0 + 0.9, t) * (1 - uret)          # 「日」：一点暖光
            if side == 0: gl += 0.35 * pick * (1 - uret)
            tok.look(draft=1.0 - (0.25 if side == 0 else 0.0) * pick * 0, alpha=1.0, glow=gl, glow_col=AMBER_L)

def same_glow(k, t):
    """回到同一个起点：周末我想去 依次亮一下（k=4 是「去」）"""
    return 1.4 * math.sin(math.pi * sstep(T_SAME[0] + 0.14 * k, T_SAME[0] + 0.14 * k + 0.9, t)) if T_SAME[0] < t < T_SAME[1] + 0.2 else 0.0

# ---------------------------------------------------------------- 第四幕
def pose_act4(t, flows):
    # 「去」那串数：在它身后展开 → 进模型 → 停在已有那几串旁边（留着）；结果另走（outs4）→ 候选
    un = sstep(*T4_UNF, t); go = sstep(*T4_GO, t)
    if t < T4_UNF[0]: cells4.hide()
    else:
        v4 = [lerp(VAL[0][3][(j + 2) % NC] * 0.9 + 0.05, UPD[(j + 3) % NC], sstep(*T4_UPD, t)) for j in range(NC)]
        gl = 2.2 * math.sin(math.pi * sstep(*T4_UPD, t)) + 1.4 * bump(t, T_PULSE, 0.3)
        if go <= 0: cells4.put(OX[0], 1.0, v4, unf=un, from_y=0.3, glow=gl, gcol=TEAL)
        else:
            q = GO4.at(go * GO4.L); cells4.put(q[0], q[1], v4, glow=gl, gcol=TEAL, dz=q[2] - 0.4)
            if go < 1: flows.append(q[1])
    if T4_EXIT[0] <= t < T4_PIL[1] + 0.2: outs4.to_pillars(EP4, sstep(*T4_EXIT, t), T4_PIL[0], t, [UPD[(j + 3) % NC] for j in range(NC)])
    else: outs4.hide()
    for k, ((tb, am, pth), (bd, bm)) in enumerate(zip(tubes4, beads4)):
        grow = sstep(T4_REACH[0] + 0.08 * k, T4_REACH[1] + 0.08 * k, t); ret = sstep(T4_UPD[0] - 0.05, T4_UPD[1], t)
        tb.data.bevel_factor_end = max(0.001, grow); tb.data.bevel_factor_start = min(0.999, ret * grow)
        tb.hide_render = grow < 0.01 or ret > 0.99; set_state(am, glow=1.6, glow_col=TEAL)
        ub = sstep(T4_BACK[0] + 0.08 * k, T4_BACK[1] - 0.15 + 0.08 * k, t)
        bd.location = pth.at((1 - ub) * pth.L); bd.hide_render = not (0.0 < ub < 1.0); set_state(bm, glow=3.0, glow_col=AMBER_L)

    # 三组候选：每组的冠军落进正式输出；落定之后，这个字并进上下文、它的一串数进模型，候选整组换掉
    s, H, vis = set_heights(t)
    for i in range(3):
        for k, tk in enumerate(cs[i]):
            top = (PILX[k], PILY, (H[k] if s == i else 0) + S / 2 + 0.03)
            if t < 28.0 or s != i and not (k == 0 and t >= C_LAND[i]):
                if not (k == 0 and t >= C_LAND[i]): off(tk); continue
            if k > 0:
                sc_ = vis if s == i else 0.0
                if sc_ < 0.02: off(tk)
                else: tk.put(top, scale=sc_); tk.look(draft=1.0)
                continue
            # 冠军
            c0 = C_LAND[i]; dst = (OX[i + 1], 0.0, ZT)
            if t < c0:
                tk.put(top, scale=max(0.001, vis)); tk.look(draft=1.0, glow=0.8 * vis, glow_col=AMBER_L); continue
            u = sstep(c0, c0 + LAND_D, t); top0 = (PILX[0], PILY, 1.5 + S / 2 + 0.03)
            pos = bez(top0, (top0[0], top0[1] - 0.4, top0[2] + 0.6), (dst[0], dst[1] + 0.4, dst[2] + 1.0), dst, u)
            if u >= 1: pos = (dst[0], dst[1], land(ZT, t, c0 + LAND_D))
            rw0 = T_RW0 + 0.25 * (2 - i); rwi = sstep(rw0, rw0 + 0.8, t)
            if rwi >= 0.999: off(tk); continue
            if rwi > 0: pos = bez(dst, (dst[0], dst[1] + 0.3, dst[2] + 0.8), (PILX[0], PILY - 0.2, 1.6), (PILX[0], PILY, 0.3), rwi)
            gl = 0.6 * (1 - u)
            if i < 2: gl += 1.6 * math.sin(math.pi * sstep(*CTXG[i], t)) if CTXG[i][0] < t < CTXG[i][1] else 0.0
            gl += 1.5 * math.sin(math.pi * sstep(T_CHAIN[0] + 0.35 * i, T_CHAIN[0] + 0.35 * i + 0.7, t)) if T_CHAIN[0] < t < T_CHAIN[1] + 0.4 else 0.0
            tk.put(pos, scale=max(0.001, 1 - sstep(0.45, 0.85, rwi))); tk.look(draft=lerp(1.0, 0.0, sstep(0.3, 1.0, u)), glow=gl, glow_col=TEAL if (i < 2 and CTXG[i][0] < t < CTXG[i][1]) else AMBER_L)
    # 新写定的字并进上下文：前缀一起亮（青）
    for i in range(2):
        if CTXG[i][0] < t < CTXG[i][1]:
            g = 1.0 * math.sin(math.pi * sstep(*CTXG[i], t))
            for tk in prefix: tk.look(glow=g, glow_col=TEAL)
            for j in range(i): cs[j][0].look(glow=g, glow_col=TEAL)
    if T_SAME[0] < t < T_SAME[1] + 0.2:
        for k, tk in enumerate(prefix): tk.look(glow=same_glow(k, t), glow_col=AMBER_L)
    # 海 / 边 的一串数：展开 → 进模型 → 停在「去」那串旁边；收回时一起缩掉（回到同一个起点）
    for i in range(2):
        a, b = COLT[i]; x = OX[i + 1]; vals = VD[i]; sq = 1 - sstep(T_RW0, T_RW0 + 0.6, t)
        if t < a or sq < 0.02: colS[i].hide(); continue
        uf = sstep(a, a + 0.35, t); go = sstep(a + 0.3, b, t)
        if go <= 0: colS[i].put(x, 1.0, vals, unf=uf, from_y=0.3, glow=1.2, gcol=TEAL)
        else:
            q = GOS[i].at(go * GOS[i].L); colS[i].put(q[0], q[1], vals, glow=1.2 * (1 - go) + 1.4 * bump(t, b + 0.1, 0.25), gcol=TEAL, dz=q[2] - 0.4, sq=sq)
            if go < 1: flows.append(q[1])
    # 每一步的结果：一颗光珠从模型里出来，回到候选区（候选整组换掉）
    lb = None
    for i in range(2):
        u = sstep(*OUTB[i], t)
        if 0 < u < 1: lb = OBS[i].at(u * OBS[i].L)
    loopbead.location = lb if lb else (0, 0, -5); loopbead.hide_render = lb is None; set_state(loopbead_m, glow=3.5, glow_col=AMBER_L)

# ---------------------------------------------------------------- 第五幕：先猜，再一趟验
def pose_act5(t, flows):
    sm = sstep(*SM_IN, t) * (1 - sstep(E0 - 1.8, E0 - 0.6, t)); small.location = (lerp(SM_OUT, SMX[0], sm), SMX[1], 0.0); hide(small, sm <= 0.0)
    push = sum(bump(t, tp + 0.05, 0.1) for tp in T_PUSH) + 0.8 * bump(t, T_REJ[1] - 0.05, 0.15)
    small.scale = (1 - 0.06 * push, 1, 1 + 0.05 * push)
    set_state(port_m, glow=3.0 * push, glow_col=AMBER_L); set_state(smlight_m, glow=2.6 * sum(bump(t, tp + 0.1, 0.12) for tp in T_PUSH), glow_col=AMBER_L)
    port = (SMX[0] - 0.55, SMX[1], 0.42)
    rej = sstep(*T_REJ, t)
    for j, tk in enumerate(drafts):
        if t < T_PUSH[j]: off(tk); continue
        u = sstep(T_PUSH[j], T_PUSH[j] + PUSH_D, t); hv = (OX[j + 1], 0.0, ZT + 0.14)
        pos = list(bez(port, (port[0] - 0.4, port[1], port[2] + 0.9), (hv[0] + 0.3, hv[1] - 0.6, hv[2] + 1.0), hv, u))
        if u >= 1: pos = [hv[0], hv[1], hv[2] + 0.04 * math.sin(t * 3 + j)]
        scl = lerp(0.5, 1.0, sstep(T_PUSH[j], T_PUSH[j] + 0.25, t)); draft, glow, gcol, pitch = 1.0, 0.0, TEAL, 0.0
        if j < ACC:
            c0 = T_CMP[j]; mg = sstep(c0 + 0.45, c0 + 0.75, t)
            glow = 2.0 * math.sin(math.pi * sstep(c0 + 0.4, c0 + 1.0, t)) if c0 + 0.4 < t < c0 + 1.0 else 0.0
            draft = 1.0 - sstep(c0 + 0.55, c0 + 0.95, t)
            if t > c0 + 0.6: pos = [hv[0], hv[1], land(ZT, t, c0 + 0.85) if t < c0 + 1.3 else ZT]
            glow += same_glow(5 + j, t) * 0
        else:
            c0 = T_CMP[2]
            if j == ACC:
                r = sstep(c0 + 0.4, c0 + 0.7, t); glow = 1.8 * r * (1 - rej); gcol = AMBER
                pos[0] += 0.07 * math.sin(t * 50) * math.sin(math.pi * sstep(c0 + 0.4, c0 + 1.0, t)); pos[2] -= 0.1 * r
            else:
                pitch = -0.32 * sstep(c0 + 0.7, c0 + 1.0, t)
            if rej > 0:
                q = (port[0] + 0.1, port[1], port[2])
                pos = list(bez(tuple(pos), (pos[0], pos[1] - 0.5, pos[2] + 0.8), (q[0] - 0.6, q[1] - 0.2, q[2] + 0.9), q, ease(sstep(0.0 + 0.12 * (j - 2), 0.88 + 0.12 * (j - 2), rej))))
                scl *= 1 - 0.9 * sstep(0.75, 1.0, rej); pitch *= 1 - rej
                if rej >= 0.999: off(tk); continue
        tk.put(tuple(pos), pitch=pitch, scale=max(0.001, scl)); tk.look(draft=draft, glow=glow, glow_col=gcol)
    # 4 个草稿的一串数：一起展开 → 一块托板一趟带进大模型 → 停在前文那一排
    up = sstep(*T_UNF5, t); py = p2_y(t)
    plate2.location = (1.85, py, 0.0); pv = sstep(T_UNF5[0], T_UNF5[0] + 0.4, t); plate2.scale = (lerp(0.2, 1, pv), lerp(0.2, 1, pv), 1); plate2.hide_render = pv < 0.01
    if T_P2[0] < t < T_P2[1]: flows.append(py)
    for j in range(4):
        sq = 1 - (sstep(T_REJ[0], T_REJ[0] + 0.6, t) if j >= ACC else 0.0)
        if t < T_UNF5[0] or sq < 0.02: colD[j].hide(); continue
        vals = [lerp(VD[2 + j][k], VD2[2 + j][k], sstep(T_P2[0] + 0.5, T_P2[1], t)) for k in range(NC)]
        gl = 0.9 * sum(math.exp(-((py - gy) / 0.3) ** 2) for gy in GATES) + 2.0 * bump(t, T_PULSE, 0.3)
        colD[j].put(OX[j + 1], py, vals, unf=sstep(T_UNF5[0] + 0.06 * j, T_UNF5[1], t), from_y=0.3 if t < T_P2[0] else None, glow=gl, gcol=TEAL if abs(t - T_PULSE) < 0.6 else AMBER_L, sq=sq)
    # 同一趟里：每个位置连到它前面的字（前文 + 它前面的草稿），一起长出来，一起亮
    gr = sstep(*T_ARC, t); ao = sstep(*T_ARC_OFF, t)
    for j, i, tb, am in arcs:
        tb.data.bevel_factor_end = max(0.001, gr); tb.data.bevel_factor_start = min(0.999, ao); tb.hide_render = gr < 0.01 or ao > 0.99
        set_state(am, glow=1.2 + 2.2 * bump(t, T_PULSE, 0.3), glow_col=TEAL)
    # 一趟出来 4 份结果：沿外侧一起回到每个空位的正后方，变成大模型在这一位的首选
    ex = sstep(*T_OUT5, t); pk = sstep(*T_PK5, t)
    for j in range(4):
        if t < T_OUT5[0] or pk >= 0.999: outD[j].hide(); continue
        outD[j].at_path(EP5[j], ex, VD2[2 + j], glow=0.8, sq=1 - pk)
    for j, tk in enumerate(picks):
        if t < T_PK5[0]: off(tk); continue
        p0 = PK[j]; scl = back_out(pk, 1.6) if pk < 1 else 1.0; pos = p0; gl = 1.0 * (1 - sstep(T_PK5[1], T_PK5[1] + 1.0, t)) + 0.4; gcol = AMBER_L
        if j < 3:
            c0 = T_CMP[j]; above = (OX[j + 1], 0.0, ZT + 0.95)
            mv = sstep(c0, c0 + 0.4, t); pos = mix3(p0, above, mv)
            if j < 2:                                                # 一致：落进草稿里，草稿变正式
                mg = sstep(c0 + 0.45, c0 + 0.75, t); pos = mix3(pos, (OX[j + 1], 0.0, ZT + 0.2), mg); scl *= 1 - 0.95 * mg
                gl += 1.6 * mv * (1 - mg); gcol = TEAL if mv > 0.5 else AMBER_L
                if mg >= 0.98: off(tk); continue
            else:                                                    # 不一致：停在「吃」上方；吃、饭退走后落进空位
                gl += 1.0 * mv
                kn = sstep(*T_KAN, t)
                if kn > 0: pos = bez(above, (above[0], above[1], above[2] + 0.35), (OX[3], 0.0, ZT + 0.5), (OX[3], 0.0, ZT), kn)
                if kn >= 1: pos = (OX[3], 0.0, land(ZT, t, T_KAN[1]))
                gl = gl * (1 - 0.7 * sstep(T_KAN[1], T_KAN[1] + 1.0, t)); gcol = AMBER
        else:                                                        # 第 4 位：是接着「吃」算的，跟着作废
            fd = sstep(T_REJ[0], T_REJ[0] + 0.5, t); scl *= 1 - fd
            if fd >= 0.98: off(tk); continue
        tk.put(pos, scale=max(0.001, scl)); tk.look(draft=0.0, glow=gl + same_glow(0, t) * 0, glow_col=gcol)
    # 结果：周末我想去海边看 一起亮一下
    if S5 + 12.7 < t < S5 + 14.6:
        for k, tk in enumerate(prefix + [cands[0], drafts[0], drafts[1], picks[2]]):
            g = math.sin(math.pi * sstep(S5 + 12.7 + 0.08 * k, S5 + 13.6 + 0.08 * k, t)); tk.look(glow=1.2 * g, glow_col=AMBER_L)

# ---------------------------------------------------------------- 对照：两排小账本
def pose_ledger(t):
    li = sstep(E0 - 1.4, E0 - 0.4, t) * (1 - sstep(T_CLOSE, T_CLOSE + 0.9, t)); led.location = (0, 0, lerp(-1.2, 0.0, li)); hide(led, li <= 0.0)
    for o in led.children_recursive: o.hide_render = li <= 0.0
    tA = [E0 + 0.4 + 1.0 * k for k in range(3)]
    set_state(led_panes[0], glow=2.6 * sum(bump(t, a + 0.2, 0.18) for a in tA), glow_col=AMBER_L)
    set_state(led_panes[1], glow=2.6 * bump(t, EB + 1.8, 0.2), glow_col=AMBER_L)
    set_state(led_small_m, glow=2.6 * sum(bump(t, EB + 0.3 * j + 0.1, 0.1) for j in range(4)), glow_col=AMBER_L)
    LZ = 0.06 + S / 2
    y = ROWY[0]
    for k, tk in enumerate(ledA):
        a = tA[k] + 0.25; u = sstep(a, a + 0.55, t)
        if t < a: off(tk); continue
        src = (GIX, y, 0.45); dst = (LSX[k], y, LZ)
        pos = bez(src, (src[0] + 0.2, y, 1.1), (dst[0], y, LZ + 0.6), dst, u)
        tk.put(pos, scale=lerp(0.5, 1, sstep(a, a + 0.25, t))); tk.look(draft=0.0, glow=1.0 * (1 - u), glow_col=AMBER_L)
    for k, (b, m) in enumerate(tallA):
        g = back_out(sstep(tA[k] + 0.2, tA[k] + 0.5, t), 1.6) if t > tA[k] + 0.2 else 0.0
        b.location = (GIX, y, 0.83 + 0.13 * k); b.scale = (max(0.001, g),) * 3; b.hide_render = g < 0.01
        set_state(m, glow=1.5 * bump(t, tA[k] + 0.4, 0.2) + 0.3, glow_col=AMBER)
    y = ROWY[1]; big = EB + 1.6
    for j, tk in enumerate(ledB):
        a = EB + 0.3 * j
        if t < a: off(tk); continue
        u = sstep(a, a + 0.45, t); src = (SIX, y, 0.45); dst = (LSX[j], y, LZ)
        pos = list(bez(src, (src[0] + 0.3, y, 1.0), (dst[0], y, LZ + 0.5), dst, u)); draft, gl, gc, scl = 1.0, 0.0, TEAL, lerp(0.5, 1, sstep(a, a + 0.2, t))
        if j < 2:
            v = sstep(big + 0.5, big + 0.9, t); draft = 1 - v; gl = 2.0 * math.sin(math.pi * v) if 0 < v < 1 else 0.0
        else:
            v = sstep(big + 0.5, big + 0.8, t); gl = 1.6 * v; gc = AMBER
            dr = sstep(big + 0.9, big + 1.4, t); pos[2] -= 0.5 * dr; scl *= 1 - dr
            if dr >= 0.99: off(tk); continue
        tk.put(tuple(pos), scale=scl); tk.look(draft=draft, glow=gl, glow_col=gc)
    a = big + 1.2
    if t < a: off(ledK)
    else:
        u = sstep(a, a + 0.5, t); src = (GIX, y, 0.45); dst = (LSX[2], y, LZ)
        ledK.put(bez(src, (src[0] + 0.2, y, 1.1), (dst[0], y, LZ + 0.6), dst, u), scale=lerp(0.5, 1, sstep(a, a + 0.25, t))); ledK.look(draft=0.0, glow=1.0 * (1 - u), glow_col=AMBER)
    for k, (b, m) in enumerate(tallB):
        tt_ = big + 0.2 if k == 0 else EB + 0.3 * (k - 1) + 0.15
        g = back_out(sstep(tt_, tt_ + 0.3, t), 1.6) if t > tt_ else 0.0
        x = GIX if k == 0 else SIX
        b.location = (x, y, 0.83 if k == 0 else 0.47 + 0.09 * (k - 1)); b.scale = (max(0.001, g),) * 3; b.hide_render = g < 0.01
        set_state(m, glow=(1.5 * bump(t, tt_ + 0.2, 0.2) + 0.3) if k == 0 else 1.2 * bump(t, tt_ + 0.15, 0.12), glow_col=AMBER if k == 0 else '#C8D0D8')

    dz = led.location.z                                             # 字块和计数块跟着账本一起沉下去（收尾时镜头要从上面飞过）
    if dz < -1e-4:
        for tk in ledA + ledB + [ledK]: tk.root.location.z += dz
        for b, m in tallA + tallB: b.location.z += dz

# ---------------------------------------------------------------- 收尾：下一个空位，又有两个候选在抢
def pose_close(t):
    for k, tk in enumerate(close_c):
        a = T_CLOSE + 0.9 + 0.15 * k
        if t < a: off(tk); continue
        hp, roll = hover(k, t, OX[4]); tk.put(hp, roll=roll, scale=back_out(sstep(a, a + 0.4, t), 1.4)); tk.look(draft=1.0, glow=0.4 * (0.5 + 0.5 * math.sin(t * 6 + 3 * k)), glow_col=AMBER_L)

# ---------------------------------------------------------------- 2D 提示的锚点
def anchors(t, cy):
    ANCH['prefix'] = (PX[1] - 0.37, 0, ZT + 0.75); ANCH['cells'] = (PLATE_C[0], cy - 0.2, 0.9)
    ANCH['gather'] = (PLATE_C[0] - 0.4, cy, 1.55); ANCH['pill'] = (PILX[1], PILY, 2.0); ANCH['gate'] = (-1.2, GATES[0], 2.6)
    ANCH['fork_u'] = UP.at(SC + 3.5 * STEP); ANCH['fork_d'] = DN.at(SC + 2.0 * STEP)
    ANCH['qu'] = (0.0, 0.0, ZT + 0.75); ANCH['ctx'] = (PX[2], 0.0, ZT + 0.75); ANCH['slot0'] = (OX[0], 0.0, ZT + 1.25)
    ANCH['park'] = (NEWX - 1.2, PARKY, 1.6); ANCH['c4'] = (PILX[1], PILY, 1.6); ANCH['step'] = (OX[2], 0.0, ZT + 0.9)
    ANCH['small'] = (SMX[0], SMX[1], 1.4); ANCH['drafts'] = (OX[2] + 0.37, 0.0, ZT + 0.8)
    ANCH['park5'] = (1.85, PARKY, 2.0); ANCH['picks'] = (OX[2] + 0.37, 0.95, ZT + 1.35)
    for j in range(4): ANCH[f'd{j}'] = (OX[j + 1], 0.0, ZT + 0.75)
    ANCH['rowA'] = (0.8, ROWY[0] + 0.45, 1.25); ANCH['rowB'] = (0.8, ROWY[1] + 0.45, 1.25)              # 每排的名字：在这一排字的上方
    ANCH['talA'] = (0.8, ROWY[0] - 0.5, -0.05); ANCH['talB'] = (0.4, ROWY[1] - 0.5, -0.05)              # 计数：在这一排的前沿下面

# ---------------------------------------------------------------- 相机
# (场景时间, 位置, 注视点, 焦距, 目的)
CAM = [
    (H0,   (2.05, -3.3, 1.75), (-0.7, 0.1, 0.85), 30, '钩子：从右前方斜看，空位和两个候选在最前面，前缀往后排'),
    (6.8,  (1.85, -3.55, 1.95), (-0.65, 0.2, 0.9), 30, '轻轻漂移'),
    (8.5,  (1.2, -5.9, 4.4), (-0.6, 1.3, 0.9), 30, '拉开：候选坐在分数柱上，柱子后面是大模型'),
    (10.0, (-3.5, -5.0, 4.4), (-1.8, 0.7, 0.5), 34, '第二幕远景：已有文字和它身后的模型'),
    (11.8, (-3.9, -3.4, 4.0), (-1.8, 1.5, 0.6), 34, '跟着展开的数'),
    (13.0, (-4.3, -0.6, 3.2), (-1.7, 3.1, 0.75), 36, '中景：回看前文'),
    (14.6, (-4.1, 0.0, 3.0), (-1.4, 3.2, 0.7), 37, '当前表示变一次'),
    (15.7, (-3.4, 1.2, 4.6), (-1.0, 5.0, 1.2), 38, '跟着托盘出最后一层'),
    (16.3, (-2.4, 2.4, 6.6), (-0.6, 5.4, 2.4), 42, '跟拍结果（下面另有逐帧跟拍）'),
    (16.9, (-1.6, 0.9, 5.9), (0.0, 3.9, 2.7), 42, '继续跟随'),
    (17.5, (-0.6, -1.5, 3.6), (0.4, 2.0, 1.3), 42, '靠近候选区'),
    (18.4, (-0.5, -2.8, 3.4), (0.4, 1.6, 1.0), 38, '近景：候选和分数柱'),
    (19.6, (0.3, -5.0, 5.0), (0.5, 0.3, 0.5), 31, '第三幕：俯一点看分叉口'),
    (21.0, (0.5, -5.4, 5.2), (0.7, 0.4, 0.6), 31, '两条路长出来时升高后退'),
    (22.6, (0.4, -6.6, 6.2), (0.6, 0.2, 0.5), 30, '全景：同一个前缀，两种未来'),
    (24.0, (0.4, -6.7, 6.3), (0.6, 0.2, 0.5), 30, '停一下'),
    (25.4, (-0.6, -6.1, 5.8), (-0.3, 0.1, 0.4), 31, '落选退场'),
    (26.9, (-1.3, -4.8, 4.9), (-0.7, 0.1, 0.35), 34, '中景：「去」进入正式序列'),
    (28.4, (-1.3, -4.8, 5.2), (-0.6, 0.6, 0.6), 33, '第四幕：上下文更新为 周末我想去'),
    (30.2, (-1.4, -4.4, 6.6), (-0.8, 2.6, 0.9), 30, '只把新字的数送进模型'),
    (32.4, (-1.3, -4.2, 6.8), (-0.6, 3.0, 1.0), 30, '回看前文、更新'),
    (34.4, (-0.4, -4.9, 5.2), (0.4, 1.0, 0.6), 31, '下一位置的候选 + 正式输出'),
    (36.3, (-0.2, -5.2, 5.8), (0.5, 1.6, 0.7), 31, '第 2 步：海进上下文，它的一串数进模型'),
    (40.8, (-0.2, -5.0, 5.6), (0.5, 1.2, 0.6), 31, '三步走完'),
    (43.6, (-0.6, -4.9, 4.8), (0.1, 0.6, 0.5), 32, '知识揭晓：海 → 边 → 看'),
    (47.0, (-0.6, -5.0, 4.9), (0.2, 0.5, 0.5), 32, '回到同一个起点'),
    (49.2, (1.3, -5.6, 4.9), (1.8, 0.3, 0.6), 29, '小模型从右边进来'),
    (S5 + 2.2, (1.3, -5.6, 4.9), (1.8, 0.3, 0.6), 29, '草稿摆好'),
    (S5 + 3.4, (1.0, -1.6, 6.2), (1.2, 3.2, 1.0), 31, '跟着托板升过各层'),
    (S5 + 4.4, (2.2, 9.0, 4.3), (0.9, 5.4, 0.6), 30, '落到模型后方回头看：4 串数停在前文旁边'),
    (S5 + 5.6, (2.2, 9.0, 4.3), (0.9, 5.4, 0.6), 30, '每个位置只看它前面的字；同一趟一起亮'),
    (S5 + 6.9, (1.2, -2.2, 6.4), (1.4, 2.0, 1.2), 31, '跟着 4 份结果越过各层出来'),
    (S5 + 7.8, (1.0, -5.2, 4.7), (1.6, 0.4, 0.7), 31, '主景别：草稿、大模型首选、正式输出同框'),
    (S5 + 12.6, (1.0, -5.2, 4.7), (1.6, 0.4, 0.7), 31, '对照全过程镜头不动'),
    (S5 + 14.4, (0.2, -5.6, 4.6), (0.6, 0.1, 0.5), 31, '结果：周末我想去海边看'),
    (E0 - 0.4, (0.0, -6.5, 3.6), (0.0, -2.55, 0.35), 25, '账本：两排'),
    (E0 + 9.4, (0.0, -6.6, 3.65), (0.0, -2.55, 0.35), 25, '账本停住'),
    (T_CLOSE + 1.2, (5.0, -3.3, 1.75), (2.25, 0.1, 0.85), 30, '收尾：回到托盘，下一个空位又有两个候选（和开头同一个角度）'),
    (DUR, (4.9, -3.4, 1.8), (2.25, 0.15, 0.87), 30, '结尾'),
]
_ct = os.environ.get('CAMTEST')            # 调构图：CAMTEST="t,x,y,z,tx,ty,tz,lens" 替换离 t 最近的那一条
if _ct:
    _v = [float(x) for x in _ct.split(',')]; _i = min(range(len(CAM)), key=lambda i: abs(CAM[i][0] - _v[0]))
    CAM[_i] = (CAM[_i][0], tuple(_v[1:4]), tuple(_v[4:7]), _v[7], CAM[_i][4])

def cam_at(t):
    ts = [c[0] for c in CAM]
    i = max(0, min(len(CAM) - 2, max(k for k in range(len(ts)) if ts[k] <= t) if t >= ts[0] else 0))
    def herm(idx):
        p = [Vector(c[idx]) if idx < 3 else c[idx] for c in CAM]
        t0, t1 = ts[i], ts[i + 1]; u = clamp((t - t0) / (t1 - t0))
        P1, P2 = p[i], p[i + 1]
        if ((P1 - P2).length if idx < 3 else abs(P1 - P2)) < 1e-6: return P1                 # 停住的段：不漂
        P0 = p[max(i - 1, 0)]; P3 = p[min(i + 2, len(p) - 1)]
        T0 = ts[max(i - 1, 0)]; T3 = ts[min(i + 2, len(ts) - 1)]
        m1 = (P2 - P0) * ((t1 - t0) / max(1e-6, (t1 - T0))); m2 = (P3 - P1) * ((t1 - t0) / max(1e-6, (T3 - t0)))
        if idx < 3:                                                                              # 前后是停住的段：在这一端速度为 0
            if (p[max(i - 1, 0)] - P1).length < 1e-6: m1 = m1 * 0
            if (p[min(i + 2, len(p) - 1)] - P2).length < 1e-6: m2 = m2 * 0
        h00 = 2 * u ** 3 - 3 * u ** 2 + 1; h10 = u ** 3 - 2 * u ** 2 + u; h01 = -2 * u ** 3 + 3 * u ** 2; h11 = u ** 3 - u ** 2
        return h00 * P1 + h10 * m1 + h01 * P2 + h11 * m2
    return tuple(herm(1)), tuple(herm(2)), herm(3)

def cam(t):
    loc, tgt, lens = cam_at(t)
    # 第二幕：跟拍「想」的结果（按它每一帧的真实位置）
    w = sstep(15.75, 16.15, t) * (1 - sstep(17.3, 17.9, t))
    if w > 0:
        cp = Vector(EP.at(sstep(*T_EXIT, t) * EP.L)); off_ = Vector((-1.5, -3.3, 2.6))
        tgt = tuple(Vector(tgt).lerp(cp, w)); loc = tuple(Vector(loc).lerp(cp + off_, w)); lens = lerp(lens, 40, w)
    w1 = sstep(29.4, 29.8, t) * (1 - sstep(30.8, 31.2, t))
    if w1 > 0:
        cp = Vector(GO4.at(sstep(*T4_GO, t) * GO4.L)); off_ = Vector((-1.6, -3.4, 2.8))
        tgt = tuple(Vector(tgt).lerp(cp, w1)); loc = tuple(Vector(loc).lerp(cp + off_, w1)); lens = lerp(lens, 36, w1)
    w2 = sstep(30.6, 31.2, t) * (1 - sstep(32.3, 32.8, t))
    if w2 > 0:
        tgt = tuple(Vector(tgt).lerp(Vector((-1.4, 5.6, 0.5)), w2)); loc = tuple(Vector(loc).lerp(Vector((-0.4, 8.8, 3.6)), w2)); lens = lerp(lens, 32, w2)
        if 0 < w2 < 1: loc = (loc[0], loc[1], loc[2] + 2.2 * math.sin(math.pi * w2))
    w3 = sstep(32.3, 32.7, t) * (1 - sstep(33.5, 34.2, t))
    if w3 > 0:
        cp = Vector(EP4.at(sstep(*T4_EXIT, t) * EP4.L)); off_ = Vector((-1.5, -3.3, 2.6))
        tgt = tuple(Vector(tgt).lerp(cp, w3)); loc = tuple(Vector(loc).lerp(cp + off_, w3)); lens = lerp(lens, 40, w3)
    return loc, tgt, lens

SHOT = {'DUR': DUR, 'FILM_DUR': v03_time.FILM_DUR, 'tmap': v03_time.film_to_scene, 'pose': pose, 'tracked': tracked}
build()
run(SHOT)
