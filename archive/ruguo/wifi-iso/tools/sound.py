"""Draft sound: Fish 「科普」 voice + a synthesized bed and SFX on the cues (120 BPM grid) -> audio/mix.wav at -14 LUFS.
The bed follows the arc: calm → wonder (opens at the switch) → busier as the world grows → a suck-out at 「等等」 → a low, uneasy
floor for the reversal → the sea → one tone on the last question."""
import os, json, re, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import butter, sosfilt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SR = 48000
s = open(os.path.join(ROOT, 'film', 'data.js')).read()
TL = json.loads(re.search(r'window.TL=(\{.*?\});', s).group(1)); C = json.loads(re.search(r'window.CUES=(\{.*\});', s).group(1))['c']
DUR = TL['duration']; N = int(DUR * SR); rng = np.random.default_rng(9)
tt = lambda d: np.arange(int(d * SR)) / SR
bp = lambda x, a, b: sosfilt(butter(2, [a / (SR / 2), min(b, 23000) / (SR / 2)], 'bandpass', output='sos'), x)
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
mus = np.zeros((N, 2)); fx = np.zeros((N, 2))
def put(buf, sig, t, g=1, pan=0):
    i = int(t * SR); sig = sig[:max(0, N - i)] * g; l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * l * 1.414; buf[i:i + len(sig), 1] += sig * r * 1.414
def env(t, segs):    # piecewise-linear envelope from (time, value) pairs
    x, y = zip(*segs); return np.interp(t, x, y)
t = tt(DUR)
# pads per act: A minor → (wonder) C major add9 → (unease) A minor with a flat-six rub → (sea) low drone
def pad(ms, amp): return sum(np.sin(2 * np.pi * mtof(m) * t + i * 1.7) * a for i, (m, a) in enumerate(zip(ms, amp)))
calm = pad([57, 64, 69], [.3, .2, .12]); wonder = pad([48, 60, 64, 67, 74], [.35, .25, .2, .18, .1]); uneasy = pad([45, 57, 60, 65], [.4, .25, .2, .16]); sea = pad([33, 40, 45, 52], [.5, .3, .25, .12])
F, Q = C['freeze'], C['prop']
mix_ = (calm * env(t, [(0, .6), (C['pak'], .6), (C['pak'] + 1, 0)]) + wonder * env(t, [(C['pak'], 0), (C['pak'] + 1.2, 1), (C['turn'], 1), (C['turn'] + 1.5, .3), (F, .3), (F + .1, 0)])
        + uneasy * env(t, [(C['turn'], 0), (C['turn'] + 1.5, .8), (F, 1), (F + .1, 0), (Q, 0), (Q + .8, .9), (C['fast'] - .2, .9), (C['fast'], .5), (C['sea'], .9), (C['sea'] + 1.5, 0)])
        + sea * env(t, [(C['sea'], 0), (C['sea'] + 2, 1), (C['black'] - .5, 1), (C['black'], 0)]))
mix_ *= (1 + .12 * np.sin(2 * np.pi * .23 * t)) * .12
mus += np.stack([mix_, np.roll(mix_, 300)], 1)
# a beacon pulse on the beat from the switch until 「等等」: denser as the world grows
for k in range(int(C['pak'] / .5) + 1, int(F / .5)):
    q = k * .5; d = tt(.3); f = mtof(81 if k % 4 == 0 else 76)
    dens = 1 if q < C['building'] else 2 if q < C['street'] else 4
    for j in range(dens):
        put(mus, (np.sin(2 * np.pi * f * (1 + .5 * j) * d) + .3 * np.sin(2 * np.pi * 2.76 * f * d)) * np.exp(-d * 16) * .09, q + j * .5 / dens, 1, rng.uniform(-.6, .6))
# the switch: a click, an air sweep, a low thump
d = tt(1.1); x = rng.standard_normal(len(d)); sw = np.zeros(len(d))
for i in range(0, len(d), 2400): fc = 300 * 20 ** (i / len(d)); seg = x[max(0, i - 4800):i + 2400]; sw[i:i + 2400] = bp(seg, fc * .7, fc * 1.4)[-len(x[i:i + 2400]):]
put(fx, bp(rng.standard_normal(int(.03 * SR)), 2000, 8000) * np.exp(-tt(.03) * 80) * .8, C['pak'] - .25)
put(fx, sw * np.sin(np.pi * d / 1.1) ** 2 * .5, C['pak'])
put(fx, np.sin(2 * np.pi * 50 * tt(.8) * (1 + .5 * np.exp(-tt(.8) * 20))) * np.exp(-tt(.8) * 5) * .7, C['pak'])
# locks, rolls, events
def blip(): d = tt(.16); return (np.sin(2 * np.pi * 1760 * d) * (d < .06) + np.sin(2 * np.pi * 2637 * d) * (d >= .07)) * np.exp(-d * 18) * .3
for key in ('router', 'phone', 'neighbor', 'wall', 'body', 'fridge', 'move', 'bt', 'long', 'pupil', 'hund'): put(fx, blip(), C[key], 1, .3)
for key in ('glowAll', 'net', 'street', 'city'):
    put(fx, np.sin(2 * np.pi * 45 * tt(1.2) * (1 + .4 * np.exp(-tt(1.2) * 15))) * np.exp(-tt(1.2) * 3) * .5, C[key])
# 「等等」: everything stops; a single tape-stop drop
d = tt(.5); put(fx, np.sin(2 * np.pi * np.cumsum(220 * np.exp(-d * 6)) / SR) * np.exp(-d * 4) * .4, F)
# the reversal lands: a low hit + a glass note; the question gets one bell
put(fx, np.sin(2 * np.pi * 40 * tt(1.6) * (1 + .5 * np.exp(-tt(1.6) * 14))) * np.exp(-tt(1.6) * 2.5) * .8, C['blind'])
def bell(m, d=3.5): x = tt(d); f = mtof(m); return (np.sin(2 * np.pi * f * x) * np.exp(-x * 1.3) + .4 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 3)) * .3
put(mus, bell(76), C['q'] + .2); put(mus, bell(69, 5), C['next'])
# the turn: the rings crack like glass
put(fx, bp(rng.standard_normal(int(.6 * SR)), 2500, 12000) * np.exp(-tt(.6) * 9) * .9, C['wobble'])
for i in range(6): put(fx, bp(rng.standard_normal(int(.05 * SR)), 3000, 9000) * np.exp(-tt(.05) * 50) * .5, C['wobble'] + .06 + i * .07, 1, rng.uniform(-.8, .8))
# the whole building lights: a swell
d = tt(1.4); x = rng.standard_normal(len(d)); sw2 = np.zeros(len(d))
for i in range(0, len(d), 2400): fc = 200 * 25 ** (i / len(d)); seg = x[max(0, i - 4800):i + 2400]; sw2[i:i + 2400] = bp(seg, fc * .7, fc * 1.4)[-len(x[i:i + 2400]):]
put(fx, sw2 * (np.arange(len(d)) / len(d)) ** 2 * .6, C['glowAll'] - 1.1)
# the flashback cuts: three whooshes
span = (C['blind'] + .6 - C['flash']) / 3
for i in range(3): put(fx, sw * np.sin(np.pi * tt(1.1) / 1.1) ** 2 * .35, C['flash'] + i * span - .3, 1, (-.4, 0, .4)[i])
# 中国天眼: a deep hit and a bell; the 5 km ring sweeps; phones inside go off one by one
put(fx, np.sin(2 * np.pi * 36 * tt(2.0) * (1 + .5 * np.exp(-tt(2.0) * 12))) * np.exp(-tt(2.0) * 2) * .9, C['fast']); put(mus, bell(64, 4), C['fast'])
put(fx, sw * np.sin(np.pi * tt(1.1) / 1.1) ** 2 * .45, C['km5'])
for i in range(8):
    d = tt(.14); put(fx, np.sin(2 * np.pi * np.cumsum(1600 * (1 - .5 * d / .14)) / SR) * np.exp(-d * 20) * .3, C['ban'] + i * .11, 1, rng.uniform(-.6, .6))
HITS = {k: C[k] for k in ('pak', 'router', 'phone', 'neighbor', 'glowAll', 'wobble', 'wall', 'body', 'fridge', 'net', 'move', 'street', 'bt', 'city', 'freeze', 'long', 'pupil', 'blind', 'hund', 'q', 'fast', 'km5', 'ban', 'next')}
json.dump(HITS, open(os.path.join(ROOT, 'audio', 'hits.json'), 'w'), indent=1)
sf.write(os.path.join(ROOT, 'audio', 'score.wav'), (mus + fx).astype(np.float32), SR)
voice, _ = sf.read(os.path.join(ROOT, 'voice', 'voice.wav')); voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
m = pyln.Meter(SR)
voice *= 10 ** ((-16 - m.integrated_loudness(voice)) / 20)
bed = mus + fx; bed *= 10 ** ((-24 - m.integrated_loudness(bed)) / 20)
mix = bed + voice[:, None]; mix *= 10 ** ((-14 - m.integrated_loudness(mix)) / 20); mix = np.tanh(mix / .89) * .89
mix *= 10 ** ((-14 - m.integrated_loudness(mix)) / 20)
os.makedirs(os.path.join(ROOT, 'audio'), exist_ok=True)
sf.write(os.path.join(ROOT, 'audio', 'mix_full.wav'), mix.astype(np.float32), SR)
print('mix', round(m.integrated_loudness(mix), 2), 'LUFS, peak', round(20 * np.log10(np.abs(mix).max()), 2), 'dBFS,', DUR, 's')
