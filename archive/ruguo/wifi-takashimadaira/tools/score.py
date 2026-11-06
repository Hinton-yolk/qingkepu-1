"""Score + room, synthesized from the one timeline (timeline.json). 120 BPM; every hit sits on a beat.
Palette (white-model sound): mallets and glass for light switching on, bowed vibraphone for held light, contrabass/cello floor,
timpani + gran cassa + gong + low brass for the heavy fact, warm low brass for the turn. No piano, no string melody.
out: audio/score.wav (music, stereo), audio/sfx.wav (room, projector, relays, lamp, rings, building ticks), audio/hits.json"""
import json, os, math
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, 'timeline.json')))
SR, B = 48000, TL['beat']
T = TL['t']; DUR = TL['dur'] + 1.0
N = int(DUR * SR)
rng = np.random.default_rng(20261102)
mus = np.zeros((N, 2)); verb = np.zeros((N, 2)); fx = np.zeros((N, 2))

mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)
tt = lambda d: np.arange(int(d * SR)) / SR
def lp(x, fc, o=2): return sosfilt(butter(o, min(fc, SR / 2 - 100) / (SR / 2), output='sos'), x, axis=0)
def hp(x, fc, o=2): return sosfilt(butter(o, fc / (SR / 2), 'highpass', output='sos'), x, axis=0)
def bp(x, f0, f1, o=2): return sosfilt(butter(o, [f0 / (SR / 2), min(f1, SR / 2 - 200) / (SR / 2)], 'bandpass', output='sos'), x, axis=0)
def env(n, a, r, hold=None):
    e = np.ones(n); na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)[:n]
    if nr < n: e[-nr:] *= np.linspace(1, 0, nr)
    return e

def put(buf, sig, t, g=1.0, pan=0.0, send=0.0):
    i = int(round(t * SR))
    if i >= N or i + len(sig) <= 0: return
    j0 = max(0, -i); s = sig[j0:max(j0, min(len(sig), N - i))] * g; i = max(i, 0)
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    buf[i:i + len(s), 0] += s * l * 1.414; buf[i:i + len(s), 1] += s * r * 1.414
    if send: verb[i:i + len(s), 0] += s * l * send; verb[i:i + len(s), 1] += s * r * send

# ------------------------------------------------------------------ instruments
def marimba(m, d=.7):
    t = tt(d); f = mtof(m)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 8) + .32 * np.sin(2 * np.pi * 3.9 * f * t) * np.exp(-t * 26) + .08 * np.sin(2 * np.pi * 9.2 * f * t) * np.exp(-t * 60)
    return s * env(len(t), .002, .05) * .5
def glass(m, d=2.2):
    t = tt(d); f = mtof(m)
    s = sum(a * np.sin(2 * np.pi * f * k * t + ph) * np.exp(-t * dc) for k, a, dc, ph in [(1, 1, 2.6, 0), (2.76, .45, 5.5, .3), (5.4, .22, 9, .7), (8.93, .09, 15, 1.1)])
    return s * env(len(t), .001, .3) * .35
def glock(m, d=2.5):
    t = tt(d); f = mtof(m)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 1.8) + .35 * np.sin(2 * np.pi * 2.71 * f * t) * np.exp(-t * 4) + .15 * np.sin(2 * np.pi * 5.1 * f * t) * np.exp(-t * 8)
    return s * env(len(t), .001, .3) * .4
def tbell(m, d=5.0):
    t = tt(d); f = mtof(m)
    s = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * dc) for k, a, dc in [(.5, .35, .9), (1, 1, 1.1), (2.0, .5, 1.5), (3.0, .35, 2.2), (4.2, .25, 3.0), (5.4, .15, 4.0)])
    nz = hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 60) * .15
    return (s * .3 + nz) * env(len(t), .001, .5)
def bvib(ms, d, a=.6, r=1.2, g=1.0):          # bowed vibraphone: pure tones that swell, a slow shimmer
    t = tt(d + r); s = np.zeros(len(t))
    for i, m in enumerate(ms):
        f = mtof(m); s += np.sin(2 * np.pi * f * t + i) * (1 + .18 * np.sin(2 * np.pi * (4.6 + .3 * i) * t)) + .12 * np.sin(2 * np.pi * 4 * f * t)
    e = np.minimum(1, t / a) * np.where(t > d, np.maximum(0, 1 - (t - d) / r), 1)
    return s * e * .16 * g / max(1, len(ms) ** .5)
def bowed(m, d, a=.25, r=.6, bright=.5, vib=.004):   # contrabass / cello: additive saw, filtered, slow bow
    t = tt(d + r); f = mtof(m) * (1 + vib * np.sin(2 * np.pi * 5.2 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum(np.sin(k * ph) / k * math.exp(-k * (1 - bright) * .5) for k in range(1, 14))
    e = np.minimum(1, t / a) * np.where(t > d, np.maximum(0, 1 - (t - d) / r), 1)
    return lp(s, 2600) * e * .22
def brass(ms, d, a=.09, r=.5, g=1.0):
    t = tt(d + r); out = np.zeros(len(t))
    e = np.minimum(1, t / a) * np.where(t > d, np.maximum(0, 1 - (t - d) / r), 1)
    br = .55 + .45 * np.exp(-t * 2.5)                  # bright on the attack, mellow on the hold
    for i, m in enumerate(ms):
        f = mtof(m) * (1 + .002 * np.sin(2 * np.pi * (4.8 + .2 * i) * t)); ph = 2 * np.pi * np.cumsum(f) / SR + i
        out += sum(np.sin(k * ph) * (br ** (k * .9)) / k for k in range(1, 16))
    return lp(out, 3200) * e * .14 * g / max(1, len(ms) ** .5)
def timpani(m, d=2.2):
    t = tt(d); f = mtof(m) * (1 + .03 * np.exp(-t * 10))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 1.6) + .4 * np.sin(1.5 * ph) * np.exp(-t * 3) + .25 * np.sin(1.99 * ph) * np.exp(-t * 4)
    nz = lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 35) * .5
    return (s + nz) * .6
def cassa(d=1.6):
    t = tt(d); f = 52 * (1 + .5 * np.exp(-t * 18))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) + lp(rng.standard_normal(len(t)), 260) * np.exp(-t * 9) * .6
    return s * .8
def gong(d=6.0):
    t = tt(d); s = np.zeros(len(t))
    for f in rng.uniform(70, 1800, 26):
        s += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t * rng.uniform(.5, 2.0)) * (120 / f) ** .6
    return s * np.minimum(1, t / .12) * .05
def noise_sweep(d, f0, f1, g=1.0, shape=2.0):   # an air riser / ring breath: band-passed noise whose centre slides
    n = int(d * SR); x = rng.standard_normal(n); out = np.zeros(n); blk = 2400
    for i in range(0, n, blk):
        k = (i / n); fc = f0 * (f1 / f0) ** k
        out[i:i + blk] = bp(x[max(0, i - 4800):i + blk], fc * .7, fc * 1.4)[-len(x[i:i + blk]):]
    e = (np.arange(n) / n) ** shape
    return out * e * g

# ------------------------------------------------------------------ harmony: one chord per bar (2 s)
CH = {'Am': [45, 57, 60, 64], 'F': [41, 57, 60, 65], 'C': [36, 55, 60, 64], 'G': [43, 55, 59, 62], 'Dm': [38, 57, 62, 65], 'E': [40, 56, 59, 64]}
PROG = {2: 'Am', 3: 'F', 4: 'C', 5: 'G', 6: 'Am', 7: 'F', 8: 'C', 9: 'E',          # 4–20 s
        10: 'Dm', 11: 'Am', 12: 'F', 13: 'G', 14: 'Am', 15: 'F', 16: 'Am'}         # 20–34 s
def chord(t): return CH[PROG.get(int(t // 2), 'Am')]

hits = {}
def hit(name, t): hits[name] = round(t, 4)

# 0 · the first window: one glass note
put(mus, glass(79, 2.6), 0.0, .9, -.1, .5); hit('first', 0.0)
for q in (B, 2 * B): put(mus, glass(79, 1.6), q, .5, -.1, .4)          # the first window calls on the beat
# 0.5–3.5 · the facade catches: notes on a 32nd grid, sparse → dense, A minor pentatonic
pent = [57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81]
k = 0
for q in np.arange(.75, T['cascade'] - .02, B / 4):
    dens = ((q - .5) / (T['cascade'] - .5)) ** 1.2
    if rng.random() < .15 + .85 * dens:
        m = pent[int(rng.integers(3, len(pent)))]
        put(mus, (glass if k % 2 else marimba)(m, 1.2), q, .28 + .32 * dens, rng.uniform(-.6, .6), .35); k += 1
# 3.5 · it has caught: the floor arrives with a bowed chord
put(mus, bowed(33, 4.0, a=.08, r=1.5, bright=.6), T['cascade'], .9, 0, .2)
put(mus, bowed(45, 4.0, a=.12, r=1.5), T['cascade'], .55, -.3, .2)
put(mus, bvib([57, 60, 64, 69], 3.6, a=.05, r=1.6), T['cascade'], 1.0, .2, .5)
put(mus, glock(81), T['cascade'], .5, .3, .4); hit('cascade', T['cascade'])

# 4–34 · bass floor and held light, one chord per bar
for bar in range(2, 17):
    t0 = bar * 2.0
    if t0 < T['cascade'] + 3.5 and bar == 2: continue
    c = chord(t0); stop = T['lightsup']
    d = min(2.0, stop - t0)
    if d <= 0: break
    put(mus, bowed(c[0] - 12 if c[0] > 40 else c[0], d, a=.2, r=.5), t0, .75, 0, .15)
    put(mus, bowed(c[0], d, a=.25, r=.5), t0, .38, -.35, .15)
    put(mus, bvib(c[1:], d, a=.5, r=.8), t0, .55, .25, .5)

# 4.5–14.5 · the pulse: marimba 8ths over the chord (a router's beacon, slowed down); 14.5–17 16ths
def pulse(t0, t1, step, g):
    i = 0
    for q in np.arange(t0, t1 - 1e-6, step):
        c = chord(q); pat = [c[1] + 12, c[2] + 12, c[3] + 12, c[2] + 12]
        acc = 1.0 if i % (int(B / step) * 2) == 0 else .72
        put(mus, marimba(pat[i % 4], .5), q, g * acc, (-.3, .3)[i % 2], .2); i += 1
pulse(T['crane'], T['readout2'], B / 2, .42)
pulse(T['readout2'], T['here'] - .5, B / 4, .34)
pulse(T['boom'], T['spread'], B / 2, .36)
hit('crane', T['crane'])
put(mus, glass(88, 1.6), T['pin'], .45, .4, .4); hit('pin', T['pin'])
# counters: a rising run that lands
def run(t0, t1, g=.32):
    sc = [57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76]
    qs = np.arange(t0, t1 - 1e-6, B / 4)
    for i, q in enumerate(qs): put(mus, marimba(sc[int(i / len(qs) * len(sc))] + 12, .4), q, g * (.5 + .5 * i / len(qs)), .1, .2)
    put(mus, glock(81, 2.4), t1, .62, .2, .45); put(mus, glock(88, 2.4), t1, .3, -.2, .45)
run(T['readout1'] + .5, T['count1']); hit('count1', T['count1'])
run(T['readout2'] + .5, T['count2']); hit('count2', T['count2'])
# 17.5 · 「我在这儿」: the music holds its breath, one window calls
put(mus, glass(93, 3.5), T['here'], .8, -.15, .7); put(mus, glock(86, 3.0), T['here'], .4, .15, .6); hit('here', T['here'])
hit('boom', T['boom'])
# 20.5 · out through the wall: a low sigh under each ring that leaves (one every 2 beats)
for k in range(5):
    q = T['spill'] + k * 1.0
    put(mus, bowed(38 - (k % 2) * 2, .9, a=.05, r=.4, bright=.7), q, .35, 0, .1)
hit('spill', T['spill'])
# 25.0, 26.0 · next door, and the next: glass + soft low brass
put(mus, glass(84, 2.4), T['n1'], .7, -.3, .5); put(mus, brass([41, 48, 53], 1.0, a=.06, r=.6), T['n1'], .55, -.2, .3); hit('n1', T['n1'])
put(mus, glass(88, 2.4), T['n2'], .7, .3, .5); put(mus, brass([43, 50, 55], 1.0, a=.06, r=.6), T['n2'], .6, .2, .3); hit('n2', T['n2'])
# 28–30 · everything switches on outward: an air riser, a timpani roll that swells, mallets in 16ths
put(mus, noise_sweep(T['all'] - T['spread'], 400, 5200, .5, 2.2), T['spread'], 1.0, 0, .3)
for i, q in enumerate(np.arange(T['spread'], T['all'] - 1e-6, B / 4)):
    k = i / ((T['all'] - T['spread']) / (B / 4))
    put(mus, timpani(45, .4), q, .12 + .35 * k ** 2, (-.2, .2)[i % 2], .1)
    c = chord(q); put(mus, marimba([c[1], c[2], c[3]][i % 3] + 12 + 12 * (k > .5), .4), q, .25 + .2 * k, (.3, -.3)[i % 2], .25)
hit('spread', T['spread'])
# 30.0 · the heaviest fact: timpani, gran cassa, gong, low brass in A minor
put(mus, timpani(33, 3.0), T['all'], 1.25, 0, .3); put(mus, timpani(45, 2.5), T['all'], .6, .1, .3)
put(mus, cassa(), T['all'], 1.25, 0, .3); put(mus, gong(6.5), T['all'], 1.0, 0, .5)
put(mus, brass([33, 45, 52, 57, 60, 64], 2.6, a=.03, r=1.0), T['all'], 1.25, 0, .35)
put(mus, bvib([57, 64, 69, 72], 3.4, a=.3, r=.3), T['all'], .9, .2, .6)
hit('all', T['all'])
# 33.5 · the lights come up: everything stops (handled by the stop envelope below)
hit('lightsup', T['lightsup'])
# 36.0 · the lamp strikes: the turn, warm low brass + bowed vibraphone in C major
put(mus, brass([36, 43, 48, 52, 55], 4.0, a=.12, r=1.8, g=1.0), T['lamp'], .8, 0, .45)
put(mus, bowed(24, 9.5, a=.3, r=1.6, bright=.6), T['lamp'], .8, 0, .2)
put(mus, bvib([64, 67, 72, 76], 8.0, a=.8, r=2.0), T['lamp'], 1.0, .2, .6)
put(mus, timpani(36, 2.6), T['lamp'], .65, 0, .3); put(mus, cassa(), T['lamp'], .5, 0, .3)
hit('lamp', T['lamp'])
# 36.5–45 · the estate twinkling: sparse glass notes in C major pentatonic, on 16ths
cpent = [72, 74, 76, 79, 81, 84, 86, 88, 91]
for q in np.arange(T['lamp'] + .5, 45.0, B / 4):
    dens = .22 if q < T['glow'] else .3 * (1 - (q - 40) / 6) if q > 40 else .3
    if rng.random() < dens:
        put(mus, glass(cpent[int(rng.integers(0, len(cpent)))], 1.8), q, .22, rng.uniform(-.8, .8), .55)
put(mus, glock(84, 3.0), T['glow'], .55, -.2, .55); put(mus, glock(91, 3.0), T['glow'], .3, .2, .55)
put(mus, bvib([60, 65, 69, 72], 2.0, a=.6, r=1.0), T['glow'], .6, -.1, .5)   # F/C, then home
put(mus, bvib([60, 64, 67, 72], 4.0, a=.8, r=2.5), T['card'], .7, .1, .6)
put(mus, bowed(36, 4.0, a=.6, r=2.0), T['card'], .5, 0, .2)
put(mus, tbell(72, 5.5), T['card'], .55, 0, .5); hit('glow', T['glow']); hit('card', T['card'])

# the stop: 33.5–36.0 nothing plays but the room (release over 0.12 s)
st = np.ones(N); a, b = int(T['lightsup'] * SR), int(T['lamp'] * SR)
st[a:a + int(.12 * SR)] = np.linspace(1, 0, int(.12 * SR)); st[a + int(.12 * SR):b] = 0
mus *= st[:, None]; verb_st = st.copy()

# a hall on the music: stereo decaying noise IR
ir_t = tt(2.4); irs = []
for ch in range(2):
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 2.6); ir = lp(ir, 6000); ir[:int(.012 * SR)] = 0; irs.append(ir / np.sqrt((ir ** 2).sum()))
wet = np.stack([fftconvolve(verb[:, c] * verb_st, irs[c])[:N] for c in range(2)], 1)
mus = mus + .55 * wet
mus = hp(mus, 38, 2)
peak = np.abs(mus).max(); mus /= peak / .7

# ------------------------------------------------------------------ the room and the machine (sfx stem)
t = tt(DUR)
room = lp(rng.standard_normal((N, 2)), 900) * .006
fan_level = np.ones(N) * .9
fan_level[a:b] = np.linspace(.9, .35, b - a)                      # the projector winds down while it is off
k0 = int(T['lamp'] * SR); fan_level[k0:k0 + int(1.2 * SR)] = np.linspace(.35, 1.05, int(1.2 * SR)); fan_level[k0 + int(1.2 * SR):] = 1.0
hum = (np.sin(2 * np.pi * 100 * t) * .5 + np.sin(2 * np.pi * 200 * t) * .25 + np.sin(2 * np.pi * 300 * t) * .1) * .004
air = bp(rng.standard_normal(N), 300, 2400) * .012
fx += (room + (hum + air)[:, None] * fan_level[:, None])
def relay():
    tq = tt(.09); s = hp(rng.standard_normal(len(tq)), 1500) * np.exp(-tq * 120) + np.sin(2 * np.pi * 180 * tq) * np.exp(-tq * 60) * .6
    return s * .5
def lamp():
    tq = tt(1.2); zap = bp(rng.standard_normal(len(tq)), 2000, 9000) * np.exp(-tq * 18) * (1 + np.sign(np.sin(2 * np.pi * 37 * tq))) * .3
    thump = np.sin(2 * np.pi * 60 * tq * (1 + .4 * np.exp(-tq * 20))) * np.exp(-tq * 7) * .8
    return zap + thump
put(fx, relay(), T['lightsup'], .9, -.2); put(fx, relay(), T['lightsup'] + .07, .5, .2)
put(fx, relay(), T['lamp'] - .25, .9, .2)
put(fx, lamp(), T['lamp'], 1.0, 0)
for fl in (.055 * 2, .055 * 4):                                    # the flicker re-strikes
    put(fx, bp(rng.standard_normal(int(.05 * SR)), 3000, 9000) * np.exp(-tt(.05) * 60) * .25, T['lamp'] + fl, 1.0, 0)
# rings leaving the slabs: a soft breath each (pick from 20.5, every 1.0 s; the neighbours from n1+.3 / n2+.3)
def breath(): return noise_sweep(.9, 2400, 500, .35, .4) * np.exp(-tt(.9) * 2.5)
for k in range(6): put(fx, breath(), T['spill'] + k * 1.0, .9, -.2)
for k in range(3): put(fx, breath(), T['n1'] + .3 + k * 1.0, .5, -.5); put(fx, breath(), T['n2'] + .3 + k * 1.0, .45, .5)
# one soft tick per building as it switches on (same order and times as the picture: distance / 118 m/s + jitter)
M = json.load(open(os.path.join(ROOT, 'data', 'A', 'model.json'))); ST = json.load(open(os.path.join(ROOT, 'data', 'A', 'stats.json')))
cen = {}
for bi, h, rings in M['p']:
    r = np.array(rings[0]); s = cen.setdefault(bi, [0, 0, 0]); s[0] += r[:, 0].sum(); s[1] += r[:, 1].sum(); s[2] += len(r)
pc = np.array(cen[ST['pick']['i']][:2]) / cen[ST['pick']['i']][2]
fr = lambda x: x - math.floor(x)
ticks = []
for bi, s in cen.items():
    if bi in (ST['pick']['i'], 32, 34) or M['b'][bi][1] < 1: continue
    d = np.hypot(*(np.array(s[:2]) / s[2] - pc)) * 1000
    tb = T["spread"] + d / 128 + fr(math.sin(bi * 91.7 + 17.3) * 43758.5453) * .25     # = studio.js hash(bi) in aData.z
    if tb < T['lightsup']: ticks.append((tb, M['b'][bi][2]))
for tb, n in ticks:
    tq = tt(.05); s = np.sin(2 * np.pi * rng.uniform(3200, 5200) * tq) * np.exp(-tq * 140)
    put(fx, s, tb, .05 + .05 * min(1, math.sqrt(n) / 20), rng.uniform(-.7, .7))
print(f'{len(ticks)} building ticks, {ticks and min(x[0] for x in ticks):.2f}–{ticks and max(x[0] for x in ticks):.2f} s')

os.makedirs(os.path.join(ROOT, 'audio'), exist_ok=True)
sf.write(os.path.join(ROOT, 'audio', 'score.wav'), mus.astype(np.float32), SR)
sf.write(os.path.join(ROOT, 'audio', 'sfx.wav'), fx.astype(np.float32), SR)
json.dump(hits, open(os.path.join(ROOT, 'audio', 'hits.json'), 'w'), indent=1)
print('score', len(mus) / SR, 's; hits', hits)
