# 白话光互连 04《检修站：模糊的信号怎么修回来？》Vox 竖屏 —— 桌面布局与时间表（唯一的真源）
# 运行：python3 tools/build_desk.py → 代码工程/ep4/desk.json（画面读）＋ 配乐读同一份；同时把原文短条裁到 代码工程/assets/strips/
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

def strip(cid, page, text, kscale=None, occ=0):
    run = runs(page, text)[occ]; assert len(boxes(run)) == 1, f'「{text}」跨行了'
    size = run[0][4]; base = run[0][3]
    x0, x1 = run[0][1] - 4.5, run[-1][2] + 4.5; y0, y1 = base - 0.93 * size - 4.0, base + 0.24 * size + 4.0
    im = page_img(page).crop((round(x0 * DPI), round(y0 * DPI), round(x1 * DPI), round(y1 * DPI)))
    dr = ImageDraw.Draw(im); gl, gr = round((run[0][1] - x0) * DPI) - 2, round((run[-1][2] - x0) * DPI) + 2
    dr.rectangle([0, 0, max(0, gl), im.height], fill='white'); dr.rectangle([min(im.width, gr), 0, im.width, im.height], fill='white')
    # 上下也只留这一行：第三篇的 PDF 行距较紧，裁边会带进上一行的底、下一行的顶，盖成白纸
    tc, bc = round((base - 0.95 * size - y0) * DPI), round((base + 0.25 * size - y0) * DPI)
    dr.rectangle([0, 0, im.width, max(0, tc)], fill='white'); dr.rectangle([0, min(im.height, bc), im.width, im.height], fill='white')
    src = f'assets/strips/{cid}.png'; im.save(os.path.join(ROOT, '代码工程', src), optimize=True)
    k = K * (kscale if kscale else (0.85 if size > 12 else 1.0))
    CLIPS[cid] = dict(src=src, page=page, crop=[round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)], at=[0, 0], r=0.0, seed=sum(map(ord, cid)) % 97 + 5, text=text, k=k)
    return cid

# ---------- 原文短条 ----------
S = [('T1', 1, '一语道破·白话光互连04｜'), ('T2', 1, '检修站：模糊的信号怎么修回来？'),
 ('I1', 1, '电信号在铜线上会变弱、拖尾，'), ('I2', 1, '跑得越快越远，越难认清。'), ('I3', 1, '这一篇看看，人们是怎'), ('I4', 1, '么把它修回来的。'),
 ('M1', 1, '还是用那条长走廊来想：'), ('M2', 1, '对面听不清，可以怎么办？'), ('M3', 1, '先想办法让话更容易听清；'), ('M4', 1, '还不行，就在中'), ('M5', 1, '间安排一个传话员，'), ('M6', 1, '听清以后重新说一遍。'),
 ('Q0', 1, '这正好对应信号修复的三个问题：'), ('Q1', 1, '怎样让信号更容易认？'), ('Q2', 1, '怎样认清以后重新出发？'), ('Q3', 1, '这些处理又怎'), ('Q4', 1, '样借助算法完成？'),
 ('A0', 1, '第一步：让信号更容易认——均衡'), ('A1', 1, '铜线对快速跳变削弱得更厉害，'), ('A2', 1, '台阶的棱角被削掉，才拖出了尾巴。'), ('A3', 1, '既然知道路会削弱哪一部分，'), ('A4', 1, '就可以反过来补：'),
 ('A5', 1, '发送端把容易被削弱的跳变提前加强一点，'), ('A6', 1, '再把被削弱的部分补回来。'), ('A7', 1, '这不是把整个信号一起放大，'), ('A8', 1, '而是调整强弱之间的比例：'),
 ('B1', 1, '就像知道走廊会吞掉高音，'), ('B2', 1, '说话的人特意把高音喊重，'), ('B3', 1, '听的人再戴上专门'), ('B4', 1, '补高音的耳机。'), ('B5', 1, '这种做法业内叫“均衡”。'), ('B6', 1, '很大一部分就是均衡。'),
 ('C0', 1, '第二步：认清以后重新出发——Retimer'), ('C1', 1, '路太长，光靠两头均衡不够用时，'), ('C2', 1, '就在路中间设一个检修站。'),
 ('C3', 2, '它先做均衡，把信号整理到容易辨认，'), ('C4', 2, '再判断每一位是0还是1，找准节拍，'), ('C5', 2, '重新发出一条干净'), ('C6', 2, '的新信号。'), ('C7', 2, '后半程信号等于重新出发，'), ('C8', 2, '前半程积累的模糊和拖尾不会再带下去。'),
 ('D1', 2, '但有个前提：传话员得先听对。'), ('D2', 2, '如果原话已经听错，再清楚地复述，'), ('D3', 2, '也只是清楚地说出了错的内'), ('D4', 2, '只能救回还在可恢复范围内的信号。'),
 ('R1', 2, '做这件事的芯片叫Retimer，'), ('R2', 2, '意思是“重新打节拍”。'), ('R3', 2, '还有一种更轻的检修站叫Redriver，'), ('R4', 2, '它同样会做均衡，但不重新认数据、'), ('R5', 2, '不重新打节拍，'), ('R6', 2, '更省电、延迟也更低，'), ('R7', 2, '适合路况没那么差的场合。'),
 ('P0', 2, '这些处理怎样用算法完成——DSP'), ('P1', 2, '均衡也好，重新打节拍也好，'), ('P2', 2, '既可以用电路直接处理，'), ('P3', 2, '也可以借助数字算法完成，'), ('P4', 2, 'DSP（数字信号处理）。'),
 ('S1', 2, 'DSP的做法是：对收到的波形高速采样，'), ('S2', 2, '把它在一连串时刻的高低记成数字，'), ('S3', 2, '推算出原来发的是0还是1。'), ('S4', 2, '这里有两种“数字”要分清：'), ('S5', 2, '采样得到的数字，描述的是收到'), ('S6', 2, '最后算出来的，才是原本的数据。'),
 ('S7', 2, '算法的好处是灵活，'), ('S8', 2, '可以把前后很多个比特的拖尾'), ('S9', 2, '一起考虑进去，'),
 ('W1', 2, 'DSP不是第三种检修站，'), ('W2', 2, '而是检修站里的一种工具：'), ('W3', 2, '它可以藏在SerDes里，也可以用在'), ('W4', 2, 'Retimer里。'), ('W5', 2, '今天的高速光模块里，'), ('W6', 2, '电信号换乘光之前，'), ('W7', 2, '通常也有一颗这样的DSP芯片。'),
 ('X0', 3, '处理得越多，代价越大'), ('X1', 3, '多做一些采样、计算和重新打节拍，'), ('X2', 3, '通常就要多花电，也会增加一点延'), ('X3', 3, '迟。'), ('X4', 3, '所以系统会看路况来选：'), ('X5', 3, '路况好时能省则省，'), ('X6', 3, '路况差时才上更重的处理。'),
 ('Y1', 3, '一个大集群里，这类处理环节数量庞大，'), ('Y2', 3, '功耗会累积起来。'), ('Y3', 3, '要么把路修短，让处理的需求变小；'), ('Y4', 3, '要么把处理工作交给链路上已有的芯片，'), ('Y5', 3, '放一颗专门的检修芯片。'),
 ('V1', 3, '在规定的速度、路况和出错率下，'), ('V2', 3, '每传一个比特花多少电，又增加多'), ('V3', 3, '少延迟？'), ('V4', 3, '比较时还要留意范围：'), ('V5', 3, '有的公司只报核心电路的功耗，'), ('V6', 3, '有的报整颗芯片；'),
 ('V8', 3, 'DSP，也可能只是把工作转给了主芯片。'), ('V9', 3, '省没省电，要看整条链路。'),
 ('E0', 3, '一句话带走'), ('E1', 3, '修信号分两步：'), ('E2', 3, '先均衡，让信号更容易认；'), ('E3', 3, '必要时由Retimer认清数据、'), ('E4', 3, '找准节拍、重新发送。'),
 ('E5', 3, 'DSP是用数字算法完成这些处理的工具。'), ('E6', 3, '处理得越多，代价越大，'), ('E7', 3, '而且任何检修都有边界。')]
for cid, p, t in S: strip(cid, p, t, kscale=1.3 if cid in ('T1', 'T2') else None)
strip('V7', 3, '少放一颗', occ=1)
strip('E9', 3, '本文仅做科普与行业分析，不构成投资建议。', kscale=0.62)

# ---------- 摆放：两列，按出场顺序往下排 ----------
L, R = 0, 1700
COLY = {L: 0, R: 0}; LAST = [0]
STACK_OF = {}
STACKS = {}
def place_stack(name, ids, col, gap=26, x_off=0):
    rnd = random.Random(sum(map(ord, name))); top = max(COLY[col], LAST[0]); y = top; xl = col - 250 + x_off; bb = [1e9, 1e9, -1e9, -1e9]
    for cid in ids:
        c = CLIPS[cid]; w = (c['crop'][2] - c['crop'][0]) * c['k']; h = (c['crop'][3] - c['crop'][1]) * c['k']
        c['at'] = [round(xl + rnd.uniform(-10, 14) + w / 2, 1), round(y + h / 2, 1)]; c['r'] = round(rnd.uniform(-0.016, 0.016), 4)
        bb = [min(bb[0], c['at'][0] - w / 2), min(bb[1], y), max(bb[2], c['at'][0] + w / 2), max(bb[3], y + h)]; y += h + gap
    wmax = max((CLIPS[c]['crop'][2] - CLIPS[c]['crop'][0]) * CLIPS[c]['k'] for c in ids)
    STACKS[name] = dict(ids=ids, bb=bb, z=round(min(2.05, 960 / (wmax + 25)), 3)); COLY[col] = bb[3] + 230; LAST[0] = top
    for cid in ids: STACK_OF[cid] = name
def place_card(cid, kind, col, w, h, r):
    top = max(COLY[col], LAST[0]); CARDS[cid] = dict(kind=kind, at=[col, top + h / 2], w=w, h=h, r=r); COLY[col] = top + h + 230; LAST[0] = top
def place_print(pid, src, col, r, w=980):
    top = max(COLY[col], LAST[0]); h = round(w * 520 / 780); PRINTS[pid] = dict(src=src, at=[col, top + h / 2 + 20], w=w, h=h, r=r, seed=len(PRINTS) * 13 + 3)
    COLY[col] = top + h + 270; LAST[0] = top
def SC(name, dy=0): b = STACKS[name]['bb']; return [round((b[0] + b[2]) / 2, 1), round((b[1] + b[3]) / 2 + dy, 1)]
def SZ(name): return STACKS[name]['z']

place_stack('title', ['T1', 'T2'], L); place_card('H0', 'hook4', L, 900, 760, -0.008)
place_stack('qs', ['Q0', 'Q1', 'Q2', 'Q3', 'Q4'], L)
LAST[0] = 0
place_stack('intro', ['I1', 'I2', 'I3', 'I4'], R); place_stack('meta', ['M1', 'M2', 'M3', 'M4', 'M5', 'M6'], R); place_card('K1', 'relay', R, 900, 720, 0.008)
place_stack('eq', ['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8'], L); place_card('K2', 'eq', L, 900, 1200, -0.008)
place_stack('hi', ['B1', 'B2', 'B3', 'B4', 'B5', 'B6'], R)
place_stack('ret', ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8'], R); place_card('K3', 'retimer', R, 900, 1100, 0.008)
place_stack('wrong', ['D1', 'D2', 'D3', 'D4'], L); place_stack('name', ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7'], L); place_card('K4', 'redriver', L, 900, 1000, -0.008)
place_stack('dsp', ['P0', 'P1', 'P2', 'P3', 'P4'], R); place_stack('samp', ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9'], R); place_card('K5', 'dspcalc', R, 900, 1050, 0.008)
place_stack('where', ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7'], L); place_card('K6', 'where', L, 900, 900, -0.01)
place_stack('cost', ['X0', 'X1', 'X2', 'X3', 'X4', 'X5', 'X6'], R); place_card('K7', 'cost', R, 900, 980, 0.008)
place_stack('trend', ['Y1', 'Y2', 'Y3', 'Y4', 'Y5'], L); place_stack('inv', ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9'], L); place_card('K8', 'scope', L, 900, 1100, -0.008)
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E9'], 850)

# ---------- 时间表工具 ----------
MARKS, PMARKS, LABELS, STRINGS, CAM, SFX = [], [], [], [], [], []
CARD_LABELS = {k: [] for k in CARDS}; CUE = {}
T = [0.0]
def now(): return T[0]
def adv(d): assert abs(d * 8 - round(d * 8)) < 1e-9, d; T[0] = round(T[0] + d, 4)
def cam(t, xy, z, e='sine'): CAM.append(dict(t=round(t, 4), x=xy[0], y=xy[1], z=z, e=e))
def hold(d, dz=0.02): last = CAM[-1]; adv(d); cam(now(), [last['x'], last['y']], round(last['z'] * (1 + dz), 4), 'lin')
def go(xy, z, d=1.5, e='sine', g=0.08): SFX.append(dict(t=now(), kind='whoosh', dur=d, g=g)); adv(d); cam(now(), xy, z, e)
# 荧光笔颜色（系列规则，第三篇起）：同一摞文字每来一轮换一种颜色——荧光黄 → 珊瑚粉 → 薄荷青 → 荧光黄…；同一轮里连续划的几处同色
HLC = ['rgba(222,208,20,.88)', 'rgba(232,140,120,.72)', 'rgba(120,205,190,.70)']
VISIT = {}; PASS_COL = {}; HL_PASSES = {}
def arrive(name): VISIT[name] = VISIT.get(name, 0) + 1          # 镜头来到（或回到）这一摞：开始新的一轮
def gostack(name, d=1.5, e='sine', g=0.08, dy=0): go(SC(name, dy), SZ(name), d, e, g); arrive(name)
def hop(name, d=2.5, g=0.16):          # 远距离跳回一摞：先拉远（看到全桌这一段），再推近；两段 qin/qout 接起来，中间不停
    a_ = CAM[-1]; b_ = SC(name); dist = math.hypot(b_[0] - a_['x'], b_[1] - a_['y']); zm = round(max(0.22, min(0.9, 1500 / (dist + 1400))), 4)
    SFX.append(dict(t=now(), kind='whoosh', dur=d, g=g)); adv(d / 2); cam(now(), [(a_['x'] + b_[0]) / 2, (a_['y'] + b_[1]) / 2], zm, 'qin'); adv(d / 2); cam(now(), b_, SZ(name), 'qout'); arrive(name)
def hl_color(cid):
    st = STACK_OF.get(cid); assert st and VISIT.get(st), f'短条 {cid} 所在的那摞还没有镜头来过'
    key = (st, VISIT[st])
    if key not in PASS_COL: n = len(HL_PASSES.setdefault(st, [])); PASS_COL[key] = HLC[n % len(HLC)]; HL_PASSES[st].append((VISIT[st], PASS_COL[key], now()))
    return PASS_COL[key]
def mark(cid, kind, phrase, d, seed=None):
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']
    run = [r for r in runs(c['page'], phrase) if x0 <= r[0][1] and r[-1][2] <= x1 and y0 <= r[0][3] <= y1]; assert run, f'「{phrase}」不在短条 {cid} 里'
    MARKS.append(dict(clip=cid, kind=kind, segs=boxes(run[0]), t=[now(), round(now() + d, 4)], seed=seed or len(MARKS) + 2, **({'col': hl_color(cid)} if kind == 'hl' else {})))
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
# --- 钩子：标题（问题）＋ 正下方一张卡片：糊的信号进检修站，出来又清楚了 ---
tb = STACKS['title']['bb']; h0 = CARDS['H0']; span = (h0['at'][1] + h0['h'] / 2) - tb[1]
ux0, ux1 = min(tb[0], h0['at'][0] - h0['w'] / 2), max(tb[2], h0['at'][0] + h0['w'] / 2)
cam(0, [round((ux0 + ux1) / 2), round((tb[1] + h0['at'][1] + h0['h'] / 2) / 2)], round(min(1.1, 1560 / span, 1000 / (ux1 - ux0)), 3), 'lin'); arrive('title')
t0 = 0.25; CUE['H0'] = dict(t0=t0, e0=t0, end=5.0)
clabel('H0', '进站：糊的', -390, 210, 1.5, align='left', bg='red'); clabel('H0', '出站：又清楚了', 390, 210, 2.75, align='right')
sfx(t0, 'thock'); sfx(1.75, 'dsp')
adv(0.25); mark('T2', 'hl', '怎么修回来', 1.0); hold(3.75)
# --- 开场 ---
gostack('intro', 2.0, 'cubic', 0.14)
HUD_IN = now(); mark('I1', 'hl', '变弱、拖尾', 0.625); mark('I2', 'hl', '越难认清', 0.5); mark('I3', 'hl', '这一篇看看', 0.5); mark('I4', 'hl', '修回来', 0.5); hold(0.5)
gostack('meta')
mark('M2', 'hl', '对面听不清', 0.625); mark('M3', 'hl', '让话更容易听清', 0.75); mark('M5', 'hl', '安排一个传话员', 0.75); mark('M6', 'hl', '重新说一遍', 0.625); hold(0.375)
string('meta-K1', edge('M6'), ctop('K1', 250)); go(PC('K1', 0, 0), 1.12)
t0 = now(); CUE['K1'] = dict(t0=t0, words=[t0 + 0.25 + 0.4 * i for i in range(6)], relay=t0 + 2.25, end=t0 + 6.0)
clabel('K1', '越走越小、越糊', -390, -260, t0 + 1.25, align='left', bg='red'); clabel('K1', '传话员：听清后重说一遍', 390, 260, t0 + 3.0, align='right')
for tt in CUE['K1']['words']: sfx(tt, 'shout')
sfx(t0 + 2.25, 'click'); hold(6.0)
# --- 三个问题（第一轮：荧光黄）---
string('K1-qs', cbot('K1', -250), edge('Q0', 'r')); hop('qs')
mark('Q0', 'hl', '信号修复的三个问题', 1.0); hold(1.0)
# --- 第一步：均衡（回到问题摞，第二轮：珊瑚粉）---
mark('Q1', 'hl', '怎样让信号更容易认', 1.0); hold(0.5)
gostack('eq', 2.0, 'sine', 0.12)
mark('A0', 'hl', '均衡', 0.375); mark('A1', 'hl', '对快速跳变削弱得更厉害', 0.875); mark('A2', 'hl', '拖出了尾巴', 0.5)
mark('A3', 'hl', '知道路会削弱哪一部分', 0.75); mark('A4', 'hl', '反过来补', 0.5); mark('A5', 'hl', '提前加强一点', 0.625); mark('A6', 'hl', '补回来', 0.375)
mark('A7', 'hl', '不是把整个信号一起放大', 0.875); mark('A8', 'hl', '调整强弱之间的比例', 0.75); hold(0.375)
string('eq-K2', edge('A8'), ctop('K2', 250)); go(PC('K2', 0, 0), 1.1)
t0 = now(); CUE['K2'] = dict(t0=t0, rows=[t0 + 0.25, t0 + 2.25, t0 + 4.25], end=t0 + 7.0)
clabel('K2', '不补：棱角被削掉，拖出尾巴', -390, -520, t0 + 1.25, align='left', bg='red', size=36)
clabel('K2', '发送端：先把跳变加强一点', -390, -130, t0 + 3.0, align='left', size=36)
clabel('K2', '接收端：再补回来，接近方正', -390, 270, t0 + 5.0, align='left', size=36)
for tt in CUE['K2']['rows']: sfx(tt, 'thock')
sfx(t0 + 2.75, 'shave', dur=0.75); sfx(t0 + 5.25, 'ok'); hold(7.0)
string('K2-hi', cbot('K2', 250), edge('B1', 'l')); gostack('hi', 2.0, 'sine', 0.12)
mark('B1', 'hl', '走廊会吞掉高音', 0.75); mark('B2', 'hl', '特意把高音喊重', 0.75); mark('B4', 'hl', '补高音的耳机', 0.625); mark('B5', 'hl', '“均衡”', 0.5); mark('B6', 'hl', '很大一部分就是均衡', 0.75); hold(0.5)
# --- 第二步：Retimer（回到问题摞，第三轮：薄荷青）---
hop('qs'); mark('Q2', 'hl', '怎样认清以后重新出发', 1.0); hold(0.5)
hop('ret', 2.5, 0.14)
mark('C0', 'hl', 'Retimer', 0.5); mark('C1', 'hl', '两头均衡不够用时', 0.75); mark('C2', 'hl', '路中间设一个检修站', 0.75)
mark('C3', 'hl', '先做均衡', 0.5); mark('C4', 'hl', '判断每一位是0还是1', 0.75); mark('C4', 'hl', '找准节拍', 0.5); mark('C5', 'hl', '重新发出一条干净', 0.625)
mark('C7', 'hl', '重新出发', 0.5); mark('C8', 'hl', '不会再带下去', 0.625); hold(0.375)
string('ret-K3', edge('C8'), ctop('K3', 250)); go(PC('K3', 0, 0), 1.1)
t0 = now(); CUE['K3'] = dict(t0=t0, ok=t0 + 0.25, bad=t0 + 4.0, end=t0 + 8.0)
clabel('K3', 'Retimer：认清、打准节拍、重新发送', -390, -470, t0 + 1.75, align='left', size=36)
clabel('K3', '原话听错：清楚地发出错的', -390, 470, t0 + 6.0, align='left', bg='red', size=36)
sfx(t0 + 1.25, 'dsp'); sfx(t0 + 1.75, 'ok'); sfx(t0 + 5.0, 'dsp'); sfx(t0 + 6.0, 'wrong'); hold(8.0)
string('K3-wrong', cbot('K3', -250), edge('D1', 'r')); gostack('wrong', 2.0, 'sine', 0.12)
mark('D1', 'hl', '传话员得先听对', 0.75); mark('D2', 'hl', '原话已经听错', 0.625); mark('D3', 'hl', '清楚地说出了错的内', 0.75); mark('D4', 'hl', '可恢复范围内', 0.625); hold(0.375)
gostack('name')
mark('R1', 'hl', 'Retimer', 0.5); mark('R2', 'hl', '“重新打节拍”', 0.625); mark('R3', 'hl', '更轻的检修站叫Redriver', 0.875); mark('R4', 'hl', '同样会做均衡', 0.5); mark('R4', 'hl', '不重新认数据', 0.5)
mark('R5', 'hl', '不重新打节拍', 0.5); mark('R6', 'hl', '更省电、延迟也更低', 0.75); mark('R7', 'hl', '路况没那么差', 0.5); hold(0.375)
string('name-K4', edge('R7'), ctop('K4', 250)); go(PC('K4', 0, 0), 1.12)
t0 = now(); CUE['K4'] = dict(t0=t0, rd=t0 + 0.25, rt=t0 + 2.5, meters=t0 + 4.5, end=t0 + 6.5)
clabel('K4', 'Redriver：只做均衡', -390, -420, t0 + 0.5, align='left', size=38); clabel('K4', 'Retimer：均衡＋认数据＋打节拍', -390, -20, t0 + 2.75, align='left', size=38)
sfx(t0 + 0.25, 'thock'); sfx(t0 + 2.5, 'thock'); sfx(t0 + 3.5, 'dsp'); sfx(t0 + 4.5, 'amp'); hold(6.5)
# --- DSP（回到问题摞，第四轮：回到荧光黄）---
hop('qs'); mark('Q3', 'hl', '这些处理又怎', 0.625); mark('Q4', 'hl', '样借助算法完成', 0.75); hold(0.5)
hop('dsp', 2.5, 0.14)
mark('P1', 'hl', '均衡也好，重新打节拍也好', 0.875); mark('P2', 'hl', '用电路直接处理', 0.625); mark('P3', 'hl', '借助数字算法完成', 0.75); mark('P4', 'hl', 'DSP（数字信号处理）', 0.75); hold(0.375)
gostack('samp')
mark('S1', 'hl', '高速采样', 0.5); hold(0.25)
ZC = (lambda r: P('S1', (r[0][1] + r[-1][2]) / 2, r[0][3] - 4.5))(runs(2, '高速采样')[0])
a = now(); cam(a + 0.5, ZC, 2.7, 'sine'); cam(a + 1.5, ZC, 40, 'cubic')
LENS = dict(at=ZC, zin=[a + 0.5, a + 1.5], open=[a + 0.75, a + 1.25], core=a + 1.5, samp=[a + 2.25, a + 3.75], lbl=a + 4.0, out=[a + 6.0, a + 7.0], zmax=40)
sfx(a + 0.5, 'riser', dur=1.0); sfx(a + 1.25, 'boom'); sfx(a + 2.25, 'samples', n=12, dur=1.5); sfx(a + 6.0, 'pullout', dur=1.0)
for txt_, at in [('收到的波形', a + 1.5), ('一连串时刻的高低，记成数字', a + 4.0)]: SFX.append(dict(t=at, kind='label', text=txt_, rate=14))
cam(a + 6.0, ZC, 40, 'lin'); cam(a + 7.0, SC('samp'), SZ('samp'), 'cubic'); T[0] = a + 7.0; arrive('samp'); hold(0.5)
mark('S2', 'hl', '一连串时刻的高低记成数字', 0.875); mark('S3', 'hl', '推算出原来发的是0还是1', 0.875); mark('S4', 'hl', '两种“数字”', 0.5)
mark('S5', 'hl', '描述的是收到', 0.5); mark('S6', 'hl', '才是原本的数据', 0.625); mark('S8', 'hl', '前后很多个比特的拖尾', 0.75); mark('S9', 'hl', '一起考虑进去', 0.5); hold(0.375)
string('samp-K5', edge('S9'), ctop('K5', 250)); go(PC('K5', 0, 0), 1.1)
t0 = now(); CUE['K5'] = dict(t0=t0, wave=t0 + 0.25, samples=[t0 + 0.75, t0 + 2.25], win=t0 + 3.0, bits=[t0 + 3.5, t0 + 5.5], end=t0 + 7.0)
clabel('K5', '采样得到的数字：描述波形', -390, -110, t0 + 2.25, align='left', size=36)
clabel('K5', '把前后几个比特一起算', 390, 120, t0 + 3.25, align='right', size=36, bg='red')
clabel('K5', '算出来的：原本的数据', -390, 450, t0 + 5.5, align='left', size=36)
sfx(t0 + 0.75, 'samples', n=12, dur=1.5); sfx(t0 + 3.0, 'click'); sfx(t0 + 3.5, 'count'); hold(7.0)
string('K5-where', cbot('K5', -250), edge('W1', 'r')); gostack('where', 2.0, 'sine', 0.12)
mark('W1', 'hl', '不是第三种检修站', 0.75); mark('W2', 'hl', '检修站里的一种工具', 0.75); mark('W3', 'hl', '藏在SerDes里', 0.5); mark('W4', 'hl', 'Retimer里', 0.5)
mark('W5', 'hl', '高速光模块里', 0.5); mark('W6', 'hl', '换乘光之前', 0.5); mark('W7', 'hl', '一颗这样的DSP芯片', 0.75); hold(0.375)
string('where-K6', edge('W7'), ctop('K6', 250)); go(PC('K6', 0, 0), 1.12)
t0 = now(); CUE['K6'] = dict(t0=t0, blocks=[t0 + 0.75, t0 + 1.25, t0 + 1.75], end=t0 + 4.5)
clabel('K6', 'DSP：检修站里的一种工具', -390, -380, t0 + 0.25, align='left', size=38)
for tt in CUE['K6']['blocks']: sfx(tt, 'stick', n=3)
hold(4.5)
# --- 代价 ---
string('K6-cost', cbot('K6', 250), edge('X0', 'l')); gostack('cost', 2.0, 'sine', 0.12)
mark('X0', 'hl', '代价越大', 0.5); mark('X1', 'hl', '采样、计算和重新打节拍', 0.75); mark('X2', 'hl', '多花电', 0.375); mark('X2', 'hl', '增加一点延', 0.5)
mark('X4', 'hl', '看路况来选', 0.5); mark('X5', 'hl', '能省则省', 0.375); mark('X6', 'hl', '更重的处理', 0.5); hold(0.375)
string('cost-K7', edge('X6'), ctop('K7', 250)); go(PC('K7', 0, 0), 1.12)
t0 = now(); CUE['K7'] = dict(t0=t0, rows=[t0 + 0.25, t0 + 1.5, t0 + 2.75], end=t0 + 5.5)
clabel('K7', '路况越差，处理越重：多花电、多一点延迟', 0, 420, t0 + 4.0, size=34, bg='red')
for tt in CUE['K7']['rows']: sfx(tt, 'thock')
sfx(t0 + 4.0, 'amp'); hold(5.5)
string('K7-trend', cbot('K7', -250), edge('Y1', 'r')); gostack('trend', 2.0, 'sine', 0.12)
mark('Y1', 'hl', '数量庞大', 0.5); mark('Y2', 'hl', '功耗会累积起来', 0.625); mark('Y3', 'hl', '把路修短', 0.5); mark('Y4', 'hl', '交给链路上已有的芯片', 0.75); mark('Y5', 'hl', '专门的检修芯片', 0.5); hold(0.375)
gostack('inv')
mark('V1', 'hl', '速度、路况和出错率', 0.75); mark('V2', 'hl', '每传一个比特花多少电', 0.75); mark('V3', 'hl', '延迟', 0.375); mark('V4', 'hl', '留意范围', 0.5)
mark('V5', 'hl', '只报核心电路的功耗', 0.75); mark('V6', 'hl', '整颗芯片', 0.375); mark('V8', 'hl', '把工作转给了主芯片', 0.75); mark('V9', 'hl', '要看整条链路', 0.625); hold(0.375)
string('inv-K8', edge('V9'), ctop('K8', 250)); go(PC('K8', 0, 0), 1.1)
t0 = now(); CUE['K8'] = dict(t0=t0, core=t0 + 0.25, chip=t0 + 1.25, link=t0 + 2.25, move=[t0 + 3.75, t0 + 4.75], end=t0 + 7.0)
clabel('K8', '少放一颗 DSP：工作转给了主芯片', -390, 500, t0 + 5.0, align='left', size=36, bg='red')
sfx(t0 + 0.25, 'stick', n=1); sfx(t0 + 1.25, 'stick', n=2); sfx(t0 + 2.25, 'stick', n=3); sfx(t0 + 3.75, 'slide'); sfx(t0 + 5.0, 'amp'); hold(7.0)
# --- 收尾 ---
allx = [c['at'][0] for c in CLIPS.values()] + [c['at'][0] for c in CARDS.values()]; ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
go([OVER['x'], OVER['y']], OVER['z'], 2.0, 'cubic', 0.16); hold(0.75, 0.03)
gostack('end', 2.0, 'cubic', 0.10, dy=-40)
mark('E2', 'hl', '先均衡', 0.375); mark('E2', 'hl', '更容易认', 0.375); mark('E3', 'hl', '必要时由Retimer认清数据', 0.75); mark('E4', 'hl', '找准节拍、重新发送', 0.625)
mark('E5', 'hl', '用数字算法完成这些处理的工具', 0.875); mark('E6', 'hl', '代价越大', 0.375); mark('E7', 'hl', '任何检修都有边界', 0.625)
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
label('白话光互连 · 04', rightof('E0'), now() + 0.5, size=24, align='left', bg='red', r=-0.02)
eb = STACKS['end']['bb']; label('下一篇：第三站 换乘', [SC('end')[0], eb[3] + 75], now() + 1.0, size=28, r=-0.01)
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
for st, ps in HL_PASSES.items():
    for (v0, c0, _), (v1, c1, _) in zip(ps, ps[1:]): assert c0 != c1, f'{st}：第 {v0} 轮和第 {v1} 轮荧光笔同色'
print('荧光笔分轮：', {st: [(v, ['黄', '粉', '青'][HLC.index(c)]) for v, c, _ in ps] for st, ps in HL_PASSES.items() if len(ps) > 1})
out = dict(dur=DUR, bpm=120, K=K, clips=CLIPS, cards=CARDS, prints=PRINTS, cardLabels=CARD_LABELS, cue=CUE, marks=MARKS, pmarks=PMARKS, labels=LABELS, strings=STRINGS, cam=CAM,
           stick={}, pops=[], over=OVER, travel=[], station=[[2, HUD_IN + 1.5]], hudIn=HUD_IN, lens=LENS, stacks=STACKS, sfx=sorted(SFX, key=lambda s: s['t']))
json.dump(out, open(os.path.join(ROOT, '代码工程/ep4/desk.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('desk.json', DUR, 's,', len(CLIPS), 'strips,', len(PRINTS), 'prints,', len(MARKS), 'marks,', len(CAM), 'cam keys,', len(SFX), 'sfx;', 'z:', {k: v['z'] for k, v in STACKS.items()})
