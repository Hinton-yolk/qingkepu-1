# 白话光互连 · Vox 风格样片 —— 原创配乐与音效（代码合成）
# 120 BPM，21.5 s，A 小调 → 结尾落 C 大调。时间点读 ../代码工程/vox/cues.json（和画面同一份）。
# 桌面段：木质拨弦八分音符＋轻踩；卡片段（3b1b）：玻璃琶音十六分音符；钻进光纤（Kurzgesagt）：上升音 → 低频一沉、只留空气感铺底；
# 拉回桌面：反向呼啸；结论：落 C 大调。纸上的动作（荧光笔、红笔、红线、标签打字）都按画面的 12fps 步进做颗粒。
# 产出 score.wav、beats.json
import json, wave, numpy as np
from scipy.signal import butter, lfilter

Q = json.load(open('../代码工程/vox/cues.json', encoding='utf-8'))
SR, BPM, DUR = 48000, Q['bpm'], Q['dur']
BEAT = 60 / BPM; N = int(SR * DUR); NB = int(round(DUR / BEAT))
rs = np.random.default_rng(7)
mus = np.zeros((2, N)); fx = np.zeros((2, N))
json.dump({'bpm': BPM, 'seconds': DUR, 'beats': [round(i * BEAT, 3) for i in range(NB)], 'downbeats': [round(i * BEAT, 3) for i in range(0, NB, 4)],
           'cues': {k: v for k, v in Q.items() if k != '_'}}, open('beats.json', 'w'), indent=1, ensure_ascii=False)

def add(buf, sig, t, g=1.0, pan=0.0):
    i0 = int(round(t * SR)); l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
    if i0 >= N or i0 + len(sig) <= 0: return
    a, b = max(0, i0), min(N, i0 + len(sig)); s = sig[a - i0:b - i0]
    buf[0, a:b] += s * g * l; buf[1, a:b] += s * g * r
def T(d): return np.arange(int(d * SR)) / SR
def env(n, a, d): e = np.exp(-np.arange(n) / (d * SR)); k = max(1, int(a * SR)); e[:k] *= np.linspace(0, 1, k); return e
def lp(x, fc, o=2): b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def bp(x, lo, hi, o=2): b, a = butter(o, [lo / (SR / 2), min(hi, SR / 2 - 200) / (SR / 2)], 'band'); return lfilter(b, a, x)
def noise(n): return rs.standard_normal(n)
def midi(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, t): return 2 * ((f * t) % 1) - 1
def fade(x, a=0.01, b=0.05):
    ka, kb = int(a * SR), int(b * SR); x = x.copy()
    if ka: x[:ka] *= np.linspace(0, 1, ka)
    if kb: x[-kb:] *= np.linspace(1, 0, kb)
    return x

CH = {'Am': [57, 60, 64, 71], 'F': [53, 57, 60, 64], 'C': [52, 55, 60, 64], 'G': [55, 59, 62, 69], 'Fsus': [53, 58, 60, 67], 'Cmaj7': [48, 55, 59, 64]}
ROOT = {'Am': 45, 'F': 41, 'C': 48, 'G': 43, 'Fsus': 41, 'Cmaj7': 36}
BARS = ['Am', 'F', 'C', 'G', 'Am', 'F', 'Fsus', 'Cmaj7', 'Am', 'F', 'C', 'C']    # 每小节 2 s
chord_at = lambda t: BARS[min(len(BARS) - 1, int(t // 2))]
DESK = lambda t: t < Q['camCard'][1] or t >= Q['pullOut'][1]          # 桌面段
CARDS = lambda t: Q['camCard'][1] <= t < Q['zoom'][0]                 # 卡片段
INSIDE = lambda t: Q['zoom'][0] <= t < Q['pullOut'][1]                # 钻进去

# ---------- 铺底 ----------
for bar, ch in enumerate(BARS):
    t0 = bar * 2.0
    if t0 >= DUR: break
    t = T(2.0 + 0.3); c = CH[ch]
    pad = sum(np.sin(2 * np.pi * midi(m) * (1 + dt) * t) + 0.25 * saw(midi(m) * (1 + dt), t) for m in c for dt in (-0.003, 0.003)) / 8
    fc = 700 if t0 < 2 else 1600 if INSIDE(t0 + 1) else 1100
    g = 0.10 if INSIDE(t0 + 1) else 0.075
    if t0 >= 18: g *= 1.15
    add(mus, fade(lp(pad, fc), 0.25, 0.3), t0 - 0.05, g, -0.3); add(mus, fade(lp(pad, fc * 0.9), 0.25, 0.3), t0 - 0.04, g * 0.8, 0.3)
# 结尾长音
t = T(3.0); c = CH['C'] + [67, 72]
pad = sum(np.sin(2 * np.pi * midi(m) * t) for m in c) / len(c) * np.exp(-t / 1.6)
add(mus, fade(lp(pad, 2400), 0.02, 0.6), 19.0, 0.16)

# ---------- 拨弦（桌面段，八分）/ 玻璃琶音（卡片段，十六分） ----------
ORD = [0, 2, 1, 3, 2, 1, 3, 2]
for i in range(int(DUR / (BEAT / 2))):
    tt = i * BEAT / 2
    if INSIDE(tt) or tt > 20.0: continue
    c = CH[chord_at(tt)]
    if DESK(tt):
        m = c[ORD[i % 8]] + 12; t = T(0.35)
        s = (np.sin(2 * np.pi * midi(m) * t) + 0.35 * np.sin(2 * np.pi * midi(m) * 3.01 * t) * np.exp(-t / 0.03)) * np.exp(-t / 0.13)
        add(mus, fade(s, 0.002, 0.02), tt, 0.07 if tt >= 0.5 else 0.09, 0.35 * np.sin(i * 0.8))
for i in range(int(DUR / (BEAT / 4))):
    tt = i * BEAT / 4
    if not CARDS(tt): continue
    c = CH[chord_at(tt)]; m = (c + [c[0] + 12, c[1] + 12])[[0, 1, 2, 3, 4, 3, 2, 1][i % 8]] + 12
    t = T(0.45); s = sum(np.sin(2 * np.pi * midi(m) * r * t) * np.exp(-t * (7 + 6 * k)) / (k + 1) for k, r in enumerate([1, 2.76, 5.4]))
    g = 0.045 if tt < Q['morph'][1] else 0.06                         # 光出来以后更亮一点
    add(mus, fade(s, 0.001, 0.03), tt, g, 0.55 * np.sin(i * 0.6))

# ---------- 低音和轻鼓 ----------
for b in range(NB):
    tt = b * BEAT
    if INSIDE(tt) or tt > 20.0: continue
    ch = chord_at(tt)
    if b % 2 == 0:
        t = T(0.9); f = midi(ROOT[ch]); s = np.sin(2 * np.pi * f * t) * env(len(t), 0.01, 0.45)
        add(mus, fade(lp(s, 300), 0.005, 0.1), tt, 0.12)
    if tt >= Q['heading'] - 0.25 or b % 2 == 0:                       # 踩：桌面段每两拍一下，卡片段每拍
        t = T(0.3); f = 110 * np.exp(-t * 30) + 45; s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)
        add(mus, s, tt, 0.16 if CARDS(tt) else 0.10)
    if Q['strAB'][0] <= tt < Q['zoom'][0] or Q['strCC'][0] <= tt < 19.0:   # 反拍沙沙
        n = noise(int(0.05 * SR)); add(mus, hp(n, 7000) * env(len(n), 0.001, 0.012), tt + BEAT / 2, 0.05, 0.4)

# ---------- 音效 ----------
def tick(t, g=0.05, f=3200):                    # 打字：一格一声
    n = noise(int(0.02 * SR)); add(fx, bp(n, f * 0.7, f * 1.4) * env(len(n), 0.0005, 0.004), t, g, 0.2)
def label(at, text, rate=14, g=0.16):            # 标签：纸片拍上去一下 + 打字声
    t = T(0.12); s = lp(noise(len(t)), 1600) * np.exp(-t / 0.025) + 0.6 * np.sin(2 * np.pi * 140 * t) * np.exp(-t / 0.04)
    add(fx, s, at, g)
    n = len(text.replace(' ', ''))
    for i in range(int(np.ceil(n / rate * 12))): tick(at + i / 12, 0.045, 2800 + 300 * (i % 3))
def marker(a, b, lo, hi, g):                     # 荧光笔 / 红笔：带通噪声，按 12fps 一格一格地蹭
    t = T(b - a + 0.05); n = bp(noise(len(t)), lo, hi)
    am = 0.55 + 0.45 * (np.sin(2 * np.pi * 12 * t) > 0); add(fx, fade(n * am, 0.01, 0.05), a, g, -0.15)
def zip_(a, b, g=0.10):                          # 红线：向上扫的拉线声 + 钉图钉
    t = T(b - a); f0 = 600; n = noise(len(t)); out = np.zeros(len(t)); seg = int(0.02 * SR)
    for i in range(0, len(t), seg):
        fc = f0 + 2400 * (i / len(t)); out[i:i + seg] = bp(n[i:i + seg], fc * 0.8, fc * 1.25)
    add(fx, fade(out * (0.4 + 0.6 * np.sin(np.pi * np.arange(len(t)) / len(t))), 0.02, 0.05), a, g, 0.2)
    tt = T(0.1); add(fx, 0.8 * np.sin(2 * np.pi * 900 * tt) * np.exp(-tt / 0.01) + lp(noise(len(tt)), 3000) * np.exp(-tt / 0.006), b, 0.12)
def whoosh(a, b, g=0.12, rev=False):             # 镜头移动：低通噪声起伏
    t = T(b - a); x = np.arange(len(t)) / len(t); e = np.sin(np.pi * x) ** 2 if not rev else x ** 2 * (1 - x) * 4
    n = lp(noise(len(t)), 900) * e; add(fx, fade(n, 0.02, 0.08), a, g, 0)
def chime(t0, m, g=0.08, pan=0.0):
    t = T(0.8); s = sum(np.sin(2 * np.pi * midi(m) * r * t) * np.exp(-t * (4 + 5 * k)) / (k + 1) for k, r in enumerate([1, 2.0, 3.0]))
    add(fx, fade(s, 0.001, 0.05), t0, g, pan)
def pop(t0, f, g=0.08, pan=0.0):
    t = T(0.12); s = np.sin(2 * np.pi * (f + 900 * np.exp(-t * 60)) * t) * np.exp(-t / 0.04); add(fx, s, t0, g, pan)

# 剪报 A
label(Q['lblQ'], 'AI 机房为啥要换成光？', rate=20, g=0.20)
marker(*Q['hlA'], 2500, 5200, 0.05); whoosh(*Q['camOut'], 0.07)
marker(*Q['circA'], 1100, 2800, 0.07)
# 红线 A→B、剪报 B
zip_(*Q['strAB']); whoosh(*Q['camB'], 0.10)
marker(*Q['hlB'], 2500, 5200, 0.05); marker(*Q['underB'], 1100, 2800, 0.07)
# 红线 B→卡片
zip_(*Q['strBC']); whoosh(*Q['camCard'], 0.12)
for i in range(int(np.ceil(11 / 14 * 12))): tick(Q['heading'] + i / 12, 0.04, 3600)
# 卡片：电那条道出来（一声闷响），变糊（下滑的颤音），复制到光（上滑），一样快（同音两下），还清楚
t = T(0.25); add(fx, np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 25)) * t) * np.exp(-t / 0.1), Q['tE0'], 0.22)
t = T(0.9); f = 520 * np.exp(-t * 0.9) * (1 + 0.03 * np.sin(2 * np.pi * 7 * t)); add(fx, lp(np.sin(2 * np.pi * np.cumsum(f) / SR), 1200) * env(len(t), 0.02, 0.35), Q['lblBlur'], 0.07, 0.35)
label(Q['lblBlur'], '跑远了：认不清', g=0.12)
t = T(0.55); f = 330 * 2 ** (np.arange(len(t)) / len(t) * 1.6); add(fx, fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * np.arange(len(t)) / len(t)), 0.01, 0.05), Q['morph'][0], 0.09, -0.2)
chime(Q['tie'], 76, 0.07, -0.2); chime(Q['tie'] + 0.25, 76, 0.07, 0.2); label(Q['tie'] + 1 / 12, '一样快', g=0.1)
chime(Q['lblClear'], 81, 0.08); label(Q['lblClear'], '光：一样快，还清楚', g=0.1)
# Kurzgesagt：钻进去（上升音）→ 镜头圈张开（低频一沉）→ 头发丝 → 一对对冒出来的芯 → 拉回（反向呼啸）
a, b = Q['zoom'][0], Q['lens'][1]; t = T(b - a); x = np.arange(len(t)) / len(t)
rise = hp(noise(len(t)), 400) * x ** 2 * 0.5 + np.sin(2 * np.pi * np.cumsum(200 * 2 ** (x * 2.5)) / SR) * x ** 1.5 * 0.4
add(fx, fade(rise, 0.05, 0.01), a, 0.16)
t = T(1.6); add(fx, np.sin(2 * np.pi * (36 + 50 * np.exp(-t * 8)) * t) * np.exp(-t / 0.5), Q['lens'][1], 0.38)
chime(Q['lens'][1], 88, 0.04, 0.3)
label(Q['lblCore'], '光纤的芯', g=0.1)
marker(*Q['hair'], 1200, 3000, 0.10); label(Q['hair'][0], '一根头发丝（截面）', g=0.08)
pop(Q['split'][0], 700, 0.08)
for j in range(4):
    pop(Q['pairs'] + j * 0.125, 800 + 160 * j, 0.07, -0.3); pop(Q['pairs'] + j * 0.125 + 0.01, 820 + 160 * j, 0.07, 0.3)
label(Q['lblTenth'], '芯≈头发丝的1/10', rate=20, g=0.14)
whoosh(*Q['pullOut'], 0.2, rev=False)
t = T(Q['pullOut'][1] - Q['pullOut'][0]); x = np.arange(len(t)) / len(t); add(fx, np.sin(2 * np.pi * np.cumsum(900 * 2 ** (-x * 2.5)) / SR) * np.sin(np.pi * x) * 0.3, Q['pullOut'][0], 0.08)
# 结论
zip_(*Q['strCC']); whoosh(*Q['pushC'], 0.10)
marker(*Q['hlC'], 2500, 5200, 0.05)
label(Q['lblCost'], '代价：电光转换 + 精密对接', g=0.18)
label(Q['lblSeries'], '白话光互连 · 01', g=0.14); chime(Q['lblSeries'], 84, 0.05)

# ---------- 混音 ----------
mix = mus * 0.75 + fx * 1.35
mix[:, -int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))
mix /= np.max(np.abs(mix)) * 1.12
with wave.open('score.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix.T * 32767).astype('<i2').tobytes())
print('score.wav', DUR, 's; beats', NB)
