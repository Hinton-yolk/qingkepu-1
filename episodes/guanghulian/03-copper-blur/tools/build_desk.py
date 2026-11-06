# 白话光互连 03《电的路：信号为什么越跑越模糊？》Vox 竖屏 —— 桌面布局与时间表（唯一的真源）
# 运行：python3 tools/build_desk.py → 代码工程/ep3/desk.json（画面读）＋ 配乐读同一份；同时把原文短条裁到 代码工程/assets/strips/
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

place_stack('title', ['T1', 'T2'], L); place_card('H0', 'blur', L, 900, 760, -0.008)
LAST[0] = 0
place_stack('intro', ['I1', 'I2', 'I3', 'I4'], R); place_stack('meta', ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7'], R); place_card('K1', 'corridor', R, 900, 720, 0.008)
place_stack('ideal', ['W0', 'W1', 'W2', 'W3', 'W4'], L); place_stack('weak', ['A1', 'A2', 'A3', 'A4', 'A5'], L); place_card('K3', 'weaken', L, 900, 820, -0.008)
place_stack('tail', ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9'], R); place_card('K4', 'tail', R, 900, 1100, 0.008)
place_stack('sum', ['S1', 'S2', 'S3', 'S4'], L); place_stack('far', ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8'], L); place_card('K6', 'faster', L, 900, 960, -0.01)
place_stack('reach', ['R1', 'R2', 'R3'], R); place_card('K7', 'reach', R, 900, 600, 0.01)
place_stack('fix', ['X0', 'X1', 'X2', 'X3', 'X4', 'X4b'], L); place_card('K8', 'fixes', L, 900, 1000, -0.008)
place_stack('fix3', ['X5', 'X6', 'X7', 'X8', 'X9', 'X10'], R); place_card('K9', 'repair', R, 900, 900, 0.008)
place_stack('copper', ['Y1', 'Y2', 'Y3', 'Y4', 'Y5'], L); place_card('K10', 'split', L, 900, 760, -0.01)
place_stack('inv', ['V1', 'V2', 'V3', 'V4', 'V5', 'V6'], R); place_stack('ask', ['Q1', 'Q1b', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6'], R); place_card('K11', 'claim', R, 900, 900, 0.008)
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'E1', 'E2', 'E3', 'E4', 'E9'], 850)

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
# --- 钩子：标题（问题）＋ 正下方一张卡片：清楚的信号越跑越糊 ---
tb = STACKS['title']['bb']; h0 = CARDS['H0']; span = (h0['at'][1] + h0['h'] / 2) - tb[1]
ux0, ux1 = min(tb[0], h0['at'][0] - h0['w'] / 2), max(tb[2], h0['at'][0] + h0['w'] / 2)
cam(0, [round((ux0 + ux1) / 2), round((tb[1] + h0['at'][1] + h0['h'] / 2) / 2)], round(min(1.1, 1560 / span, 1000 / (ux1 - ux0)), 3), 'lin'); arrive('title')
t0 = 0.25; CUE['H0'] = dict(t0=t0, e0=t0, end=5.0)
clabel('H0', '出发时：清楚', -330, 210, 1.5, align='left'); clabel('H0', '跑远了：糊了', 380, 210, 2.75, bg='red', align='right')
sfx(t0, 'thock'); sfx(2.75, 'blur')
adv(0.25); mark('T2', 'hl', '越跑越模糊', 1.0); hold(3.75)
# --- 开场：上一篇 → 第二站 ---
gostack('intro', 2.0, 'cubic', 0.14)
HUD_IN = now(); mark('I1', 'hl', '排成一列', 0.5); mark('I3', 'hl', '第二站：电的路', 0.875); mark('I4', 'hl', '走线和铜缆', 0.75); hold(0.5)
# --- 走廊里喊话 ---
gostack('meta')
mark('M2', 'hl', '长走廊里喊话', 0.75); mark('M3', 'hl', '声音会变小', 0.625); mark('M4', 'hl', '余音还没散', 0.625); mark('M5', 'hl', '又到了', 0.375)
mark('M6', 'hl', '说得越快、走廊越长', 0.875); mark('M7', 'hl', '越听不清', 0.5); hold(0.375)
string('meta-K1', edge('M7'), ctop('K1', 250)); go(PC('K1', 0, 0), 1.12)
t0 = now(); CUE['K1'] = dict(t0=t0, words=[t0 + 0.25 + 0.5 * i for i in range(6)], fast=t0 + 3.5, end=t0 + 6.0)
clabel('K1', '声音会变小', -390, -260, t0 + 1.25, align='left'); clabel('K1', '余音没散，下一个字又到了', -390, 260, t0 + 2.5, align='left', bg='red')
for tt in CUE['K1']['words']: sfx(tt, 'shout')
hold(6.0)
# --- 理想的台阶 → 第一，变弱 ---
string('K1-ideal', cbot('K1', 250), edge('W0', 'r')); gostack('ideal', 2.0, 'sine', 0.12)
mark('W0', 'hl', '变弱了', 0.5); mark('W0', 'hl', '也拖尾了', 0.5); mark('W1', 'hl', '1和0', 0.375); mark('W2', 'hl', '干净利落', 0.5); mark('W4', 'hl', '方方正正的台阶', 0.75); hold(0.375)
gostack('weak')
mark('A1', 'hl', '变弱', 0.375); mark('A2', 'hl', '有损耗', 0.5); mark('A3', 'hl', '力气就越小', 0.625); mark('A4', 'hl', '差距被压缩', 0.625); mark('A5', 'hl', '难分清', 0.375); hold(0.375)
string('weak-K3', edge('A5'), ctop('K3', 250)); go(PC('K3', 0, 0), 1.12)
t0 = now(); CUE['K3'] = dict(t0=t0, wave=t0 + 0.25, env=t0 + 2.0, end=t0 + 5.25)
clabel('K3', '理想：方方正正的台阶', -390, -330, t0 + 0.25, align='left'); clabel('K3', '跑远了：高低差距被压缩', 390, 280, t0 + 2.5, align='right', bg='red')
sfx(t0 + 0.25, 'thock'); sfx(t0 + 2.0, 'envE'); hold(5.25)
# --- 第二，拖尾（第一轮）→ 钻进「棱角」→ 回来（第二轮，换色） ---
string('K3-tail', cbot('K3', -250), edge('B1', 'l')); gostack('tail', 2.0, 'sine', 0.12)
mark('B1', 'hl', '拖尾', 0.375); mark('B2', 'hl', '削弱快速跳变的力度', 0.875); mark('B3', 'hl', '更厉害', 0.375); mark('B4', 'hl', '棱角被削掉', 0.625); hold(0.25)
ZC = (lambda r: P('B4', (r[0][1] + r[-1][2]) / 2, r[0][3] - 4.5))(runs(1, '棱角')[0])
a = now(); cam(a + 0.5, ZC, 2.7, 'sine'); cam(a + 1.5, ZC, 40, 'cubic')
LENS = dict(at=ZC, zin=[a + 0.5, a + 1.5], open=[a + 0.75, a + 1.25], sharp=a + 1.5, shave=[a + 2.5, a + 4.0], lbl=a + 3.25, lbl2=a + 4.25, out=[a + 6.0, a + 7.0], zmax=40)
sfx(a + 0.5, 'riser', dur=1.0); sfx(a + 1.25, 'boom'); sfx(a + 2.5, 'shave', dur=1.5); sfx(a + 6.0, 'pullout', dur=1.0)
for txt_, at in [('方方正正的台阶', a + 1.5), ('棱角被削掉', a + 3.25), ('跳变变得迟缓', a + 4.25)]: SFX.append(dict(t=at, kind='label', text=txt_, rate=14))
cam(a + 6.0, ZC, 40, 'lin'); cam(a + 7.0, SC('tail'), SZ('tail'), 'cubic'); T[0] = a + 7.0; arrive('tail'); hold(0.5)
mark('B5', 'hl', '跳变变得迟缓', 0.625); mark('B6', 'hl', '拖出一条尾巴', 0.75); mark('B7', 'hl', '压到后面的比特身上', 0.75); mark('B9', 'hl', '码间干扰', 0.5); hold(0.375)
string('tail-K4', edge('B9'), ctop('K4', 250)); go(PC('K4', 0, 0), 1.1)
t0 = now(); CUE['K4'] = dict(t0=t0, single=t0 + 0.25, morph=[t0 + 1.0, t0 + 1.75], seq=t0 + 3.0, sum=t0 + 4.25, ask=t0 + 5.25, end=t0 + 7.0)
clabel('K4', '一个比特：拖出一条尾巴', -390, -440, t0 + 1.75, align='left'); clabel('K4', '尾巴压到后面的比特上', -390, 30, t0 + 3.5, align='left', bg='red')
clabel('K4', '叠在一起：码间干扰', 390, 470, t0 + 4.5, align='right', bg='red')
sfx(t0 + 0.25, 'thock'); sfx(t0 + 1.0, 'shave', dur=0.75); sfx(t0 + 3.0, 'pairs'); sfx(t0 + 4.25, 'blur'); sfx(t0 + 5.25, 'wrong'); hold(7.0)
# --- 两件事叠加 → 越快、越远 ---
string('K4-sum', cbot('K4', -250), edge('S1', 'r')); gostack('sum', 2.0, 'sine', 0.12)
mark('S1', 'hl', '两件事叠加', 0.625); mark('S2', 'hl', '一片起伏的波浪', 0.75); mark('S3', 'hl', '很难判断', 0.5); mark('S4', 'hl', '0还是1', 0.5); hold(0.375)
gostack('far')
mark('F1', 'hl', '越远', 0.25); mark('F2', 'hl', '一路累积', 0.5); mark('F3', 'hl', '越快', 0.25); mark('F4', 'hl', '时间减半', 0.5); mark('F5', 'hl', '更窄', 0.25)
mark('F6', 'hl', '并不会跟着变短', 0.75); mark('F7', 'hl', '压到更多后面的比特上', 0.875); mark('F8', 'hl', '尾巴本身也更重', 0.75); hold(0.375)
string('far-K6', edge('F8'), ctop('K6', 250)); go(PC('K6', 0, 0), 1.12)
t0 = now(); CUE['K6'] = dict(t0=t0, rowA=t0 + 0.25, rowB=t0 + 1.75, hitA=t0 + 1.0, hitB=t0 + 2.75, end=t0 + 5.5)
clabel('K6', '原来', -390, -400, t0 + 0.25, align='left'); clabel('K6', '快一倍：台阶更窄，尾巴还那么长', -390, 0, t0 + 1.75, align='left', size=38)
clabel('K6', '压到更多比特上，尾巴也更重', 390, 400, t0 + 3.0, align='right', bg='red', size=38)
sfx(t0 + 0.25, 'thock'); sfx(t0 + 1.75, 'thock'); sfx(t0 + 3.0, 'wrong'); hold(5.5)
# --- 跑得越快，可靠距离越短 → 换乘光 ---
string('K6-reach', cbot('K6', 250), edge('R1', 'l')); gostack('reach', 2.0, 'sine', 0.12)
mark('R1', 'hl', '跑得越快', 0.5); mark('R2', 'hl', '距离就越短', 0.625); mark('R3', 'hl', '换乘光', 0.5); hold(0.375)
string('reach-K7', edge('R3'), ctop('K7', 250)); go(PC('K7', 0, 0), 1.15)
t0 = now(); CUE['K7'] = dict(t0=t0, slow=t0, fast=t0 + 1.0, end=t0 + 3.5)
clabel('K7', '慢：能可靠地跑很远', -400, -235, t0, align='left', size=38); clabel('K7', '快：没多远就糊了', -400, 5, t0 + 1.0, align='left', bg='red', size=38)
clabel('K7', '所以：换乘光', 400, 245, t0 + 2.0, align='right', size=40)
sfx(t0, 'reach'); sfx(t0 + 1.0, 'reach2'); hold(3.5)
# --- 三种思路：修短、修好 ---
string('K7-fix', cbot('K7', -250), edge('X0', 'r')); gostack('fix', 2.0, 'sine', 0.12)
mark('X0', 'hl', '三种思路', 0.5); mark('X1', 'hl', '把路修短', 0.5); mark('X2', 'hl', '离得更近', 0.5); mark('X3', 'hl', '把路修好', 0.5); mark('X4', 'hl', '损耗更低', 0.5); mark('X4b', 'hl', '更好的铜缆', 0.5); hold(0.375)
string('fix-K8', edge('X4'), ctop('K8', 250)); go(PC('K8', 0, 0), 1.12)
t0 = now(); CUE['K8'] = dict(t0=t0, rows=[t0 + 0.25, t0 + 1.75, t0 + 3.25], end=t0 + 5.75)
clabel('K8', '原来：路长，到了就糊', -390, -440, t0 + 0.5, align='left', bg='red', size=38); clabel('K8', '修短：芯片离得更近', -390, -110, t0 + 2.0, align='left', size=38)
clabel('K8', '修好：损耗更低的板材、铜缆', -390, 220, t0 + 3.5, align='left', size=38)
for tt in CUE['K8']['rows']: sfx(tt, 'thock')
hold(5.75)
# --- 三，在路上修信号（检修站）---
string('K8-fix3', cbot('K8', 250), edge('X5', 'l')); gostack('fix3', 2.0, 'sine', 0.12)
mark('X5', 'hl', '在路上修信号', 0.625); mark('X6', 'hl', '中途设检修站', 0.625); mark('X7', 'hl', '重新认出来、整理干净', 0.875); mark('X8', 'hl', '能力范围', 0.5); mark('X10', 'hl', '修不回来了', 0.625); hold(0.375)
string('fix3-K9', edge('X10'), ctop('K9', 250)); go(PC('K9', 0, 0), 1.12)
t0 = now(); CUE['K9'] = dict(t0=t0, ok=t0 + 0.25, bad=t0 + 3.0, end=t0 + 6.0)
clabel('K9', '中途设检修站：认出来、整理干净', -390, -420, t0 + 1.25, align='left', size=38); clabel('K9', '模糊到一定程度：修不回来', -390, 400, t0 + 4.25, align='left', bg='red', size=38)
sfx(t0 + 1.25, 'dsp'); sfx(t0 + 4.25, 'wrong'); hold(6.0)
# --- 电的路并没有被淘汰 ---
string('K9-copper', cbot('K9', -250), edge('Y1', 'r')); gostack('copper', 2.0, 'sine', 0.12)
mark('Y1', 'hl', '并没有被淘汰', 0.625); mark('Y2', 'hl', '便宜、可靠', 0.5); mark('Y2', 'hl', '不需要电光转换', 0.625); mark('Y3', 'hl', '机柜内', 0.375); mark('Y4', 'hl', '依然大量使用', 0.5)
mark('Y5', 'hl', '铜线力不从心的那一段', 0.75); hold(0.375)
string('copper-K10', edge('Y5'), ctop('K10', 250)); go(PC('K10', 0, 0), 1.12)
t0 = now(); CUE['K10'] = dict(t0=t0, copper=t0 + 0.25, limit=t0 + 1.75, light=t0 + 2.5, end=t0 + 5.0)
clabel('K10', '铜线：便宜、可靠，机柜内的短距离', -390, -260, t0 + 0.75, align='left', size=36); clabel('K10', '光：接手铜线力不从心的那一段', 390, 230, t0 + 2.75, align='right', size=36)
sfx(t0 + 0.25, 'thock'); sfx(t0 + 1.75, 'blur'); sfx(t0 + 2.5, 'laser'); hold(5.0)
# --- 从投资角度 ---
string('K10-inv', cbot('K10', 250), edge('V1', 'l')); gostack('inv', 2.0, 'sine', 0.12)
mark('V1', 'hl', '损耗', 0.375); mark('V2', 'hl', '分贝（dB）', 0.5); mark('V3', 'hl', '数字越大', 0.5); mark('V3', 'hl', '信号衰减得越', 0.5); mark('V4', 'hl', '严重', 0.25)
mark('V5', 'hl', '代表不了全部路况', 0.75); mark('V6', 'hl', '在什么频率下测得的', 0.75); hold(0.375)
gostack('ask')
mark('Q1b', 'hl', '能跑200G', 0.75); MARKS[-1]['segs'][-1][2] = round(MARKS[-1]['segs'][-1][2] + INS_W, 2); mark('Q2', 'under', '每条通道的速度', 0.5); mark('Q3', 'under', '多大损耗、什么条件', 0.625); mark('Q4', 'under', '出错率多少', 0.5); mark('Q5', 'under', '每个比特花多少电', 0.5)
mark('Q6', 'hl', '速度只是结果', 0.5); hold(0.375)
string('ask-K11', edge('Q6'), ctop('K11', 250)); go(PC('K11', 0, 0), 1.12)
t0 = now(); CUE['K11'] = dict(t0=t0, claim=t0 + 0.25, qs=[t0 + 1.0, t0 + 1.5, t0 + 2.0, t0 + 2.5], res=t0 + 3.25, end=t0 + 5.0)
for tt in [t0 + 0.25] + CUE['K11']['qs']: sfx(tt, 'stick', n=2)
sfx(t0 + 3.25, 'click'); hold(5.0)
# --- 收尾：拉回全桌 → 一句话带走 ---
allx = [c['at'][0] for c in CLIPS.values()] + [c['at'][0] for c in CARDS.values()]; ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
go([OVER['x'], OVER['y']], OVER['z'], 2.0, 'cubic', 0.16); hold(0.75, 0.03)
gostack('end', 2.0, 'cubic', 0.10, dy=-40)
mark('E1', 'hl', '变弱、拖尾', 0.625); mark('E2', 'hl', '越快、越远就越难认清', 0.875); mark('E3', 'hl', '把路修短、把路修好', 0.875); mark('E4', 'hl', '在路上修信号', 0.625)
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
eb = STACKS['end']['bb']; label('下一篇：路上的检修站', [SC('end')[0], eb[3] + 75], now() + 0.5, size=28, r=-0.01)
label('白话光互连 · 03', rightof('E0'), now() + 1.0, size=24, align='left', bg='red', r=-0.02)
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
json.dump(out, open(os.path.join(ROOT, '代码工程/ep3/desk.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('desk.json', DUR, 's,', len(CLIPS), 'strips,', len(PRINTS), 'prints,', len(MARKS), 'marks,', len(CAM), 'cam keys,', len(SFX), 'sfx;', 'z:', {k: v['z'] for k, v in STACKS.items()})
