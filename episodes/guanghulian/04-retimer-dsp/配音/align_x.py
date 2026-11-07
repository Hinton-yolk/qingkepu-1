# python3 align.py script_full.json align_full.json —— 每句旁白：语音起止、句内停顿（≥90 ms）、按标点分句（时间表据此把「说到哪个词」对到秒）
import json, wave, sys, re, numpy as np
S = json.load(open(sys.argv[1], encoding='utf-8')); out = {}
for s in S:
    w = wave.open(f"fish_x/{s['id']}.wav"); x = np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32768; SR = w.getframerate()
    hop = SR // 100; env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    thr = max(1e-4, np.percentile(env, 90) * 0.06); sil = env < thr
    idx = np.where(~sil)[0]; on, off = (idx[0] * 0.01, idx[-1] * 0.01) if len(idx) else (0, len(env) * 0.01)
    pauses = []; i = 0
    while i < len(sil):
        if sil[i]:
            j = i
            while j < len(sil) and sil[j]: j += 1
            a, b = i * 0.01, j * 0.01
            if b - a >= 0.09 and a > on + 0.05 and b < off - 0.05: pauses.append([round(a, 2), round(b, 2)])
            i = j
        else: i += 1
    clauses = [c for c in re.split(r'(?<=[，：；。？、])', s['text']) if c.strip()]
    out[s['id']] = dict(dur=round(len(x) / SR, 3), on=round(on, 2), off=round(off, 2), pauses=pauses, clauses=clauses)
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'lines;', round(sum(v['dur'] for v in out.values()), 1), 's of speech')
