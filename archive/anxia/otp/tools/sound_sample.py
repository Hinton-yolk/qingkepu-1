"""Music for the 10 s opening sample (text + music version): a light pluck bed at 120 BPM and hits on the cues."""
import os, json, re, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import butter, sosfilt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SR = 48000
s = open(os.path.join(ROOT, 'film', 'data.js')).read(); C = json.loads(re.search(r'window.CUES=(\{.*\});', s).group(1))['c']; DUR = json.loads(re.search(r'window.TL=(\{.*?\});', s).group(1))['duration']
N = int(DUR * SR); rng = np.random.default_rng(3); out = np.zeros((N, 2)); tt = lambda d: np.arange(int(d * SR)) / SR
bp = lambda x, a, b: sosfilt(butter(2, [a / (SR / 2), b / (SR / 2)], 'bandpass', output='sos'), x)
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
def put(sig, t, g=1, pan=0):
    i = int(t * SR); sig = sig[:max(0, N - i)] * g; l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4); out[i:i + len(sig), 0] += sig * l * 1.4; out[i:i + len(sig), 1] += sig * r * 1.4
def pluck(m, d=.45): x = tt(d); f = mtof(m); return (np.sin(2 * np.pi * f * x) + .35 * np.sin(4 * np.pi * f * x) + .1 * np.sin(6 * np.pi * f * x)) * np.exp(-x * 9) * .3
def kick(): x = tt(.4); return np.sin(2 * np.pi * 55 * x * (1 + 1.5 * np.exp(-x * 30))) * np.exp(-x * 9) * .7
def hat(): x = tt(.05); return bp(rng.standard_normal(len(x)), 5000, 12000) * np.exp(-x * 80) * .25
def sweep(d, f0, f1): x = tt(d); n = rng.standard_normal(len(x)); o = np.zeros(len(x)); [o.__setitem__(slice(i, i + 2400), bp(n[max(0, i - 4800):i + 2400], f0 * (f1 / f0) ** (i / len(x)) * .7, f0 * (f1 / f0) ** (i / len(x)) * 1.4)[-len(n[i:i + 2400]):]) for i in range(0, len(x), 2400)]; return o * np.sin(np.pi * x / d) ** 2
def slash(): x = tt(.25); return bp(rng.standard_normal(len(x)), 800, 6000) * np.exp(-x * 18) * .6
melody = [72, 76, 79, 76, 74, 77, 81, 77]
for k in range(int(DUR / .5)):
    q = k * .5; put(hat(), q, 1, .3 if k % 2 else -.3)
    if k % 2 == 0: put(kick() * (.7 if q < C['flood'] else 1), q)
    put(pluck(melody[k % 8] - (5 if C['flood'] <= q < C['x'] + .5 else 0)), q, .9, (-.4, .4)[k % 2])
put(sweep(.5, 400, 6000) * .6, C['flood'] - .1); put(kick() * 1.2, C['flood'])
put(slash(), C['x']); put(slash(), C['x'] + .12); put(kick(), C['x'])
put(pluck(84, .6), C['slip']); put(sweep(.6, 3000, 800) * .4, C['phone2']); x = tt(.08); put(bp(rng.standard_normal(len(x)), 300, 3000) * np.exp(-x * 50) * .8, C['tap'])
fo = int(.4 * SR); out[-fo:] *= np.linspace(1, 0, fo)[:, None]
m = pyln.Meter(SR); out *= 10 ** ((-14 - m.integrated_loudness(out)) / 20); out = np.tanh(out / .9) * .9
os.makedirs(os.path.join(ROOT, 'audio'), exist_ok=True); sf.write(os.path.join(ROOT, 'audio', 'sample_music.wav'), out.astype(np.float32), SR); print('ok', round(m.integrated_loudness(out), 1))
