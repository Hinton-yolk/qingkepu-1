"""EP.01 AI 为什么一个字一个字往外蹦？—— 代码合成配乐 + 音效（运动草稿，按字幕 v3.1 的时间）。
音色沿用「AI 为什么非要用显卡？」那条（系列原有音色里做变化），调性、和声、段落都换：
python3 music.py out.wav
BPM 100。七段：开头 D 大调木琴 / 分叉段 B 小调断奏 + 滴答 / 停半拍 / 机制段 D 大调稳定脉冲 /
显卡与学说话 G 大调铺开 / 抢答批改段 A 持续音往上推 / 停半拍 / 揭晓段 D 大调全编制（中间变薄）/ 结尾钟声回到 D。
"""
import sys
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile

SR = 48000
DUR = 109.6
N = int(SR * (DUR + 0.5))
BEAT = 0.6
rng = np.random.default_rng(7)

mus = np.zeros((2, N))   # 音乐
sfx = np.zeros((2, N))   # 音效


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def add(buf, t0, sig, gain=1.0, pan=0.0):
    i = int(round(t0 * SR))
    if i < 0:
        sig = sig[-i:]
        i = 0
    n = min(len(sig), N - i)
    if n <= 0:
        return
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[0, i:i + n] += sig[:n] * gain * l * 1.414
    buf[1, i:i + n] += sig[:n] * gain * r * 1.414


def env_adsr(n, a, d, s, r, dur):
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = np.clip((t - dur) / max(r, 1e-4), 0, 1)
    return e * (1 - rel)


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)


# ---------- 音色 ----------
def marimba(f, d=0.9):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 5) + 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t * 18)
    s += 0.12 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 40)
    return s * np.minimum(1, t / 0.002)


def pluck(f, d=0.5, bright=8):
    t = tt(d)
    s = sum((1 / k ** 1.1) * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (4 + k * bright * 0.4)) for k in range(1, 10))
    return s * np.minimum(1, t / 0.003) * 0.6


def saw(f, d, nh=14, detune=(0, -7, 7)):
    t = tt(d)
    out = np.zeros_like(t)
    for c in detune:
        ff = f * 2 ** (c / 1200)
        for k in range(1, nh + 1):
            if ff * k > 9000:
                break
            out += np.sin(2 * np.pi * ff * k * t + k * c) / k
    return out / len(detune)


def square(f, d, nh=15, vib=0.0):
    t = tt(d)
    ph = 2 * np.pi * f * t + vib * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.3)
    return sum(np.sin(k * ph) / k for k in range(1, nh + 1, 2)) * 0.8


def tri(f, d):
    t = tt(d)
    return sum(((-1) ** ((k - 1) // 2)) * np.sin(2 * np.pi * f * k * t) / k ** 2 for k in range(1, 12, 2)) * 0.8


def pad(freqs, d, att=0.4, rel=0.6, cutoff=2200):
    n = int((d + rel) * SR)
    s = np.zeros(n)
    for f in freqs:
        s += saw(f, d + rel, nh=10)
    s = lp(s, cutoff)
    return s * env_adsr(n, att, 0.8, 0.8, rel, d) / max(1, len(freqs)) * 0.9


def bass(f, d, dec=3.0):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    return s * np.exp(-t * dec) * np.minimum(1, t / 0.005) * np.clip((d - t) / 0.02, 0, 1)


def kick(g=1.0):
    t = tt(0.45)
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 7) + 0.3 * np.exp(-t * 300) * rng.standard_normal(len(t))) * g


def clap():
    t = tt(0.25)
    n = bp(rng.standard_normal(len(t)), 900, 4000)
    e = np.exp(-t * 22) + 0.6 * np.exp(-((t - 0.012) % 0.011) * 300) * (t < 0.035)
    return n * e * 0.7


def hat(d=0.05, g=1.0):
    t = tt(d)
    return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t * 90) * g


def bell(f, d=2.0):
    t = tt(d)
    parts = [(1, 1, 2.2), (2.76, 0.45, 4), (5.40, 0.25, 7), (8.93, 0.12, 11)]
    return sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * k) for r, a, k in parts) * np.minimum(1, t / 0.002) * 0.5


def noise_sweep(d, f0, f1, g=1.0, shape='rise'):
    t = tt(d)
    x = rng.standard_normal(len(t))
    nseg = 24
    out = np.zeros_like(x)
    edges = np.linspace(0, len(x), nseg + 1).astype(int)
    for i in range(nseg):
        fc = f0 * (f1 / f0) ** (i / (nseg - 1))
        lo, hi = max(60, fc * 0.6), min(18000, fc * 1.6)
        a, b = max(0, edges[i] - 2000), min(len(x), edges[i + 1] + 2000)
        y = bp(x[a:b], lo, hi)
        out[edges[i]:edges[i + 1]] = y[edges[i] - a: edges[i] - a + edges[i + 1] - edges[i]]
    u = t / d
    e = (u ** 2) if shape == 'rise' else (np.sin(np.pi * u) ** 1.5 if shape == 'swell' else (1 - u) ** 2)
    return out * e * g


def blip(f, d=0.12, g=1.0):
    t = tt(d)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 35) * g


def tick(f=2400, g=1.0):
    t = tt(0.03)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 260) * g


# ---------- 和弦 ----------
NOTE = {'C': 0, 'Db': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'Gb': 6, 'F#': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}


def chord(name):
    """'F' 'Dm' 'Bb' 'A'  → (root midi at octave 3, [triad midis around C4])"""
    minor = name.endswith('m')
    r = NOTE[name[:-1] if minor else name]
    third = 3 if minor else 4
    root3 = 48 + r if r <= 7 else 36 + r          # 低音 E2..G3
    tones = [60 + r, 60 + r + third, 60 + r + 7]
    tones = [x - 12 if x > 72 else x for x in tones]
    return root3, sorted(tones)


def at(beat):
    return beat * BEAT


def section(chords, b0, b1, fn):
    """chords: [(name, beats)] 循环铺满 [b0, b1)"""
    b = b0
    i = 0
    while b < b1 - 1e-6:
        name, nb = chords[i % len(chords)]
        nb = min(nb, b1 - b)
        fn(name, b, nb)
        b += nb
        i += 1



# 段 1：0–8.2 D 大调，木琴琶音 + 柔垫（手机里逐字回复）
def s1(name, b, nb):
    root, tones = chord(name)
    add(mus, at(b), pad([hz(x) for x in tones], nb * BEAT, att=0.6, cutoff=1500), 0.15)
    arp = [tones[0], tones[1], tones[2], tones[0] + 12, tones[2], tones[1]]
    for k in range(int(nb * 2)):
        add(mus, at(b + k * 0.5), marimba(hz(arp[k % 6] + 12)), 0.19, pan=0.3 * np.sin(k))
section([('D', 4), ('Bm', 4), ('G', 3.67)], 0, 13.67, s1)

# 段 2：8.2–19.8 B 小调，断奏低音 + 滴答（为什么不能几个字一起写？分叉）
def s2(name, b, nb):
    root, tones = chord(name)
    add(mus, at(b), pad([hz(x - 12) for x in tones], nb * BEAT, att=0.3, cutoff=900), 0.18)
    for k in range(int(nb * 2)):
        add(mus, at(b + k * 0.5), bass(hz(root), 0.22, dec=8), 0.30)
        add(mus, at(b + k * 0.5), tick(1800 if k % 2 else 2600, 0.11), 1, pan=-0.3 if k % 2 else 0.3)
    add(mus, at(b), bell(hz(tones[2] + 12), 1.6), 0.09, pan=0.2)
section([('Bm', 4), ('G', 4), ('Em', 4), ('F#', 7.25)], 13.67, 32.92, s2)

# 段 3：19.8–46.5 D 大调，稳定脉冲（每一个字是怎么写出来的：过模型、乘加、回头看、打分、抽签）
def s3(name, b, nb):
    root, tones = chord(name)
    add(mus, at(b), pad([hz(x) for x in tones], nb * BEAT, att=0.2, cutoff=1800), 0.13)
    add(mus, at(b), bass(hz(root), nb * BEAT * 0.9, dec=1.0), 0.24)
    for k in range(int(nb * 2)):
        add(mus, at(b + k * 0.5), pluck(hz(tones[k % 3] + 12), 0.35, bright=6), 0.10, pan=0.4 * np.sin(k * 1.3))
    for k in range(0, int(nb), 2):
        add(mus, at(b + k), kick(0.55), 0.22)
section([('D', 4), ('A', 4), ('Bm', 4), ('G', 4)], 33.0, 57.83, s3)
section([('G', 4), ('D', 4), ('A', 4), ('Bm', 4)], 57.83, 77.5, s3)        # 34.7 秒起换一组和声，不一个循环铺到底

# 段 4：46.5–56.7 G 大调铺开（显卡再多核 / 学说话一整段同时算）
def s4(name, b, nb):
    root, tones = chord(name)
    add(mus, at(b), pad([hz(x) for x in tones] + [hz(tones[0] + 12)], nb * BEAT, att=0.5, cutoff=2600), 0.17)
    add(mus, at(b), bass(hz(root), nb * BEAT, dec=0.7), 0.26)
    for k in range(int(nb)):
        add(mus, at(b + k), bell(hz(tones[k % 3] + 24), 1.4), 0.06, pan=0.5 * np.sin(k))
section([('G', 4), ('Em', 4), ('C', 4), ('D', 5)], 77.5, 94.5, s4)

# 段 5：56.7–65.7 A 持续音往上推（小模型抢答、大模型一起批改）
def s5(name, b, nb):
    root, tones = chord(name)
    add(mus, at(b), pad([hz(x) for x in tones], nb * BEAT, att=0.1, cutoff=2200), 0.14)
    add(mus, at(b), bass(hz(45), nb * BEAT, dec=0.4), 0.22)
    for k in range(int(nb * 4)):
        add(mus, at(b + k * 0.25), hat(0.03, 0.05 + 0.08 * (b + k * 0.25 - 94.5) / 15), 1, pan=0.4)
section([('A', 4), ('Bm', 4), ('G', 4), ('A', 3)], 94.5, 109.5, s5)
add(mus, 64.2, noise_sweep(1.3, 400, 9000, 1.0, 'rise'), 0.10)

# 段 6：65.7–99.4 揭晓：D 大调全编制（批改 4 个和写 1 个差不多快 → 慢在搬 → 快 2–3 倍），82.9–92.5 变薄
MEL = {'D': [74, 78, 81, 78], 'A': [76, 81, 85, 81], 'Bm': [74, 78, 83, 78], 'G': [74, 79, 83, 79]}
def s6(name, b, nb):
    root, tones = chord(name)
    thin = 138.2 <= b < 154.2
    add(mus, at(b), pad([hz(x) for x in tones] + [hz(tones[0] + 12)], nb * BEAT, att=0.05, cutoff=3000 if not thin else 1600), 0.15)
    add(mus, at(b), bass(hz(root), nb * BEAT * 0.95, dec=0.9), 0.28)
    for k in range(int(nb)):
        if not thin:
            add(mus, at(b + k), kick(), 0.38)
            if k % 2 == 1: add(mus, at(b + k), clap(), 0.17, pan=0.05)
        add(mus, at(b + k + 0.5), hat(0.05, 0.14 if not thin else 0.06), 1, pan=0.35)
        m = MEL.get(name, MEL['D'])[k % 4]
        add(mus, at(b + k), marimba(hz(m)), 0.16 if not thin else 0.10, pan=-0.2)
section([('D', 4), ('A', 4), ('Bm', 4), ('G', 4)], 109.5, 165.67, s6)

# 段 7：99.4–109.6 结尾：钟声回到 D
def s7(name, b, nb):
    root, tones = chord(name)
    add(mus, at(b), pad([hz(x) for x in tones], nb * BEAT, att=0.4, rel=0.8, cutoff=2000), 0.16)
    add(mus, at(b), bell(hz(tones[2] + 12), 2.4), 0.10, pan=0.2)
section([('G', 4), ('A', 4), ('D', 4.6)], 165.67, 178.3, s7)
add(mus, 106.6, pad([hz(62), hz(66), hz(69), hz(74)], 3.0, att=0.05, rel=0.8, cutoff=2400), 0.20)
add(mus, 106.6, bass(hz(38), 3.0, dec=0.6), 0.28)
for i, m in enumerate([81, 86, 90, 93]):
    add(mus, 106.6 + i * 0.15, bell(hz(m), 2.6), 0.07, pan=-0.4 + i * 0.25)

fade = np.ones(N)
i0, i1 = int(108.6 * SR), int(109.6 * SR)
fade[i0:i1] = np.linspace(1, 0, i1 - i0) ** 1.5
fade[i1:] = 0

# ---------- 停半拍（揭晓前） ----------
for tp in (19.5, 65.4):
    g = np.ones(N); a, b = int(tp * SR), int((tp + 0.3) * SR)
    g[a - 1200:a] = np.linspace(1, 0, 1200); g[a:b] = 0
    mus *= g

# ---------- 音效（卡画面动作；时间按字幕 v3.1） ----------
for tc in (0.5, 0.9, 1.3, 1.7):
    add(sfx, tc, blip(hz(86), 0.12), 0.22, pan=0.1)                          # 逐字蹦
add(sfx, 5.0, noise_sweep(0.3, 2000, 400, 1, 'fall'), 0.15)                   # ✕ 碎
add(sfx, 11.5, noise_sweep(0.8, 400, 3000, 1, 'swell'), 0.10)                 # 分叉长出来
add(sfx, 14.3, noise_sweep(0.8, 400, 3000, 1, 'swell'), 0.10)
add(sfx, 19.8, kick(1.0), 0.40); add(sfx, 19.8, bell(hz(86), 1.4), 0.12)     # 停半拍后进机制段
for k in range(6): add(sfx, 29.5 + k * 0.08, blip(hz(84 + k), 0.06), 0.10)    # 乘加
add(sfx, 30.8, bell(hz(90), 1.0), 0.12)                                      # 加成一个数
for k in range(8): add(sfx, 32.4 + k * 0.12, tick(2600 - k * 120, 0.2), 0.3)   # 回头看
add(sfx, 38.2, noise_sweep(0.6, 600, 2400, 1, 'swell'), 0.08)                 # 柱子升起
for k in range(14):                                                          # 转盘
    add(sfx, 44.0 + 1.5 * (1 - (1 - k / 13) ** 0.5), tick(2200, 0.25), 0.3)
add(sfx, 45.6, bell(hz(88), 1.2), 0.14)
add(sfx, 50.9, noise_sweep(0.5, 3000, 9000, 1, 'fall'), 0.08)
for k in range(10): add(sfx, 52.5 + k * 0.02, blip(hz(90 + k % 3), 0.05), 0.06)  # 一排勾一起亮
for k in range(4): add(sfx, 57.6 + k * 0.25, blip(hz(83 + k * 2), 0.08), 0.14)   # 小模型抢答
add(sfx, 60.4, noise_sweep(0.7, 800, 6000, 1, 'swell'), 0.12)                 # 大模型扫光
add(sfx, 65.7, kick(1.2), 0.50); add(sfx, 65.7, lp(rng.standard_normal(int(0.8 * SR)), 1200) * np.exp(-tt(0.8) * 5), 0.18)
for k in range(10): add(sfx, 70.2 + k * 0.12, tick(1800, 0.15), 0.25)         # 参数排队搬
add(sfx, 80.5, noise_sweep(0.5, 600, 3000, 1, 'swell'), 0.10)
for k in range(2): add(sfx, 83.4 + k * 0.15, bell(hz(88 + k * 2), 0.8), 0.12)  # 绿勾
add(sfx, 84.0, noise_sweep(0.3, 2000, 400, 1, 'fall'), 0.12)                  # 作废
add(sfx, 87.6, bell(hz(91), 0.9), 0.12)                                       # 好猜 ✓
add(sfx, 90.5, noise_sweep(0.3, 2000, 400, 1, 'fall'), 0.10)
add(sfx, 93.4, bell(hz(86), 1.2), 0.10); add(sfx, 93.4, bell(hz(93), 1.0), 0.08)
add(sfx, 96.2, kick(1.1), 0.45); add(sfx, 96.2, bell(hz(86), 1.8), 0.16)      # 2–3 倍
add(sfx, 102.6, noise_sweep(1.2, 1500, 10000, 1, 'swell'), 0.06)              # 片尾大字

# ---------- 混音 ----------
irn = int(1.7 * SR)
ti = np.arange(irn) / SR
ir = np.stack([rng.standard_normal(irn) * np.exp(-ti * 3.2), rng.standard_normal(irn) * np.exp(-ti * 3.2)])
ir[:, :int(0.015 * SR)] = 0
ir = np.stack([lp(ir[0], 6000), lp(ir[1], 6000)])
ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
wet = np.stack([fftconvolve(mus[0], ir[0])[:N], fftconvolve(mus[1], ir[1])[:N]])
wet_s = np.stack([fftconvolve(sfx[0], ir[1])[:N], fftconvolve(sfx[1], ir[0])[:N]])
mix = (mus + 0.22 * wet) * fade + 1.0 * (sfx + 0.15 * wet_s) * fade
mix = hp(mix, 30)
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
out = (mix[:, :int(DUR * SR)] * 0.89).T.astype(np.float32)
wavfile.write(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', SR, out)
print('ok', out.shape)
