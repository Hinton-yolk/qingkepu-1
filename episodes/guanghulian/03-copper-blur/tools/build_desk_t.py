# 白话光互连 03 · 小红书改版 t（由 tools/assemble.py 拼出，别直接改这个文件）—— 桌面布局沿用正片（tools/build_desk.py），时间表跟着旁白走
# 运行：python3 tools/build_desk_voice.py → 代码工程/ep3/desk_t.json（画面和配乐读同一份）
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

# ---------- 抖音第 1 条的摆放 ----------
def bare(cid): CARDS[cid]['bare'] = True
place_card('C0', 'cables', L, 1000, 1180, 0.0); bare('C0'); COLY[L] += 350
LAST[0] = 0
place_card('RT', 'route', R, 900, 700, 0.008)
place_stack('tail', ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9'], L); place_card('K4', 'tail', R, 900, 1100, 0.008)
place_card('G1', 'glitch', L, 900, 980, -0.01)
place_stack('far', ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8'], R); place_card('K6', 'faster', L, 900, 960, 0.01)
place_card('C1', 'cables', R, 1000, 1180, 0.0); bare('C1'); place_card('K7', 'reach', L, 900, 600, -0.01)
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'E1', 'E2', 'E3', 'E4', 'E9'], 850)
place_card('HE', 'here', 850, 1000, 260, 0.0); bare('HE')
for _cid in [c for c in CLIPS if c not in STACK_OF]: del CLIPS[_cid]          # 这一条用不到的纸条不上桌

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
def fitstack(name, top=310, bot=1320):       # 一摞纸条整摞放在 HUD 下、字幕带上面
    b = STACKS[name]['bb']; hgt = b[3] - b[1]; z = round(min(SZ(name), (bot - top) / (hgt + 40)), 3); cy = (b[1] + b[3]) / 2
    return [round((b[0] + b[2]) / 2, 1), round(cy + (960 - (top + bot) / 2) / z, 1)], z
def gost(name, d=1.0, e='sine', g=0.08): xy, z = fitstack(name); go(xy, z, d, e, g); arrive(name)
def gocard(cid, z=1.12, d=1.0):                # 卡片框在 HUD 下、字幕带上面
    h = CARDS[cid]['h']; z = min(z, 1010 / h); dy = 145 / z
    go(PC(cid, 0, round(dy)), round(z, 3), d)

# ======================= 旁白时间表（抖音第 1 条：线长一点，速度砍半？ ≤ 55 秒） =======================
# 机制演示长在第一帧：两根线的出口从第 0 秒就冒出信号（短线方正、长线糊了）。纸条一拍、演示一拍；结尾回到开头那根线。
def cardview(cid, z=1.12):
    h = CARDS[cid]['h']; z = min(z, 1010 / h); return PC(cid, 0, round(145 / z)), round(z, 3)
def gocab(cid, d=1.0): go(PC(cid, 0, 40), 1.1, d)
LENS = dict(at=[0, 0], zin=[1e6, 1e6 + 1], open=[1e6, 1e6 + 1], sharp=1e6, shave=[1e6, 1e6 + 1], lbl=1e6, lbl2=1e6, out=[1e6, 1e6 + 1], zmax=40)
# --- 第一帧：两根雷电线 + 大字；出口的信号已经在动 ---
cam(0, PC('C0', 30, 40), 1.0, 'lin')
clabel('C0', '长一点，速度砍半？', 0, -470, 0, size=60, bg='red', r=-0.012, rate=400)
adv(0.125); speak('X1'); after('X1', 0.25)
speak('X2'); a_ = g8(span('X2', '0.8 米')[0]); b_ = g8(max(a_ + 0.75, span('X2', '2 米')[0]))
clabel('C0', '0.8 米 · 40G', -150, -290, a_, size=44); clabel('C0', '2 米 · 20G', -150, 300, b_, size=44, bg='red')
after('X2', 0.125)
speak('T3'); r2 = g8(max(LINE['T3'] + 0.25, span('T3', '糊了')[0] - 0.5))
clabel('C0', '清楚', 330, -330, r2, size=40); clabel('C0', '糊了', 345, 235, r2 + 0.25, size=40, bg='red'); sfx(r2, 'blur')
after('T3', 0.125); CUE['C0'] = dict(t0=0, out=1, ring2=r2, end=now()); hold(0, 0.02)
# --- 快递路线图：亮「路上」 ---
string('C0-RT', cbot('C0', 300), ctop('RT', -250)); gocard('RT', 1.15, 0.75)
t0 = g8(now()); speak('X4'); lit = g8(max(t0 + 0.5, span('X4', '也卡在')[0] - 0.25))
clabel('RT', '第二站：路上', 0, 250, lit, size=44, bg='red'); sfx(lit, 'thock'); HUD_IN = lit
after('X4', 0.125); CUE['RT'] = dict(t0=t0, lit=lit, end=now()); hold(0, 0)
# --- 纸条一拍：每个比特都拖出一条尾巴 ---
string('RT-tail', cbot('RT', -250), edge('B6', 'r')); gost('tail', 0.75, 'sine', 0.12)
speak('T5'); fwin('tail', ['B6', 'B7'], 'T5'); vmark('B6', 'hl', '拖出一条尾巴', 'T5', '拖出一条尾巴')
after('T5', 0.125); hold(0, 0)
# --- 演示：一个比特拖尾 → 尾巴叠在一起（车库回音） ---
string('tail-K4', edge('B7'), ctop('K4', 250)); gocard('K4', 1.1, 0.75)
t0 = g8(now()); single = t0; m0 = t0 + 0.25; speak('X16')
seq = g8(max(m0 + 1.0, span('X16', '下一个字已经出口')[0])); sm = g8(max(seq + 0.75, span('X16', '糊成一片')[0])); ask = sm + 0.75
clabel('K4', '一个比特：拖出一条尾巴', -390, -440, m0 + 0.5, align='left'); clabel('K4', '尾巴压到后面的比特上', -390, 30, seq + 0.25, align='left', bg='red')
clabel('K4', '像车库回音：糊成一片', 390, 470, sm + 0.25, align='right', bg='red')
sfx(single, 'thock'); sfx(m0, 'shave', dur=0.75); sfx(seq, 'pairs'); sfx(sm, 'blur')
after('X16', 0.125); adv(max(0, g8(ask + 0.5 - now()))); CUE['K4'] = dict(t0=t0, single=single, morph=[m0, m0 + 0.75], seq=seq, sum=sm, ask=ask, end=now()); hold(0, 0)
# --- 演示：认错一个 → 照片花了、消息乱码 ---
string('K4-G1', cbot('K4', -250), ctop('G1', 250)); gocard('G1', 1.12, 0.75)
t0 = g8(now()); speak('X20'); ph = g8(max(t0 + 0.25, span('X20', '照片花了一块')[0])); ms = g8(max(ph + 0.75, span('X20', '乱码')[0] - 0.25))
clabel('G1', '照片花了一块', -210, 240, ph + 0.25, bg='red'); clabel('G1', '消息冒出乱码', 220, 0, ms + 0.25, bg='red'); sfx(ph, 'wrong'); sfx(ms, 'wrong')
after('X20', 0.25); adv(max(0, g8(ms + 0.75 - now()))); CUE['G1'] = dict(t0=t0, photo=ph, msg=ms, end=now()); hold(0, 0)
# --- 纸条一拍：越快，台阶越窄 ---
string('G1-far', cbot('G1', 250), edge('F3', 'l')); gost('far', 0.75, 'sine', 0.12)
speak('U16'); fwin('far', ['F3', 'F4', 'F5'], 'U16'); vmark('F3', 'hl', '越快', 'U16', '越快'); vmark('F4', 'hl', '时间减半', 'U16', '时间减半'); vmark('F5', 'hl', '变得更窄', 'U16', '变窄')
after('U16', 0.125); hold(0, 0)
# --- 演示：台阶变窄，同一条尾巴盖住两个比特 ---
string('far-K6', edge('F5'), ctop('K6', 250)); gocard('K6', 1.12, 0.75)
t0 = g8(now()); rowA = t0 + 0.125; hitA = rowA + 0.75; speak('X24'); rowB = g8(t0 + 1.0); hitB = g8(max(rowB + 1.0, span('X24', '压到更多后面的比特上')[0]))
clabel('K6', '原来', -390, -400, rowA, align='left'); clabel('K6', '快一倍：台阶更窄，尾巴还那么长', -390, 0, rowB + 0.25, align='left', size=38)
clabel('K6', '压到更多比特上', 390, 400, hitB + 0.25, align='right', bg='red', size=40)
sfx(rowA, 'thock'); sfx(rowB, 'thock'); sfx(hitB, 'wrong')
after('X24', 0.25); CUE['K6'] = dict(t0=t0, rowA=rowA, rowB=rowB, hitA=hitA, hitB=hitB, end=now()); hold(0, 0)
# --- 回到开头那根线（揭晓：配乐在这里停半拍） ---
string('K6-C1', cbot('K6', 250), ctop('C1', -300)); go(PC('C1', 30, 40), 1.0, 0.75)
t0 = g8(now()); speak('X28'); rg = g8(max(t0 + 0.25, span('X28', '长到 2 米')[0]))
clabel('C1', '0.8 米 · 40G', -150, -290, t0, size=44); clabel('C1', '2 米：只剩 20G', -150, 330, rg + 0.25, size=48, bg='red'); sfx(rg, 'thock')
after('X28', 0.125); CUE['C1'] = dict(t0=t0, out=1, ring=rg, end=now()); hold(0, 0)
REV = CUE['C1']['t0']
# --- 所以要换成光 ---
string('C1-K7', cbot('C1', -300), ctop('K7', 250)); gocard('K7', 1.15, 0.75)
t0 = g8(now()); slow, fast = t0, t0 + 0.75; speak('T11'); so = g8(max(fast + 0.75, span('T11', '换成光')[0]))
clabel('K7', '慢：能可靠地跑很远', -400, -235, slow, align='left', size=38); clabel('K7', '快：没多远就糊了', -400, 5, fast, align='left', bg='red', size=38)
clabel('K7', '所以：换成光', 400, 245, so, align='right', size=40); sfx(slow, 'reach'); sfx(fast, 'reach2')
after('T11', 0.25); adv(max(0, g8(so + 0.75 - now()))); CUE['K7'] = dict(t0=t0, slow=slow, fast=fast, end=now()); hold(0, 0)
# --- 一句话 + 你在这里 ---
ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
gost('end', 1.0, 'cubic', 0.10)
speak('T12'); fwin('end', ['E0', 'E2'], 'T12'); vmark('E0', 'hl', '一句话带走', 'T12', '一句话'); vmark('E2', 'hl', '跑得越快', 'T12', '越快')
after('T12', 0.125); hold(0, 0)
he = CARDS['HE']; go([he['at'][0], he['at'][1] - 40], 1.15, 0.75); hq = g8(now() - 0.5); CUE['HE'] = dict(t0=hq, end=hq + 1)
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
label('白话光互连 · 03', rightof('E0'), LINE['T12'] + 0.5, size=24, align='left', bg='red', r=-0.02)
hold(1.0, 0.02)

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
FORCE = {('X1', 0): (False, '第一帧：大字问题已经贴在实物上')}
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
        assert not (1310 < sy < 1500), f"{m['clip']} 划重点时落在字幕带里：y {sy:.0f}"
        assert sx0 > 20 and sx1 < 1060 and 300 < sy < 1860, f"{m['clip']}「{c['text']}」读的时候不在画面里：x {sx0:.0f}–{sx1:.0f}, y {sy:.0f}"
for st, ps in HL_PASSES.items():
    for (v0, c0, _), (v1, c1, _) in zip(ps, ps[1:]): assert c0 != c1, f'{st}：第 {v0} 轮和第 {v1} 轮荧光笔同色'
for cid, cu in CUE.items(): assert 't0' in cu and 'end' in cu, cid
print('荧光笔分轮：', {st: [(v, ['黄', '粉', '青'][HLC.index(c)]) for v, c, _ in ps] for st, ps in HL_PASSES.items() if len(ps) > 1})
out = dict(dur=DUR, bpm=120, K=K, clips=CLIPS, cards=CARDS, prints=PRINTS, cardLabels=CARD_LABELS, cue=CUE, marks=MARKS, pmarks=PMARKS, labels=LABELS, strings=STRINGS, cam=CAM,
           stick={}, pops=[], over=OVER, travel=[], station=[[2, HUD_IN + 1.5]], stn=['打包出发', '路上', '中转', '干线', '签收'], rev=REV, subY=1400, hudY=200, hudIn=HUD_IN, lens=LENS, stacks=STACKS, focus=FOCUS, voice=VOICE, subs=SUBS, sfx=sorted(SFX, key=lambda s: s['t']))
json.dump(out, open(os.path.join(ROOT, '代码工程/ep3/desk_t.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('desk_voice.json', DUR, 's,', len(MARKS), 'marks,', len(CAM), 'cam keys,', len(VOICE), 'voice lines,', len(FOCUS), 'focus windows;', sum(x['show'] for x in SUBS), '/', len(SUBS), 'subs shown')

