# 光互连 03 抖音无旁白版的配乐 + 音效（代码合成，音色沿用小红书版）：python3 tools/score_g.py g1|g2 → audio/<name>_mix.wav
# 120 BPM，E 小调 Em–Am–D–G。三段织体：开头（到第一张大字卡）只有铺底 + 低音 + 铃声动机；中段拨弦八分 + 演示时的玻璃琶音 + 轻踩；
# 揭晓（D.cue.rev）前停半拍，揭晓那一拍低频一沉，之后加四拍轻踩 + 反拍沙沙、拨弦升八度，一直到片尾。大字卡那一拍织体收薄，让画面「静一拍」。
import sys, json, wave, numpy as np
from scipy.signal import butter, lfilter
N_ = sys.argv[1]; D = json.load(open(f'代码工程/split/{N_}.json', encoding='utf-8')); C = D['cue']
SR = 48000; BPM = D['bpm']; BEAT = 60 / BPM; DUR = D['dur']; N = int(SR * DUR); rs = np.random.default_rng(5)
mus = np.zeros((2, N)); fx = np.zeros((2, N))
def add(buf, sig, t, g=1.0, pan=0.0):
    i0 = int(round(t * SR)); l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
    if i0 >= N or i0 + len(sig) <= 0: return
    a, b = max(0, i0), min(N, i0 + len(sig)); s = sig[a - i0:b - i0]; buf[0, a:b] += s * g * l; buf[1, a:b] += s * g * r
T = lambda d: np.arange(int(d * SR)) / SR
def env(n, a, d): e = np.exp(-np.arange(n) / (d * SR)); k = max(1, int(a * SR)); e[:k] *= np.linspace(0, 1, k); return e
def lp(x, fc): b, a = butter(2, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def hp(x, fc): b, a = butter(2, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def bp(x, lo, hi): b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], 'band'); return lfilter(b, a, x)
midi = lambda m: 440 * 2 ** ((m - 69) / 12); saw = lambda f, t: 2 * ((f * t) % 1) - 1
def fade(x, a=0.01, b=0.05):
    x = x.copy(); ka, kb = int(a * SR), int(b * SR)
    if ka: x[:ka] *= np.linspace(0, 1, ka)
    if kb: x[-kb:] *= np.linspace(1, 0, kb)
    return x
noise = lambda n: rs.standard_normal(n)
CH = {'Em': [52, 55, 59, 66], 'Am': [57, 60, 64, 71], 'D': [54, 57, 62, 64], 'G': [55, 59, 62, 69], 'C': [52, 55, 60, 64]}
ROOT = {'Em': 40, 'Am': 45, 'D': 38, 'G': 43, 'C': 36}
NBAR = int(np.ceil(DUR / 2)); BARS = [['Em', 'Am', 'D', 'G'][i % 4] for i in range(NBAR)]; BARS[-3:] = ['C', 'D', 'G']
chord = lambda t: BARS[min(NBAR - 1, int(t // 2))]
shots = D['shots']; OPEN1 = [s['t0'] for s in shots if s['kind'] == 'beat'][0]; REV = C['rev']; TAKE = [s['t0'] for s in shots if s['kind'] == 'take'][0]
BEATS = [(s['t0'], s['t1']) for s in shots if s['kind'] == 'beat']; isbeat = lambda t: any(a <= t < b for a, b in BEATS)
# 铺底
for bar, ch in enumerate(BARS):
    t0 = bar * 2.0; t = T(2.3); c = CH[ch]
    pad = sum(np.sin(2 * np.pi * midi(m) * (1 + dt) * t) + 0.25 * saw(midi(m) * (1 + dt), t) for m in c for dt in (-0.003, 0.003)) / (2 * len(c))
    fc = 700 if t0 < OPEN1 else 1600 if t0 >= REV else 1100
    add(mus, fade(lp(pad, fc), 0.25, 0.3), t0 - 0.05, 0.09, -0.3); add(mus, fade(lp(pad, fc * 0.9), 0.25, 0.3), t0 - 0.04, 0.07, 0.3)
t = T(4.0); pad = sum(np.sin(2 * np.pi * midi(m) * t) for m in CH['G'] + [67, 71]) / 6 * np.exp(-t / 1.8); add(mus, fade(lp(pad, 2400), 0.02, 0.8), DUR - 4.0, 0.18)
# 开头：铃声动机（B–E–F#–G）
MOTIF = [71, 76, 78, 79, 78, 76, 74, 71]
for j in range(int(OPEN1 / BEAT)):
    tt = j * BEAT; t = T(0.9); s_ = sum(np.sin(2 * np.pi * midi(MOTIF[j % 8]) * r * t) * np.exp(-t * (3 + 5 * k)) / (k + 1) for k, r in enumerate([1, 2.0, 3.0])); add(mus, fade(s_, 0.002, 0.05), tt, 0.06, 0.3 * np.sin(j))
# 中段和揭晓段：拨弦八分（大字卡那一拍收掉），揭晓后升八度
ORD = [0, 2, 1, 3, 2, 1, 3, 2]
for i in range(int(DUR / (BEAT / 2))):
    tt = i * BEAT / 2
    if tt < OPEN1 or isbeat(tt) or tt > DUR - 3.0: continue
    c = CH[chord(tt)]; m = c[ORD[i % 8] % len(c)] + (24 if tt >= REV and i % 2 else 12); t = T(0.35)
    s_ = (np.sin(2 * np.pi * midi(m) * t) + 0.35 * np.sin(2 * np.pi * midi(m) * 3.01 * t) * np.exp(-t / 0.03)) * np.exp(-t / 0.13); add(mus, fade(s_, 0.002, 0.02), tt, 0.08, 0.35 * np.sin(i * 0.8))
# 低音、轻踩、反拍沙沙
for b in range(int(DUR / BEAT)):
    tt = b * BEAT
    if tt > DUR - 3.0: continue
    ch = chord(tt)
    if b % 2 == 0: t = T(0.9); add(mus, fade(lp(np.sin(2 * np.pi * midi(ROOT[ch]) * t) * env(len(t), 0.01, 0.45), 300), 0.005, 0.1), tt, 0.14)
    if tt >= OPEN1 and not isbeat(tt) and (tt >= REV or b % 2 == 0):
        t = T(0.3); f = 110 * np.exp(-t * 30) + 45; add(mus, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09), tt, 0.13 if tt >= REV else 0.09)
    if tt >= REV: n = noise(int(0.08 * SR)); add(mus, hp(n, 6000) * env(len(n), 0.001, 0.03), tt + BEAT / 2, 0.06, -0.4)
# 揭晓前停半拍
k0, k1 = int((REV - BEAT / 2) * SR), int(REV * SR); mus[:, k0:k1] *= 0.0
# ---------- 音效 ----------
def tick(t0, g=0.04, f=3200): n = noise(int(0.02 * SR)); add(fx, bp(n, f * 0.7, f * 1.4) * env(len(n), 0.0005, 0.004), t0, g, 0.2)
def chime(t0, m, g=0.08, pan=0.0): t = T(0.8); add(fx, fade(sum(np.sin(2 * np.pi * midi(m) * r * t) * np.exp(-t * (4 + 5 * k)) / (k + 1) for k, r in enumerate([1, 2.0, 3.0])), 0.001, 0.05), t0, g, pan)
def thock(t0, g=0.09): t = T(0.25); add(fx, np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 25)) * t) * np.exp(-t / 0.1), t0, g)
def whoosh(t0, d=0.5, g=0.12): t = T(d); x = np.arange(len(t)) / len(t); add(fx, fade(lp(noise(len(t)), 900) * np.sin(np.pi * x) ** 2, 0.02, 0.08), t0 - d * 0.6, g)
def wrong(t0, g=0.07): t = T(0.45); add(fx, fade(lp(saw(110, t) + saw(116.5, t), 900) * np.exp(-t / 0.18), 0.005, 0.08), t0, g)
def boom(t0, g=0.16): t = T(1.6); add(fx, np.sin(2 * np.pi * (36 + 50 * np.exp(-t * 8)) * t) * np.exp(-t / 0.5), t0, g); chime(t0, 88, 0.05, 0.3)
def riser(t0, d=1.0, g=0.12): t = T(d); x = np.arange(len(t)) / len(t); add(fx, fade(hp(noise(len(t)), 400) * x ** 2 * 0.5 + np.sin(2 * np.pi * np.cumsum(200 * 2 ** (x * 2.5)) / SR) * x ** 1.5 * 0.4, 0.05, 0.01), t0 - d, g)
def laser(t0, g=0.07): t = T(0.4); add(fx, fade(np.sin(2 * np.pi * np.cumsum(300 * 4 ** (np.arange(len(t)) / len(t))) / SR) * np.linspace(0, 1, len(t)), 0.01, 0.1), t0, g); chime(t0 + 0.3, 84, 0.05)
def blur(t0, g=0.08): t = T(0.9); f = 520 * np.exp(-t * 0.9); add(fx, lp(np.sin(2 * np.pi * np.cumsum(f) / SR), 1200) * env(len(t), 0.02, 0.35), t0, g, 0.35)
def stamp(t0, g=0.12): t = T(0.12); add(fx, lp(noise(len(t)), 1600) * np.exp(-t / 0.025) + 0.6 * np.sin(2 * np.pi * 140 * t) * np.exp(-t / 0.04), t0, g)
for s in shots[1:]: whoosh(s['t0'], 0.5, 0.10)
for s in shots:
    if s['kind'] == 'beat': stamp(s['t0'] + 0.05, 0.16); chime(s['t0'] + 0.3, 76, 0.05)
    if s['kind'] == 'take': chime(s['t0'] + 0.2, 79, 0.08); chime(s['t0'] + 0.5, 83, 0.07); chime(s['t0'] + 0.8, 86, 0.07)
riser(REV, 1.0); boom(REV, 0.18)
if N_ == 'g1':
    for k in ('tag1', 'tag2'): stamp(C[k], 0.1)
    blur(C['ring1']); wrong(C['ring1'] + 0.3); chime(C['ring1'] + 0.1, 83, 0.05)
    blur(C['morph']); stamp(C['seq'], 0.08); wrong(C['sum']); stamp(C['ana'], 0.08)
    wrong(C['photo']); wrong(C['msg'])
    stamp(C['rowA'], 0.08); stamp(C['rowB'], 0.08); stamp(C['same'], 0.1)
    stamp(C['ring2'], 0.1); laser(C['fiber2']); chime(C['fiber2'] + 0.6, 88, 0.06)
else:
    chime(C['mag'], 84, 0.07); laser(C['fiber'])
    blur(C['slide'] - 1.0); chime(C['slide'] + 0.8, 83, 0.07)
    blur(C['swap'] - 1.0); chime(C['swap'] + 0.6, 83, 0.07)
    stamp(C['station'], 0.12); chime(C['station'] + 0.5, 86, 0.07)
    stamp(C['ring'], 0.1); laser(C['far'])
mix = mus * 0.8 + fx * 1.3; mix[:, -int(1.2 * SR):] *= np.linspace(1, 0, int(1.2 * SR)); mix /= np.max(np.abs(mix)) * 1.1
with wave.open(f'audio/{N_}_mix.wav', 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
print(N_, 'mix', DUR, 's')
