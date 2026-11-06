# python3 voice_mix.py s1 → audio/s1_voice.wav：每句先统一到 -20 LUFS，再按时间表放到位置上
import json, sys, subprocess, re, wave, numpy as np, os
N = sys.argv[1]; SRC = '/home/user/kepu-studio/episodes/guanghulian/02-serdes/douyin-split/fish'
D = json.load(open(f'代码工程/split/{N}.json')); SR = 48000
out = np.zeros(int((D['dur'] + 1) * SR))
for l in D['lines']:
    f = f"{SRC}/{l['id']}.wav"; o = subprocess.run(['ffmpeg', '-i', f, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', o)[-1]); w = wave.open(f); x = np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32768 * 10 ** ((-20 - I) / 20)
    i = int(round(l['clip'] * SR)); n = min(len(x), len(out) - i); out[i:i + n] += x[:n]
os.makedirs('audio', exist_ok=True); y = (np.clip(out, -1, 1) * 32767).astype('<i2')
w = wave.open(f'audio/{N}_voice.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes()); w.close(); print(N, 'voice', round(len(y) / SR, 1), 's')
