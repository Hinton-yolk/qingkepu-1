# 白话光互连 04 · 小红书版 u（由 tools/assemble04.py 拼出，别直接改这个文件）
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
# ---------- 04 上集的摆放（按出场顺序左右交替） ----------
def bare(cid): CARDS[cid]['bare'] = True
place_card('P0', 'eqapp', L, 1000, 1000, 0.0); bare('P0'); COLY[L] += 350
LAST[0] = 0
place_card('RT', 'route', R, 900, 700, 0.008)
place_stack('eq', ['A0', 'A1', 'A2'], R); place_card('K2', 'eq', R, 900, 1200, -0.008)
place_card('WH', 'whole', L, 900, 1000, 0.008)
place_stack('nm', ['B5', 'B6'], L)
place_stack('ret', ['C0', 'C1', 'C2'], R); place_card('K3', 'retimer', R, 900, 1100, 0.008)
place_card('HB', 'hub', L, 900, 760, -0.01)
place_stack('rname', ['R1', 'R2', 'R3'], L); place_card('K4', 'redriver', R, 900, 1000, -0.008)
place_card('P1', 'eqapp', L, 1000, 1000, 0.0); bare('P1')
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'E1', 'E2', 'E3', 'E4', 'E7'], 850)
place_card('HE', 'here', 850, 1000, 260, 0.0); bare('HE')
for _cid in [c for c in CLIPS if c not in STACK_OF]: del CLIPS[_cid]

# ---------- 时间表工具（旁白版：从 0 往后排） ----------
MARKS, PMARKS, LABELS, STRINGS, CAM, SFX = [], [], [], [], [], []
CARD_LABELS = {k: [] for k in CARDS}; CUE = {}
T = [0.0]
def now(): return T[0]
def adv(d): assert abs(d * 8 - round(d * 8)) < 1e-9, d; T[0] = round(T[0] + d, 4)
def cam(t, xy, z, e='sine'): CAM.append(dict(t=round(t, 4), x=xy[0], y=xy[1], z=z, e=e))
def hold(d, dz=0.02): last = CAM[-1]; adv(d); cam(now(), [last['x'], last['y']], round(last['z'] * (1 + dz), 4), 'lin')
def go(xy, z, d=1.0, e='sine', g=0.08): SFX.append(dict(t=now(), kind='whoosh', dur=d, g=g)); adv(d); cam(now(), xy, z, e)
def label(text, xy, at, size=30, align='center', r=0.0, bg=None, rate=24):
    LABELS.append(dict(text=text, x=xy[0], y=xy[1], at=round(at, 4), size=size, align=align, r=r, bg=bg, fg=None, rate=rate)); SFX.append(dict(t=round(at, 4), kind='label', text=text, rate=rate))
def clabel(cid, text, cx, cy, at, size=40, align='center', bg='cream', r=0.0, rate=24):
    CARD_LABELS[cid].append(dict(text=text, x=cx, y=cy, at=round(at, 4), size=size, align=align, bg=bg, r=r, rate=rate)); SFX.append(dict(t=round(at, 4), kind='label', text=text, rate=rate))
def string(key, a, b, d=0.5, sag=0.06):
    STRINGS.append(dict(key=key, a=a, b=b, t=[now(), round(now() + d, 4)], sag=sag, route=False)); SFX.append(dict(t=now(), kind='string', dur=d))
def sfx(t, kind, **kw): SFX.append(dict(t=round(t, 4), kind=kind, **kw))
def edge(cid, side='r'):
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']; return P(cid, (x1 + 2) if side == 'r' else (x0 - 2), (y0 + y1) / 2)
def ctop(cid, dx=0): c = CARDS[cid]; return PC(cid, dx, -c['h'] / 2 + 30)
def cbot(cid, dx=0): c = CARDS[cid]; return PC(cid, dx, c['h'] / 2 - 30)
# 荧光笔颜色（系列规则，第三篇起）：同一摞文字每来一轮换一种颜色——荧光黄 → 珊瑚粉 → 薄荷青 → 荧光黄…；同一轮里连续划的几处同色
HLC = ['rgba(222,208,20,.88)', 'rgba(232,140,120,.72)', 'rgba(120,205,190,.70)']
VISIT = {}; PASS_COL = {}; HL_PASSES = {}
def arrive(name): VISIT[name] = VISIT.get(name, 0) + 1
def hl_color(cid):
    st = STACK_OF.get(cid); assert st and VISIT.get(st), f'短条 {cid} 所在的那摞还没有镜头来过'
    key = (st, VISIT[st])
    if key not in PASS_COL: n = len(HL_PASSES.setdefault(st, [])); PASS_COL[key] = HLC[n % len(HLC)]; HL_PASSES[st].append((VISIT[st], PASS_COL[key], now()))
    return PASS_COL[key]

# ---------- 旁白 ----------
SCRIPT = {s['id']: s for s in json.load(open(os.path.join(ROOT, '配音/script_x.json'), encoding='utf-8'))}
ALIGN = json.load(open(os.path.join(ROOT, '配音/align_x.json'), encoding='utf-8'))
PUNCT = set('，：；。？、 “”')
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
VOICE, FOCUS = [], []
LINE = {}
def speak(lid):
    t0 = g8(now()); VOICE.append(dict(id=lid, t=t0, file=f'配音/fish_x/{lid}.wav')); LINE[lid] = t0; return t0
def span(lid, phrase):
    text = SCRIPT[lid]['text']; i = text.find(phrase); assert i >= 0, f'旁白 {lid} 里没有「{phrase}」'
    return LINE[lid] + tmap(lid, i), LINE[lid] + tmap(lid, i + len(phrase))
def vmark(cid, kind, strip_phrase, lid, spoken, mind=0.375):
    a, b = span(lid, spoken); t0 = g8(a - 0.06); d = max(mind, g8(b - a))
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']
    run = [r for r in runs(c['page'], strip_phrase) if x0 <= r[0][1] and r[-1][2] <= x1 and y0 <= r[0][3] <= y1]; assert run, f'「{strip_phrase}」不在短条 {cid} 里'
    MARKS.append(dict(clip=cid, kind=kind, segs=boxes(run[0]), t=[t0, round(t0 + d, 4)], seed=len(MARKS) + 2, **({'col': hl_color(cid)} if kind == 'hl' else {})))
    SFX.append(dict(t=t0, kind='marker' if kind == 'hl' else 'pen', dur=d, soft=1))
def focus(stack, ids, a, b): FOCUS.append(dict(stack=stack, ids=ids, t=[round(a, 3), round(b, 3)]))
def lend(lid): return LINE[lid] + ALIGN[lid]['dur']
def after(lid, gap=0.25): adv(g8(lend(lid) + gap - now()))
def fwin(stack, ids, lid, pre=0.15, post=0.2): focus(stack, ids, LINE[lid] - pre, lend(lid) + post)
def fitstack(name, top=235, bot=1440):       # 一摞纸条整摞放在 HUD 下、字幕带上面
    b = STACKS[name]['bb']; hgt = b[3] - b[1]; z = round(min(SZ(name), (bot - top) / (hgt + 40)), 3); cy = (b[1] + b[3]) / 2
    return [round((b[0] + b[2]) / 2, 1), round(cy + (960 - (top + bot) / 2) / z, 1)], z
def gost(name, d=1.0, e='sine', g=0.08): xy, z = fitstack(name); go(xy, z, d, e, g); arrive(name)
def gocard(cid, z=1.12, d=1.0):                # 卡片框在 HUD 下、字幕带上面
    h = CARDS[cid]['h']; z = min(z, 1205 / h); dy = max(0, h / 2 - 470 / z)
    if 960 - (h / 2 + dy) * z < 215: dy = (960 - 215) / z - h / 2
    go(PC(cid, 0, round(dy)), round(z, 3), d)

# ======================= 旁白时间表（04 小红书 · 上集：芯片里，也装着均衡器？） =======================
def cardview(cid, z=1.12):
    h = CARDS[cid]['h']; z = min(z, 1205 / h); dy = max(0, h / 2 - 470 / z)
    if 960 - (h / 2 + dy) * z < 215: dy = (960 - 215) / z - h / 2
    return PC(cid, 0, round(dy)), round(z, 3)
LENS = dict(at=[0, 0], zin=[1e6, 1e6 + 1], open=[1e6, 1e6 + 1], core=1e6, samp=[1e6, 1e6 + 1], lbl=1e6, out=[1e6, 1e6 + 1], zmax=40)   # 上集没有放大镜头
# --- 第一帧：只有手机均衡器（用户 2026-11-07：均衡器和波形分开演示，别一上来就变好）---
cam(0, PC('P0', 0, 20), 1.0, 'lin')
clabel('P0', '芯片里，也装着均衡器？', 0, -560, 0, size=56, bg='red', r=-0.012, rate=400)
adv(0.125); speak('u1'); after('u1', 0.25)
speak('u2'); mv = g8(max(LINE['u2'] + 0.5, span('u2', '高音')[0] - 0.25)); sfx(mv, 'shave', dur=0.75)          # 推子各自上下：高音推上去、低音拉下来
after('u2', 0.125)
# 第二步：右边出现铜线出口的信号（糊的）→ 推子把高音再推上去，信号变清楚
speak('u3'); sh_ = g8(span('u3', '铜线')[0] - 0.25); pu = g8(max(sh_ + 1.5, span('u3', '同一件事')[0] - 0.25))
clabel('P0', '铜线出口：糊了', 230, 230, sh_ + 0.75, size=40, bg='red'); clabel('P0', '推子一推：变清楚', 230, 330, pu + 0.75, size=40, bg='#7fd6b4')
sfx(sh_ + 0.5, 'blur'); sfx(pu, 'shave', dur=0.75); sfx(pu + 0.9, 'dsp')
after('u3', 0.25); adv(max(0, g8(pu + 1.25 - now()))); CUE['P0'] = dict(t0=0, eqmove=mv, show=sh_, push=pu, end=now()); hold(0, 0.03)
# --- 快递路线图：亮「路上」；糊掉的信号到底怎么修？ ---
string('P0-RT', cbot('P0', 300), ctop('RT', -250)); gocard('RT', 1.15, 0.75)
t0 = g8(now()); speak('u4'); lit = g8(t0 + 0.25)
clabel('RT', '第二站：路上', 0, 250, lit, size=44, bg='red'); sfx(lit, 'thock'); HUD_IN = lit
after('u4', 0.25); CUE['RT'] = dict(t0=t0, lit=lit, end=now()); hold(0, 0)
# --- 纸条一拍：铜线削弱快速跳变最厉害 ---
string('RT-eq', cbot('RT', 250), edge('A1', 'l')); gost('eq', 1.0, 'sine', 0.12)
speak('u5'); fwin('eq', ['A1', 'A2'], 'u5'); vmark('A1', 'hl', '快速跳变削弱得更厉害', 'u5', '削弱快速跳变最厉害'); vmark('A2', 'hl', '棱角被削掉', 'u5', '棱角被削掉'); vmark('A2', 'hl', '拖出了尾巴', 'u5', '拖出了尾巴')
after('u5', 0.125); hold(0, 0)
# --- 演示：均衡（不补 / 发送端加强 / 接收端补回） ---
string('eq-K2', edge('A2'), ctop('K2', 250)); gocard('K2')
t0 = g8(now()); r0 = t0 + 0.25; speak('u6'); r1 = g8(max(r0 + 1.0, span('u6', '加强一点')[0] - 0.5)); r2 = g8(max(r1 + 1.0, span('u6', '补回来')[0] - 0.5))
clabel('K2', '不补：棱角被削掉，拖出尾巴', -390, -520, r0 + 0.5, align='left', bg='red', size=36); clabel('K2', '发送端：先把跳变加强一点', -390, -130, r1 + 0.75, align='left', size=36)
clabel('K2', '接收端：再补回来，接近方正', -390, 270, r2 + 0.75, align='left', size=36)
for tt in (r0, r1, r2): sfx(tt, 'thock')
after('u6', 0.25); adv(max(0, g8(r2 + 1.5 - now()))); CUE['K2'] = dict(t0=t0, rows=[r0, r1, r2], end=now()); hold(0, 0)
# --- 演示：整体放大 ✗ vs 只补被吞的 ✓ ---
string('K2-WH', cbot('K2', -250), ctop('WH', 250)); gocard('WH')
t0 = g8(now()); wa = t0 + 0.25; speak('u7'); wb = g8(max(wa + 1.0, span('u7', '而是')[0])); sfx(wa + 0.8, 'wrong'); sfx(wb + 0.8, 'dsp')
after('u7', 0.25); adv(max(0, g8(wb + 1.0 - now()))); CUE['WH'] = dict(t0=t0, a=wa, b=wb, end=now()); hold(0, 0)
# --- 纸条一拍：业内叫它均衡 ---
string('WH-nm', cbot('WH', 250), edge('B5', 'l')); gost('nm', 1.0, 'sine', 0.12)
speak('u8'); fwin('nm', ['B5'], 'u8'); vmark('B5', 'hl', '均衡', 'u8', '均衡', 0.5)
after('u8', 0.125); hold(0, 0)
# --- 纸条一拍：路太长，就在中间设检修站 ---
string('nm-ret', edge('B5'), edge('C1', 'l')); gost('ret', 1.0, 'sine', 0.12)
speak('u9'); fwin('ret', ['C1', 'C2'], 'u9'); vmark('C1', 'hl', '两头均衡不够用', 'u9', '两头补不过来'); vmark('C2', 'hl', '路中间设一个检修站', 'u9', '路中间设一个检修站')
after('u9', 0.125); hold(0, 0)
# --- 演示：检修站（认清、打节拍、重发） → 转运中心 → 回到检修站：后半程重新出发；认错的救不回来 ---
string('ret-K3', edge('C2'), ctop('K3', 250)); gocard('K3')
t3 = g8(now()); ok = t3 + 0.25; speak('u10'); clabel('K3', '检修站：认清、打准节拍、重新发送', -390, -470, ok + 1.25, align='left', size=36); sfx(ok + 1.25, 'dsp')
after('u10', 0.25); hold(0, 0)
string('K3-HB', cbot('K3', -250), ctop('HB', 250)); gocard('HB', 1.12, 0.75)
t0 = g8(now()); speak('u11'); after('u11', 0.25); CUE['HB'] = dict(t0=t0, end=now()); hold(0, 0)
gocard('K3', 1.12, 0.75); speak('u12'); after('u12', 0.125)
speak('u13'); bad = g8(span('u13', '已经认错')[0] - 0.25); clabel('K3', '先认错了：清楚地发出错的', -390, 470, bad + 1.25, align='left', bg='red', size=36); sfx(bad + 1.25, 'wrong')
after('u13', 0.25); adv(max(0, g8(bad + 2.5 - now()))); CUE['K3'] = dict(t0=t3, ok=ok, bad=bad, end=now()); hold(0, 0)
# --- 纸条一拍：Retimer = 重新打节拍 ---
string('K3-rname', cbot('K3', -250), edge('R1', 'r')); gost('rname', 1.0, 'sine', 0.12)
speak('u14'); fwin('rname', ['R1', 'R2'], 'u14'); vmark('R1', 'hl', 'Retimer', 'u14', 'Retimer'); vmark('R2', 'hl', '“重新打节拍”', 'u14', '重新打节拍')
after('u14', 0.125); hold(0, 0)
# --- 演示：Redriver vs Retimer ---
string('rname-K4', edge('R2'), ctop('K4', -250)); gocard('K4')
t0 = g8(now()); rd = t0 + 0.25; speak('u15'); rt = g8(max(rd + 1.75, span('u15', '只做均衡')[0])); me = g8(max(rt + 1.25, span('u15', '更省电')[0] - 0.25))
clabel('K4', 'Redriver：只做均衡', -390, -420, rd + 0.25, align='left', size=38); clabel('K4', 'Retimer：均衡＋认数据＋打节拍', -390, -20, rt + 0.25, align='left', size=38)
sfx(rd, 'thock'); sfx(rt, 'thock'); sfx(me, 'reach')
after('u15', 0.25); adv(max(0, g8(me + 1.25 - now()))); CUE['K4'] = dict(t0=t0, rd=rd, rt=rt, meters=me, end=now()); hold(0, 0)
# --- 回到开头那个均衡器（揭晓：配乐停半拍、换织体） ---
string('K4-P1', cbot('K4', -250), ctop('P1', 300)); go(PC('P1', 0, 20), 1.0, 1.0)
t0 = g8(now()); REV = t0; speak('u16'); ag = g8(t0 + 0.5); clabel('P1', '每秒上千亿个比特，也这样被调、被修', 0, -540, g8(span('u16', '每秒')[0]), size=38, bg='#7fd6b4'); sfx(ag, 'shave', dur=0.75)
after('u16', 0.25); CUE['P1'] = dict(t0=t0, again=ag, end=now()); hold(0, 0)
# --- 一句话 + 你在这里 → 下一篇 ---
ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
gost('end', 1.5, 'cubic', 0.10)
speak('u17'); fwin('end', ['E0', 'E1', 'E2', 'E3', 'E7'], 'u17')
vmark('E0', 'hl', '一句话带走', 'u17', '一句话带走'); vmark('E1', 'hl', '修信号分两步', 'u17', '修信号分两步'); vmark('E2', 'hl', '先均衡', 'u17', '先均衡'); vmark('E3', 'hl', 'Retimer认清数据', 'u17', 'Retimer 认清'); vmark('E7', 'hl', '任何检修都有边界', 'u17', '修不回来')
after('u17', 0.25); hold(0, 0)
he = CARDS['HE']; go([he['at'][0], he['at'][1] - 40], 1.15, 1.0); hq = g8(now() - 0.5); CUE['HE'] = dict(t0=hq, end=hq + 1)
speak('u18'); after('u18', 0.125)
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
label('下一篇：光模块一半的电，花在哪？', [he['at'][0], round(he['at'][1] + he['h'] / 2 + 60, 1)], LINE['u18'], size=34, r=-0.01)
label('白话光互连 · 04 上', rightof('E0'), LINE['u17'] + 0.5, size=24, align='left', bg='red', r=-0.02)
hold(2.25, 0.02)

# ---------- 字幕 ----------
def build_subs():
    out = []
    for v in VOICE:
        lid = v['id']; text = SCRIPT[lid]['text']; pos = 0
        for n, seg_ in enumerate(SCRIPT[lid]['sub']):
            core = seg_.rstrip('？'); i = text.find(core, pos); assert i >= 0, (lid, seg_)
            j = i + len(core); pos = j
            out.append(dict(lid=lid, n=n, text=seg_, t=[round(LINE[lid] + tmap(lid, i) - 0.08, 3), round(LINE[lid] + tmap(lid, j) + 0.15, 3)]))
    for i in range(len(out) - 1):
        if out[i + 1]['t'][0] - out[i]['t'][1] < 0.45: out[i]['t'][1] = out[i + 1]['t'][0]
    return out
SUBS = build_subs()
import difflib
CLEAN = lambda x: ''.join(ch for ch in x if ch not in '，。；：、？！“”‘’（）() ·')
def cam_mid(t):
    for i in range(1, len(CAM)):
        if t <= CAM[i]['t']:
            a_, b_ = CAM[i - 1], CAM[i]; p_ = (t - a_['t']) / max(1e-6, b_['t'] - a_['t']); return a_['x'] + (b_['x'] - a_['x']) * p_, a_['y'] + (b_['y'] - a_['y']) * p_
    return CAM[-1]['x'], CAM[-1]['y']
LENS_TXT = '收到的波形一连串时刻的高低记成数字'
def on_screen(t):
    if LENS['open'][0] <= t <= LENS['out'][0]: return 'lens', None
    x, y = cam_mid(t)
    for cid, cd in CARDS.items():
        if abs(x - cd['at'][0]) < cd['w'] / 2 and abs(y - cd['at'][1]) < cd['h'] / 2: return 'card', cid
    best = min(STACKS.items(), key=lambda kv: math.hypot(x - (kv[1]['bb'][0] + kv[1]['bb'][2]) / 2, y - (kv[1]['bb'][1] + kv[1]['bb'][3]) / 2))
    return 'stack', best[0]
FORCE = {('u1', 0): (False, '第一帧：大字问题已经贴在实物上')}
for x_ in SUBS:
    kind, name = on_screen((x_['t'][0] + x_['t'][1]) / 2)
    if kind == 'card': x_['show'] = True; x_['why'] = f'卡片 {name}'
    else:
        sub = CLEAN(x_['text']); ref = LENS_TXT if kind == 'lens' else CLEAN(''.join(CLIPS[i]['text'] for i in STACKS[name]['ids']))
        same = sum(b.size for b in difflib.SequenceMatcher(None, sub, ref, autojunk=False).get_matching_blocks() if b.size >= 2)
        x_['overlap'] = round(same / max(1, len(sub)), 2); x_['show'] = x_['overlap'] < 0.6; x_['why'] = f"{name or kind} 重合 {x_['overlap']}"
    if (x_['lid'], x_['n']) in FORCE: x_['show'], x_['why'] = FORCE[(x_['lid'], x_['n'])]
runs_ = []
for i, x_ in enumerate(SUBS):
    if not x_['show']: continue
    if runs_ and SUBS[i - 1]['show'] and x_['t'][0] - SUBS[i - 1]['t'][1] < 0.45: runs_[-1][1] = x_['t'][1]; runs_[-1][2].append(x_)
    else: runs_.append([x_['t'][0], x_['t'][1], [x_]])
for r0_, r1_, xs in runs_:
    for x_ in xs: x_['run'] = [round(r0_, 3), round(r1_, 3)]
DUR = now()

# ---------- 检查 ----------
def ongrid(t): return abs(t * 8 - round(t * 8)) < 1e-6
bad_ = [(k, v) for k, v in [('cam', c['t']) for c in CAM] + [('mark', m['t'][0]) for m in MARKS] + [('label', l['at']) for l in LABELS] if not ongrid(v)]
assert not bad_, bad_
assert all(CAM[i]['t'] < CAM[i + 1]['t'] for i in range(len(CAM) - 1)), [(CAM[i]['t'], CAM[i + 1]['t']) for i in range(len(CAM) - 1) if CAM[i]['t'] >= CAM[i + 1]['t']]
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
for st, ps in HL_PASSES.items():
    for (v0, c0, _), (v1, c1, _) in zip(ps, ps[1:]): assert c0 != c1, f'{st}：第 {v0} 轮和第 {v1} 轮荧光笔同色'
for cid, cu in CUE.items(): assert 't0' in cu and 'end' in cu, cid
print('荧光笔分轮：', {st: [(v, ['黄', '粉', '青'][HLC.index(c)]) for v, c, _ in ps] for st, ps in HL_PASSES.items() if len(ps) > 1})
out = dict(dur=DUR, bpm=120, K=K, clips=CLIPS, cards=CARDS, prints=PRINTS, cardLabels=CARD_LABELS, cue=CUE, marks=MARKS, pmarks=PMARKS, labels=LABELS, strings=STRINGS, cam=CAM,
           stick={}, pops=[], over=OVER, travel=[], station=[[2, HUD_IN + 1.5]], stn=['打包出发', '路上', '中转', '干线', '签收'], rev=REV, hudIn=HUD_IN, lens=LENS, stacks=STACKS, focus=FOCUS, voice=VOICE, subs=SUBS, sfx=sorted(SFX, key=lambda s: s['t']))
json.dump(out, open(os.path.join(ROOT, '代码工程/ep4/desk_u.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('desk_voice.json', DUR, 's,', len(MARKS), 'marks,', len(CAM), 'cam keys,', len(VOICE), 'voice lines,', len(FOCUS), 'focus windows;', sum(x['show'] for x in SUBS), '/', len(SUBS), 'subs shown')

