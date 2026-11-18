#!/usr/bin/env python3
"""一语道破 EP01 DIRECTOR-LOCKED 60s：原创器乐 + 音效，全部代码合成，没有任何人声 / TTS。
时间点和 remotion/src60/lib/plan.ts 的 T 对齐（下面 T 的数值是照抄的，改画面时一起改）。

  python3 dl60_audio.py   → remotion/public/dl60/mix.wav（48 kHz 立体声，未归一；master60.sh 再归一到 -14 LUFS）

段落（每段换调性 / 和声 / 织体；揭晓前收一下再进）：
  0–5   SHOT 01  D 小调低垫音 + 很轻的机械质感（滤波噪声 + 低频嗡），1.5 秒一记低频音头
  5–12  SHOT 02  F 大调，稀疏的拨弦；单个计算 = 干脆的一声 click
  12.6  母题首次出现：并行计算那一刻，四音拨弦母题（A–C–D–F）卡在 100 BPM 的十六分音符上，一组 click 收进一记软的落点
  14–17 横移：空气声，不用街机音效
  17–30 SHOT 03  E 小调 9 和弦垫音 + 很轻的数字脉冲；选数、出数各一声；「23」一声干净的钟音
  30–42 SHOT 04  A 小调 → C 大调，加贝斯；两个结果同时亮 = 两声同时；五个结果 = 五声和弦
  42–44 SHOT 05  收一下（只剩垫音）→ 44 秒揭晓：克制的低频 + 母题以完整配器回来（D 大调）
  48.5–51 真芯片浮现：上行的长音
  51–57 SHOT 06  叠加层分组亮起的轻钟音 → 57 秒 D 大调主和弦解决，留白到结束
"""
import os, wave
import numpy as np

SR = 48000
DUR = 60.0
N = int(DUR * SR)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'remotion', 'public', 'dl60', 'mix.wav')
rng = np.random.default_rng(11)
T = dict(q1=0.35, q2=1.5, reveal=4.35, sel=6.3, drain1=7.4, tile1=8.05, in1=8.6, comp1=9.15, out1=9.85, lit1=10.2,
         pull=10.8, tilesAll=11.35, cue=12.2, compAll=12.6, outAll=13.1, litAll=13.4, lift=14.0, fly0=14.3, fly1=16.9,
         type0=16.15, split=17.4, nums=18.15, select=20.0, center=20.8, params=22.55, f1=23.9, f2=24.45, prod=25.15, sum=25.8,
         contract=27.0, row2=28.8, op2=30.4, both=33.0, rows=36.2, all=37.6, pullAI=39.0, act1=42.3, act2=43.25, act3=44.4, reveal5=44.0,
         stream0=45.6, lock=48.5, plateFull=50.3, g1=51.3, g2=52.1, g3=52.9, recede=54.0, ansQ=56.8, ansA=57.5, sig=58.5)

def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
def env(n, a, r, sus=1.0):
    e = np.ones(n) * sus; na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, sus, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e
def add(buf, t, sig, g=1.0, pan=0.0):
    i = int(t * SR)
    if i >= buf.shape[1] or i < 0: return
    j = min(buf.shape[1], i + len(sig)); s = sig[:j - i] * g
    buf[0, i:j] += s * np.sqrt(0.5 * (1 - pan)); buf[1, i:j] += s * np.sqrt(0.5 * (1 + pan))

def pad(notes, dur, g=0.12, bright=0.18, att=1.2, rel=1.5):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for k, m in enumerate(notes):
        fr = midi(m)
        for det in (-0.1, 0.0, 0.1):
            s += np.sin(2 * np.pi * fr * (1 + det / 100) * t + k) * (0.6 if det else 1.0)
            s += bright * np.sin(2 * np.pi * 2 * fr * (1 + det / 100) * t)
    return s * env(n, min(att, dur / 3), min(rel, dur / 3)) / (len(notes) * 2.2) * g
def pluck(m, dur=0.6, g=0.2, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; fr = midi(m)
    s = sum((0.6 ** h) * np.sin(2 * np.pi * fr * (h + 1) * t) * np.exp(-t * (3 + h * 2.5 / bright)) for h in range(5))
    return s * env(n, 0.004, 0.08) * g
def bell(m, dur=1.6, g=0.15):
    n = int(dur * SR); t = np.arange(n) / SR; fr = midi(m)
    s = np.sin(2 * np.pi * fr * t) * np.exp(-t * 2.2) + 0.35 * np.sin(2 * np.pi * fr * 2.76 * t) * np.exp(-t * 4) + 0.18 * np.sin(2 * np.pi * fr * 5.4 * t) * np.exp(-t * 7)
    return s * env(n, 0.002, 0.2) * g
def bass(m, dur, g=0.22):
    n = int(dur * SR); t = np.arange(n) / SR; fr = midi(m)
    s = np.sin(2 * np.pi * fr * t) + 0.3 * np.sin(2 * np.pi * 2 * fr * t) * np.exp(-t * 3)
    return s * env(n, 0.01, 0.2) * np.exp(-t * 0.5) * g
def bandnoise(dur, lo, hi):
    n = int(dur * SR); X = np.fft.rfft(rng.standard_normal(n)); fq = np.fft.rfftfreq(n, 1 / SR)
    X[(fq < lo) | (fq > hi)] = 0; x = np.fft.irfft(X, n); return x / (np.max(np.abs(x)) + 1e-9)
def click(g=0.2, f0=2600, dur=0.035):       # 干脆的「计算」声：短促的高频衰减 + 一点噪声
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f0 * t) * 0.7 + bandnoise(dur, 2000, 9000) * 0.3) * np.exp(-t * 160) * g
def thump(g=0.5, f0=55, dur=1.6):           # 低频音头：正弦下滑 + 柔和的包络
    n = int(dur * SR); t = np.arange(n) / SR
    f = f0 * (1 + 0.8 * np.exp(-t * 18)); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 2.6) * env(n, 0.004, 0.3) * g
def air(dur, g=0.12, up=True):              # 镜头运动的空气声（滤波扫动的噪声）
    n = int(dur * SR); x = rng.standard_normal(n); out = np.zeros(n); y = 0.0
    cut = np.linspace(0.015, 0.12, n) if up else np.linspace(0.12, 0.015, n)
    for i in range(n): y += cut[i] * (x[i] - y); out[i] = y
    out /= np.max(np.abs(out)) + 1e-9; t = np.arange(n) / SR
    return out * np.sin(np.pi * t / dur) ** 1.6 * g
def blip(m, g=0.08, dur=0.12):              # 数字脉冲：短正弦
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * midi(m) * t) * np.exp(-t * 35) * env(n, 0.002, 0.02) * g
def reverb(x, wet=0.22, length=2.4):
    n = int(length * SR); t = np.arange(n) / SR
    out = np.zeros_like(x)
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-t * 2.8); ir[0] = 0
        k = 1 << int(np.ceil(np.log2(x.shape[1] + n)))
        y = np.fft.irfft(np.fft.rfft(x[ch], k) * np.fft.rfft(ir, k), k)[:x.shape[1]]
        out[ch] = y / (np.max(np.abs(y)) + 1e-9) * np.max(np.abs(x[ch]))
    return x * (1 - wet) + out * wet

music = np.zeros((2, N)); sfx = np.zeros((2, N))
beat = 0.6                                  # 100 BPM
MOTIF = [57, 60, 62, 65]                    # A C D F：母题

# ---------------- SHOT 01：D 小调悬念 + 机械质感 ----------------
add(music, 0.0, pad([38, 50, 57, 60, 65], 5.6, 0.20, att=0.05, rel=1.2))          # Dm(add9)，第一帧就有声音
hum = bandnoise(5.4, 60, 400) * 0.5 + np.sin(2 * np.pi * 49 * np.arange(int(5.4 * SR)) / SR) * 0.5
add(sfx, 0.0, hum * env(len(hum), 0.3, 1.2) * np.linspace(0.6, 1.0, len(hum)), 0.05)  # 推镜头时很轻的机械底噪
add(sfx, T['q2'], thump(0.55, 46), 1.0)                                               # 问题出现：一记克制的低频音头
add(music, T['q2'], bell(62, 2.4, 0.06), 1.0, -0.2)
add(sfx, 3.9, air(1.6, 0.10, up=True))                                                # 推向芯片方框
add(sfx, T['reveal'] + 0.1, bell(69, 1.8, 0.05), 1.0, 0.2)                            # 视口打开

# ---------------- SHOT 02：F 大调，稀疏拨弦 → 母题 ----------------
prog_F = [[53, 57, 60, 64], [50, 57, 60, 65], [46, 53, 57, 62], [48, 55, 60, 64]]   # Fmaj7 Dm7 B♭maj7 C
t = 5.0; k = 0
while t < 14.2:
    ch = prog_F[k % 4]; bar = 4 * beat
    add(music, t, pad([ch[0] - 12] + ch[1:], bar + 0.5, 0.11))
    if t < 12.0:                                                                       # 母题出现前：每拍只一个音，留空间
        for e in range(4):
            add(music, t + e * beat, pluck(ch[[0, 2, 1, 3][e]] + 12, 0.5, 0.05), 1.0, 0.15 * (e - 1.5))
    t += bar; k += 1
add(sfx, T['sel'], blip(81, 0.05), 1.0, -0.1)                                          # 选中地块
add(sfx, T['in1'], blip(86, 0.04), 1.0, 0.3)                                           # 输入进方块
for i in range(5): add(sfx, T['comp1'] + i * 0.14, click(0.16 if i < 4 else 0.22), 1.0, -0.1)   # 单个计算：干脆的几声
add(sfx, T['lit1'], bell(72, 1.2, 0.06))                                               # 地块亮
# 并行：同一时刻一组整齐的 click（十六分音符）→ 一记软落点；母题第一次出现
add(sfx, T['cue'], blip(84, 0.05), 1.0, 0.3)
for i in range(8):
    tt = T['compAll'] + i * beat / 4 * 0.8
    for p in (-0.5, 0.0, 0.5): add(sfx, tt + 0.004 * (p + 1), click(0.09, 2400 + 300 * p), 1.0, p)
add(sfx, T['litAll'], thump(0.35, 62, 1.2)); add(music, T['litAll'], pad([53, 60, 65, 69], 1.8, 0.12, att=0.02))
for i, m in enumerate(MOTIF + [69, 65]):
    add(music, T['compAll'] + i * beat / 2, pluck(m + 12, 0.7, 0.09, bright=1.4), 1.0, 0.2 * np.sin(i))
# 横移：空气声
add(sfx, T['fly0'], air(2.8, 0.12, up=False))

# ---------------- SHOT 03：E 小调 9，数字脉冲 ----------------
add(music, 16.6, pad([40, 52, 59, 62, 66], 7.2, 0.12, att=1.5))                        # Em9
add(music, 23.4, pad([36, 52, 55, 59, 62], 4.4, 0.11, att=1.2))                        # Cmaj9
add(music, 27.4, pad([38, 54, 57, 62, 64], 3.0, 0.11, att=0.8))                        # D6/9 → 进 SHOT 04
for i in range(6): add(sfx, T['type0'] + i * 0.1, click(0.05, 3400, 0.02), 1.0, 0.1 * i - 0.25)   # 打字
add(sfx, T['split'], air(0.7, 0.05))
for k in range(4): add(sfx, T['nums'] + k * 0.35, blip(76 + 3 * k, 0.05), 1.0, -0.4 + 0.27 * k)
add(sfx, T['select'], blip(83, 0.08)); add(sfx, T['select'] + 0.06, blip(88, 0.05))   # 选中 [2, 3]
add(sfx, T['center'], air(1.0, 0.05))
add(sfx, T['params'] + 0.1, blip(79, 0.06), 1.0, 0.4)
for tt, m in ((T['f1'], 76), (T['f1'] + 0.3, 79), (T['f2'], 78), (T['f2'] + 0.3, 81)): add(sfx, tt, blip(m, 0.05))
add(sfx, T['prod'], blip(83, 0.06)); add(sfx, T['prod'] + 0.05, blip(86, 0.05))
for m, d in ((76, 0.0), (79, 0.012), (83, 0.024)): add(sfx, T['sum'] + 0.3 + d, bell(m, 2.0, 0.07))   # 「23」：干净的一声
add(sfx, T['contract'], air(0.9, 0.05))
add(sfx, T['contract'] + 0.9, click(0.12, 2200))
t = 17.6
while t < 29.8:
    if not (T['f1'] - 0.2 < t < T['sum'] + 1.0): add(music, t, blip(64 if int(t / beat) % 4 else 52, 0.018, 0.09), 1.0, 0.2)
    t += beat / 2

# ---------------- SHOT 04：A 小调 → C 大调，加贝斯 ----------------
prog_Am = [[45, 52, 57, 60, 64], [41, 53, 57, 60, 65], [43, 55, 59, 62, 67], [48, 55, 60, 64, 67]]   # Am F G C
t = 30.0; k = 0
while t < 42.0:
    ch = prog_Am[k % 4]; bar = 4 * beat
    add(music, t, pad(ch[1:], bar + 0.4, 0.11))
    add(music, t, bass(ch[0] - 12 + 12 if ch[0] < 45 else ch[0] - 12, bar * 0.95, 0.12 + 0.05 * (t > 36)))
    if t > 33.0:
        for e in range(8):
            te = t + e * beat / 2
            if te < 41.8: add(music, te, bell(ch[1 + [0, 1, 2, 3, 2, 1, 3, 2][e]] + 12, 0.7, 0.022 + 0.01 * (t > 36)), 1.0, 0.3 * np.sin(e))
    t += bar; k += 1
add(sfx, T['row2'] + 0.3, blip(79, 0.05), 1.0, 0.4)
add(sfx, T['op2'], blip(76, 0.04)); add(sfx, 31.25, blip(81, 0.04)); add(sfx, 31.7, blip(83, 0.04))
add(sfx, 32.4, bell(81, 1.4, 0.06))                                                   # 「20」
for p in (-0.3, 0.3): add(sfx, T['both'] + 0.05, blip(79, 0.04), 1.0, p)
add(sfx, 34.1, bell(76, 1.6, 0.07), 1.0, -0.3); add(sfx, 34.1, bell(81, 1.6, 0.07), 1.0, 0.3)   # 两个结果同时亮：两声同时
for i in range(3): add(sfx, T['rows'] + 0.25 * i + 0.4, click(0.06, 2000 + 200 * i))
for i, m in enumerate((72, 76, 79, 83, 88)): add(sfx, 38.7, bell(m, 1.8, 0.05), 1.0, -0.6 + 0.3 * i)    # 五个结果：一个和弦
add(sfx, T['pullAI'], air(3.0, 0.08, up=False))

# ---------------- SHOT 05：收 → 揭晓 → 母题完整回来（D 大调） ----------------
add(music, 42.0, pad([43, 50, 55, 59, 62], 2.2, 0.08, att=0.3, rel=1.0))              # 只剩垫音（强度降下来）
for i in range(6): add(sfx, T['act1'] + i * 0.09, click(0.05, 2400), 1.0, -0.4 + 0.16 * i)
for i in range(6): add(sfx, T['act2'] + i * 0.09, click(0.05, 2600), 1.0, 0.4 - 0.16 * i)
for i in range(8): add(sfx, T['act3'] + i * 0.07, click(0.045, 2500), 1.0, -0.5 + 0.14 * i)
add(sfx, T['reveal5'], thump(0.5, 49, 2.0))                                           # 揭晓：克制的低频
add(music, T['reveal5'], bell(74, 2.6, 0.06)); add(music, T['reveal5'] + 0.015, bell(78, 2.6, 0.05)); add(music, T['reveal5'] + 0.03, bell(81, 2.6, 0.045))
prog_D = [[50, 57, 62, 66, 69], [47, 54, 59, 62, 66], [43, 55, 59, 62, 67], [45, 57, 61, 64, 69]]     # D Bm G A
t = T['reveal5']; k = 0
while t < 51.0:
    ch = prog_D[k % 4]; bar = 4 * beat
    add(music, t, pad(ch[1:], bar + 0.4, 0.14))
    add(music, t, bass(ch[0] - 12, bar * 0.95, 0.15))
    for i, m in enumerate(MOTIF + [69, 65, 62, 60]):                                   # 母题，配器更满：拨弦 + 高八度钟音
        te = t + i * beat / 2
        if te < 50.9:
            mm = m + 1 if m in (60, 65) else m                                         # 移到 D 大调（C→C#、F→F#）
            add(music, te, pluck(mm + 12, 0.6, 0.075, bright=1.6), 1.0, 0.25 * np.sin(i))
            if i % 2 == 0: add(music, te, bell(mm + 24, 0.8, 0.018), 1.0, -0.25 * np.sin(i))
    t += bar; k += 1
for j in range(20): add(sfx, T['stream0'] + 1.35 + j * 0.06 + (j % 2) * 0.03, click(0.035, 1800 + 60 * (j % 5)), 1.0, -0.5 + 0.05 * j)   # 方块落进格子
add(sfx, T['lock'], air(2.2, 0.08, up=True))
add(music, T['lock'], pad([62, 66, 69, 74], 3.0, 0.07, att=1.6))                      # 真芯片浮现：上行的长音

# ---------------- SHOT 06：分组亮起 → 解决 ----------------
add(music, 51.0, pad([50, 57, 62, 66], 6.2, 0.11, att=0.6))
for tt, ms in ((T['g1'], (74, 78)), (T['g2'], (76, 81)), (T['g3'], (74, 78, 81, 86))):
    for i, m in enumerate(ms): add(sfx, tt + 0.01 * i, bell(m, 1.4, 0.045), 1.0, -0.3 + 0.2 * i)
add(sfx, T['recede'], air(2.2, 0.05, up=False))
add(music, 57.0, pad([38, 50, 57, 62, 66, 69], 3.0, 0.18, att=0.15, rel=2.4))          # D 大调主和弦：解决
add(music, 57.0, bass(38, 2.9, 0.14))
add(music, 57.0, bell(74, 2.8, 0.05))
add(sfx, T['sig'], bell(86, 1.4, 0.03))

mix = reverb(music, 0.24) * 0.9 + reverb(sfx, 0.12)
fade = np.ones(N); nf = int(0.5 * SR); fade[-nf:] = np.linspace(1, 0, nf) ** 1.5
mix *= fade
mix /= np.max(np.abs(mix)) + 1e-9; mix *= 0.89
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix.T * 32767).astype('<i2').tobytes())
print('wrote', os.path.abspath(OUT), f'{N / SR:.1f}s')
