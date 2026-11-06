"""Sound for 「你按下去之后」· 你上划之前: Fish 「科普」 voice + a synthesized bed and SFX on the cues (120 BPM half-beat grid)
-> audio/score.wav, audio/hits.json, audio/mix_full.wav at -14 LUFS.
Arc: a quiet night in bed → a glassy dive through the screen → soft digital pulses while the videos download →
your seconds tick → the signal zips off over the city → the hum of the data centre → the wall, the funnel, the odds."""
import os, json, re, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import butter, sosfilt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SR = 48000
s = open(os.path.join(ROOT, 'film', 'data.js')).read()
TL = json.loads(re.search(r'window.TL=(\{.*?\});', s).group(1)); C = json.loads(re.search(r'window.CUES=(\{.*\});', s).group(1))['c']
DUR = TL['duration']; N = int(DUR * SR); rng = np.random.default_rng(11)
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
night = pad([45, 52, 57, 59, 64], [.3, .2, .16, .1, .08])
journey = pad([41, 53, 57, 60, 64], [.32, .2, .16, .12, .08])
dc = pad([36, 43, 48, 55], [.45, .25, .18, .1])
turn = pad([40, 52, 55, 59], [.4, .22, .16, .12])
D = C['dive']
bed = (night * env(t, [(0, .9), (D - .2, .9), (D + .6, 0), (C['home'], 0), (C['home'] + 1.5, .9), (C['black'], .9)])
       + journey * env(t, [(D, 0), (D + .8, .9), (C['dc'], .9), (C['dc'] + 1, 0), (C['top'], 0), (C['top'] + 1, .8), (C['rev'], .8), (C['rev'] + .8, 0)])
       + dc * env(t, [(C['dc'] - .3, 0), (C['dc'] + .8, 1), (C['top'], 1), (C['top'] + 1, 0)])
       + turn * env(t, [(C['rev'], 0), (C['rev'] + 1, .9), (C['home'], .9), (C['home'] + 1.5, 0)]))
bed *= (1 + .12 * np.sin(2 * np.pi * .21 * t)) * .12
mus += np.stack([bed, np.roll(bed, 300)], 1)
# the data-centre air: fans
d = tt(C['top'] - C['dc'] + 1); put(fx, bp(rng.standard_normal(len(d)), 120, 900) * env(d, [(0, 0), (.8, .25), (len(d) / SR - .8, .25), (len(d) / SR, 0)]), C['dc'])
# the beat: a crisp click on every beat (keeps the grid measurable), silent in the black
TICK = bp(rng.standard_normal(int(.04 * SR)), 700, 9000) * np.exp(-tt(.04) * 120)
for k in range(1, int(C['black'] / .5)): put(mus, TICK * .18, k * .5, 1, .3 if k % 2 else -.3)
# soft digital arpeggio on the half-beat during the journey
for k in range(int((D + .5) / .25), int(C['rev'] / .25)):
    q = k * .25; f = mtof([69, 72, 76, 79, 76, 72][k % 6] + (12 if C['dc'] <= q < C['top'] else 0)); dd = tt(.18)
    put(mus, np.sin(2 * np.pi * f * dd) * np.exp(-dd * 22) * .045, q, 1, (-.5, .5)[k % 2])
def sweep(dur, f0, f1):
    dd = tt(dur); x = rng.standard_normal(len(dd)); out = np.zeros(len(dd))
    for i in range(0, len(dd), 2400): u = i / len(dd); fc = f0 * (f1 / f0) ** u; seg = x[max(0, i - 4800):i + 2400]; out[i:i + 2400] = bp(seg, fc * .7, fc * 1.4)[-len(x[i:i + 2400]):]
    return out * np.sin(np.pi * dd / dur) ** 2
thump = lambda f=50, d=.8, a=.7: np.sin(2 * np.pi * f * tt(d) * (1 + .5 * np.exp(-tt(d) * 20))) * np.exp(-tt(d) * 5) * a
def blip(f1=1760, f2=2637): dd = tt(.16); return (np.sin(2 * np.pi * f1 * dd) * (dd < .06) + np.sin(2 * np.pi * f2 * dd) * (dd >= .07)) * np.exp(-dd * 18) * .3
def bell(m, d=3.0): x = tt(d); f = mtof(m); return (np.sin(2 * np.pi * f * x) * np.exp(-x * 1.4) + .4 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 3)) * .3
def pluck(m): dd = tt(.5); f = mtof(m); return (np.sin(2 * np.pi * f * dd) + .3 * np.sin(4 * np.pi * f * dd)) * np.exp(-dd * 8) * .25
# the laugh: a playful pluck pair
put(mus, pluck(76), C['laugh']); put(mus, pluck(81), C['laugh'] + .25)
# through the screen: a glassy rising shimmer and a soft thump
put(fx, sweep(1.0, 800, 9000) * .45, D - .25); put(fx, thump(55, .7, .5), D + .5)
# the queue fills: one blip per card as it finishes downloading
for i in (1, 2, 3): put(fx, blip(1568 + i * 200, 2349 + i * 200), C['dl'] + i * .5 + 1.0, 1, .4)
put(fx, blip(), C['queue'])
# 谁挑的？ two rising notes; 是你。 a low hit and a bell
put(mus, pluck(69), C['who']); put(mus, pluck(74), C['who'] + .5)
put(fx, thump(40, 1.4, .8), C['you']); put(mus, bell(76), C['you'])
# your seconds tick
for n in range(0, int(C['fly'] - C['secs']) + 1): put(fx, bp(rng.standard_normal(int(.03 * SR)), 2000, 6000) * np.exp(-tt(.03) * 90) * .4, C['secs'] + n, 1, -.3)
# the signal zips off, the flight, arriving inside
dd = tt(1.0); put(fx, np.sin(2 * np.pi * np.cumsum(500 + 2500 * dd) / SR) * np.exp(-dd * 3) * .25, C['signal'])
put(fx, sweep(1.6, 300, 4000) * .5, C['fly']); put(fx, thump(48, 1.0, .6), C['dc'])
# the wall, the funnel, the odds
put(fx, sweep(1.2, 2000, 9000) * .3, C['sea']); put(fx, sweep(1.2, 5000, 300) * .5, C['pick'])
for key, n in (('q1', 0), ('q2', 1), ('q3', 2), ('q4', 3)): put(fx, blip(1318 + n * 200, 1976 + n * 260), C[key], 1, (-.4, .4)[n % 2])
# (rest of the film)
put(fx, sweep(.8, 400, 5000) * .4, C['back']); put(fx, sweep(.5, 3000, 600) * .35, C['swipe'])
put(fx, thump(36, 1.8, .9), C['rev2']); put(mus, bell(64, 4), C['rev2'])
put(fx, blip(1200, 900), C['nope'])
put(fx, sweep(2.0, 6000, 300) * .4, C['home']); put(mus, bell(69, 5) * .8, C['self'] + 2.0)
# paper sounds for the second half (all on the quarter-beat grid)
def tap(a=.5): dd = tt(.12); return (bp(rng.standard_normal(len(dd)), 300, 3500) * np.exp(-dd * 45) + np.sin(2 * np.pi * 140 * dd) * np.exp(-dd * 30) * .8) * a
def rustle(dur, a=.4):
    dd = tt(dur); g = np.repeat(rng.random(len(dd) // 144 + 1) ** 3, 144)[:len(dd)]
    return bp(rng.standard_normal(len(dd)), 1500, 7000) * lp(g, 400) * 6 * np.sin(np.pi * dd / dur) * a
def swish(a=.35): return sweep(.22, 900, 4000) * a
PAPER = {}
put(fx, rustle(.5, .4), C['next1'], 1, .5); PAPER['peek'] = C['next1']
for i, tt0 in enumerate((C['top'], C['top'] + .25, C['top'] + .5)): put(fx, tap(.55), tt0, 1, (-.4, 0, .4)[i]); PAPER[f'rank{i}'] = tt0
put(fx, sweep(.45, 600, 6000) * .3, C['top'] + 1.25); PAPER['lace'] = C['top'] + 1.25
for i, tt0 in enumerate((34.25, 34.5, 34.75)): put(fx, tap(.5), tt0, 1, (-.4, 0, .4)[i]); PAPER[f'land{i}'] = tt0
put(fx, rustle(.8, .5), C['loop'] - .5); PAPER['popup'] = C['loop'] - .5
for i, tt0 in enumerate((41.0, 41.5, 42.0)): put(fx, swish(), tt0, 1, .2); PAPER[f'flick{i}'] = tt0
for i in range(5): tt0 = C['tip'] + .25 * (i + 1); put(fx, bp(rng.standard_normal(int(.03 * SR)), 2000, 6000) * np.exp(-tt(.03) * 90) * .45, tt0, 1, -.3); PAPER[f'stare{i}'] = tt0
put(fx, tap(.6), 46.5); put(fx, sweep(.9, 500, 3000) * .3, 46.5); PAPER['minus'] = 46.5
for i, tt0 in enumerate((47.5, 47.75, 48.0, 48.25)): put(fx, rustle(.2, .35), tt0, 1, .4); PAPER[f'flip{i}'] = tt0
HITS = {k: C[k] for k in ('laugh', 'dive', 'queue', 'who', 'you', 'secs', 'signal', 'fly', 'dc', 'sea', 'pick', 'q1', 'q2', 'q3', 'q4', 'back', 'swipe', 'rev2', 'nope', 'home')}
HITS['bell_end'] = C['self'] + 2.0
HITS.update(PAPER)
os.makedirs(os.path.join(ROOT, 'audio'), exist_ok=True)
json.dump(HITS, open(os.path.join(ROOT, 'audio', 'hits.json'), 'w'), indent=1)
score = mus + fx
sf.write(os.path.join(ROOT, 'audio', 'score.wav'), score.astype(np.float32), SR)
voice, _ = sf.read(os.path.join(ROOT, 'voice', 'voice.wav')); voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
m = pyln.Meter(SR)
voice *= 10 ** ((-16 - m.integrated_loudness(voice)) / 20)
b = score.copy(); b *= 10 ** ((-24 - m.integrated_loudness(b)) / 20)
fr = int(.05 * SR); nf = N // fr
ve = np.sqrt(np.convolve((voice[:nf * fr] ** 2).reshape(nf, fr).mean(1), np.ones(6) / 6, 'same')) + 1e-9
be = np.sqrt(np.convolve((b[:nf * fr] ** 2).mean(1).reshape(nf, fr).mean(1), np.ones(6) / 6, 'same')) + 1e-9
talk = np.clip(20 * np.log10(ve) + 45, 0, 1)
g = 10 ** (-11 * talk / 20); over = np.maximum(0, 20 * np.log10(be * g) - (20 * np.log10(ve) - 12)) * talk; g *= 10 ** (-over / 20)
g = np.convolve(g, np.ones(4) / 4, 'same'); b *= np.interp(np.arange(N), np.arange(nf) * fr + fr / 2, g)[:, None]
mix = b + voice[:, None]; mix *= 10 ** ((-14 - m.integrated_loudness(mix)) / 20); mix = np.tanh(mix / .89) * .89
fo = int(.45 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5      # a short tail, no click
mix *= 10 ** ((-14 - m.integrated_loudness(mix)) / 20)
sf.write(os.path.join(ROOT, 'audio', 'mix_full.wav'), mix.astype(np.float32), SR)
print('mix', round(m.integrated_loudness(mix), 2), 'LUFS, peak', round(20 * np.log10(np.abs(mix).max()), 2), 'dBFS,', DUR, 's')
