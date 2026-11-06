"""Sound for 「你按下去之后」· 你刚说完: Fish 「科普」 voice + a synthesized bed and paper SFX on the cues (120 BPM, half-beat grid)
-> audio/score.wav, audio/hits.json, audio/mix_full.wav at -14 LUFS.
Arc: a warm dinner → a small doubt (偷听?) → inside the microphone, hushed → the lab stamp → three clues click into place
→ the feed rushes past and one card is pinned → the turn (先替你开了口) → a switch flicks off → back to the table."""
import os, json, re, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import butter, sosfilt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SR = 48000
s = open(os.path.join(ROOT, 'film', 'data.js')).read()
TL = json.loads(re.search(r'window.TL=(\{.*?\});', s).group(1)); C = json.loads(re.search(r'window.CUES=(\{.*\});', s).group(1))['c']
DUR = TL['duration']; N = int(DUR * SR); rng = np.random.default_rng(23)
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
warm = pad([48, 55, 60, 64, 67], [.3, .2, .15, .1, .07])          # the dinner table
hush = pad([41, 48, 53, 56], [.38, .22, .14, .08])                 # inside the microphone
clue = pad([45, 52, 57, 60, 64], [.32, .2, .16, .12, .08])         # the clues
turn = pad([43, 50, 55, 59], [.4, .22, .16, .12])                  # the turn
D = C['dive']
bed = (warm * env(t, [(0, .9), (D - .2, .9), (D + .5, 0), (C['home'], 0), (C['home'] + 1.2, .9), (DUR, .9)])
       + hush * env(t, [(D - .1, 0), (D + .6, 1), (C['but'], 1), (C['but'] + .8, 0)])
       + clue * env(t, [(C['but'], 0), (C['but'] + .8, .9), (C['rev'], .9), (C['rev'] + .8, 0)])
       + turn * env(t, [(C['rev'], 0), (C['rev'] + 1, .9), (C['home'], .9), (C['home'] + 1.2, 0)]))
bed *= (1 + .12 * np.sin(2 * np.pi * .21 * t)) * .12
mus += np.stack([bed, np.roll(bed, 300)], 1)
# a crisp click on every beat keeps the grid measurable
TICK = bp(rng.standard_normal(int(.04 * SR)), 700, 9000) * np.exp(-tt(.04) * 120)
for k in range(1, int((DUR - .5) / .5)): put(mus, TICK * .18, k * .5, 1, .3 if k % 2 else -.3)
# soft plucked arpeggio on the half-beat while the clues come together
def pluck(m, d=.5): dd = tt(d); f = mtof(m); return (np.sin(2 * np.pi * f * dd) + .3 * np.sin(4 * np.pi * f * dd)) * np.exp(-dd * 8) * .25
for k in range(int(C['clue'] / .25) + 2, int(C['rev'] / .25)):
    q = k * .25; put(mus, pluck([69, 72, 76, 79, 76, 72][k % 6]) * .18, q, 1, (-.5, .5)[k % 2])
def sweep(dur, f0, f1):
    dd = tt(dur); x = rng.standard_normal(len(dd)); out = np.zeros(len(dd))
    for i in range(0, len(dd), 2400): u = i / len(dd); fc = f0 * (f1 / f0) ** u; seg = x[max(0, i - 4800):i + 2400]; out[i:i + 2400] = bp(seg, fc * .7, fc * 1.4)[-len(x[i:i + 2400]):]
    return out * np.sin(np.pi * dd / dur) ** 2
thump = lambda f=50, d=.8, a=.7: np.sin(2 * np.pi * f * tt(d) * (1 + .5 * np.exp(-tt(d) * 20))) * np.exp(-tt(d) * 5) * a
def blip(f1=1760, f2=2637): dd = tt(.16); return (np.sin(2 * np.pi * f1 * dd) * (dd < .06) + np.sin(2 * np.pi * f2 * dd) * (dd >= .07)) * np.exp(-dd * 18) * .3
def bell(m, d=3.0): x = tt(d); f = mtof(m); return (np.sin(2 * np.pi * f * x) * np.exp(-x * 1.4) + .4 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 3)) * .3
def tap(a=.5): dd = tt(.12); return (bp(rng.standard_normal(len(dd)), 300, 3500) * np.exp(-dd * 45) + np.sin(2 * np.pi * 140 * dd) * np.exp(-dd * 30) * .8) * a
def rustle(dur, a=.4):
    dd = tt(dur); g = np.repeat(rng.random(len(dd) // 144 + 1) ** 3, 144)[:len(dd)]
    return bp(rng.standard_normal(len(dd)), 1500, 7000) * lp(g, 400) * 6 * np.sin(np.pi * dd / dur) * a
H = {}
def hit(name, tm, sig, buf=fx, g=1, pan=0): put(buf, sig, tm, g, pan); H[name] = tm
hit('say', C['say'], pluck(76), mus); put(mus, pluck(81), C['say'] + .25)                    # the speech bubble pops
hit('push', C['push'], blip(1318, 1976))                                                     # the push arrives
hit('ask', C['ask'], pluck(69), mus); put(mus, pluck(74), C['ask'] + .5)                     # 偷听你？
hit('dive', D - .25, sweep(1.0, 800, 9000) * .45); put(fx, thump(55, .7, .5), D + .25)       # into the microphone hole
hit('listen', C['listen'], sweep(.8, 400, 3000) * .3)                                       # the microphone wakes
hit('suck', C['suck'], sweep(1.1, 600, 7000) * .45)                                          # your words are sucked in
hit('server', C['server'], thump(48, 1.0, .6))                                               # into the machine room
hit('hit', C['hit'], bell(79, 2.0) * .7, mus); put(fx, blip(1760, 2637), C['hit'])           # 「空气炸锅」 lights up
hit('back', C['back'], sweep(1.0, 6000, 500) * .45)                                          # the ad flies back
hit('but2', C['but2'], tap(.7)); put(mus, pluck(62) * .8, C['but2'])                          # 可是……
hit('off', C['off'], tap(.6)); put(fx, blip(1200, 900), C['off'] + .25)                       # the microphone switch
hit('again', C['again'], sweep(.5, 2000, 4000) * .3); put(fx, blip(1318, 1976), C['again'] + .25)   # it comes anyway
hit('six', C['six'], blip(1568, 2349))                                                       # your 6 seconds
hit('search', C['search'], blip(1760, 2637))                                                 # your friend's search
for i in range(3): put(fx, sweep(.5, 600, 2400) * .25, C['wifi'] + .5 * i, 1, .3)              # Wi-Fi ripples
H['wifi'] = C['wifi']
hit('gang', C['gang'], thump(48, .9, .5)); put(mus, bell(76, 2.5) * .6, C['gang'])
for i in range(int((C['pin'] - C['feed']) / .25)): put(fx, rustle(.12, .22), C['feed'] + .25 * i, 1, (-.4, .4)[i % 2])   # the feed rushes past
H['feed'] = C['feed']
hit('pin', C['pin'], tap(.7))
hit('rev2', C['rev2'], thump(36, 1.8, .9)); put(mus, bell(64, 4), C['rev2'])
hit('toggle', C['toggle'], tap(.5)); put(fx, blip(1200, 900), C['toggle'] + .25)
hit('law', C['law'], tap(.4))
hit('home', C['home'] - .5, sweep(1.6, 5000, 400) * .35)
hit('bell_end', C['self'] + 1.75, bell(69, 5) * .8, mus)
os.makedirs(os.path.join(ROOT, 'audio'), exist_ok=True)
json.dump(H, open(os.path.join(ROOT, 'audio', 'hits.json'), 'w'), indent=1)
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
