#!/usr/bin/env python3
"""EP01 配乐和音效，全部用代码合成（无第三方素材，无版权问题）。读 remotion/src/timing.json 对齐旁白。

  python3 music.py        → remotion/public/audio/music.wav、sfx.wav，并把 remotion/src/audio.json 打开

配乐分四段，各换调性、和声和织体（工作室规则：不要一个循环铺到底，揭晓前停半拍）：
  A 钩子      D 小调，低垫音 + 稀疏的脉冲，悬念
  B/C 讲解    F 大调 → C 段转 G 大调；拨弦琶音（100 BPM 八分音符）；2×4+3×5 那几秒只留垫音，给讲解让路
  D 揭晓      停半拍 → A 小调到 C 大调，加贝斯和更密的琶音；D8 前再停半拍，落在 C 大调主和弦上
  E 过渡      挂留和弦，留一个没解决的问题，最后淡出
"""
import json, os
import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(HERE)
T = json.load(open(os.path.join(EP, 'remotion', 'src', 'timing.json')))
L = {l['id']: l for l in T['lines']}
DUR = T['total'] + 0.4
N = int(DUR * SR) + SR
rng = np.random.default_rng(7)

def cue(i, at='start'): return L[i][at]
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
def env(n, a, r, sustain=1.0):
    e = np.ones(n) * sustain
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, sustain, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e
def add(buf, t, sig, g=1.0):
    i = int(t * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(sig)); buf[i:j] += sig[:j - i] * g

def pad(notes, dur, g=0.12):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for k, m in enumerate(notes):
        fr = midi(m)
        for det in (-0.12, 0.0, 0.12):                       # 三个略微失谐的音，柔和
            s += np.sin(2 * np.pi * fr * (1 + det / 100) * t + k) * (0.6 if det else 1.0)
            s += 0.18 * np.sin(2 * np.pi * 2 * fr * (1 + det / 100) * t)
    s *= env(n, min(1.2, dur / 3), min(1.5, dur / 3)) / (len(notes) * 2.2)
    return s * g

def pluck(m, dur=0.6, g=0.2, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; fr = midi(m)
    s = sum((0.6 ** h) * np.sin(2 * np.pi * fr * (h + 1) * t) * np.exp(-t * (3 + h * 2.5 / bright)) for h in range(5))
    return s * env(n, 0.004, 0.08) * g

def bell(m, dur=1.6, g=0.15):
    n = int(dur * SR); t = np.arange(n) / SR; fr = midi(m)
    s = np.sin(2 * np.pi * fr * t) * np.exp(-t * 2.2) + 0.35 * np.sin(2 * np.pi * fr * 2.76 * t) * np.exp(-t * 4) + 0.2 * np.sin(2 * np.pi * fr * 5.4 * t) * np.exp(-t * 7)
    return s * env(n, 0.002, 0.2) * g

def bass(m, dur, g=0.22):
    n = int(dur * SR); t = np.arange(n) / SR; fr = midi(m)
    s = np.sin(2 * np.pi * fr * t) + 0.3 * np.sin(2 * np.pi * 2 * fr * t) * np.exp(-t * 3)
    return s * env(n, 0.01, 0.15) * np.exp(-t * 0.6) * g

def noise_burst(dur, g, lo=200, hi=6000, a=0.005, decay=12.0):
    n = int(dur * SR); x = rng.standard_normal(n)
    X = np.fft.rfft(x); fq = np.fft.rfftfreq(n, 1 / SR); X[(fq < lo) | (fq > hi)] = 0
    x = np.fft.irfft(X, n); x /= np.max(np.abs(x)) + 1e-9
    t = np.arange(n) / SR
    return x * env(n, a, 0.02) * np.exp(-t * decay) * g

def whoosh(dur=0.5, g=0.25, up=True):
    n = int(dur * SR); x = rng.standard_normal(n); t = np.arange(n) / SR
    out = np.zeros(n); y = 0.0
    cut = np.linspace(0.02, 0.35, n) if up else np.linspace(0.35, 0.02, n)   # 一阶低通，截止频率扫动
    for i in range(n): y += cut[i] * (x[i] - y); out[i] = y
    out /= np.max(np.abs(out)) + 1e-9
    return out * np.sin(np.pi * t / dur) ** 1.5 * g

def tick(g=0.18, f0=1800):
    n = int(0.06 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f0 * t) * np.exp(-t * 90) * g

def reverb(x, wet=0.25, length=2.2):
    n = int(length * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 3.0); ir[0] = 0
    k = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, k) * np.fft.rfft(ir, k), k)[:len(x)]
    y /= np.max(np.abs(y)) + 1e-9
    return x * (1 - wet) + y * wet * np.max(np.abs(x))

music = np.zeros(N); sfx = np.zeros(N)
beat = 60 / 100

# ---------------- A：D 小调，悬念 ----------------
tB = cue('B1') - 0.35
add(music, 0.0, pad([50, 57, 60, 65], tB * 0.5 + 0.3, 0.16))            # Dm(add9)
add(music, tB * 0.5, pad([46, 53, 57, 62], tB * 0.3 + 0.3, 0.16))       # B♭（甩到机房）
add(music, tB * 0.78, pad([48, 55, 60, 64], tB * 0.22 + 0.6, 0.15))     # C/E 色彩，往 F 大调走
for k in range(int(tB / beat)):
    t = k * beat
    if t > 1.0: add(music, t, pluck(38 if k % 4 == 0 else 50, 0.25, 0.09 if k % 4 == 0 else 0.04))
# ---------------- B：F 大调，拨弦琶音 ----------------
tC = cue('C1') - 0.35
prog_F = [[53, 57, 60, 64], [52, 55, 60, 67], [50, 57, 60, 65], [46, 53, 57, 62]]   # Fmaj7  C/E  Dm7  B♭maj7
bar = 4 * beat; t = tB; k = 0
while t < tC - 0.05:
    ch = prog_F[k % 4]
    add(music, t, pad([c - 12 if i == 0 else c for i, c in enumerate(ch)], bar + 0.4, 0.10))
    for e in range(8):
        te = t + e * beat / 2
        if te < tC - 0.1: add(music, te, pluck(ch[[0, 1, 2, 3, 2, 1, 2, 3][e]] + 12, 0.5, 0.075))
    t += bar; k += 1
# ---------------- C：转 G 大调；讲 2×4+3×5 时只留垫音 ----------------
tD = cue('D1') - 0.3
quiet_a, quiet_b = cue('C4') - 0.4, cue('C5', 'end') + 0.4
prog_G = [[55, 59, 62, 66], [54, 57, 62, 69], [52, 55, 59, 62], [48, 55, 59, 64]]   # Gmaj7  D/F#  Em  Cmaj7
t = tC; k = 0
while t < tD - 0.55:
    ch = prog_G[k % 4]
    add(music, t, pad([ch[0] - 12] + ch[1:], bar + 0.4, 0.10))
    for e in range(8):
        te = t + e * beat / 2
        if te < tD - 0.6 and not (quiet_a < te < quiet_b):
            add(music, te, bell(ch[[0, 2, 1, 3, 2, 1, 3, 2][e]] + 12, 0.9, 0.035))
    t += bar; k += 1
# 半拍停顿 → D
# ---------------- D：A 小调 → C 大调，更满 ----------------
t8 = cue('D7')
prog_Am = [[45, 52, 57, 60, 64], [41, 53, 57, 60, 65], [43, 55, 59, 62, 67], [40, 52, 56, 59, 64]]  # Am  F  G  E
t = tD + 0.05; k = 0
while t < t8 - 0.45:
    ch = prog_Am[k % 4]
    add(music, t, pad(ch[1:], bar + 0.3, 0.12))
    add(music, t, bass(ch[0] - 12 + 12, bar * 0.95, 0.16))
    for e in range(8):
        te = t + e * beat / 2
        if te < t8 - 0.5: add(music, te, pluck(ch[1 + [0, 1, 2, 3, 2, 1, 3, 2][e]] + 12, 0.45, 0.08, bright=1.6))
    t += bar; k += 1
add(music, t8, pad([48, 55, 60, 64, 67], 4.4, 0.2))           # 落在 C 大调
add(music, t8, bass(36, 3.5, 0.22))
add(music, t8, bell(72, 2.5, 0.08)); add(music, t8 + 0.02, bell(76, 2.5, 0.06)); add(music, t8 + 0.04, bell(79, 2.5, 0.05))
# ---------------- E：挂留和弦，问题没解决 ----------------
tE = cue('E1') - 0.45
add(music, tE, pad([50, 55, 57, 62], 5.5, 0.14))              # Dsus4
add(music, tE + 5.2, pad([46, 53, 55, 60], DUR - tE - 5.2, 0.14))   # B♭sus2，开放结尾
for k in range(int((DUR - tE) / beat)):
    tt = tE + k * beat
    if k % 2 == 0: add(music, tt, pluck(62 if k % 4 == 0 else 57, 0.4, 0.035))
music[int((DUR - 2.0) * SR):int(DUR * SR)] *= np.linspace(1, 0, int(DUR * SR) - int((DUR - 2.0) * SR))
music[int(DUR * SR):] = 0
music = reverb(music, 0.3)

# ---------------- 音效（v02：少而准，只卡在关键动作上） ----------------
fps = 30
add(sfx, cue('A1') + 1.3, whoosh(0.45, 0.12)); add(sfx, cue('A1') + 1.8, bell(84, 1.0, 0.07))      # 光落到芯片
add(sfx, cue('A2') - 0.33, whoosh(0.6, 0.28))                                                         # 甩到机房
add(sfx, tB, whoosh(0.5, 0.14))
B4 = cue('B4')
for i in range(6): add(sfx, B4 + 0.3 + i * 4 / fps, tick(0.08, 1300))                                # 排队：一块一块
add(sfx, B4 + 1.55, noise_burst(0.35, 0.10, 1500, 9000, a=0.01, decay=8)); add(sfx, B4 + 1.55, bell(79, 1.2, 0.08))   # 一起算
add(sfx, tC, whoosh(0.45, 0.14))
C2, C4, C5, C6 = cue('C2'), cue('C4'), cue('C5'), cue('C6')
add(sfx, C2 + 0.2, noise_burst(0.08, 0.12, 2000, 9000, decay=40))                                    # 切段
add(sfx, C4 + 0.55, tick(0.12, 1400)); add(sfx, C4 + 1.3, tick(0.12, 1500)); add(sfx, C4 + 2.15, bell(84, 1.4, 0.12))
add(sfx, C5 + 1.5, tick(0.12, 1400)); add(sfx, C5 + 1.85, tick(0.12, 1500)); add(sfx, C5 + 2.6, bell(81, 1.4, 0.11))
add(sfx, C6 + 2.0, pad([67, 71, 74], 0.9, 0.09))                                                      # 很多行一起出结果
add(sfx, tD - 0.35, whoosh(0.4, 0.14))
D2, D6, D7 = cue('D2'), cue('D6'), cue('D7')
add(sfx, D2 + 2.3, whoosh(0.5, 0.1, up=False)); add(sfx, D2 + 3.2, bell(76, 1.4, 0.08))
add(sfx, D6 + 1.2 + 22 / fps, bass(31, 0.6, 0.22)); add(sfx, D6 + 1.2 + 22 / fps, noise_burst(0.08, 0.1, 100, 1200, decay=30))   # 卡进去
add(sfx, D7 + 1.6, noise_burst(0.25, 0.10, 600, 5000, a=0.01, decay=10))                               # 划掉
E1, E4, E5 = cue('E1'), cue('E4'), cue('E5')
add(sfx, E1 + 3.0 - 0.9, whoosh(0.9, 0.11))
add(sfx, E4, bell(79, 1.2, 0.07)); add(sfx, E5, bass(38, 1.2, 0.13))
sfx = reverb(sfx, 0.18, 1.4)

os.makedirs(os.path.join(EP, 'remotion', 'public', 'audio'), exist_ok=True)
def write(path, x):
    import wave
    x = x[:int(DUR * SR)]
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype('<i2').tobytes())
write(os.path.join(EP, 'remotion', 'public', 'audio', 'music.wav'), music)
write(os.path.join(EP, 'remotion', 'public', 'audio', 'sfx.wav'), sfx)
# 电平：旁白已统一到 -20 LUFS；音乐压到旁白下约 12 dB（≈ -32 LUFS），音效 ≈ -27 LUFS。增益在下面用 ffmpeg 量过再写进 audio.json
with open(os.path.join(EP, 'remotion', 'src', 'audio.json'), 'w') as fo: json.dump(dict(music=True, sfx=True, musicGain=0.28, sfxGain=0.35), fo)
print('ok', DUR)
