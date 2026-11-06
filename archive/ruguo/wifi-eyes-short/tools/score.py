"""Synthesized score for the Douyin cut — a real arrangement, audible on a phone speaker.
100 BPM (8th = 0.3 s = 9 frames). D minor, lifting to D major at the FAST payoff.
Drums: kick with a click transient (phones cannot play 50 Hz), clap, 16th hats, open hats.
Bass: saw with harmonics + octave layer. Lead hook: a two-bar motif. Pads: sidechained to the kick.
Sections follow the shot plan in voice/timeline.json. No samples, no noise whooshes (risers are tonal).
out: audio/score.wav (stereo 48 k)"""
import json, os
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
TL = json.load(open(os.path.join(ROOT, 'voice', 'timeline.json')))
DUR = TL['duration']
S = dict(TL['shots']); S['END'] = DUR
BEAT, S16, BAR = 0.6, 0.15, 2.4
N = int(DUR * SR) + SR * 4
rng = np.random.default_rng(20261102)
bus = {k: np.zeros((N, 2)) for k in ('drums', 'bass', 'lead', 'pad', 'fx')}
wet = np.zeros((N, 2))
kick_times = []


def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR
def lp(x, fc, o=2): return sosfilt(butter(o, min(fc, SR / 2 - 100) / (SR / 2), output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc / (SR / 2), 'highpass', output='sos'), x)
def bp(x, f0, f1): return sosfilt(butter(2, [f0 / (SR / 2), f1 / (SR / 2)], 'bandpass', output='sos'), x)


def place(b, sig, t, g=1.0, pan=0.0, send=0.15):
    i = int(round(t * SR))
    if i >= N or t < 0: return
    sig = sig[:N - i] * g
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    bus[b][i:i + len(sig), 0] += sig * l; bus[b][i:i + len(sig), 1] += sig * r
    wet[i:i + len(sig), 0] += sig * l * send; wet[i:i + len(sig), 1] += sig * r * send


# ---------------------------------------------------------------- instruments
def kick(g=1.0):
    t = tt(0.45)
    f = 48 + 110 * np.exp(-t * 30)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    click = hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 400) * 0.5 + np.sin(2 * np.pi * 1600 * t) * np.exp(-t * 180) * 0.35
    return np.tanh(1.6 * (body + click)) * 0.9 * g


def clap(g=1.0):
    t = tt(0.35)
    n = rng.standard_normal(len(t))
    env = sum(np.exp(-np.maximum(0, t - d) * 90) * (t >= d) for d in (0, 0.009, 0.018)) + 0.6 * np.exp(-np.maximum(0, t - 0.027) * 14) * (t >= 0.027)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.5
    return (bp(n, 900, 4200) * env * 0.55 + tone) * g


def hat(open_=False, g=1.0):
    t = tt(0.25 if open_ else 0.06)
    return hp(rng.standard_normal(len(t)), 7000, 4) * np.exp(-t * (14 if open_ else 70)) * 0.35 * g


def crash(g=1.0):
    t = tt(2.2)
    return hp(rng.standard_normal(len(t)), 4500, 2) * np.exp(-t * 2.2) * 0.25 * g


def saw(m, d, cutoff=10, a=0.004, dec=3.0):
    t = tt(d)
    f = mtof(m)
    s = sum(np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * dec * (1 + k / cutoff)) for k in range(1, 14) if f * k < 9000)
    return s * np.minimum(1, t / a) * np.minimum(1, (d - t) / 0.02 + 1e-9).clip(0, 1)


def bass(m, d):           # saw bass + octave so a phone speaker can find it
    return (saw(m, d, cutoff=6, dec=2.2) * 0.7 + saw(m + 12, d, cutoff=4, dec=4) * 0.35) * 0.55


def lead(m, d):
    t = tt(d + 0.25)
    f = mtof(m) * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.15))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.5 * np.sin(3 * ph) / 3 * 2 + 0.25 * np.sin(5 * ph) / 5 * 2 + 0.35 * np.sin(2 * ph + 0.3)
    env = np.minimum(1, t / 0.006) * np.exp(-t * 2.2) * np.where(t > d, np.exp(-(t - d) / 0.06), 1)
    return s * env * 0.32


def bell(m, d=3.0):
    t = tt(d); f = mtof(m)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 1.4) + 0.5 * np.sin(2 * np.pi * f * 2.756 * t) * np.exp(-t * 2.6)
            + 0.25 * np.sin(2 * np.pi * f * 5.404 * t) * np.exp(-t * 4.5)) * np.minimum(1, t / 0.002) * 0.4


def pad(ms, d, a=0.4, r=0.8, bright=0.6):
    t = tt(d + r)
    s = np.zeros_like(t)
    for m in ms:
        for det in (-0.08, 0.0, 0.07):
            f = mtof(m) * 2 ** (det / 12); ph = rng.uniform(0, 2 * np.pi)
            s += np.sin(2 * np.pi * f * t + ph) + bright * 0.4 * np.sin(4 * np.pi * f * t + ph) + bright * 0.15 * np.sin(6 * np.pi * f * t + ph)
    env = np.minimum(1, t / a) * np.where(t > d, np.exp(-(t - d) / (r / 3)), 1)
    return s * env / (len(ms) * 3) * 0.55


def riser(m, d):          # tonal riser: a chord gliding up an octave, swelling
    t = tt(d)
    s = np.zeros_like(t)
    for k in (0, 7, 12, 19):
        f = mtof(m + k) * 2 ** (t / d)
        s += np.sin(2 * np.pi * np.cumsum(f) / SR)
    return s * (t / d) ** 2.2 * 0.18


def sub(m, d):
    t = tt(d)
    return np.sin(2 * np.pi * mtof(m) * t) * np.minimum(1, t / 0.01) * np.exp(-t * 1.2) * 0.8


# ---------------------------------------------------------------- harmony
MIN = [(50, [50, 53, 57, 64]), (46, [46, 50, 53, 57]), (41, [45, 48, 53, 57]), (48, [48, 52, 55, 62])]   # Dm Bb F C
MAJ = [(50, [50, 54, 57, 64]), (43, [47, 50, 55, 59]), (47, [47, 50, 54, 59]), (45, [45, 49, 52, 57])]   # D G Bm A
HOOK_MIN = [(0, 69, 2), (3, 74, 2), (6, 72, 2), (8, 69, 3), (11, 65, 2), (13, 67, 1), (14, 69, 2),
            (16, 70, 2), (19, 69, 2), (22, 67, 2), (24, 65, 3), (27, 64, 2), (30, 62, 2)]
HOOK_MAJ = [(0, 69, 2), (3, 74, 2), (6, 73, 2), (8, 69, 3), (11, 66, 2), (13, 67, 1), (14, 69, 2),
            (16, 71, 2), (19, 69, 2), (22, 67, 2), (24, 66, 3), (27, 64, 2), (30, 62, 2)]
BASSPAT = [(0, 0, 2), (3, 0, 1), (6, 12, 2), (8, 0, 2), (11, 0, 1), (14, 12, 2)]
PATS = {
    'half': dict(kick=[0, 10], clap=[8], hat=list(range(0, 16, 2)), ohat=[]),
    'four': dict(kick=[0, 4, 8, 12], clap=[4, 12], hat=list(range(16)), ohat=[2, 6, 10, 14]),
    'drive': dict(kick=[0, 7, 10], clap=[4, 12], hat=list(range(16)), ohat=[14]),
}


def bar_at(t, prog): return prog[int(np.floor(t / BAR + 1e-6)) % 4]


def drums(t0, t1, pat, g=1.0, hat_g=1.0, muffle=False):
    P = PATS[pat]
    b0 = np.ceil(t0 / BAR - 1e-6) * BAR if t0 % BAR > 1e-6 else t0
    t = np.floor(t0 / S16 + 1e-6) * S16
    while t < t1 - 1e-6:
        step = int(round((t % BAR) / S16)) % 16
        if step in P['kick']:
            k = kick(g); place('drums', lp(k, 900) if muffle else k, t, 1.0, 0, 0.05); kick_times.append(t)
        if step in P['clap'] and not muffle: place('drums', clap(g), t, 0.8, 0.1, 0.25)
        if step in P['hat'] and not muffle:
            acc = 1.0 if step % 4 == 2 else 0.6
            place('drums', hat(False, hat_g * acc), t, 1.0, 0.35, 0.05)
        if step in P['ohat'] and not muffle: place('drums', hat(True, hat_g * 0.7), t, 1.0, -0.3, 0.1)
        t += S16


def bassline(t0, t1, prog, g=1.0):
    t = np.floor(t0 / BAR + 1e-6) * BAR
    while t < t1 - 1e-6:
        root, _ = bar_at(t + 1e-3, prog)
        for st, off, ln in BASSPAT:
            tt0 = t + st * S16
            if t0 - 1e-6 <= tt0 < t1 - 1e-6:
                place('bass', bass(root - 12 + off, ln * S16 * 0.95), tt0, g, 0, 0.0)
        t += BAR


def hookline(t0, t1, hook, g=1.0, octave=0):
    t = np.floor(t0 / (2 * BAR) + 1e-6) * 2 * BAR
    while t < t1 - 1e-6:
        for st, m, ln in hook:
            tt0 = t + st * S16
            if t0 - 1e-6 <= tt0 < t1 - 1e-6:
                place('lead', lead(m + octave, ln * S16), tt0, g, 0.15 * np.sin(st), 0.35)
        t += 2 * BAR


def pads(t0, t1, prog, g=1.0, bright=0.6):
    t = t0
    while t < t1 - 1e-6:
        nb = min((np.floor(t / BAR + 1e-6) + 1) * BAR - t, t1 - t)
        if nb < 0.05: t += max(nb, 0.05); continue
        _, ch = bar_at(t + 1e-3, prog)
        place('pad', pad(ch, nb, bright=bright), t, g, 0, 0.5)
        t += nb


def arp(t0, t1, prog, g=1.0, every=S16, octave=12):
    t, i = t0, 0
    while t < t1 - 1e-6:
        _, ch = bar_at(t + 1e-3, prog)
        m = ch[[0, 2, 1, 3, 2, 1][i % 6]] + octave
        place('lead', lead(m, every * 0.9) * 0.5, t, g, 0.4 if i % 2 else -0.4, 0.3)
        t += every; i += 1


# ---------------------------------------------------------------- arrangement
sw = 2.4                                     # the vision switch: the drop
place('fx', bell(74, 3.0), 0.3, 0.5, 0, 0.6)
pads(0.0, sw, MIN, g=0.5, bright=0.2)
drums(0.0, sw, 'half', g=0.7, muffle=True)  # a muffled beat from frame 0
place('fx', riser(50, sw - 0.6), 0.6, 0.8, 0, 0.4)
place('drums', crash(0.9), sw, 1.0, 0, 0.3)

# groove A: the explanation (voice over it)
drums(sw, S['S04'], 'half', g=0.9, hat_g=0.8)
bassline(sw, S['S05'] - BAR / 2, MIN, g=0.85)
pads(sw, S['S05'], MIN, g=0.55)
arp(S['S03'], S['S04'], MIN, g=0.35, every=0.3)
# the router: hats go to 16ths
drums(S['S04'], S['S05'] - BAR / 2, 'drive', g=0.9, hat_g=0.9)
place('fx', riser(50, BAR / 2), S['S05'] - BAR / 2, 1.0, 0, 0.4)

# drop B: the building lights up
place('drums', crash(1.0), S['S05'], 1.0, 0, 0.3)
drums(S['S05'], S['S09'] - 0.3, 'four', g=0.85, hat_g=0.9)
bassline(S['S05'], S['S09'] - 0.3, MIN, g=0.85)
pads(S['S05'], S['S09'] - 0.3, MIN, g=0.6, bright=0.8)
hookline(S['S05'], S['S09'] - 0.3, HOOK_MIN, g=0.9)

# bad news: a dead stop, then only room tone
t = tt(S['S10'] - S['S09'])
place('fx', lp(rng.standard_normal(len(t)), 300) * 0.02, S['S09'], 1.0, 0, 0)

# dark build: half time, drone, then a snare roll and a tonal riser into silence
hit = S['S12']
pads(S['S10'], hit - 0.6, [(38, [38, 45, 51, 57])] * 4, g=0.55, bright=0.2)
drums(S['S10'] + 0.6, S['S11'], 'half', g=0.8, hat_g=0.5)
bassline(S['S10'] + 0.6, S['S11'], [(38, [])] * 4, g=0.6)
drums(S['S11'], hit - 0.6, 'half', g=0.9, hat_g=0.9)
roll_t0 = max(S['S11'], hit - 0.6 - BAR)
t = roll_t0; step = S16
while t < hit - 0.6 - 1e-6:
    place('drums', clap(0.35 + 0.65 * (t - roll_t0) / (hit - 0.6 - roll_t0)), t, 0.6, 0, 0.2)
    t += step
    if t > hit - 0.6 - BAR / 2: step = S16 / 2
place('fx', riser(50, hit - 0.6 - S['S11']), S['S11'], 1.1, 0, 0.4)

# PAYOFF: the loudest moment, then D major — big half-time
place('drums', kick(1.7), hit, 1.0, 0, 0.1)
place('drums', clap(1.4), hit, 1.0, 0, 0.5)
place('drums', crash(2.0), hit, 1.0, 0, 0.4)
place('bass', sub(38, 2.5), hit, 1.3, 0, 0)
place('pad', pad([50, 54, 57, 62, 66, 69], 0.6, a=0.004, r=1.6, bright=1.0), hit, 2.6, 0, 0.8)
place('fx', bell(74, 4.0), hit, 0.6, 0, 0.8)
drums(hit + BAR / 2, S['S13'], 'half', g=1.0, hat_g=0.9)
bassline(hit + BAR / 2, S['S13'], MAJ, g=0.9)
pads(hit + 0.6, S['S13'], MAJ, g=0.6, bright=0.8)
hookline(hit + BAR / 2, S['S13'], HOOK_MAJ, g=0.8, octave=-12)

# quiet zone: a breath — pads and a pulse
pads(S['S13'], S['S14'], MAJ, g=0.5, bright=0.4)
for t in np.arange(S['S13'], S['S14'] - 1e-6, BEAT):
    place('drums', lp(kick(0.6), 700), t, 1.0, 0, 0.1); kick_times.append(t)
place('fx', riser(50, S['S14'] - S['S13']), S['S13'], 0.9, 0, 0.4)

# the city: the final drop
place('drums', crash(1.2), S['S14'], 1.0, 0, 0.3)
drums(S['S14'], S['S15'], 'four', g=0.9, hat_g=1.0)
bassline(S['S14'], S['S15'], MAJ, g=1.0)
pads(S['S14'], S['S15'], MAJ, g=0.65, bright=0.9)
hookline(S['S14'], S['S15'], HOOK_MAJ, g=1.0)
arp(S['S14'] + BAR, S['S15'], MAJ, g=0.3, every=S16, octave=24)

# outro: the hook's first notes as bells, a long Dadd9
place('pad', pad([50, 57, 62, 64, 69], DUR - S['S15'] - 0.6, a=0.3, r=1.4, bright=0.5), S['S15'], 0.8, 0, 0.6)
for i, (st, m, _) in enumerate(HOOK_MAJ[:4]):
    place('fx', bell(m, 3.0), S['S15'] + 0.6 + st * S16 * 2, 0.35, 0.3 * (-1) ** i, 0.7)
place('drums', lp(kick(0.8), 900), S['S15'], 1.0, 0, 0.2)

# ---------------------------------------------------------------- sidechain, reverb, master
duck = np.ones(N)
tk = tt(0.3)
shape = 1 - 0.55 * np.exp(-tk / 0.09)
for k in kick_times:
    i = int(round(k * SR)); j = min(N, i + len(shape))
    duck[i:j] = np.minimum(duck[i:j], shape[:j - i])
for b in ('pad', 'bass', 'lead'):
    bus[b] *= duck[:, None] if b != 'lead' else (0.5 + 0.5 * duck)[:, None]
ir_t = tt(2.2)
ir = np.stack([rng.standard_normal(len(ir_t)), rng.standard_normal(len(ir_t))], 1) * np.exp(-ir_t * 3.0)[:, None]
ir = np.stack([lp(ir[:, c], 7000) for c in range(2)], 1); ir /= np.sqrt((ir ** 2).sum(0))
rev = np.stack([fftconvolve(wet[:, c], ir[:, c])[:N] for c in range(2)], 1) * 0.45
gains = {'drums': 1.0, 'bass': 0.8, 'lead': 0.75, 'pad': 0.6, 'fx': 0.8}
out = sum(bus[k] * g for k, g in gains.items()) + rev
out = out[:int(DUR * SR)]
fe = int(1.2 * SR); out[-fe:] *= np.linspace(1, 0, fe)[:, None]
out = np.tanh(out / np.max(np.abs(out)) * 1.3) / np.tanh(1.3) * 0.9      # gentle glue
sf.write(os.path.join(ROOT, 'audio', 'score.wav'), out, SR)
print('score', round(out.shape[0] / SR, 2), 's; hit at', hit)
