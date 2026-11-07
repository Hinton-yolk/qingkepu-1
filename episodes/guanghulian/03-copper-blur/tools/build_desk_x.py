# 白话光互连 03 · 小红书改版（2026-11-07，开头 A；由 build_desk_voice.py 改来）—— 桌面布局沿用正片（tools/build_desk.py），时间表跟着旁白走
# 运行：python3 tools/build_desk_voice.py → 代码工程/ep3/desk_x.json（画面和配乐读同一份）
# 规则（系列规则.md「旁白」）：说到哪个词，荧光笔就在那一刻划到；一摞纸条只亮正在讲的那几条；镜头移动 1 s；先演机制、再报名字；
#   字幕只在屏上没有这句话的地方出；同一摞纸条每来一轮，荧光笔换一种颜色（黄 → 粉 → 青）。
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
    # 上下也只留这一行：第三篇的 PDF 行距较紧，裁边会带进上一行的底、下一行的顶，盖成白纸
    tc, bc = round((base - 0.95 * size - y0) * DPI), round((base + 0.25 * size - y0) * DPI)
    dr.rectangle([0, 0, im.width, max(0, tc)], fill='white'); dr.rectangle([0, min(im.height, bc), im.width, im.height], fill='white')
    src = f'assets/strips/{cid}.png'; im.save(os.path.join(ROOT, '代码工程', src), optimize=True)
    k = K * (kscale if kscale else (0.85 if size > 12 else 1.0))
    CLIPS[cid] = dict(src=src, page=page, crop=[round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)], at=[0, 0], r=0.0, seed=sum(map(ord, cid)) % 97 + 5, text=text, k=k)
    return cid

# ---------- 原文短条 ----------
S = [('T1', 1, '一语道破·白话光互连03｜'), ('T2', 1, '电的路：信号为什么越跑越模糊？'),
 ('I1', 1, '上一篇，数据在第一站被排成一列，'), ('I2', 1, '变成高速电信号出发了。'), ('I3', 1, '这一篇跟着它走上第二站：电的路，'), ('I4', 1, '也就是电路板上的走线和铜缆。'),
 ('M1', 1, '电信号在铜线上跑，'), ('M2', 1, '就像在一条长走廊里喊话：'), ('M3', 1, '声音会变小，'), ('M4', 1, '前一个字的余音还没散，后一个字'), ('M5', 1, '又到了。'), ('M6', 1, '说得越快、走廊越长，'), ('M7', 1, '对面就越听不清。'),
 ('W0', 1, '信号为什么会模糊：变弱了，也拖尾了'), ('W1', 1, '还是先以高、低两种电平代表1和0。'), ('W2', 1, '信号在高低之间切换得干净利落，'), ('W3', 1, '像一个个'), ('W4', 1, '方方正正的台阶。'),
 ('A1', 1, '第一，变弱。'), ('A2', 1, '铜线本身有损耗，'), ('A3', 1, '信号跑得越远，力气就越小，'), ('A4', 1, '高电平和低电平之间的差距被压缩，'), ('A5', 1, '越来越难分清。'),
 ('B1', 1, '第二，拖尾。'), ('B2', 1, '铜线削弱快速跳变的力度，'), ('B3', 1, '比削弱缓慢变化更厉害。'), ('B4', 1, '于是方正台阶的棱角被削掉，'), ('B5', 1, '跳变变得迟缓，'),
 ('B6', 1, '每一个比特都拖出一条尾巴，'), ('B7', 1, '压到后面的比特身上。'), ('B8', 1, '业内把这种前后比特互相干扰的'), ('B9', 1, '现象叫码间干扰。'),
 ('S1', 1, '两件事叠加，'), ('S2', 1, '而是一片起伏的波浪，'), ('S3', 1, '很难判断某一刻到底是'), ('S4', 1, '0还是1。'),
 ('F1', 1, '越远，好理解：'), ('F2', 1, '损耗是一路累积的，'), ('F3', 1, '越快，要多想一步。'), ('F4', 1, '意味着每个比特占的时间减半，台阶'), ('F5', 1, '变得更窄。'),
 ('F6', 1, '可尾巴并不会跟着变短，'), ('F7', 1, '会压到更多后面的比特上。'), ('F8', 1, '尾巴本身也更重。'),
 ('R1', 1, '每条通道跑得越快，'), ('R2', 1, '铜线能可靠覆盖的距离就越短。'), ('R3', 1, '越来越多的连接要换乘光的根本原因。'),
 ('X0', 1, '怎么办：三种思路'), ('X1', 1, '一是把路修短。'), ('X2', 1, '让芯片之间离得更近，'), ('X3', 1, '二是把路修好。'), ('X4', 1, '用损耗更低的电路板材料、'), ('X4b', 1, '更好的铜缆，'),
 ('X5', 2, '三是在路上修信号。'), ('X6', 2, '就在中途设检修站，'), ('X7', 2, '把模糊的信号重新认出来、整理干净，'), ('X8', 2, '不过检修站也有能力范围，'), ('X9', 2, '信号模糊到一'), ('X10', 2, '定程度，就修不回来了。'),
 ('Y1', 2, '电的路并没有被淘汰。'), ('Y2', 2, '铜线便宜、可靠，也不需要电光转换，'), ('Y3', 2, '在机柜内这样的短'), ('Y4', 2, '距离里依然大量使用。'), ('Y5', 2, '光要接手的，是铜线力不从心的那一段。'),
 ('V1', 2, '最常用的指标是损耗，'), ('V2', 2, '单位是分贝（dB），'), ('V3', 2, '数字越大，信号衰减得越'), ('V4', 2, '严重。'), ('V5', 2, '不过一个损耗数字代表不了全部路况，'), ('V6', 2, '而且要说明是在什么频率下测得的，'),
 ('Q1', 2, '所以听到我们的芯片'), ('Q1b', 2, '能跑200G”时，'), ('Q2', 2, '还要追问：这是每条通道的速度吗？'), ('Q3', 2, '在多大损耗、什么条件'), ('Q4', 2, '下跑通？出错率多少？'), ('Q5', 2, '每个比特花多少电？'), ('Q6', 2, '速度只是结果，'),
 ('E0', 2, '一句话带走'), ('E1', 2, '电信号在铜线上会变弱、拖尾，'), ('E2', 2, '跑得越快、越远就越难认清；'), ('E3', 2, '应对的办法是把路修短、把路修好，'), ('E4', 2, '或者在路上修信号。')]

DROP = {'T1', 'T2', 'I1', 'I2', 'I3', 'I4', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'W0'}
S = [x for x in S if x[0] not in DROP]
for cid, p, t in S: strip(cid, p, t, kscale=1.3 if cid in ('T1', 'T2') else None)
strip('E9', 2, '本文仅做科普与行业分析，不构成投资建议。', kscale=0.62)
# 用户 2026-11-03：「200G」是比较老的数字，画面上改成「200G/400G/800G…」（…表示这一类、没列举完）。
# 在原文这条剪报的「200G」后面接上「/400G/800G…」，字体、字号、基线和原文的数字一致（PDF 里数字是 Carlito）。
def splice(cid, after_x1, insert):
    from PIL import ImageFont
    c = CLIPS[cid]; path = os.path.join(ROOT, '代码工程', c['src']); im = Image.open(path).convert('RGB')
    run = runs(c['page'], c['text'])[0]; base = run[0][3]
    font = ImageFont.truetype('/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf', round(11 * DPI))
    w = font.getlength(insert); xcut = round((after_x1 - c['crop'][0]) * DPI); bpx = round((base - c['crop'][1]) * DPI)
    ink = min(im.getpixel((x, y)) for x in range(0, im.width, 3) for y in range(0, im.height, 3))
    out = Image.new('RGB', (im.width + round(w), im.height), 'white'); out.paste(im.crop((0, 0, xcut, im.height)), (0, 0)); out.paste(im.crop((xcut, 0, im.width, im.height)), (xcut + round(w), 0))
    ImageDraw.Draw(out).text((xcut, bpx), insert, font=font, fill=ink, anchor='ls'); out.save(path, optimize=True)
    c['crop'][2] = round(c['crop'][2] + round(w) / DPI, 2); c['text'] = c['text'].replace('200G', '200G' + insert)
    return round(w) / DPI
G_X1 = [ch for ch in runs(2, '能跑200G')[0] if ch[0] == 'G'][0][2]
INS_W = splice('Q1b', G_X1, '/400G/800G…')

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

# ---------- 小红书改版的摆放：按出场顺序左右两列交替 ----------
def bare(cid): CARDS[cid]['bare'] = True
place_card('C0', 'cables', L, 1000, 1180, 0.0); bare('C0'); COLY[L] += 350        # 第一帧下面别露出下一张卡片
LAST[0] = 0
place_card('RT', 'route', R, 900, 700, 0.008)
place_card('H0', 'blur', L, 900, 760, -0.008)
place_stack('ideal', ['W1', 'W2', 'W3', 'W4'], R); place_stack('weak', ['A1', 'A2', 'A3', 'A4', 'A5'], R)
place_card('K1', 'corridor', L, 900, 720, -0.008); place_card('K3', 'weaken', L, 900, 820, 0.008)
place_stack('tail', ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9'], R); place_card('K4', 'tail', R, 900, 1100, 0.008)
place_stack('sum', ['S1', 'S2', 'S3', 'S4'], L); place_card('G1', 'glitch', L, 900, 980, -0.01)
place_stack('far', ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8'], R); place_card('K6', 'faster', R, 900, 960, 0.01)
place_stack('reach', ['R1', 'R2', 'R3'], L); place_card('C1', 'cables', L, 1000, 1180, 0.0); bare('C1'); place_card('K7', 'reach', L, 900, 600, -0.01)
place_stack('fix', ['X0', 'X1', 'X2', 'X3', 'X4', 'X4b'], R); place_card('K8', 'fixes', R, 900, 1000, 0.008)
place_stack('fix3', ['X5', 'X6', 'X7', 'X8', 'X9', 'X10'], L); place_card('C2', 'cables', L, 1000, 1180, 0.0); bare('C2'); place_card('K9', 'repair', L, 900, 900, -0.008)
place_stack('copper', ['Y1', 'Y2', 'Y3', 'Y4', 'Y5'], R); place_card('K10', 'split', R, 900, 760, 0.01)
place_stack('inv', ['V1', 'V2', 'V3', 'V4', 'V5', 'V6'], L); place_card('RD', 'road', L, 900, 860, -0.01)
place_stack('ask', ['Q1', 'Q1b', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6'], R); place_card('K11', 'claim', R, 900, 900, 0.008)
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'E1', 'E2', 'E3', 'E4', 'E9'], 850)
place_card('HE', 'here', 850, 1000, 260, 0.0); bare('HE')

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

# ======================= 旁白时间表（小红书改版，48 句） =======================
def cardview(cid, z=1.12):
    h = CARDS[cid]['h']; z = min(z, 1205 / h); dy = max(0, h / 2 - 470 / z)
    if 960 - (h / 2 + dy) * z < 215: dy = (960 - 215) / z - h / 2
    return PC(cid, 0, round(dy)), round(z, 3)
# --- 钩子：第一帧就是桌上的两根雷电线 + 贴在线上的大字问题 ---
def gocab(cid, d=1.0): go(PC(cid, 0, 40), 1.1, d)       # 雷电线：镜头对准线的中间，放大一点，下面不留空
cam(0, PC('C0', 0, 40), 1.1, 'lin')
clabel('C0', '长一点，速度砍半？', 0, -470, 0, size=60, bg='red', r=-0.012, rate=400)   # 第一帧就是完整的大字问题，不打字
adv(0.125); speak('X1'); after('X1', 0.25)
speak('X2'); a_ = g8(span('X2', '0.8 米')[0]); b_ = g8(max(a_ + 0.75, span('X2', '2 米')[0]))
clabel('C0', '0.8 米 · 40G', 0, -350, a_, size=46); clabel('C0', '2 米 · 20G', 0, 420, b_, size=46, bg='red')
after('X2', 0.125)
speak('X3'); ch_ = g8(span('X3', '带芯片')[0]); fb_ = g8(max(ch_ + 0.75, span('X3', '光纤线')[0]))
clabel('C0', '带芯片的线', 290, 30, ch_, size=40); clabel('C0', '光纤线', -290, 30, fb_, size=40, bg='#3fb5a5')
sfx(ch_, 'dsp'); sfx(fb_, 'laser')
after('X3', 0.125); CUE['C0'] = dict(t0=0, chip=ch_, fiber=fb_, end=now()); hold(0, 0.05)
# --- 快递路线图：亮第二站「路上」 ---
string('C0-RT', cbot('C0', 300), ctop('RT', -250)); gocard('RT', 1.15, 0.75)
t0 = g8(now()); speak('X4'); lit = g8(max(t0 + 0.5, span('X4', '也卡在')[0] - 0.25))
clabel('RT', '第二站：路上', 0, 250, lit, size=44, bg='red'); sfx(lit, 'thock'); HUD_IN = lit
after('X4', 0.125); CUE['RT'] = dict(t0=t0, lit=lit, end=now()); hold(0, 0)
# --- 电信号在铜线上遭遇了什么：清楚的台阶跑过铜线变糊（第一个机制演示） ---
string('RT-H0', cbot('RT', 250), ctop('H0', 250)); gocard('H0', 1.12, 0.5)
e0 = g8(now()); speak('X5'); lA = g8(e0 + 1.0); lB = g8(max(lA + 1.0, span('X5', '遭遇了什么')[0]))
clabel('H0', '出发时：清楚', -330, 210, lA, align='left'); clabel('H0', '跑过铜线：糊了', 380, 210, lB, bg='red', align='right')
sfx(e0, 'thock'); sfx(lB, 'blur')
after('X5', 0.375); adv(max(0, g8(lB + 1.0 - now()))); CUE['H0'] = dict(t0=e0, e0=e0, end=now()); hold(0, 0)
# --- 出发时：方方正正的台阶 ---
string('H0-ideal', cbot('H0', 250), edge('W1', 'l')); gost('ideal', 1.0, 'sine', 0.12)
speak('X6'); fwin('ideal', ['W1', 'W2', 'W3', 'W4'], 'X6')
vmark('W1', 'hl', '高、低两种电平', 'X6', '高电平是 1'); vmark('W1', 'hl', '1和0', 'X6', '低电平是 0'); vmark('W4', 'hl', '方方正正的台阶', 'X6', '方方正正的台阶')
after('X6')
speak('X7'); fwin('ideal', [], 'X7'); after('X7', 0.375); hold(0, 0)
# --- 第一，变弱 → 楼道里喊人 → 高低差距被压缩 ---
gost('weak')
speak('X8'); fwin('weak', ['A1', 'A2', 'A3'], 'X8'); vmark('A1', 'hl', '变弱', 'X8', '变弱'); vmark('A2', 'hl', '有损耗', 'X8', '有损耗'); vmark('A3', 'hl', '力气就越小', 'X8', '力气越小')
after('X8'); hold(0, 0)
string('weak-K1', edge('A3'), ctop('K1', 250)); gocard('K1')
t0 = g8(now()); W_ = [t0 + 0.25 + 0.5 * i for i in range(6)]
speak('X9'); far_ = g8(max(t0 + 1.0, span('X9', '离得越远')[0]))
clabel('K1', '楼道里喊人：越远，声音越小', -390, -260, far_, align='left')
for tt in W_: sfx(tt, 'shout')
after('X9', 0.25); adv(max(0, g8(W_[-1] + 1.0 - now()))); CUE['K1'] = dict(t0=t0, words=W_, fast=t0 + 3.5, end=now()); hold(0, 0)
string('K1-K3', cbot('K1', -250), ctop('K3', -250)); gocard('K3')
t0 = g8(now()); wave = t0 + 0.25; speak('X10'); env = g8(max(wave + 1.25, span('X10', '差距被压缩')[0]))
clabel('K3', '出发：方方正正的台阶', -390, -330, wave, align='left'); clabel('K3', '跑远了：高低差距被压缩', 390, 280, env + 0.5, align='right', bg='red')
sfx(wave, 'thock'); sfx(env, 'envE')
after('X10', 0.375); adv(max(0, g8(env + 1.5 - now()))); CUE['K3'] = dict(t0=t0, wave=wave, env=env, end=now()); hold(0, 0)
# --- 第二，拖尾（第一轮）→ 钻进「棱角」→ 回来（第二轮）---
string('K3-tail', cbot('K3', 250), edge('B1', 'l')); gost('tail', 1.0, 'sine', 0.12)
speak('X11'); fwin('tail', ['B1', 'B2', 'B3'], 'X11'); vmark('B1', 'hl', '拖尾', 'X11', '拖尾'); vmark('B2', 'hl', '削弱快速跳变的力度', 'X11', '削弱快速跳变'); vmark('B3', 'hl', '更厉害', 'X11', '更厉害')
after('X11')
speak('X12'); fwin('tail', ['B4'], 'X12'); vmark('B4', 'hl', '棱角被削掉', 'X12', '棱角，被削掉')
after('X12', 0.125); hold(0, 0)
ZC = (lambda r: P('B4', (r[0][1] + r[-1][2]) / 2, r[0][3] - 4.5))(runs(1, '棱角')[0])
a = g8(now()); cam(a + 0.5, ZC, 2.7, 'sine'); cam(a + 1.5, ZC, 40, 'cubic'); T[0] = a + 0.5
speak('X13'); T[0] = a + 1.5
sharp = a + 1.5; s0 = g8(max(sharp + 0.5, span('X13', '棱角一点点被磨圆')[0])); shave = [s0, s0 + 1.5]
lbl = s0 + 0.75; lbl2 = shave[1] + 0.25; o0 = g8(max(lend('X13') + 0.5, lbl2 + 1.0))
LENS = dict(at=ZC, zin=[a + 0.5, a + 1.5], open=[a + 0.75, a + 1.25], sharp=sharp, shave=shave, lbl=lbl, lbl2=lbl2, out=[o0, o0 + 1.0], zmax=40)
sfx(a + 0.5, 'riser', dur=1.0); sfx(a + 1.25, 'boom'); sfx(s0, 'shave', dur=1.5); sfx(o0, 'pullout', dur=1.0)
for txt_, at_ in [('方方正正的台阶', sharp), ('棱角被削掉', lbl), ('跳变变得迟缓', lbl2)]: SFX.append(dict(t=at_, kind='label', text=txt_, rate=14))
xy_, z_ = fitstack('tail'); cam(o0, ZC, 40, 'lin'); cam(o0 + 1.0, xy_, z_, 'cubic'); T[0] = o0 + 1.0; arrive('tail'); hold(0.25, 0.01)
speak('X14'); fwin('tail', ['B5', 'B6', 'B7'], 'X14')
vmark('B5', 'hl', '跳变变得迟缓', 'X14', '跳变变得迟缓'); vmark('B6', 'hl', '拖出一条尾巴', 'X14', '拖出一条尾巴'); vmark('B7', 'hl', '压到后面的比特身上', 'X14', '压到后面的比特身上')
after('X14'); hold(0, 0)
# 卡片：一个比特拖出尾巴 → 一串比特的尾巴叠在一起（车库回音；这时还不报名字）
string('tail-K4', edge('B7'), ctop('K4', 250)); gocard('K4', 1.1)
t0 = g8(now()); single = t0 + 0.25; speak('X15'); after('X15', 0.25); speak('X16')
m0 = g8(max(t0 + 1.0, span('X16', '回音还没散')[0])); seq = g8(max(m0 + 1.25, span('X16', '下一个字已经出口')[0])); sm = g8(max(seq + 1.0, span('X16', '糊成一片')[0])); ask = sm + 1.0
clabel('K4', '一个比特：拖出一条尾巴', -390, -440, m0 + 0.75, align='left'); clabel('K4', '尾巴压到后面的比特上', -390, 30, seq + 0.5, align='left', bg='red')
clabel('K4', '像车库回音：糊成一片', 390, 470, sm + 0.25, align='right', bg='red')
sfx(single, 'thock'); sfx(m0, 'shave', dur=0.75); sfx(seq, 'pairs'); sfx(sm, 'blur'); sfx(ask, 'wrong')
after('X16', 0.25); adv(max(0, g8(ask + 1.0 - now()))); CUE['K4'] = dict(t0=t0, single=single, morph=[m0, m0 + 0.75], seq=seq, sum=sm, ask=ask, end=now()); hold(0, 0)
string('K4-tail', cbot('K4', -250), edge('B8', 'l')); gost('tail', 1.0)
speak('X17'); fwin('tail', ['B8', 'B9'], 'X17'); vmark('B8', 'hl', '前后比特互相干扰', 'X17', '前后比特互相干扰'); vmark('B9', 'hl', '码间干扰', 'X17', '码间干扰', 0.5)
after('X17', 0.375); hold(0, 0)
# --- 两件事叠在一起 → 认错一个：照片花了、消息乱码 ---
string('tail-sum', edge('B9'), edge('S1', 'r')); gost('sum', 1.0, 'sine', 0.12)
speak('X18'); fwin('sum', ['S1', 'S2'], 'X18'); vmark('S1', 'hl', '两件事叠加', 'X18', '两件事叠在一起'); vmark('S2', 'hl', '一片起伏的波浪', 'X18', '一片起伏的波浪')
after('X18')
speak('X19'); fwin('sum', ['S3', 'S4'], 'X19'); vmark('S4', 'hl', '0还是1', 'X19', '0 还是 1'); vmark('S3', 'hl', '很难判断', 'X19', '很难判断')
after('X19'); hold(0, 0)
string('sum-G1', edge('S4'), ctop('G1', 250)); gocard('G1')
t0 = g8(now()); speak('X20'); ph = g8(max(t0 + 0.25, span('X20', '照片花了一块')[0])); ms = g8(max(ph + 0.75, span('X20', '乱码')[0] - 0.25))
clabel('G1', '照片花了一块', -210, 240, ph + 0.25, bg='red'); clabel('G1', '消息冒出乱码', 220, 0, ms + 0.25, bg='red')
sfx(ph, 'wrong'); sfx(ms, 'wrong')
after('X20', 0.375); adv(max(0, g8(ms + 1.25 - now()))); CUE['G1'] = dict(t0=t0, photo=ph, msg=ms, end=now()); hold(0, 0)
# --- 为什么越快、越远就越糟 ---
string('G1-far', cbot('G1', 250), edge('F1', 'l')); gost('far', 1.0, 'sine', 0.12)
speak('X21'); fwin('far', [], 'X21'); after('X21')
speak('X22'); fwin('far', ['F1', 'F2'], 'X22'); vmark('F1', 'hl', '越远', 'X22', '越远'); vmark('F2', 'hl', '一路累积', 'X22', '一路累积'); after('X22')
speak('X23'); fwin('far', ['F3', 'F4', 'F5'], 'X23'); vmark('F3', 'hl', '越快', 'X23', '越快'); vmark('F4', 'hl', '时间减半', 'X23', '时间减半'); vmark('F5', 'hl', '变得更窄', 'X23', '变窄')
after('X23'); hold(0, 0)
string('far-K6', edge('F5'), ctop('K6', 250)); gocard('K6')
t0 = g8(now()); rowA = t0 + 0.25; hitA = rowA + 0.75; adv(0.75); speak('X24'); rowB = g8(LINE['X24'] + 0.125); hitB = g8(max(rowB + 1.0, span('X24', '压到更多后面的比特上')[0]))
clabel('K6', '原来', -390, -400, rowA, align='left'); clabel('K6', '快一倍：台阶更窄，尾巴还那么长', -390, 0, rowB + 0.25, align='left', size=38)
clabel('K6', '压到更多比特上，尾巴也更重', 390, 400, hitB + 0.25, align='right', bg='red', size=38)
sfx(rowA, 'thock'); sfx(rowB, 'thock'); sfx(hitB, 'wrong')
after('X24'); speak('X25'); after('X25'); speak('X26'); after('X26', 0.375); CUE['K6'] = dict(t0=t0, rowA=rowA, rowB=rowB, hitA=hitA, hitB=hitB, end=now()); hold(0, 0)
# --- 越快，可靠距离越短 → 回到开头那根线 → 换乘光 ---
string('K6-reach', cbot('K6', 250), edge('R1', 'l')); gost('reach', 1.0, 'sine', 0.12)
speak('X27'); fwin('reach', ['R1', 'R2'], 'X27'); vmark('R1', 'hl', '跑得越快', 'X27', '跑得越快'); vmark('R2', 'hl', '距离就越短', 'X27', '距离就越短')
after('X27'); hold(0, 0)
string('reach-C1', edge('R2'), ctop('C1', 300)); gocab('C1')
t0 = g8(now()); speak('X28'); rg = g8(max(t0 + 0.25, span('X28', '长到 2 米')[0]))
clabel('C1', '0.8 米 · 40G', 0, -350, t0, size=46); clabel('C1', '2 米：只剩 20G', 0, 430, rg + 0.25, size=50, bg='red')
sfx(rg, 'thock')
after('X28', 0.25); CUE['C1'] = dict(t0=t0, ring=rg, end=now()); hold(0, 0)
string('C1-K7', cbot('C1', 300), ctop('K7', 250)); gocard('K7', 1.15)
t0 = g8(now()); slow, fast = t0, t0 + 1.0; speak('X29'); so = g8(max(fast + 0.75, span('X29', '换乘光')[0]))
clabel('K7', '慢：能可靠地跑很远', -400, -235, slow, align='left', size=38); clabel('K7', '快：没多远就糊了', -400, 5, fast, align='left', bg='red', size=38)
clabel('K7', '所以：换乘光', 400, 245, so, align='right', size=40)
sfx(slow, 'reach'); sfx(fast, 'reach2')
after('X29', 0.375); adv(max(0, g8(so + 1.0 - now()))); CUE['K7'] = dict(t0=t0, slow=slow, fast=fast, end=now()); hold(0, 0)
# --- 怎么办：修短、修好 ---
string('K7-fix', cbot('K7', -250), edge('X0', 'r')); gost('fix', 1.0, 'sine', 0.12)
speak('X30'); fwin('fix', ['X0'], 'X30'); vmark('X0', 'hl', '怎么办', 'X30', '怎么办'); vmark('X0', 'hl', '三种思路', 'X30', '大致三类')
after('X30'); hold(0, 0)
string('fix-K8', edge('X0'), ctop('K8', 250)); gocard('K8')
t0 = g8(now()); r0 = t0 + 0.25; speak('X31'); r1 = g8(max(r0 + 1.0, span('X31', '把路修短')[0])); after('X31'); speak('X32'); r2 = g8(max(r1 + 1.0, span('X32', '把路修好')[0]))
clabel('K8', '原来：路长，到了就糊', -390, -440, r0 + 0.25, align='left', bg='red', size=38); clabel('K8', '修短：芯片离得更近', -390, -110, r1 + 0.25, align='left', size=38)
clabel('K8', '修好：损耗更低的板材、铜缆', -390, 220, r2 + 0.25, align='left', size=38)
for tt in (r0, r1, r2): sfx(tt, 'thock')
after('X32', 0.375); CUE['K8'] = dict(t0=t0, rows=[r0, r1, r2], end=now()); hold(0, 0)
# --- 三，在路上修信号 → 带芯片的线 = 把检修站做进线里 → 检修站也有极限 ---
string('K8-fix3', cbot('K8', 250), edge('X5', 'l')); gost('fix3', 1.0, 'sine', 0.12)
speak('X33'); fwin('fix3', ['X5'], 'X33'); vmark('X5', 'hl', '在路上修信号', 'X33', '在路上修信号')
after('X33')
speak('X34'); fwin('fix3', ['X6', 'X7'], 'X34'); vmark('X6', 'hl', '中途设检修站', 'X34', '设一个检修站'); vmark('X7', 'hl', '重新认出来、整理干净', 'X34', '重新认出来、整理干净')
after('X34'); hold(0, 0)
string('fix3-C2', edge('X7'), ctop('C2', 300)); gocab('C2')
t0 = g8(now()); speak('X35'); cr = g8(max(t0 + 0.5, span('X35', '检修站')[0]))
clabel('C2', '线里的芯片：一个小检修站', 60, 470, cr + 0.25, size=44, bg='red'); sfx(t0 + 0.25, 'dsp')
after('X35', 0.25); CUE['C2'] = dict(t0=t0, chip=t0 + 0.25, chipRing=cr, end=now()); hold(0, 0)
string('C2-K9', cbot('C2', 300), ctop('K9', 250)); gocard('K9')
t0 = g8(now()); ok = t0 + 0.25; speak('X36'); bad = g8(max(ok + 2.0, span('X36', '信号糊到一定程度')[0]))
clabel('K9', '中途设检修站：认出来、整理干净', -390, -420, ok + 1.0, align='left', size=38); clabel('K9', '糊到一定程度：修不回来', -390, 400, bad + 1.25, align='left', bg='red', size=38)
sfx(ok + 1.0, 'dsp'); sfx(bad + 1.25, 'wrong')
after('X36', 0.375); adv(max(0, g8(bad + 2.5 - now()))); CUE['K9'] = dict(t0=t0, ok=ok, bad=bad, end=now()); hold(0, 0)
# --- 铜线会被淘汰吗？没有 ---
string('K9-copper', cbot('K9', -250), edge('Y1', 'r')); gost('copper', 1.0, 'sine', 0.12)
speak('X37'); fwin('copper', ['Y1'], 'X37'); vmark('Y1', 'hl', '并没有被淘汰', 'X37', '没有')
after('X37')
speak('X38'); fwin('copper', ['Y2', 'Y3', 'Y4'], 'X38')
vmark('Y2', 'hl', '便宜、可靠', 'X38', '便宜、可靠'); vmark('Y2', 'hl', '不需要电光转换', 'X38', '不用电光转换'); vmark('Y3', 'hl', '机柜内', 'X38', '机柜里'); vmark('Y4', 'hl', '依然大量使用', 'X38', '依然大量使用')
after('X38'); hold(0, 0)
string('copper-K10', edge('Y4'), ctop('K10', 250)); gocard('K10')
t0 = g8(now()); cp = t0 + 0.25; speak('X39'); lim = g8(max(cp + 1.5, span('X39', '几千根铜缆')[0])); after('X39'); speak('X40'); light = g8(max(lim + 0.5, span('X40', '光要接手')[0]))
clabel('K10', '柜内短距离：几千根铜缆', -390, -260, cp + 0.5, align='left', size=36); clabel('K10', '光：接手铜线力不从心的那一段', 390, 230, light + 0.25, align='right', size=36)
sfx(cp, 'thock'); sfx(lim, 'blur'); sfx(light, 'laser')
after('X40', 0.375); adv(max(0, g8(light + 1.5 - now()))); CUE['K10'] = dict(t0=t0, copper=cp, limit=lim, light=light, end=now()); hold(0, 0)
# --- 从投资角度：先问路况 ---
string('K10-inv', cbot('K10', 250), edge('V1', 'l')); gost('inv', 1.0, 'sine', 0.12)
speak('X41'); fwin('inv', [], 'X41'); after('X41')
speak('X42'); fwin('inv', ['V1', 'V2', 'V3', 'V4'], 'X42')
vmark('V1', 'hl', '损耗', 'X42', '损耗'); vmark('V2', 'hl', '分贝（dB）', 'X42', '分贝'); vmark('V3', 'hl', '数字越大', 'X42', '数字越大'); vmark('V3', 'hl', '信号衰减得越', 'X42', '信号衰减越'); vmark('V4', 'hl', '严重', 'X42', '严重', 0.25)
after('X42')
speak('X43'); fwin('inv', ['V5', 'V6'], 'X43'); vmark('V5', 'hl', '代表不了全部路况', 'X43', '代表不了全部路况'); vmark('V6', 'hl', '在什么频率下测得的', 'X43', '在什么频率下测的')
after('X43', 0.25); hold(0, 0)
string('inv-RD', edge('V6'), ctop('RD', 250)); gocard('RD')
t0 = g8(now()); speak('X44'); hw = g8(max(t0 + 0.25, span('X44', '在高速上')[0])); mt = g8(max(hw + 0.75, span('X44', '还是在山路上')[0]))
clabel('RD', '“能跑 200 公里每小时”', 0, -410, t0 + 0.25, size=40); clabel('RD', '在高速上？', 260, -100, hw, size=40); clabel('RD', '还是在山路上？', 220, 400, mt, size=40, bg='red')
sfx(hw, 'whoosh', dur=0.5, g=0.06); sfx(mt, 'thock')
after('X44', 0.375); adv(max(0, g8(mt + 1.5 - now()))); CUE['RD'] = dict(t0=t0, hw=hw, mt=mt, end=now()); hold(0, 0)
string('RD-ask', cbot('RD', 250), edge('Q1', 'l')); gost('ask', 1.0, 'sine', 0.12)
speak('X45'); fwin('ask', ['Q1', 'Q1b', 'Q2', 'Q3', 'Q4', 'Q5'], 'X45'); vmark('Q1', 'hl', '我们的芯片', 'X45', '我们的芯片'); vmark('Q1b', 'hl', '能跑200G', 'X45', '能跑 200G、400G、800G')
MARKS[-1]['segs'][-1][2] = round(MARKS[-1]['segs'][-1][2] + INS_W, 2)      # 荧光笔一直划到接上去的「/400G/800G…」
vmark('Q2', 'under', '每条通道的速度', 'X45', '每条通道的速度'); vmark('Q3', 'under', '多大损耗、什么条件', 'X45', '多大损耗、什么条件'); vmark('Q4', 'under', '出错率多少', 'X45', '出错率多少'); vmark('Q5', 'under', '每个比特花多少电', 'X45', '每个比特花多少电')
after('X45'); hold(0, 0)
string('ask-K11', edge('Q5'), ctop('K11', 250)); gocard('K11')
t0 = g8(now()); claim = t0 + 0.125; qs = [t0 + 0.5, t0 + 0.875, t0 + 1.25, t0 + 1.625]; adv(1.875); speak('X46'); res = g8(max(qs[-1] + 0.5, span('X46', '速度只是结果')[0]))
for tt in [claim] + qs: sfx(tt, 'stick', n=2)
sfx(res, 'click')
after('X46', 0.375); CUE['K11'] = dict(t0=t0, claim=claim, qs=qs, res=res, end=now()); hold(0, 0)
# --- 收尾：拉回全桌 → 一句话带走（下面一张小路线图：你在这里）→ 下一篇 ---
ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
go([OVER['x'], OVER['y']], OVER['z'], 1.5, 'cubic', 0.16); hold(0.5, 0.03)
eb = STACKS['end']['bb']; he = CARDS['HE']; top_, bot_ = eb[1], he['at'][1] + he['h'] / 2 + 140
zE = round(min(SZ('end'), (1440 - 235) / (bot_ - top_ + 40)), 3); go([SC('end')[0], round((top_ + bot_) / 2 + (960 - (235 + 1440) / 2) / zE, 1)], zE, 1.5, 'cubic', 0.10); arrive('end')
speak('X47'); fwin('end', ['E0', 'E1', 'E2', 'E3', 'E4'], 'X47')
vmark('E0', 'hl', '一句话带走', 'X47', '一句话带走'); vmark('E1', 'hl', '变弱、拖尾', 'X47', '变弱、拖尾'); vmark('E2', 'hl', '越快、越远就越难认清', 'X47', '越快、越远，就越难认清')
vmark('E3', 'hl', '把路修短、把路修好', 'X47', '把路修短、把路修好'); vmark('E4', 'hl', '在路上修信号', 'X47', '在路上修信号')
hq = g8(span('X47', '办法是')[0]); CUE['HE'] = dict(t0=hq, end=hq + 1)
after('X47', 0.375)
speak('X48'); after('X48', 0.125)
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
label('下一篇：路上的检修站', [SC('end')[0], round(he['at'][1] + he['h'] / 2 + 60, 1)], LINE['X48'], size=28, r=-0.01)
label('白话光互连 · 03', rightof('E0'), LINE['X48'] + 0.5, size=24, align='left', bg='red', r=-0.02)
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
LENS_TXT = '方方正正的台阶棱角被削掉跳变变得迟缓'
def on_screen(t):
    if LENS['open'][0] <= t <= LENS['out'][0]: return 'lens', None
    x, y = cam_mid(t)
    for cid, cd in CARDS.items():
        if abs(x - cd['at'][0]) < cd['w'] / 2 and abs(y - cd['at'][1]) < cd['h'] / 2: return 'card', cid
    best = min(STACKS.items(), key=lambda kv: math.hypot(x - (kv[1]['bb'][0] + kv[1]['bb'][2]) / 2, y - (kv[1]['bb'][1] + kv[1]['bb'][3]) / 2))
    return 'stack', best[0]
FORCE = {('X1', 0): (False, '第一帧：大字问题已经贴在线上')}
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
           stick={}, pops=[], over=OVER, travel=[], station=[[2, HUD_IN + 1.5]], stn=['打包出发', '路上', '中转', '干线', '签收'], hudIn=HUD_IN, lens=LENS, stacks=STACKS, focus=FOCUS, voice=VOICE, subs=SUBS, sfx=sorted(SFX, key=lambda s: s['t']))
json.dump(out, open(os.path.join(ROOT, '代码工程/ep3/desk_x.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('desk_voice.json', DUR, 's,', len(MARKS), 'marks,', len(CAM), 'cam keys,', len(VOICE), 'voice lines,', len(FOCUS), 'focus windows;', sum(x['show'] for x in SUBS), '/', len(SUBS), 'subs shown')

