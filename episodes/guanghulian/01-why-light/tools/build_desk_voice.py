# 白话光互连 01 · 旁白完整版 —— 桌面布局沿用正片（tools/build_desk.py），时间表改成跟着旁白走
# 运行：python3 tools/build_desk_voice.py → 代码工程/full/desk_voice.json（画面和配乐读同一份）
# 规则（系列规则.md「旁白」）：说到哪个词，荧光笔就在那一刻划到；一摞纸条只亮正在讲的那几条；镜头移动 1 s（换站 1.5 s）；
#   先演机制、再报名字；字幕只在屏上没有这句话的地方出（深色撕边条＋米白字，画面下部）；所有时间点落在 1/8 s 格上。
import json, math, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CH = {int(k): v for k, v in json.load(open(os.path.join(ROOT, '素材/chars2.json'), encoding='utf-8')).items()}
K, DPI = 2.5, 600 / 72
os.makedirs(os.path.join(ROOT, '代码工程/assets/strips'), exist_ok=True)
PAGES = {}
def page_img(p):
    if p not in PAGES: PAGES[p] = Image.open(os.path.join(ROOT, f'素材/hi-{p}.png')).convert('RGB')
    return PAGES[p]

# ---------- 原文找字 ----------
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

CLIPS, CARDS = {}, {}
def rot(x, y, r): return [x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)]
def P(cid, px, py):
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']; w, h = x1 - x0, y1 - y0; k = c.get('k', K)
    rx, ry = rot((px - x0) * k - w * k / 2, (py - y0) * k - h * k / 2, c['r']); return [round(c['at'][0] + rx, 1), round(c['at'][1] + ry, 1)]
def PC(cid, cx, cy):
    c = CARDS[cid]; rx, ry = rot(cx, cy, c['r']); return [round(c['at'][0] + rx, 1), round(c['at'][1] + ry, 1)]

# 一条剪报短条：原文同一行里的一段话
def strip(cid, page, text, occ=0):
    run = runs(page, text)[occ]; bx = boxes(run); assert len(bx) == 1, f'「{text}」跨行了'
    size = run[0][4]; base = run[0][3]
    x0, x1 = run[0][1] - 4.5, run[-1][2] + 4.5; y0, y1 = base - 0.93 * size - 4.0, base + 0.24 * size + 4.0
    im = page_img(page).crop((round(x0 * DPI), round(y0 * DPI), round(x1 * DPI), round(y1 * DPI))); src = f'assets/strips/{cid}.png'
    from PIL import ImageDraw                                   # 盖掉两头露出来的邻字（只留这句话本身）
    dr = ImageDraw.Draw(im); gl, gr = round((run[0][1] - x0) * DPI) - 2, round((run[-1][2] - x0) * DPI) + 2
    dr.rectangle([0, 0, max(0, gl), im.height], fill='white'); dr.rectangle([min(im.width, gr), 0, im.width, im.height], fill='white')
    im.save(os.path.join(ROOT, '代码工程', src), optimize=True)
    CLIPS[cid] = dict(src=src, page=page, crop=[round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)], at=[0, 0], r=0.0, seed=sum(map(ord, cid)) % 97 + 5, text=text, k=K * (0.85 if size > 12 else 1.0))
    return cid
# 一摞短条：左边对齐（带一点错落），从 top 往下排
STACKS = {}
def stack(name, ids, cx, top, gap=26):
    import random; rnd = random.Random(sum(map(ord, name)))
    y = top; xl = cx - 250; bb = [1e9, 1e9, -1e9, -1e9]
    for i, cid in enumerate(ids):
        c = CLIPS[cid]; w = (c['crop'][2] - c['crop'][0]) * c.get('k', K); h = (c['crop'][3] - c['crop'][1]) * c.get('k', K)
        c['at'] = [round(xl + rnd.uniform(-10, 14) + w / 2, 1), round(y + h / 2, 1)]; c['r'] = round(rnd.uniform(-0.016, 0.016), 4)
        bb = [min(bb[0], c['at'][0] - w / 2), min(bb[1], y), max(bb[2], c['at'][0] + w / 2), max(bb[3], y + h)]; y += h + gap
    wmax = max((CLIPS[c]['crop'][2] - CLIPS[c]['crop'][0]) * CLIPS[c].get('k', K) for c in ids)
    STACKS[name] = dict(ids=ids, bb=bb, z=round(min(2.05, 960 / (wmax + 25)), 3))
    return STACKS[name]
def SC(name, dy=0):           # 一摞的中心（镜头对准这里时整摞都在画面里）
    b = STACKS[name]['bb']; return [round((b[0] + b[2]) / 2, 1), round((b[1] + b[3]) / 2 + dy, 1)]
def SZ(name): return STACKS[name]['z']

# ---------- 桌面：短条 ----------
T = 'T'; CLIPS[T] = dict(src='assets/clipT.png', page=1, crop=[62, 86, 408, 114], at=[0, 0], r=-0.02, seed=11, text='标题', k=K)
strip('I1', 1, '要用成千上万颗 GPU 一起算。'); strip('I2', 1, '它们都要互相交换结果，'); strip('I3', 1, '所以 GPU 不仅要算得快，还要“说得快”。')
strip('I4', 1, '今天越来越多地要借助光来完成，'); strip('I5', 1, '这就是光互连。')
strip('A0', 1, '第一站 出发：把货物装上车'); strip('A1', 1, 'GPU 内部的数据是“一大排”并排放着的，'); strip('A2', 1, '可芯片对外的出口有限，')
strip('A3', 1, '是把这一大排数据排成一列，'); strip('A4', 1, '负责这件事的电路，业内叫 SerDes。')
strip('B0', 1, '第二站 电的路：跑得越快，货越难认'); strip('B1', 1, '速度越高、距离越远，'); strip('B2', 1, '到达时就越模糊，'); strip('B3', 1, '接收方可能分不清哪个是 0、哪'); strip('B4', 1, '个是 1。')
strip('D1', 2, '会在路上设一个“检修站”：'); strip('D2', 2, '把模糊的信号重新认出来、'); strip('D3', 2, '业内叫 DSP。检修要耗电，')
strip('R1', 2, '速度越高，'); strip('R2', 2, '电的路能可靠覆盖的距离就越短。')
strip('C0', 2, '第三站 换乘：把数据装到光上'); strip('C1s', 2, '“高铁”，重点不是光跑得更快，'); strip('C2s', 2, '而是它更适合高速、长距离')
strip('C3s', 2, '就是数据的载体从电换成了光。'); strip('C4s', 2, '激光器发出一束稳定的光，'); strip('C5s', 2, '再由调制器按照电信号的 0 和 1，')
strip('C6s', 2, '让这束光一明'); strip('C7s', 2, '一暗，数据就被“装”到了光上。'); strip('C8s', 2, '所以前面还有一个驱动器')
strip('F0', 3, '第四站 光的路：铁轨与对接'); strip('F1', 3, '光能比铜缆跑得远得多，信号依'); strip('F2', 3, '然清晰可辨。')
strip('H1', 3, '芯只有头发丝的十分之一左右粗，'); strip('H2', 3, '两者要对准接好，'); strip('H3', 3, '接歪一点光就漏掉了。')
strip('V0', 3, '第五站 抵达：把货卸回仓库'); strip('V1', 3, '感光元件把光的明暗重新变成电流。'); strip('V2', 3, '这时的电流非常微弱，'); strip('V3', 3, '要先经过一个放大器放大，'); strip('V4', 3, '光变回电，一列变回一排。')
strip('E0', 4, '一句话带走'); strip('E1', 4, '电信号跑得越快、越远，'); strip('E2', 4, '就越难保持清晰，'); strip('E3', 4, '所以数据要换乘光；'); strip('E4', 4, '但换成光，也带来了电光转换'); strip('E5', 4, '和精密对接的新难题。')

L, R = 0, 1700
CLIPS[T]['at'] = [0, 0]
stack('intro', ['I1', 'I2', 'I3', 'I4', 'I5'], L, 170)
stack('s1', ['A0', 'A1', 'A2', 'A3', 'A4'], R, 0)
stack('s2', ['B0', 'B1', 'B2', 'B3', 'B4'], R, 1800)
stack('dsp', ['D1', 'D2', 'D3'], R, 3300)
stack('reach', ['R1', 'R2'], R, 4720)
stack('s3a', ['C0', 'C1s', 'C2s'], L, 3020)
stack('s3b', ['C3s', 'C4s', 'C5s', 'C6s', 'C7s', 'C8s'], L, 3360)
stack('s4', ['F0', 'F1', 'F2'], L, 5400)
stack('s4b', ['H1', 'H2', 'H3'], L, 6900)
stack('s5', ['V0', 'V1', 'V2', 'V3', 'V4'], R, 6100)
stack('end', ['E0', 'E1', 'E2', 'E3', 'E4', 'E5'], 1150, 8300)
CARDS.update({
  'G':   dict(kind='gpu',      at=[L, 960],  w=900, h=760,  r=-0.01),
  'C1':  dict(kind='serdes',   at=[R, 950],  w=900, h=1000, r=-0.008),
  'C2a': dict(kind='blur',     at=[R, 2650], w=900, h=760,  r=0.008),
  'C2b': dict(kind='dsp',      at=[R, 4000], w=900, h=860,  r=-0.01),
  'C2c': dict(kind='reach',    at=[R, 5250], w=900, h=600,  r=0.01),
  'C3':  dict(kind='transfer', at=[L, 4560], w=900, h=1150, r=0.008),
  'C4a': dict(kind='race',     at=[L, 6150], w=900, h=950,  r=-0.008),
  'C4b': dict(kind='align',    at=[L, 7560], w=900, h=700,  r=0.01),
  'C5':  dict(kind='arrive',   at=[R, 7300], w=900, h=1100, r=-0.008),
})


# ---------- 画幅：默认竖屏（抖音/小红书）；LAND=1 出 B站横屏版（1920×1080，时间表完全一样，只改取景） ----------
LAND = os.environ.get('LAND') == '1'
SW, SH = (1920, 1080) if LAND else (1080, 1920)
TOP, BOT = (120, 900) if LAND else (235, 1440)          # 纸条/卡片放在进度条下面、字幕带上面
BAND = (925, 1055) if LAND else (1470, 1660)            # 字幕带：划重点的纸条不能落在这里
OUTF = 'desk_voice_land.json' if LAND else 'desk_voice.json'

# ---------- 时间表工具（旁白版：从 0 往后排，镜头/标注都按「现在」往后推） ----------
MARKS, LABELS, STRINGS, CAM, SFX = [], [], [], [], []
CARD_LABELS = {k: [] for k in CARDS}; CUE = {}
TM = [0.0]
def now(): return TM[0]
def adv(d): assert abs(d * 8 - round(d * 8)) < 1e-9, d; TM[0] = round(TM[0] + d, 4)
def cam(t, xy, z, e='sine'): CAM.append(dict(t=round(t, 4), x=xy[0], y=xy[1], z=z, e=e))
def hold(d, dz=0.02): last = CAM[-1]; adv(d); cam(now(), [last['x'], last['y']], round(last['z'] * (1 + dz), 4), 'lin')
def go(xy, z, d=1.0, e='sine', g=0.08): SFX.append(dict(t=now(), kind='whoosh', dur=d, g=g)); adv(d); cam(now(), xy, z, e)
def label(text, xy, at, size=30, align='center', r=0.0, bg=None, fg=None, rate=24):
    LABELS.append(dict(text=text, x=xy[0], y=xy[1], at=round(at, 4), size=size, align=align, r=r, bg=bg, fg=fg, rate=rate)); SFX.append(dict(t=round(at, 4), kind='label', text=text, rate=rate))
def clabel(cid, text, cx, cy, at, size=40, align='center', bg='cream', r=0.0, rate=24):
    CARD_LABELS[cid].append(dict(text=text, x=cx, y=cy, at=round(at, 4), size=size, align=align, bg=bg, r=r, rate=rate)); SFX.append(dict(t=round(at, 4), kind='label', text=text, rate=rate))
def string(key, a, b, d=0.5, sag=0.06):        # 红线和镜头移动同时开始
    STRINGS.append(dict(key=key, a=a, b=b, t=[now(), round(now() + d, 4)], sag=sag, route=False)); SFX.append(dict(t=now(), kind='string', dur=d))
def rstring(key, a, b, t0, t1, sag=0.04):      # 五站路线
    STRINGS.append(dict(key=key, a=a, b=b, t=[round(t0, 4), round(t1, 4)], sag=sag, route=True)); SFX.append(dict(t=round(t0, 4), kind='string', dur=t1 - t0))
def sfx(t, kind, **kw): SFX.append(dict(t=round(t, 4), kind=kind, **kw))
def edge(cid, side='r', dy=0):   # 短条左/右边缘的中点（世界坐标）
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']; return P(cid, (x1 + 2) if side == 'r' else (x0 - 2), (y0 + y1) / 2 + dy)
def above(cid): c = CLIPS[cid]; w = (c['crop'][2] - c['crop'][0]) * c['k']; h = (c['crop'][3] - c['crop'][1]) * c['k']; return [round(c['at'][0] - w / 2 + 60, 1), round(c['at'][1] - h / 2 - 95, 1)]
def ctop(cid, dx=0): c = CARDS[cid]; return PC(cid, dx, -c['h'] / 2 + 30)
def cbot(cid, dx=0): c = CARDS[cid]; return PC(cid, dx, c['h'] / 2 - 30)
def leftof(cid): c = CLIPS[cid]; w = (c['crop'][2] - c['crop'][0]) * c['k']; return [round(c['at'][0] - w / 2 - 110, 1), c['at'][1]]
STICK = {n: (leftof if LAND else above)(cid) for n, cid in {1: 'A0', 2: 'B0', 3: 'C0', 4: 'F0', 5: 'V0'}.items()}   # 横屏：贴纸贴在站名左边（竖屏贴在上面）
STATION_OF = {'s1': 1, 's2': 2, 's3a': 3, 's4': 4, 's5': 5}
OVER = dict(x=850, y=3050, z=0.165) if LAND else dict(x=850, y=4380, z=0.208)       # 横屏装不下整张桌子：开头看五站，结尾看后半张
OVER2 = dict(x=850, y=5300, z=0.165) if LAND else OVER
ZC = (lambda r: P('H1', r[0][1] + 5.5, r[0][3] - 4.5))(runs(3, '芯只有')[0])           # 「芯」字中心：Kurzgesagt 钻进去的那一点
EXITS = {0: edge('I5', 'r', 6), 1: PC('C1', 300, 470), 2: PC('C2c', -440, 120), 3: PC('C3', 300, 545), 4: PC('C4b', 440, -120), 5: PC('C5', -300, 520)}
TRAVEL, STATION = [], []
def travel(i, a, b): TRAVEL.append(dict(route=i, t=[round(a, 4), round(b, 4)]))

# ---------- 旁白 ----------
SCRIPT = {s['id']: s for s in json.load(open(os.path.join(ROOT, '配音/script_ep1.json'), encoding='utf-8'))}
ALIGN = json.load(open(os.path.join(ROOT, '配音/align_ep1.json'), encoding='utf-8'))
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
VOICE, FOCUS = [], []
LINE = {}
def speak(lid):
    t0 = g8(now()); VOICE.append(dict(id=lid, t=t0, file=f'配音/fish/{lid}.wav')); LINE[lid] = t0; return t0
def span(lid, phrase):
    text = SCRIPT[lid]['text']; i = text.find(phrase); assert i >= 0, f'旁白 {lid} 里没有「{phrase}」'
    return LINE[lid] + tmap(lid, i), LINE[lid] + tmap(lid, i + len(phrase))
def vmark(cid, kind, strip_phrase, lid, spoken, mind=0.375):
    a, b = span(lid, spoken); t0 = g8(a - 0.06); d = max(mind, g8(b - a))
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']
    run = [r for r in runs(c['page'], strip_phrase) if x0 <= r[0][1] and r[-1][2] <= x1 and y0 <= r[0][3] <= y1]; assert run, f'「{strip_phrase}」不在短条 {cid} 里'
    MARKS.append(dict(clip=cid, kind=kind, segs=boxes(run[0]), t=[t0, round(t0 + d, 4)], seed=len(MARKS) + 2)); SFX.append(dict(t=t0, kind='marker' if kind == 'hl' else 'pen', dur=d, soft=1))
def focus(stack, ids, a, b): FOCUS.append(dict(stack=stack, ids=ids, t=[round(a, 3), round(b, 3)]))
def lend(lid): return LINE[lid] + ALIGN[lid]['dur']
def after(lid, gap=0.5): adv(g8(lend(lid) + gap - now()))
def fwin(stack, ids, lid, pre=0.15, post=0.2): focus(stack, ids, LINE[lid] - pre, lend(lid) + post)
def fitstack(name, top=TOP, bot=BOT, at=None):   # 一摞纸条整摞放在 HUD 下、字幕带上面；at＝这摞纸条中心落在屏幕的哪一高度（默认居中；横屏不用）
    b = list(STACKS[name]['bb'])
    if LAND and name in STATION_OF: b[0] = min(b[0], STICK[STATION_OF[name]][0] - 100)     # 横屏：贴纸也框进来
    hgt = b[3] - b[1]; z = min(SZ(name), (bot - top) / (hgt + 40))
    if LAND: z = min(z, 1.85, SW * 0.9 / (b[2] - b[0] + 40)); at = None
    z = round(z, 3); cy = (b[1] + b[3]) / 2
    if at == 'top': at = top + 20 + hgt * z / 2
    return [round((b[0] + b[2]) / 2, 1), round(cy + (SH / 2 - (at or (top + bot) / 2)) / z, 1)], z
def gost(name, d=1.0, e='sine', g=0.08, at=None): xy, z = fitstack(name, at=at); go(xy, z, d, e, g)
def gocard(cid, z=1.12, d=1.0):                # 卡片框在 HUD 下、字幕带上面
    h = CARDS[cid]['h']
    if LAND: z = round(min(z, (BOT - TOP) / (h + 20)), 3); go(PC(cid, 0, round((SH / 2 - (TOP + BOT) / 2) / z)), z, d); return
    z = min(z, 1205 / h); dy = max(0, h / 2 - 470 / z)
    if 960 - (h / 2 + dy) * z < 215: dy = (960 - 215) / z - h / 2
    go(PC(cid, 0, round(dy)), round(z, 3), d)

# ======================= 旁白时间表 =======================
# --- 钩子：第③站上半摞（标题问题 + 两条原话） ---
_, z = fitstack('s3a'); HL_Y = STACKS['s3a']['bb'][1] - 235
if LAND: hb = [HL_Y - 40, STACKS['s3a']['bb'][3]]; z = round(min(1.85, (BOT - 80) / (hb[1] - hb[0] + 40)), 3); cam(0, [SC('s3a')[0], round((hb[0] + hb[1]) / 2 + (SH / 2 - (80 + BOT) / 2) / z, 1)], z, 'lin')
else: cam(0, [SC('s3a')[0], round(HL_Y + (960 - 330) / z, 1)], z, 'lin')
label('AI 芯片互连为什么要从电换成光？', [SC('s3a')[0], HL_Y], 0.0, size=27, r=-0.02, rate=24)
adv(0.25)
speak('P1'); fwin('s3a', [], 'P1')
after('P1', 0.25)
speak('P2'); fwin('s3a', ['C1s', 'C2s'], 'P2'); focus('s3b', [], 0, lend('P2') + 0.2)
vmark('C1s', 'hl', '不是光跑得更快', 'P2', '不是光跑得更快'); vmark('C2s', 'circle', '更适合高速、长距离', 'P2', '更适合高速、长距离', 0.625)
after('P2', 0.375); hold(0, 0)
# 快镜头：拉开再钻到标题（只有这种很快的镜头带运动模糊）
a = now(); cam(a + 0.875, [500, 1700], 0.36, 'cubic'); cam(a + 1.75, [0, 0], 1.5 if LAND else 1.12, 'cubic'); sfx(a, 'whoosh', dur=1.75, g=0.16); TM[0] = a + 1.75
speak('P3'); vmark(T, 'hl', '一个比特的旅程', 'P3', '一个比特，走一遍它的旅程')
after('P3', 0.375); hold(0, 0)
# --- 开场：几千颗 GPU 要互相交换结果 ---
gost('intro', 1.0, at='top')
speak('P4'); fwin('intro', ['I1'], 'P4'); vmark('I1', 'hl', '成千上万颗 GPU 一起算', 'P4', '成千上万颗 GPU 一起算')
after('P4', 0.25); hold(0, 0)
string('I-G', edge('I1', 'r'), ctop('G', 250)); gocard('G')
t0 = g8(now()); speak('P5'); x0 = g8(max(t0 + 0.875, span('P5', '交换结果')[0])); X = [x0, x0 + 0.875, x0 + 1.75]
clabel('G', '每算一步，都要交换结果', 0, 300, x0, size=42)
for tt in X: sfx(tt, 'exchange')
after('P5', 0.25); adv(max(0, g8(X[-1] + 0.75 - now()))); CUE['G'] = dict(x=X, t0=t0, end=now()); hold(0, 0)
string('G-intro', cbot('G', -250), edge('I3', 'r')); gost('intro', 1.0, at='top')
speak('P6'); fwin('intro', ['I3'], 'P6'); vmark('I3', 'hl', '还要“说得快”', 'P6', '还要“说得快”')
after('P6', 0.25)
speak('P7'); fwin('intro', ['I4', 'I5'], 'P7'); vmark('I4', 'hl', '借助光来完成', 'P7', '借助光来完成'); vmark('I5', 'circle', '光互连', 'P7', '光互连', 0.625)
after('P7', 0.375); hold(0, 0)
# --- 五站路线：拉回全桌，说到哪一站，那一站的贴纸就弹出来 ---
go([OVER['x'], OVER['y']], OVER['z'], 1.5, 'cubic', 0.14)
speak('P8'); label('跟着一个比特，走五站', [-2350, 3050] if LAND else [0, 2250], g8(LINE['P8'] + 0.25), size=230 if LAND else 150, r=-0.015, rate=24)
after('P8', 0.25)
speak('P9'); HUD_IN = g8(LINE['P9'])
POP = []
for w in ['出发', '电的路', '换乘', '光的路', '抵达']: POP.append(g8(max(span('P9', w)[0], (POP[-1] + 0.375) if POP else 0)))
for i in range(5): rstring(f'route{i}', EXITS[i], STICK[i + 1], POP[i] - 0.5, POP[i]); sfx(POP[i], 'stick', n=i + 1)
after('P9', 0.375); hold(0, 0.04)
# --- ① 出发 ---
travel(0, now(), now() + 1.5); gost('s1', 1.5, 'cubic', 0.14); STATION.append((1, now()))
speak('P10'); fwin('s1', ['A0'], 'P10'); vmark('A0', 'hl', '第一站 出发', 'P10', '第一站，出发')
after('P10', 0.25)
speak('P11'); fwin('s1', ['A1', 'A2'], 'P11'); vmark('A1', 'hl', '“一大排”并排放着', 'P11', '“一大排”并排放着'); vmark('A2', 'hl', '出口有限', 'P11', '出口有限')
after('P11', 0.25); hold(0, 0)
# 先演机制：排成一列、变成高速电信号（「SerDes」那条纸条先不划）
string('s1-C1', edge('A2', 'r'), ctop('C1', 250)); gocard('C1')
t0 = g8(now()); speak('P12'); go_ = g8(max(t0 + 0.5, span('P12', '排成一列')[0] - 0.25))
clabel('C1', 'GPU 里：一大排', -390, -448, t0 + 0.125, align='left'); clabel('C1', '出口有限', -330, -100, go_, bg='red', align='left')
clabel('C1', '排成一列，一件接一件', -390, 120, g8(max(go_ + 0.5, span('P12', '一件接一件')[0])), align='left')
clabel('C1', '变成高速电信号', 390, 400, g8(max(go_ + 1.5, span('P12', '变成一条高速的电信号')[0])), align='right')
sfx(go_, 'serdes', dur=3.4)
after('P12', 0.25); adv(max(0, g8(go_ + 3.75 - now()))); CUE['C1'] = dict(t0=t0, go=go_, end=now()); hold(0, 0)
# 再报名字
string('C1-s1', cbot('C1', -250), edge('A4', 'r')); gost('s1', 1.0)
speak('P13'); mid = span('P13', '现在只需记住')[0]
focus('s1', ['A4'], LINE['P13'] - 0.15, mid); focus('s1', ['A3'], mid, lend('P13') + 0.2)
vmark('A4', 'under', 'SerDes', 'P13', 'SerDes'); vmark('A3', 'hl', '排成一列', 'P13', '先要被排成一列')
after('P13', 0.375); hold(0, 0)
# --- ② 电的路 ---
travel(1, now(), now() + 1.5); gost('s2', 1.5, 'cubic', 0.12); STATION.append((2, now()))
speak('P14'); fwin('s2', ['B0'], 'P14'); vmark('B0', 'hl', '第二站 电的路', 'P14', '第二站，电的路')
after('P14', 0.25)
speak('P15'); fwin('s2', [], 'P15')
after('P15', 0.25)
speak('P16'); fwin('s2', ['B0'], 'P16'); vmark('B0', 'hl', '跑得越快', 'P16', '车开得越快'); vmark('B0', 'hl', '货越难认', 'P16', '越来越难认清')
after('P16', 0.25)
speak('P17'); fwin('s2', ['B1', 'B2', 'B3', 'B4'], 'P17')
vmark('B1', 'hl', '速度越高、距离越远', 'P17', '速度越高、距离越远'); vmark('B2', 'hl', '到达时就越模糊', 'P17', '到达时就越模糊')
vmark('B3', 'under', '分不清哪个是0', 'P17', '分不清哪个是 0'); vmark('B4', 'under', '个是1', 'P17', '哪个是 1')
after('P17', 0.25); hold(0, 0)
string('s2-C2a', edge('B3', 'r'), ctop('C2a', 250)); gocard('C2a')
t0 = g8(now()); adv(0.25); speak('P18')
lA = g8(max(span('P18', '出发时还清清楚楚')[0], t0 + 0.5)); lB = g8(max(span('P18', '跑远了')[0], t0 + 1.5, lA + 0.75))
clabel('C2a', '出发时：清楚', -330, 210, lA, align='left'); clabel('C2a', '跑远了：糊了', 380, 210, lB, bg='red', align='right')
sfx(t0, 'thock'); sfx(lB, 'blur')
after('P18', 0.25); adv(max(0, g8(t0 + 3.0 - now()))); CUE['C2a'] = dict(t0=t0, e0=t0, end=now()); hold(0, 0)
# 检修站：先讲它做什么，再在卡片上报名字、看它耗电
string('C2a-dsp', cbot('C2a', -250), edge('D1', 'l')); gost('dsp', 1.0, at=1060)
speak('P19'); fwin('dsp', ['D1', 'D2'], 'P19'); vmark('D1', 'hl', '“检修站”', 'P19', '“检修站”'); vmark('D2', 'hl', '把模糊的信号重新认出来', 'P19', '把模糊的信号重新认出来')
after('P19', 0.25); hold(0, 0)
string('dsp-C2b', edge('D2', 'r'), ctop('C2b', 250)); gocard('C2b')
t0 = g8(now()); speak('P20')
g1 = g8(max(t0 + 0.875, span('P20', '检修要耗电')[0])); g2 = g1 + 0.625; g3 = g8(max(g2 + 0.625, span('P20', '数量庞大')[0])); g4 = g8(max(g3 + 0.625, span('P20', '累积起来')[0]))
clabel('C2b', '进站：糊的', -390, -250, t0 + 0.125, bg='red', align='left'); clabel('C2b', '出站：又清楚了', 390, -250, t0 + 0.75, align='right')
clabel('C2b', '每整理一组，耗一格电', 0, 330, g1 + 0.125)
for tt in (g1, g2, g3, g4): sfx(tt, 'dsp')
after('P20', 0.25); adv(max(0, g8(g4 + 0.75 - now()))); CUE['C2b'] = dict(t0=t0, groups=[g1, g2, g3, g4], end=now()); hold(0, 0)
string('C2b-reach', cbot('C2b', -250), edge('R1', 'l')); gost('reach', 1.0)
speak('P21'); vmark('R1', 'hl', '速度越高', 'P21', '速度越高'); vmark('R2', 'hl', '电的路能可靠覆盖的距离就越短', 'P21', '电的路能可靠覆盖的距离就越短')
after('P21', 0.25); hold(0, 0)
string('reach-C2c', edge('R2', 'r'), ctop('C2c', 250)); gocard('C2c', 1.15)
t0 = g8(now()); speak('P22')
slow = g8(max(t0, span('P22', '慢的时候')[0])); fast = g8(max(slow + 1.0, span('P22', '快了以后')[0])); so = g8(max(fast + 0.75, span('P22', '这正是')[0]))
clabel('C2c', '慢：能可靠地跑很远', -400, -235, slow, align='left', size=38); clabel('C2c', '快：没多远就糊了', -400, 5, fast, align='left', bg='red', size=38)
clabel('C2c', '所以：换乘', 400, 245, so, align='right', size=40)
sfx(slow, 'reach'); sfx(fast, 'reach2')
after('P22', 0.375); CUE['C2c'] = dict(t0=t0, slow=slow, fast=fast, end=now()); hold(0, 0)
# --- ③ 换乘 ---
travel(2, now(), now() + 1.5); gost('s3a', 1.5, 'cubic', 0.12, at=1000); STATION.append((3, now()))
speak('P23'); fwin('s3a', ['C0'], 'P23'); vmark('C0', 'hl', '第三站 换乘', 'P23', '第三站，换乘')
after('P23', 0.25); hold(0, 0)
gost('s3b', 1.0)
speak('P24'); fwin('s3b', ['C3s'], 'P24'); vmark('C3s', 'hl', '数据的载体从电换成了光', 'P24', '数据的载体，从电换成了光')
after('P24', 0.25)
speak('P25'); fwin('s3b', ['C4s'], 'P25'); vmark('C4s', 'hl', '激光器发出一束稳定的光', 'P25', '激光器发出一束稳定的光')
after('P25', 0.25)
speak('P26'); fwin('s3b', ['C5s', 'C6s', 'C7s'], 'P26')
vmark('C5s', 'under', '调制器', 'P26', '调制器'); vmark('C6s', 'hl', '一明', 'P26', '一明', 0.25); vmark('C7s', 'hl', '一暗', 'P26', '一暗', 0.25)
vmark('C7s', 'hl', '数据就被“装”到了光上', 'P26', '数据就被“装”到了光上')
after('P26', 0.25)
speak('P27'); fwin('s3b', ['C8s'], 'P27'); vmark('C8s', 'under', '驱动器', 'P27', '驱动器')
after('P27', 0.25); hold(0, 0)
string('s3-C3', edge('C8s', 'r'), ctop('C3', 250)); gocard('C3')
t0 = g8(now()); mod = t0 + 0.5; drv = t0 + 2.0
clabel('C3', '激光器：一束稳定的光', -400, -470, t0 + 0.125, align='left'); clabel('C3', '调制器：1 亮，0 暗', -400, -40, mod + 0.25, align='left')
clabel('C3', '驱动器：把电信号放大', -400, 300, drv + 0.125, align='left')
adv(g8(drv + 0.5 - now())); speak('P28'); h0 = g8(span('P28', '这个比特')[0]); h1 = g8(max(span('P28', '换到了光上')[0], h0 + 1.0))
clabel('C3', '还是 1，只换了载体', 400, 470, g8(max(span('P28', '还是 1')[0], h1 + 0.25)), align='right', bg='red')
sfx(t0, 'laser'); sfx(mod, 'mod', dur=3.0); sfx(drv, 'amp'); sfx(h1, 'flash')
after('P28', 0.375); adv(max(0, g8(h1 + 1.5 - now()))); CUE['C3'] = dict(t0=t0, laser=t0, mod=mod, drv=drv, hero=[h0, h1], end=now()); hold(0, 0)
# --- ④ 光的路 ---
travel(3, now(), now() + 1.5); gost('s4', 1.5, 'cubic', 0.12); STATION.append((4, now()))
speak('P29'); fwin('s4', ['F0'], 'P29'); vmark('F0', 'hl', '第四站 光的路', 'P29', '第四站，光的路')
after('P29', 0.25)
speak('P30'); fwin('s4', ['F1', 'F2'], 'P30')
vmark('F1', 'hl', '光能比铜缆跑得远得多，信号依', 'P30', '光能比铜缆跑得远得多，信号依'); vmark('F2', 'hl', '然清晰可辨', 'P30', '然清晰可辨')
after('P30', 0.25); hold(0, 0)
string('s4-C4a', edge('F2', 'r'), ctop('C4a', 250)); gocard('C4a')
t0 = g8(now()); tE0 = t0 + 0.25; adv(0.25); speak('P31')
eL = g8(max(span('P31', '电越跑越弱')[0], tE0 + 0.75)); envE = g8(max(span('P31', '越乱')[1], tE0 + 2.0))
m0 = g8(max(span('P31', '光的损耗少')[0] - 0.25, envE + 0.25)); lL = g8(max(span('P31', '光的损耗少')[0], m0 + 0.5)); envL = g8(max(span('P31', '更稳定')[0], m0 + 0.875))
clabel('C4a', '电：越跑越弱、越乱', 390, -355, eL, bg='red', align='right'); clabel('C4a', '光：损耗少，更稳定', -370, 320, lL, align='left')
sfx(t0, 'thock'); sfx(eL, 'blur'); sfx(m0, 'morph'); sfx(envE, 'envE'); sfx(envL, 'envL')
after('P31', 0.25); speak('P32'); after('P32', 0.375)
CUE['C4a'] = dict(t0=t0, heading=t0, tE0=tE0, tL0=m0 - 0.5, morph=[m0, m0 + 0.5], envE=envE, envL=envL, end=now()); LABELS_TIE = envE + 1 / 12; hold(0, 0)
string('C4a-s4b', cbot('C4a', -250), edge('H1', 'l')); gost('s4b', 1.0)
speak('P33'); fwin('s4b', ['H1'], 'P33'); vmark('H1', 'hl', '芯只有头发丝的十分之一左右粗', 'P33', '芯，只有头发丝的十分之一左右粗')
after('P33', 0.125); hold(0, 0)
# Kurzgesagt：钻进「芯」字 → 镜头圈打开：光纤的芯 vs 头发丝，一根头发丝的直径上排得下十个芯 → 拉回
a = g8(now()); cam(a + 0.5, ZC, 2.7, 'sine'); cam(a + 1.5, ZC, 40, 'cubic'); TM[0] = a + 0.5
speak('P34'); TM[0] = a + 1.5
core = a + 1.5; h_ = g8(max(core + 0.25, span('P34', '头发丝的直径上')[0])); hair = [h_, h_ + 0.5]
s_ = g8(max(hair[1] + 0.25, span('P34', '大约能排下')[0])); split = [s_, s_ + 0.25]; pairs = split[1]
tenth = g8(max(pairs + 0.5, span('P34', '十个这样的芯')[0])); o0 = g8(max(lend('P34') + 0.5, tenth + 1.25))
LENS = dict(at=ZC, zin=[a + 0.5, a + 1.5], open=[a + 0.75, a + 1.25], core=core, hair=hair, split=split, pairs=pairs, tenth=tenth, out=[o0, o0 + 1.0], zmax=40)
xy_, z_ = fitstack('s4b'); cam(o0, ZC, 40, 'lin'); cam(o0 + 1.0, xy_, z_, 'cubic'); TM[0] = o0 + 1.0; hold(0.25, 0.01)
sfx(a + 0.5, 'riser', dur=1.0); sfx(a + 1.25, 'boom'); sfx(pairs, 'pairs'); sfx(o0, 'pullout', dur=1.0)
for (txt_, at) in [('光纤的芯', core), ('一根头发丝（截面）', hair[0]), ('芯≈头发丝的1/10', tenth)]: SFX.append(dict(t=at, kind='label', text=txt_, rate=20 if '1/10' in txt_ else 14))
speak('P35'); fwin('s4b', ['H2', 'H3'], 'P35'); vmark('H2', 'hl', '两者要对准接好', 'P35', '两者要对准接好'); vmark('H3', 'hl', '接歪一点光就漏掉了', 'P35', '接歪一点，光就漏掉了')
after('P35', 0.25); hold(0, 0)
string('s4b-C4b', edge('H3', 'r'), ctop('C4b', 250)); gocard('C4b', 1.15)
t0 = g8(now()); speak('P36'); sl = g8(max(t0 + 1.75, span('P36', '两段轨道的对接')[0])); slide = [sl, sl + 0.5]
clabel('C4b', '歪一点：光就漏了', -400, 230, t0 + 0.5, bg='red', align='left'); clabel('C4b', '对准了：光才进得去', 400, 230, slide[1] + 0.25, align='right')
sfx(t0 + 0.25, 'leak', dur=1.5); sfx(slide[0], 'slide'); sfx(slide[1], 'click')
after('P36', 0.25); adv(max(0, g8(slide[1] + 1.25 - now()))); CUE['C4b'] = dict(t0=t0, slide=slide, end=now()); hold(0, 0)
# --- ⑤ 抵达 ---
travel(4, now(), now() + 1.5); gost('s5', 1.5, 'cubic', 0.12); STATION.append((5, now()))
speak('P37'); fwin('s5', ['V0'], 'P37'); vmark('V0', 'hl', '第五站 抵达', 'P37', '第五站，抵达')
after('P37', 0.25)
speak('P38'); fwin('s5', ['V1'], 'P38'); vmark('V1', 'hl', '感光元件把光的明暗重新变成电流', 'P38', '感光元件，把光的明暗重新变成电流')
after('P38', 0.25)
speak('P39'); fwin('s5', ['V2', 'V3'], 'P39'); vmark('V2', 'hl', '非常微弱', 'P39', '非常微弱'); vmark('V3', 'under', '放大器', 'P39', '放大器')
after('P39', 0.25); hold(0, 0)
string('s5-C5', edge('V3', 'r'), ctop('C5', 250)); gocard('C5')
t0 = g8(now()); amp = t0 + 1.0
clabel('C5', '感光元件：光 → 电流', -400, -470, t0 + 0.125, align='left'); clabel('C5', '电流很弱，放大器放大', -400, -60, amp + 0.125, align='left')
adv(0.5); speak('P40'); fa = g8(max(amp + 0.75, span('P40', '被重新拆开')[0])); fan = [fa, fa + 1.5]
clabel('C5', '一列 → 一排，回到 GPU B', 400, 470, g8(max(fa + 0.25, span('P40', '并排放回')[0])), align='right')
sfx(t0 + 0.25, 'pd'); sfx(amp, 'amp'); sfx(fa, 'fan', dur=1.5)
after('P40', 0.25); adv(max(0, g8(fa + 2.0 - now()))); CUE['C5'] = dict(t0=t0, pd=t0, amp=amp, fan=fan, end=now()); hold(0, 0)
string('C5-s5', cbot('C5', -250), edge('V4', 'r')); gost('s5', 1.0)
speak('P41'); fwin('s5', ['V4'], 'P41'); vmark('V4', 'hl', '光变回电，一列变回一排', 'P41', '光变回电，一列变回一排')
after('P41', 0.375); hold(0, 0)
# --- 收尾：拉回全桌 → 一句话带走 ---
go([OVER2['x'], OVER2['y']], OVER2['z'], 1.5, 'cubic', 0.16); STATION.append((6, now()))
rstring('route5', EXITS[5], edge('E0', 'l'), now(), now() + 0.75)
speak('P42'); after('P42', 0.25); hold(0, 0.03)
gost('end', 1.5, 'cubic', 0.10)
speak('P43'); fwin('end', ['E1', 'E2', 'E3'], 'P43')
vmark('E1', 'hl', '电信号跑得越快、越远', 'P43', '电信号跑得越快、越远'); vmark('E2', 'hl', '就越难保持清晰', 'P43', '就越难保持清晰'); vmark('E3', 'hl', '所以数据要换乘光', 'P43', '所以数据要换乘光')
after('P43', 0.25)
speak('P44'); fwin('end', ['E4', 'E5'], 'P44')
vmark('E4', 'under', '电光转换', 'P44', '电光转换'); vmark('E5', 'under', '精密对接', 'P44', '精密对接'); vmark('E5', 'hl', '新难题', 'P44', '新难题')
after('P44', 0.375)
speak('P45'); after('P45', 0.125)
eb = STACKS['end']['bb']
if LAND:      # 横屏：放在那摞纸条右边
    label('下一篇：第一站 出发', [eb[2] + 70, SC('end')[1] + 40], now(), size=26, align='left', r=-0.01)
    label('白话光互连 · 01', [eb[2] + 70, SC('end')[1] + 105], now() + 0.625, size=22, align='left', bg='red', r=-0.02)
else:
    label('下一篇：第一站 出发', [SC('end')[0], eb[3] + 55], now(), size=26, r=-0.01)
    label('白话光互连 · 01', [SC('end')[0], eb[3] + 115], now() + 0.625, size=22, bg='red', r=-0.02)
hold(2.25, 0.02)

# ---------- 字幕 ----------
def build_subs():
    out = []
    for v in VOICE:
        lid = v['id']; text = SCRIPT[lid]['text']; pos = 0
        for n, seg_ in enumerate(SCRIPT[lid]['sub']):            # 手写的字幕断句（script_ep1.json 的 sub）
            core = seg_.rstrip('？'); i = text.find(core, pos); assert i >= 0, (lid, seg_)
            j = i + len(core); pos = j
            out.append(dict(lid=lid, n=n, text=seg_, t=[round(LINE[lid] + tmap(lid, i) - 0.08, 3), round(LINE[lid] + tmap(lid, j) + 0.15, 3)]))
    for i in range(len(out) - 1):                      # 两条之间空隙很短就接上，不闪
        if out[i + 1]['t'][0] - out[i]['t'][1] < 0.45: out[i]['t'][1] = out[i + 1]['t'][0]
    return out
SUBS = build_subs()
# 只在「屏上没有这句话」的地方出字幕：镜头在卡片上、术语出现、旁白说了纸条上没有的内容；
# 旁白和眼前那摞纸条说的基本是同一句（连续相同的字占到 60% 以上）就不出
import difflib
CLEAN = lambda x: ''.join(ch for ch in x if ch not in '，。；：、？！“”‘’（）() ·')
def cam_mid(t):
    for i in range(1, len(CAM)):
        if t <= CAM[i]['t']:
            a_, b_ = CAM[i - 1], CAM[i]; p_ = (t - a_['t']) / max(1e-6, b_['t'] - a_['t']); return a_['x'] + (b_['x'] - a_['x']) * p_, a_['y'] + (b_['y'] - a_['y']) * p_
    return CAM[-1]['x'], CAM[-1]['y']
LENS_TXT = '光纤的芯一根头发丝截面芯≈头发丝的1/10'
def on_screen(t):
    if LENS['open'][0] <= t <= LENS['out'][0]: return 'lens', None
    x, y = cam_mid(t)
    for cid, cd in CARDS.items():
        if abs(x - cd['at'][0]) < cd['w'] / 2 and abs(y - cd['at'][1]) < cd['h'] / 2: return 'card', cid
    if abs(x) < 500 and abs(y) < 200: return 'title', None
    best = min(STACKS.items(), key=lambda kv: math.hypot(x - (kv[1]['bb'][0] + kv[1]['bb'][2]) / 2, y - (kv[1]['bb'][1] + kv[1]['bb'][3]) / 2))
    return 'stack', best[0]
FORCE = {('P1', 0): (False, '和桌上的标题标签同一句'), ('P9', 0): (False, '贴纸和进度条已经在数五站')}
for x_ in SUBS:
    kind, name = on_screen((x_['t'][0] + x_['t'][1]) / 2)
    if kind == 'card': x_['show'] = True; x_['why'] = f'卡片 {name}'
    else:
        sub = CLEAN(x_['text']); ref = {'lens': LENS_TXT, 'title': '一个比特的旅程'}.get(kind) or CLEAN(''.join(CLIPS[i]['text'] for i in STACKS[name]['ids']))
        same = sum(b.size for b in difflib.SequenceMatcher(None, sub, ref, autojunk=False).get_matching_blocks() if b.size >= 2)
        x_['overlap'] = round(same / max(1, len(sub)), 2); x_['show'] = x_['overlap'] < 0.6; x_['why'] = f"{name or kind} 重合 {x_['overlap']}"
    if (x_['lid'], x_['n']) in FORCE: x_['show'], x_['why'] = FORCE[(x_['lid'], x_['n'])]
# 连续出现的几条字幕合成一段，底下的纸色带整段只淡入淡出一次，不闪
runs_ = []
for i, x_ in enumerate(SUBS):
    if not x_['show']: continue
    if runs_ and SUBS[i - 1]['show'] and x_['t'][0] - SUBS[i - 1]['t'][1] < 0.45: runs_[-1][1] = x_['t'][1]; runs_[-1][2].append(x_)
    else: runs_.append([x_['t'][0], x_['t'][1], [x_]])
for r0, r1, xs in runs_:
    for x_ in xs: x_['run'] = [round(r0, 3), round(r1, 3)]
assert all(len(x['text']) <= 20 for x in SUBS), [x['text'] for x in SUBS if len(x['text']) > 18]
DUR = now()

# ---------- 检查 ----------
def ongrid(t): return abs(t * 8 - round(t * 8)) < 1e-6
bad = [(k, v) for k, v in [('cam', c['t']) for c in CAM] + [('mark', m['t'][0]) for m in MARKS] + [('label', l['at']) for l in LABELS] if not ongrid(v)]
assert not bad, bad
assert all(CAM[i]['t'] < CAM[i + 1]['t'] for i in range(len(CAM) - 1)), [(CAM[i]['t'], CAM[i + 1]['t']) for i in range(len(CAM) - 1) if CAM[i]['t'] >= CAM[i + 1]['t']]
def camseg(t):
    for i in range(1, len(CAM)):
        if t <= CAM[i]['t']: return CAM[i - 1], CAM[i]
    return CAM[-1], CAM[-1]
def cam_state(t):
    a, b = camseg(t)
    if a is b: return a
    p = (t - a['t']) / (b['t'] - a['t']); return dict(x=a['x'] + (b['x'] - a['x']) * p, y=a['y'] + (b['y'] - a['y']) * p, z=a['z'] * (b['z'] / a['z']) ** p)
for m in MARKS:      # 读字时镜头不动，整条都在画面里（顶部进度条以下、字幕带以上）
    a, b = camseg(m['t'][0] + 0.01); assert b['e'] == 'lin', f"标注 {m['clip']} {m['t']} 时镜头在动"
    if m['clip'] == T: continue
    for tt in m['t']:
        k = cam_state(tt); c = CLIPS[m['clip']]; w = (c['crop'][2] - c['crop'][0]) * c.get('k', K)
        sx0 = (c['at'][0] - w / 2 - k['x']) * k['z'] + SW / 2; sx1 = (c['at'][0] + w / 2 - k['x']) * k['z'] + SW / 2; sy = (c['at'][1] - k['y']) * k['z'] + SH / 2
        assert not (BAND[0] < sy < BAND[1]), f"{m['clip']} 划重点时落在字幕带里：y {sy:.0f}"
        assert sx0 > 20 and sx1 < SW - 20 and TOP - 30 < sy < BAND[0], f"{m['clip']}「{c['text']}」读的时候不在画面里：x {sx0:.0f}–{sx1:.0f}, y {sy:.0f}"
for cid, cu in CUE.items(): assert 't0' in cu and 'end' in cu, cid
out = dict(dur=DUR, bpm=120, K=K, clips=CLIPS, cards=CARDS, cardLabels=CARD_LABELS, cue=CUE, marks=MARKS, labels=LABELS, strings=STRINGS, cam=CAM,
           stick=STICK, pops=POP, over=OVER, travel=TRAVEL, station=STATION, hudIn=HUD_IN, lens=LENS, tieLabel=LABELS_TIE, stacks=STACKS,
           focus=FOCUS, voice=VOICE, subs=SUBS, sfx=sorted(SFX, key=lambda s: s['t']))
if LAND:      # 横屏版和竖屏版用同一条声音：人声、标注、音效的时间点必须一模一样
    P_ = json.load(open(os.path.join(ROOT, '代码工程/full/desk_voice.json'), encoding='utf-8'))
    assert P_['dur'] == DUR and P_['voice'] == VOICE and [m['t'] for m in P_['marks']] == [m['t'] for m in MARKS], '横屏版时间表和竖屏版不一致'
    assert [(x['t'], x['kind']) for x in P_['sfx']] == [(x['t'], x['kind']) for x in out['sfx']], '横屏版音效时间点和竖屏版不一致'
json.dump(out, open(os.path.join(ROOT, '代码工程/full', OUTF), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(OUTF, DUR, 's,', len(MARKS), 'marks,', len(CAM), 'cam keys,', len(VOICE), 'voice lines,', len(FOCUS), 'focus windows;', sum(x['show'] for x in SUBS), '/', len(SUBS), 'subs shown')
