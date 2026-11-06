"""Delivery stats per line: median pitch, pitch spread, loudness, peak-to-median level, speech rate — to keep the opening lines in one voice."""
import sys, json, numpy as np, librosa, soundfile as sf, pyloudnorm as pyln
L = {l['id']: l for l in json.load(open('voice/lines_with_L19.json'))}
def stats(path, text):
    y, sr = librosa.load(path, sr=22050)
    f0, vf, _ = librosa.pyin(y, fmin=70, fmax=500, sr=sr, frame_length=1024)
    f = f0[vf & ~np.isnan(f0)]; st = 12 * np.log2(f / np.median(f))
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=256)[0]; db = 20 * np.log10(rms + 1e-9); act = db[db > db.max() - 35]
    n = len([c for c in text if '一' <= c <= '鿿'])
    m = pyln.Meter(sr)
    return dict(f0_med=round(float(np.median(f)), 1), f0_spread_st=round(float(np.percentile(st, 90) - np.percentile(st, 10)), 2),
                lufs=round(m.integrated_loudness(y), 1), peak_over_med_db=round(float(np.percentile(act, 98) - np.median(act)), 1), chars_per_s=round(n / (len(y) / sr), 2))
for p in sys.argv[1:]:
    lid = p.split('/')[-1].split('.')[0].split('_')[0]
    try: print(p.split('/')[-1], stats(p, L[lid]['tts']))
    except Exception as e: print(p, 'n/a', e)
