# 一语道破 EP01 · Full Motion Draft V01（约 64 秒）：六幕完整动态草稿。
# 第一幕 手机 → 第二幕 模型（Test02 B）→ 第三幕 分叉（Test02 A）→ 第四幕 逐步生成的依赖（新）→ 第五幕 推测解码（Test02 C）→ 第六幕 回到手机（新）：B → A → C 一条连续动画，一个场景。
# 身份链：已有文字「周末我想」→ 每个字的一串数 → 模型（回看前文、逐层）→ 候选「去 / 睡」→ 分叉选「去」→ 正式输出「周末我想去」
#        → 小模型草稿「海边吃饭」→ 大模型集中验证 → 接受「海边」→「吃饭」撤回小模型 → 大模型输出口补充「看」→「周末我想去海边看」。
# 所有主角从第一帧到最后一帧都是同一批物体；每帧只改位置、朝向、材质状态（pose(t) 是时间的纯函数）。
# 用法：blender -b -P shot_int.py -- --outdir DIR --scale 0.333 --samples 16 --font F.otf [--f0 --f1 | --only 1.0,5.0]
import os, math
ANIM_DIR = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib.py'), encoding='utf-8').read())

DUR = 64.5
S, STEP = 0.6, 0.74
TRAY_Z = 0.06; ZT = TRAY_Z + S / 2
ZG = 0.09 + 0.0125 + S / 2                       # 字块在分叉玻璃轨道上
ZR = 0.06 + S / 2                                 # 字块在草稿轨上（贴着桌面，比正式托盘低）
PREFIX = '周末我想'
PX = [-2.96, -2.22, -1.48, -0.74]
OX = [0.0, 0.74, 1.48, 2.22, 2.96]               # 去 海 边 看 （下一个）

# ---------------- B：模型 ----------------
NC, CELL, CG = 6, 0.17, 0.19
PLATE_C = (-1.85, 1.45)                           # 数值托盘中心（在已有文字的正后方）
GATES = [3.1, 4.0, 4.9]                           # 三道层（垂直于 y，越往里越深）
CY_STOP1, CY_END = 3.1, 5.75
PILX, PILY = [-0.3, 0.45, 1.2], 1.6
CANDS = [('去', 1.0), ('睡', 0.62), ('出', 0.25)]  # 分数为示意
CELL_TO = [0, 0, 0, 1, 1, 2]                      # 「想」那串数的 6 个方块各飞向哪根柱

# ---------------- A：分叉 ----------------
def _branch(side, L):
    a = math.radians(40) * side; c, n = math.cos(a), math.sin(a)
    return Path([(0, 0, ZG), (0.3, 0.05 * side, ZG), (0.6, 0.22 * side, ZG)] + [(0.6 + c * d, 0.22 * side + n * d, ZG) for d in (0.8, 1.8, L)])
UP, DN = _branch(1, 4.4), _branch(-1, 2.6)
SC = 1.0
FUT_U, FUT_D = '海边看日落', '个懒觉'

# ---------------- C：草稿轨、小模型、大模型 ----------------
RY = -2.8                                          # 草稿轨：在正式输出托盘右前方，从一开始就在
RAIL = Path([(2.6, RY, 0.012), (10.0, RY, 0.012)])
SMALL = (9.3, RY); PORT_X = 8.8                    # 小模型在草稿轨右端，出字口朝左
GX0, GX1 = 3.6, 6.7; GC = (GX0 + GX1) / 2         # 大模型（验证通道），入口在右端
VX = [GC - 1.5 * STEP + j * STEP for j in range(4)]
GH = 1.1
TPORT = (3.1, -2.35)                               # 大模型输出口：通道左后方，开口朝正式输出
DRAFT, NEXT = '海边吃饭', '日'
ACC = 2

# ---------------- 时间表 ----------------
T_UNF = (0.4, 2.0)          # 每个字身后展开一串数
T_GO1 = (1.9, 2.9)          # 托盘带着数进第一层
T_REACH = (3.0, 3.6)        # 连线从当前位置伸向前面的字
T_RESP = (3.5, 3.9)         # 前面的字响应
T_BACK = (3.8, 4.5)         # 信息沿连线回到当前位置
T_UPD = (4.4, 4.9)          # 当前表示变一次
T_GO2 = (4.9, 5.9)          # 穿过第二、三层
T_EXIT = (5.9, 7.2)         # 「想」那串数离开模型，沿外侧回到前面
T_PIL = (7.0, 8.3)          # 方块落进柱脚，分数柱长起来，候选坐在柱顶
T_TRK = (8.4, 9.6)          # 分叉轨道从空位长出去
T_C2F = [(8.7, 10.0), (8.95, 10.25)]   # 去 / 睡 从柱顶沿弧线进入分叉起点
T_PDN = (9.6, 10.4)         # 柱子缩回桌面（出 跟着下去）
T_FUT0, T_FGAP, T_FDUR = 10.3, 0.42, 1.0
T_PICK = (14.0, 14.8)       # 采用上面一条
T_DRET = (14.6, 16.0)       # 下面一条：后面的字收回到「睡」，「睡」沿来路退回候选池
T_QU = (15.4, 16.8)         # 「去」沿轨道回到空位，变成正式的字
T_URET = (17.4, 18.5)       # 上面那条假设的后续收回（只是假设，没有生成）
T_PUSH = [20.4 + 0.4 * j for j in range(4)]; PUSH_DUR = 1.4   # 小模型依次推出草稿，沿草稿轨往左滑进验证通道
T_SCAN = (22.9, 23.9)       # 一道光同时扫过 4 个位置（集中验证）
T_RES = [24.1, 24.5, 24.9]  # 海 接受（抬起）、边 接受、吃 未接受（顿住、下沉）；饭随之失效（后仰）
T_ACC = [(25.6, 27.0), (25.85, 27.25)]   # 海、边从通道后方出来，进正式输出
T_REJ = (27.3, 28.6)        # 吃、饭沿草稿轨往右退出入口，回到小模型
T_KAN = (28.8, 30.3)        # 大模型输出口给出「看」，补到正式输出末端
OB, OC = 10.0, 22.6         # 完整片：B/A 段整体往后 OB 秒（前面是手机幕），C 段往后 OC 秒（前面是第四幕）
for _n in ('T_UNF', 'T_GO1', 'T_REACH', 'T_RESP', 'T_BACK', 'T_UPD', 'T_GO2', 'T_EXIT', 'T_PIL', 'T_TRK', 'T_PDN', 'T_PICK', 'T_DRET', 'T_QU', 'T_URET'):
    globals()[_n] = tuple(x + OB for x in globals()[_n])
T_C2F = [(a + OB, b + OB) for a, b in T_C2F]; T_FUT0 += OB
T_PUSH = [x + OC for x in T_PUSH]; T_SCAN = tuple(x + OC for x in T_SCAN); T_RES = [x + OC for x in T_RES]
T_ACC = [(a + OC, b + OC) for a, b in T_ACC]; T_REJ = tuple(x + OC for x in T_REJ); T_KAN = tuple(x + OC for x in T_KAN)

# ---------------- 第一幕 / 第四幕 / 第六幕 ----------------
PHX, PHY = -6.2, -2.0                              # 手机（站在桌上，屏幕朝镜头）
SCR = '周末我想去海边看日落'
def scr_pos(i):                                    # 回答气泡里第 i 个字的位置（屏幕前面）
    r, c = divmod(i, 5); return (PHX - 0.68 + c * 0.34, PHY - 0.155 - 0.1, 2.3 + 0.86 - r * 0.42)
T_TYPE = [0.8 + 0.32 * i for i in range(10)]       # 手机上逐个出现
T_RWD = [5.4 + 0.12 * (9 - i) for i in range(10)]  # 倒回去：去海边看日落 依次收回（4..9）
T_LIFT = [6.4 + 0.25 * k for k in range(4)]; LIFT_DUR = 1.6   # 周末我想 从屏幕里升起，落到托盘
# 第四幕：去 的一串数进模型（前面的字的结果留着）→ 回看前文 → 出模型 → 下一位置的候选 → 逐步生成循环
T4_UNF = (28.6, 29.6); T4_GO = (29.5, 31.0); T4_REACH = (31.0, 31.5); T4_RESP = (31.4, 31.8); T4_BACK = (31.6, 32.2); T4_UPD = (32.1, 32.5)
T4_EXIT = (32.5, 33.6); T4_PIL = (33.5, 34.5)
T4_CYC = [34.9 + 1.5 * i for i in range(3)]        # 三步：海 → 边 → 看（假设的逐步生成）
T4_RWD = (39.6, 40.7)                              # 收回：换个办法
C4 = [('海', 1.0), ('爬', 0.45), ('吃', 0.3)]
G4 = '海边看'
NEWX = -0.37                                       # 「去」那串数在模型里停放的位置（挨着前面四串）
EP4 = Path([(NEWX, 5.25, 0.4), (-0.4, 5.45, 2.9), (0.0, 3.9, 3.05), (0.45, 2.5, 1.7), (0.45, 1.9, 0.9)], n=200)
GO4 = Path([(0.0, 1.0, 0.4), (-0.2, 1.8, 0.9), (NEWX, 2.6, 0.5), (NEWX, 5.25, 0.4)], n=200)
T6_FLY = [55.0 + 0.2 * i for i in range(8)]; FLY6 = 1.4   # 第六幕：正式输出的 8 个字飞回手机屏幕
T6_TYPE = [58.0, 58.35]                            # 日 落 在手机上接着出现

def build():
    global rig, prefix, plate, cells, gate_tiles, tubes, beads, pillars, cands, strip_u, strip_d, fut_u, fut_d
    global slot, slot_m, rail, small, port_m, gantry, lamps, sheet, sheet_m, tport_m, drafts, kan, nxt, carrier
    new_scene(); studio_lights((0.2, 0.6, 0.4)); desk(0.0)
    rbox((6.9, 0.95, TRAY_Z * 2), (0.05, 0, 0), bevel=0.04, mat=m_metal('#C9CDD2', 0.42))        # 正式输出托盘
    prefix = [Tok(ch, S, f'p{k}') for k, ch in enumerate(PREFIX)]
    slot = bpy.data.objects.new('slot', None); bpy.context.collection.objects.link(slot)           # 「下一个位置」框：会沿托盘往后挪
    slot_m = state_mat('slot', AMBER)
    for (sx, sy, dx, dy) in ((0.66, 0.05, 0, 0.33), (0.66, 0.05, 0, -0.33), (0.05, 0.66, 0.33, 0), (0.05, 0.66, -0.33, 0)):
        b = rbox((sx, sy, 0.03), (dx, dy, 0), bevel=0.012, mat=slot_m); b.parent = slot
    # B：数值托盘 + 每个字一串数
    carrier = bpy.data.objects.new('carrier', None); bpy.context.collection.objects.link(carrier)
    gm = state_mat('plate', '#E8E1D6'); set_state(gm, draft=0.22)
    plate = rbox((3.0, 1.35, 0.06), (0, 0, 0.035), bevel=0.03, mat=gm); plate.parent = carrier
    cells = [[(lambda m: (rbox((CELL, CELL, 1.0), (0, 0, 0), bevel=0.03, mat=m), m))(state_mat(f'c{k}{j}', '#D9C7AE')) for j in range(NC)] for k in range(4)]
    for row in cells:
        for c, m in row: c.parent = carrier
    gate_tiles = []
    for gi, gy in enumerate(GATES):
        gmat = m_metal('#BFC4CA', 0.38)
        for dx in (-1.75, 1.75): rbox((0.12, 0.12, 2.4), (PLATE_C[0] + dx, gy, 1.2), bevel=0.04, mat=gmat)
        rbox((3.62, 0.12, 0.12), (PLATE_C[0], gy, 2.4), bevel=0.04, mat=gmat)
        pm = state_mat(f'pane{gi}', '#EEF0F0'); set_state(pm, draft=0.7)
        rbox((3.4, 0.05, 0.85), (PLATE_C[0], gy, 1.92), bevel=0.02, mat=pm)
        tl = []
        for r in range(2):
            for c in range(6):
                tm = state_mat(f't{gi}{r}{c}', '#575B62' if (r + c + gi) % 3 == 0 else '#D9C7AE')
                rbox((0.3, 0.06, 0.2), (PLATE_C[0] - 1.35 + c * 0.54, gy - 0.05, 1.72 + r * 0.38), bevel=0.04, mat=tm); tl.append(tm)
        gate_tiles.append(tl)
    tubes, beads = [], []          # 回看前文：从当前位置（想）伸向前面每个字的连线 + 沿线回来的小珠
    for k in range(3):
        x0, x1 = PX[3] - PLATE_C[0], PX[k] - PLATE_C[0]
        pth = Path([(x0, 0.0, 0.62), ((x0 + x1) / 2, 0.0, 1.05 + 0.12 * (3 - k)), (x1, 0.0, 0.62)], n=60)
        am = state_mat(f'tube{k}', TEAL)
        tb = curve_tube(pth.pts[::2] + [pth.pts[-1]], 0.022, am, poly=True); tb.parent = carrier
        bm = state_mat(f'bead{k}', AMBER_L); bd = sphere(0.075, (0, 0, 0), bm); bd.parent = carrier
        tubes.append((tb, am, pth)); beads.append((bd, bm))
    pillars = []
    for k in range(3):
        pm = state_mat(f'pil{k}', AMBER if k == 0 else '#D6CBB9'); p = rbox((0.5, 0.5, 1.0), (0, 0, 0), bevel=0.06, mat=pm); pillars.append((p, pm))
    cands = [Tok(ch, S, f'cand{k}') for k, (ch, _) in enumerate(CANDS)]
    # A：分叉轨道与假设的后续
    gu, gd = state_mat('strip_u', '#E4E7E8'), state_mat('strip_d', '#E4E7E8'); set_state(gu, draft=0.55); set_state(gd, draft=0.55)
    strip_u = Grow(UP, 0.84, gu, thick=0.025, name='strip_u', z=0.09, s0=0.5)
    strip_d = Grow(DN, 0.84, gd, thick=0.025, name='strip_d', z=0.13, s0=0.5)
    fut_u = [Tok(ch, S, f'u{k}') for k, ch in enumerate(FUT_U)]
    fut_d = [Tok(ch, S, f'd{k}') for k, ch in enumerate(FUT_D)]
    # C：草稿轨、小模型、大模型（验证通道 + 输出口）
    rm = state_mat('rail', '#E6E9EA'); set_state(rm, draft=0.5)
    rail = Grow(RAIL, 0.86, rm, thick=0.03, name='rail', z=0.045); rail.show(RAIL.L)
    small = bpy.data.objects.new('small', None); bpy.context.collection.objects.link(small)
    b = rbox((0.95, 0.95, 0.95), (0, 0, 0.48), bevel=0.14, mat=m_metal('#B9BEC5', 0.32)); b.parent = small
    port_m = state_mat('port', '#3A3D43'); b = rbox((0.05, 0.7, 0.7), (-0.48, 0, ZR), bevel=0.03, mat=port_m); b.parent = small
    gantry = bpy.data.objects.new('gantry', None); bpy.context.collection.objects.link(gantry)
    fm = m_metal('#BFC4CA', 0.36); L = GX1 - GX0
    for x in (GX0, GX1):
        for y in (RY - 0.6, RY + 0.6):
            b = rbox((0.09, 0.09, GH), (x, y, GH / 2), bevel=0.03, mat=fm); b.parent = gantry
        b = rbox((0.09, 1.3, 0.09), (x, RY, GH), bevel=0.03, mat=fm); b.parent = gantry
    b = rbox((L, 0.09, 0.09), (GC, RY - 0.6, GH), bevel=0.03, mat=fm); b.parent = gantry
    b = rbox((L, 0.09, 0.09), (GC, RY + 0.6, GH), bevel=0.03, mat=fm); b.parent = gantry
    vm = state_mat('roof', '#EEF0F0'); set_state(vm, draft=0.62)
    en = state_mat('entr', '#EAF6F3')                              # 入口：左端一圈淡青的门框
    for (sx, sz, dy, dz) in ((0.05, GH, -0.6, GH / 2), (0.05, GH, 0.6, GH / 2), (0.05, 0.05, 0, GH)):
        b = rbox((0.06, 0.06 if sz == GH else 1.2, sz), (GX1 + 0.06, RY + dy, dz), bevel=0.02, mat=en); b.parent = gantry
    lamps = []
    for j in range(4):
        lm = state_mat(f'lamp{j}', '#D9D4CB'); b = rbox((0.36, 0.2, 0.12), (VX[j], RY + 0.6, GH + 0.1), bevel=0.05, mat=lm); b.parent = gantry; lamps.append(lm)
    sheet_m = state_mat('sheet', '#E2FFF8'); sheet = rbox((L - 0.2, 1.15, 0.02), (GC, RY, 0.05), bevel=0.006, mat=sheet_m); sheet.parent = gantry
    # 大模型输出口：通道右后方一个金属小盒，朝正式输出那一侧开口（琥珀色口框）
    b = rbox((0.6, 0.6, 0.62), (TPORT[0], TPORT[1], 0.31), bevel=0.08, mat=m_metal('#B9BEC5', 0.32)); b.parent = gantry
    b = rbox((GX0 - TPORT[0] - 0.25, 0.09, 0.09), ((GX0 + TPORT[0] + 0.3) / 2, TPORT[1], 0.55), bevel=0.03, mat=fm); b.parent = gantry
    tport_m = state_mat('tport', '#3A3D43')
    for (sx, sz, dx, dz) in ((0.5, 0.06, 0, 0.6), (0.5, 0.06, 0, 0.08), (0.06, 0.52, -0.22, 0.34), (0.06, 0.52, 0.22, 0.34)):
        b = rbox((sx, 0.05, sz), (TPORT[0] + dx, TPORT[1] + 0.3, dz), bevel=0.015, mat=tport_m); b.parent = gantry
    drafts = [Tok(ch, S, f'dr{j}') for j, ch in enumerate(DRAFT)]
    kan = Tok('看', S, 'kan'); nxt = Tok(NEXT, S, 'next')
    rig = Rig(fstop=3.2)
    build_extra()

def build_extra():
    global phone, scr_toks, c4, g4, cells4, tubes4, beads4, loopbead, loopbead_m
    phone = bpy.data.objects.new('phone', None); bpy.context.collection.objects.link(phone)
    b = rbox((2.3, 0.3, 4.6), (PHX, PHY, 2.3), bevel=0.32, seg=10, mat=m_metal('#C9CED6', 0.28)); b.parent = phone
    b = rbox((2.2, 0.02, 4.5), (PHX, PHY - 0.15, 2.3), bevel=0.28, seg=8, mat=m_plastic('#141518', 0.1)); b.parent = phone
    bpy.ops.mesh.primitive_plane_add(size=1, location=(PHX, PHY - 0.165, 2.3), rotation=(math.pi / 2, 0, 0))
    sc_ = bpy.context.active_object; sc_.scale = (2.06, 4.12, 1); sc_.parent = phone
    ui = os.path.join(ANIM_DIR, 'ui_phone.png')
    assign(sc_, image_mat(ui, emit_strength=0.85))
    scr_toks = [None] * 4 + [Tok(ch, S, f'scr{i}') for i, ch in enumerate(SCR) if i >= 4]
    c4 = [Tok(ch, S, f'c4_{k}') for k, (ch, _) in enumerate(C4)]
    g4 = [c4[0]] + [Tok(ch, S, f'g4_{i}') for i, ch in enumerate(G4) if i > 0]
    cells4 = [(lambda m: (rbox((CELL, CELL, 1.0), (0, 0, 0), bevel=0.03, mat=m), m))(state_mat(f'n4{j}', '#D9C7AE')) for j in range(NC)]
    tubes4, beads4 = [], []
    for k in range(3):
        pth = Path([(NEWX, 5.25, 0.62), ((NEWX + PX[k]) / 2, 5.25, 1.0 + 0.1 * (4 - k)), (PX[k], 5.25, 0.62)], n=60)
        am = state_mat(f'tube4{k}', TEAL); tb = curve_tube(pth.pts[::2] + [pth.pts[-1]], 0.022, am, poly=True)
        bm = state_mat(f'bead4{k}', AMBER_L); bd = sphere(0.075, (0, 0, 0), bm)
        tubes4.append((tb, am, pth)); beads4.append((bd, bm))
    loopbead_m = state_mat('loopbead', AMBER_L); loopbead = sphere(0.11, (0, 0, -5), loopbead_m)

def tracked():
    d = {'想': prefix[3].root, '想的一串数': cells[3][0][0], '去': cands[0].root, '睡': cands[1].root, '出': cands[2].root}
    d.update({f'草稿{ch}': t.root for ch, t in zip(DRAFT, drafts)}); d['补充候选看'] = kan.root; d['小模型'] = small; d['大模型'] = gantry
    return d

def hide(o, h):
    o.hide_render = h
    for c in o.children: c.hide_render = h

def bez(p0, p1, p2, p3, u):
    p0, p1, p2, p3 = Vector(p0), Vector(p1), Vector(p2), Vector(p3)
    return tuple((1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * p1 + 3 * (1 - u) * u ** 2 * p2 + u ** 3 * p3)

def land(z_rest, t, t_land):
    """落位时轻轻回弹"""
    return z_rest + 0.12 * (1 - back_out(sstep(t_land - 0.1, t_land + 0.25, t)))

# ---------------- 数值 ----------------
import random
rnd = random.Random(5)
VAL = [[[rnd.uniform(0.14, 0.6) for j in range(NC)] for k in range(4)] for g in range(4)]
UPD = [rnd.uniform(0.2, 0.68) for j in range(NC)]    # 「想」收到前文信息后的新数值（示意）

def carrier_y(t):
    y = lerp(PLATE_C[1], CY_STOP1, sstep(*T_GO1, t))
    return lerp(y, CY_END, sstep(*T_GO2, t))

EP = Path([(PX[3], CY_END - 0.5 + 2.5 * CG, 0.4), (-0.6, CY_END - 0.3, 2.9), (0.0, 3.9, 3.05), (0.45, 2.5, 1.7), (0.45, 1.9, 0.9)], n=200)

def cell_val(k, j, cy, t):
    v = VAL[0][k][j]
    if k == 3: v = lerp(v, UPD[j], sstep(*T_UPD, t))          # 第一层：「想」收到前文的信息，变一次
    for gi in (1, 2): v = lerp(v, VAL[gi + 1][k][j], sstep(GATES[gi] - 0.1, GATES[gi] + 0.25, cy))   # 后两层：穿过时再变
    return v

def pose(t):
    ANCH.clear()
    for k, tk in enumerate(prefix): tk.put((PX[k], 0, ZT)); tk.look()

    # ===================== B =====================
    cy = carrier_y(t); carrier.location = (PLATE_C[0], cy, 0.0)
    unf = [sstep(T_UNF[0] + 0.25 * k, T_UNF[0] + 0.25 * k + 0.9, t) for k in range(4)]
    plate_vis = sstep(T_UNF[0], T_UNF[0] + 0.4, t); plate.scale = (lerp(0.2, 1, plate_vis), lerp(0.2, 1, plate_vis), 1); plate.hide_render = plate_vis < 0.01
    ex = sstep(*T_EXIT, t)
    for k in range(4):
        for j in range(NC):
            c, m = cells[k][j]
            uj = sstep(0.12 * j, 0.5 + 0.1 * j, unf[k])
            v = cell_val(k, j, cy, t)
            h = max(0.01, v * uj)
            # 从字的脚下往后滑出来（局部坐标：托盘中心为原点）
            yl = lerp(0.3 - cy, -0.5 + j * CG, uj)
            xl = PX[k] - PLATE_C[0]
            loc = Vector((xl, yl, 0.065 + h / 2)); sc = (lerp(0.4, 1, uj), lerp(0.4, 1, uj), h)
            shade = clamp((v - 0.14) / 0.46)
            col = tuple(hex3('#E3D6C2')[i] + (hex3('#4F535A')[i] - hex3('#E3D6C2')[i]) * shade for i in range(3))
            glow, gcol = 0.0, AMBER_L
            for gi, gy in enumerate(GATES[1:]): glow += 1.4 * math.exp(-((cy - gy) / 0.3) ** 2)
            if k < 3: glow += 1.6 * math.sin(math.pi * sstep(*T_RESP, t))                    # 前面的字：被连到时响应
            if k == 3:
                glow += 2.2 * math.sin(math.pi * sstep(*T_UPD, t)); gcol = TEAL if T_UPD[0] < t < T_UPD[1] else AMBER_L
                if T_UPD[0] < t < T_UPD[1]: sc = (sc[0] * (1 + 0.15 * math.sin(math.pi * sstep(*T_UPD, t))), sc[1], sc[2])
            if k < 3 and T_RESP[0] < t < T_RESP[1]: sc = (sc[0], sc[1], sc[2] * (1 + 0.18 * math.sin(math.pi * sstep(*T_RESP, t))))
            hidden = uj < 0.01
            if k == 3 and t >= T_EXIT[0]:
                # 「想」那串数：整串离开托盘，从模型外侧绕回前面，再分头落进三根柱脚
                ep = EP
                pg = ep.at(ex * ep.L); w = Vector(pg) + Vector((0, (j - 2.5) * CG, h / 2 - 0.3))
                if t > T_PIL[0]:
                    uf = sstep(T_PIL[0] + 0.07 * j, T_PIL[0] + 0.07 * j + 0.6, t)
                    pk = CELL_TO[j]; nth = [i for i in range(j) if CELL_TO[i] == pk].__len__()
                    dst = Vector((PILX[pk], PILY, 0.09 + nth * 0.2))
                    w = w.lerp(dst, uf); w.z += 0.5 * math.sin(math.pi * uf)
                    sq = 1 - sstep(T_PIL[0] + 0.75, T_PIL[0] + 1.05, t); sc = (sq, sq, h * sq + 0.001); hidden = sq < 0.02
                loc = w - Vector(carrier.location)
            c.location = loc; c.scale = sc; c.hide_render = hidden
            set_state(m, col=col, glow=glow, glow_col=gcol, alpha=1.0)
            if k < 3: set_state(m, alpha=1.0 - 0.0 * ex)
    # 层上的参数块：托盘穿过时亮
    for gi, gy in enumerate(GATES):
        near = math.exp(-((cy - gy) / 0.5) ** 2) * (1 if gi > 0 else (0.4 + 0.6 * sstep(T_REACH[0], T_UPD[1], t) * (1 - sstep(T_UPD[1], T_GO2[0] + 0.4, t))))
        for i, tm in enumerate(gate_tiles[gi]): set_state(tm, glow=1.5 * near * (0.6 + 0.4 * math.sin(t * 9 + i)), glow_col=AMBER_L)
    # 回看前文：连线从「想」伸出去 → 前面的字响应 → 小珠沿线回来 → 连线收回
    for k, ((tb, am, pth), (bd, bm)) in enumerate(zip(tubes, beads)):
        grow = sstep(T_REACH[0] + 0.12 * k, T_REACH[1] + 0.12 * k, t); ret = sstep(T_UPD[0] - 0.05, T_UPD[1], t)
        tb.data.bevel_factor_end = max(0.001, grow); tb.data.bevel_factor_start = min(0.999, ret * grow)
        tb.hide_render = grow < 0.01 or ret > 0.99
        set_state(am, glow=1.6, glow_col=TEAL)
        ub = sstep(T_BACK[0] + 0.1 * k, T_BACK[1] - 0.2 + 0.1 * k, t)
        bd.location = pth.at((1 - ub) * pth.L); bd.hide_render = not (0.0 < ub < 1.0)
        set_state(bm, glow=3.0, glow_col=AMBER_L)
    # 分数柱：从落下的方块长出来；候选坐在柱顶。之后柱子缩回桌面
    pd = sstep(*T_PDN, t)
    for k, ((p, pm), (ch, scv)) in enumerate(zip(pillars, CANDS)):
        g = back_out(sstep(T_PIL[0] + 0.55, T_PIL[1], t), 1.1) if t > T_PIL[0] + 0.55 else 0.0
        H = max(0.02, 1.5 * scv * g * (1 - pd)); p.location = (PILX[k], PILY, H / 2); p.scale = (1, 1, H); p.hide_render = g < 0.01 or pd > 0.99
        set_state(pm, glow=0.8 * sstep(T_PIL[1] - 0.3, T_PIL[1], t) if k == 0 else 0.0, glow_col=AMBER)
    # 候选字：在柱顶 → 去 / 睡 沿弧线进入分叉起点；出 跟着柱子缩回
    for k, tk in enumerate(cands):
        g = sstep(T_PIL[0] + 0.55, T_PIL[1], t)
        H = 1.5 * CANDS[k][1] * (back_out(g, 1.1) if g > 0 else 0) * (1 - (pd if k == 2 else 0))
        top = (PILX[k], PILY, H + S / 2 + 0.03)
        if t < T_PIL[0] + 0.55: hide(tk.root, True); tk.look(alpha=0.0); continue
        hide(tk.root, False)
        if k == 2:
            tk.put(top, scale=max(0.001, g * (1 - sstep(T_PDN[0] + 0.4, T_PDN[1], t)))); tk.look(draft=1.0)
            continue
        path = UP if k == 0 else DN
        u = sstep(*T_C2F[k], t)
        if u <= 0: tk.put(top, scale=max(0.001, g)); tk.look(draft=1.0); continue
        fs = path.at(SC)
        pos = bez(top, (top[0], top[1] - 0.2, top[2] + 0.9), (fs[0], fs[1] + 0.3 * (1 if k == 0 else -1), fs[2] + 0.9), fs, u)
        yaw = yaw_of(path.tan(SC)) * 0.35 * u
        if k == 0:
            pick = sstep(*T_PICK, t); bq = sstep(*T_QU, t)
            if t >= T_QU[0]:
                s = SC * (1 - bq); pp = path.at(s); hop = 0.4 * math.sin(math.pi * bq)
                pos = (pp[0], pp[1], pp[2] + hop) if bq < 0.85 else (0.0, 0.0, land(ZT, t, T_QU[1]))
                yaw = yaw_of(path.tan(max(s, 0.01))) * 0.35 * (1 - bq)
            tk.put(pos, yaw=yaw); tk.look(draft=1.0 - bq, glow=1.4 * pick * (1 - 0.8 * bq), glow_col=AMBER)
        else:
            # 落选：后面的字先收回到「睡」，然后「睡」沿来路退回候选池，落进桌面上那根柱子的位置
            r = sstep(T_DRET[0] + 0.7, T_DRET[1], t)
            if r > 0:
                hole = (PILX[1], PILY, ZT - 0.1)
                pos = bez(fs, (fs[0], fs[1] - 0.3, fs[2] + 0.9), (hole[0], hole[1] - 0.2, hole[2] + 1.2), hole, r)
                if r > 0.85: pos = (hole[0], hole[1], lerp(hole[2], -0.6, sstep(0.85, 1.0, r)))
                yaw *= 1 - r
            tk.put(pos, yaw=yaw); tk.look(draft=1.0); hide(tk.root, r >= 0.999)

    # ===================== A =====================
    gtr = sstep(*T_TRK, t)
    dret = sstep(*T_DRET, t); uret = sstep(*T_URET, t)
    su = 0.55 + gtr * (UP.L - 0.55); sd = 0.55 + gtr * (DN.L - 0.55)
    if t > T_URET[0]: su = 0.55 + (UP.L - 0.55) * (1 - uret)
    if t > T_DRET[0]: sd = 0.55 + (DN.L - 0.55) * (1 - dret)
    strip_u.show(su if gtr > 0 and uret < 0.999 else 0); strip_d.show(sd if gtr > 0 and dret < 0.999 else 0)
    pick = sstep(*T_PICK, t)
    set_state(strip_u.mat, glow=0.25 * pick * (1 - sstep(*T_QU, t)), glow_col=AMBER_L)
    for path, toks, side in ((UP, fut_u, 0), (DN, fut_d, 1)):
        for k, tok in enumerate(toks):
            t0 = T_FUT0 + (k + side * 0.5) * T_FGAP
            if t < t0: tok.put((0, 0, -5), scale=0.001); tok.look(alpha=0.0); hide(tok.root, True); continue
            hide(tok.root, False)
            u = sstep(t0, t0 + T_FDUR, t)
            s = lerp(SC + k * STEP, SC + (k + 1) * STEP, u); scl = lerp(0.55, 1.0, sstep(t0, t0 + 0.4, t)); a = min(1.0, lin(t0, t0 + 0.15, t))
            # 退场：沿轨道收回（下面一条收回到「睡」，上面一条收回到分叉口），一边收一边缩进前一个字里
            rt = sstep(T_DRET[0] + 0.1 * (len(toks) - 1 - k), T_DRET[0] + 0.7, t) if side else sstep(T_URET[0] + 0.08 * (len(toks) - 1 - k), T_URET[1], t)
            if rt > 0: s = lerp(s, SC, rt); scl *= 1 - 0.95 * sstep(0.25, 0.9, rt)
            p = path.at(s); tok.put((p[0], p[1], p[2] + 0.1 * math.sin(math.pi * u)), yaw=yaw_of(path.tan(s)) * 0.35, scale=max(0.001, scl))
            tok.look(draft=1.0, alpha=a, glow=0.3 * pick * (1 - uret) if side == 0 else 0.0, glow_col=AMBER_L)
            hide(tok.root, rt >= 0.999)

    # 「下一个位置」框：开始在「去」的位置；之后每落进一个正式的字就往后挪一格
    idx = 0 + sstep(T_QU[1] - 0.2, T_QU[1] + 0.3, t) + sstep(T_ACC[0][1] - 0.2, T_ACC[0][1] + 0.3, t) + sstep(T_ACC[1][1] - 0.2, T_ACC[1][1] + 0.3, t) + sstep(T_KAN[1] - 0.2, T_KAN[1] + 0.3, t)
    slot.location = (OX[0] + idx * STEP, 0, TRAY_Z + 0.015)
    pulse = 0.5 + 0.5 * math.sin(t * 4)
    busy = sstep(T_PIL[0], T_PIL[0] + 0.5, t) * (1 - sstep(T_QU[0], T_QU[0] + 0.3, t))
    set_state(slot_m, glow=(1.0 + 0.8 * pulse) * (1 - 0.6 * busy), alpha=1.0)

    # ===================== C =====================
    # 草稿轨、小模型、大模型一开始就在（在镜头外 / 背景里），不再从桌面下升起
    push = sum(math.exp(-((t - (tp + 0.05)) / 0.12) ** 2) for tp in T_PUSH) + 0.8 * math.exp(-((t - (T_REJ[1] - 0.05)) / 0.15) ** 2)
    set_state(port_m, glow=3.0 * push, glow_col=AMBER_L)
    small.location = (SMALL[0], SMALL[1], 0.0); small.scale = (1 - 0.05 * push, 1, 1 + 0.03 * push)
    rej = sstep(*T_REJ, t)
    for j, tk in enumerate(drafts):
        if t < T_PUSH[j]: hide(tk.root, True); tk.look(alpha=0.0); continue
        hide(tk.root, False)
        up = sstep(T_PUSH[j], T_PUSH[j] + PUSH_DUR, t)
        x = lerp(PORT_X - 0.1, VX[j], up)
        pos = [x, RY, ZR + 0.25 * math.sin(math.pi * min(1, up * 3))]; pitch = 0.0
        draft, glow, gcol, scl = 1.0, 0.0, TEAL, lerp(0.55, 1.0, sstep(T_PUSH[j], T_PUSH[j] + 0.2, t))
        if j < ACC:
            r = sstep(T_RES[j], T_RES[j] + 0.3, t)
            pos[2] += 0.2 * back_out(r) if r > 0 else 0.0           # 接受：抬起来，等着进正式输出
            glow = 1.4 * r
            if t > T_ACC[j][0]:
                u = sstep(*T_ACC[j], t)
                pos = list(bez((VX[j], RY, ZR + 0.2), (VX[j] - 0.3, RY + 0.9, 0.9), (OX[j + 1] + 0.6, -0.6, 1.2), (OX[j + 1], 0.0, ZT), u))
                if u > 0.9: pos = [OX[j + 1], 0.0, land(ZT, t, T_ACC[j][1])]
                draft = 1.0 - sstep(T_ACC[j][0] + 0.3, T_ACC[j][1], t); glow = 1.4 * (1 - u) + 0.4 * (1 - sstep(T_ACC[j][1], T_ACC[j][1] + 0.6, t))
        else:
            r = sstep(T_RES[2], T_RES[2] + 0.35, t)
            if j == ACC:
                glow = 1.6 * r; gcol = AMBER
                pos[0] += 0.06 * math.sin(t * 55) * math.sin(math.pi * sstep(T_RES[2], T_RES[2] + 0.5, t))   # 未接受：顿一下
                pos[2] -= 0.12 * r                                                                         # 并沉下去
            else:
                pitch = -0.32 * sstep(T_RES[2] + 0.2, T_RES[2] + 0.55, t)                                  # 后面的「饭」跟着失效：往后仰
            if rej > 0:
                # 「吃」带着「饭」沿草稿轨往右退出入口，回到小模型的出字口
                x0 = VX[j]; x1 = PORT_X + 0.2 - (3 - j) * 0.62
                xx = lerp(x0, x1, ease(rej)); pos = [xx, RY, pos[2] * (1 - rej) + ZR * rej]
                if rej > 0.8: scl *= 1 - 0.9 * sstep(0.8, 1.0, rej); pos[0] = lerp(xx, SMALL[0], sstep(0.8, 1.0, rej))
                glow *= 1 - rej; pitch *= 1 - rej
        tk.put(tuple(pos), pitch=pitch, scale=max(0.001, scl)); tk.look(draft=draft, glow=glow, glow_col=gcol)
        if j >= ACC: hide(tk.root, rej >= 0.999)
    # 大模型：草稿进来后灯亮；扫描时 4 盏灯一起白亮（一次看 4 个）；结果沿序列点亮
    on = sstep(T_PUSH[-1] + 0.6, T_PUSH[-1] + 1.4, t)
    scanning = math.sin(math.pi * sstep(*T_SCAN, t)) if T_SCAN[0] < t < T_SCAN[1] else 0.0
    for j, lm in enumerate(lamps):
        if j <= ACC:
            r = sstep(T_RES[j], T_RES[j] + 0.25, t); col = TEAL if j < ACC else AMBER; g = (2.0 if j < ACC else 2.4) * r
        else: r, col, g = 0.0, '#D9D4CB', 0.0
        fade = 1 - sstep(T_KAN[1], T_KAN[1] + 1.0, t)
        set_state(lm, glow=(g + 0.5 * on * (1 - r) + 3.0 * scanning) * fade, glow_col=col if r > 0.05 else '#F4FFFB')
    if T_SCAN[0] <= t <= T_SCAN[1] + 0.05:
        u = sstep(*T_SCAN, t); sheet.location = (GC, RY, lerp(0.08, GH - 0.08, u)); sheet.hide_render = False
        set_state(sheet_m, glow=4.5 * math.sin(math.pi * u), glow_col='#DFFFF6', alpha=0.8 * math.sin(math.pi * u))
    else: sheet.hide_render = True
    # 补充候选「看」：大模型输出口先亮，「看」从口里滑出来，沿独立的弧线落到正式输出末端
    set_state(tport_m, glow=2.8 * sstep(T_KAN[0] - 0.4, T_KAN[0], t) * (1 - sstep(T_KAN[0] + 0.8, T_KAN[0] + 1.4, t)), glow_col=AMBER)
    if t < T_KAN[0]: hide(kan.root, True); kan.look(alpha=0.0)
    else:
        hide(kan.root, False)
        mouth = (TPORT[0], TPORT[1] + 0.05, 0.34); out_ = (TPORT[0], TPORT[1] + 0.6, 0.38)
        e = sstep(T_KAN[0], T_KAN[0] + 0.45, t)
        if e < 1: pos = mix3(mouth, out_, e); scl = lerp(0.7, 1.0, e)
        else:
            u = sstep(T_KAN[0] + 0.45, T_KAN[1], t); pos = bez(out_, (out_[0], out_[1] + 0.4, 1.1), (OX[3] + 0.4, -0.3, 1.0), (OX[3], 0.0, ZT), u); scl = 1.0
            if u > 0.9: pos = (OX[3], 0.0, land(ZT, t, T_KAN[1]))
        kan.put(pos, scale=scl); kan.look(draft=0.0, glow=2.0 * (1 - 0.8 * sstep(T_KAN[1], T_KAN[1] + 0.8, t)), glow_col=AMBER)
    hide(nxt.root, True)

    # 2D 提示的锚点
    ANCH['prefix'] = (PX[1] - 0.37, 0, ZT + 0.75); ANCH['cells'] = (PLATE_C[0], cy - 0.2, 0.9)
    ANCH['gather'] = (PLATE_C[0] - 0.4, cy, 1.55); ANCH['pill'] = (PILX[1], PILY, 2.0)
    ANCH['fork_u'] = UP.at(SC + 3.5 * STEP); ANCH['fork_d'] = DN.at(SC + 2.5 * STEP)
    ANCH['qu'] = (0.0, 0.0, ZT + 0.75); ANCH['ghost'] = UP.at(SC + 2.5 * STEP)
    ANCH['small'] = (SMALL[0], RY, 1.35); ANCH['drafts'] = (VX[1] + 0.37, RY, 1.25)
    ANCH['ver'] = (GC, RY + 0.6, GH + 0.6); ANCH['out'] = (PX[1], 0.0, ZT + 0.75)
    ANCH['chi'] = drafts[ACC].root.location.copy() + Vector((0, 0, 0.65)); ANCH['kan'] = kan.root.location.copy() + Vector((0, 0, 0.65))
    ANCH['acc'] = (VX[0] + 0.37, RY, 1.35)

    # 相机：每一段都有一个要跟的东西（见文末 CAM 表）
    pose_extra(t)
    loc, tgt, lens = cam_at(t)
    # 6–8 秒：跟拍「想」那串数（按它每一帧的真实位置，保持同一个相对角度），模型退到背景
    w = sstep(5.75 + OB, 6.15 + OB, t) * (1 - sstep(7.3 + OB, 7.9 + OB, t))
    if w > 0:
        cp = Vector(EP.at(sstep(*T_EXIT, t) * EP.L)); off = Vector((-1.5, -3.3, 2.6))
        tgt = tuple(Vector(tgt).lerp(cp, w)); loc = tuple(Vector(loc).lerp(cp + off, w)); lens = lerp(lens, 40, w)
    # 第四幕：跟拍「去」那串数进模型；回看前文时从模型上方俯视；出模型时再跟拍（和第二幕同一种镜头语言）
    w1 = sstep(29.4, 29.8, t) * (1 - sstep(30.8, 31.2, t))
    if w1 > 0:
        cp = Vector(GO4.at(sstep(*T4_GO, t) * GO4.L)); off = Vector((-1.6, -3.4, 2.8))
        tgt = tuple(Vector(tgt).lerp(cp, w1)); loc = tuple(Vector(loc).lerp(cp + off, w1)); lens = lerp(lens, 36, w1)
    w2 = sstep(30.6, 31.2, t) * (1 - sstep(32.3, 32.8, t))
    if w2 > 0:   # 从层的上方越过去，落到模型后方回头看（停在里面的几串数和「去」那串之间没有遮挡）
        tgt = tuple(Vector(tgt).lerp(Vector((-1.5, 5.2, 0.5)), w2)); loc = tuple(Vector(loc).lerp(Vector((-0.6, 8.4, 3.6)), w2)); lens = lerp(lens, 32, w2)
        if 0 < w2 < 1: loc = (loc[0], loc[1], loc[2] + 2.2 * math.sin(math.pi * w2))
    w3 = sstep(32.3, 32.7, t) * (1 - sstep(33.5, 34.2, t))
    if w3 > 0:
        cp = Vector(EP4.at(sstep(*T4_EXIT, t) * EP4.L)); off = Vector((-1.5, -3.3, 2.6))
        tgt = tuple(Vector(tgt).lerp(cp, w3)); loc = tuple(Vector(loc).lerp(cp + off, w3)); lens = lerp(lens, 40, w3)
    rig.set(loc, tgt, lens=lens)

# (时间, 相机位置, 注视点, 焦距, 目的)
def formal_toks():
    """正式输出的 8 个字（同一批物体）：周 末 我 想 去 海 边 看"""
    return prefix + [cands[0], drafts[0], drafts[1], kan]

def pose_extra(t):
    phone.location = (0, 0, 0)
    # ---------- 第一幕：手机上逐字出现；倒回去；周末我想 从屏幕里升起，落到托盘 ----------
    for i in range(10):
        tk = prefix[i] if i < 4 else scr_toks[i]
        if i < 4 and t >= T_LIFT[i] + LIFT_DUR: continue                       # 已经在托盘上（第二幕接管）
        ap = sstep(T_TYPE[i], T_TYPE[i] + 0.22, t)
        if i >= 4:
            if t < 53.0:
                rw = sstep(T_RWD[i], T_RWD[i] + 0.25, t); scl = 0.5 * back_out(ap, 1.6) * (1 - rw)
            else:                                                                 # 第六幕：日 落 接着出现（去海边看 由正式的字飞回来）
                if i < 8: hide(tk.root, True); tk.look(alpha=0.0); continue
                ap2 = sstep(T6_TYPE[i - 8], T6_TYPE[i - 8] + 0.22, t); scl = 0.5 * back_out(ap2, 1.6)
            tk.put(scr_pos(i), scale=max(0.001, scl)); tk.look(draft=0.0); hide(tk.root, scl < 0.01); continue
        if t < T_LIFT[i]:
            scl = 0.5 * back_out(ap, 1.6); tk.put(scr_pos(i), scale=max(0.001, scl)); hide(tk.root, scl < 0.01); tk.look()
        else:
            u = sstep(T_LIFT[i], T_LIFT[i] + LIFT_DUR, t); a = scr_pos(i); b = (PX[i], 0.0, ZT)
            pos = bez(a, (a[0], a[1] - 0.6, a[2] + 0.4), (b[0] - 0.8, b[1] - 0.6, b[2] + 1.6), b, u)
            if u > 0.9: pos = (b[0], b[1], land(ZT, t, T_LIFT[i] + LIFT_DUR))
            tk.put(pos, scale=lerp(0.5, 1.0, sstep(0.0, 0.6, u))); hide(tk.root, False); tk.look()

    # ---------- 第四幕：上下文更新 → 只把新字「去」的数送进模型 → 回看前文 → 下一位置的候选 → 逐步生成 ----------
    un = sstep(*T4_UNF, t); go = sstep(*T4_GO, t); ex = sstep(*T4_EXIT, t)
    for j, (c, m) in enumerate(cells4):
        v = VAL[0][3][(j + 2) % NC] * 0.9 + 0.05
        if T4_UPD[0] < t: v = lerp(v, UPD[(j + 3) % NC], sstep(*T4_UPD, t))
        uj = sstep(0.12 * j, 0.5 + 0.1 * j, un); h = max(0.01, v * uj)
        dy = -0.5 + j * CG
        if go <= 0: p = (OX[0], lerp(0.3, 1.0 + 0.0, uj) + j * CG * uj, 0.065 + h / 2)
        else:
            q = GO4.at(go * GO4.L); p = (q[0], q[1] + dy * (0.6 + 0.4 * go), 0.065 + h / 2 + (q[2] - 0.4))
        if t >= T4_EXIT[0]:
            q = EP4.at(ex * EP4.L); p = (q[0], q[1] + dy, q[2] + h / 2 - 0.3)
            if t > T4_PIL[0]:
                uf = sstep(T4_PIL[0] + 0.06 * j, T4_PIL[0] + 0.06 * j + 0.5, t); pk = CELL_TO[j]; nth = sum(1 for i in range(j) if CELL_TO[i] == pk)
                w_ = Vector(p).lerp(Vector((PILX[pk], PILY, 0.09 + nth * 0.2)), uf); w_.z += 0.5 * math.sin(math.pi * uf); p = tuple(w_)
                sq = 1 - sstep(T4_PIL[0] + 0.6, T4_PIL[0] + 0.9, t); h = h * sq + 0.001; uj = uj * sq
        c.location = p; c.scale = (lerp(0.4, 1, uj), lerp(0.4, 1, uj), h); c.hide_render = uj < 0.02 or t < T4_UNF[0]
        shade = clamp((v - 0.14) / 0.46)
        col = tuple(hex3('#E3D6C2')[i] + (hex3('#4F535A')[i] - hex3('#E3D6C2')[i]) * shade for i in range(3))
        set_state(m, col=col, glow=2.2 * math.sin(math.pi * sstep(*T4_UPD, t)), glow_col=TEAL)
    # 前面四串数（停在模型里，没有重算）：被连到时亮一下
    if T4_RESP[0] < t < T4_RESP[1]:
        for k in range(3):
            for j, (c, m) in enumerate(cells[k]): set_state(m, glow=1.6 * math.sin(math.pi * sstep(*T4_RESP, t)), glow_col=AMBER_L)
    for k, ((tb, am, pth), (bd, bm)) in enumerate(zip(tubes4, beads4)):
        grow = sstep(T4_REACH[0] + 0.08 * k, T4_REACH[1] + 0.08 * k, t); ret = sstep(T4_UPD[0] - 0.05, T4_UPD[1], t)
        tb.data.bevel_factor_end = max(0.001, grow); tb.data.bevel_factor_start = min(0.999, ret * grow)
        tb.hide_render = grow < 0.01 or ret > 0.99; set_state(am, glow=1.6, glow_col=TEAL)
        ub = sstep(T4_BACK[0] + 0.08 * k, T4_BACK[1] - 0.15 + 0.08 * k, t)
        bd.location = pth.at((1 - ub) * pth.L); bd.hide_render = not (0.0 < ub < 1.0); set_state(bm, glow=3.0, glow_col=AMBER_L)
    # 下一位置的候选：柱子再长起来（海 / 爬 / 吃）；之后逐步生成的三步；最后收回
    rw = sstep(*T4_RWD, t)
    if T4_PIL[0] + 0.4 < t < T4_RWD[1] + 0.2:
        g = back_out(sstep(T4_PIL[0] + 0.4, T4_PIL[1], t), 1.1)
        for k, ((p, pm), (ch, scv)) in enumerate(zip(pillars, C4)):
            H = max(0.02, 1.5 * scv * g * (1 - rw)); p.location = (PILX[k], PILY, H / 2); p.scale = (1, 1, H); p.hide_render = H < 0.03
            bump = sum(math.exp(-((t - (c0 + 1.25)) / 0.15) ** 2) for c0 in T4_CYC[:2]) if k == 0 else 0.0
            p.scale = (1 + 0.12 * bump, 1 + 0.12 * bump, H)
            set_state(pm, glow=0.8 * (k == 0) + 1.6 * bump, glow_col=AMBER)
        for k in (1, 2):
            H = 1.5 * C4[k][1] * g * (1 - rw); c4[k].put((PILX[k], PILY, H + S / 2 + 0.03), scale=max(0.001, g * (1 - rw)))
            c4[k].look(draft=1.0); hide(c4[k].root, g * (1 - rw) < 0.02)
    else:
        for k in (1, 2): hide(c4[k].root, True); c4[k].look(alpha=0.0)
    H0 = 1.5 * C4[0][1]
    for i, tk in enumerate(g4):
        c0 = T4_CYC[i]; top = (PILX[0], PILY, H0 + S / 2 + 0.03)
        if i == 0: appear = sstep(T4_PIL[0] + 0.5, T4_PIL[1], t)
        else: appear = sstep(c0 - 0.25, c0, t)                                   # 上一步落定后，下一步的候选才从柱顶升起
        if appear <= 0 or t > T4_RWD[1] + 0.1: hide(tk.root, True); tk.look(alpha=0.0); continue
        hide(tk.root, False)
        u = sstep(c0, c0 + 0.6, t); dst = (OX[i + 1], 0.0, ZT)
        pos = bez(top, (top[0], top[1] - 0.4, top[2] + 0.6), (dst[0], dst[1] + 0.4, dst[2] + 1.0), dst, u)
        if t < c0: pos = (top[0], top[1], lerp(top[2] - 0.5, top[2], appear))
        # 收回：从最后一个字开始依次回去，并在汇合前缩小，避免三个字块在柱脚互相穿插
        rwi = sstep(T4_RWD[0] + 0.2 * (2 - i), T4_RWD[1] - 0.4 + 0.2 * (2 - i), t)
        if rwi > 0: pos = bez(dst, (dst[0], dst[1] + 0.3, dst[2] + 0.8), (top[0], top[1] - 0.2, 1.4), (PILX[0], PILY, 0.2), rwi)
        tk.put(pos, scale=max(0.001, (appear if t < c0 else 1.0) * (1 - sstep(0.45, 0.85, rwi)))); tk.look(draft=1.0, glow=0.6 * (1 - u) if t >= c0 else 0.0, glow_col=AMBER_L)
    # 每一步的「一轮」：一颗光珠从刚写下的字出发，回到模型，再到候选柱（下一步才能开始）
    lb = None
    for i, c0 in enumerate(T4_CYC[:3]):
        if c0 + 0.6 <= t < c0 + 1.4:
            u = sstep(c0 + 0.6, c0 + 1.4, t); a = (OX[i + 1], 0.0, ZT + 0.4)
            lb = bez(a, (NEWX + 0.4, 2.0, 1.4), (NEWX, 5.2, 1.6), (PILX[0], PILY, H0 + 0.1), u) if u < 1 else None
    loopbead.location = lb if lb else (0, 0, -5); loopbead.hide_render = lb is None; set_state(loopbead_m, glow=3.5, glow_col=AMBER_L)

    # ---------- 第六幕：正式输出的 8 个字沿托盘回到手机屏幕 ----------
    for i, tk in enumerate(formal_toks()):
        if t < T6_FLY[i]: continue
        u = sstep(T6_FLY[i], T6_FLY[i] + FLY6, t)
        a = (OX[i - 4] if i >= 4 else PX[i], 0.0, ZT); b = scr_pos(i)
        pos = bez(a, (a[0], a[1] - 0.4, a[2] + 1.2), (b[0] + 0.8, b[1] - 0.8, b[2] + 0.6), b, u)
        tk.put(pos, scale=lerp(1.0, 0.5, sstep(0.3, 1.0, u))); tk.look(draft=0.0, glow=0.0); hide(tk.root, False)

    ANCH['phone'] = (PHX, PHY, 4.9); ANCH['scr'] = (PHX, PHY - 0.3, 1.6); ANCH['park'] = (NEWX - 1.2, 5.25, 1.6)
    ANCH['step'] = (OX[2], 0.0, ZT + 0.9); ANCH['c4'] = (PILX[1], PILY, 1.6); ANCH['ctx'] = (PX[2], 0.0, ZT + 0.75)

CAM = [
    (0.0,  (-6.2, -9.0, 2.5), (-6.2, -2.0, 2.4), 42, '第一幕：手机近景，回答逐字出现'),
    (4.8,  (-6.2, -8.4, 2.7), (-6.2, -2.0, 2.6), 44, '靠近回答'),
    (6.6,  (-5.8, -7.2, 3.4), (-5.4, -1.4, 2.2), 40, '周末我想 从屏幕里升起'),
    (8.4,  (-4.6, -6.2, 4.2), (-3.0, -0.3, 1.0), 36, '跟着字落到托盘'),
    (10.0, (-3.5, -5.0, 4.4), (-1.8, 0.7, 0.5), 34, '第二幕远景：已有文字和它身后的模型'),
    (11.8, (-3.9, -3.4, 4.0), (-1.8, 1.5, 0.6), 34, '跟着展开的数'),
    (13.0, (-4.3, -0.6, 3.2), (-1.7, 3.1, 0.75), 36, '中景：回看前文'),
    (14.6, (-4.1, 0.0, 3.0), (-1.4, 3.2, 0.7), 37, '当前表示变一次'),
    (15.7, (-3.4, 1.2, 4.6), (-1.0, 5.0, 1.2), 38, '跟着托盘出最后一层'),
    (16.3, (-2.4, 2.4, 6.6), (-0.6, 5.4, 2.4), 42, '跟拍「想」那串数（下面另有逐帧跟拍）'),
    (16.9, (-1.6, 0.9, 5.9), (0.0, 3.9, 2.7), 42, '继续跟随'),
    (17.5, (-0.6, -1.5, 3.6), (0.4, 2.0, 1.3), 42, '靠近候选区'),
    (18.4, (-0.5, -2.8, 3.4), (0.4, 1.6, 1.0), 38, '近景：候选和分数柱'),
    (19.6, (-0.8, -4.2, 4.6), (0.3, 0.8, 0.5), 35, '第三幕：候选进入分叉'),
    (21.0, (-1.0, -6.0, 6.4), (-0.3, 0.3, 0.3), 31, '远景：前缀 + 空位 + 两条分支起点'),
    (24.0, (-1.0, -6.4, 6.8), (-0.3, 0.2, 0.3), 31, '两条续写共享同一段前缀'),
    (25.4, (-1.0, -6.0, 6.4), (-0.3, 0.1, 0.3), 31, '落选退场'),
    (26.9, (-1.3, -4.8, 4.9), (-0.7, 0.1, 0.35), 34, '中景：「去」进入正式序列'),
    (28.4, (-1.3, -4.8, 5.2), (-0.6, 0.6, 0.6), 33, '第四幕：上下文更新为 周末我想去'),
    (30.2, (-1.4, -4.4, 6.6), (-0.8, 2.6, 0.9), 30, '中景：只把新字的数送进模型'),
    (32.4, (-1.3, -4.2, 6.8), (-0.6, 3.0, 1.0), 30, '回看前文、更新'),
    (34.4, (-0.9, -4.6, 6.0), (0.0, 1.2, 0.6), 31, '下一位置的候选 + 正式输出'),
    (39.6, (-0.9, -4.7, 6.0), (0.1, 1.0, 0.6), 31, '稳定构图：一步、两步、三步'),
    (40.8, (0.2, -6.0, 5.6), (1.0, -0.6, 0.4), 32, '第五幕：沿正式输出托盘往右'),
    (42.4, (2.4, -8.6, 6.8), (3.6, -1.6, 0.4), 30, '远景：揭示草稿轨和验证区'),
    (43.4, (6.4, -7.4, 5.0), (7.6, -2.6, 0.5), 34, '小模型推出草稿'),
    (44.9, (4.8, -7.0, 4.6), (5.4, -2.7, 0.5), 34, '草稿滑进验证通道'),
    (45.9, (4.8, -6.4, 4.2), (5.15, -2.75, 0.5), 30, '近景：集中验证'),
    (48.0, (4.8, -6.3, 4.1), (5.1, -2.75, 0.5), 30, '近景：接受 / 未接受'),
    (49.2, (2.4, -6.6, 5.3), (2.6, -1.2, 0.5), 32, '跟着海、边进入正式输出'),
    (50.3, (6.2, -7.4, 5.0), (6.6, -2.4, 0.5), 32, '吃、饭退回小模型'),
    (51.3, (4.6, -7.2, 5.2), (4.6, -1.8, 0.5), 32, '转向大模型输出口'),
    (52.6, (1.9, -6.6, 5.4), (1.9, -0.9, 0.45), 32, '跟着「看」到正式输出末端'),
    (53.6, (-0.9, -5.7, 5.6), (-0.45, 0.0, 0.4), 29, '结果：周末我想去海边看'),
    (55.2, (-3.4, -7.6, 4.4), (-3.4, -1.0, 1.4), 33, '第六幕：字沿托盘回到手机'),
    (57.2, (-6.0, -9.2, 2.8), (-6.0, -2.0, 2.5), 40, '回到手机'),
    (64.5, (-6.1, -9.4, 2.8), (-6.1, -2.0, 2.5), 40, '结尾'),
]

def cam_at(t):
    ts = [c[0] for c in CAM]
    i = max(0, min(len(CAM) - 2, max(k for k in range(len(ts)) if ts[k] <= t) if t >= ts[0] else 0))
    def herm(idx):
        p = [Vector(c[idx]) if idx < 3 else c[idx] for c in CAM]
        t0, t1 = ts[i], ts[i + 1]; u = clamp((t - t0) / (t1 - t0))
        P0 = p[max(i - 1, 0)]; P1 = p[i]; P2 = p[i + 1]; P3 = p[min(i + 2, len(p) - 1)]
        T0 = ts[max(i - 1, 0)]; T3 = ts[min(i + 2, len(ts) - 1)]
        m1 = (P2 - P0) * ((t1 - t0) / max(1e-6, (t1 - T0))); m2 = (P3 - P1) * ((t1 - t0) / max(1e-6, (T3 - t0)))
        h00 = 2 * u ** 3 - 3 * u ** 2 + 1; h10 = u ** 3 - 2 * u ** 2 + u; h01 = -2 * u ** 3 + 3 * u ** 2; h11 = u ** 3 - u ** 2
        return h00 * P1 + h10 * m1 + h01 * P2 + h11 * m2
    return tuple(herm(1)), tuple(herm(2)), herm(3)

SHOT = {'DUR': DUR, 'pose': pose, 'tracked': tracked}
build()
run(SHOT)
