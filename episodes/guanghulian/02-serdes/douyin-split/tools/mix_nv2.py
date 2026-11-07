# 纯动画版 v2 的音效 + 混音：python3 tools/mix_nv2.py s1m_724 → audio/s1m_724_mix.wav
# 音乐是主声部，从 D.off 秒起播（拍点已对齐时间线）；音效卡在 D.cue 的动作上（代码合成）。
# 「晚到半步」的子弹时间里音乐压暗，「并排对比」前半拍完全停住，对比那一拍重新进；结尾 2 秒淡出。
import sys, json, wave, subprocess, numpy as np
from scipy.signal import butter, lfilter
N_ = sys.argv[1]; SR = 48000; D = json.load(open(f'代码工程/split/{N_}.json', encoding='utf-8')); C = D['cue']; B = 60 / D['bpm']
N = int(D['dur'] * SR); fx = np.zeros((2, N)); rs = np.random.default_rng(7); T = lambda d: np.arange(int(d * SR)) / SR
def add(sig, t, g=1.0, pan=0.0):
    i = int(t * SR); sig = sig[:max(0, N - i)]
    if i < 0 or len(sig) == 0: return
    fx[0, i:i + len(sig)] += sig * g * (1 - pan) ** 0.5; fx[1, i:i + len(sig)] += sig * g * (1 + pan) ** 0.5
def filt(x, f, kind): b, a = butter(2, np.array(f) / (SR / 2), kind); return lfilter(b, a, x)
midi = lambda m: 440 * 2 ** ((m - 69) / 12)
def whoosh(t0, d=0.5, g=0.5): t = T(d); add(filt(rs.standard_normal(len(t)), [400, 3000], 'band') * np.sin(np.pi * t / d) ** 2, t0 - d * 0.6, g)
def boom(t0, g=0.9): t = T(1.2); add(np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-t / 0.05)) / SR) * np.exp(-t / 0.4) + 0.3 * filt(rs.standard_normal(len(t)), 800, 'low') * np.exp(-t / 0.15), t0, g)
def glass(t0, g=0.3): t = T(1.0); add(filt(rs.standard_normal(len(t)), 3000, 'high') * np.exp(-t / 0.08) + sum(np.sin(2 * np.pi * f * t) * np.exp(-t / (0.2 + 0.1 * k)) * 0.3 for k, f in enumerate([2300, 3100, 4170, 5230])), t0, g)
def click(t0, g=0.25, pan=0.0): t = T(0.05); add(filt(rs.standard_normal(len(t)), 2000, 'high') * np.exp(-t / 0.004) + np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.01), t0, g, pan)
def ding(t0, m, g=0.25, pan=0.0): t = T(1.2); add(sum(np.sin(2 * np.pi * midi(m) * r * t) * np.exp(-t * (3 + 4 * k)) / (k + 1) for k, r in enumerate([1, 2, 3])), t0, g, pan)
def buzz(t0, g=0.22): t = T(0.35); add(np.sign(np.sin(2 * np.pi * 110 * t)) * 0.5 * np.exp(-t / 0.12), t0, g)
def thud(t0, g=0.5): t = T(0.3); add(filt(rs.standard_normal(len(t)), 300, 'low') * np.exp(-t / 0.05) + np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.08), t0, g)
def down(t0, d=1.4, g=0.35): t = T(d); add(np.sin(2 * np.pi * np.cumsum(420 * 0.25 ** (t / d)) / SR) * np.sin(np.pi * t / d) * 0.6, t0, g)   # 子弹时间：往下滑的音
# 第一帧：红圈画出来，「错」的一声；绿勾「对」的一声
buzz(0.3, 0.2); ding(0.45, 84, 0.18, 0.4)
whoosh(C['route'], 0.6); click(C['route'] + 0.25)
whoosh(C['pipes'], 0.5, 0.4); thud(C['pipes'] + 0.05, 0.35)
# 慢的时候：每到一张照片，两边各「叮」一声（上左下右）
s = C['pipes'] + 0.4
while s < C['fast'] - 0.3: ding(s + 0.9, 79, 0.08, -0.3); ding(s + 1.0, 83, 0.08, 0.3); s += 1.5
whoosh(C['fast'], 0.9, 0.6); boom(C['fast'], 0.35)
s = C['fast']
while s < C['late']: click(s + 0.5, 0.1, -0.2); s += 0.62
buzz(C['bend'] + 0.2, 0.25)
down(C['late'], C['lateEnd'] - C['late'])
boom(C['compare'], 1.0); glass(C['compare'], 0.35)
whoosh(C['faster'], 0.7, 0.5)
s = C['faster'] + 0.4
while s < C['so'] - 0.4: click(s, 0.07, 0.3); s += 0.36
for k in range(3): buzz(C['faster'] + 0.8 + k * 0.9, 0.12)
ding(C['so'], 88, 0.25)
for k in range(3): thud(C['take'] + 0.12 + k * 0.12, 0.3)
click(C['z2'] - 0.1, 0.2)
# 音乐
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', str(D['off']), '-i', f"audio/tracks/{D['track']}.mp3", '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
m = np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)[:, :N]; m = np.pad(m, ((0, 0), (0, N - m.shape[1])))
t = np.arange(N) / SR; HIT = C['compare']
g = np.ones(N); g[(t >= C['late']) & (t < HIT - B / 2)] = 0.3; g[(t >= HIT - B / 2) & (t < HIT)] = 0.0
k = int(0.03 * SR); g = np.convolve(g, np.ones(k) / k, 'same'); fo = np.ones(N); n2 = int(2.0 * SR); fo[-n2:] = np.linspace(1, 0, n2); fo[:int(0.06 * SR)] = np.linspace(0, 1, int(0.06 * SR))
m = m / (np.sqrt(np.mean(m ** 2)) + 1e-9) * 0.14 * g * fo
mix = m + fx / max(1e-9, np.max(np.abs(fx))) * 0.32; mix /= max(1.0, np.max(np.abs(mix)) * 1.05)
with wave.open(f'audio/{N_}_mix.wav', 'wb') as o: o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((mix.T * 32767).astype('<i2').tobytes())
print(N_, 'mixed')
