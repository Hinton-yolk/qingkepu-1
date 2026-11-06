# 白话光互连 01 · Vox 完整版 —— 桌面布局与时间表（唯一的真源）
# 运行：python3 tools/build_desk.py → 代码工程/full/desk.json（画面读）＋ 配乐读同一份
# 剪报上的标注（荧光笔/红圈/下划线）按原文 PDF 的逐字坐标（素材/chars2.json）定位；所有时间点落在 120 BPM 的十六分音符格（0.125 s）上。
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CH = {int(k): v for k, v in json.load(open(os.path.join(ROOT, '素材/chars2.json'), encoding='utf-8')).items()}
K = 2.5

# ---------- 原文找字 ----------
def find(page, phrase, occ=0):
    cs = CH[page]; text = ''.join(c[0] for c in cs); ph = phrase.replace(' ', '')
    i = -1
    for _ in range(occ + 1):
        i = text.find(ph, i + 1)
        if i < 0: raise SystemExit(f'找不到「{phrase}」(p{page}, 第{occ}处)')
    run = cs[i:i + len(ph)]; segs = []
    for c in run:
        if segs and abs(segs[-1]['base'] - c[3]) < 2: segs[-1]['x1'] = c[2]
        else: segs.append({'x0': c[1], 'x1': c[2], 'base': c[3], 'size': c[4]})
    return [[round(s['x0'], 2), round(s['base'] - 0.93 * s['size'], 2), round(s['x1'], 2), round(s['base'] + 0.24 * s['size'], 2)] for s in segs]
def center(segs): s = segs[0]; return ((s[0] + s[2]) / 2, (s[1] + s[3]) / 2)

# ---------- 桌面 ----------
CLIPS = {
  'T':   dict(src='assets/clipT.png', page=1, crop=[62, 86, 408, 114], at=[-150, 0], r=-0.03, seed=11),
  'I':   dict(src='assets/cI.png',    page=1, crop=[62, 135, 552, 213], at=[0, 230], r=0.012, seed=12),
  'S1':  dict(src='assets/cS1.png',   page=1, crop=[62, 298, 552, 358], at=[1700, 60], r=0.015, seed=13),
  'S2':  dict(src='assets/cS2.png',   page=1, crop=[62, 622, 552, 722], at=[1700, 1900], r=-0.015, seed=14),
  'S2b': dict(src='assets/cS2b.png',  page=2, crop=[62, 67, 552, 118], at=[1700, 3500], r=0.015, seed=15),
  'S2c': dict(src='assets/cS2c.png',  page=2, crop=[62, 137, 470, 160], at=[1640, 4900], r=-0.02, seed=16),
  'S3':  dict(src='assets/cS3.png',   page=2, crop=[62, 346, 552, 460], at=[0, 3500], r=-0.018, seed=17),
  'S4':  dict(src='assets/cS4.png',   page=3, crop=[62, 68, 552, 127], at=[0, 5400], r=0.012, seed=18),
  'S4b': dict(src='assets/cS4b.png',  page=3, crop=[62, 129, 556, 183], at=[0, 6950], r=-0.012, seed=19),
  'S5':  dict(src='assets/cS5.png',   page=3, crop=[62, 392, 552, 474.5], at=[1700, 6300], r=0.015, seed=20),
  'E':   dict(src='assets/clipC.png', page=4, crop=[62, 67, 552, 127], at=[1100, 8400], r=-0.015, seed=41),
}
CARDS = {
  'G':   dict(kind='gpu',      at=[0, 880],    w=900, h=760,  r=-0.01),
  'C1':  dict(kind='serdes',   at=[1700, 720], w=900, h=1000, r=-0.008),
  'C2a': dict(kind='blur',     at=[1700, 2700], w=900, h=760, r=0.008),
  'C2b': dict(kind='dsp',      at=[1700, 4100], w=900, h=860, r=-0.01),
  'C2c': dict(kind='reach',    at=[1700, 5450], w=900, h=600, r=0.01),
  'C3':  dict(kind='transfer', at=[0, 4330],   w=900, h=1150, r=0.008),
  'C4a': dict(kind='race',     at=[0, 6060],   w=900, h=950,  r=-0.008),
  'C4b': dict(kind='align',    at=[0, 7500],   w=900, h=700,  r=0.01),
  'C5':  dict(kind='arrive',   at=[1700, 7020], w=900, h=1100, r=-0.008),
}
def rot(x, y, r): return [x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)]
def P(cid, px, py):
    c = CLIPS[cid]; x0, y0, x1, y1 = c['crop']; w, h = x1 - x0, y1 - y0
    rx, ry = rot((px - x0) * K - w * K / 2, (py - y0) * K - h * K / 2, c['r']); return [round(c['at'][0] + rx, 1), round(c['at'][1] + ry, 1)]
def PC(cid, cx, cy):
    c = CARDS[cid]; rx, ry = rot(cx, cy, c['r']); return [round(c['at'][0] + rx, 1), round(c['at'][1] + ry, 1)]
def PH(cid, phrase, occ=0, dx=0, dy=0):            # 剪报上一句话的中心 → 世界
    cx, cy = center(find(CLIPS[cid]['page'], phrase, occ)); return P(cid, cx + dx, cy + dy)

MARKS, LABELS, STRINGS, CAM, SFX = [], [], [], [], []
def mark(cid, kind, phrase, a, b, occ=0, seed=1):
    segs = find(CLIPS[cid]['page'], phrase, occ); MARKS.append(dict(clip=cid, kind=kind, segs=segs, t=[a, b], seed=seed))
    SFX.append(dict(t=a, kind='marker' if kind == 'hl' else 'pen', dur=b - a))
def label(text, xy, at, size=30, align='center', r=0.0, bg=None, fg=None, rate=14):
    LABELS.append(dict(text=text, x=xy[0], y=xy[1], at=at, size=size, align=align, r=r, bg=bg, fg=fg, rate=rate))
    SFX.append(dict(t=at, kind='label', text=text, rate=rate))
def string(key, a, b, t0, t1, sag=0.06, route=False):
    STRINGS.append(dict(key=key, a=a, b=b, t=[t0, t1], sag=sag, route=route)); SFX.append(dict(t=t0, kind='string', dur=t1 - t0))
def cam(t, xy, z, e='sine'):
    CAM.append(dict(t=t, x=xy[0], y=xy[1], z=z, e=e))
def sfx(t, kind, **kw): SFX.append(dict(t=t, kind=kind, **kw))
CARD_LABELS = {k: [] for k in CARDS}
def clabel(cid, text, cx, cy, at, size=40, align='center', bg='cream', r=0.0, rate=14):
    CARD_LABELS[cid].append(dict(text=text, x=cx, y=cy, at=at, size=size, align=align, bg=bg, r=r, rate=rate)); SFX.append(dict(t=at, kind='label', text=text, rate=rate))
CUE = {}

# 站点贴纸 ①–⑤（贴在每站第一张剪报左上，远景也认得出）
STICK = {1: P('S1', 46, 305), 2: P('S2', 46, 630), 3: P('S3', 566, 353), 4: P('S4', 46, 75), 5: P('S5', 46, 399)}
OVER = dict(x=850, y=4220, z=0.2155)
ZOOM_CHAR = PH('S4b', '芯只有', 0, dx=-11.04)      # 「芯」字：Kurzgesagt 钻进去的那一点（该词组中心往左一格）
ZOOM_CHAR = (lambda s: P('S4b', s[0][0] + 5.5, (s[0][1] + s[0][3]) / 2))(find(3, '芯只有'))

# ======================= 时间表 =======================
# --- 钩子：第③站那张剪报 ---
label('AI 机房为啥要换成光？', P('S3', 178, 334), 0.0, size=30, r=-0.025, rate=20)
mark('S3', 'hl', '不是光跑得更快', 0.25, 1.75, seed=2)
mark('S3', 'circle', '更适合高速、长距离', 2.5, 3.25, seed=3)
cam(0.0, PH('S3', '不是光跑得更快', dy=0), 2.55, 'lin'); cam(1.75, PH('S3', '不是光跑得更快', dy=-1), 2.6, 'lin')
cam(2.5, PH('S3', '更适合高速、长距离', dy=-2), 2.4); cam(3.5, PH('S3', '更适合高速、长距离', dy=-2), 2.42, 'lin')
# 大幅拉开、飞到桌面最上方的标题（Kurzgesagt 式：拉远 → 平移 → 推近）
cam(4.375, [500, 1700], 0.36, 'cubic'); cam(5.25, P('T', 235, 100), 1.2, 'cubic'); sfx(3.5, 'whoosh', dur=1.75, g=0.16)
# --- 开场：标题、背景 ---
mark('T', 'hl', '一个比特的旅程', 5.5, 6.5, seed=4)
cam(6.5, P('T', 236, 100), 1.22, 'lin')
cam(7.25, PH('I', '成千上万颗 GPU 一起算', dy=8), 2.2)
mark('I', 'hl', '成千上万颗 GPU 一起算', 7.25, 8.5, seed=5)
cam(8.5, PH('I', '互相交换结果', dy=8), 2.2, 'sine'); mark('I', 'hl', '互相交换结果', 8.5, 9.5, seed=6)
cam(9.5, PH('I', '互相交换结果', dy=8), 2.22, 'lin')
string('I-G', P('I', 470, 160), PC('G', 0, -380 + 30), 9.5, 10.25, 0.05)
cam(10.25, PC('G', 0, -20), 3.6, 'long'); cam(11.25, PC('G', 0, 10), 1.15, 'cubic')          # Kurzgesagt 式：贴着一颗芯片 → 拉开看到一整片
CUE['G'] = dict(x=[10.5, 11.5, 12.5])
clabel('G', '每算一步，都要交换结果', 0, 300, 11.75, size=42)
for t in CUE['G']['x']: sfx(t, 'exchange')
cam(13.0, PC('G', 0, 10), 1.17, 'lin')
cam(13.75, PH('I', '还要“说得快”', dy=-6), 2.0, 'long')
mark('I', 'hl', '还要“说得快”', 13.75, 14.875, seed=7)
cam(15.0, PH('I', '这就是光互连', dy=-6), 2.0, 'sine'); mark('I', 'circle', '光互连', 15.0, 15.75, occ=2, seed=8)
cam(16.25, PH('I', '这就是光互连', dy=-6), 2.02, 'lin')
# --- 五站路线：拉到全桌，红线依次连起五站 ---
cam(17.25, [OVER['x'], OVER['y']], OVER['z'], 'cubic'); sfx(16.25, 'whoosh', dur=1.0, g=0.14)
label('跟着一个比特，走五站', [300, 1520], 17.25, size=150, r=-0.015)
EXITS = {0: P('I', 520, 205), 1: PC('C1', 300, 470), 2: PC('C2c', -440, 120), 3: PC('C3', 300, 545), 4: PC('C4b', 440, -120), 5: PC('C5', -300, 520)}
POP = [17.5, 17.875, 18.25, 18.625, 19.0]
for i in range(5): string(f'route{i}', EXITS[i], STICK[i + 1], POP[i] - 0.375 + 0.0, POP[i], 0.04, route=True); sfx(POP[i], 'stick', n=i + 1)
HUD_IN = 17.25
# --- ① 出发 ---
TRAVEL = []
def travel(i, a, b): TRAVEL.append(dict(route=i, t=[a, b]))
cam(19.5, [OVER['x'], OVER['y']], OVER['z'] * 1.04, 'lin')
cam(21.0, PH('S1', '“一大排”并排放着', dy=-4), 2.3, 'cubic'); travel(0, 19.5, 21.0); sfx(19.5, 'whoosh', dur=1.5, g=0.14)
STATION = [(1, 21.0)]
mark('S1', 'hl', '“一大排”并排放着', 21.0, 22.25, seed=9)
cam(22.25, PH('S1', '出口有限', dy=-4), 2.3, 'sine'); mark('S1', 'hl', '出口有限', 22.25, 23.25, seed=10)
string('S1-C1', P('S1', 520, 336), PC('C1', 200, -470), 23.25, 24.0)
cam(24.0, PC('C1', 0, 0), 1.12, 'long'); sfx(23.25, 'whoosh', dur=0.75, g=0.08)
CUE['C1'] = dict(t0=24.0, go=24.5, end=28.5)
clabel('C1', 'GPU 里：一大排', -390, -448, 24.0, align='left'); clabel('C1', '出口有限', -330, -100, 24.75, bg='red', align='left')
clabel('C1', 'SerDes：排成一列', -390, 120, 25.5, align='left'); clabel('C1', '变成高速电信号', 390, 400, 27.0, align='right')
sfx(24.5, 'serdes', dur=3.0)
cam(28.5, PC('C1', 0, 10), 1.14, 'lin')
# --- ② 电的路 ---
STATION.append((2, 30.0)); travel(1, 28.5, 30.0)
cam(30.0, PH('S2', '速度越高、距离越远', dy=-4), 2.3, 'long'); sfx(28.5, 'whoosh', dur=1.5, g=0.12)
mark('S2', 'hl', '速度越高、距离越远，到达时就越模糊', 30.25, 31.75, seed=11)
cam(32.25, PH('S2', '分不清哪个是', dx=10, dy=-4), 2.3, 'sine')
mark('S2', 'under', '分不清哪个是0', 31.875, 32.375, seed=12)
cam(32.75, PH('S2', '分不清哪个是', dx=12, dy=-4), 2.3, 'lin')
string('S2-C2a', P('S2', 520, 712), PC('C2a', 200, -350), 32.75, 33.5)
cam(33.5, PC('C2a', 0, 0), 1.12, 'long'); sfx(32.75, 'whoosh', dur=0.75, g=0.08)
CUE['C2a'] = dict(t0=33.5, e0=33.5, end=38.0)
clabel('C2a', '出发时：清楚', -330, 210, 34.75, align='left'); clabel('C2a', '跑远了：糊了', 380, 210, 35.75, bg='red', align='right')
sfx(33.5, 'thock'); sfx(35.75, 'blur')
cam(38.0, PC('C2a', 0, 0), 1.14, 'lin')
cam(38.75, PH('S2b', '“检修站”', dy=0), 2.3, 'long'); sfx(38.0, 'whoosh', dur=0.75, g=0.08)
string('C2a-S2b', PC('C2a', -200, 360), P('S2b', 120, 70), 38.0, 38.75)
mark('S2b', 'hl', '“检修站”', 38.75, 39.5, seed=13)
cam(39.5, PH('S2b', '把模糊的信号重新认出来', dy=0), 2.3, 'sine'); mark('S2b', 'hl', '把模糊的信号重新认出来', 39.5, 40.5, seed=14)
cam(40.75, PH('S2b', 'DSP。检修要耗电', dy=0), 2.3, 'sine'); mark('S2b', 'under', 'DSP', 40.75, 41.125, seed=15)
mark('S2b', 'hl', '检修要耗电', 41.125, 42.0, seed=16)
cam(42.0, PH('S2b', 'DSP。检修要耗电', dy=0), 2.32, 'lin')
string('S2b-C2b', P('S2b', 300, 104), PC('C2b', 0, -400), 42.0, 42.75)
cam(42.75, PC('C2b', 0, 0), 1.12, 'long'); sfx(42.0, 'whoosh', dur=0.75, g=0.08)
CUE['C2b'] = dict(t0=42.75, groups=[43.5, 44.25, 45.0, 45.75], end=46.75)
clabel('C2b', '进站：糊的', -390, -250, 43.0, bg='red', align='left'); clabel('C2b', '出站：又清楚了', 390, -250, 43.75, align='right')
clabel('C2b', '每整理一组，耗一格电', 0, 330, 44.5)
for t in CUE['C2b']['groups']: sfx(t, 'dsp')
cam(46.75, PC('C2b', 0, 0), 1.14, 'lin')
cam(47.5, PH('S2c', '电的路能可靠覆盖', dy=0), 2.0, 'long'); sfx(46.75, 'whoosh', dur=0.75, g=0.08)
mark('S2c', 'hl', '速度越高，电的路能可靠覆盖的距离就越短。', 47.5, 48.75, seed=17)
cam(48.75, PH('S2c', '电的路能可靠覆盖', dy=0), 2.02, 'lin'); cam(49.25, PC('C2c', 0, 0), 1.15, 'long')
string('S2c-C2c', P('S2c', 300, 158), PC('C2c', 0, -270), 48.5, 49.25)
CUE['C2c'] = dict(t0=49.25, slow=49.25, fast=50.25, end=51.75)
clabel('C2c', '慢：能可靠地跑很远', -400, -235, 49.25, align='left', size=38); clabel('C2c', '快：没多远就糊了', -400, 5, 50.25, align='left', bg='red', size=38)
clabel('C2c', '所以：换乘', 400, 245, 51.0, align='right', size=40)
sfx(49.25, 'reach'); sfx(50.25, 'reach2')
cam(51.75, PC('C2c', 0, 0), 1.17, 'lin')
# --- ③ 换乘 ---
STATION.append((3, 53.25)); travel(2, 51.75, 53.25)
cam(53.25, PH('S3', '数据的载体从电换成了光', dy=0), 2.1, 'long'); sfx(51.75, 'whoosh', dur=1.5, g=0.12)
mark('S3', 'hl', '数据的载体从电换成了光', 53.5, 54.75, seed=18)
cam(55.0, PH('S3', '激光器发出一束稳定的光', dy=0), 2.1, 'sine'); mark('S3', 'hl', '激光器发出一束稳定的光', 55.0, 56.0, seed=19)
cam(56.375, PH('S3', '调制器按照', dx=60, dy=8), 1.9, 'sine')
mark('S3', 'under', '调制器', 56.25, 56.625, seed=20); mark('S3', 'hl', '一明一暗', 56.625, 57.25, seed=21); mark('S3', 'under', '驱动器', 57.25, 57.625, seed=22)
cam(57.75, PH('S3', '调制器按照', dx=62, dy=8), 1.92, 'lin')
string('S3-C3', P('S3', 520, 450), PC('C3', 200, -545), 57.75, 58.5)
cam(58.5, PC('C3', 0, 0), 1.12, 'long'); sfx(57.75, 'whoosh', dur=0.75, g=0.08)
CUE['C3'] = dict(t0=58.5, laser=58.5, mod=60.0, drv=61.75, hero=[63.25, 64.25], end=65.75)
clabel('C3', '激光器：一束稳定的光', -400, -470, 58.75, align='left'); clabel('C3', '调制器：1 亮，0 暗', -400, -40, 60.25, align='left')
clabel('C3', '驱动器：把电信号放大', -400, 300, 62.0, align='left'); clabel('C3', '还是 1，只换了载体', 400, 470, 64.5, align='right', bg='red')
sfx(58.5, 'laser'); sfx(60.0, 'mod', dur=3.0); sfx(61.75, 'amp'); sfx(64.0, 'flash')
cam(65.75, PC('C3', 0, 0), 1.14, 'lin')
# --- ④ 光的路 ---
STATION.append((4, 67.25)); travel(3, 65.75, 67.25)
cam(67.25, PH('S4', '光能比铜缆跑得远得多', dy=8), 2.0, 'long'); sfx(65.75, 'whoosh', dur=1.5, g=0.12)
mark('S4', 'hl', '光能比铜缆跑得远得多，信号依然清晰可辨', 67.375, 69.0, seed=23)
cam(69.0, PH('S4', '光能比铜缆跑得远得多', dy=8), 2.02, 'lin')
string('S4-C4a', P('S4', 520, 120), PC('C4a', 200, -475), 69.0, 69.75)
cam(69.75, PC('C4a', 0, -10), 1.12, 'long'); sfx(69.0, 'whoosh', dur=0.75, g=0.08)
t0 = 69.75
CUE['C4a'] = dict(t0=t0, heading=t0 - 0.25, tE0=t0, tL0=t0 + 1.0, morph=[t0 + 1.5, t0 + 2.0], tie=t0 + 2.25, end=t0 + 4.25)
clabel('C4a', '跑远了：认不清', 390, -355, t0 + 1.25, bg='red', align='right'); clabel('C4a', '光：一样快，还清楚', -370, 320, t0 + 2.75, align='left')
sfx(t0, 'thock'); sfx(t0 + 1.25, 'blur'); sfx(t0 + 1.5, 'morph'); sfx(t0 + 2.25, 'tie')
LABELS_TIE = t0 + 2.25 + 1 / 12
cam(t0 + 4.25, PC('C4a', 0, -10), 1.14, 'lin')
cam(74.75, PH('S4b', '芯只有头发丝的十分之一左右粗', dy=0), 2.3, 'long'); sfx(74.0, 'whoosh', dur=0.75, g=0.08)
string('C4a-S4b', PC('C4a', -200, 460), P('S4b', 120, 132), 74.0, 74.75)
mark('S4b', 'hl', '芯只有头发丝的十分之一左右粗', 74.75, 76.0, seed=24)
# Kurzgesagt：钻进「芯」这个字 → 镜头圈打开：光纤的芯 vs 头发丝 → 拉回剪报
cam(76.125, ZOOM_CHAR, 2.6, 'sine'); cam(77.0, ZOOM_CHAR, 40, 'cubic')
LENS = dict(at=ZOOM_CHAR, zin=[76.125, 77.0], open=[76.375, 76.875], core=77.0, hair=[77.25, 77.75], split=[78.0, 78.25], pairs=78.25, tenth=78.25, out=[79.5, 80.25], zmax=40)
cam(79.5, ZOOM_CHAR, 40, 'lin'); cam(80.25, PH('S4b', '接歪一点光就漏掉了', dy=0), 2.3, 'cubic')
sfx(76.125, 'riser', dur=0.75); sfx(76.875, 'boom'); sfx(78.25, 'pairs'); sfx(79.5, 'pullout', dur=0.75)
for (txt, at) in [('光纤的芯', 77.0), ('一根头发丝（截面）', 77.25), ('芯≈头发丝的1/10', 78.25)]: SFX.append(dict(t=at, kind='label', text=txt, rate=20 if '1/10' in txt else 14))
mark('S4b', 'hl', '接歪一点光就漏掉了', 80.25, 81.25, seed=25)
string('S4b-C4b', P('S4b', 300, 180), PC('C4b', 0, -330), 81.25, 82.0)
cam(81.25, PH('S4b', '接歪一点光就漏掉了', dy=0), 2.32, 'lin'); cam(82.0, PC('C4b', 0, 0), 1.15, 'long'); sfx(81.25, 'whoosh', dur=0.75, g=0.08)
CUE['C4b'] = dict(t0=82.0, slide=[83.75, 84.25], end=86.0)
clabel('C4b', '歪一点：光就漏了', -400, 230, 82.5, bg='red', align='left'); clabel('C4b', '对准了：光才进得去', 400, 230, 84.5, align='right')
sfx(82.25, 'leak', dur=1.5); sfx(83.75, 'slide'); sfx(84.25, 'click')
cam(86.0, PC('C4b', 0, 0), 1.17, 'lin')
# --- ⑤ 抵达 ---
STATION.append((5, 87.5)); travel(4, 86.0, 87.5)
cam(87.5, PH('S5', '感光元件把光的明暗重新变成电流', dy=0), 2.2, 'long'); sfx(86.0, 'whoosh', dur=1.5, g=0.12)
mark('S5', 'hl', '感光元件把光的明暗重新变成电流', 87.625, 88.875, seed=26)
cam(89.0, PH('S5', '非常微弱', dx=30, dy=0), 2.2, 'sine'); mark('S5', 'hl', '非常微弱', 88.875, 89.5, seed=27); mark('S5', 'under', '放大器', 89.5, 89.875, seed=28)
cam(90.0, PH('S5', '非常微弱', dx=32, dy=0), 2.22, 'lin')
string('S5-C5', P('S5', 520, 470), PC('C5', 200, -545), 90.0, 90.75)
cam(90.75, PC('C5', 0, 0), 1.12, 'long'); sfx(90.0, 'whoosh', dur=0.75, g=0.08)
CUE['C5'] = dict(t0=90.75, pd=90.75, amp=92.0, fan=[93.25, 94.75], end=96.0)
clabel('C5', '感光元件：光 → 电流', -400, -470, 91.0, align='left'); clabel('C5', '电流很弱，放大器放大', -400, -60, 92.25, align='left')
clabel('C5', '一列 → 一排，回到 GPU B', 400, 470, 94.0, align='right')
sfx(91.0, 'pd'); sfx(92.0, 'amp'); sfx(93.25, 'fan', dur=1.5)
cam(96.0, PC('C5', 0, 0), 1.14, 'lin')
# --- 收尾：拉回全桌 → 结论剪报 ---
cam(97.5, [OVER['x'], OVER['y'] + 120], OVER['z'], 'cubic'); sfx(96.0, 'whoosh', dur=1.5, g=0.16); STATION.append((6, 97.5))
string('route5', EXITS[5], P('E', 70, 70), 97.25, 98.0, 0.04, route=True)
cam(98.25, [OVER['x'], OVER['y'] + 120], OVER['z'] * 1.03, 'lin')
cam(99.25, PH('E', '所以数据要换乘光', dy=26), 2.45, 'long'); sfx(98.25, 'whoosh', dur=1.0, g=0.10)
mark('E', 'hl', '所以数据要换乘光', 99.25, 100.0, seed=29)
label('代价：电光转换 + 精密对接', P('E', 330, 146), 100.25, size=29, r=0.015)
label('下一篇：第一站 出发', P('E', 330, 171), 101.5, size=24, r=-0.01)
label('白话光互连 · 01', P('E', 330, 192), 102.0, size=20, bg='red', r=-0.02)
DUR = 104.0
cam(DUR, PH('E', '所以数据要换乘光', dy=27), 2.5, 'lin')

# ---------- 检查：时间点都在十六分音符格上 ----------
def ongrid(t): return abs(t * 8 - round(t * 8)) < 1e-6
bad = [(k, v) for k, v in [('cam', c['t']) for c in CAM] + [('mark', m['t'][0]) for m in MARKS] + [('label', l['at']) for l in LABELS] if not ongrid(v)]
assert not bad, bad
assert all(CAM[i]['t'] < CAM[i + 1]['t'] for i in range(len(CAM) - 1)), [c['t'] for c in CAM]
out = dict(dur=DUR, bpm=120, K=K, clips=CLIPS, cards=CARDS, cardLabels=CARD_LABELS, cue=CUE, marks=MARKS, labels=LABELS, strings=STRINGS, cam=CAM,
           stick=STICK, pops=POP, over=OVER, travel=TRAVEL, station=STATION, hudIn=HUD_IN, lens=LENS, tieLabel=LABELS_TIE, sfx=sorted(SFX, key=lambda s: s['t']))
json.dump(out, open(os.path.join(ROOT, '代码工程/full/desk.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('desk.json', DUR, 's,', len(MARKS), 'marks,', len(LABELS), 'labels,', len(CAM), 'cam keys,', len(SFX), 'sfx')
