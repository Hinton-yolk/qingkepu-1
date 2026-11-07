# 用曲库音乐替换合成配乐：python3 mix_lib.py s1 <曲子.mp3> <输出.wav>
# 人声 + 原来的音效 + 曲库音乐。音乐：从这首歌的拍点里挑一个，平移到高潮那一刻；人声下压低约 13 dB（侧链）；结尾 2 秒淡出。
import sys, json, wave, numpy as np, librosa, subprocess
N_, track, out = sys.argv[1:4]; SR = 48000
rd = lambda p: (lambda w: np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64).reshape(-1, 2).T / 32767)(wave.open(p))
voice, fx = rd(f'audio/{N_}_stem_voice.wav'), rd(f'audio/{N_}_stem_fx.wav'); N = voice.shape[1]; cue = json.load(open(f'audio/{N_}_cues.json')); HIT = cue['hit']
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', track, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
m = np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)
# 拍点：选一个落在 HIT 附近之后的强拍，让它对准 HIT（只往后平移，不超过 8 拍）
y = librosa.to_mono(m[:, :SR * 90].astype(np.float32)); y22 = librosa.resample(y, orig_sr=SR, target_sr=22050)
tempo, bt = librosa.beat.beat_track(y=y22, sr=22050, units='time'); bt = [b for b in bt if b >= HIT]
shift = (bt[0] - HIT) if bt else 0.0
m = m[:, int(shift * SR):]
if m.shape[1] < N: m = np.concatenate([m, m], axis=1)
m = m[:, :N]
env = np.abs(voice[0]); att, rel = np.exp(-1 / (0.02 * SR)), np.exp(-1 / (0.35 * SR)); e = np.zeros(N); x_ = 0
for i in range(0, N, 48):
    x = env[i:i + 48].max(); x_ = att * x_ + (1 - att) * x if x > x_ else rel * x_ + (1 - rel) * x; e[i:i + 48] = x_
duck = 1 - 0.5 * np.clip(e / 0.12, 0, 1); act = e > 0.05
g = np.sqrt(np.mean(voice[:, act] ** 2)) * 10 ** (-13 / 20) / (np.sqrt(np.mean((m * duck)[:, act] ** 2)) + 1e-9)
fo = np.ones(N); k = int(2.0 * SR); fo[-k:] = np.linspace(1, 0, k)
mix = voice + m * g * duck * fo + fx
mix /= np.max(np.abs(mix)) * 1.12
with wave.open(out, 'wb') as o: o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((mix.T * 32767).astype('<i2').tobytes())
print(out, 'shift', round(shift, 2), 's; tempo', round(float(np.atleast_1d(tempo)[0])))
