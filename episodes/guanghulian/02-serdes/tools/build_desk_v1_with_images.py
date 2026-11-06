# 白话光互连 02《第一站 出发：SerDes，为什么要把数据排成一列？》Vox 竖屏 —— 桌面布局与时间表（唯一的真源）
# 运行：python3 tools/build_desk.py → 代码工程/ep2/desk.json（画面读）＋ 配乐读同一份；同时把原文短条裁到 代码工程/assets/strips/
# 语法同第一篇第二版：原文按行剪成短纸条叠成一摞（整摞都在画面里），读字时镜头不动；文章里的三张信息图作为冲印照片贴在桌上，镜头推进去看细节；
# 每段配一张黑卡片做 3b1b 式机制动画；「每秒上千亿个比特」做一次 Kurzgesagt 式的放大镜头。所有时间点落在 120 BPM 的十六分音符格（0.125 s）上。
import json, math, os, random
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CH = {int(k): v for k, v in json.load(open(os.path.join(ROOT, '素材/chars2.json'), encoding='utf-8')).items()}
K, DPI = 2.5, 600 / 72
os.makedirs(os.path.join(ROOT, '代码工程/assets/strips'), exist_ok=True)
PAGES = {}
def page_img(p):
    if p not in PAGES: PAGES[p] = Image.open(os.path.join(ROOT, f'素材/hi-{p}.png')).convert('RGB')
    return PAGES[p]
def runs(page, phrase):
    cs = CH[page]; text = ''.join(c[0] for c in cs); ph = phrase.replace(' ', ''); i = text.find(ph); out = []
    while i >= 0: out.append(cs[i:i + len(ph)]); i = text.find(ph, i + 1)
    if not out: raise SystemExit(f'找不到「{phrase}」(p{page})')
    return out
def boxes(run):
    segs = []
    for c in run:
        if segs and abs(segs[-1]['base'] - c[3]) < 2: segs[-1]['x1'] = c[2]
        else: segs.append({'x0': c[1], 'x1': c[2], 'base': c[3], 'size': c[4]})
    return [[round(s['x0'], 2), round(s['base'] - 0.93 * s['size'], 2), round(s['x1'], 2), round(s['base'] + 0.24 * s['size'], 2)] for s in segs]

CLIPS, CARDS, PRINTS = {}, {}, {}
def rot(x, y, r): return [x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)]
def P(cid, px, py):
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']; w, h = x1 - x0, y1 - y0; k = c['k']
    rx, ry = rot((px - x0) * k - w * k / 2, (py - y0) * k - h * k / 2, c['r']); return [round(c['at'][0] + rx, 1), round(c['at'][1] + ry, 1)]
def PC(cid, cx, cy): c = CARDS[cid]; rx, ry = rot(cx, cy, c['r']); return [round(c['at'][0] + rx, 1), round(c['at'][1] + ry, 1)]
def PP(pid, u, v): p = PRINTS[pid]; rx, ry = rot((u - 0.5) * p['w'], (v - 0.5) * p['h'], p['r']); return [round(p['at'][0] + rx, 1), round(p['at'][1] + ry, 1)]

def strip(cid, page, text, kscale=None):
    run = runs(page, text)[0]; assert len(boxes(run)) == 1, f'「{text}」跨行了'
    size = run[0][4]; base = run[0][3]
    x0, x1 = run[0][1] - 4.5, run[-1][2] + 4.5; y0, y1 = base - 0.93 * size - 4.0, base + 0.24 * size + 4.0
    im = page_img(page).crop((round(x0 * DPI), round(y0 * DPI), round(x1 * DPI), round(y1 * DPI)))
    dr = ImageDraw.Draw(im); gl, gr = round((run[0][1] - x0) * DPI) - 2, round((run[-1][2] - x0) * DPI) + 2
    dr.rectangle([0, 0, max(0, gl), im.height], fill='white'); dr.rectangle([min(im.width, gr), 0, im.width, im.height], fill='white')
    src = f'assets/strips/{cid}.png'; im.save(os.path.join(ROOT, '代码工程', src), optimize=True)
    k = K * (kscale if kscale else (0.85 if size > 12 else 1.0))
    CLIPS[cid] = dict(src=src, page=page, crop=[round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)], at=[0, 0], r=0.0, seed=sum(map(ord, cid)) % 97 + 5, text=text, k=k)
    return cid

# ---------- 原文短条 ----------
S = [('T1', 1, '第一站出发：SerDes，'), ('I1', 1, '上一篇我们跟着一个比特走完了五站。'), ('I2', 1, '这一篇回到第一站：出发。'),
 ('M1', 1, 'SerDes就像仓库的发货口：'), ('M2', 1, '仓库里的货物原本并排摆着，'), ('M3', 1, '发货口把它们排成一列，'), ('M4', 1, '再把这一列拆开、重新并排摆好。'),
 ('N1', 1, 'Ser是Serializer（串行化），'), ('N2', 1, '负责“排成一列”；'), ('N3', 1, 'Des是Deserializer'), ('N4', 1, '（解串），负责“拆回一排”。'),
 ('W0', 1, '为什么不并排走，而要排成一列？'), ('W1', 1, '直觉上，并排走似乎更快：'), ('W2', 1, '修几十条路，几十件货同时出发。'), ('W3', 1, '速度一高，这个办法就越来越吃力，'),
 ('R1', 1, '第一，出口不够。'), ('R2', 1, '芯片对外的引脚数量有限，'), ('R3', 1, '而且每多一条线，'), ('R4', 1, '就多占面积、多耗电。'),
 ('Q1', 1, '第二，很难同时到达。'), ('Q2', 1, '这就像一排运动员要求同时冲线：'), ('Q3', 1, '哪怕一条路长了一点点，'), ('Q4', 1, '那件货就晚到一步，'), ('Q5', 1, '整排数据就拼错了。'),
 ('L1', 1, '不如只修少数几条路，'), ('L2', 1, '让货物排成一列，'), ('L3', 1, '跑到极快。'),
 ('O1', 2, '发货端把并排的数据排成一列，'), ('O2', 2, '今天一条通道每秒'), ('O3', 2, '要送出上千亿个比特。'),
 ('O4', 2, '收货端把这一列重新拆开，'), ('O5', 2, '连续五个1，'), ('O6', 2, '就是一段连在一起、'), ('O7', 2, '没有缝隙的高电平。'),
 ('O8', 2, '收货端要数清这里有几个1，'), ('O9', 2, '比特占多长时间，这就是“节拍”。'),
 ('X1', 2, '从信号高低变化的节奏里，'), ('X2', 2, '自己推算出节拍，'), ('X3', 2, '再按节拍一个一个地清点。'), ('X4', 2, '发出去时排成一列，'), ('X5', 2, '收进来时听准节拍、拆回一排。'),
 ('H1', 2, '提高“每条路跑多快”就成了'), ('H2', 2, 'SerDes的速度大约每过几年就要翻一倍。'), ('H3', 2, '信号在路上更容易变模糊，'), ('H4', 2, '自己也带着不少“整理”能力，'),
 ('H5', 2, '都要耗电、占芯片面积。'), ('H6', 2, '让每送出一个比特少花一点电，'),
 ('V1', 2, '很少作为一颗独立的芯片单独出售。'), ('V2', 2, '它更像一种“能力”，'), ('V3', 2, '嵌在GPU、交换芯片、光模块'), ('V4', 2, '里的各种芯片之中，'),
 ('V5', 2, '常以设计模块（IP）的形式'), ('V6', 2, '授权给芯片公司使用，'), ('V7', 2, '大公司则多半自己研发。'),
 ('Y1', 2, '不能只看它宣称跑得多快。'), ('Y2', 2, '什么路况下跑到这个速度，'), ('Y3', 2, '每个比特花多少电，'), ('Y4', 2, '是否已经在真实芯片上跑通。'), ('Y5', 3, '是自研还是授权，'),
 ('E0', 3, '一句话带走'), ('E1', 3, '速度一高，并排走就难以对齐，'), ('E2', 3, '所以数据要排成一列出发；'), ('E3', 3, 'SerDes负责发出时排队、'), ('E4', 3, '收到时听准'), ('E5', 3, '节拍拆回一排，'),
 ('E6', 3, '让收货端依然读得准，'), ('E7', 3, '每个比特还要尽'), ('E8', 3, '量省电。')]
for cid, p, t in S: strip(cid, p, t)
strip('E9', 3, '本文仅做科普与行业分析，不构成投资建议。', kscale=0.62)

# ---------- 摆放：两列，按出场顺序往下排 ----------
L, R = 0, 1700
COLY = {L: 0, R: 0}; LAST = [0]
STACKS = {}
def place_stack(name, ids, col, gap=26, x_off=0):
    rnd = random.Random(sum(map(ord, name))); top = max(COLY[col], LAST[0]); y = top; xl = col - 250 + x_off; bb = [1e9, 1e9, -1e9, -1e9]
    for cid in ids:
        c = CLIPS[cid]; w = (c['crop'][2] - c['crop'][0]) * c['k']; h = (c['crop'][3] - c['crop'][1]) * c['k']
        c['at'] = [round(xl + rnd.uniform(-10, 14) + w / 2, 1), round(y + h / 2, 1)]; c['r'] = round(rnd.uniform(-0.016, 0.016), 4)
        bb = [min(bb[0], c['at'][0] - w / 2), min(bb[1], y), max(bb[2], c['at'][0] + w / 2), max(bb[3], y + h)]; y += h + gap
    wmax = max((CLIPS[c]['crop'][2] - CLIPS[c]['crop'][0]) * CLIPS[c]['k'] for c in ids)
    STACKS[name] = dict(ids=ids, bb=bb, z=round(min(2.05, 960 / (wmax + 25)), 3)); COLY[col] = bb[3] + 230; LAST[0] = top
def place_card(cid, kind, col, w, h, r):
    top = max(COLY[col], LAST[0]); CARDS[cid] = dict(kind=kind, at=[col, top + h / 2], w=w, h=h, r=r); COLY[col] = top + h + 230; LAST[0] = top
def place_print(pid, src, col, r, w=980):
    top = max(COLY[col], LAST[0]); h = round(w * 520 / 780); PRINTS[pid] = dict(src=src, at=[col, top + h / 2 + 20], w=w, h=h, r=r, seed=len(PRINTS) * 13 + 3)
    COLY[col] = top + h + 270; LAST[0] = top
def SC(name, dy=0): b = STACKS[name]['bb']; return [round((b[0] + b[2]) / 2, 1), round((b[1] + b[3]) / 2 + dy, 1)]
def SZ(name): return STACKS[name]['z']

place_print('P1', 'assets/p1.png', R, -0.012); place_stack('why', ['W0', 'W1', 'W2', 'W3'], R)
LAST[0] = 0
place_stack('intro', ['T1', 'I1', 'I2'], L); place_stack('meta', ['M1', 'M2', 'M3', 'M4'], L)
place_card('K1', 'serdes2', L, 900, 1250, -0.008); place_stack('name', ['N1', 'N2', 'N3', 'N4'], L)
place_stack('r1', ['R1', 'R2', 'R3', 'R4'], R); place_card('K3', 'pins', R, 900, 860, 0.008)
place_stack('r2', ['Q1', 'Q2', 'Q3', 'Q4', 'Q5'], L); place_card('K4', 'skew', L, 900, 1000, -0.008)
place_stack('lanes', ['L1', 'L2', 'L3'], R); place_card('K5', 'lanes', R, 900, 760, 0.01)
place_stack('oa', ['O1', 'O2', 'O3'], L)
place_stack('ob', ['O4', 'O5', 'O6', 'O7'], R); place_print('P2', 'assets/p2.png', R, 0.012)
place_stack('oc', ['O8', 'O9'], R); place_card('K6', 'clock', R, 900, 1000, -0.008)
place_stack('od', ['X1', 'X2', 'X3', 'X4', 'X5'], R)
place_stack('hard', ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'], L); place_card('K7', 'double', L, 900, 1150, 0.008)
place_stack('inv', ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7'], R); place_card('K8', 'embed', R, 900, 900, -0.01)
place_print('P3', 'assets/p3.png', L, -0.01); place_stack('ask', ['Y1', 'Y2', 'Y3', 'Y4', 'Y5'], L)
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9'], 850)

# ---------- 时间表工具 ----------
MARKS, PMARKS, LABELS, STRINGS, CAM, SFX = [], [], [], [], [], []
CARD_LABELS = {k: [] for k in CARDS}; CUE = {}
T = [0.0]
def now(): return T[0]
def adv(d): assert abs(d * 8 - round(d * 8)) < 1e-9, d; T[0] = round(T[0] + d, 4)
def cam(t, xy, z, e='sine'): CAM.append(dict(t=round(t, 4), x=xy[0], y=xy[1], z=z, e=e))
def hold(d, dz=0.02): last = CAM[-1]; adv(d); cam(now(), [last['x'], last['y']], round(last['z'] * (1 + dz), 4), 'lin')
def go(xy, z, d=1.5, e='sine', g=0.08): SFX.append(dict(t=now(), kind='whoosh', dur=d, g=g)); adv(d); cam(now(), xy, z, e)
def mark(cid, kind, phrase, d, seed=None):
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']
    run = [r for r in runs(c['page'], phrase) if x0 <= r[0][1] and r[-1][2] <= x1 and y0 <= r[0][3] <= y1]; assert run, f'「{phrase}」不在短条 {cid} 里'
    MARKS.append(dict(clip=cid, kind=kind, segs=boxes(run[0]), t=[now(), round(now() + d, 4)], seed=seed or len(MARKS) + 2))
    SFX.append(dict(t=now(), kind='marker' if kind == 'hl' else 'pen', dur=d)); adv(d)
def pmark(pid, kind, box, d):   # 照片上的红笔：box 用照片的相对坐标 [u0, v0, u1, v1]
    PMARKS.append(dict(print=pid, kind=kind, box=box, t=[now(), round(now() + d, 4)], seed=len(PMARKS) + 7)); SFX.append(dict(t=now(), kind='pen', dur=d)); adv(d)
def label(text, xy, at, size=30, align='center', r=0.0, bg=None, rate=14):
    LABELS.append(dict(text=text, x=xy[0], y=xy[1], at=at, size=size, align=align, r=r, bg=bg, fg=None, rate=rate)); SFX.append(dict(t=at, kind='label', text=text, rate=rate))
def clabel(cid, text, cx, cy, at, size=40, align='center', bg='cream', r=0.0, rate=14):
    CARD_LABELS[cid].append(dict(text=text, x=cx, y=cy, at=round(at, 4), size=size, align=align, bg=bg, r=r, rate=rate)); SFX.append(dict(t=round(at, 4), kind='label', text=text, rate=rate))
def string(key, a, b, d=0.75, sag=0.06):
    STRINGS.append(dict(key=key, a=a, b=b, t=[now(), round(now() + d, 4)], sag=sag, route=False)); SFX.append(dict(t=now(), kind='string', dur=d))
def sfx(t, kind, **kw): SFX.append(dict(t=round(t, 4), kind=kind, **kw))
def edge(cid, side='r'):
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']; return P(cid, (x1 + 2) if side == 'r' else (x0 - 2), (y0 + y1) / 2)
def ptop(pid): p = PRINTS[pid]; return [p['at'][0], p['at'][1] - p['h'] / 2 - 10]
def pbot(pid): p = PRINTS[pid]; return [p['at'][0] + 200, p['at'][1] + p['h'] / 2 + 10]
def ctop(cid, dx=0): c = CARDS[cid]; return PC(cid, dx, -c['h'] / 2 + 30)
def cbot(cid, dx=0): c = CARDS[cid]; return PC(cid, dx, c['h'] / 2 - 30)
def PZ(pid, fill=1.0): return round(min(1.9, 1080 * 0.94 / PRINTS[pid]['w'] * fill), 3)

# ======================= 时间表 =======================
# --- 钩子：文章里的信息图「为什么要把数据排成一列？」 ---
cam(0, PP('P1', 0.5, 0.5), PZ('P1'), 'lin')
label('白话光互连 · 02', PP('P1', 0.84, 1.03), 0.25, size=26, bg='red', r=-0.02)
hold(2.75, 0.04)
go(SC('why'), SZ('why'))
mark('W1', 'hl', '并排走似乎更快', 1.0); mark('W3', 'hl', '速度一高', 0.625); mark('W3', 'circle', '越来越吃力', 0.75); hold(0.625)
# --- 开场：回到第一站 ---
go(SC('intro'), SZ('intro'), 2.0, 'cubic', 0.14)
HUD_IN = now(); mark('I1', 'hl', '走完了五站', 0.75); mark('I2', 'hl', '回到第一站：出发', 1.0); hold(0.5)
go(SC('meta'), SZ('meta'))
mark('M1', 'hl', '仓库的发货口', 0.75); mark('M2', 'hl', '并排摆着', 0.75); mark('M3', 'hl', '排成一列', 0.625); mark('M4', 'hl', '拆开、重新并排摆好', 1.0); hold(0.375)
string('meta-K1', edge('M4'), ctop('K1', 250)); go(PC('K1', 0, 0), 1.1)
t0 = now(); CUE['K1'] = dict(t0=t0, ser=t0 + 0.25, des=t0 + 3.0, end=t0 + 6.5)
clabel('K1', '发货口：排成一列', -390, -560, t0 + 0.5, align='left'); clabel('K1', '收货口：拆回一排', -390, 70, t0 + 3.25, align='left')
sfx(t0 + 0.25, 'serdes', dur=2.4); sfx(t0 + 3.0, 'fan', dur=2.0); hold(6.5)
string('K1-name', cbot('K1', -250), edge('N1', 'l')); go(SC('name'), SZ('name'))
mark('N1', 'hl', 'Serializer（串行化）', 0.875); mark('N2', 'hl', '排成一列', 0.5); mark('N3', 'hl', 'Deserializer', 0.625); mark('N4', 'hl', '拆回一排', 0.5); hold(0.5)
# --- 为什么排成一列：回到信息图，推进左右两半 ---
go(PP('P1', 0.27, 0.52), PZ('P1', 1.75), 2.0, 'cubic', 0.14); hold(1.5)
go(PP('P1', 0.78, 0.5), PZ('P1', 1.75), 1.25); pmark('P1', 'circle', [0.6, 0.18, 0.97, 0.31], 0.75); hold(0.5)
go(SC('why'), SZ('why')); mark('W2', 'hl', '修几十条路', 0.75); hold(0.5)
go(SC('r1'), SZ('r1'))
mark('R1', 'hl', '出口不够', 0.625); mark('R2', 'hl', '引脚数量有限', 0.75); mark('R4', 'hl', '多占面积、多耗电', 0.875); hold(0.5)
string('r1-K3', edge('R4'), ctop('K3', 250)); go(PC('K3', 0, 0), 1.12)
t0 = now(); CUE['K3'] = dict(t0=t0, lines=[t0 + 0.5 + 0.375 * i for i in range(10)], end=t0 + 5.0)
clabel('K3', '出口有限', -390, -360, t0 + 0.25, align='left', bg='red'); clabel('K3', '多一条线：多占面积、多耗电', 0, 395, t0 + 2.75)
for i, tt in enumerate(CUE['K3']['lines']): sfx(tt, 'pin', n=i)
hold(5.0)
string('K3-r2', cbot('K3', -250), edge('Q1', 'r')); go(SC('r2'), SZ('r2'), 2.0, 'sine', 0.12)
mark('Q1', 'hl', '很难同时到达', 0.75); mark('Q2', 'hl', '同时冲线', 0.625); mark('Q3', 'hl', '长了一点点', 0.625); mark('Q4', 'hl', '晚到一步', 0.625); mark('Q5', 'hl', '整排数据就拼错了', 0.75); hold(0.375)
string('r2-K4', edge('Q5'), ctop('K4', 250)); go(PC('K4', 0, 0), 1.12)
t0 = now(); CUE['K4'] = dict(t0=t0, slow=[t0 + 0.25, t0 + 1.75], fast=[t0 + 2.25, t0 + 3.75], end=t0 + 4.75)
clabel('K4', '跑得慢：还好对齐', -390, -420, t0 + 1.5, align='left'); clabel('K4', '跑得快：晚到一步，拼错了', -390, 380, t0 + 3.5, align='left', bg='red')
sfx(t0 + 1.75, 'ok'); sfx(t0 + 3.75, 'wrong'); hold(4.75)
string('K4-lanes', cbot('K4', 250), edge('L1', 'l')); go(SC('lanes'), SZ('lanes'), 2.0, 'sine', 0.12)
mark('L1', 'hl', '只修少数几条路', 0.875); mark('L2', 'hl', '排成一列', 0.5); mark('L3', 'hl', '跑到极快', 0.5); hold(0.375)
string('lanes-K5', edge('L3'), ctop('K5', 250)); go(PC('K5', 0, 0), 1.15)
t0 = now(); CUE['K5'] = dict(t0=t0, many=t0, few=t0 + 1.0, end=t0 + 3.0)
clabel('K5', '很多条路，每条都慢', -390, -320, t0 + 0.25, align='left'); clabel('K5', '少数几条路，每条极快', -390, 60, t0 + 1.25, align='left')
sfx(t0, 'reach'); sfx(t0 + 1.0, 'reach2'); hold(3.0)
# --- 一进一出 ---
string('K5-oa', cbot('K5', -250), edge('O1', 'r')); go(SC('oa'), SZ('oa'), 2.0, 'sine', 0.12)
mark('O1', 'hl', '排成一列', 0.5); mark('O3', 'hl', '上千亿个比特', 0.75); hold(0.25)
# Kurzgesagt：钻进「上千亿」→ 一秒的信号一放再放，直到看见一个个比特 → 拉回
ZC = (lambda r: P('O3', (r[0][1] + r[-1][2]) / 2, r[0][3] - 4.5))(runs(2, '上千亿')[0])
a = now(); cam(a + 0.5, ZC, 2.7, 'sine'); cam(a + 1.5, ZC, 40, 'cubic')
LENS = dict(at=ZC, zin=[a + 0.5, a + 1.5], open=[a + 0.75, a + 1.25], band=a + 1.5, zooms=[a + 2.25, a + 3.0, a + 3.75], bits=a + 4.5, lbl=a + 4.75, out=[a + 6.5, a + 7.5], zmax=40)
sfx(a + 0.5, 'riser', dur=1.0); sfx(a + 1.25, 'boom')
for z in LENS['zooms']: sfx(z, 'zoomstep')
sfx(a + 4.5, 'pairs'); sfx(a + 6.5, 'pullout', dur=1.0)
for txt, at in [('1 秒', a + 1.5), ('放大', LENS['zooms'][0]), ('再放大', LENS['zooms'][1]), ('再放大', LENS['zooms'][2]), ('这一秒里，有上千亿个这样的比特', a + 4.75)]: SFX.append(dict(t=at, kind='label', text=txt, rate=14))
cam(a + 6.5, ZC, 40, 'lin'); cam(a + 7.5, SC('oa'), SZ('oa'), 'cubic'); T[0] = a + 7.5; hold(0.5)
string('oa-ob', edge('O3'), edge('O4', 'l')); go(SC('ob'), SZ('ob'), 2.0, 'sine', 0.12)
mark('O4', 'hl', '重新拆开', 0.625); mark('O5', 'hl', '连续五个1', 0.5); mark('O6', 'hl', '连在一起', 0.5); mark('O7', 'hl', '没有缝隙的高电平', 0.75); hold(0.375)
go(PP('P2', 0.6, 0.33), PZ('P2', 1.3)); pmark('P2', 'circle', [0.78, 0.17, 0.99, 0.29], 0.75); hold(1.0)
go(PP('P2', 0.45, 0.62), PZ('P2', 1.5), 1.25); hold(1.5)
go(SC('oc'), SZ('oc')); mark('O8', 'hl', '数清这里有几个1', 0.75); mark('O9', 'hl', '这就是“节拍”', 0.75); hold(0.25)
string('oc-K6', edge('O9'), ctop('K6', 250)); go(PC('K6', 0, 0), 1.12)
t0 = now(); CUE['K6'] = dict(t0=t0, wave=t0, ask=t0 + 0.75, edges=t0 + 1.75, grid=[t0 + 2.25, t0 + 3.0], count=[t0 + 3.25, t0 + 4.5], end=t0 + 5.25)
clabel('K6', '只看电平：这里有几个 1？', -390, -400, t0 + 0.75, align='left', bg='red')
clabel('K6', '从高低变化推算节拍', -390, 230, t0 + 2.25, align='left'); clabel('K6', '按节拍一个一个清点：5 个', -390, 330, t0 + 4.25, align='left')
sfx(t0 + 1.75, 'tick'); sfx(t0 + 3.25, 'count'); hold(5.25)
string('K6-od', cbot('K6', -250), edge('X1', 'l')); go(SC('od'), SZ('od'))
mark('X1', 'hl', '高低变化的节奏', 0.75); mark('X2', 'hl', '推算出节拍', 0.625); mark('X3', 'hl', '一个一个地清点', 0.75); mark('X4', 'hl', '排成一列', 0.5); mark('X5', 'hl', '听准节拍、拆回一排', 1.0); hold(0.5)
# --- 为什么越来越难 ---
string('od-hard', edge('X5'), edge('H1', 'r')); go(SC('hard'), SZ('hard'), 2.0, 'sine', 0.12)
mark('H1', 'hl', '每条路跑多快', 0.75); mark('H2', 'hl', '每过几年就要翻一倍', 1.0); mark('H3', 'hl', '更容易变模糊', 0.75); mark('H4', 'hl', '“整理”能力', 0.75)
mark('H5', 'hl', '耗电、占芯片面积', 0.75); mark('H6', 'hl', '少花一点电', 0.625); hold(0.375)
string('hard-K7', edge('H6'), ctop('K7', 250)); go(PC('K7', 0, 0), 1.1)
t0 = now(); CUE['K7'] = dict(t0=t0, rows=[t0 + 0.25, t0 + 1.0, t0 + 1.75], eq=t0 + 2.75, cost=t0 + 3.5, end=t0 + 5.0)
clabel('K7', '每过几年：快一倍', 390, -500, t0 + 1.0, align='right'); clabel('K7', '越快越糊', 390, 285, t0 + 2.0, align='right', bg='red')
clabel('K7', '自带「整理」：要耗电、占面积', -390, 500, t0 + 3.5, align='left')
for tt in CUE['K7']['rows']: sfx(tt, 'thock')
sfx(t0 + 2.75, 'dsp'); sfx(t0 + 3.5, 'amp'); hold(5.0)
# --- 从投资角度 ---
string('K7-inv', cbot('K7', 250), edge('V1', 'l')); go(SC('inv'), SZ('inv'), 2.0, 'sine', 0.12)
mark('V1', 'hl', '很少作为一颗独立的芯片单独出售', 1.0); mark('V2', 'hl', '一种“能力”', 0.625); mark('V3', 'hl', 'GPU、交换芯片、光模块', 0.875)
mark('V5', 'hl', '设计模块（IP）', 0.75); mark('V7', 'hl', '多半自己研发', 0.625); hold(0.375)
string('inv-K8', edge('V7'), ctop('K8', 250)); go(PC('K8', 0, 0), 1.12)
t0 = now(); CUE['K8'] = dict(t0=t0, blocks=[t0 + 0.5, t0 + 0.875, t0 + 1.25], ip=t0 + 2.0, own=t0 + 2.75, end=t0 + 4.25)
clabel('K8', 'SerDes：嵌在芯片里的一种能力', -390, -380, t0 + 0.25, align='left', size=38)
for tt in CUE['K8']['blocks']: sfx(tt, 'stick', n=3)
sfx(t0 + 2.0, 'click'); sfx(t0 + 2.75, 'click'); hold(4.25)
string('K8-P3', cbot('K8', -250), ptop('P3')); go(PP('P3', 0.5, 0.5), PZ('P3'), 2.0, 'sine', 0.12); hold(1.25)
go(PP('P3', 0.5, 0.5), PZ('P3', 1.6), 1.0); pmark('P3', 'circle', [0.33, 0.68, 0.68, 0.81], 0.75); hold(0.75)
go(SC('ask'), SZ('ask'))
mark('Y1', 'hl', '不能只看它宣称跑得多快', 1.0); mark('Y2', 'under', '什么路况下跑到这个速度', 0.75); mark('Y3', 'under', '每个比特花多少电', 0.625)
mark('Y4', 'under', '是否已经在真实芯片上跑通', 0.75); mark('Y5', 'under', '自研还是授权', 0.5); hold(0.5)
# --- 收尾：拉回全桌 → 一句话带走 ---
allx = [c['at'][0] for c in CLIPS.values()] + [c['at'][0] for c in CARDS.values()]; ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
go([OVER['x'], OVER['y']], OVER['z'], 2.0, 'cubic', 0.16); hold(0.75, 0.03)
go(SC('end', -40), SZ('end'), 2.0, 'cubic', 0.10)
mark('E1', 'hl', '并排走就难以对齐', 0.75); mark('E2', 'hl', '排成一列出发', 0.625); mark('E3', 'hl', '发出时排队', 0.5); mark('E4', 'hl', '收到时听准', 0.5); mark('E5', 'hl', '节拍拆回一排', 0.5)
mark('E6', 'hl', '依然读得准', 0.625); mark('E7', 'hl', '每个比特还要尽', 0.5); mark('E8', 'hl', '量省电', 0.375)
eb = STACKS['end']['bb']
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
label('下一篇：第二站', rightof('E4'), now() + 0.5, size=26, align='left', r=-0.01)
label('白话光互连 · 02', rightof('E8'), now() + 1.0, size=24, align='left', bg='red', r=-0.02)
hold(3.5, 0.03)
DUR = now()

# ---------- 检查 ----------
def ongrid(t): return abs(t * 8 - round(t * 8)) < 1e-6
bad = [(k, v) for k, v in [('cam', c['t']) for c in CAM] + [('mark', m['t'][0]) for m in MARKS] + [('label', l['at']) for l in LABELS] if not ongrid(v)]
assert not bad, bad
assert all(CAM[i]['t'] < CAM[i + 1]['t'] for i in range(len(CAM) - 1)), [c['t'] for c in CAM]
def camseg(t):
    for i in range(1, len(CAM)):
        if t <= CAM[i]['t']: return CAM[i - 1], CAM[i]
    return CAM[-1], CAM[-1]
def cam_state(t):
    a, b = camseg(t)
    if a is b: return a
    p = (t - a['t']) / (b['t'] - a['t']); return dict(x=a['x'] + (b['x'] - a['x']) * p, y=a['y'] + (b['y'] - a['y']) * p, z=a['z'] * (b['z'] / a['z']) ** p)
for m in MARKS:
    a, b = camseg(m['t'][0] + 0.01); assert b['e'] == 'lin', f"标注 {m['clip']} {m['t']} 时镜头在动"
    for tt in m['t']:
        k = cam_state(tt); c = CLIPS[m['clip']]; w = (c['crop'][2] - c['crop'][0]) * c['k']
        sx0 = (c['at'][0] - w / 2 - k['x']) * k['z'] + 540; sx1 = (c['at'][0] + w / 2 - k['x']) * k['z'] + 540; sy = (c['at'][1] - k['y']) * k['z'] + 960
        assert sx0 > 20 and sx1 < 1060 and 200 < sy < 1860, f"{m['clip']}「{c['text']}」读的时候不在画面里：x {sx0:.0f}–{sx1:.0f}, y {sy:.0f}"
out = dict(dur=DUR, bpm=120, K=K, clips=CLIPS, cards=CARDS, prints=PRINTS, cardLabels=CARD_LABELS, cue=CUE, marks=MARKS, pmarks=PMARKS, labels=LABELS, strings=STRINGS, cam=CAM,
           stick={}, pops=[], over=OVER, travel=[], station=[[1, HUD_IN + 1.5]], hudIn=HUD_IN, lens=LENS, stacks=STACKS, sfx=sorted(SFX, key=lambda s: s['t']))
json.dump(out, open(os.path.join(ROOT, '代码工程/ep2/desk.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('desk.json', DUR, 's,', len(CLIPS), 'strips,', len(PRINTS), 'prints,', len(MARKS), 'marks,', len(CAM), 'cam keys,', len(SFX), 'sfx;', 'z:', {k: v['z'] for k, v in STACKS.items()})
