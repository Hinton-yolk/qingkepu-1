"""Synthesized music bed for 'If your eyes could see Wi-Fi'.
100 BPM, D minor -> D major at the payoff. No samples, no noise whooshes.
out: audio/score.wav (stereo, 48k)
"""
import json, os
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
TL = json.load(open(os.path.join(ROOT, 'voice', 'timeline.json')))
DUR = TL['duration']
BEAT = 0.6
E8 = 0.3
N = int(DUR * SR) + SR * 4
rng = np.random.default_rng(20261102)

mus = np.zeros((N, 2))      # dry music bus
wet = np.zeros((N, 2))      # send to reverb


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(sig, t, gain=1.0, pan=0.0, send=0.25):
    i = int(round(t * SR))
    if i >= N:
        return
    sig = sig[: N - i]
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    mus[i:i + len(sig), 0] += sig * gain * l
    mus[i:i + len(sig), 1] += sig * gain * r
    wet[i:i + len(sig), 0] += sig * gain * l * send
    wet[i:i + len(sig), 1] += sig * gain * r * send


def tt(d):
    return np.arange(int(d * SR)) / SR


def pluck(m, d=1.2, bright=1.0):
    t = tt(d)
    f = mtof(m)
    s = np.zeros_like(t)
    for k, a in [(1, 1.0), (2, 0.45 * bright), (3, 0.22 * bright), (4, 0.12 * bright), (5, 0.06 * bright)]:
        s += a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (3.2 + 2.2 * k))
    att = np.minimum(1, t / 0.004)
    return s * att * 0.5


def bell(m, d=3.0):
    t = tt(d)
    f = mtof(m)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 1.4)
         + 0.5 * np.sin(2 * np.pi * f * 2.756 * t) * np.exp(-t * 2.6)
         + 0.25 * np.sin(2 * np.pi * f * 5.404 * t) * np.exp(-t * 4.5)
         + 0.12 * np.sin(2 * np.pi * f * 8.93 * t) * np.exp(-t * 7))
    return s * np.minimum(1, t / 0.002) * 0.4


def pad(ms, d, a=0.8, r=1.2, bright=0.5):
    t = tt(d + r)
    s = np.zeros_like(t)
    for m in ms:
        f = mtof(m)
        for det in (-0.07, 0.0, 0.06):
            ff = f * 2 ** (det / 12)
            ph = rng.uniform(0, 2 * np.pi)
            s += np.sin(2 * np.pi * ff * t + ph) + bright * 0.35 * np.sin(4 * np.pi * ff * t + ph) + bright * 0.12 * np.sin(6 * np.pi * ff * t)
    env = np.minimum(1, t / a) * np.where(t > d, np.exp(-(t - d) / (r / 3)), 1)
    return s * env / (len(ms) * 3) * 0.6


def kick(d=0.5, g=1.0):
    t = tt(d)
    f = 45 + 80 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7.5) * g


def sub(m, d):
    t = tt(d)
    return np.sin(2 * np.pi * mtof(m) * t) * np.minimum(1, t / 0.01) * np.exp(-t * 1.6) * 0.8


def tick(g=0.3):
    t = tt(0.05)
    return np.sin(2 * np.pi * 5200 * t) * np.exp(-t * 160) * g


def blip(m, g=0.3):
    t = tt(0.22)
    return (np.sin(2 * np.pi * mtof(m) * t) + 0.3 * np.sin(4 * np.pi * mtof(m) * t)) * np.exp(-t * 22) * g


def lowpass(x, fc):
    sos = butter(2, fc / (SR / 2), output='sos')
    return sosfilt(sos, x)


# ---------------------------------------------------------------- harmony
MINOR = [  # bar chords (pad voicing, bass)
    ([50, 53, 57, 64], 38),   # Dm(add9)
    ([46, 50, 53, 57], 34),   # Bbmaj7
    ([45, 48, 53, 57], 41),   # F/A
    ([48, 52, 55, 62], 36),   # Cadd9
]
MAJOR = [
    ([50, 54, 57, 64], 38),   # Dadd9
    ([47, 50, 55, 59], 43),   # G/B
    ([45, 50, 54, 59], 35),   # Bm7/A-ish
    ([45, 49, 52, 59], 33),   # A
]
SCALE_MIN = [62, 64, 65, 67, 69, 70, 72, 74, 76, 77, 79, 81]
SCALE_MAJ = [62, 64, 66, 67, 69, 71, 73, 74, 76, 78, 79, 81]


def chord_at(t, prog):
    return prog[int(np.floor(t / 2.4 + 1e-6)) % 4]


def arp(t0, t1, prog, g=0.22, every=E8, pattern=(0, 2, 1, 3, 2, 1), octave=12, bright=0.8, pan=0.25):
    t = t0
    i = 0
    while t < t1 - 1e-6:
        ch, _ = chord_at(t, prog)
        m = ch[pattern[i % len(pattern)] % len(ch)] + octave
        place(pluck(m, 0.9, bright), t, g * (1.0 if i % 2 == 0 else 0.75), pan if i % 2 else -pan, 0.35)
        t += every
        i += 1


def pads(t0, t1, prog, g=0.25, bright=0.5):
    t = t0
    while t < t1 - 1e-6:
        nb = min((np.floor(t / 2.4 + 1e-6) + 1) * 2.4 - t, t1 - t)
        if nb < 0.05:
            t += max(nb, 0.05)
            continue
        ch, _ = chord_at(t, prog)
        place(pad(ch, nb, a=0.5, r=1.0, bright=bright), t, g, 0, 0.5)
        t += nb


def bass(t0, t1, prog, g=0.5, every=BEAT * 2):
    t = t0
    while t < t1 - 1e-6:
        _, b = chord_at(t, prog)
        place(sub(b, every * 0.95), t, g, 0, 0.0)
        t += every


def kicks(t0, t1, every=BEAT, g=0.7):
    t = t0
    while t < t1 - 1e-6:
        place(kick(g=g), t, 1.0, 0, 0.05)
        t += every


def ticks(t0, t1, g=0.12):
    t = t0 + E8
    while t < t1 - 1e-6:
        place(tick(g), t, 1.0, 0.3, 0.1)
        t += BEAT


# ---------------------------------------------------------------- sections (seconds, on the beat grid) — from the voice layout
S = dict(TL['shots']); S['END'] = DUR

# S01 intro: low drone + shimmer
place(pad([38, 45], S['S02'], a=1.5, r=1.0, bright=0.2), 0.0, 0.30, 0, 0.6)
for k, t in enumerate(np.arange(1.2, S['S02'], BEAT * 2)):
    place(bell(81 + (k % 2) * 2, 2.0), t, 0.07, (-0.5 if k % 2 else 0.5), 0.8)

# S02-S03 explain: pluck arpeggio, light pads
arp(S['S02'], S['S04'], MINOR, g=0.16, bright=0.6)
pads(S['S02'], S['S04'], MINOR, g=0.16, bright=0.3)
bass(S['S03'], S['S04'], MINOR, g=0.25)

# S04 router: groove enters (half time)
arp(S['S04'], S['S05'], MINOR, g=0.15, bright=0.8)
pads(S['S04'], S['S05'], MINOR, g=0.17)
bass(S['S04'], S['S05'], MINOR, g=0.4)
kicks(S['S04'], S['S05'], every=BEAT * 2, g=0.55)
ticks(S['S04'] + 2.4, S['S05'], g=0.07)

# S05 building: full
arp(S['S05'], S['S06'], MINOR, g=0.18, every=E8, bright=1.0)
arp(S['S05'] + 2.4, S['S06'], MINOR, g=0.08, every=E8, pattern=(3, 1, 2, 0), octave=24, bright=0.5, pan=0.6)
pads(S['S05'], S['S06'], MINOR, g=0.24, bright=0.7)
bass(S['S05'], S['S06'], MINOR, g=0.5, every=BEAT)
kicks(S['S05'], S['S06'], every=BEAT, g=0.62)
ticks(S['S05'], S['S06'], g=0.09)

# S06 wall / body / metal: thinner groove, stops a beat before the bad news
arp(S['S06'], S['S09'] - 0.6, MINOR, g=0.13, every=E8, pattern=(0, 2, 3, 1), bright=0.7)
pads(S['S06'], S['S09'] - 0.6, MINOR, g=0.15)
bass(S['S06'], S['S09'] - 0.6, MINOR, g=0.38)
kicks(S['S06'], S['S09'] - 0.6, every=BEAT * 2, g=0.5)

# S09 silence (bad news): only a faint room tone
t = tt(S['S10'] - S['S09'])
place(lowpass(rng.standard_normal(len(t)), 300) * 0.02, S['S09'], 1.0, 0, 0)

# S10-S11 dark: drone with a minor-second rub, slow heartbeat sub, in-key swell to the cut before the hit
hit_t = S['S12']
place(pad([38, 45, 51], hit_t - 0.6 - S['S10'], a=2.0, r=0.15, bright=0.15), S['S10'], 0.3, 0, 0.5)
for t in np.arange(S['S10'], hit_t - 0.6, BEAT * 2):
    place(sub(38, 0.5), t, 0.5, 0, 0)
    place(sub(38, 0.4), t + 0.3, 0.25, 0, 0)
sw = hit_t - 0.6 - S['S11']
ts = tt(sw + 0.05)
swell = pad([50, 57, 62, 64, 69], sw, a=sw, r=0.05, bright=0.9) * (ts / sw) ** 1.5 * 3.0
place(swell, S['S11'], 0.5, 0, 0.6)
arp(S['S11'] + 0.6, hit_t - 0.6, [([50, 57, 62, 64], 38)] * 4, g=0.10, every=E8 / 2, pattern=(0, 1, 2, 3), octave=12, bright=1.0)

# S12 PAYOFF: the loudest hit, then D major warmth
place(pad([50, 54, 57, 62, 66, 69], 0.5, a=0.005, r=1.8, bright=1.0), hit_t, 1.1, 0, 0.9)
place(kick(0.9, 1.0), hit_t, 1.0, 0, 0.1)
place(sub(38, 2.5), hit_t, 0.9, 0, 0)
place(bell(74, 4.0), hit_t, 0.35, 0, 0.9)
place(bell(81, 4.0), hit_t + 0.01, 0.2, 0.3, 0.9)
pads(hit_t + 0.6, S['S14'], MAJOR, g=0.2, bright=0.4)
arp(hit_t + 2.4, S['S14'], MAJOR, g=0.12, every=BEAT, pattern=(0, 2, 3, 1), bright=0.5)
bass(hit_t + 2.4, S['S14'], MAJOR, g=0.35)
for t in np.arange(S['S13'], S['S14'], BEAT * 2):   # quiet-zone pulse
    place(kick(0.5, 0.35), t, 1.0, 0, 0.2)

# S14 the city: the second climax — full groove in D major, building to the last bar
arp(S['S14'], S['S15'], MAJOR, g=0.15, every=E8, pattern=(0, 2, 1, 3, 2, 1), bright=0.9)
arp(S['S14'] + 1.2, S['S15'], MAJOR, g=0.07, every=E8 / 2, pattern=(3, 1, 2, 0), octave=24, bright=0.5, pan=0.6)
pads(S['S14'], S['S15'], MAJOR, g=0.24, bright=0.8)
bass(S['S14'], S['S15'], MAJOR, g=0.45, every=BEAT)
kicks(S['S14'] + 0.6, S['S15'] - 0.6, every=BEAT, g=0.55)
ticks(S['S14'] + 0.6, S['S15'] - 0.6, g=0.08)

# S15 end: rising fifth motif and a long Dadd9
place(pad([50, 57, 62, 64, 69], DUR - S['S15'] - 0.8, a=0.6, r=1.6, bright=0.4), S['S15'], 0.24, 0, 0.6)
place(pluck(62, 1.6), S['S15'] + 0.6, 0.3, -0.2, 0.5)
place(pluck(69, 1.6), S['S15'] + 1.2, 0.3, 0.2, 0.5)
place(bell(74, 4.0), S['S15'] + 1.8, 0.2, 0, 0.8)

# ---------------------------------------------------------------- reverb + master bus
ir_t = tt(2.6)
ir = np.stack([rng.standard_normal(len(ir_t)), rng.standard_normal(len(ir_t))], 1) * np.exp(-ir_t * 2.6)[:, None]
ir[:, 0] = lowpass(ir[:, 0], 6000)
ir[:, 1] = lowpass(ir[:, 1], 6000)
ir /= np.sqrt((ir ** 2).sum(0))
rev = np.stack([fftconvolve(wet[:, c], ir[:, c])[:N] for c in range(2)], 1) * 0.55
out = mus + rev
out = out[: int(DUR * SR)]
# fade the very end
fe = int(1.2 * SR)
out[-fe:] *= np.linspace(1, 0, fe)[:, None]
out /= np.max(np.abs(out)) / 0.9
sf.write(os.path.join(ROOT, 'audio', 'score.wav'), out, SR)
json.dump({'sections': S, 'hit': hit_t, 'bpm': 100}, open(os.path.join(ROOT, 'audio', 'score_meta.json'), 'w'), indent=1)
print('score', out.shape[0] / SR, 's')
