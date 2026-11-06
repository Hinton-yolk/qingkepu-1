# 白话光互连 01 · Vox 完整版（第二版）—— 桌面布局与时间表（唯一的真源）
# 运行：python3 tools/build_desk.py → 代码工程/full/desk.json（画面读）＋ 配乐读同一份；同时把剪报短条裁到 代码工程/assets/strips/
# 第二版改动（用户反馈：镜头跟着字移动看不清、很多字在画面外）：
#   · 原文不再整段整行地裁：每句关键的话按原文的一行剪成一条短纸条（最长约 16 个字），叠成一摞贴在桌上——整摞都在画面里；
#   · 读字的时候镜头不动，只在「纸条 ↔ 卡片 ↔ 下一站」之间移动，每次 1.5–2 s；成片 60 fps。
# 标注（荧光笔/红圈/下划线）按原文 PDF 的逐字坐标（素材/chars2.json）定位；所有时间点落在 120 BPM 的十六分音符格（0.125 s）上。
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

MARKS, LABELS, STRINGS, CAM, SFX = [], [], [], [], []
def mark(cid, kind, phrase, a, b, seed=1):
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']
    run = [r for r in runs(c['page'], phrase) if x0 <= r[0][1] and r[-1][2] <= x1 and y0 <= r[0][3] <= y1]
    assert run, f'「{phrase}」不在短条 {cid} 里'
    MARKS.append(dict(clip=cid, kind=kind, segs=boxes(run[0]), t=[a, b], seed=seed)); SFX.append(dict(t=a, kind='marker' if kind == 'hl' else 'pen', dur=b - a))
def label(text, xy, at, size=30, align='center', r=0.0, bg=None, fg=None, rate=14):
    LABELS.append(dict(text=text, x=xy[0], y=xy[1], at=at, size=size, align=align, r=r, bg=bg, fg=fg, rate=rate)); SFX.append(dict(t=at, kind='label', text=text, rate=rate))
def string(key, a, b, t0, t1, sag=0.06, route=False):
    STRINGS.append(dict(key=key, a=a, b=b, t=[t0, t1], sag=sag, route=route)); SFX.append(dict(t=t0, kind='string', dur=t1 - t0))
def cam(t, xy, z, e='sine'): CAM.append(dict(t=t, x=xy[0], y=xy[1], z=z, e=e))
def hold(t, dz=0.02): last = CAM[-1]; cam(t, [last['x'], last['y']], round(last['z'] * (1 + dz), 4), 'lin')
def sfx(t, kind, **kw): SFX.append(dict(t=t, kind=kind, **kw))
CARD_LABELS = {k: [] for k in CARDS}
def clabel(cid, text, cx, cy, at, size=40, align='center', bg='cream', r=0.0, rate=14):
    CARD_LABELS[cid].append(dict(text=text, x=cx, y=cy, at=at, size=size, align=align, bg=bg, r=r, rate=rate)); SFX.append(dict(t=at, kind='label', text=text, rate=rate))
def move(t, xy, z, e='sine', g=0.08): sfx(CAM[-1]['t'], 'whoosh', dur=t - CAM[-1]['t'], g=g); cam(t, xy, z, e)
CUE = {}

def edge(cid, side='r', dy=0):   # 短条左/右边缘的中点（世界坐标）
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']; return P(cid, (x1 + 2) if side == 'r' else (x0 - 2), (y0 + y1) / 2 + dy)
def above(cid): c = CLIPS[cid]; w = (c['crop'][2] - c['crop'][0]) * c['k']; h = (c['crop'][3] - c['crop'][1]) * c['k']; return [round(c['at'][0] - w / 2 + 60, 1), round(c['at'][1] - h / 2 - 95, 1)]
STICK = {1: above('A0'), 2: above('B0'), 3: above('C0'), 4: above('F0'), 5: above('V0')}
OVER = dict(x=850, y=4380, z=0.208)
ZC = (lambda r: P('H1', r[0][1] + 5.5, r[0][3] - 4.5))(runs(3, '芯只有')[0])           # 「芯」字中心：Kurzgesagt 钻进去的那一点

# ======================= 时间表 =======================
# --- 钩子：第③站上半摞（标题 + 两条原话） ---
label('AI 机房为啥要换成光？', [SC('s3a')[0] + 40, STACKS['s3a']['bb'][1] - 215], 0.0, size=32, r=-0.02, rate=20)
mark('C1s', 'hl', '不是光跑得更快', 0.25, 1.75, seed=2)
mark('C2s', 'circle', '更适合高速、长距离', 2.25, 3.25, seed=3)
cam(0.0, SC('s3a', -60), 1.98, 'lin'); hold(4.0, 0.03)
cam(5.0, [500, 1700], 0.36, 'cubic'); cam(6.0, [0, 0], 1.2, 'cubic'); sfx(4.0, 'whoosh', dur=2.0, g=0.16)
# --- 开场 ---
mark(T, 'hl', '一个比特的旅程', 6.25, 7.5, seed=4); hold(7.75)
move(9.25, SC('intro'), SZ('intro'))
mark('I1', 'hl', '成千上万颗 GPU 一起算', 9.5, 10.75, seed=5); mark('I2', 'hl', '互相交换结果', 10.75, 11.75, seed=6); hold(12.0)
string('I-G', edge('I5', 'r'), PC('G', 300, -380 + 30), 12.0, 12.75, 0.05)
move(13.5, PC('G', 0, 10), 1.15)
CUE['G'] = dict(x=[13.75, 14.75, 15.75]); clabel('G', '每算一步，都要交换结果', 0, 300, 14.5, size=42)
for t in CUE['G']['x']: sfx(t, 'exchange')
hold(16.75)
move(18.25, SC('intro'), SZ('intro'))
mark('I3', 'hl', '还要“说得快”', 18.5, 19.5, seed=7); mark('I4', 'hl', '借助光来完成', 19.5, 20.5, seed=8); mark('I5', 'circle', '光互连', 20.75, 21.5, seed=9)
hold(22.25)
# --- 五站路线 ---
move(23.75, [OVER['x'], OVER['y']], OVER['z'], 'cubic', g=0.14)
label('跟着一个比特，走五站', [0, 2250], 24.0, size=150, r=-0.015)
EXITS = {0: edge('I5', 'r', 6), 1: PC('C1', 300, 470), 2: PC('C2c', -440, 120), 3: PC('C3', 300, 545), 4: PC('C4b', 440, -120), 5: PC('C5', -300, 520)}
POP = [24.5, 25.0, 25.5, 26.0, 26.5]
for i in range(5): string(f'route{i}', EXITS[i], STICK[i + 1], POP[i] - 0.5, POP[i], 0.04, route=True); sfx(POP[i], 'stick', n=i + 1)
HUD_IN = 24.0
hold(27.5, 0.04)
TRAVEL, STATION = [], []
def travel(i, a, b): TRAVEL.append(dict(route=i, t=[a, b]))
# --- ① 出发 ---
travel(0, 27.5, 29.5); move(29.5, SC('s1'), SZ('s1'), 'cubic', g=0.14); STATION.append((1, 29.5))
mark('A1', 'hl', '“一大排”并排放着', 29.75, 31.0, seed=10); mark('A2', 'hl', '出口有限', 31.0, 31.75, seed=11)
mark('A3', 'hl', '排成一列', 32.0, 32.75, seed=12); mark('A4', 'under', 'SerDes', 32.875, 33.375, seed=13); hold(34.0)
string('s1-C1', edge('A4', 'r'), PC('C1', 250, -470), 34.0, 34.75)
move(35.5, PC('C1', 0, 0), 1.12)
CUE['C1'] = dict(t0=35.5, go=36.0, end=40.75)
clabel('C1', 'GPU 里：一大排', -390, -448, 35.5, align='left'); clabel('C1', '出口有限', -330, -100, 36.25, bg='red', align='left')
clabel('C1', 'SerDes：排成一列', -390, 120, 37.0, align='left'); clabel('C1', '变成高速电信号', 390, 400, 38.5, align='right')
sfx(36.0, 'serdes', dur=3.4); hold(41.0)
# --- ② 电的路 ---
travel(1, 41.0, 43.0); move(43.0, SC('s2'), SZ('s2'), g=0.12); STATION.append((2, 43.0))
mark('B1', 'hl', '速度越高、距离越远', 43.25, 44.25, seed=14); mark('B2', 'hl', '到达时就越模糊', 44.25, 45.0, seed=15)
mark('B3', 'under', '分不清哪个是0', 45.25, 45.75, seed=16); hold(46.5)
string('s2-C2a', edge('B3', 'r'), PC('C2a', 250, -350), 46.5, 47.25)
move(48.0, PC('C2a', 0, 0), 1.12)
CUE['C2a'] = dict(t0=48.0, e0=48.0, end=53.0)
clabel('C2a', '出发时：清楚', -330, 210, 49.25, align='left'); clabel('C2a', '跑远了：糊了', 380, 210, 50.25, bg='red', align='right')
sfx(48.0, 'thock'); sfx(50.25, 'blur'); hold(53.5)
string('C2a-dsp', PC('C2a', -250, 360), edge('D1', 'l'), 53.5, 54.25)
move(55.0, SC('dsp'), SZ('dsp'))
mark('D1', 'hl', '“检修站”', 55.25, 56.0, seed=17); mark('D2', 'hl', '把模糊的信号重新认出来', 56.0, 57.0, seed=18)
mark('D3', 'under', 'DSP', 57.25, 57.625, seed=19); mark('D3', 'hl', '检修要耗电', 57.625, 58.5, seed=20); hold(59.0)
string('dsp-C2b', edge('D3', 'r'), PC('C2b', 250, -400), 59.0, 59.75)
move(60.5, PC('C2b', 0, 0), 1.12)
CUE['C2b'] = dict(t0=60.5, groups=[61.25, 62.0, 62.75, 63.5], end=64.75)
clabel('C2b', '进站：糊的', -390, -250, 60.75, bg='red', align='left'); clabel('C2b', '出站：又清楚了', 390, -250, 61.5, align='right')
clabel('C2b', '每整理一组，耗一格电', 0, 330, 62.25)
for t in CUE['C2b']['groups']: sfx(t, 'dsp')
hold(65.0)
string('C2b-reach', PC('C2b', -250, 430), edge('R1', 'l'), 65.0, 65.75)
move(66.5, SC('reach'), SZ('reach'))
mark('R1', 'hl', '速度越高', 66.75, 67.25, seed=21); mark('R2', 'hl', '电的路能可靠覆盖的距离就越短', 67.25, 68.5, seed=22); hold(69.0)
string('reach-C2c', edge('R2', 'r'), PC('C2c', 250, -270), 69.0, 69.75)
move(70.5, PC('C2c', 0, 0), 1.15)
CUE['C2c'] = dict(t0=70.5, slow=70.5, fast=71.5, end=73.5)
clabel('C2c', '慢：能可靠地跑很远', -400, -235, 70.5, align='left', size=38); clabel('C2c', '快：没多远就糊了', -400, 5, 71.5, align='left', bg='red', size=38)
clabel('C2c', '所以：换乘', 400, 245, 72.25, align='right', size=40)
sfx(70.5, 'reach'); sfx(71.5, 'reach2'); hold(73.75)
# --- ③ 换乘 ---
travel(2, 73.75, 75.75); move(75.75, SC('s3b', -40), SZ('s3b'), g=0.12); STATION.append((3, 75.75))
mark('C3s', 'hl', '数据的载体从电换成了光', 76.0, 77.0, seed=23); mark('C4s', 'hl', '激光器发出一束稳定的光', 77.25, 78.25, seed=24)
mark('C5s', 'under', '调制器', 78.5, 78.875, seed=25); mark('C6s', 'hl', '一明', 79.0, 79.25, seed=26); mark('C7s', 'hl', '一暗', 79.25, 79.5, seed=27)
mark('C8s', 'under', '驱动器', 79.75, 80.125, seed=28); hold(80.75)
string('s3-C3', edge('C8s', 'r'), PC('C3', 250, -545), 80.75, 81.5)
move(82.25, PC('C3', 0, 0), 1.12)
CUE['C3'] = dict(t0=82.25, laser=82.25, mod=83.75, drv=85.5, hero=[87.0, 88.0], end=90.0)
clabel('C3', '激光器：一束稳定的光', -400, -470, 82.5, align='left'); clabel('C3', '调制器：1 亮，0 暗', -400, -40, 84.0, align='left')
clabel('C3', '驱动器：把电信号放大', -400, 300, 85.75, align='left'); clabel('C3', '还是 1，只换了载体', 400, 470, 88.25, align='right', bg='red')
sfx(82.25, 'laser'); sfx(83.75, 'mod', dur=3.0); sfx(85.5, 'amp'); sfx(87.75, 'flash'); hold(90.25)
# --- ④ 光的路 ---
travel(3, 90.25, 92.25); move(92.25, SC('s4'), SZ('s4'), g=0.12); STATION.append((4, 92.25))
mark('F1', 'hl', '光能比铜缆跑得远得多，信号依', 92.5, 93.75, seed=29); mark('F2', 'hl', '然清晰可辨', 93.75, 94.25, seed=30); hold(95.0)
string('s4-C4a', edge('F2', 'r'), PC('C4a', 250, -475), 95.0, 95.75)
move(96.5, PC('C4a', 0, -10), 1.12)
t0 = 96.5
CUE['C4a'] = dict(t0=t0, heading=t0 - 0.25, tE0=t0, tL0=t0 + 1.0, morph=[t0 + 1.5, t0 + 2.0], envE=t0 + 2.25, envL=t0 + 2.875, end=t0 + 4.5)
clabel('C4a', '电：越跑越弱、越乱', 390, -355, t0 + 1.25, bg='red', align='right'); clabel('C4a', '光：损耗少，更稳定', -370, 320, t0 + 3.125, align='left')
sfx(t0, 'thock'); sfx(t0 + 1.25, 'blur'); sfx(t0 + 1.5, 'morph'); sfx(t0 + 2.25, 'envE'); sfx(t0 + 2.875, 'envL')
LABELS_TIE = t0 + 2.25 + 1 / 12
hold(t0 + 4.75)
string('C4a-s4b', PC('C4a', -250, 470), edge('H1', 'l'), 101.25, 102.0)
move(102.75, SC('s4b'), SZ('s4b'))
mark('H1', 'hl', '芯只有头发丝的十分之一左右粗', 103.0, 104.25, seed=31); hold(104.5)
# Kurzgesagt：钻进「芯」字 → 镜头圈打开：光纤的芯 vs 头发丝 → 拉回
cam(105.0, ZC, 2.7, 'sine'); cam(106.0, ZC, 40, 'cubic')
LENS = dict(at=ZC, zin=[105.0, 106.0], open=[105.25, 105.75], core=106.0, hair=[106.25, 106.75], split=[107.0, 107.25], pairs=107.25, tenth=107.25, out=[109.0, 110.0], zmax=40)
cam(109.0, ZC, 40, 'lin'); cam(110.0, SC('s4b'), SZ('s4b'), 'cubic')
sfx(105.0, 'riser', dur=1.0); sfx(105.75, 'boom'); sfx(107.25, 'pairs'); sfx(109.0, 'pullout', dur=1.0)
for (txt, at) in [('光纤的芯', 106.0), ('一根头发丝（截面）', 106.25), ('芯≈头发丝的1/10', 107.25)]: SFX.append(dict(t=at, kind='label', text=txt, rate=20 if '1/10' in txt else 14))
mark('H3', 'hl', '接歪一点光就漏掉了', 110.25, 111.25, seed=32); hold(111.75)
string('s4b-C4b', edge('H3', 'r'), PC('C4b', 250, -330), 111.75, 112.5)
move(113.25, PC('C4b', 0, 0), 1.15)
CUE['C4b'] = dict(t0=113.25, slide=[115.0, 115.5], end=117.25)
clabel('C4b', '歪一点：光就漏了', -400, 230, 113.75, bg='red', align='left'); clabel('C4b', '对准了：光才进得去', 400, 230, 115.75, align='right')
sfx(113.5, 'leak', dur=1.5); sfx(115.0, 'slide'); sfx(115.5, 'click'); hold(117.5)
# --- ⑤ 抵达 ---
travel(4, 117.5, 119.5); move(119.5, SC('s5'), SZ('s5'), g=0.12); STATION.append((5, 119.5))
mark('V1', 'hl', '感光元件把光的明暗重新变成电流', 119.75, 121.0, seed=33); mark('V2', 'hl', '非常微弱', 121.0, 121.75, seed=34)
mark('V3', 'under', '放大器', 122.0, 122.375, seed=35); hold(123.0)
string('s5-C5', edge('V3', 'r'), PC('C5', 250, -545), 123.0, 123.75)
move(124.5, PC('C5', 0, 0), 1.12)
CUE['C5'] = dict(t0=124.5, pd=124.5, amp=125.75, fan=[127.0, 128.5], end=129.75)
clabel('C5', '感光元件：光 → 电流', -400, -470, 124.75, align='left'); clabel('C5', '电流很弱，放大器放大', -400, -60, 126.0, align='left')
clabel('C5', '一列 → 一排，回到 GPU B', 400, 470, 127.75, align='right')
sfx(124.75, 'pd'); sfx(125.75, 'amp'); sfx(127.0, 'fan', dur=1.5); hold(130.0)
move(131.5, SC('s5'), SZ('s5'))
mark('V4', 'hl', '光变回电，一列变回一排', 131.75, 132.75, seed=36); hold(133.25)
# --- 收尾：拉回全桌 → 一句话带走 ---
move(135.25, [OVER['x'], OVER['y']], OVER['z'], 'cubic', g=0.16); STATION.append((6, 135.25))
string('route5', EXITS[5], edge('E0', 'l'), 135.25, 136.0, 0.04, route=True)
hold(136.25, 0.03)
move(138.25, SC('end'), SZ('end'), 'cubic', g=0.10)
mark('E3', 'hl', '所以数据要换乘光', 138.5, 139.25, seed=37); mark('E4', 'under', '电光转换', 139.5, 139.875, seed=38); mark('E5', 'under', '精密对接', 139.875, 140.25, seed=39)
eb = STACKS['end']['bb']
label('下一篇：第一站 出发', [SC('end')[0], eb[3] + 70], 140.75, size=26, r=-0.01)
label('白话光互连 · 01', [SC('end')[0], eb[3] + 140], 141.25, size=22, bg='red', r=-0.02)
DUR = 144.0
hold(DUR, 0.03)

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
for m in MARKS:      # 读字时镜头不动，而且整条都在画面里（顶部进度条以下）
    a, b = camseg(m['t'][0] + 0.01)
    assert b['e'] == 'lin', f"标注 {m['clip']} {m['t']} 时镜头在动"
    if m['clip'] == T: continue
    for tt in m['t']:
        k = cam_state(tt); c = CLIPS[m['clip']]; w = (c['crop'][2] - c['crop'][0]) * c.get('k', K)
        sx0 = (c['at'][0] - w / 2 - k['x']) * k['z'] + 540; sx1 = (c['at'][0] + w / 2 - k['x']) * k['z'] + 540; sy = (c['at'][1] - k['y']) * k['z'] + 960
        assert sx0 > 20 and sx1 < 1060 and 200 < sy < 1860, f"{m['clip']}「{c['text']}」读的时候不在画面里：x {sx0:.0f}–{sx1:.0f}, y {sy:.0f}"
out = dict(dur=DUR, bpm=120, K=K, clips=CLIPS, cards=CARDS, cardLabels=CARD_LABELS, cue=CUE, marks=MARKS, labels=LABELS, strings=STRINGS, cam=CAM,
           stick=STICK, pops=POP, over=OVER, travel=TRAVEL, station=STATION, hudIn=HUD_IN, lens=LENS, tieLabel=LABELS_TIE, stacks=STACKS, sfx=sorted(SFX, key=lambda s: s['t']))
json.dump(out, open(os.path.join(ROOT, '代码工程/full/desk.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('desk.json', DUR, 's,', len(CLIPS), 'strips,', len(MARKS), 'marks,', len(CAM), 'cam keys,', len(SFX), 'sfx;', 'stack z:', {k: v['z'] for k, v in STACKS.items()})
