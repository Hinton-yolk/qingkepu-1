# 抖音拆解版配乐 + 音效 + 混音：python3 score_split.py s1 → audio/s1_mix.wav（-14 LUFS 之前的混音，出片时再整体对响度）
# 沿用系列音色（正弦 + 锯齿铺底、玻璃琶音、木质拨弦、低音），每条换调：s1 D 小调、s2 E 小调、s3 F 大调。
# 三段织体：开头（低音脉冲 + 上升噪声）/ 讲解（玻璃琶音十六分 + 轻鼓）/ 揭晓（四拍底鼓 + 亮琶音）；揭晓的那一下之前停半拍。
# 节拍：在 96–112 BPM 里选一个，让高潮那一下正好落在拍点上；时间点全部读 代码工程/split/sN.json（和画面同一份）。
import json, sys, wave, numpy as np
from scipy.signal import butter, lfilter
N_ = sys.argv[1]; D = json.load(open(f'代码工程/split/{N_}.json', encoding='utf-8'))
SR, DUR = 48000, D['dur']; N = int(SR * (DUR + 0.5)); rs = np.random.default_rng(7)
L = {l['id']: l for l in D['lines']}
def kw(i, w, k=0):
    l = L[i]; j = -1
    for _ in range(k + 1): j = l['text'].index(w, j + 1)
    return l['ch'][j]
first = lambda seg: next(l['t0'] for l in D['lines'] if l['seg'] == seg)
tE, tR, tZ = first('explain') - 0.3, first('reveal') - 0.3, [s for s in D['shots'] if s['kind'] == 'take'][0]['t0']
CFG = {
 's1': lambda: dict(key='Dm', prog=[('Dm', [50, 53, 57, 62]), ('Bb', [46, 50, 53, 58]), ('F', [45, 48, 53, 57]), ('C', [43, 48, 52, 55])], root=[38, 34, 41, 36], hit=kw('p05', '拼进'), pre=kw('p05', '晚到半步') - 0.1),
 's2': lambda: dict(key='Em', prog=[('Em', [52, 55, 59, 64]), ('C', [48, 52, 55, 60]), ('G', [47, 50, 55, 59]), ('D', [50, 54, 57, 62])], root=[40, 36, 43, 38], hit=kw('q06', '踩准'), pre=None),
 's3': lambda: dict(key='F', prog=[('F', [53, 57, 60, 65]), ('C', [52, 55, 60, 64]), ('Dm', [50, 53, 57, 62]), ('Bb', [50, 53, 58, 62])], root=[41, 36, 38, 34], hit=kw('k07', '到手'), pre=None),
}[N_]()
HIT = CFG['hit']
BPM = min(np.arange(96, 112.01, 0.5), key=lambda b: abs((HIT / (60 / b)) - round(HIT / (60 / b))))
BEAT = 60 / BPM; BAR = 4 * BEAT
mus = np.zeros((2, N)); fx = np.zeros((2, N))
def add(buf, sig, t, g=1.0, pan=0.0):
    i0 = int(round(t * SR)); l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
    if i0 >= N or i0 + len(sig) <= 0: return
    a, b = max(0, i0), min(N, i0 + len(sig)); s = sig[a - i0:b - i0]; buf[0, a:b] += s * g * l; buf[1, a:b] += s * g * r
T = lambda d: np.arange(int(d * SR)) / SR
def lp(x, fc, o=2): b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def bp(x, lo, hi, o=2): b, a = butter(o, [lo / (SR / 2), min(hi, SR / 2 - 200) / (SR / 2)], 'band'); return lfilter(b, a, x)
midi = lambda m: 440 * 2 ** ((m - 69) / 12); saw = lambda f, t: 2 * ((f * t) % 1) - 1
def fade(x, a=0.01, b=0.05):
    ka, kb = int(a * SR), int(b * SR); x = x.copy()
    if ka: x[:ka] *= np.linspace(0, 1, ka)
    if kb: x[-kb:] *= np.linspace(1, 0, kb)
    return x
def gl(f0, f1, d): n = int(d * SR); return np.sin(2 * np.pi * np.cumsum(f0 * (f1 / f0) ** (np.arange(n) / n)) / SR)
silent = lambda t: HIT - 0.5 * BEAT <= t < HIT                    # 揭晓前停半拍
quiet = lambda t: CFG['pre'] is not None and CFG['pre'] <= t < HIT  # 子弹时间：只留低频嗡声
NBAR = int(np.ceil((DUR + 1) / BAR)); chord = lambda b: CFG['prog'][b % 4]
# ---------- 铺底（全程）----------
for b in range(NBAR):
    t0 = b * BAR; name, c = chord(b); t = T(BAR + 0.3)
    pad = sum(np.sin(2 * np.pi * midi(m) * (1 + d) * t) + 0.25 * saw(midi(m) * (1 + d), t) for m in c for d in (-0.003, 0.003)) / (2 * len(c))
    fc = 700 if t0 < tE else 1300 if t0 < tR else 1800; g = 0.07 if t0 < tZ else 0.09
    pad = fade(lp(pad, fc), 0.2, 0.3)
    for k in range(len(pad) // 480):                                   # 停半拍 / 子弹时间里把铺底挖掉
        tt = t0 + k * 0.01
        if silent(tt): pad[k * 480:(k + 1) * 480] *= 0
        elif quiet(tt): pad[k * 480:(k + 1) * 480] *= 0.25
    add(mus, pad, t0, g, -0.3); add(mus, lp(pad, fc * 0.9), t0 + 0.012, g * 0.8, 0.3)
# ---------- 开头：低音八分脉冲 + 上升噪声冲进讲解 ----------
for i in range(int(tE / (BEAT / 2))):
    t0 = i * BEAT / 2; b = int(t0 // BAR); r = CFG['root'][b % 4]; t = T(BEAT / 2)
    s = lp(saw(midi(r + 12), t) * np.exp(-t / 0.12), 500); add(mus, fade(s, 0.003, 0.02), t0, 0.10 if i % 2 == 0 else 0.06)
n = T(1.6); rise = hp(rs.standard_normal(len(n)), 1500) * (n / 1.6) ** 2; add(fx, fade(rise, 0.01, 0.05), tE - 1.6, 0.05)
# ---------- 讲解 + 揭晓：玻璃琶音十六分；揭晓再加四拍底鼓、亮一点 ----------
ORD = [0, 2, 1, 3, 2, 0, 3, 1]
for i in range(int((tZ - tE) / (BEAT / 4))):
    t0 = tE + i * BEAT / 4
    if silent(t0) or quiet(t0): continue
    b = int(t0 // BAR); name, c = chord(b); m = c[ORD[i % 8] % len(c)] + (24 if t0 >= tR else 12); t = T(0.4)
    s = sum(np.sin(2 * np.pi * midi(m) * r * t) * np.exp(-t * (8 + 6 * k)) / (k + 1) for k, r in enumerate([1, 2.76, 5.4]))
    add(mus, fade(s, 0.002, 0.05), t0, 0.035 if t0 < tR else 0.045, -0.4 if i % 2 else 0.4)
def kick(t0, g=0.5): t = T(0.35); add(mus, np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-T(0.35) / 0.03)) / SR) * np.exp(-t / 0.12), t0, g)
def hat(t0, g=0.03): t = T(0.06); add(mus, hp(rs.standard_normal(len(t)), 7000) * np.exp(-t / 0.015), t0, g, 0.3)
for i in range(int((tZ - tE) / BEAT)):
    t0 = tE + i * BEAT
    if silent(t0) or quiet(t0): continue
    if t0 >= tR or i % 2 == 0: kick(t0, 0.35 if t0 < tR else 0.5)
    hat(t0 + BEAT / 2, 0.025 if t0 < tR else 0.04)
    if t0 >= tR: b = int(t0 // BAR); r = CFG['root'][b % 4]; t = T(BEAT * 0.9); add(mus, fade(lp(saw(midi(r), t) * np.exp(-t / 0.3), 300), 0.005, 0.05), t0, 0.12)
# ---------- 结尾：落在主和弦上，木质拨弦慢慢弹一遍 ----------
name, c = CFG['prog'][0]; t = T(4.0); pad = sum(np.sin(2 * np.pi * midi(m + 12) * t) for m in c) / len(c) * np.exp(-t / 1.8); add(mus, fade(lp(pad, 2400), 0.02, 0.8), tZ + 0.1, 0.14)
for k, m in enumerate(c + [c[0] + 12]):
    t = T(0.9); s = (np.sin(2 * np.pi * midi(m + 12) * t) + 0.35 * np.sin(2 * np.pi * midi(m + 12) * 3.01 * t) * np.exp(-t / 0.03)) * np.exp(-t / 0.25); add(mus, fade(s, 0.002, 0.1), tZ + 0.3 + k * BEAT / 2, 0.08, (k - 2) * 0.2)
# ---------- 音效（卡在画面动作上）----------
def whoosh(t0, d=0.5, g=0.06): t = T(d); s = bp(rs.standard_normal(len(t)), 400, 3000) * np.sin(np.pi * t / d) ** 2; add(fx, s, t0 - d * 0.6, g)
def boom(t0, g=0.4): t = T(1.2); s = np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-t / 0.05)) / SR) * np.exp(-t / 0.4) + 0.3 * lp(rs.standard_normal(len(t)), 800) * np.exp(-t / 0.15); add(fx, s, t0, g)
def glass(t0, g=0.12): t = T(1.0); s = hp(rs.standard_normal(len(t)), 3000) * np.exp(-t / 0.08); s += sum(np.sin(2 * np.pi * f * t) * np.exp(-t / (0.2 + 0.1 * k)) * 0.3 for k, f in enumerate([2300, 3100, 4170, 5230])); add(fx, s, t0, g)
def click(t0, g=0.12): t = T(0.05); add(fx, hp(rs.standard_normal(len(t)), 2000) * np.exp(-t / 0.004) + np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.01), t0, g)
def ding(t0, m, g=0.08): t = T(1.2); add(fx, sum(np.sin(2 * np.pi * midi(m) * r * t) * np.exp(-t * (3 + 4 * k)) / (k + 1) for k, r in enumerate([1, 2, 3])), t0, g)
def thud(t0, g=0.25): t = T(0.3); add(fx, lp(rs.standard_normal(len(t)), 300) * np.exp(-t / 0.05) + np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.08), t0, g)
for s in D['shots'][1:]: whoosh(s['t0'] + 0.05)
whoosh(0.05, 0.8, 0.08)                                              # 第一帧：冲进画面
def clapfx(t0, g=0.14): t = T(0.12); add(fx, bp(rs.standard_normal(len(t)), 800, 4000) * np.exp(-t / 0.025), t0, g)
if N_ == 's1':
    tFast = kw('p05', '一快'); add(fx, gl(300, 1400, 0.5) * np.linspace(1, 0.2, int(0.5 * SR)) * 0.6, tFast - 0.05, 0.06)        # 一快：加速的上扬声
    pre = CFG['pre']; t = T(HIT - pre + 1.2); drone = lp(saw(midi(26), t) + saw(midi(26) * 1.01, t), 200) * np.minimum(1, t / 0.3); add(fx, fade(drone, 0.2, 0.4), pre, 0.12)
    for k in range(3): thud(pre + 0.25 + k * 0.5, 0.18)
    boom(HIT, 0.5); glass(HIT + 0.02, 0.12)                                                                                   # 拼进下一张
    ding(kw('p07', '错一位'), 70, 0.08)
    tUp = kw('p09', '越跑越快'); t = T(1.2); add(fx, hp(rs.standard_normal(len(t)), 2000) * (t / 1.2) ** 2, tUp - 1.0, 0.07); boom(tUp + 0.2, 0.25)
elif N_ == 's2':
    for k in range(3): click(kw('q02', '全乱了') + k * 0.07, 0.08)                                                              # 乱码：咔咔几声
    sc = [s for s in D['shots'] if s['kind'] == 'clap'][0]; n = 0
    while True:                                                                                                                # 拍手：每个鼓点经过中线时拍一下
        tc = sc['t0'] + (n * 220 - 540) / 220; n += 1
        if tc < sc['t0']: continue
        if tc > sc['t1']: break
        clapfx(tc); kick(tc, 0.3)
    tEdge, tLock = kw('q06', '跳一下'), HIT
    tt = tEdge; k = 0
    while tt < tLock - 0.1: click(tt, 0.05 + 0.02 * (k % 2)); tt += 0.5 + 0.12 * np.sin(k * 1.7) * max(0, 1 - (tt - tEdge) / (tLock - tEdge)); k += 1
    click(tLock, 0.25); boom(tLock, 0.3); ding(tLock + 0.02, 76, 0.1); ding(tLock + 0.02, 83, 0.06)
    tC = kw('q07', '每一拍'); [ding(tC - 0.4 + i * 0.5, [64, 66, 67, 69, 71][i], 0.07) for i in range(5)]
    tMix = kw('q09', '打乱'); [click(tMix + i * 0.04, 0.04) for i in range(22)]; tBack = kw('q09', '还原'); [click(tBack + i * 0.04, 0.04) for i in range(12)]; ding(tBack + 0.45, 76, 0.09)
elif N_ == 's3':
    boom(0.1, 0.2)                                                                                                            # 第一帧：大屏亮起
    tAsk = kw('k03', '三句'); [thud(tAsk - 0.1 + i * 0.22, 0.3) for i in range(3)]
    t4 = kw('k04', '一半'); add(fx, gl(900, 300, 0.6) * np.linspace(1, 0, int(0.6 * SR)) * 0.5, t4 - 0.1, 0.05)               # 网速掉一半
    tScore = kw('k06', '跑分'); add(fx, gl(300, 1600, 1.4) * 0.4, tScore - 0.2, 0.04); boom(kw('k06', '几万颗芯片'), 0.25)
    glass(HIT - 0.25, 0.06); boom(HIT, 0.35); glass(HIT + 0.01, 0.16)                                                         # PPT 碎掉
    ding(kw('k07', '两回事'), 77, 0.06)
mus[:, :] = np.where(np.isfinite(mus), mus, 0)
# ---------- 混音：人声 + （配乐 + 音效）；人声一出来，配乐自动压低（侧链）----------
w = wave.open(f'audio/{N_}_voice.wav'); v = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64) / 32768
v = np.pad(v, (0, max(0, N - len(v))))[:N]; voice = np.vstack([v, v]); b, a = butter(2, 90 / (SR / 2), 'high'); voice = lfilter(b, a, voice); voice *= 0.5 / np.max(np.abs(voice))
env = np.abs(voice[0]); att, rel = np.exp(-1 / (0.02 * SR)), np.exp(-1 / (0.35 * SR)); e = np.zeros(N); x_ = 0
for i in range(0, N, 48):
    x = env[i:i + 48].max(); x_ = att * x_ + (1 - att) * x if x > x_ else rel * x_ + (1 - rel) * x; e[i:i + 48] = x_
duck = 1 - 0.75 * np.clip(e / 0.12, 0, 1)
bed = mus / np.max(np.abs(mus)) * 0.36; fxs = fx / max(1e-9, np.max(np.abs(fx))) * 0.45
mix = voice + bed * duck + fxs * (1 - 0.35 * np.clip(e / 0.12, 0, 1))
act = e > 0.05; rms = lambda x: 20 * np.log10(np.sqrt(np.mean(x[:, act] ** 2)) + 1e-9)
print('voice vs music under voice:', round(rms(voice) - rms(bed * duck), 1), 'dB; music level between lines:', round(rms(voice) - 20 * np.log10(np.sqrt(np.mean((bed * duck)[:, ~act] ** 2)) + 1e-9), 1), 'dB below voice')
mix /= np.max(np.abs(mix)) * 1.12
with wave.open(f'audio/{N_}_mix.wav', 'wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((mix[:, :int(DUR * SR)].T * 32767).astype('<i2').tobytes())
json.dump({'bpm': float(BPM), 'key': CFG['key'], 'hit': HIT, 'beats': [round(i * BEAT, 3) for i in range(int(DUR / BEAT))]}, open(f'audio/{N_}_beats.json', 'w'))
print(N_, CFG['key'], 'BPM', BPM, 'hit', round(HIT, 2), 'beat error', round(abs(HIT / BEAT - round(HIT / BEAT)) * BEAT * 1000), 'ms')
