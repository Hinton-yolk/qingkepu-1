"""Draft sound for If-series 02: Fish 「科普」 voice + a synthesized bed and SFX on the cues (120 BPM half-beat grid)
-> audio/score.wav, audio/hits.json, audio/mix_full.wav at -14 LUFS.
Arc: warm dusk → golden wish (opens at 啪) → a pulse of unease that gets denser (cup → street → air → sea) →
a rewind and a calm, slow second world (one day = one year, then night) → cold reversal (the sea moves) → a low sea drone → one bell."""
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
dusk = pad([50, 57, 62, 66], [.3, .22, .16, .1])                  # D major-ish, warm
wish = pad([50, 62, 66, 69, 74, 76], [.3, .22, .2, .16, .12, .08])   # brighter, open
uneasy = pad([45, 57, 58, 64], [.42, .25, .14, .16])               # A with a b9 rub
gentle = pad([43, 55, 62, 67], [.3, .2, .14, .1])                  # G, slow and calm
night = pad([38, 45, 50, 53], [.4, .25, .2, .12])                  # D minor, low
cold = pad([40, 47, 52, 55, 59], [.42, .26, .2, .14, .1])         # E minor add9
sea = pad([33, 40, 45, 52], [.5, .3, .25, .12])
P, T, G, R, NI = C['pak'], C['turn'], C['gentle'], C['realSea'], C['night']
bed = (dusk * env(t, [(0, .7), (P - .2, .7), (P + .6, 0)])
       + wish * env(t, [(P, 0), (P + 1, 1), (T, 1), (T + 1.2, 0)])
       + uneasy * env(t, [(T, 0), (T + 1.5, .7), (C['cars'], .9), (C['sea'], 1), (G, 1), (G + .6, 0)])
       + gentle * env(t, [(G + .4, 0), (G + 1.6, .9), (NI, .9), (NI + 1.5, 0)])
       + night * env(t, [(NI, 0), (NI + 1.5, .9), (R, .9), (R + 1, 0)])
       + cold * env(t, [(R, 0), (R + 1.5, .9), (C['black'] - .6, .9), (C['black'], 0)])
       + sea * 0)
bed *= (1 + .12 * np.sin(2 * np.pi * .23 * t)) * .12
mus += np.stack([bed, np.roll(bed, 300)], 1)
# the unease pulse: from 「但有一个问题」 to the rewind, denser as it gets bigger
for k in range(int(T / .5) + 1, int(G / .5)):
    q = k * .5; d = tt(.3); f = mtof(69 if k % 4 == 0 else 64)
    dens = 1 if q < C['cup'] else 2
    for j in range(dens):
        put(mus, (np.sin(2 * np.pi * f * (1 + .5 * j) * d) + .3 * np.sin(2 * np.pi * 2.76 * f * d)) * np.exp(-d * 16) * .08, q + j * .5 / dens, 1, rng.uniform(-.6, .6))
# the planet's clock: one soft tick per beat for the whole film (louder in the slow world), silent in the black
TICK = bp(rng.standard_normal(int(.06 * SR)), 2500, 7000) * np.exp(-tt(.06) * 70)
for k in range(1, int(C['black'] / .5)):
    q = k * .5; g = .1 if C['noFly'] <= q < R else .05
    put(mus, TICK * g, q, 1, .3 if k % 2 else -.3)
def sweep(dur, f0, f1, up=True):
    d = tt(dur); x = rng.standard_normal(len(d)); out = np.zeros(len(d))
    for i in range(0, len(d), 2400):
        u = i / len(d); fc = f0 * (f1 / f0) ** (u if up else 1 - u); seg = x[max(0, i - 4800):i + 2400]; out[i:i + 2400] = bp(seg, fc * .7, fc * 1.4)[-len(x[i:i + 2400]):]
    return out * np.sin(np.pi * d / dur) ** 2
thump = lambda f=50, d=.8, a=.7: np.sin(2 * np.pi * f * tt(d) * (1 + .5 * np.exp(-tt(d) * 20))) * np.exp(-tt(d) * 5) * a
click = lambda: bp(rng.standard_normal(int(.03 * SR)), 2000, 8000) * np.exp(-tt(.03) * 80) * .8
def blip(): d = tt(.16); return (np.sin(2 * np.pi * 1760 * d) * (d < .06) + np.sin(2 * np.pi * 2637 * d) * (d >= .07)) * np.exp(-d * 18) * .3
def bell(m, d=3.5): x = tt(d); f = mtof(m); return (np.sin(2 * np.pi * f * x) * np.exp(-x * 1.3) + .4 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 3)) * .3
# 啪 ×3: the switch (自转 0×), the gentle brake, the spin coming back
for key in ('pak', 'pak2'):
    put(fx, click(), C[key] - .25); put(fx, sweep(1.1, 300, 6000) * .5, C[key]); put(fx, thump(), C[key])
put(fx, click(), C['always'] + .35); put(fx, sweep(1.1, 300, 6000) * .45, C['always'] + .6)
put(mus, bell(74), C['frozen'])      # the sun stops: one clear note
# the turn: the gold drains with a falling sweep
put(fx, sweep(1.2, 4000, 200, up=False) * .45, T)
# locks and readouts
for key in ('coffee', 'endless', 'beijing', 'speed', 'together', 'noFeel', 'record', 'x3', 'year', 'week', 'pile', 'harbin', 'scs', 'fat', 'coast'):
    put(fx, blip(), C[key], 1, .3)
put(fx, bp(rng.standard_normal(int(.25 * SR)), 1500, 5000) * np.exp(-tt(.25) * 14) * .4, C['sound'])      # the sound barrier crack
# the ground stops: a hard thump and a short silence in the bed (ducked below)
put(fx, thump(38, 1.6, 1.0), C['groundStop']); put(fx, click(), C['groundStop'] - .02)
# the fling chain: whooshes left → right
FL = {'cup': C['cup'], 'dripper': C['cup'] + .25, 'plant': C['cup'] + .5, 'table': C['cup'] + .75, 'you': C['you'], 'chair': C['you'] + .25, 'cars': C['cars'], 'loose': C['loose'], 'east': C['east']}
for key, g in (('cup', .5), ('dripper', .35), ('plant', .4), ('table', .5), ('you', .6), ('chair', .35), ('cars', .7), ('loose', .7), ('east', .5)):
    put(fx, sweep(.7, 500, 6000) * g, FL[key] - .05, 1, -.5); put(fx, click() * g * .6, FL[key])
for i in range(1, 6):      # windows blowing out behind the wind front
    for j in range(3): put(fx, bp(rng.standard_normal(int(.12 * SR)), 3000, 11000) * np.exp(-tt(.12) * 30) * .35, C['air'] + i * .25 + j * .03, 1, rng.uniform(-.8, .8))
# the air: a wind roar from 「空气」 to the sea, brightening
d = tt(C['gentle'] - C['air'] + .5); x = rng.standard_normal(len(d))
wind = (bp(x, 70, 700) + .35 * bp(x, 3500, 9000)) * env(d, [(0, 0), (1.0, .6), (C['x3'] - C['air'], .9), (C['gentle'] - C['air'], .9), (len(d) / SR, 0)])
put(fx, wind * .2, C['air'], 1, 0)
# the sea: a long low rumble, a slam at 「拍向」
d = tt(4); put(fx, lp(rng.standard_normal(len(d)), 220) * np.exp(-d * .6) * 1.3, C['ocean']); put(fx, sweep(1.0, 300, 3000) * .45, C['slam']); put(fx, thump(32, 2.2, 1.0), C['slam'] + 1.0)
# rewind: a reversed sweep
put(fx, sweep(.9, 6000, 300, up=False) * .55, C['gentle'])
# night falls: one low note
put(mus, bell(50, 5) * .8, C['night']); put(mus, bell(79, 2.5) * .7, C['slow']); put(fx, sweep(.9, 400, 4000) * .4, C['dusk'])
# the reversal: a deep hit when the sea starts to move, a water swish to the poles, a hit on the map
put(fx, thump(36, 2.0, .9), C['realSea'] + .4); put(mus, bell(64, 4), C['realSea'] + .4)
put(fx, thump(30, 1.4, .8), C['stopSpin'])
d = tt(2.2); put(fx, lp(bp(rng.standard_normal(len(d)), 200, 3000), 2500) * np.sin(np.pi * d / 2.2) ** 2 * .6, C['flow'], 1, -.3)
put(fx, thump(34, 2.0, .9), C['map'])
put(mus, bell(76), C['always'] + .6)
put(mus, bell(69, 5), C['next'])
HITS = dict({k: v for k, v in FL.items()}, slam2=C['slam'] + 1.0, **{k: C[k] for k in ('pak', 'frozen', 'turn', 'coffee', 'beijing', 'speed', 'sound', 'together', 'noFeel', 'groundStop', 'cup', 'you', 'cars', 'loose', 'east',
                          'air', 'record', 'x3', 'ocean', 'slam', 'gentle', 'pak2', 'year', 'week', 'night', 'fat', 'stopSpin', 'flow', 'map', 'harbin', 'scs', 'coast', 'next', 'endless', 'slow', 'dusk', 'pile')})
os.makedirs(os.path.join(ROOT, 'audio'), exist_ok=True)
json.dump(HITS, open(os.path.join(ROOT, 'audio', 'hits.json'), 'w'), indent=1)
score = mus + fx
duck = env(t, [(0, 1), (C['groundStop'] - .05, 1), (C['groundStop'], .25), (C['youNot'] + .4, .25), (C['youNot'] + .9, 1), (DUR, 1)])
score *= duck[:, None]
sf.write(os.path.join(ROOT, 'audio', 'score.wav'), score.astype(np.float32), SR)
voice, _ = sf.read(os.path.join(ROOT, 'voice', 'voice.wav')); voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
m = pyln.Meter(SR)
voice *= 10 ** ((-16 - m.integrated_loudness(voice)) / 20)
b = score.copy(); b *= 10 ** ((-24 - m.integrated_loudness(b)) / 20)
# duck the bed under the voice: short-term voice level drives up to −9 dB, and the bed is also held at least 8 dB under the voice
fr = int(.05 * SR); nf = N // fr
ve = np.sqrt(np.convolve(np.pad(voice[:nf * fr] ** 2, (0, 0)).reshape(nf, fr).mean(1), np.ones(6) / 6, 'same')) + 1e-9
be = np.sqrt(np.convolve((b[:nf * fr] ** 2).mean(1).reshape(nf, fr).mean(1), np.ones(6) / 6, 'same')) + 1e-9
talk = np.clip(20 * np.log10(ve) + 45, 0, 1)      # 1 while someone is speaking
g = 10 ** (-11 * talk / 20)
over = np.maximum(0, 20 * np.log10(be * g) - (20 * np.log10(ve) - 12)) * talk
g *= 10 ** (-over / 20)
g = np.convolve(g, np.ones(4) / 4, 'same')
b *= np.interp(np.arange(N), np.arange(nf) * fr + fr / 2, g)[:, None]
mix = b + voice[:, None]; mix *= 10 ** ((-14 - m.integrated_loudness(mix)) / 20); mix = np.tanh(mix / .89) * .89
mix *= 10 ** ((-14 - m.integrated_loudness(mix)) / 20)
sf.write(os.path.join(ROOT, 'audio', 'mix_full.wav'), mix.astype(np.float32), SR)
print('mix', round(m.integrated_loudness(mix), 2), 'LUFS, peak', round(20 * np.log10(np.abs(mix).max()), 2), 'dBFS,', DUR, 's')
