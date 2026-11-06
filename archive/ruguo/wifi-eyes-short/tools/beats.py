"""Measure the beat grid of the synthesized bed -> beats.json.
librosa's tracker drifts on this sparse score, so the grid is measured as the comb
(period, phase) that collects the most onset energy, then each detected onset that
sits near the comb is reported. Cuts and SFX hits snap to this grid."""
import json, os
import numpy as np, librosa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR, HOP = 22050, 128
y, _ = librosa.load(os.path.join(ROOT, 'audio', 'score.wav'), sr=SR, mono=True)
env = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP, aggregate=np.median)
times = librosa.times_like(env, sr=SR, hop_length=HOP)
dur = len(y) / SR


def comb(period, phase):
    g = np.arange(phase, dur, period)
    return np.interp(g, times, env).sum()


best = (0, 0, 0)
for period in np.arange(0.590, 0.610, 0.0002):
    for phase in np.arange(0, period, 0.003):
        s = comb(period, phase)
        if s > best[0]:
            best = (s, period, phase)
_, period, phase = best
# refine phase finely
fine = max(((comb(period, p), p) for p in np.arange(phase - 0.006, phase + 0.006, 0.0005)))
phase = fine[1] % period
onsets = librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, units='time')
near = [round(float(o), 4) for o in onsets if abs(((o - phase + period / 2) % period) - period / 2) < 0.03]
grid = [round(float(phase + i * period), 4) for i in range(int(dur / period) + 1)]
rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
loud = float(times[int(np.argmax(rms))])
json.dump({'tempo': round(60 / period, 3), 'period': round(float(period), 5), 'phase': round(float(phase), 4),
           'measured_onsets_on_grid': near, 'grid': grid, 'loudest': round(loud, 3)},
          open(os.path.join(ROOT, 'beats.json'), 'w'))
print(f'tempo {60/period:.3f} BPM  period {period:.4f}  phase {phase*1000:.1f} ms  on-grid onsets {len(near)}/{len(onsets)}  loudest {loud:.2f}s')
# the 8th grid the film snaps to: the measured comb's 8th subdivision, corrected for onset-detector latency
B = json.load(open(os.path.join(ROOT, 'beats.json')))
on = np.array(B['measured_onsets_on_grid'])
lat = float(np.median(on - np.round(on / (period / 2)) * (period / 2))) if len(on) else 0.0
ph8 = (phase - lat) % (period / 2)
if ph8 > period / 4: ph8 -= period / 2
if abs(ph8) < HOP / SR: ph8 = 0.0   # below one detector frame: quantization, not offset
B['detector_latency'] = round(lat, 4)
B['grid8'] = [round(ph8 + k * period / 2, 4) for k in range(int(dur / (period / 2)) + 2) if ph8 + k * period / 2 >= 0]
json.dump(B, open(os.path.join(ROOT, 'beats.json'), 'w'))
print(f'grid8 phase {ph8*1000:.1f} ms (latency {lat*1000:.1f} ms), {len(B["grid8"])} points')
