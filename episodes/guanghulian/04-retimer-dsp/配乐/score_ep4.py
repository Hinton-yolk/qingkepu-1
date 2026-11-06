# 白话光互连 04 · Vox 竖屏 —— 原创配乐与音效（代码合成，沿用第一篇的音色）
# 120 BPM，A 小调循环 Am–F–C–G，结尾落 C。时间点和事件全部读 ../代码工程/full/desk.json（和画面同一份）：
#   桌面段：木质拨弦八分音符＋轻踩；卡片段（3b1b 机制）：玻璃琶音十六分音符；钻进光纤（Kurzgesagt）：上升音 → 低频一沉、只留空气感铺底。
#   纸上的动作（荧光笔、红笔、红线、标签打字、贴纸）按画面 12fps 步进做颗粒；卡片里的动作各有一个小音色。
# 产出 score_full.wav、beats_full.json
import json, wave, numpy as np
from scipy.signal import butter, lfilter

D = json.load(open('../代码工程/ep4/desk.json', encoding='utf-8'))
SR, BPM, DUR = 48000, D['bpm'], D['dur']
BEAT = 60 / BPM; N = int(SR * DUR); NB = int(round(DUR / BEAT))
rs = np.random.default_rng(11)
mus = np.zeros((2, N)); fx = np.zeros((2, N))
CU = D['cue']; LENS = D['lens']
CARDW = [(v['t0'], v['end']) for k, v in CU.items()]
CARDS = lambda t: any(a <= t < b for a, b in CARDW)
INSIDE = lambda t: LENS['zin'][0] <= t < LENS['out'][1]
END0 = D['station'][-1][1]
json.dump({'bpm': BPM, 'seconds': DUR, 'beats': [round(i * BEAT, 3) for i in range(NB)], 'downbeats': [round(i * BEAT, 3) for i in range(0, NB, 4)], 'cards': CARDW},
          open('beats_ep4.json', 'w'), indent=1)

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
def gl(f0, f1, d): t = T(d); return np.sin(2 * np.pi * np.cumsum(f0 * (f1 / f0) ** (np.arange(len(t)) / len(t))) / SR)

CH = {'Am': [57, 60, 64, 71], 'F': [53, 57, 60, 64], 'C': [52, 55, 60, 64], 'G': [55, 59, 62, 69], 'Fmaj7': [53, 57, 60, 64, 69], 'Cmaj7': [48, 55, 59, 64]}
ROOT = {'Am': 45, 'F': 41, 'C': 48, 'G': 43, 'Fmaj7': 41, 'Cmaj7': 36}
NBAR = int(np.ceil(DUR / 2))
BARS = [['Am', 'F', 'C', 'G'][i % 4] for i in range(NBAR)]
for i in range(NBAR):
    if INSIDE(i * 2 + 1): BARS[i] = 'Fmaj7' if i % 2 == 0 else 'Cmaj7'
BARS[-3:] = ['F', 'C', 'C']
chord_at = lambda t: BARS[min(NBAR - 1, int(t // 2))]

# 铺底
for bar, ch in enumerate(BARS):
    t0 = bar * 2.0; t = T(2.3); c = CH[ch]
    pad = sum(np.sin(2 * np.pi * midi(m) * (1 + dt) * t) + 0.25 * saw(midi(m) * (1 + dt), t) for m in c for dt in (-0.003, 0.003)) / (2 * len(c))
    fc = 700 if t0 < 4 else 1600 if INSIDE(t0 + 1) else 1100
    g = 0.075 if INSIDE(t0 + 1) else 0.075
    if t0 >= END0: g *= 1.15
    add(mus, fade(lp(pad, fc), 0.25, 0.3), t0 - 0.05, g, -0.3); add(mus, fade(lp(pad, fc * 0.9), 0.25, 0.3), t0 - 0.04, g * 0.8, 0.3)
t = T(4.0); c = CH['C'] + [67, 72]; pad = sum(np.sin(2 * np.pi * midi(m) * t) for m in c) / len(c) * np.exp(-t / 1.8)
add(mus, fade(lp(pad, 2400), 0.02, 0.8), DUR - 4.5, 0.16)
# 拨弦（桌面段八分）/ 玻璃琶音（卡片段十六分）
ORD = [0, 2, 1, 3, 2, 1, 3, 2]
for i in range(int(DUR / (BEAT / 2))):
    tt = i * BEAT / 2
    if INSIDE(tt) or CARDS(tt) or tt > DUR - 3.5: continue
    c = CH[chord_at(tt)]; m = c[ORD[i % 8] % len(c)] + 12; t = T(0.35)
    s = (np.sin(2 * np.pi * midi(m) * t) + 0.35 * np.sin(2 * np.pi * midi(m) * 3.01 * t) * np.exp(-t / 0.03)) * np.exp(-t / 0.13)
    add(mus, fade(s, 0.002, 0.02), tt, 0.07, 0.35 * np.sin(i * 0.8))
for i in range(int(DUR / (BEAT / 4))):
    tt = i * BEAT / 4
    if not CARDS(tt) or INSIDE(tt): continue
    c = CH[chord_at(tt)]; cc = c + [c[0] + 12, c[1] + 12]; m = cc[[0, 1, 2, 3, 4, 3, 2, 1][i % 8] % len(cc)] + 12
    t = T(0.45); s = sum(np.sin(2 * np.pi * midi(m) * r * t) * np.exp(-t * (7 + 6 * k)) / (k + 1) for k, r in enumerate([1, 2.76, 5.4]))
    add(mus, fade(s, 0.001, 0.03), tt, 0.05, 0.55 * np.sin(i * 0.6))
# 低音、轻踩、反拍沙沙
for b in range(NB):
    tt = b * BEAT
    if INSIDE(tt) or tt > DUR - 3.5: continue
    ch = chord_at(tt)
    if b % 2 == 0:
        t = T(0.9); s = np.sin(2 * np.pi * midi(ROOT[ch]) * t) * env(len(t), 0.01, 0.45); add(mus, fade(lp(s, 300), 0.005, 0.1), tt, 0.12)
    if CARDS(tt) or b % 2 == 0:
        t = T(0.3); f = 110 * np.exp(-t * 30) + 45; s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09); add(mus, s, tt, 0.12 if CARDS(tt) else 0.09)
    if tt >= 3.5:
        n = noise(int(0.05 * SR)); add(mus, hp(n, 7000) * env(len(n), 0.001, 0.012), tt + BEAT / 2, 0.045, 0.4)

# ---------- 音效 ----------
def tick(t, g=0.045, f=3200): n = noise(int(0.02 * SR)); add(fx, bp(n, f * 0.7, f * 1.4) * env(len(n), 0.0005, 0.004), t, g, 0.2)
def chime(t0, m, g=0.08, pan=0.0):
    t = T(0.8); s = sum(np.sin(2 * np.pi * midi(m) * r * t) * np.exp(-t * (4 + 5 * k)) / (k + 1) for k, r in enumerate([1, 2.0, 3.0])); add(fx, fade(s, 0.001, 0.05), t0, g, pan)
def pop(t0, f, g=0.08, pan=0.0): t = T(0.12); s = np.sin(2 * np.pi * (f + 900 * np.exp(-t * 60)) * t) * np.exp(-t / 0.04); add(fx, s, t0, g, pan)
def thud(t0, g=0.16): t = T(0.12); add(fx, lp(noise(len(t)), 1600) * np.exp(-t / 0.025) + 0.6 * np.sin(2 * np.pi * 140 * t) * np.exp(-t / 0.04), t0, g)
def marker(a, d, lo, hi, g):
    t = T(d + 0.05); n = bp(noise(len(t)), lo, hi); am = 0.55 + 0.45 * (np.sin(2 * np.pi * 12 * t) > 0); add(fx, fade(n * am, 0.01, 0.05), a, g, -0.15)
def zip_(a, d, g=0.10):
    t = T(d); n = noise(len(t)); out = np.zeros(len(t)); sg = int(0.02 * SR)
    for i in range(0, len(t), sg): fc = 600 + 2400 * (i / len(t)); out[i:i + sg] = bp(n[i:i + sg], fc * 0.8, fc * 1.25)
    add(fx, fade(out * (0.4 + 0.6 * np.sin(np.pi * np.arange(len(t)) / len(t))), 0.02, 0.05), a, g, 0.2)
    tt = T(0.1); add(fx, 0.8 * np.sin(2 * np.pi * 900 * tt) * np.exp(-tt / 0.01) + lp(noise(len(tt)), 3000) * np.exp(-tt / 0.006), a + d, 0.09)
def whoosh(a, d, g):
    t = T(d); x = np.arange(len(t)) / len(t); add(fx, fade(lp(noise(len(t)), 900) * np.sin(np.pi * x) ** 2, 0.02, 0.08), a, g)
BITS = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1]
for e in D['sfx']:
    k, t0 = e['kind'], e['t']
    if k == 'label':
        thud(t0, 0.11); n = len(e['text'].replace(' ', ''))
        for i in range(int(np.ceil(n / e['rate'] * 12))): tick(t0 + i / 12, 0.04, 2800 + 300 * (i % 3))
    elif k == 'marker': marker(t0, e['dur'], 2500, 5200, 0.05)
    elif k == 'pen': marker(t0, e['dur'], 1100, 2800, 0.07)
    elif k == 'string': zip_(t0, e['dur'])
    elif k == 'whoosh': whoosh(t0, e['dur'], e['g'])
    elif k == 'stick': thud(t0, 0.14); chime(t0, [72, 74, 76, 79, 81][e['n'] - 1], 0.06)
    elif k == 'exchange':
        for j in range(4): pop(t0 + j * 0.06, 1200 + 200 * j, 0.04, (-1) ** j * 0.4)
    elif k == 'serdes':
        for j in range(24): tick(t0 + j * 0.143, 0.05, 2200 + 100 * BITS[j] * 8)
    elif k == 'thock': t = T(0.25); add(fx, np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 25)) * t) * np.exp(-t / 0.1), t0, 0.07)
    elif k == 'blur':
        t = T(0.9); f = 520 * np.exp(-t * 0.9) * (1 + 0.03 * np.sin(2 * np.pi * 7 * t)); add(fx, lp(np.sin(2 * np.pi * np.cumsum(f) / SR), 1200) * env(len(t), 0.02, 0.35), t0, 0.07, 0.35)
    elif k == 'dsp': t = T(0.18); add(fx, np.sin(2 * np.pi * 660 * t) * np.exp(-t / 0.05), t0, 0.06); t = T(0.25); add(fx, np.sin(2 * np.pi * 220 * t) * np.exp(-t / 0.08) * 0.8, t0 + 0.05, 0.08)
    elif k in ('reach', 'reach2'):
        rate = 0.11 if k == 'reach' else 0.045
        for j in range(int(1.2 / rate)): tick(t0 + j * rate, 0.035, 2600 if k == 'reach' else 4200)
    elif k == 'laser': add(fx, fade(gl(300, 1200, 0.4) * np.linspace(0, 1, int(0.4 * SR)), 0.01, 0.1), t0, 0.06); chime(t0 + 0.3, 84, 0.04)
    elif k == 'mod':
        for j in range(int(e['dur'] / 0.2)):
            if BITS[j % 24]: chime(t0 + j * 0.2, 88, 0.025, 0.3)
    elif k == 'amp': t = T(0.4); add(fx, fade(lp(saw(110, t) * np.linspace(0.2, 1, len(t)), 900), 0.01, 0.1), t0, 0.05)
    elif k == 'flash': chime(t0, 79, 0.09); chime(t0 + 0.06, 86, 0.06)
    elif k == 'morph': add(fx, fade(gl(330, 1000, 0.55) * np.sin(np.pi * np.arange(int(0.55 * SR)) / int(0.55 * SR)), 0.01, 0.05), t0, 0.09, -0.2)
    elif k == 'tie': chime(t0, 76, 0.07, -0.2); chime(t0 + 0.25, 76, 0.07, 0.2)
    elif k == 'envE': t = T(0.7); add(fx, fade(lp(gl(520, 260, 0.7), 1500) * np.linspace(1, 0.35, len(t)), 0.01, 0.1), t0, 0.07, -0.25)   # 电：往下掉
    elif k == 'envL': t = T(0.7); add(fx, fade(np.sin(2 * np.pi * midi(81) * t) * np.exp(-t / 0.5), 0.01, 0.1), t0, 0.06, 0.25); chime(t0, 88, 0.04, 0.25)   # 光：平稳
    elif k == 'riser':
        d = e['dur']; t = T(d); x = np.arange(len(t)) / len(t)
        add(fx, fade(hp(noise(len(t)), 400) * x ** 2 * 0.5 + np.sin(2 * np.pi * np.cumsum(200 * 2 ** (x * 2.5)) / SR) * x ** 1.5 * 0.4, 0.05, 0.01), t0, 0.11)
    elif k == 'boom': t = T(1.6); add(fx, np.sin(2 * np.pi * (36 + 50 * np.exp(-t * 8)) * t) * np.exp(-t / 0.5), t0, 0.12); chime(t0, 88, 0.04, 0.3)
    elif k == 'pairs':
        if 'split' in LENS: pop(LENS['split'][0], 700, 0.08)
        for j in range(4): pop(t0 + j * 0.125, 800 + 160 * j, 0.07, -0.3); pop(t0 + j * 0.125 + 0.01, 820 + 160 * j, 0.07, 0.3)
    elif k == 'pullout':
        whoosh(t0, e['dur'], 0.2); t = T(e['dur']); x = np.arange(len(t)) / len(t); add(fx, np.sin(2 * np.pi * np.cumsum(900 * 2 ** (-x * 2.5)) / SR) * np.sin(np.pi * x) * 0.3, t0, 0.08)
    elif k == 'leak':
        for j in range(int(e['dur'] / 0.2)): add(fx, fade(bp(noise(int(0.12 * SR)), 3000, 7000), 0.005, 0.08), t0 + j * 0.2, 0.03, 0.4 * np.sin(j))
    elif k == 'slide': whoosh(t0, 0.5, 0.06)
    elif k == 'click': t = T(0.08); add(fx, np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.008) + lp(noise(len(t)), 4000) * np.exp(-t / 0.005), t0, 0.14); chime(t0 + 0.05, 81, 0.06)
    elif k == 'pd':
        for j in range(5): pop(t0 + j * 0.2, 500, 0.03)
    elif k == 'pin':
        if e['n'] < 6: tick(t0, 0.05, 2400); pop(t0 + 0.05, 600 + 60 * e['n'], 0.05)
        else: t = T(0.25); add(fx, fade(lp(saw(90, t), 700) * np.exp(-t / 0.08), 0.005, 0.05), t0, 0.07)   # 没有引脚了：闷闷的一声「不行」
    elif k == 'ok': chime(t0, 79, 0.07); chime(t0 + 0.12, 84, 0.06)
    elif k == 'wrong': t = T(0.45); add(fx, fade(lp(saw(110, t) + saw(116.5, t), 900) * np.exp(-t / 0.18), 0.005, 0.08), t0, 0.06)
    elif k == 'zoomstep': whoosh(t0, 0.5, 0.10); pop(t0 + 0.45, 500, 0.05)
    elif k == 'tick':
        for j in range(6): tick(t0 + j * 0.0833, 0.05, 3000)
    elif k == 'count':
        for j in range(12): pop(t0 + j * 0.104, 700 + (40 * j if 1 <= j <= 5 else 0), 0.05 if 1 <= j <= 5 else 0.02)
    elif k == 'shout':        # 走廊里喊一个字：短促的一声，后面跟着两声越来越轻的回声
        t = T(0.18); s_ = lp(saw(210, t) * 0.5 + np.sin(2 * np.pi * 420 * t), 1400) * np.exp(-t / 0.06)
        for j, gg in enumerate([0.07, 0.035, 0.018]): add(fx, fade(s_, 0.003, 0.03), t0 + j * 0.12, gg, -0.3 + 0.3 * j)
    elif k == 'shave':        # 棱角被削掉：一声往下滑、越来越闷的音
        d = e.get('dur', 1.0); t = T(d); x = np.arange(len(t)) / len(t)
        add(fx, fade(lp(np.sin(2 * np.pi * np.cumsum(700 * 2 ** (-x * 1.5)) / SR), 2400) * (1 - 0.6 * x), 0.02, 0.1), t0, 0.06)
    elif k == 'samples':      # 采样：一个时刻一声短促的「嘀」，音高跟着采样值走
        n_ = e.get('n', 12); d = e.get('dur', 1.5)
        for j in range(n_): pop(t0 + j * d / n_, 900 + 260 * ((j * 7) % 5), 0.035, -0.4 + 0.8 * j / max(1, n_ - 1))
    elif k == 'fan':
        for j in range(24): pop(t0 + j * e['dur'] / 24, 900 + 30 * (j % 8), 0.035, 0.5 - (j % 8) / 8)

mix = mus * 0.75 + fx * 1.35
mix[:, -int(0.8 * SR):] *= np.linspace(1, 0, int(0.8 * SR))
mix /= np.max(np.abs(mix)) * 1.12
with wave.open('score_ep4.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
print('score_ep4.wav', DUR, 's; beats', NB, '; sfx', len(D['sfx']))
