# 纯动画版混音：python3 mix_nv.py s1n <曲子.mp3> <输出.wav>
# 音乐是主声部：把曲子的第一个拍点对到 t = 0（时间线是 129 BPM 的拍点网格）；
# 「晚到半步」那段子弹时间里音乐压暗，高潮前半拍完全停住，「拼进下一张」那一拍重新炸开；音效叠在上面；结尾 2 秒淡出。
import sys, json, wave, numpy as np, librosa, subprocess
N_, track, out = sys.argv[1:4]; SR = 48000; D = json.load(open(f'代码工程/split/{N_}.json', encoding='utf-8')); B = 60 / D['bpm']
L = {l['id']: l for l in D['lines']}; kw = lambda i, w: L[i]['ch'][L[i]['text'].index(w)]
fx = (lambda w: np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64).reshape(-1, 2).T / 32767)(wave.open(f'audio/{N_}_stem_fx.wav')); N = int(D['dur'] * SR); fx = fx[:, :N]
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', track, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
m = np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)
y = librosa.resample(librosa.to_mono(m[:, :SR * 40].astype(np.float32)), orig_sr=SR, target_sr=22050); tempo, bt = librosa.beat.beat_track(y=y, sr=22050, units='time')
m = m[:, int(bt[0] * SR):][:, :N]; m = np.pad(m, ((0, 0), (0, N - m.shape[1])))
t = np.arange(N) / SR; tLate, HIT = kw('p05', '晚到半步') - 0.1, kw('p05', '拼进')
g = np.ones(N); g[(t >= tLate) & (t < HIT - B / 2)] = 0.3; g[(t >= HIT - B / 2) & (t < HIT)] = 0.0
k = int(0.03 * SR); g = np.convolve(g, np.ones(k) / k, 'same'); fo = np.ones(N); n2 = int(2.0 * SR); fo[-n2:] = np.linspace(1, 0, n2)
m = m / (np.sqrt(np.mean(m ** 2)) + 1e-9) * 0.14 * g * fo
mix = m + fx / max(1e-9, np.max(np.abs(fx))) * 0.32
mix /= max(1.0, np.max(np.abs(mix)) * 1.05)
with wave.open(out, 'wb') as o: o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((mix.T * 32767).astype('<i2').tobytes())
print(out, 'track tempo', round(float(np.atleast_1d(tempo)[0]), 1), 'first beat', round(bt[0], 2))
