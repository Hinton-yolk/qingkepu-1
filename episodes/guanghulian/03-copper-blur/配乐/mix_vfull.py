# 旁白样片混音：人声按 desk_voice.json 的 voice 时间点铺好；配乐和音效垫在下面，人声一出来就自动压低（侧链闪避），出 mix_voice.wav
import json, wave, numpy as np
from scipy.signal import butter, lfilter
D = json.load(open('../代码工程/ep3/desk_voice.json', encoding='utf-8')); SR = 48000; N = int(SR * D['dur'])
def rd(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64) / 32768
    if w.getnchannels() == 2: x = x.reshape(-1, 2).T
    else: x = np.vstack([x, x])
    assert w.getframerate() == SR, (p, w.getframerate()); return x
bed = rd('score_vfull_bed.wav')[:, :N]; bed = np.pad(bed, ((0, 0), (0, N - bed.shape[1])))
voice = np.zeros((2, N))
for v in D['voice']:
    x = rd('../' + v['file'])[0]; i0 = int(round(v['t'] * SR)); n = min(len(x), N - i0); voice[0, i0:i0 + n] += x[:n]; voice[1, i0:i0 + n] += x[:n]
# 人声：轻微提亮（高架 3 kHz）、去低频，峰值对齐
b, a = butter(2, 90 / (SR / 2), 'high'); voice = lfilter(b, a, voice)
voice *= 0.5 / np.max(np.abs(voice))
# 侧链：人声包络（快起慢放），配乐在人声下压低约 12 dB
env = np.abs(voice[0]); att, rel = np.exp(-1 / (0.02 * SR)), np.exp(-1 / (0.35 * SR)); e = np.zeros(N); v = 0
for i in range(0, N, 48):                       # 1 ms 一步算包络
    x = env[i:i + 48].max(); v = att * v + (1 - att) * x if x > v else rel * v + (1 - rel) * x; e[i:i + 48] = v
duck = 1 - 0.75 * np.clip(e / 0.12, 0, 1)
bed *= 0.55 / np.max(np.abs(bed))
mix = voice + bed * duck
mix /= np.max(np.abs(mix)) * 1.12
with wave.open('mix_vfull.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
print('mix_vfull.wav', D['dur'], 's')
