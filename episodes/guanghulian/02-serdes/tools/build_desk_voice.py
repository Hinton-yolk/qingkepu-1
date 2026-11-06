# 白话光互连 02 · 配旁白样片（开头约 70 秒）—— 布局沿用正片，时间表按旁白排：说到哪句，镜头去哪、纸条亮哪条、荧光笔划哪几个字
# 运行：python3 tools/build_desk_voice.py → 代码工程/ep2/desk_voice.json；旁白每句的音频在 配音/fish/，停顿分析在 配音/align_raw.json
# 运行：python3 tools/build_desk.py → 代码工程/ep2/desk.json（画面读）＋ 配乐读同一份；同时把原文短条裁到 代码工程/assets/strips/
# 语法同第一篇第二版：原文按行剪成短纸条叠成一摞（整摞都在画面里），读字时镜头不动；
# 系列规定（用户 2026-11-03）：只用文章的文字，不把文章里的图片/信息图放进片子；
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

place_stack('why', ['W0', 'W1', 'W2', 'W3'], R)
LAST[0] = 0
place_stack('intro', ['T1', 'I1', 'I2'], L); place_stack('meta', ['M1', 'M2', 'M3', 'M4'], L)
place_card('K1', 'serdes2', L, 900, 1250, -0.008); place_stack('name', ['N1', 'N2', 'N3', 'N4'], L)
place_stack('r1', ['R1', 'R2', 'R3', 'R4'], R); place_card('K3', 'pins', R, 900, 860, 0.008)
place_stack('r2', ['Q1', 'Q2', 'Q3', 'Q4', 'Q5'], L); place_card('K4', 'skew', L, 900, 1000, -0.008)
place_stack('lanes', ['L1', 'L2', 'L3'], R); place_card('K5', 'lanes', R, 900, 760, 0.01)
place_stack('oa', ['O1', 'O2', 'O3'], L)
place_stack('ob', ['O4', 'O5', 'O6', 'O7'], R)
place_stack('oc', ['O8', 'O9'], R); place_card('K6', 'clock', R, 900, 1000, -0.008)
place_stack('od', ['X1', 'X2', 'X3', 'X4', 'X5'], R)
place_stack('hard', ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'], L); place_card('K7', 'double', L, 900, 1150, 0.008)
place_stack('inv', ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7'], R); place_card('K8', 'embed', R, 900, 900, -0.01)
place_stack('ask', ['Y1', 'Y2', 'Y3', 'Y4', 'Y5'], L)
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
def clabel(cid, text, cx, cy, at, size=40, align='center', bg='cream', r=0.0, rate=24):
    CARD_LABELS[cid].append(dict(text=text, x=cx, y=cy, at=round(at, 4), size=size, align=align, bg=bg, r=r, rate=rate)); SFX.append(dict(t=round(at, 4), kind='label', text=text, rate=rate))
def string(key, a, b, d=0.75, sag=0.06):   # 旁白版：红线和镜头移动同时开始
    STRINGS.append(dict(key=key, a=a, b=b, t=[now(), round(now() + d, 4)], sag=sag, route=False)); SFX.append(dict(t=now(), kind='string', dur=d))
def sfx(t, kind, **kw): SFX.append(dict(t=round(t, 4), kind=kind, **kw))
def edge(cid, side='r'):
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']; return P(cid, (x1 + 2) if side == 'r' else (x0 - 2), (y0 + y1) / 2)
def ptop(pid): p = PRINTS[pid]; return [p['at'][0], p['at'][1] - p['h'] / 2 - 10]
def pbot(pid): p = PRINTS[pid]; return [p['at'][0] + 200, p['at'][1] + p['h'] / 2 + 10]
def ctop(cid, dx=0): c = CARDS[cid]; return PC(cid, dx, -c['h'] / 2 + 30)
def cbot(cid, dx=0): c = CARDS[cid]; return PC(cid, dx, c['h'] / 2 - 30)
def PZ(pid, fill=1.0): return round(min(1.9, 1080 * 0.94 / PRINTS[pid]['w'] * fill), 3)


# ======================= 旁白时间表 =======================
SCRIPT = {s['id']: s for s in json.load(open(os.path.join(ROOT, '配音/script.json'), encoding='utf-8'))}
ALIGN = json.load(open(os.path.join(ROOT, '配音/align_raw.json'), encoding='utf-8'))
PUNCT = set('，：；。？、 ')
def g8(t): return round(round(t * 8) / 8, 4)
def tmap(lid, ci):
    """旁白第 lid 句里第 ci 个字大约在几秒说出：按标点分句，句与句之间对到实测的停顿上，句内按字数均分"""
    text = SCRIPT[lid]['text']; A = ALIGN[lid]; on, off, pauses = A['on'], A['off'], A['pauses']
    cl = A['clauses']; bounds = [0]
    for c in cl: bounds.append(bounds[-1] + len(c))
    nchar = lambda a, b: sum(1 for ch in text[a:b] if ch not in PUNCT) or 1
    total = nchar(0, len(text)); spans = []; cur = on; used = -1
    for k in range(len(cl)):
        est_end = on + (off - on) * nchar(0, bounds[k + 1]) / total
        if k == len(cl) - 1: spans.append((cur, off)); break
        cand = [(abs((p[0] + p[1]) / 2 - est_end), j, p) for j, p in enumerate(pauses) if j > used]
        if cand and min(cand)[0] < 0.6: _, used, p = min(cand); spans.append((cur, p[0])); cur = p[1]
        else: spans.append((cur, est_end)); cur = est_end
    for k in range(len(cl)):
        if bounds[k] <= ci <= bounds[k + 1]:
            a, b = spans[k]; f = nchar(bounds[k], ci) / nchar(bounds[k], bounds[k + 1]) if ci > bounds[k] else 0
            return a + (b - a) * min(1, f)
    return off
VOICE, FOCUS, SUBS = [], [], []
LINE = {}
def speak(lid, gap=0.375):
    t0 = g8(now()); VOICE.append(dict(id=lid, t=t0, file=f'配音/fish/{lid}.wav')); LINE[lid] = t0
    d = ALIGN[lid]['dur']; return t0, d
def span(lid, phrase):
    text = SCRIPT[lid]['text']; i = text.find(phrase); assert i >= 0, f'旁白 {lid} 里没有「{phrase}」'
    return LINE[lid] + tmap(lid, i), LINE[lid] + tmap(lid, i + len(phrase))
def vmark(cid, kind, strip_phrase, lid, spoken, mind=0.375):
    a, b = span(lid, spoken); t0 = g8(a - 0.06); d = max(mind, g8(b - a))
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']
    run = [r for r in runs(c['page'], strip_phrase) if x0 <= r[0][1] and r[-1][2] <= x1 and y0 <= r[0][3] <= y1]; assert run, f'「{strip_phrase}」不在短条 {cid} 里'
    MARKS.append(dict(clip=cid, kind=kind, segs=boxes(run[0]), t=[t0, round(t0 + d, 4)], seed=len(MARKS) + 2)); SFX.append(dict(t=t0, kind='marker' if kind == 'hl' else 'pen', dur=d, soft=1))
def focus(stack, ids, a, b): FOCUS.append(dict(stack=stack, ids=ids, t=[round(a, 3), round(b, 3)]))
def after(lid, gap=0.5): adv(g8(LINE[lid] + ALIGN[lid]['dur'] + gap - now()))
def speak_hold(lid, gap=0.5): speak(lid); after(lid, gap); hold(0, 0)

# --- 钩子：原文的问题那一摞 ---
cam(0, SC('why'), SZ('why'), 'lin')
label('白话光互连 · 02', [SC('why')[0], STACKS['why']['bb'][1] - 90], 0.0, size=28, bg='red', r=-0.02, rate=20)
adv(0.25)
speak('L1'); focus('why', ['W1', 'W2'], LINE['L1'], LINE['L1'] + ALIGN['L1']['dur'] + 0.3)
vmark('W1', 'hl', '并排走似乎更快', 'L1', '并排走似乎更快'); vmark('W2', 'hl', '修几十条路，几十件货同时出发', 'L1', '修几十条路，几十件货同时出发')
after('L1', 0.25)
speak('L2'); focus('why', ['W3'], LINE['L2'], LINE['L2'] + ALIGN['L2']['dur'] + 0.3)
vmark('W3', 'hl', '速度一高', 'L2', '速度一高'); vmark('W3', 'circle', '越来越吃力', 'L2', '越来越吃力', 0.625)
after('L2', 0.25)
speak('L3'); focus('why', ['W0'], LINE['L3'], LINE['L3'] + ALIGN['L3']['dur'] + 0.4)
vmark('W0', 'hl', '而要排成一列', 'L3', '让数据排成一列'); vmark('W0', 'circle', '为什么不并排走', 'L3', '为什么？', 0.625)
after('L3', 0.375); hold(0, 0)
# --- 回到第一站 ---
go(SC('intro'), SZ('intro'), 1.0, 'cubic', 0.12); HUD_IN = now()
speak('L4'); vmark('I1', 'hl', '走完了五站', 'L4', '走完了五站'); vmark('I2', 'hl', '回到第一站：出发', 'L4', '回到第一站：出发')
after('L4', 0.375); hold(0, 0)
# --- 先演比喻和机制（「SerDes」那一条先压暗，不剧透名字）---
go(SC('meta'), SZ('meta'), 1.0)
speak('L5'); focus('meta', ['M2'], LINE['L5'] - 0.2, LINE['L5'] + ALIGN['L5']['dur'] + 0.2); vmark('M2', 'hl', '并排摆着', 'L5', '并排摆着')
after('L5', 0.25)
speak('L6'); focus('meta', ['M3'], LINE['L6'] - 0.2, LINE['L6'] + ALIGN['L6']['dur'] + 0.2); vmark('M3', 'hl', '排成一列', 'L6', '排成一列')
after('L6', 0.25)
speak('L7'); focus('meta', ['M4'], LINE['L7'] - 0.2, LINE['L7'] + ALIGN['L7']['dur'] + 0.2); vmark('M4', 'hl', '拆开、重新并排摆好', 'L7', '拆开、重新并排摆好')
after('L7', 0.25); hold(0, 0)
string('meta-K1', edge('M4'), ctop('K1', 250), 0.5); go(PC('K1', 0, 143), 0.95, 1.0)
speak('L8'); a_ser, _ = span('L8', '发出去时排成一列'); a_des, _ = span('L8', '到了那边')
t0 = g8(now()); CUE['K1'] = dict(t0=t0, ser=g8(a_ser - 0.25), des=g8(a_des), end=g8(a_des) + 2.5)
clabel('K1', '发货口：排成一列', -390, -560, g8(a_ser), align='left'); clabel('K1', '收货口：拆回一排', -390, 70, g8(a_des), align='left')
sfx(g8(a_ser - 0.25), 'serdes', dur=2.4); sfx(g8(a_des), 'fan', dur=2.0)
adv(g8(CUE['K1']['end'] - now())); hold(0, 0)
# --- 再报名字 ---
string('K1-name', cbot('K1', -250), edge('N1', 'l'), 0.5); go(SC('name'), SZ('name'), 1.0)
speak('L9'); a, _ = span('L9', 'SerDes')
label('SerDes', [SC('name')[0], STACKS['name']['bb'][1] - 100], g8(a), size=64, bg='red', r=-0.02, rate=20)
focus('name', ['N1', 'N2'], *span('L9', 'Ser，串行化')[:1], span('L9', '负责排成一列')[1] + 0.2)
focus('name', ['N3', 'N4'], span('L9', 'Des，解串')[0] - 0.1, LINE['L9'] + ALIGN['L9']['dur'] + 0.4)
vmark('N1', 'hl', 'Serializer（串行化）', 'L9', 'Ser，串行化'); vmark('N2', 'hl', '排成一列', 'L9', '负责排成一列')
vmark('N3', 'hl', 'Deserializer', 'L9', 'Des，解串'); vmark('N4', 'hl', '拆回一排', 'L9', '负责拆回一排')
after('L9', 0.375); hold(0, 0)
# --- 为什么不并排走：第一，出口不够 ---
go(SC('r1'), SZ('r1'), 1.0, 'sine', 0.12)
speak('L10'); focus('r1', ['R1'], LINE['L10'], LINE['L10'] + ALIGN['L10']['dur'] + 0.2); vmark('R1', 'hl', '出口不够', 'L10', '出口不够')
after('L10', 0.25)
speak('L11'); focus('r1', ['R2', 'R3', 'R4'], LINE['L11'], LINE['L11'] + ALIGN['L11']['dur'] + 0.3)
vmark('R2', 'hl', '引脚数量有限', 'L11', '引脚数量有限'); vmark('R4', 'hl', '多占面积、多耗电', 'L11', '多占面积、多耗电')
after('L11', 0.25); hold(0, 0)
string('r1-K3', edge('R4'), ctop('K3', 250), 0.5); go(PC('K3', 0, 54), 1.12, 1.0)
t0 = g8(now()); CUE['K3'] = dict(t0=t0, lines=[t0 + 0.25 + 0.25 * i for i in range(10)], end=t0 + 3.5)
clabel('K3', '出口有限', -390, -360, t0 + 0.25, align='left', bg='red'); clabel('K3', '多一条线：多占面积、多耗电', 0, 395, t0 + 1.75)
for i, tt in enumerate(CUE['K3']['lines']): sfx(tt, 'pin', n=i)
adv(0.25); speak('L12'); adv(g8(max(t0 + 3.5, LINE['L12'] + ALIGN['L12']['dur'] + 0.25) - now())); hold(0, 0)
# --- 第二个原因（悬念收尾）---
string('K3-r2', cbot('K3', -250), edge('Q1', 'r'), 0.5); go(SC('r2'), SZ('r2'), 1.0, 'sine', 0.12)
speak('L13'); focus('r2', ['Q1'], LINE['L13'] - 0.2, LINE['L13'] + ALIGN['L13']['dur'] + 1.25); vmark('Q1', 'hl', '很难同时到达', 'L13', '很难同时到达')
after('L13', 1.25); hold(0, 0)
def build_subs():
    out = []
    for v in VOICE:
        lid = v['id']; text = SCRIPT[lid]['text']; cl = ALIGN[lid]['clauses']; bounds = [0]
        for c in cl: bounds.append(bounds[-1] + len(c))
        if SCRIPT[lid].get('sub'):                 # 手写的字幕断句（script.json 里的 sub）：按字找到每条在这句旁白里的位置
            pos = 0
            for seg_ in SCRIPT[lid]['sub']:
                core = seg_.rstrip('？'); i = text.find(core, pos); assert i >= 0, (lid, seg_)
                j = i + len(core); pos = j
                out.append(dict(text=seg_, t=[round(LINE[lid] + tmap(lid, i) - 0.08, 3), round(LINE[lid] + tmap(lid, j) + 0.15, 3)]))
            continue
        groups, cur = [], []
        vis = lambda x: len(x.strip().rstrip('，。；：、？ '))
        for k, c in enumerate(cl):
            cur.append(k); body = ''.join(cl[j] for j in cur); n = vis(body)
            nxt = vis(cl[k + 1]) if k + 1 < len(cl) else 0
            hard = c.strip()[-1:] in ('。', '？', '；')
            if hard or k == len(cl) - 1 or n + nxt > 16 or (n >= 8 and nxt >= 5): groups.append(cur); cur = []
        if cur: groups.append(cur)
        for g in groups:
            a_, b_ = bounds[g[0]], bounds[g[-1] + 1]; txt_ = text[a_:b_].strip().rstrip('，。；：、 ').replace(' ', ' ')
            out.append(dict(text=txt_, t=[round(LINE[lid] + tmap(lid, a_) - 0.08, 3), round(LINE[lid] + tmap(lid, b_) + 0.15, 3)]))
    for i in range(len(out) - 1):                      # 两条之间空隙很短就接上，不闪
        if out[i + 1]['t'][0] - out[i]['t'][1] < 0.45: out[i]['t'][1] = out[i + 1]['t'][0]
    return out
SUBS = build_subs()
# 第四版：只在「屏上没有这句话」的地方出字幕——镜头在卡片上、术语出现、旁白说了纸条上没有的内容；
# 旁白和眼前那摞纸条说的基本是同一句（连续相同的字占到 60% 以上）就不出，避免重复
import difflib
CLEAN = lambda x: ''.join(ch for ch in x if ch not in '，。；：、？！“”‘’（）() ·')
def cam_mid(t):
    for i in range(1, len(CAM)):
        if t <= CAM[i]['t']:
            a_, b_ = CAM[i - 1], CAM[i]; p_ = (t - a_['t']) / max(1e-6, b_['t'] - a_['t']); return a_['x'] + (b_['x'] - a_['x']) * p_, a_['y'] + (b_['y'] - a_['y']) * p_
    return CAM[-1]['x'], CAM[-1]['y']
def on_screen(t):
    x, y = cam_mid(t)
    for cid, cd in CARDS.items():
        if abs(x - cd['at'][0]) < cd['w'] / 2 and abs(y - cd['at'][1]) < cd['h'] / 2: return 'card', cid
    best = min(STACKS.items(), key=lambda kv: math.hypot(x - (kv[1]['bb'][0] + kv[1]['bb'][2]) / 2, y - (kv[1]['bb'][1] + kv[1]['bb'][3]) / 2))
    return 'stack', best[0]
for x_ in SUBS:
    kind, name = on_screen((x_['t'][0] + x_['t'][1]) / 2)
    if kind == 'card': x_['show'] = True; x_['why'] = '卡片'; continue
    sub = CLEAN(x_['text']); ref = CLEAN(''.join(CLIPS[i]['text'] for i in STACKS[name]['ids']))
    same = sum(b.size for b in difflib.SequenceMatcher(None, sub, ref, autojunk=False).get_matching_blocks() if b.size >= 2)
    x_['overlap'] = round(same / max(1, len(sub)), 2); x_['show'] = x_['overlap'] < 0.6; x_['why'] = f"纸条 {name} 重合 {x_['overlap']}"
# 连续出现的几条字幕合成一段，底下的纸色带整段只淡入淡出一次，不闪
runs_ = []
for i, x_ in enumerate(SUBS):
    if not x_['show']: continue
    if runs_ and i - 1 >= 0 and SUBS[i - 1]['show'] and x_['t'][0] - SUBS[i - 1]['t'][1] < 0.45: runs_[-1][1] = x_['t'][1]; runs_[-1][2].append(x_)
    else: runs_.append([x_['t'][0], x_['t'][1], [x_]])
for r0, r1, xs in runs_:
    for x_ in xs: x_['run'] = [round(r0, 3), round(r1, 3)]
assert all(len(x['text']) <= 20 for x in SUBS), [x['text'] for x in SUBS if len(x['text']) > 18]
DUR = now(); OVER = dict(x=850, y=3000, z=0.2); LENS = dict(at=[0, 0], zin=[1e9, 1e9 + 1], open=[1e9, 1e9 + 1], band=1e9, zooms=[1e9, 1e9, 1e9], bits=1e9, lbl=1e9, out=[1e9, 1e9 + 1], zmax=40)

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
        assert not (1470 < sy < 1660), f"{m['clip']} 划重点时落在字幕带里：y {sy:.0f}"
        assert sx0 > 20 and sx1 < 1060 and 200 < sy < 1860, f"{m['clip']}「{c['text']}」读的时候不在画面里：x {sx0:.0f}–{sx1:.0f}, y {sy:.0f}"

out = dict(dur=DUR, bpm=120, K=K, clips=CLIPS, cards=CARDS, prints=PRINTS, cardLabels=CARD_LABELS, cue=CUE, marks=MARKS, pmarks=PMARKS, labels=LABELS, strings=STRINGS, cam=CAM,
           stick={}, pops=[], over=OVER, travel=[], station=[[1, HUD_IN + 1.5]], hudIn=HUD_IN, lens=LENS, stacks=STACKS, focus=FOCUS, voice=VOICE, subs=SUBS, sfx=sorted(SFX, key=lambda s: s['t']))
json.dump(out, open(os.path.join(ROOT, '代码工程/ep2/desk_voice.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('desk_voice.json', DUR, 's,', len(MARKS), 'marks,', len(CAM), 'cam keys,', len(VOICE), 'voice lines,', len(FOCUS), 'focus windows')
