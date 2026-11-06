"""Measure the beat grid of the synthesized score (music + effects, no voice) -> beats.json, then check every hit against it.
The grid is the comb (period, phase) that collects the most onset energy; the detector's latency is measured and removed."""
import json, os, sys
import numpy as np, librosa
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR, HOP = 22050, 128
y, _ = librosa.load(os.path.join(ROOT, 'audio', 'score.wav'), sr=SR, mono=True)
env = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP, aggregate=np.median)
times = librosa.times_like(env, sr=SR, hop_length=HOP); dur = len(y) / SR
comb = lambda p, ph: np.interp(np.arange(ph, dur, p), times, env).sum()
_, period, phase = max((comb(p, ph), p, ph) for p in np.arange(.49, .51, .0002) for ph in np.arange(0, p, .003))
_, period, phase = max((comb(p, q), p, q) for p in np.arange(period - .0004, period + .0004, .00001) for q in np.arange(phase - .006, phase + .006, .0005))   # refine
phase %= period
on = librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, units='time')
# refine by least squares on the onsets that sit near the comb: o = a + b·n (n = half-beat index); a carries the detector latency
half = period / 2
for _ in range(3):
    n = np.round((on - phase) / half); r = on - (phase + n * half); keep = np.abs(r) < .03
    b, a = np.polyfit(n[keep], on[keep], 1); half, phase = b, a
period = 2 * half; near = on[keep]
lat = phase % half if phase % half < half / 2 else phase % half - half      # a constant offset of every onset = detector latency
ph = 0.0 if abs(lat) < .045 else lat
grid = [round(ph + k * period / 2, 4) for k in range(int(dur / (period / 2)) + 1) if ph + k * period / 2 >= 0]
B = dict(tempo=round(60 / period, 3), period=round(float(period), 5), half_beat_phase=round(float(ph), 4), detector_latency=round(lat, 4), grid=grid)
json.dump(B, open(os.path.join(ROOT, 'beats.json'), 'w'))
print(f"tempo {B['tempo']} BPM, half-beat phase {ph * 1000:.1f} ms, latency {lat * 1000:.1f} ms, {len(near)}/{len(on)} onsets on the grid")
H = json.load(open(os.path.join(ROOT, 'audio', 'hits.json'))); g = np.array(grid); worst = 0
for k, t in H.items(): d = (t - g[np.argmin(abs(g - t))]) * 1000; worst = max(worst, abs(d))
print(f'cuecheck: {len(H)} hits, worst {worst:.1f} ms (tolerance {HOP / SR * 1000:.1f} ms)')
sys.exit(0 if worst <= HOP / SR * 1000 + .1 else 1)
