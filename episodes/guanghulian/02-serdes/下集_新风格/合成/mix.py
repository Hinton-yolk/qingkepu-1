# 混音：人声按 out/info.json 的时间点铺好；配乐和音效垫在下面，人声一出来就压低（侧链，人声下方约 12 dB）；成片 -14 LUFS。
# 产出 out/mix.wav
import os, json, wave, subprocess, re, numpy as np
from scipy.signal import butter, lfilter
HERE = os.path.dirname(os.path.abspath(__file__)); D = json.load(open(os.path.join(HERE, 'out', 'info.json'), encoding='utf-8')); SR = 48000; N = int(SR * (D['end'] + 0.6))
def rd(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64) / 32768
    x = x.reshape(-1, 2).T if w.getnchannels() == 2 else np.vstack([x, x]); assert w.getframerate() == SR, p; return x
bed = rd(os.path.join(HERE, 'out', 'score.wav'))[:, :N]; bed = np.pad(bed, ((0, 0), (0, N - bed.shape[1])))
voice = np.zeros((2, N))
for k, t0 in D['vs'].items():
    x = rd(os.path.join(HERE, 'in', 'voice', k + '.wav'))[0]; i0 = int(round(t0 * SR)); n = min(len(x), N - i0); voice[:, i0:i0 + n] += x[:n]
b, a = butter(2, 90 / (SR / 2), 'high'); voice = lfilter(b, a, voice); voice *= 0.5 / np.max(np.abs(voice))
env = np.abs(voice[0]); att, rel = np.exp(-1 / (0.02 * 1000)), np.exp(-1 / (0.35 * 1000)); e = np.zeros(N); v = 0.0
for i in range(0, N, 48):
    x = env[i:i + 48].max(); v = att * v + (1 - att) * x if x > v else rel * v + (1 - rel) * x; e[i:i + 48] = v
duck = 1 - 0.62 * np.clip(e / 0.10, 0, 1)
vr = np.sqrt(np.mean(voice[0][np.abs(voice[0]) > 0.02] ** 2)); br = np.sqrt(np.mean((bed * duck)[0] ** 2)); bed *= vr / br * 10 ** (-12 / 20)   # 人声段里配乐在人声下方约 12 dB
mix = voice + bed * duck; mix /= np.max(np.abs(mix)) * 1.1
tmp = os.path.join(HERE, 'out', '_mix_raw.wav')
with wave.open(tmp, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]); g = -14 - I
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', f'volume={g:.2f}dB,alimiter=limit=0.84:attack=3:release=60:level=disabled', '-ar', '48000', os.path.join(HERE, 'out', 'mix.wav')], check=True)
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', os.path.join(HERE, 'out', 'mix.wav'), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
print('响度', re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1], 'LUFS  峰值', re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1], 'dBFS  人声/配乐', round(20 * np.log10(vr / (vr * 10 ** (-12 / 20))), 1), 'dB')
