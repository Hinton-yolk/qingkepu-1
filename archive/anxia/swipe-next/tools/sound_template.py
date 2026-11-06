"""Draft sound for If-series 03 (shrink to 1 cm): Fish 「科普」 voice + a synthesized bed and SFX on the cues (120 BPM half-beat grid)
-> audio/score.wav, audio/hits.json, audio/mix_full.wav at -14 LUFS.
Arc: a quiet rainy room → 啪, a falling whoosh as you shrink → light plucks while you are a superhero → a tense floor (rain thumps, wind) →
a low hit on 「同一个原因」 → the ant's tiny steps → a rising sweep as you grow back → one bell."""
import os, json, re, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import butter, sosfilt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SR = 48000
s = open(os.path.join(ROOT, 'film', 'data.js')).read()
TL = json.loads(re.search(r'window.TL=(\{.*?\});', s).group(1)); C = json.loads(re.search(r'window.CUES=(\{.*\});', s).group(1))['c']
DUR = TL['duration']; N = int(DUR * SR); rng = np.random.default_rng(9)
tt = lambda d: np.arange(int(d * SR)) / SR
bp = lambda x, a, b: sosfilt(butter(2, [a / (SR / 2), min(b, 23000) / (SR / 2)], 'bandpass', output='sos'), x)
lp = lambda x, f: sosfilt(butter(2, f / (SR / 2), 'low', output='sos'), x)
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
mus = np.zeros((N, 2)); fx = np.zeros((N, 2))
def put(buf, sig, t, g=1, pan=0):
    i = int(t * SR); sig = sig[:max(0, N - i)] * g; l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * l * 1.414; buf[i:i + len(sig), 1] += sig * r * 1.414
def env(t, segs): x, y = zip(*segs); return np.interp(t, x, y)
t = tt(DUR)
def pad(ms, amp): return sum(np.sin(2 * np.pi * mtof(m) * t + i * 1.7) * a for i, (m, a) in enumerate(zip(ms, amp)))
room = pad([45, 52, 57, 61, 64], [.3, .22, .16, .1, .08])          # A add9, warm and quiet
wish = pad([45, 57, 61, 64, 69, 71], [.25, .2, .18, .14, .1, .08])
tense = pad([40, 52, 53, 59], [.42, .25, .12, .14])                 # E with a b9 rub
cold = pad([38, 45, 50, 53, 57], [.4, .26, .2, .14, .1])           # D minor
P, T, B = C['pak'], C['turn'], C['back']
bed = (room * env(t, [(0, .8), (P - .2, .8), (P + .8, 0), (B + 1.5, 0), (B + 3, .8), (C['black'], .8), (C['black'] + .2, 0)])
       + wish * env(t, [(P + .6, 0), (P + 1.6, 1), (T, 1), (T + 1, 0)])
       + tense * env(t, [(T, 0), (T + 1.2, .8), (C['wind'], .9), (C['wind'] + 1, .3), (C['hero'], .3), (C['hero'] + .5, 0), (C['ant'], 0), (C['ant'] + 1.5, .5), (B, .5), (B + 1, 0)])
       + cold * env(t, [(C['wind'], 0), (C['wind'] + 1, 1), (C['hero'], 1), (C['hero'] + 1.5, .6), (C['ant'], .3), (C['ant'] + 1, 0)]))
bed *= (1 + .12 * np.sin(2 * np.pi * .23 * t)) * .12
mus += np.stack([bed, np.roll(bed, 300)], 1)
# rain on the window: soft hiss at room scale, bigger and lower once you are small
d = tt(DUR); x = rng.standard_normal(len(d))
hiss = bp(x, 3500, 10000) * env(t, [(0, .12), (P, .12), (P + 1.5, .06), (B + 1, .06), (B + 3, .12), (C['black'], .12), (C['black'] + .3, 0)])
rumble = lp(x, 400) * env(t, [(P + 1, 0), (C['rain'] - 1, .4), (C['hero'], .5), (B, .5), (B + 2, 0)]) * .6
put(fx, hiss + rumble, 0)
# the clock: one soft tick per beat (keeps the grid measurable), silent in the black
TICK = bp(rng.standard_normal(int(.04 * SR)), 700, 9000) * np.exp(-tt(.04) * 120)      # a crisp broadband click (stands out across bands)
for k in range(1, int(C['black'] / .5)): put(mus, TICK * .2, k * .5, 1, .3 if k % 2 else -.3)
# superhero plucks on the beat from the shrink to the turn
for k in range(int((P + 1.5) / .5), int(T / .5)):
    q = k * .5; f = mtof([69, 73, 76, 81][k % 4]); dd = tt(.4)
    put(mus, (np.sin(2 * np.pi * f * dd) + .3 * np.sin(2 * np.pi * 2 * f * dd)) * np.exp(-dd * 9) * .08, q, 1, (-.4, .4)[k % 2])
# the uneasy pulse on the floor
for k in range(int(T / .5) + 1, int(C['hero'] / .5)):
    q = k * .5; f = mtof(52 if k % 4 == 0 else 47); dd = tt(.3)
    put(mus, np.sin(2 * np.pi * f * dd) * np.exp(-dd * 12) * .08, q, 1, 0)
def sweep(dur, f0, f1):
    dd = tt(dur); x = rng.standard_normal(len(dd)); out = np.zeros(len(dd))
    for i in range(0, len(dd), 2400): u = i / len(dd); fc = f0 * (f1 / f0) ** u; seg = x[max(0, i - 4800):i + 2400]; out[i:i + 2400] = bp(seg, fc * .7, fc * 1.4)[-len(x[i:i + 2400]):]
    return out * np.sin(np.pi * dd / dur) ** 2
thump = lambda f=50, d=.8, a=.7: np.sin(2 * np.pi * f * tt(d) * (1 + .5 * np.exp(-tt(d) * 20))) * np.exp(-tt(d) * 5) * a
click = lambda: bp(rng.standard_normal(int(.03 * SR)), 2000, 8000) * np.exp(-tt(.03) * 80) * .8
def blip(): dd = tt(.16); return (np.sin(2 * np.pi * 1760 * dd) * (dd < .06) + np.sin(2 * np.pi * 2637 * dd) * (dd >= .07)) * np.exp(-dd * 18) * .3
def bell(m, d=3.5): x = tt(d); f = mtof(m); return (np.sin(2 * np.pi * f * x) * np.exp(-x * 1.3) + .4 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 3)) * .3
# 啪: the shrink — a click, a falling whoosh, a soft low thump when you arrive
put(fx, click(), P); put(fx, sweep(1.6, 6000, 250) * .55, P); put(fx, thump(60, .8, .5), P + 1.5)
# superhero beats
for key in ('half', 'clip', 'surf', 'heavy', 'x5', 'minutes', 'eat'): put(fx, blip(), C[key], 1, .3)
dd = tt(1.2); put(fx, (np.sin(2 * np.pi * 2900 * dd) + .5 * np.sin(2 * np.pi * 4350 * dd)) * np.exp(-dd * 5) * .18, C['lift'])      # the clip: a metal ting
put(fx, sweep(.9, 400, 5000) * .45, C['jump']); put(fx, sweep(1.6, 800, 300) * .25, C['jump'] + .8)
put(fx, bp(rng.standard_normal(int(.08 * SR)), 300, 1500) * np.exp(-tt(.08) * 40) * .5, C['land'])
put(fx, sweep(1.0, 3000, 400) * .3, T)
# water: a plop when the drop wraps you, a deep thump for every raindrop (the film puts each impact on the beat)
def plop(): dd = tt(.25); return np.sin(2 * np.pi * np.cumsum(300 + 900 * np.exp(-dd * 30)) / SR) * np.exp(-dd * 14) * .5
put(fx, plop(), C['drop'])
for i in range(20):
    ti = C['x5'] - 1 + i * .5
    if C['rain'] - .2 <= ti < C['hero']: put(fx, thump(45, .5, .55) + bp(rng.standard_normal(int(.5 * SR)), 800, 4000) * np.exp(-tt(.5) * 12) * .25, ti, 1, rng.uniform(-.5, .5))
# the draught
dd = tt(C['food'] - C['wind'] + 1); x = rng.standard_normal(len(dd)); put(fx, bp(x, 200, 1800) * env(dd, [(0, 0), (.8, .5), (len(dd) / SR - .8, .5), (len(dd) / SR, 0)]) * .5, C['wind'])
# eating: small crunches on the beat
for k in range(6): put(fx, bp(rng.standard_normal(int(.05 * SR)), 1500, 6000) * np.exp(-tt(.05) * 60) * .35, C['eat'] + k * .5)
# the reversal: a deep hit, a bell on the cause
put(fx, thump(36, 2.0, .9), C['same']); put(mus, bell(64, 4), C['cause'])
# the ant: tiny steps
for k in range(int(C['ant'] / .25), int(C['back'] / .25)): put(fx, bp(rng.standard_normal(int(.015 * SR)), 4000, 10000) * np.exp(-tt(.015) * 200) * .12, k * .25, 1, .4)
for i, key in enumerate(('antp',)): put(fx, blip(), C[key], 1, -.3)
# growing back: a rising sweep, then the room returns; one bell for the question
put(fx, sweep(2.4, 250, 6000) * .5, B + .2); put(mus, bell(76, 3), B + 2.5); put(mus, bell(69, 5), C['next'])
HITS = {k: C[k] for k in ('pak', 'half', 'clip', 'lift', 'jump', 'land', 'turn', 'surf', 'drop', 'heavy', 'x5', 'wind', 'minutes', 'eat', 'same', 'cause', 'antp', 'next')}
os.makedirs(os.path.join(ROOT, 'audio'), exist_ok=True)
json.dump(HITS, open(os.path.join(ROOT, 'audio', 'hits.json'), 'w'), indent=1)
score = mus + fx
sf.write(os.path.join(ROOT, 'audio', 'score.wav'), score.astype(np.float32), SR)
voice, _ = sf.read(os.path.join(ROOT, 'voice', 'voice.wav')); voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
m = pyln.Meter(SR)
voice *= 10 ** ((-16 - m.integrated_loudness(voice)) / 20)
b = score.copy(); b *= 10 ** ((-24 - m.integrated_loudness(b)) / 20)
# duck the bed under the voice: up to −11 dB while speaking, and always at least 12 dB under the voice
fr = int(.05 * SR); nf = N // fr
ve = np.sqrt(np.convolve((voice[:nf * fr] ** 2).reshape(nf, fr).mean(1), np.ones(6) / 6, 'same')) + 1e-9
be = np.sqrt(np.convolve((b[:nf * fr] ** 2).mean(1).reshape(nf, fr).mean(1), np.ones(6) / 6, 'same')) + 1e-9
talk = np.clip(20 * np.log10(ve) + 45, 0, 1)
g = 10 ** (-11 * talk / 20); over = np.maximum(0, 20 * np.log10(be * g) - (20 * np.log10(ve) - 12)) * talk; g *= 10 ** (-over / 20)
g = np.convolve(g, np.ones(4) / 4, 'same'); b *= np.interp(np.arange(N), np.arange(nf) * fr + fr / 2, g)[:, None]
mix = b + voice[:, None]; mix *= 10 ** ((-14 - m.integrated_loudness(mix)) / 20); mix = np.tanh(mix / .89) * .89
mix *= 10 ** ((-14 - m.integrated_loudness(mix)) / 20)
sf.write(os.path.join(ROOT, 'audio', 'mix_full.wav'), mix.astype(np.float32), SR)
print('mix', round(m.integrated_loudness(mix), 2), 'LUFS, peak', round(20 * np.log10(np.abs(mix).max()), 2), 'dBFS,', DUR, 's')
