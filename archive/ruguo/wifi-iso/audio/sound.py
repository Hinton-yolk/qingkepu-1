"""Sample sound: the approved Fish 「科普」 voice (first two lines) + a synthesized bed and SFX on the 120 BPM grid -> audio/mix.wav (-14 LUFS)."""
import os, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import butter, sosfilt
ROOT = os.path.dirname(os.path.abspath(__file__)); SR = 48000; DUR = 11.6; N = int(DUR * SR)
rng = np.random.default_rng(5)
tt = lambda d: np.arange(int(d * SR)) / SR
def bp(x, a, b): return sosfilt(butter(2, [a / (SR / 2), b / (SR / 2)], 'bandpass', output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f / (SR / 2), output='sos'), x)
mus = np.zeros((N, 2)); fx = np.zeros((N, 2))
def put(buf, s, t, g=1, pan=0):
    i = int(t * SR); s = s[:max(0, N - i)] * g; l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(s), 0] += s * l * 1.414; buf[i:i + len(s), 1] += s * r * 1.414
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
# the bed: a soft A-minor drone that opens when the scan passes, a filtered pulse on every beat (the router's beacon, slowed)
t = tt(DUR)
drone = sum(np.sin(2 * np.pi * mtof(m) * t + i) * a for i, (m, a) in enumerate([(45, .5), (52, .35), (57, .3), (60, .18), (64, .14)]))
drone *= np.clip((t - .5) / 1.2, 0, 1) * (1 + .15 * np.sin(2 * np.pi * .25 * t)) * .14
drone += np.sin(2 * np.pi * mtof(33) * t) * np.clip((t - 6) / .3, 0, 1) * .12          # floor under part two
mus += np.stack([drone, np.roll(drone, 240)], 1)
for k in range(3, int(DUR / .5)):
    q = k * .5; d = tt(.35); f = mtof(81 if k % 4 == 0 else 76)
    s = (np.sin(2 * np.pi * f * d) + .3 * np.sin(2 * np.pi * 2.76 * f * d)) * np.exp(-d * 14) * (.10 if q < 6 else .13)
    put(mus, s, q, 1, (-.4, .4)[k % 2])
# the scan: a rising air sweep across the room, hits on 0.5
d = tt(1.1); x = rng.standard_normal(len(d)); sw = np.zeros(len(d))
for i in range(0, len(d), 2400):
    fc = 300 * (6000 / 300) ** (i / len(d)); seg = x[max(0, i - 4800):i + 2400]; sw[i:i + 2400] = bp(seg, fc * .7, min(fc * 1.4, 20000))[-len(x[i:i + 2400]):]
put(fx, sw * np.sin(np.pi * d / 1.1) ** 2 * .5, .5, 1, 0)
put(fx, np.sin(2 * np.pi * 55 * tt(.6) * (1 + .5 * np.exp(-tt(.6) * 20))) * np.exp(-tt(.6) * 6) * .6, .5)
# target locks: two-tone blips; the rolling digits tick
def blip(): d = tt(.16); return (np.sin(2 * np.pi * 1760 * d) * (d < .06) + np.sin(2 * np.pi * 2637 * d) * (d >= .07)) * np.exp(-d * 18) * .35
for q in (1.5, 3.0, 4.0, 8.0, 10.0): put(fx, blip(), q, 1, .3)
for q0, n in ((1.7, 8), (8.1, 9), (9.2, 8), (10.0, 10)):
    for i in range(n): put(fx, bp(rng.standard_normal(int(.012 * SR)), 3000, 9000) * .25, q0 + i * .06, 1, -.2)
# part two arrives: a low thump + a glass note on 6.0
put(fx, np.sin(2 * np.pi * 48 * tt(1.2) * (1 + .6 * np.exp(-tt(1.2) * 18))) * np.exp(-tt(1.2) * 3.5) * .8, 6.0)
put(mus, (np.sin(2 * np.pi * mtof(88) * tt(2.5)) * np.exp(-tt(2.5) * 2.2) + .4 * np.sin(2 * np.pi * mtof(88) * 2.76 * tt(2.5)) * np.exp(-tt(2.5) * 5)) * .25, 6.0)
voice, sr = sf.read('/home/user/wifi-eyes-v3/voice/voice.wav'); voice = voice[:N]; voice = np.pad(voice, (0, N - len(voice)))
meter = pyln.Meter(SR)
voice *= 10 ** ((-16 - meter.integrated_loudness(voice)) / 20)
m = mus + fx; m *= 10 ** ((-24 - meter.integrated_loudness(m)) / 20)
mix = m + voice[:, None]
mix *= 10 ** ((-14 - meter.integrated_loudness(mix)) / 20)
mix = np.tanh(mix / .89) * .89
mix *= 10 ** ((-14 - meter.integrated_loudness(mix)) / 20)
sf.write(os.path.join(ROOT, 'mix.wav'), mix.astype(np.float32), SR)
print('mix', round(meter.integrated_loudness(mix), 2), 'LUFS, peak', round(20 * np.log10(np.abs(mix).max()), 2), 'dBFS')
