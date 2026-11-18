"""AI 为什么非要用显卡？—— 代码合成配乐 + 音效。
python3 music.py out.wav
BPM 100（一拍 0.6 秒）。六段：开头 F 大调木琴 / CPU 段 D 小调滴答 / 停半拍 / GPU 段 F 大调全编制 /
「谁也不用等谁」段变薄 / 游戏段转 G 大调芯片音（chiptune）/ 结尾 G 大调钟声收束。
"""
import sys
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile

SR = 48000
DUR = 60.0
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
NOTE = {'C': 0, 'Db': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'Gb': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}


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


# 段 1：0–13.2（拍 0–22）F 大调，木琴琶音 + 柔垫
def s1(name, b, nb):
    root, tones = chord(name)
    add(mus, at(b), pad([hz(x) for x in tones], nb * BEAT, att=0.6, cutoff=1500), 0.16)
    arp = [tones[0], tones[1], tones[2], tones[0] + 12, tones[2], tones[1]]
    for k in range(int(nb * 2)):
        bb = b + k * 0.5
        add(mus, at(bb), marimba(hz(arp[k % 6] + 12)), 0.20, pan=0.3 * np.sin(k))
    if b >= 5:
        add(mus, at(b), bass(hz(root), nb * BEAT * 0.95, dec=1.2), 0.30)
        for k in range(int(nb * 4)):
            add(mus, at(b + k * 0.25), hat(0.03, 0.10 if k % 2 else 0.05), 1, pan=0.4)


section([('F', 4), ('Dm', 4), ('Bb', 4), ('C', 4)], 0, 22, s1)


# 段 2：13.2–20.7（拍 22–34.5）D 小调，紧张的断奏低音 + 滴答
def s2(name, b, nb):
    root, tones = chord(name)
    add(mus, at(b), pad([hz(x - 12) for x in tones], nb * BEAT, att=0.3, cutoff=900), 0.20)
    for k in range(int(nb * 2)):
        add(mus, at(b + k * 0.5), bass(hz(root), 0.22, dec=8), 0.32)
        add(mus, at(b + k * 0.5), tick(1800 if k % 2 else 2600, 0.12), 1, pan=-0.3 if k % 2 else 0.3)
    add(mus, at(b), bell(hz(tones[2] + 12), 1.6), 0.10, pan=0.2)


section([('Dm', 3), ('Bb', 3), ('Gm', 3), ('A', 3.5)], 22, 34.5, s2)
add(mus, 19.5, noise_sweep(1.2, 400, 9000, 1.0, 'rise'), 0.10)
t_r = tt(1.2)
add(mus, 19.5, np.sin(2 * np.pi * np.cumsum(220 * 2 ** (2 * t_r / 1.2)) / SR) * (t_r / 1.2) ** 2, 0.06)


# 段 3：21.0–30.0（拍 35–50）F 大调全编制
MEL3 = {'F': [72, 77, 81, 79], 'C': [76, 79, 76, 72], 'Dm': [74, 77, 81, 77], 'Bb': [74, 77, 82, 81]}


def s3(name, b, nb):
    root, tones = chord(name)
    add(mus, at(b), pad([hz(x) for x in tones] + [hz(tones[0] + 12)], nb * BEAT, att=0.05, cutoff=3200), 0.17)
    for k in range(int(nb)):
        add(mus, at(b + k), kick(), 0.42)
        if int(b + k - 35) % 2 == 1:
            add(mus, at(b + k), clap(), 0.20, pan=0.05)
        add(mus, at(b + k + 0.5), hat(0.05, 0.16), 1, pan=0.35)
    for k in range(int(nb * 2)):
        add(mus, at(b + k * 0.5), bass(hz(root if k % 2 == 0 else root + 12), 0.27, dec=5), 0.34)
    arp = [tones[0] + 12, tones[1] + 12, tones[2] + 12, tones[1] + 12]
    for k in range(int(nb * 4)):
        add(mus, at(b + k * 0.25), pluck(hz(arp[k % 4]), 0.25, bright=6), 0.10, pan=0.5 * np.sin(k * 0.7))
    mel = MEL3[name]
    for k in range(int(nb)):
        f = hz(mel[k % 4])
        n = int(0.55 * SR)
        add(mus, at(b + k), lp(saw(f, 0.55, nh=10, detune=(0, -5, 5)), 4000) * env_adsr(n, 0.01, 0.25, 0.5, 0.08, 0.45), 0.10, pan=-0.1)


section([('F', 4), ('C', 4), ('Dm', 4), ('Bb', 3)], 35, 50, s3)


# 段 4：30.0–37.2（拍 50–62）变薄
def s4(name, b, nb):
    root, tones = chord(name)
    add(mus, at(b), pad([hz(x) for x in tones], nb * BEAT, att=0.2, cutoff=1800), 0.14)
    add(mus, at(b), bass(hz(root), nb * BEAT * 0.9, dec=1.0), 0.30)
    add(mus, at(b), kick(0.7), 0.30)
    for k in range(int(nb)):
        add(mus, at(b + k), pluck(hz(tones[k % 3] + 12), 0.5, bright=4), 0.13, pan=0.3 * (k % 3 - 1))


section([('Bb', 3), ('C', 3), ('Am', 3), ('Dm', 3)], 50, 62, s4)


# 段 5：37.2–48.0（拍 62–80）G 大调芯片音
MEL5 = {'G': [79, 83, 86, 83, 79, 74, 79, 83], 'Em': [79, 76, 83, 79, 76, 71, 76, 79], 'C': [76, 79, 84, 79, 76, 72, 76, 79], 'D': [78, 81, 86, 81, 78, 74, 81, 86]}


def s5(name, b, nb):
    root, tones = chord(name)
    for k in range(int(nb * 4)):
        add(mus, at(b + k * 0.25), square(hz(tones[k % 3] + 12), 0.12, nh=9) * np.exp(-tt(0.12) * 18), 0.045, pan=0.4)
    for k in range(int(nb * 2)):
        add(mus, at(b + k * 0.5), tri(hz(root + (12 if k % 2 else 0)), 0.28) * np.exp(-tt(0.28) * 4), 0.30)
        add(mus, at(b + k * 0.5 + 0.25), hat(0.03, 0.12), 1, pan=-0.3)
    for k in range(int(nb)):
        if k % 2 == 0:
            add(mus, at(b + k), kick(0.8), 0.32)
        else:
            add(mus, at(b + k), clap(), 0.14)
    mel = MEL5[name]
    for k in range(int(nb * 2)):
        n = int(0.28 * SR)
        add(mus, at(b + k * 0.5), square(hz(mel[k % 8]), 0.28, nh=11, vib=0.15) * env_adsr(n, 0.005, 0.12, 0.6, 0.04, 0.24), 0.055, pan=-0.15)


section([('G', 4), ('Em', 4), ('C', 4), ('D', 4), ('G', 2)], 62, 80, s5)


# 段 6：48.0–57.0（拍 80–95）G 大调钟声收束；57–60 主和弦延音
def s6(name, b, nb):
    root, tones = chord(name)
    add(mus, at(b), pad([hz(x) for x in tones] + [hz(tones[1] + 12)], nb * BEAT, att=0.5, cutoff=2400), 0.18)
    add(mus, at(b), bass(hz(root), nb * BEAT * 0.95, dec=0.8), 0.30)
    for k in range(int(nb * 2)):
        add(mus, at(b + k * 0.5), bell(hz(tones[(k * 2) % 3] + 24), 1.2), 0.055, pan=0.5 * np.sin(k))
    for k in range(0, int(nb), 2):
        add(mus, at(b + k), kick(0.6), 0.26)


section([('C', 4), ('D', 4), ('Em', 4), ('C', 2), ('D', 1)], 80, 95, s6)
add(mus, 57.0, pad([hz(55), hz(59), hz(62), hz(67), hz(71)], 2.4, att=0.05, rel=0.6, cutoff=2600), 0.24)
add(mus, 57.0, bass(hz(43), 2.6, dec=0.6), 0.32)
for i, m in enumerate([79, 83, 86, 91]):
    add(mus, 57.0 + i * 0.15, bell(hz(m), 2.6), 0.08, pan=-0.4 + i * 0.25)

# 结尾 59.2–60 淡出
fade = np.ones(N)
i0, i1 = int(59.0 * SR), int(60.0 * SR)
fade[i0:i1] = np.linspace(1, 0, i1 - i0) ** 1.5
fade[i1:] = 0

# ---------- 音效（卡画面动作） ----------
for tc, k in [(0.4, 5), (0.8, 6), (1.2, 7)]:
    add(sfx, tc, blip(hz(84 + k), 0.15), 0.30, pan=0.1)
    add(sfx, tc - 0.28, noise_sweep(0.3, 800, 3000, 1, 'swell'), 0.05)
add(sfx, 2.25, noise_sweep(0.8, 300, 8000, 1, 'rise'), 0.22)                     # 推进
for c in range(8):
    add(sfx, 3.8 + c * 0.08, blip(hz(88 + c), 0.08), 0.12, pan=-0.6 + c * 0.17)    # 数字蹦出
for r in range(5):
    add(sfx, 6.0 + r * 0.2, bell(hz(91 + r * 2), 0.4), 0.07, pan=-0.3)             # 乘
    add(sfx, 7.1 + r * 0.16, noise_sweep(0.45, 1500, 5000, 1, 'swell'), 0.04, pan=0.4)
    add(sfx, 7.55 + r * 0.16, blip(hz(84 + r), 0.1), 0.15, pan=0.5)                # 加成一个数
add(sfx, 9.3, noise_sweep(0.55, 600, 4000, 1, 'swell'), 0.10)
add(sfx, 9.85, bell(hz(88), 1.8), 0.22)                                           # 光 落位
add(sfx, 9.85, bell(hz(95), 1.4), 0.10)
add(sfx, 10.4, noise_sweep(1.9, 6000, 300, 1, 'swell'), 0.16)                     # 拉远
for i in range(40):                                                              # 计数滚动
    u = i / 39
    tc = 10.8 + 1.4 * (1 - (1 - u) ** 0.5)
    add(sfx, tc, tick(1500 + 1500 * u, 0.35), 0.4)
add(sfx, 12.2, kick(0.8), 0.35)
add(sfx, 12.2, bell(hz(81), 1.2), 0.10)
add(sfx, 13.25, kick(0.9), 0.30)                                                 # CPU 升起
t_c = tt(0.2)
add(sfx, 14.0, hp(rng.standard_normal(len(t_c)), 2000) * np.exp(-t_c * 40), 0.12)  # 顶盖
add(sfx, 14.0, noise_sweep(0.7, 500, 3000, 1, 'swell'), 0.07)
for i in range(8):
    add(sfx, 14.6 + i * 0.05, blip(hz(79 + (i % 4) * 2), 0.1), 0.08, pan=-0.5 + i * 0.14)
# CPU 每核算完一道：轻滴答
t0 = 15.4
for k in range(int((21.0 - t0) / 0.3)):
    for c in range(8):
        tc = t0 + k * 0.3 + c * 0.0375 + 0.22
        if tc < 20.7:
            add(sfx, tc, tick(2000 + c * 150, 0.10), 1, pan=-0.6 + c * 0.17)
# 停半拍 20.7–21.0：把音乐静掉
g = np.ones(N)
a, b = int(20.66 * SR), int(21.0 * SR)
g[a - 1200:a] = np.linspace(1, 0, 1200)
g[a:b] = 0
mus *= g
# 甩镜 + 冲击
add(sfx, 20.9, noise_sweep(0.6, 1200, 6000, 1, 'swell'), 0.22, pan=-0.3)
add(sfx, 21.0, kick(1.2), 0.55)
add(sfx, 21.0, lp(rng.standard_normal(int(0.8 * SR)), 1200) * np.exp(-tt(0.8) * 5), 0.20)
add(sfx, 22.45, noise_sweep(1.2, 300, 12000, 1, 'swell'), 0.12)                  # 通电
for i in range(10):
    add(sfx, 22.45 + i * 0.1, bell(hz(84 + i * 2), 0.6), 0.03, pan=-0.8 + i * 0.18)
# 一起算：每 0.3 秒全片闪
for k in range(7):
    tc = 24.0 + k * 0.3
    for m in [72, 76, 79, 84]:
        add(sfx, tc, pluck(hz(m + 12), 0.25, bright=10), 0.05, pan=0.0)
    add(sfx, tc, noise_sweep(0.25, 4000, 9000, 1, 'fall'), 0.06)
for i in range(60):                                                              # 题雨
    add(sfx, 24.0 + rng.random() * 2.0, tick(3000 + rng.random() * 3000, 0.08), 1, pan=rng.random() * 1.6 - 0.8)
add(sfx, 25.95, bell(hz(84), 1.6), 0.18)                                          # 算完
add(sfx, 25.95, bell(hz(91), 1.4), 0.10)
add(sfx, 26.4, noise_sweep(0.6, 3000, 600, 1, 'swell'), 0.08)
add(sfx, 28.2, blip(hz(79), 0.2), 0.10)
# 谁也不用等谁：同时到 → 和弦一齐响
for s0, s1 in [(30.6, 31.4), (32.1, 32.9)]:
    add(sfx, s0, noise_sweep(s1 - s0, 800, 5000, 1, 'rise'), 0.08)
    for m in [65, 69, 72, 77, 81, 84]:
        add(sfx, s1, pluck(hz(m + 12), 0.6, bright=5), 0.07)
# 一步等一步：单个滴
for k in range(6):
    add(sfx, 33.6 + k * 0.6, blip(hz(76 + k * 2), 0.12), 0.18, pan=-0.6 + k * 0.24)
# 像素同时亮
for i in range(50):
    add(sfx, 37.62 + rng.random() * 0.26, blip(hz(84 + rng.integers(0, 12)), 0.05), 0.05, pan=rng.random() * 1.6 - 0.8)
add(sfx, 40.2, noise_sweep(0.45, 800, 4000, 1, 'swell'), 0.10)
add(sfx, 43.6, kick(1.0), 0.40)                                                  # 2012
add(sfx, 43.6, bell(hz(79), 1.5), 0.12)
add(sfx, 45.0, blip(hz(84), 0.12), 0.18)
add(sfx, 46.3, bell(hz(88), 1.4), 0.20)                                           # 猫 ✓
add(sfx, 46.3, bell(hz(95), 1.0), 0.08)
add(sfx, 48.5, noise_sweep(0.5, 6000, 900, 1, 'rise'), 0.12)                     # 光落下
add(sfx, 49.0, bell(hz(91), 2.0), 0.18)
for i in range(6):
    add(sfx, 49.0 + i * 0.05, bell(hz(96 + i), 0.8), 0.03, pan=-0.6 + i * 0.24)
add(sfx, 50.4, kick(0.9), 0.30)
add(sfx, 52.8, kick(1.0), 0.36)
add(sfx, 52.8, bell(hz(86), 1.6), 0.12)
add(sfx, 57.0, noise_sweep(1.6, 2000, 12000, 1, 'swell'), 0.07)

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
