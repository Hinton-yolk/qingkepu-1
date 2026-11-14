# 光互连 02 下集 · 新画面版 —— 配乐与音效（代码合成，音色沿用系列：铺底、拨弦、玻璃琶音、低音、轻踩、铃声）
# 这一集换调性和进行：G 大调，Am7–D–Gmaj7–Em（02 抖音版是 D 大调 Bm–G–D–A，03 / 04 是 E 小调），铃声动机也换了；结尾 C–D–G。
# 三段不同织体：开头（手机 → 飞进机房）只有铺底 + 低音 + 铃声动机；讲解段拨弦八分音符，「鼓点」是画面里信号跳变的那一下（时间读 out/info.json，和画面同一份）；
#   y7 一长串 1：鼓点停、拨弦停，只剩铺底；y8 鼓点回来；y9–y11 加十六分玻璃琶音；
# 揭晓（y12 回到开头那部手机）前停半拍，之后轻踩四拍 + 拨弦升八度，一直到片尾。
# 120 BPM。产出 out/score.wav（配乐 + 音效，未混人声）
import os, json, wave, numpy as np
from scipy.signal import butter, lfilter
HERE = os.path.dirname(os.path.abspath(__file__)); D = json.load(open(os.path.join(HERE, 'out', 'info.json'), encoding='utf-8'))
SR, BPM, DUR = 48000, 120, D['end'] + 0.6; BEAT = 60 / BPM; N = int(SR * DUR); NB = int(DUR / BEAT)
T, VS, HITS, MK = D['T'], D['vs'], D['hits'], D['marks']
def sub0(k, n): return next(s['t0'] for s in D['subs'] if s['id'] == k and s['n'] == n)
rs = np.random.default_rng(23); mus = np.zeros((2, N)); fx = np.zeros((2, N))
def add(buf, sig, t, g=1.0, pan=0.0):
    i0 = int(round(t * SR)); l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
    if i0 >= N or i0 + len(sig) <= 0: return
    a, b = max(0, i0), min(N, i0 + len(sig)); s = sig[a - i0:b - i0]; buf[0, a:b] += s * g * l; buf[1, a:b] += s * g * r
def Tm(d): return np.arange(int(d * SR)) / SR
def env(n, a, d): e = np.exp(-np.arange(n) / (d * SR)); k = max(1, int(a * SR)); e[:k] *= np.linspace(0, 1, k); return e
def lp(x, fc, o=2): b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def bp(x, lo, hi, o=2): b, a = butter(o, [lo / (SR / 2), min(hi, SR / 2 - 200) / (SR / 2)], 'band'); return lfilter(b, a, x)
def noise(n): return rs.standard_normal(n)
def midi(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, t): return 2 * ((f * t) % 1) - 1
def fade(x, a=0.01, b=0.05):
    ka, kb = min(len(x) // 2, int(a * SR)), min(len(x) // 2, int(b * SR)); x = x.copy()
    if ka: x[:ka] *= np.linspace(0, 1, ka)
    if kb: x[-kb:] *= np.linspace(1, 0, kb)
    return x

OPEN1 = T['side']; LONG0, LONG1 = D['b0']['y7'], D['m8'] + 0.6; FAST0 = T['close']; REV = round(T['arev'] / BEAT) * BEAT; END0 = T['close2']
CH = {'Am7': [57, 60, 64, 67], 'D': [57, 62, 66, 69], 'Gmaj7': [55, 59, 62, 66], 'Em': [52, 55, 59, 64], 'C': [55, 60, 64, 67], 'G': [55, 59, 62, 67]}
ROOT = {'Am7': 45, 'D': 38, 'Gmaj7': 43, 'Em': 40, 'C': 36, 'G': 43}
NBAR = int(np.ceil(DUR / 2)); BARS = [['Am7', 'D', 'Gmaj7', 'Em'][i % 4] for i in range(NBAR)]
for i in range(NBAR):
    if i * 2 >= REV: BARS[i] = ['C', 'D', 'Em', 'G'][(i - int(REV // 2)) % 4]      # 揭晓后换一个往上走的进行
BARS[-3:] = ['C', 'D', 'G']
chord_at = lambda t: BARS[min(NBAR - 1, int(t // 2))]
inlong = lambda t: LONG0 <= t < LONG1

# 铺底
for bar, ch in enumerate(BARS):
    t0 = bar * 2.0; t = Tm(2.3); c = CH[ch]
    pad = sum(np.sin(2 * np.pi * midi(m) * (1 + dt) * t) + 0.25 * saw(midi(m) * (1 + dt), t) for m in c for dt in (-0.003, 0.003)) / (2 * len(c))
    fc = 650 if t0 < OPEN1 else 520 if inlong(t0 + 1) else 1500 if t0 >= REV else 1050
    add(mus, fade(lp(pad, fc), 0.25, 0.3), t0 - 0.05, 0.078, -0.3); add(mus, fade(lp(pad, fc * 0.9), 0.25, 0.3), t0 - 0.04, 0.062, 0.3)
t = Tm(4.0); c = CH['G'] + [71, 74]; pad = sum(np.sin(2 * np.pi * midi(m) * t) for m in c) / len(c) * np.exp(-t / 1.8); add(mus, fade(lp(pad, 2400), 0.02, 0.8), DUR - 4.3, 0.16)
# 拨弦（讲解段八分；一长串 1 那段停）
ORD = [0, 2, 3, 1, 2, 3, 1, 2]
for i in range(int(DUR / (BEAT / 2))):
    tt = i * BEAT / 2
    if tt < OPEN1 or inlong(tt) or tt > DUR - 3.6 or REV - BEAT <= tt < REV: continue
    c = CH[chord_at(tt)]; m = c[ORD[i % 8] % len(c)] + (24 if tt >= REV and i % 2 else 12); t = Tm(0.35)
    s = (np.sin(2 * np.pi * midi(m) * t) + 0.35 * np.sin(2 * np.pi * midi(m) * 3.01 * t) * np.exp(-t / 0.03)) * np.exp(-t / 0.13)
    add(mus, fade(s, 0.002, 0.02), tt, 0.062, 0.35 * np.sin(i * 0.8))
# 玻璃琶音十六分（y9–y11：越来越快那一段）
for i in range(int(DUR / (BEAT / 4))):
    tt = i * BEAT / 4
    if not (FAST0 <= tt < REV - BEAT): continue
    c = CH[chord_at(tt)]; cc = c + [c[0] + 12, c[1] + 12]; m = cc[[0, 1, 2, 3, 4, 3, 2, 1][i % 8] % len(cc)] + 12
    t = Tm(0.45); s = sum(np.sin(2 * np.pi * midi(m) * r * t) * np.exp(-t * (7 + 6 * k)) / (k + 1) for k, r in enumerate([1, 2.76, 5.4]))
    add(mus, fade(s, 0.001, 0.03), tt, 0.042 * min(1, 0.4 + (tt - FAST0) / 6), 0.55 * np.sin(i * 0.6))
# 低音；揭晓后轻踩四拍 + 反拍沙沙
for b in range(NB):
    tt = b * BEAT
    if tt > DUR - 3.6 or REV - BEAT <= tt < REV: continue
    if b % 2 == 0 and not inlong(tt):
        t = Tm(0.9); s = np.sin(2 * np.pi * midi(ROOT[chord_at(tt)]) * t) * env(len(t), 0.01, 0.45); add(mus, fade(lp(s, 300), 0.005, 0.1), tt, 0.12)
    if tt >= REV:
        t = Tm(0.3); f = 110 * np.exp(-t * 30) + 45; add(mus, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09), tt, 0.10)
        n = noise(int(0.08 * SR)); add(mus, hp(n, 6000) * env(len(n), 0.001, 0.03), tt + BEAT / 2, 0.05, -0.4)
    elif tt >= FAST0:
        n = noise(int(0.05 * SR)); add(mus, hp(n, 7000) * env(len(n), 0.001, 0.012), tt + BEAT / 2, 0.04, 0.4)
# 铃声动机（开头；揭晓后再回来一次）
MOTIF = [79, 76, 74, 71, 74, 76, 81, 79]
def bell(tt, m, g=0.05, pan=0.0):
    t = Tm(0.9); s = sum(np.sin(2 * np.pi * midi(m) * r * t) * np.exp(-t * (3 + 5 * k)) / (k + 1) for k, r in enumerate([1, 2.0, 3.0])); add(mus, fade(s, 0.002, 0.05), tt, g, pan)
for j in range(int(OPEN1 / BEAT)): bell(j * BEAT, MOTIF[j % 8], 0.05, 0.3 * np.sin(j))
for j in range(int((END0 - REV) / BEAT)):
    if j % 2 == 0: bell(REV + j * BEAT, MOTIF[(j // 2) % 8] + 0, 0.04, 0.3 * np.sin(j))
# 揭晓前停半拍
k0, k1 = int((REV - BEAT / 2) * SR), int(REV * SR); mus[:, k0:k1] *= 0.0

# ---------- 音效（卡在画面动作上）----------
def chime(t0, m, g=0.08, pan=0.0):
    t = Tm(0.8); s = sum(np.sin(2 * np.pi * midi(m) * r * t) * np.exp(-t * (4 + 5 * k)) / (k + 1) for k, r in enumerate([1, 2.0, 3.0])); add(fx, fade(s, 0.001, 0.05), t0, g, pan)
def pop(t0, f, g=0.08, pan=0.0): t = Tm(0.12); add(fx, np.sin(2 * np.pi * (f + 900 * np.exp(-t * 60)) * t) * np.exp(-t / 0.04), t0, g, pan)
def thud(t0, g=0.16): t = Tm(0.12); add(fx, lp(noise(len(t)), 1600) * np.exp(-t / 0.025) + 0.6 * np.sin(2 * np.pi * 140 * t) * np.exp(-t / 0.04), t0, g)
def tick(t0, g=0.045, f=3200): n = noise(int(0.02 * SR)); add(fx, bp(n, f * 0.7, f * 1.4) * env(len(n), 0.0005, 0.004), t0, g, 0.2)
def whoosh(a, d, g, hi=900):
    t = Tm(d); x = np.arange(len(t)) / len(t); add(fx, fade(lp(noise(len(t)), hi) * np.sin(np.pi * x) ** 2, 0.02, 0.08), a, g)
def drum(t0, g=0.30, pan=0.0):
    """「鼓点」：信号每跳一下。手鼓一样的短促一声（低音一沉 + 一点皮面的噪声）"""
    t = Tm(0.22); f = 190 * np.exp(-t * 26) + 92; s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.075) + 0.35 * bp(noise(len(t)), 900, 3200) * np.exp(-t / 0.018)
    add(fx, fade(s, 0.001, 0.02), t0, g, pan)
def glitch(a, d, g=0.07):
    t = Tm(d); sg = int(0.022 * SR); out = np.zeros(len(t))
    for i in range(0, len(t) - sg, sg): f = rs.choice([420, 660, 990, 1480, 2200]); out[i:i + sg] = np.sign(np.sin(2 * np.pi * f * t[:sg])) * rs.uniform(0.3, 1)
    add(fx, fade(lp(out, 5000), 0.005, 0.03), a, g)
# 开头：消息变乱码（0.85–1.05 秒）；信号飞出去；B 段落到走线上
glitch(0.85, 0.24); whoosh(1.35, 1.0, 0.16, 1400); chime(1.45, 86, 0.06)
whoosh(T['B'] - 0.1, 0.9, 0.12); thud(T['B'] + 0.9, 0.2); chime(T['B'] + 0.92, 79, 0.07)
# 鼓点
for h in HITS: drum(h, 0.30, 0.25 * np.sin(h * 3))
# y3：4？5？
chime(sub0('y3', 1) + 1.9, 88, 0.05); chime(sub0('y3', 1) + 2.05, 86, 0.04)
# y4：刻度出现；时钟线划掉
for i in range(8): tick(VS['y4'] + 0.9 + i * 0.06, 0.04, 3000 + 150 * i)
tk0 = sub0('y4', 2); thud(tk0 + 1.3, 0.14); pop(tk0 + 1.3, 300, 0.07)
# 甩镜
for k in ('count', 'close', 'rx', 'wide'): whoosh(T[k] - 0.22, 0.5, 0.17, 1600)
# y6：刻度对齐一声；数五拍；「五个，不是四个」
tl = sub0('y6', 1) + 0.3; chime(tl + 1.0, 83, 0.06)
cp = MK['count_park']
for i in range(5): chime(cp + 0.15 + 0.25 * i, [71, 74, 76, 79, 83][i], 0.085, -0.4 + 0.2 * i)
chime(sub0('y6', 2), 91, 0.05)
# y7：冲到一长串 1（一声长的下行）；拍子跑偏：几声越来越不准的轻敲
whoosh(D['b0']['y7'] - 0.05, 0.8, 0.14, 700)
for i in range(7): tick(VS['y7'] + 1.3 + i * (0.25 + 0.022 * i), 0.05, 2200 - 110 * i)
# y8：打乱
glitch(D['m8'], 0.6, 0.06); chime(D['m8'] + 0.65, 86, 0.05)
tr = sub0('y8', 2) - 0.2
for i in range(6): pop(tr + 0.1 + i * 0.2, 500 + 60 * i, 0.05)
# y9：两级台阶
for t0, m in ((VS['y9'] + 1.15, 79), (VS['y9'] + 2.35, 86)): pop(t0, 600, 0.08); chime(t0 + 0.05, m, 0.06)
# y10：电路一块块亮起；耗电条
for i in range(8): chime(T['rx'] + 0.5 + i * 0.14, [74, 76, 79, 81, 83, 86, 88, 91][i], 0.04, 0.6 - 0.15 * i)
# y12：光点弹起；消息还原
pop(T['arev'] - 0.45, 700, 0.08); whoosh(T['arev'] - 0.1, 0.9, 0.14, 1400)
for i in range(4): chime(VS['y12'] + 2.75 + i * 0.18, [79, 83, 86, 91][i], 0.07)
# y13：卡片；y14：卡片滑走
thud(T['card'], 0.15); whoosh(T['close2'] - 0.05, 0.6, 0.12)

bed = mus + fx
with wave.open(os.path.join(HERE, 'out', 'score.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(bed.T / (np.max(np.abs(bed)) * 1.05), -1, 1) * 32767).astype('<i2').tobytes())
np.save(os.path.join(HERE, 'out', 'score_fx.npy'), fx.astype(np.float32) / (np.max(np.abs(bed)) * 1.05))
print('score.wav', round(DUR, 2), 's', 'drums', len(HITS))
