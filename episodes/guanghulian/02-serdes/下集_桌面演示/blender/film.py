"""光互连 02 下集 · 桌面演示版：全片的场景和动画（文字分镜 v4 第九节的时码，timeline.json）。
rig.py 是 y6 试镜头那一版，留作记录；这里把同一套装置做成「按镜头配置」，并加上其余各拍要的道具。
小工具、材质、房间直接取 rig.py 里的那一段源码（见下面 exec），保证两边是同一套。

用法：
  blender -b -P film.py -- <tex目录> <素材目录> <输出> [缩放% 默认25] [采样 默认32] shot=<镜头> [key=value ...]
  still=<帧>        只渲一帧（<输出> 是 png），同时把这一帧的屏幕锚点写到 <输出>.json（合成贴字用）
  fs=<帧> fe=<帧>   渲一段，<输出> 是目录（f_0000.png …）；step=2 隔帧渲（草稿用）
  anchors=1         不渲染，把每帧的屏幕锚点写到 <输出>（json）
  其它：gpu=1 thr=<自适应阈值> mb=0 exposure fstop …
镜头名见 SHOTS。同一条时间线上切了机位的，一个机位一个镜头名（s34a / s34b / s34c、s9a / s9b、y6g / y6c），各渲各的帧段（RANGE），
这样切点两侧的运动模糊不会串。

坐标：纸带往 +x 走；窄缝在 SLIT_X。纸带上的位置用「过窄缝的帧数」t 表示：t 处的那一点在第 t 帧正好过窄缝，
第 f 帧时它在 x = SLIT_X + V·(f − t)。一格通常 20 帧（24 毫米）。
"""
import bpy, sys, math, json, os, time, random
import numpy as np
from math import sin, cos, radians, pi
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:]
TEX, DL, OUT = argv[0], argv[1], argv[2]
pos = [a for a in argv[3:] if "=" not in a]
SCALE = int(pos[0]) if len(pos) > 0 else 25
SAMPLES = int(pos[1]) if len(pos) > 1 else 32
P = dict(el=24, az=-18, exposure=0.55, sun=8.0, sky=0.8, fstop=4.0, lens=50, blind=0.66, mb=1, slat=14)
GLOW_DEFAULTS = dict(blind=0.15, slat=-50, exposure=2.9, fstop=5.6)
S = {}
for a in argv[3:]:
    if "=" in a:
        k, v = a.split("=")
        try: P[k] = float(v)
        except ValueError: S[k] = v
SHOT = S.get("shot", "y6c")

FPS, TB = 24, 20
CELL = 0.024
V = CELL / TB
SLIT_X, YR = 0.10, -0.06
RAIL_H = 0.008
Z_TAPE = RAIL_H + 0.00012
Y_NEAR, Y_M, Y_F, Y_FAR = YR - 0.021, YR - 0.008, YR + 0.018, YR + 0.021
Y_DOT = YR - 0.0145
TH_MAX = radians(22)
RX0, RX1 = -0.62, 0.76
PRN_X = SLIT_X - 24.5 * CELL
T_PRN = (SLIT_X - PRN_X) / V                 # 印头处的 t 比窄缝处大这么多帧（490）
X_SCR, X_DES = -0.33, 0.34                   # 打乱盒、还原盒
X_FIX = dict(fix1=0.060, fix2=-0.230, fix3=-0.130)
X_CUT = 0.47                                 # 切刀
PHONE = Vector((0.84, 0.035, 0.0))          # 手机（桌子右端，靠在小支架上）


# =====================================================================================================
# 镜头配置
# =====================================================================================================
def alt(n, w=20, first=0): return [((first + i) % 2, w) for i in range(n)]


def pose(t, dist, pitch, yaw, focus=None, lens=50, fstop=4.0): return dict(t=t, dist=dist, pitch=pitch, yaw=yaw, focus=focus, lens=lens, fstop=fstop)


# 机位。C1 读带口中景，C2 窄缝近景，C3 节拍器，D 发货端，E 整套装置，A 手机，G 暗场（上半纸带、下半电路板）
C1 = pose((SLIT_X - 0.012, YR + 0.045, 0.062), 0.84, 31, 5, (SLIT_X + 0.03, YR, 0.012))
C2 = pose((SLIT_X + 0.058, YR + 0.022, 0.040), 0.66, 40, 3, (SLIT_X + 0.03, YR, 0.012))
C1W = pose((SLIT_X + 0.12, YR + 0.03, 0.05), 1.15, 33, 4, (SLIT_X + 0.06, YR, 0.012))
C3 = pose((SLIT_X - 0.030, YR + 0.050, 0.040), 0.72, 20, 6, (SLIT_X - 0.05, YR + 0.07, 0.08))
D1 = pose((PRN_X + 0.03, YR + 0.005, 0.035), 0.66, 30, -7, (PRN_X + 0.03, YR, 0.012))
W0 = pose((-0.08, -0.30, 0.0), 1.75, 60, 0, (0.0, -0.06, 0.02), lens=28, fstop=9.0)          # 整套装置：正面俯拍，从纸带卷到切刀都在画面里
W1 = pose((0.14, -0.04, 0.03), 1.36, 40, 12, (0.10, -0.06, 0.02), lens=35, fstop=8.0)        # 三只修字盒、插线板、两只表
M1 = pose((0.465, 0.10, 0.085), 0.46, 12, 6, (0.45, 0.09, 0.09), lens=50)                   # 两只表
A1 = pose((PHONE.x, PHONE.y - 0.02, 0.100), 0.26, 14, 0, (PHONE.x, PHONE.y + 0.035, 0.10))
G1 = pose((SLIT_X + 0.012, YR - 0.085, 0.0), 0.80, 47, 4, (SLIT_X - 0.02, YR - 0.19, 0.004))


def shift(p, dx=0, dy=0, dz=0, **kw):
    q = dict(p); q["t"] = (p["t"][0] + dx, p["t"][1] + dy, p["t"][2] + dz)
    if p["focus"]: q["focus"] = (p["focus"][0] + dx, p["focus"][1] + dy, p["focus"][2])
    q.update(kw); return q


ALL = {"scr", "des", "fix1", "fix2", "fix3", "meters", "cutter"}       # 桌沿的「整套 = SerDes」签只在 y9 的全景里
SHOTS, RANGE = {}, {}
# y1 手机：消息从「七」字起变乱码
SHOTS["y1"] = dict(n=60, cells=alt(8), cam=[(0, shift(A1, dist=0.285)), (60, A1)], phone=("y1", 60))
# y2 跟着纸带横移：托盘 → 印带器 → 读带口
SHOTS["y2"] = dict(n=102, cells=alt(40), cards=True,
                   cam=[(0, shift(D1, dx=-0.10, dy=-0.03)), (14, shift(D1, dx=-0.09, dy=-0.03)), (84, shift(C1, dx=-0.03)), (102, C1)])
# y3 发货端：切入时黑带已印出四格，第 10 帧印第五下。印头处的格子 = 窄缝处 t 再加 490 帧
SHOTS["y3d"] = dict(n=36, cells=alt(21, first=0) + [(1, 20)] * 5 + [(0, 20)], cards=True, cam=[(0, D1), (36, shift(D1, dx=0.012))])
# y3 窄缝 + y4 读带口（同一条时间线）：第 0 帧长黑带进窄缝；没对过的节拍器 24.5 帧一下，只盖下四个实心点
_slow = [2.5 + 25 * k for k in range(-12, 16)]            # 四个点落在每格的 1/8、3/8、5/8、7/8 处；第五下落在黑带后 3 毫米的白格里
_s34 = dict(n=258, cells=[(1, 20)] * 5 + [(0, 20)] * 12, pre=[(0, 20)] * 3 + alt(30, first=1), rights=_slow, coral_lamp=(104, None),   # 长黑带前后都是白：只有黑带下面是实心点
            counter=[(0, 0), (2.5, 1), (27.5, 2), (52.5, 3), (77.5, 4)], marks=dict(dot1=2.5, band=50),
            ruler=dict(t=20, cells=8, land=(120, 132), lift=(230, 248)))
SHOTS["s34a"] = dict(_s34, cam=[(0, C2), (90, shift(C2, dx=0.004))]); RANGE["s34a"] = (0, 89)                       # y3 窄缝
SHOTS["s34b"] = dict(_s34, cam=[(90, shift(C1, dx=0.03)), (187, shift(C1, dx=0.13))]); RANGE["s34b"] = (90, 186)    # y4 前段
SHOTS["s34c"] = dict(_s34, cam=[(228, shift(C1, dx=0.17)), (258, shift(C1, dx=0.18))]); RANGE["s34c"] = (228, 257)  # y4 末段：尺被抽走
# y4 发货端：发货端的节拍器想跟着走，被挡片挡停
SHOTS["y4d"] = dict(n=41, cells=alt(40), gate=(2, 12), cam=[(0, pose((PRN_X + 0.125, YR + 0.04, 0.075), 0.66, 22, -5, (PRN_X + 0.135, YR + 0.03, 0.05))), (41, pose((PRN_X + 0.130, YR + 0.04, 0.075), 0.63, 22, -5, (PRN_X + 0.135, YR + 0.03, 0.05)))])
# y5 节拍器：鼓在 10、30、50…；「嗒」（摆到左头）比鼓晚 6、3、1、0 帧
_lefts = [16 - 24.5 * k for k in range(12, 0, -1)] + [16, 33, 51] + [70 + 20 * k for k in range(8)]
SHOTS["y5"] = dict(n=120, cells=[(0, 10)] + alt(12, first=1), pre=alt(30, first=0), lefts=_lefts,
                   cam=[(0, C3), (120, shift(C3, dx=0.01, dist=0.64))])
# y6：第 0–120 帧黑白相间，第 140 帧进长黑带，第 240 帧出。前 96 帧是暗场（发光信号）
_y6 = dict(n=270, cells=alt(7, first=0) + [(1, 20)] * 5 + [(0, 20)], sign=("flip", 10, 22), marks=dict(band=190))
SHOTS["y6g"] = dict(_y6, glow=True, cam=[(0, G1), (96, shift(G1, dx=0.006, dy=-0.006, dist=0.75))]); RANGE["y6g"] = (0, 95)
SHOTS["y6c"] = dict(_y6, cam=[(96, C1), (112, C1), (238, C2), (270, shift(C2, dx=0.003))]); RANGE["y6c"] = (96, 269)
# y7 一长串全是 1：节拍器 23 帧一下，没人纠正；第五个点滑过格边
_r7 = [-10 - 20 * k for k in range(12, -1, -1)] + [10 + 23 * k for k in range(1, 8)]
SHOTS["y7"] = dict(n=114, cells=[(1, 20)] * 40, pre=[(1, 20)] * 2 + alt(30, first=0), rights=sorted(_r7 + [10]), coral_dots=[102], coral_lamp=(106, None),
                   sign="B", ruler=dict(t=60, cells=12), cam=[(0, shift(C2, dx=-0.01)), (114, shift(C2, dx=0.02, dist=0.63))])
# y8 发货端：长黑带进打乱盒，出来是花带
SHOTS["y8d"] = dict(n=71, scr=True, orig=[(1, 20)] * 80, orig_pre=[(1, 20)] * 40, cells="random", sign="B", props={"scr", "des"},
                    cam=[(0, pose((X_SCR + 0.02, YR + 0.005, 0.035), 0.82, 30, -6, (X_SCR, YR, 0.02))), (71, pose((X_SCR + 0.035, YR + 0.005, 0.035), 0.79, 30, -6, (X_SCR, YR, 0.02)))])
# y8 读带口：鼓回来；花带过还原盒，出来还是长黑带
SHOTS["y8c"] = dict(n=85, scr=True, orig=[(1, 20)] * 80, orig_pre=[(1, 20)] * 40, cells="random", sign="B", props={"scr", "des"},
                    cam=[(0, shift(C1W, dx=0.05)), (85, shift(C1W, dx=0.07, dist=1.11))])
# y9 整套装置；桌沿落下「整套 = SerDes」
SHOTS["y9e"] = dict(n=94, scr=True, orig="random", cells="random", sign="B", props={"scr", "des", "meters", "cutter", "serdes"}, serdes=(62, 70),
                    cam=[(0, W0), (94, shift(W0, dist=1.72))])
# y9 窄缝 + y10 + y11（同一条时间线）：第 10 帧起格子窄一半；第 62 帧起是 y10，第 254 帧起是 y11（第 297 帧起再窄一档）
_s9cells = alt(29, w=10, first=0)
_s9cells += alt(140, w=5, first=(_s9cells[-1][0] + 1) % 2)
_s9 = dict(n=374, scr=True, orig="random", cells=_s9cells, pre=alt(4, w=10, first=1) + alt(30, first=1), sign="B", props=set(ALL),
           g=[(-9999, 0.35), (72, 1.0), (62 + 95 + 33, 0.5), (62 + 151, 0.1)],
           drops=dict(fix1=62 + 95, fix2=62 + 125, fix3=62 + 144), needle_big=[(0, 0.25), (62 + 154, 0.25), (62 + 178, 0.80), (374, 0.82)],
           needle_small=[(0, 0.70), (254 + 92, 0.70), (254 + 99, 0.48), (254 + 105, 0.60), (254 + 114, 0.40), (374, 0.42)])
SHOTS["s9a"] = dict(_s9, cam=[(0, shift(C2, dx=-0.05)), (62, shift(C2, dx=-0.045))]); RANGE["s9a"] = (0, 61)                           # y9 窄缝
SHOTS["s9b"] = dict(_s9, cam=[(62, shift(C2, dx=-0.045)), (62 + 86, shift(C1W, dx=-0.10)), (62 + 100, shift(C1W, dx=-0.10)),
                              (62 + 156, W1), (254, shift(W1, dist=1.86)), (374, M1)]); RANGE["s9b"] = (62, 373)   # y10 + y11
# y12 读带口：蓝点稳稳地一个接一个（6 毫米一格）
SHOTS["y12c"] = dict(n=31, scr=True, orig="random", cells=alt(200, w=5), pre=alt(120, w=5, first=1), sign="B", props=set(ALL), fixed=True, needle_big=[(0, 0.82)], needle_small=[(0, 0.42)],
                     g=[(-9999, 0.1)], cam=[(0, C1), (31, shift(C1, dx=0.01, dist=0.80))])
# y12 暗场：格子从 6 毫米窄到 3 毫米，走线上是带细闪的金色流光
SHOTS["y12g"] = dict(n=55, glow=True, scr=True, orig="random", cells=alt(3, w=5) + alt(260, w=2.5, first=1), pre=alt(120, w=5, first=1), sign="B", props=set(ALL), fixed=True,
                     g=[(-9999, 0.1)], cam=[(0, G1), (55, shift(G1, dx=0.005, dy=-0.005, dist=0.76))])
# y12 手机：乱码从「七」字起一个个变回来
SHOTS["y12a"] = dict(n=76, cells=alt(8), props=set(ALL), fixed=True, cam=[(0, A1), (76, shift(A1, dist=0.34))], phone=("y12", 76))
# y13 读带口 → 切刀 → 托盘：一格切一段，拆回一排
SHOTS["y13"] = dict(n=120, scr=True, orig=alt(60), orig_pre=alt(60, first=1), cells="random",     # 切下来的八段和 y2 左托盘那八张同一组黑白
                    sign="B", props=set(ALL), fixed=True, cut=True, needle_big=[(0, 0.82)], needle_small=[(0, 0.42)],
                    g=[(-9999, 0.1)], cam=[(0, C1), (22, C1), (88, pose((0.69, -0.09, 0.03), 0.92, 38, 3, (0.62, -0.14, 0.01))), (120, pose((0.695, -0.09, 0.03), 0.90, 38, 3, (0.62, -0.14, 0.01)))])
# y14 手机 + 路线图小卡
SHOTS["y14"] = dict(n=96, cells=alt(8), props=set(ALL), fixed=True, route=(8, 16), cam=[(0, shift(A1, dx=-0.02, dz=-0.05, dist=0.46)), (96, shift(A1, dx=-0.02, dz=-0.05, dist=0.44))], phone=("clean", 1))

SP = SHOTS[SHOT]
NF = SP["n"]
G = bool(SP.get("glow"))
PROPS = SP.get("props", set()) | {"cutter"}                # 切刀和右托盘从头就在桌子右端
if G:
    for k, v in GLOW_DEFAULTS.items():
        if not any(a.startswith(k + "=") for a in argv[3:]): P[k] = v

# =====================================================================================================
# 纸带上的图样（按 t 排）
# =====================================================================================================
T_LO, T_HI = -(RX1 - SLIT_X) / V - 60, T_PRN + NF + 80
rng_pat = random.Random(11)


def rand_cells(n, w=20, seed=5):
    r = random.Random(seed); out = []; run = 0; last = None
    for _ in range(n):
        b = r.randint(0, 1)
        if b == last and run >= 2: b = 1 - b
        run = run + 1 if b == last else 1; last = b; out.append((b, w))
    return out


def pattern(cells, pre):
    """返回 [(t0, t1, bit)]，盖住 [T_LO, T_HI]。cells 从 t = 0 往后排，pre 从 t = 0 往前排；不够的用黑白相间补。"""
    if cells == "random": cells = rand_cells(200)
    if pre == "random": pre = rand_cells(60, seed=9)
    out, t = [], 0.0
    for b, w in cells: out.append((t, t + w, b)); t += w
    b = 1 - out[-1][2]
    while t < T_HI: out.append((t, t + TB, b)); t += TB; b = 1 - b
    pl, t = [], 0.0
    for b, w in (pre or []): pl.append((t - w, t, b)); t -= w
    b = 1 - (pl[-1][2] if pl else out[0][2])
    while t > T_LO: pl.append((t - TB, t, b)); t -= TB; b = 1 - b
    return pl[::-1] + out


PAT_A = pattern(SP["cells"], SP.get("pre"))                                   # 窄缝看到的（打乱盒和还原盒之间）
if not SP.get("scr"): PAT_B = PAT_A
elif SP["orig"] == "random":                                                  # 打乱前 / 还原后：格子的宽窄和位置不变，只是另一组 0 和 1
    _r = random.Random(21); PAT_B = []; run = 0; last = None
    for a_, b_, _ in PAT_A:
        bit = _r.randint(0, 1)
        if bit == last and run >= 2: bit = 1 - bit
        run = run + 1 if bit == last else 1; last = bit; PAT_B.append((a_, b_, bit))
else: PAT_B = pattern(SP["orig"], SP.get("orig_pre"))


def cell_at(pat, t):
    lo, hi = 0, len(pat) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if pat[mid][1] <= t: lo = mid + 1
        else: hi = mid
    return pat[lo]


def bit_at(pat, t): return cell_at(pat, t)[2]


def edges(pat): return [(a[1], min(a[1] - a[0], b[1] - b[0])) for a, b in zip(pat[:-1], pat[1:]) if a[2] != b[2]]


PXF = 4                                                                       # 每帧 4 个像素（0.3 毫米 / 像素）
NPX = int((T_HI - T_LO) * PXF)
G_STEPS = SP.get("g", [(-9999, 0.35)])                                        # 洇墨的程度（到窄缝时），按 t 分段


def g_at(t):
    v = G_STEPS[0][1]
    for t0, gv in G_STEPS:
        if t >= t0: v = gv
    return v


def pat_image(name, pat):
    tt = T_LO + (np.arange(NPX) + 0.5) / PXF
    crisp = np.zeros(NPX, np.float32)
    for t0, t1, b in pat:
        if b: crisp[max(0, int((t0 - T_LO) * PXF)):max(0, int((t1 - T_LO) * PXF))] = 1.0
    sig = 0.004 / V * PXF                                                     # 洇边：σ = 4 毫米，和格子宽窄无关
    r = int(sig * 3); k = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2); k /= k.sum()
    blur = np.convolve(np.pad(crisp, r, mode="edge"), k, mode="valid")
    gg = np.array([g_at(t) for t in tt[::PXF * 5]], np.float32).repeat(PXF * 5)[:NPX]
    gg = np.convolve(np.pad(gg, 40, mode="edge"), np.ones(81) / 81, mode="valid")
    bleed = crisp * (1 - gg) + blur * gg
    px = np.zeros((2, NPX, 4), np.float32); px[..., 0] = crisp; px[..., 1] = bleed; px[..., 3] = 1
    img = bpy.data.images.new(name, NPX, 2, float_buffer=True, is_data=True)
    img.pixels.foreach_set(px.ravel()); img.update(); img.pack()
    return img


# =====================================================================================================
# 小工具、材质、房间：取 rig.py 里的同一段源码
# =====================================================================================================
_src = open(os.path.join(HERE, "rig.py"), encoding="utf-8").read()
exec(_src[_src.index("bpy.ops.wm.read_factory_settings"):_src.index("# ---------- 导轨")], globals())
bpy.data.objects.remove(bpy.data.objects["desk"])                                       # 桌子往镜头这边加深：大全景里下半个画面也是桌面
box("desk", -0.80, 1.00, -1.35, 0.40, -0.032, 0.0, WOOD, bevel=0.0015)
M_BLUE_T = M_BLUE.copy()
M_CORAL, _ = principled("dot_coral", **{"Base Color": (0.80, 0.16, 0.10, 1), "Roughness": 0.42})
box("rail", RX0, RX1, YR - 0.027, YR + 0.027, 0, RAIL_H, M_RAIL, bevel=0.0006)
box("rail_lip_n", RX0, RX1, YR - 0.027, YR - 0.0235, RAIL_H, RAIL_H + 0.0022, M_RAIL, bevel=0.0005)
box("rail_lip_f", RX0, RX1, YR + 0.0235, YR + 0.027, RAIL_H, RAIL_H + 0.0022, M_RAIL, bevel=0.0005)


def keys_val(sock, pairs, kind="LINEAR"):
    for f, v in pairs:
        sock.default_value = v; sock.keyframe_insert("default_value", frame=f)


def tex_quad(name, p, ux, uy, w, h, tex, mat=None, emit=0.0):
    """一张贴了图的小牌：中心 p，沿 ux 宽 w、沿 uy 高 h。"""
    ux, uy = Vector(ux).normalized(), Vector(uy).normalized(); p = Vector(p)
    v = [tuple(p - ux * w / 2 - uy * h / 2), tuple(p + ux * w / 2 - uy * h / 2), tuple(p + ux * w / 2 + uy * h / 2), tuple(p - ux * w / 2 + uy * h / 2)]
    o = add_obj(name, mesh_from(name, v, [(0, 1, 2, 3)], uvs=[(0, 0), (1, 0), (1, 1), (0, 1)]))
    o.data.materials.append(mat or mat_paper_tex(name, f"{TEX}/{tex}.png"))
    return o


# =====================================================================================================
# 纸带
# =====================================================================================================
TAPE_X1 = X_CUT if "cutter" in PROPS else 0.74
IMG_A = pat_image("pat_a", PAT_A)
IMG_B = pat_image("pat_b", PAT_B) if SP.get("scr") else IMG_A
M_TAPE, bt = principled("tape_data", Roughness=0.78)
bt.inputs["Sheen Weight"].default_value = 0.15
bump(M_TAPE, bt, 2500, 0.25, 0.00004)
nt = M_TAPE.node_tree
uvn = nt.nodes.new("ShaderNodeUVMap")
geo = nt.nodes.new("ShaderNodeNewGeometry"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sep.inputs[0])


def tex_rg(img):
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; t.interpolation = "Linear"; t.extension = "EXTEND"
    nt.links.new(uvn.outputs["UV"], t.inputs["Vector"])
    s_ = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(t.outputs["Color"], s_.inputs[0]); return s_


def nmath(op, a, b=None, clamp=False):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
    for i, x in enumerate((a, b)):
        if x is None: continue
        if isinstance(x, (int, float)): n.inputs[i].default_value = x
        else: nt.links.new(x, n.inputs[i])
    return n.outputs[0]


def mixf(fac, a, b):
    n = nt.nodes.new("ShaderNodeMix"); n.data_type = "FLOAT"
    nt.links.new(fac, n.inputs[0]); nt.links.new(a, n.inputs[2]); nt.links.new(b, n.inputs[3]); return n.outputs[0]


sa = tex_rg(IMG_A)
if SP.get("scr"):
    sb = tex_rg(IMG_B)
    zone = nmath("MULTIPLY", nmath("GREATER_THAN", sep.outputs["X"], X_SCR), nmath("LESS_THAN", sep.outputs["X"], X_DES))
    crisp, bleed = mixf(zone, sb.outputs[0], sa.outputs[0]), mixf(zone, sb.outputs[1], sa.outputs[1])
else:
    crisp, bleed = sa.outputs[0], sa.outputs[1]
wx = nmath("DIVIDE", nmath("SUBTRACT", sep.outputs["X"], PRN_X), SLIT_X - PRN_X, clamp=True)   # 洇边随走过的路变宽：印头处 0，到窄缝处 1
kk = mixf(wx, crisp, bleed)
mc = nt.nodes.new("ShaderNodeMix"); mc.data_type = "RGBA"
mc.inputs[6].default_value = (0.84, 0.82, 0.76, 1); mc.inputs[7].default_value = (0.012, 0.012, 0.014, 1)
nt.links.new(kk, mc.inputs[0]); nt.links.new(mc.outputs[2], bt.inputs["Base Color"])
M_PAPER_T = M_PAPER.copy()
cut_outside(M_TAPE, PRN_X - 0.004, TAPE_X1); cut_outside(M_PAPER_T, PRN_X - 0.004, TAPE_X1)
xa, xb = SLIT_X - V * T_HI, SLIT_X - V * T_LO
verts, faces, luv = [], [], []
for r, (y0, y1) in enumerate(((Y_NEAR, Y_M), (Y_M, Y_F), (Y_F, Y_FAR))):
    n = len(verts)
    verts += [(xa, y0, Z_TAPE), (xb, y0, Z_TAPE), (xb, y1, Z_TAPE), (xa, y1, Z_TAPE)]
    faces.append((n, n + 1, n + 2, n + 3)); luv.append([(1, 0), (0, 0), (0, 1), (1, 1)])
tape = add_obj("tape", mesh_from("tape", verts, faces, loop_uvs=luv))
tape.data.materials.append(M_PAPER_T); tape.data.materials.append(M_TAPE)
tape.data.polygons[1].material_index = 1
tape.location.x = -V * 5; tape.keyframe_insert("location", frame=-5)
tape.location.x = V * (NF + 5); tape.keyframe_insert("location", frame=NF + 5)
set_interp(tape, "LINEAR")


def tape_x(t): return SLIT_X - V * t          # 纸带物体坐标系里，t 处的 x


# =====================================================================================================
# 节拍器（摆到右头盖点）
# =====================================================================================================
def periods(R): return [R[i + 1] - R[i] if i + 1 < len(R) else R[-1] - R[-2] for i in range(len(R))]


def amp_for(p): return TH_MAX * max(0.16, min(1.0, (p / TB) ** 0.75))


def theta_fn(R):
    """R：摆到右头的时刻（帧）。右头永远在 +TH_MAX（盖点臂正好落到纸带上）；摆得快时左头收得近。"""
    R = sorted(R)

    def th(f):
        if f <= R[0]: k = 0
        elif f >= R[-1]: k = len(R) - 2
        else:
            k = max(i for i in range(len(R) - 1) if R[i] <= f)
        p = R[k + 1] - R[k]
        return TH_MAX - amp_for(p) * (1 - cos(2 * pi * (f - R[k]) / p))
    return th


def swing(pend, R):
    th = theta_fn(R); R = sorted(R)
    pmin = min(b - a for a, b in zip(R[:-1], R[1:]) if a < NF + 5 and b > -5) if len(R) > 1 else TB
    step = 1.0 if pmin >= 8 else 0.25
    f = -2.0
    while f <= NF + 2:
        pend.rotation_euler = (0, th(f), 0); pend.keyframe_insert("rotation_euler", frame=f); f += step
    if step < 1: set_interp(pend, "LINEAR")


def auto_rights(pat, lo, hi): return [(a + b) / 2 for a, b, _ in pat if b > lo and a < hi]


if "rights" in SP: RIGHTS = sorted(SP["rights"])
elif "lefts" in SP:
    L = SP["lefts"]; RIGHTS = [(a + b) / 2 for a, b in zip(L[:-1], L[1:])]
    RIGHTS = [RIGHTS[0] - (RIGHTS[1] - RIGHTS[0]) * k for k in range(3, 0, -1)] + RIGHTS
else:
    RIGHTS = auto_rights(PAT_A, -420, NF + 60)
    rj = random.Random(4)
    RIGHTS = [r + rj.uniform(-1, 1) * 3.0 * max(0.0, (g_at(r) - 0.3) / 0.7) * min(1.0, (cell_at(PAT_A, r)[1] - cell_at(PAT_A, r)[0]) / 10) for r in RIGHTS]
    RIGHTS = sorted(RIGHTS)
while RIGHTS[-1] < NF + 30: RIGHTS.append(RIGHTS[-1] + (RIGHTS[-1] - RIGHTS[-2]))
PER = dict(zip(RIGHTS, periods(RIGHTS)))

# ---------- 蓝点 ----------
random.seed(3)


def dot(t, solid, coral, rad):
    seg, verts = 28, [(0, 0, 0)]
    ph = [random.uniform(0, 6.28) for _ in range(3)]
    for s in range(seg):
        a = 2 * pi * s / seg
        r = rad * (1 + 0.035 * sin(3 * a + ph[0]) + 0.025 * sin(5 * a + ph[1]) + 0.015 * sin(9 * a + ph[2]))
        verts.append((r * cos(a), r * sin(a), 0))
    if solid: faces = [(0, 1 + s, 1 + (s + 1) % seg) for s in range(seg)]
    else:
        verts += [(0.72 * x, 0.72 * y, 0) for x, y, _ in verts[1:]]
        faces = [(1 + s, 1 + (s + 1) % seg, 1 + seg + (s + 1) % seg, 1 + seg + s) for s in range(seg)]
    o = add_obj("dot", mesh_from("dot", verts, faces)); o.data.materials.append(M_CORAL_T if coral else M_BLUE_T)
    o.location = (tape_x(t) + random.uniform(-0.0003, 0.0003), Y_DOT + random.uniform(-0.0003, 0.0003), Z_TAPE + 0.00003)
    o.parent = tape
    if t > -2:
        o.scale = (0, 0, 0); o.keyframe_insert("scale", frame=-5)
        o.scale = (1, 1, 1); o.keyframe_insert("scale", frame=t)
        set_interp(o, "CONSTANT")


# 蓝点只在纸带上：有还原盒时到盒子里为止（还原以后带上是原来的数据，清点的记号不跟过去），否则到纸带尽头
M_CORAL_T = M_CORAL.copy()                               # 只给蓝点用的那份才裁；表针也用珊瑚色，不能跟着裁掉
for m_ in (M_BLUE_T, M_CORAL_T): cut_outside(m_, PRN_X, X_DES - 0.02 if "des" in PROPS else (X_CUT if "cutter" in PROPS else 0.74))
CORAL = SP.get("coral_dots", [])
STAMPS = [r for r in RIGHTS if -330 < r <= NF + 1]
for r in STAMPS:
    dot(r, bool(bit_at(PAT_A, r)), any(abs(r - c) < 0.6 for c in CORAL), 0.0040 * max(0.28, min(1.0, PER[r] / TB)))

# =====================================================================================================
# 读带口、小灯、计数器、纸签（尺寸同 rig.py）
# =====================================================================================================
SW = 0.0025
GX0, GX1 = SLIT_X - 0.024, SLIT_X + 0.024
PZ0, PZ1 = RAIL_H + 0.0030, RAIL_H + 0.0045
box("gate_block", GX0, GX1, YR + 0.0275, YR + 0.060, 0, PZ0, PLY, bevel=0.0008)
PY0, PY1 = Y_M - 0.0005, YR + 0.058
SY0, SY1 = Y_M + 0.0015, Y_F - 0.0015
for nm_, (a, b_, c, d_) in {"l": (GX0, SLIT_X - SW, PY0, PY1), "r": (SLIT_X + SW, GX1, PY0, PY1),
                            "n": (SLIT_X - SW, SLIT_X + SW, PY0, SY0), "f": (SLIT_X - SW, SLIT_X + SW, SY1, PY1)}.items():
    box("gate_plate_" + nm_, a, b_, c, d_, PZ0, PZ1, M_BRASS)
for sx in (GX0 + 0.005, GX1 - 0.005):
    cyl("gate_screw", (sx, YR + 0.044, PZ1), (sx, YR + 0.044, PZ1 + 0.0012), 0.0024, M_STEEL, 16)


def lamp(name, at, rad, color, base):
    cyl(name + "_bezel", at, at + Vector((0, 0, 0.0018)), rad * 1.35, M_STEEL, 24)
    m, b = principled(name, **{"Base Color": base, "Roughness": 0.25})
    b.inputs["Emission Color"].default_value = (*color, 1); b.inputs["Emission Strength"].default_value = 0.0
    d = lathe(name + "_dome", [(rad * cos(radians(a)), rad * sin(radians(a))) for a in range(0, 91, 10)], 24, [m], split=0)
    d.location = at + Vector((0, 0, 0.0016))
    return m, b.inputs["Emission Strength"]


LAMP = Vector((SLIT_X + 0.0125, YR + 0.005, PZ1))
M_LAMP, es = lamp("lamp", LAMP, 0.0034, (1.0, 0.50, 0.10), (0.75, 0.33, 0.04, 1))
EDGES = [(t, w) for t, w in edges(PAT_A) if -6 <= t <= NF + 2]
for t, w in EDGES:
    gain = 1.0 - max(0.0, (g_at(t) - 0.35) / 0.65) * (1.0 if w < 15 else 0.0) * 0.92      # 洇糊了以后，窄格的交界小灯几乎不亮
    k = min(1.0, w / TB)
    keys_val(es, [(t - 1 * k, 0.0), (t, 90.0 * gain), (t + 1 * k, 55.0 * gain), (t + 2 * k, 18.0 * gain), (t + 4 * k, 0.0)])
if EDGES: set_interp(M_LAMP.node_tree, "LINEAR")

CX, CY, CZ, WR, WW = SLIT_X + 0.085, YR + 0.056, 0.040, 0.026, 0.024
PHI_W = radians(138)
seg = 90
verts, luv, faces = [], [], []
for s in range(seg + 1):
    a = 2 * pi * s / seg
    for xx in (-WW / 2, WW / 2): verts.append((xx, WR * cos(a), WR * sin(a)))
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


# 计数：新一段黑带进来清零，每盖一个实心点加一（格子窄于 15 帧时不数，轮子转不过来）
events = [(t, "reset") for t, w in edges(PAT_A) if bit_at(PAT_A, t + 0.01) == 1] + \
         [(r, "inc") for r in RIGHTS if bit_at(PAT_A, r) == 1]                          # 窄格也是同一条规则，轮子在 0 和 1 之间飞快地翻
run, count_keys = 0, []
for t, ev in sorted(e for e in events if -400 < e[0] <= NF + 2):
    run = 0 if ev == "reset" else run + 1
    count_keys.append((t, run % 10))
if "counter" in SP: count_keys = list(SP["counter"])
prev = 0
for t, n_ in count_keys:
    if t < -3: prev = n_
whub.rotation_euler = (wheel_rot(prev), 0, 0); whub.keyframe_insert("rotation_euler", frame=-6)
for t, n_ in count_keys:
    if t < -3: continue
    whub.rotation_euler = (wheel_rot(prev), 0, 0); whub.keyframe_insert("rotation_euler", frame=t)
    whub.rotation_euler = (wheel_rot(n_), 0, 0); whub.keyframe_insert("rotation_euler", frame=t + 3)
    prev = n_
if count_keys and min(b_ - a_ for (a_, _), (b_, _) in zip(count_keys[:-1], count_keys[1:])) < 6 if len(count_keys) > 1 else False: set_interp(whub, "LINEAR")
HX0, HX1 = CX - WW / 2 - 0.0012, CX + WW / 2 + 0.0012
HT = CZ + WR + 0.006
for nm_, (a, b_) in {"l": (HX0 - 0.006, HX0), "r": (HX1, HX1 + 0.006)}.items():
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
# 计数器旁的珊瑚色小灯：数错时亮
CORAL_LAMP = Vector((HX1 + 0.016, CY - 0.020, 0.0))
box("coral_post", CORAL_LAMP.x - 0.006, CORAL_LAMP.x + 0.006, CORAL_LAMP.y - 0.006, CORAL_LAMP.y + 0.006, 0, 0.026, PLY, bevel=0.0008)
M_CL, ecl = lamp("coral_lamp", CORAL_LAMP + Vector((0, 0, 0.026)), 0.0042, (1.0, 0.16, 0.08), (0.55, 0.10, 0.06, 1))
if SP.get("coral_lamp"):
    f0, f1 = SP["coral_lamp"]
    keys_val(ecl, [(f0 - 1, 0.0), (f0 + 1, 7.0)] + ([(f1, 7.0), (f1 + 3, 0.0)] if f1 else []))
    set_interp(M_CL.node_tree, "LINEAR")

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
sgn = SP.get("sign", "A")
sg = empty("sign_pivot", SG, (radians(-22 + (180 if sgn == "B" else 0)), 0, 0)); card.parent = sg
for sx in (-1, 1):
    cyl("sign_pin", SG + Vector((sx * (SGW / 2 - 0.0005), 0, 0)), SG + Vector((sx * (SGW / 2 + 0.004), 0, 0)), 0.0007, M_STEEL, 10)
    px = CX + sx * (SGW / 2 + 0.004)
    cyl("sign_post", (px, SG.y, HT - 0.001), (px, SG.y, SG.z + 0.002), 0.0013, M_BRASS, 12)
box("sign_base", CX - SGW / 2 - 0.008, CX + SGW / 2 + 0.008, SG.y - 0.006, SG.y + 0.006, HT, HT + 0.003, M_BRASS, bevel=0.0006)
if isinstance(sgn, tuple):
    sg.keyframe_insert("rotation_euler", frame=sgn[1])
    sg.rotation_euler = (radians(-22 + 180), 0, 0); sg.keyframe_insert("rotation_euler", frame=sgn[2])


# =====================================================================================================
# 节拍器（建模同 rig.py；所有零件挂在一个根上，方便整只挪动）
# =====================================================================================================
def metronome(name, cx, y_front, R, crank_to=None):
    root = empty(name + "_root", (0, 0, 0))
    made = []

    def keep(o): made.append(o); return o
    b, t, H = 0.055, 0.019, 0.215
    cy = y_front + b
    v = [(cx - b, cy - b, 0), (cx + b, cy - b, 0), (cx + b, cy + b, 0), (cx - b, cy + b, 0),
         (cx - t, cy - t, H), (cx + t, cy - t, H), (cx + t, cy + t, H), (cx - t, cy + t, H)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    body = keep(add_obj(name + "_body", mesh_from(name + "_body", v, f))); body.data.materials.append(WALNUT)
    bm = body.modifiers.new("bev", "BEVEL"); bm.width = 0.002; bm.segments = 3
    keep(box(name + "_plinth", cx - b - 0.004, cx + b + 0.004, cy - b - 0.004, cy + b + 0.004, 0, 0.012, WALNUT, bevel=0.0015))
    keep(cyl(name + "_cap", (cx, cy, H), (cx, cy, H + 0.004), 0.011, M_BRASS, 24))
    sl = (b - t) / H

    def face_quad(nm, z0, z1, hw0, hw1, off, mat, uv=None):
        q = [(cx - hw0, y_front + sl * z0 - off, z0), (cx + hw0, y_front + sl * z0 - off, z0),
             (cx + hw1, y_front + sl * z1 - off, z1), (cx - hw1, y_front + sl * z1 - off, z1)]
        o = add_obj(nm, mesh_from(nm, q, [(0, 1, 2, 3)], uvs=uv)); o.data.materials.append(mat); return keep(o)
    face_quad(name + "_panel", 0.030, 0.203, 0.031, 0.0125, 0.0012, M_FELT)
    face_quad(name + "_scaleplate", 0.078, 0.198, 0.0075, 0.0075, 0.0016, mat_paper_tex(name + "_scale", f"{TEX}/scale.png"), uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
    PV = Vector((cx, y_front - 0.007, 0.060))
    keep(cyl(name + "_boss", (cx, PV.y - 0.003, PV.z), (cx, y_front + sl * PV.z, PV.z), 0.0045, M_BRASS, 24))
    pend = empty(name + "_pend", PV); made.append(pend)
    rod = box(name + "_rod", cx - 0.0016, cx + 0.0016, PV.y - 0.0006, PV.y + 0.0006, PV.z - 0.012, PV.z + 0.150, M_STEEL)
    child(rod, pend, PV)
    # 游码：摆得越快，游码越靠下（机械节拍器就是这样调速的）
    pmin = min([b_ - a_ for a_, b_ in zip(R[:-1], R[1:]) if -5 < a_ < NF] or [TB])
    wz = PV.z + 0.030 + 0.066 * max(0.0, min(1.0, (pmin - 2.5) / 17.5))
    wv = [(cx - 0.0125, PV.y - 0.0035, wz), (cx + 0.0125, PV.y - 0.0035, wz), (cx + 0.0125, PV.y + 0.0035, wz), (cx - 0.0125, PV.y + 0.0035, wz),
          (cx - 0.0085, PV.y - 0.0035, wz + 0.018), (cx + 0.0085, PV.y - 0.0035, wz + 0.018), (cx + 0.0085, PV.y + 0.0035, wz + 0.018), (cx - 0.0085, PV.y + 0.0035, wz + 0.018)]
    wt = add_obj(name + "_weight", mesh_from(name + "_weight", wv, f)); wt.data.materials.append(M_BRASS)
    wt.modifiers.new("bev", "BEVEL").width = 0.0006
    child(wt, pend, PV)
    if crank_to is not None:
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
    swing(pend, R)
    for o in made: o.parent = root
    return root


metronome("metro", SLIT_X - 0.070, YR + 0.075, RIGHTS, crank_to=SLIT_X)

# =====================================================================================================
# 印带器、托盘和八张小卡、发货端的节拍器
# =====================================================================================================
PB = PRN_X - 0.060                                                                        # 机身中心；右侧面（出带口）正好在 PRN_X
box("prn_foot_n", PB - 0.06, PB + 0.06, YR - 0.052, YR - 0.030, 0, 0.0135, PLY, bevel=0.0008)
box("prn_foot_f", PB - 0.06, PB + 0.06, YR + 0.030, YR + 0.052, 0, 0.0135, PLY, bevel=0.0008)
box("prn_body", PB - 0.06, PB + 0.06, YR - 0.052, YR + 0.052, 0.0135, 0.078, PLY, bevel=0.0012)
box("prn_lid", PB - 0.063, PB + 0.063, YR - 0.055, YR + 0.055, 0.078, 0.083, WALNUT, bevel=0.0012)
box("prn_slot", PB + 0.0595, PB + 0.0603, YR - 0.024, YR + 0.024, 0.0135, 0.0175, M_BLACK)
box("prn_slot_lip", PB + 0.060, PB + 0.0625, YR - 0.027, YR + 0.027, 0.0175, 0.0200, M_BRASS, bevel=0.0004)
cyl("prn_roller", (PB + 0.066, YR - 0.025, 0.0125), (PB + 0.066, YR + 0.025, 0.0125), 0.0040, M_STEEL, 20)      # 出带口的压辊
for sy in (-1, 1): box("prn_roller_ear", PB + 0.060, PB + 0.071, YR + sy * 0.0275 - 0.0012, YR + sy * 0.0275 + 0.0012, 0.006, 0.019, M_BRASS)
box("prn_intake", PB - 0.016, PB + 0.016, YR - 0.0528, YR - 0.0518, 0.020, 0.026, M_BLACK)                       # 正面的进卡口
box("prn_intake_lip", PB - 0.020, PB + 0.020, YR - 0.060, YR - 0.052, 0.0175, 0.0195, M_BRASS, bevel=0.0004)     # 进卡口下面的小托板
box("prn_plate", PB - 0.034, PB + 0.034, YR - 0.0528, YR - 0.0520, 0.046, 0.066, M_BRASS)                        # 铭牌
for sx in (-1, 1):
    for sz in (0.022, 0.070): cyl("prn_screw", (PB + sx * 0.052, YR - 0.052, sz), (PB + sx * 0.052, YR - 0.0532, sz), 0.0022, M_STEEL, 12)
# 白纸带卷：机身左边的支架上
RLX, RLZ = PB - 0.105, 0.052
reel = empty("prn_reel", (RLX, YR, RLZ))
child(cyl("prn_reel_paper", (RLX, YR - 0.021, RLZ), (RLX, YR + 0.021, RLZ), 0.036, M_PAPER, 48), reel, reel.location)
child(cyl("prn_reel_core", (RLX, YR - 0.024, RLZ), (RLX, YR + 0.024, RLZ), 0.008, WALNUT, 24), reel, reel.location)
for k_ in range(3):                                                                                              # 侧面三根辐条，看得出在转
    child(box(f"prn_reel_spoke{k_}", RLX - 0.034, RLX + 0.034, YR - 0.0222, YR - 0.0216, RLZ - 0.0012, RLZ + 0.0012, M_BRASS), reel, reel.location).rotation_euler = (0, radians(60 * k_), 0)
for sy in (-1, 1): box("prn_reel_arm", RLX - 0.006, RLX + 0.006, YR + sy * 0.027 - 0.002, YR + sy * 0.027 + 0.002, 0, RLZ + 0.006, WALNUT, bevel=0.0008)
cyl("prn_reel_axle", (RLX, YR - 0.031, RLZ), (RLX, YR + 0.031, RLZ), 0.0022, M_BRASS, 12)
box("prn_feed", RLX + 0.01, PB - 0.059, YR - 0.021, YR + 0.021, 0.0162, 0.0164, M_PAPER)                          # 白纸带从卷到机身
reel.rotation_euler = (0, 0, 0); reel.keyframe_insert("rotation_euler", frame=-5)
reel.rotation_euler = (0, V * (NF + 10) / 0.036, 0); reel.keyframe_insert("rotation_euler", frame=NF + 5); set_interp(reel, "LINEAR")
cyl("prn_collar", (PB, YR, 0.083), (PB, YR, 0.087), 0.009, M_BRASS, 24)
plg = empty("prn_plunger", (PB, YR, 0.078))
child(cyl("prn_rod", (PB, YR, 0.060), (PB, YR, 0.117), 0.004, M_STEEL, 20), plg, plg.location)
kn = lathe("prn_knob", [(0.012 * sin(radians(a)), 0.012 - 0.012 * cos(radians(a))) for a in range(0, 181, 12)], 32, [WALNUT], split=0)
kn.location = (0, 0, 0.039); kn.parent = plg
PRESS = [(a - T_PRN, b - a, bit) for a, b, bit in PAT_B if -30 < a - T_PRN < NF + 30]      # 每印一格按一下：(帧, 格宽, 这一格的颜色)
for f_, w, _ in PRESS:
    k = min(1.0, w / TB)
    for df, dz in ((-3 * k, 0.0), (0, -0.013 * k), (5 * k, 0.0)):
        plg.location.z = 0.078 + dz; plg.keyframe_insert("location", frame=f_ + df)
TX0 = PB - 0.095
box("tray", TX0 - 0.006, TX0 + 0.19, YR - 0.128, YR - 0.086, 0, 0.004, WALNUT, bevel=0.001)
upcoming = [p for p in PRESS if p[0] >= 0][:8]
for i in range(8):
    f_, w, bit = upcoming[i] if i < len(upcoming) else (9999, TB, i % 2)
    x0 = TX0 + 0.004 + (7 - i) * 0.023                                                    # 先用的那张最靠右（离进卡口近）
    c = box(f"card{i}", -0.010, 0.010, -0.015, 0.015, 0, 0.0008, M_INK if bit else M_PAPER)
    c.location = (x0 + 0.010, YR - 0.107, 0.004)
    if SP.get("cards") and f_ < NF + 5:                                                   # 印这一格之前，小卡滑进印带器正面的进卡口
        c.keyframe_insert("location", frame=f_ - 11); c.keyframe_insert("scale", frame=f_ - 4)
        c.location = (PB, YR - 0.066, 0.021); c.keyframe_insert("location", frame=f_ - 4)
        c.location = (PB, YR - 0.040, 0.021); c.scale = (0.9, 0.2, 1); c.keyframe_insert("location", frame=f_ - 1); c.keyframe_insert("scale", frame=f_ - 1)
M2X = PRN_X + 0.135
m2 = metronome("metro2", M2X, YR + 0.075, [p[0] for p in PRESS] or [0, TB])
if SP.get("gate"):                                                                         # y4：想跟着纸带走，被挡片挡停
    f0, f1 = SP["gate"]
    m2.keyframe_insert("location", frame=f0)
    m2.location.y = -0.034; m2.keyframe_insert("location", frame=f1)
    m2.location.y = -0.024; m2.keyframe_insert("location", frame=f1 + 5)
    m2.location.y = -0.027; m2.keyframe_insert("location", frame=f1 + 12)
    gy = YR + 0.031
    gate = empty("gate_root", (M2X, gy, 0.14))
    for sx in (-1, 1):
        cyl("gate_leg", (sx * 0.052, 0.0006, 0), (sx * 0.052, 0.0006, 0.070), 0.0018, M_BRASS, 12).parent = gate
    q = tex_quad("gate_card", (0, -0.0005, 0.048), (1, 0, 0), (0, 0, 1), 0.120, 0.056, "gate"); q.parent = gate
    box("gate_back", -0.060, 0.060, 0.0, 0.0012, 0.020, 0.076, PLY).parent = gate
    gate.keyframe_insert("location", frame=f1 - 6)
    gate.location.z = 0.0; gate.keyframe_insert("location", frame=f1 - 1)
    gate.location.z = 0.006; gate.keyframe_insert("location", frame=f1 + 2)
    gate.location.z = 0.0; gate.keyframe_insert("location", frame=f1 + 5)

# =====================================================================================================
# 透明尺：只盖数据道（盖点的白边露在外面），贴着纸带一起走；刻度一格一道
# =====================================================================================================
M_ACR, ba = principled("acrylic", **{"Base Color": (0.93, 0.97, 0.96, 1), "Roughness": 0.03, "IOR": 1.30})    # 折射率调低一点：反光弱，压在黑带上黑带不发灰
ba.inputs["Transmission Weight"].default_value = 1.0
nt2 = M_ACR.node_tree; lp = nt2.nodes.new("ShaderNodeLightPath"); tr = nt2.nodes.new("ShaderNodeBsdfTransparent")
tr.inputs["Color"].default_value = (0.86, 0.92, 0.90, 1); mix = nt2.nodes.new("ShaderNodeMixShader")
nt2.links.new(lp.outputs["Is Shadow Ray"], mix.inputs[0]); nt2.links.new(ba.outputs[0], mix.inputs[1]); nt2.links.new(tr.outputs[0], mix.inputs[2])
nt2.links.new(mix.outputs[0], nt2.nodes["Material Output"].inputs["Surface"])
RU = SP.get("ruler")
M_TICK, _ = principled("ruler_tick", **{"Base Color": (0.93, 0.90, 0.80, 1), "Roughness": 0.5})
ncell = RU["cells"] if RU else 8
ruler = empty("ruler", (-0.22, -0.27, 0), (0, 0, radians(7)))
RL = CELL * ncell + 0.012
RY0, RY1 = -0.0128, 0.0128
box("ruler_body", -RL / 2, RL / 2, RY0, RY1, 0.0002, 0.0026, M_ACR, bevel=0.0004).parent = ruler
for i in range(ncell + 1):
    x = -CELL * ncell / 2 + i * CELL
    box(f"ruler_tick{i}", x - 0.0005, x + 0.0005, RY0, RY0 + 0.013, 0.00264, 0.00268, M_TICK).parent = ruler       # 浅色刻度，压在黑带上也看得见
    box(f"ruler_tickb{i}", x - 0.0010, x + 0.0010, RY0, RY0 + 0.013, 0.0026, 0.00264, M_BLACK).parent = ruler      # 深色衬底，压在白格上也看得见
if RU:
    ruler.parent = tape
    rest = Vector((tape_x(RU["t"]), YR + 0.005, Z_TAPE))
    ruler.rotation_euler = (0, 0, 0); ruler.location = rest
    if RU.get("land"):
        f0, f1 = RU["land"]
        ruler.location = rest + Vector((0.02, -0.45, 0.30)); ruler.rotation_euler = (radians(-25), 0, radians(6))    # 从镜头这一侧的画外进来
        ruler.keyframe_insert("location", frame=f0); ruler.keyframe_insert("rotation_euler", frame=f0)
        ruler.location = rest; ruler.rotation_euler = (0, 0, 0)
        ruler.keyframe_insert("location", frame=f1); ruler.keyframe_insert("rotation_euler", frame=f1)
    if RU.get("lift"):
        f0, f1 = RU["lift"]
        ruler.keyframe_insert("location", frame=f0); ruler.keyframe_insert("rotation_euler", frame=f0)
        ruler.location = rest + Vector((0.03, -0.45, 0.30)); ruler.rotation_euler = (radians(-25), 0, radians(10))
        ruler.keyframe_insert("location", frame=f1); ruler.keyframe_insert("rotation_euler", frame=f1)

# ---------- 杯子（远处，虚掉） ----------
R_, Hm = 0.041, 0.092
prof = [(0.0, 0.0), (R_ - 0.004, 0.0), (R_ - 0.001, 0.001), (R_, 0.004), (R_, Hm - 0.002), (R_ - 0.001, Hm), (R_ - 0.003, Hm), (R_ - 0.004, Hm - 0.002),
        (R_ - 0.004, Hm - 0.016), (0.0, Hm - 0.016)]
mug = lathe("mug", prof, 64, [M_CER, M_COF], [0, 0, 0, 0, 0, 0, 0, 0, 1], split=50)
mug.location = (0.44, 0.24, 0.0)


# =====================================================================================================
# 打乱盒、还原盒、修字盒、切刀和托盘、表、桌沿签
# =====================================================================================================
def tunnel(name, xc, w, h, body, tex=None, top=None):
    """跨在导轨上的一只盒子：纸带从底下穿过去。正面（朝相机）贴字。"""
    root = empty(name, (xc, YR, 0))
    for nm_, (y0, y1, z0, z1) in {"n": (-0.036, -0.0285, 0, h), "f": (0.0285, 0.036, 0, h), "t": (-0.036, 0.036, RAIL_H + 0.006, h)}.items():
        box(f"{name}_{nm_}", -w / 2, w / 2, y0, y1, z0, z1, body, bevel=0.001).parent = root
    if top: box(name + "_top", -w / 2 + 0.004, w / 2 - 0.004, -0.030, 0.030, h, h + 0.0015, top).parent = root
    if tex:
        lw = w - 0.006; lh = lw / (2.0 if tex != "box_fix" else 2.33)                    # 一块斜放在盒顶的牌子，正面和俯视都读得到
        tex_quad(name + "_label", (0, -0.036 + 0.36 * lh, h + 0.0022 + 0.36 * lh), (1, 0, 0), (0, 0.72, 0.72), lw, lh, tex).parent = root
    return root


if "scr" in PROPS: tunnel("scr_box", X_SCR, 0.084, 0.050, WALNUT, "box_scr")
if "des" in PROPS: tunnel("des_box", X_DES, 0.084, 0.050, WALNUT, "box_des")
STRIP = Vector((0.47, 0.20, 0.0))                                                       # 插线板：在导轨后面，不挡近景                                                       # 插线板
DROPS = SP.get("drops", {})
for nm_ in ("fix1", "fix2", "fix3"):
    if nm_ not in PROPS: continue
    r = tunnel(nm_, X_FIX[nm_], 0.050, 0.034, M_BLACK, "box_fix", top=M_BRASS)
    # 电源线：从盒子正面下沿拖到插线板（挂在盒子上，跟着一起落下）
    i_ = ("fix2", "fix3", "fix1").index(nm_); o_ = Vector((X_FIX[nm_], YR, 0))
    a = Vector((0.0, 0.037, 0.006))
    b_ = STRIP + Vector((-0.085 + 0.055 * i_, -0.004, 0.024)) - o_
    way = [Vector((0.105, 0.045, 0.002)) - o_, Vector((0.125, 0.12, 0.002)) - o_] if nm_ == "fix1" else \
          [Vector((X_FIX[nm_], 0.165 + 0.01 * i_, 0.002)) - o_, Vector((STRIP.x - 0.10, 0.17 + 0.01 * i_, 0.002)) - o_]   # 绕到节拍器后面
    cu = bpy.data.curves.new(nm_ + "_cable", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.0016; cu.bevel_resolution = 3
    sp = cu.splines.new("BEZIER"); sp.bezier_points.add(3)
    for p, co in zip(sp.bezier_points, [a] + way + [b_]):
        p.co = co; p.handle_left_type = p.handle_right_type = "AUTO"
    co = bpy.data.objects.new(nm_ + "_cable", cu); col.objects.link(co); cu.materials.append(M_BLACK); co.parent = r
    if nm_ in DROPS and not SP.get("fixed"):
        f0 = DROPS[nm_]
        r.location.z = 0.55; r.keyframe_insert("location", frame=f0 - 5)
        r.location.z = 0.0; r.keyframe_insert("location", frame=f0)
        r.location.z = 0.004; r.keyframe_insert("location", frame=f0 + 2)
        r.location.z = 0.0; r.keyframe_insert("location", frame=f0 + 4)
if "meters" in PROPS:
    box("strip", STRIP.x - 0.11, STRIP.x + 0.11, STRIP.y - 0.022, STRIP.y + 0.022, 0, 0.022, M_PLAIN, bevel=0.002)
    for i in range(4):
        box(f"strip_hole{i}", STRIP.x - 0.085 + i * 0.055, STRIP.x - 0.060 + i * 0.055, STRIP.y - 0.010, STRIP.y + 0.010, 0.022, 0.0224, M_BLACK)

    M_NEEDLE, bn_ = principled("needle", **{"Base Color": (0.80, 0.16, 0.10, 1), "Roughness": 0.4})
    bn_.inputs["Emission Color"].default_value = (1.0, 0.22, 0.12, 1); bn_.inputs["Emission Strength"].default_value = 0.9   # 略带自发光：表盘在阴影里时指针也看得见

    def meter(name, at, scale, yaw, keys_, tag):
        """Poly Haven「retro_multimeter」（CC0）。指针是单独的零件，绕 y 轴转。v = 0–1 对应指针从左到右。"""
        root = empty(name, at, (0, 0, radians(yaw))); root.scale = (scale,) * 3
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=f"{DL}/retro_multimeter/retro_multimeter_2k.gltf")
        needle = None
        for o in set(bpy.data.objects) - before:
            if "cables" in o.name or "handle" in o.name: o.hide_render = True; continue
            if o.parent is None: o.parent = root
            if "needle" in o.name: needle = o
            for sl_ in getattr(o, "material_slots", []):                                   # 表蒙子换成不挡光的亚克力，否则表盘在它的影子里是黑的
                if sl_.material and "glass" in sl_.material.name: sl_.material = M_ACR
        if needle is not None:
            piv = empty(name + "_piv", (0, -0.024, 0.148)); piv.parent = root
            for f_, v_ in keys_:
                piv.rotation_euler = (0, radians(-38 + 76 * v_), 0); piv.keyframe_insert("rotation_euler", frame=f_)
            bpy.data.objects.remove(needle)                                                # 模型自带的黑针去掉，只留珊瑚色这一根
            nd = box(name + "_red", -0.0009, 0.0009, -0.0006, -0.0001, 0.004, 0.054, M_NEEDLE); nd.parent = piv   # 模型自带的指针太细太暗，换成一根珊瑚色的
            nd.visible_shadow = False                                                      # 不投影：太阳很斜，影子会像第二根针
        tex_quad(name + "_tag", (0, -0.030, 0.222 + 0.030), (1, 0, 0), (0, 0.25, 1), 0.120, 0.051, tag).parent = root   # 小签立在表顶上
        return root
    meter("meter_big", (0.42, 0.12, 0.0), 0.62, 6, SP.get("needle_big", [(0, 0.25)]), "tag_power")
    meter("meter_small", (0.515, 0.105, 0.0), 0.45, 12, SP.get("needle_small", [(0, 0.70)]), "tag_bit")
if "serdes" in PROPS:                                                                      # 桌沿的签：整套 = SerDes
    f0, f1 = SP.get("serdes", (-99, -90))
    tg = empty("serdes_tag", (-0.06, -0.33, 0.0))                                           # 一张大签，斜靠在小木条上，落在装置前面的桌面上
    tex_quad("serdes_card", (0, 0, 0.028), (1, 0, 0), (0, 0.92, 0.39), 0.50, 0.150, "tag_serdes").parent = tg
    box("serdes_foot", -0.25, 0.25, 0.060, 0.072, 0, 0.056, WALNUT, bevel=0.0008).parent = tg
    tg.location.z = 0.40; tg.keyframe_insert("location", frame=f0)
    tg.location.z = 0.0; tg.keyframe_insert("location", frame=f1)
    tg.location.z = 0.008; tg.keyframe_insert("location", frame=f1 + 2)
    tg.location.z = 0.0; tg.keyframe_insert("location", frame=f1 + 4)
if "cutter" in PROPS:
    for sy in (-1, 1):
        box("cut_post", X_CUT - 0.004, X_CUT + 0.004, YR + sy * 0.031 - 0.004, YR + sy * 0.031 + 0.004, 0, 0.075, M_BRASS, bevel=0.0006)
    box("cut_bar", X_CUT - 0.005, X_CUT + 0.005, YR - 0.035, YR + 0.035, 0.075, 0.083, WALNUT, bevel=0.001)
    blade = box("cut_blade", X_CUT - 0.0006, X_CUT + 0.0006, YR - 0.027, YR + 0.027, 0, 0.030, M_STEEL)
    blade.location.z = 0.040
    TRX = 0.505                                                                            # 右托盘：切下来的八段并排
    box("tray_r", TRX - 0.006, TRX + 0.225, YR - 0.150, YR - 0.096, 0, 0.004, WALNUT, bevel=0.001)
    cuts = [(a + (X_CUT - SLIT_X) / V, bit) for a, b, bit in PAT_B if b - a >= 15]         # (这一格的前沿到切刀的帧, 颜色)
    done = [c for c in cuts if c[0] < 0][-5:] if SP.get("cut") else [c for c in cuts if c[0] < 0][-8:]
    todo = [c for c in cuts if 0 <= c[0] < NF][:3] if SP.get("cut") else []

    def piece(i, bit):
        root = empty(f"piece{i}", (TRX + 0.014 + i * 0.027, YR - 0.123, 0.0044))
        box(f"piece{i}_p", -0.012, 0.012, -0.021, 0.021, 0, 0.0002, M_PAPER).parent = root
        if bit: box(f"piece{i}_k", -0.012, 0.012, -0.008, 0.018, 0.0002, 0.00026, M_INK).parent = root
        return root
    if not SP.get("cut"): done = [(0, upcoming[7 - k][2] if 7 - k < len(upcoming) else k % 2) for k in range(8)]   # 不在切的镜头：右托盘和左托盘从左到右同一组黑白
    for i, (f_, bit) in enumerate(done): piece(i, bit)
    for j, (f_, bit) in enumerate(todo):
        i = len(done) + j; r = piece(i, bit); rest = r.location.copy(); fc = f_ + TB       # 这一格的后沿到切刀：落刀
        for df, z in ((-3, 0.040), (0, Z_TAPE - 0.001), (4, 0.040)):
            blade.location.z = z; blade.keyframe_insert("location", frame=fc + df)
        r.scale = (0, 0, 0); r.keyframe_insert("scale", frame=fc - 1); r.scale = (1, 1, 1); r.keyframe_insert("scale", frame=fc)
        r.location = (X_CUT + 0.013, YR, Z_TAPE); r.keyframe_insert("location", frame=fc)
        r.location = (rest.x, YR - 0.05, 0.03); r.keyframe_insert("location", frame=fc + 6)
        r.location = rest; r.keyframe_insert("location", frame=fc + 12)

# =====================================================================================================
# 手机（靠在小支架上）和路线图小卡
# =====================================================================================================
PW, PH, PT = 0.0715, 0.147, 0.0082
TILT = radians(-24)                                                                        # 上沿往后仰
ph = empty("phone", PHONE + Vector((0, 0, 0.012)), (TILT, 0, 0))
M_PH, _ = principled("phone_body", **{"Base Color": (0.03, 0.03, 0.035, 1), "Roughness": 0.25, "Metallic": 0.6})
box("phone_body", -PW / 2, PW / 2, 0, PT, 0, PH, M_PH, bevel=0.003).parent = ph
M_SCR, bs = principled("phone_screen", **{"Base Color": (0.01, 0.01, 0.01, 1), "Roughness": 0.08})
scr_tex = M_SCR.node_tree.nodes.new("ShaderNodeTexImage")
kind, cnt = SP.get("phone", ("clean", 1))
PH_IMGS = [bpy.data.images.load(f"{TEX}/phone/{kind}_{i:04d}.png" if cnt > 1 else f"{TEX}/phone/clean.png") for i in range(cnt)]
scr_tex.image = PH_IMGS[0]
M_SCR.node_tree.links.new(scr_tex.outputs["Color"], bs.inputs["Emission Color"]); bs.inputs["Emission Strength"].default_value = P.get("screen", 1.6)
sq = tex_quad("phone_screen", (0, -0.0002, PH / 2), (1, 0, 0), (0, 0, 1), PW - 0.006, PH - 0.008, None, mat=M_SCR); sq.parent = ph
box("phone_stand", PHONE.x - 0.03, PHONE.x + 0.03, PHONE.y - 0.004, PHONE.y + 0.075, 0, 0.012, WALNUT, bevel=0.001)
bk = box("phone_prop", -0.02, 0.02, 0, 0.006, 0, 0.10, WALNUT, bevel=0.001); bk.location = PHONE + Vector((0, 0.058, 0.012)); bk.rotation_euler = (radians(-33), 0, 0)


def _phone_frame(scene, *a):
    scr_tex.image = PH_IMGS[max(0, min(len(PH_IMGS) - 1, scene.frame_current))]


if cnt > 1: bpy.app.handlers.frame_change_pre.append(_phone_frame)
if SP.get("route"):
    f0, f1 = SP["route"]
    rc = empty("route_root", (0, 0, 0))
    tex_quad("route_card", (0, 0, 0.024), (1, 0, 0), (0, 0.45, 1), 0.086, 0.050, "route").parent = rc
    box("route_foot", -0.043, 0.043, -0.003, 0.016, 0, 0.003, WALNUT, bevel=0.0006).parent = rc
    rest = Vector((PHONE.x - 0.030, PHONE.y - 0.048, 0.0))
    rc.location = rest + Vector((-0.01, -0.01, 0.30)); rc.rotation_euler = (radians(20), 0, radians(-20))
    rc.keyframe_insert("location", frame=f0); rc.keyframe_insert("rotation_euler", frame=f0)
    rc.location = rest; rc.rotation_euler = (0, 0, radians(-5)); rc.keyframe_insert("location", frame=f1); rc.keyframe_insert("rotation_euler", frame=f1)
    rc.location = rest + Vector((0, 0, 0.004)); rc.keyframe_insert("location", frame=f1 + 2)
    rc.location = rest; rc.keyframe_insert("location", frame=f1 + 4)

# =====================================================================================================
# 发光信号（暗场）：纸带前面一块真电路板，走线上的金色明暗段和纸带同图样同速，走进芯片引脚
# =====================================================================================================
PIN = None
if G:
    BS = 0.6
    BO = Vector((SLIT_X - BS * 0.024, YR - 0.040 - BS * 0.1986, BS * 0.006 + 0.0004))
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f"{S.get('model', DL + '/circuit_board')}/circuit_board_2k.gltf")
    for o in set(bpy.data.objects) - before:
        if o.parent is None: o.scale = (BS, BS, BS); o.location = BO

    def bw(x, y, z=0.0): return BO + BS * Vector((x, y, z))
    route = [(-0.196, -0.060), (0.000, -0.060), (0.014, -0.074), (0.0235, -0.074)]
    pts = [bw(x, y, P.get("lanez", 0.0019)) for x, y in route]
    seglen = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(seglen); hw = P.get("lanew", 0.0011) / 2
    verts, faces, luv = [], [], []; acc = 0.0

    def u_of(d): return (d / V - T_LO) / (T_HI - T_LO)          # 离引脚 d 米的那一点，在第 0 帧对应纸带上 t = d / V
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; d = (b - a).normalized(); nrm = Vector((-d.y, d.x, 0)) * hw
        ext = d * hw * 0.42 if i < len(pts) - 2 else Vector((0, 0, 0))
        n0 = len(verts)
        verts += [tuple(a - nrm), tuple(a + nrm), tuple(b + ext + nrm), tuple(b + ext - nrm)]
        faces.append((n0, n0 + 3, n0 + 2, n0 + 1))
        u0, u1 = u_of(total - acc), u_of(total - acc - seglen[i])
        luv.append([(u0, 0), (u1, 0), (u1, 1), (u0, 1)]); acc += seglen[i]
    M_SIG, bsg = principled("signal", **{"Base Color": (0.55, 0.30, 0.10, 1), "Metallic": 1.0, "Roughness": 0.35})
    nt3 = M_SIG.node_tree
    uv3 = nt3.nodes.new("ShaderNodeUVMap"); mp3 = nt3.nodes.new("ShaderNodeMapping")
    tx3 = nt3.nodes.new("ShaderNodeTexImage"); tx3.image = IMG_A; tx3.interpolation = "Linear"; tx3.extension = "EXTEND"
    sp3 = nt3.nodes.new("ShaderNodeSeparateColor")
    nt3.links.new(uv3.outputs["UV"], mp3.inputs["Vector"]); nt3.links.new(mp3.outputs["Vector"], tx3.inputs["Vector"]); nt3.links.new(tx3.outputs["Color"], sp3.inputs[0])
    mul = nt3.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = P.get("sig", 9.0)
    nt3.links.new(sp3.outputs[0], mul.inputs[0]); nt3.links.new(mul.outputs[0], bsg.inputs["Emission Strength"])
    bsg.inputs["Emission Color"].default_value = (1.0, 0.56, 0.14, 1)
    loc = mp3.inputs["Location"]
    for f_ in (-5, NF + 5):
        loc.default_value = (f_ / (T_HI - T_LO), 0, 0); loc.keyframe_insert("default_value", frame=f_)
    lane = add_obj("signal_lane", mesh_from("signal_lane", verts, faces, loop_uvs=luv)); lane.data.materials.append(M_SIG)
    PIN = pts[-1]

    def blip(name, at, rad, color, frames, peak):
        m, b = principled(name, **{"Base Color": (0.02, 0.02, 0.02, 1), "Roughness": 0.3})
        b.inputs["Emission Color"].default_value = (*color, 1); e = b.inputs["Emission Strength"]; e.default_value = 0.0
        cyl(name, at, at + Vector((0, 0, 0.0005)), rad, m, 20)
        for f_, w in frames:
            k = min(1.0, w / TB)
            keys_val(e, [(f_ - 1 * k, 0.0), (f_, peak), (f_ + 1 * k, peak * 0.6), (f_ + 2 * k, peak * 0.2), (f_ + 4 * k, 0.0)])
        set_interp(m.node_tree, "LINEAR")
    blip("pin_flash", PIN + Vector((0.0016, 0, 0.0002)), 0.0016, (1.0, 0.56, 0.14), EDGES, P.get("sig", 9.0) * 4)
    blip("chip_sample", bw(0.042, -0.0775, P.get("chipz", 0.0066)), 0.0022, (0.03, 0.22, 1.0),
         [(r, PER[r]) for r in RIGHTS if -2 <= r <= NF + 2], P.get("smp", 3.0))
    set_interp(nt3, "LINEAR")

# =====================================================================================================
# 光、相机、渲染
# =====================================================================================================
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

CAMK = SP["cam"]


def cam_state(f):
    k = 0
    while k < len(CAMK) - 2 and f >= CAMK[k + 1][0]: k += 1
    (f0, a), (f1, b) = CAMK[k], CAMK[k + 1]
    u = min(1.0, max(0.0, (f - f0) / max(1e-6, f1 - f0)))
    if f1 - f0 > 1.5: u = u * u * (3 - 2 * u) * 0.9 + u * 0.1
    lerp = lambda x, y: x + (y - x) * u
    T = Vector(a["t"]).lerp(Vector(b["t"]), u)
    d, pt, yw = lerp(a["dist"], b["dist"]), radians(lerp(a["pitch"], b["pitch"])), radians(lerp(a["yaw"], b["yaw"]))
    loc = T + d * Vector((sin(yw) * cos(pt), -cos(yw) * cos(pt), sin(pt)))
    fa, fb = Vector(a["focus"] or a["t"]), Vector(b["focus"] or b["t"])
    return loc, (T - loc).normalized().to_track_quat("-Z", "Y").to_euler(), fa.lerp(fb, u), lerp(a["lens"], b["lens"]), lerp(a["fstop"], b["fstop"])


cd = bpy.data.cameras.new("cam"); cd.lens = P["lens"]; cd.sensor_width = 36; cd.sensor_fit = "AUTO"
cam = bpy.data.objects.new("cam", cd); col.objects.link(cam); scene.camera = cam
foc = empty("focus", (0, 0, 0))
cd.dof.use_dof = True; cd.dof.focus_object = foc; cd.dof.aperture_blades = 7
for f_ in range(-1, NF + 2):
    cam.location, cam.rotation_euler, foc.location, cd.lens, cd.dof.aperture_fstop = cam_state(f_)
    cam.keyframe_insert("location", frame=f_); cam.keyframe_insert("rotation_euler", frame=f_); foc.keyframe_insert("location", frame=f_)
    cd.keyframe_insert("lens", frame=f_); cd.dof.keyframe_insert("aperture_fstop", frame=f_)
set_interp(cam, "LINEAR"); set_interp(foc, "LINEAR")

scene.render.fps = FPS; scene.frame_start = 0; scene.frame_end = NF - 1
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
if P.get("gpu"):
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"; prefs.get_devices()
    for d_ in prefs.devices: d_.use = True
    optix = [d_.name for d_ in prefs.devices if d_.type == "OPTIX"]
    print("[gpu]", optix)
    if not optix: raise SystemExit("gpu=1 但没有可用的 OptiX 设备：不要退回 CPU 慢慢渲")
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
scene.render.resolution_x, scene.render.resolution_y = 1080, 1920; scene.render.resolution_percentage = SCALE
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "None"
scene.view_settings.exposure = P["exposure"]
scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_depth = "8"
scene.render.image_settings.compression = 30
scene.render.threads_mode = "AUTO"

# ---------- 屏幕锚点（合成贴字用） ----------
ANCH = {"lamp": LAMP + Vector((0, 0, 0.004)), "slit": Vector((SLIT_X, YR + 0.005, PZ1)), "count": Vector((CX, CY, CZ + WR)), "sign": SG.copy(),
        "metro": Vector((SLIT_X - 0.07, YR + 0.07, 0.19)), "metro2": Vector((M2X, YR + 0.07, 0.215)), "tray": Vector((TX0 + 0.09, YR - 0.107, 0.004)),
        "printer": Vector((PB, YR, 0.09)), "prn_out": Vector((PRN_X + 0.10, Y_NEAR, Z_TAPE)), "dot": Vector((SLIT_X, Y_DOT, Z_TAPE)),
        "tape_mid": Vector((SLIT_X - 0.10, Y_NEAR, Z_TAPE)), "tray_r": Vector((0.61, YR - 0.123, 0.004)), "phone_top": PHONE + Vector((0, 0.06, 0.16)), "cutter": Vector((X_CUT, YR, 0.08)),
        "fix1": Vector((X_FIX["fix1"], YR - 0.036, 0.04)), "meter_big": Vector((0.385, 0.08, 0.18)), "meter_small": Vector((0.495, 0.08, 0.12)), "metro2_gate": Vector((M2X, YR + 0.031, 0.08)),
        "scr": Vector((X_SCR, YR - 0.036, 0.05)), "des": Vector((X_DES, YR - 0.036, 0.05))}
if PIN is not None: ANCH["pin"] = PIN.copy()


def anchors_at(f_):
    from bpy_extras.object_utils import world_to_camera_view
    scene.frame_set(int(f_))
    pts = dict(ANCH)
    if RU: pts["ruler"] = Vector((tape_x(RU["t"]) + V * f_, YR - 0.012, Z_TAPE))
    for k_, t_m in SP.get("marks", {}).items(): pts[k_] = Vector((tape_x(t_m) + V * f_, Y_NEAR, Z_TAPE))   # 跟着纸带走的点
    out = {}
    for k_, p_ in pts.items():
        c = world_to_camera_view(scene, cam, p_); out[k_] = [round(c.x, 4), round(1 - c.y, 4)]
    return out


if P.get("anchors"):
    ev = {"edges": [[round(t, 2), round(w, 2), round(1.0 - max(0.0, (g_at(t) - 0.35) / 0.65) * (1.0 if w < 15 else 0.0) * 0.92, 2)] for t, w in EDGES],   # 鼓：帧、相邻格宽、强度
          "stamps": [[round(r, 2), int(bit_at(PAT_A, r)), round(PER[r], 2)] for r in RIGHTS if -1 <= r <= NF],                                       # 啪：帧、实心?、周期
          "press": [[round(p_[0], 2), round(p_[1], 2)] for p_ in PRESS if 0 <= p_[0] <= NF]}                                                          # 印带器：帧、格宽
    json.dump({"fps": FPS, "frames": NF, "pts": [anchors_at(f_) for f_ in range(NF)], "events": ev}, open(OUT, "w"))
    print("[anchors]", OUT)
elif "fs" in P:
    os.makedirs(OUT, exist_ok=True)
    scene.frame_start, scene.frame_end = int(P["fs"]), int(P["fe"])
    scene.frame_step = int(P.get("step", 1))                 # 草稿可以隔帧渲（step=2）
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
    f_ = int(P.get("still", RANGE.get(SHOT, (0, 0))[0]))
    json.dump(anchors_at(f_), open(OUT + ".json", "w"))
    scene.frame_set(f_)
    if cnt > 1: _phone_frame(scene)
    scene.render.filepath = OUT
    bpy.ops.render.render(write_still=True)
