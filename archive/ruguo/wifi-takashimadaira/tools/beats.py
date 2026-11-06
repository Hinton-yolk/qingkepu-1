"""Measure the beat grid of the synthesized score -> beats.json, then check every hit against it (cuecheck).
The grid is the comb (period, phase) that collects the most onset energy; the onset detector's latency is measured
from the onsets that sit near the comb and removed. Every hit in audio/hits.json (= the picture's events in
timeline.json) must sit on that grid within one detector frame."""
import json, os, sys
import numpy as np, librosa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR, HOP = 22050, 128
y, _ = librosa.load(os.path.join(ROOT, 'audio', 'score.wav'), sr=SR, mono=True)
env = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP, aggregate=np.median)
times = librosa.times_like(env, sr=SR, hop_length=HOP)
dur = len(y) / SR
comb = lambda period, phase: np.interp(np.arange(phase, dur, period), times, env).sum()
best = max((comb(p, ph), p, ph) for p in np.arange(0.490, 0.510, 0.0002) for ph in np.arange(0, p, 0.003))
_, period, phase = best
phase = max((comb(period, p), p) for p in np.arange(phase - .006, phase + .006, .0005))[1] % period
onsets = librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, units='time')
near = [float(o) for o in onsets if abs(((o - phase + period / 2) % period) - period / 2) < 0.03]
lat = float(np.median([o - round(o / period) * period for o in near])) if near else 0.0
ph = (phase - lat) % period
if ph > period / 2: ph -= period
if abs(ph) < HOP / SR: ph = 0.0
grid = [round(ph + k * period, 4) for k in range(int(dur / period) + 1) if ph + k * period >= 0]
rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
B = dict(tempo=round(60 / period, 3), period=round(float(period), 5), phase=round(float(ph), 4), detector_latency=round(lat, 4),
         measured_onsets_on_grid=[round(o, 4) for o in near], grid=grid, loudest=round(float(times[int(np.argmax(rms))]), 3))
json.dump(B, open(os.path.join(ROOT, 'beats.json'), 'w'))
print(f"tempo {B['tempo']} BPM  period {period:.4f}  phase {ph * 1000:.1f} ms (latency {lat * 1000:.1f} ms)  on-grid onsets {len(near)}/{len(onsets)}  loudest {B['loudest']} s")
# cuecheck: each hit vs the nearest grid line
H = json.load(open(os.path.join(ROOT, 'audio', 'hits.json')))
g = np.array(grid); worst = 0
for k, t in H.items():
    d = (t - g[np.argmin(abs(g - t))]) * 1000; worst = max(worst, abs(d))
    print(f'  {k:9s} {t:7.3f} s  {d:+6.1f} ms')
print(f'cuecheck: worst {worst:.1f} ms (tolerance {HOP / SR * 1000:.1f} ms)')
sys.exit(0 if worst <= HOP / SR * 1000 + .1 else 1)
