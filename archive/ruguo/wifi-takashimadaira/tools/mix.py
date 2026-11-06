"""voice (Fish 「科普」) + score + room/sfx -> audio/mix.wav at -14 LUFS, true peak <= -1.2 dBTP.
Voice compressed first, then balanced by RMS: the music sits ~10 dB under the voice while it speaks (ducked), fuller in the gaps.
Prints the checks: loudness, peak, voice-over-music while speaking (full band and phone band), the loudest music moments."""
import json, os
import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import butter, sosfilt, resample_poly

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
TL = json.load(open(os.path.join(ROOT, 'timeline.json')))
score, _ = sf.read(os.path.join(ROOT, 'audio', 'score.wav'))
fx, _ = sf.read(os.path.join(ROOT, 'audio', 'sfx.wav'))
voice, _ = sf.read(os.path.join(ROOT, 'voice', 'voice.wav'))
N = int(TL['dur'] * SR)
fit = lambda x: (np.pad(x, ((0, max(0, N - len(x))),) + ((0, 0),) * (x.ndim - 1)))[:N]
score, fx, voice = fit(score), fit(fx), fit(voice)
meter = pyln.Meter(SR)
sos = lambda kind, f, o=2: butter(o, f / (SR / 2), kind, output='sos')

# voice: de-boom, a little presence, a slow compressor (4:1 above the 85th percentile envelope)
v = sosfilt(sos('highpass', 85), voice)
v = v + .18 * sosfilt(butter(2, [2500 / (SR / 2), 6000 / (SR / 2)], 'bandpass', output='sos'), v)
e = np.sqrt(np.convolve(v ** 2, np.ones(int(.03 * SR)) / int(.03 * SR), 'same'))
th = np.percentile(e[e > 1e-4], 85)
v = v * np.where(e > th, (th / np.maximum(e, 1e-9)) ** .75, 1.0)
speaking = np.convolve(np.abs(voice) > .01, np.ones(int(.06 * SR)), 'same') > 0
v *= 10 ** ((-16 - meter.integrated_loudness(v[speaking])) / 20)

# duck the music under speech: attack 60 ms, release 400 ms, -6 dB
duck = np.zeros(N); y = 0.0; aa, ar = np.exp(-1 / (.06 * SR)), np.exp(-1 / (.40 * SR)); step = 64
for i in range(0, N, step):
    tg = 1.0 if speaking[i] else 0.0; c = aa if tg > y else ar
    y = tg + (y - tg) * c ** step; duck[i:i + step] = y
g_m = 1 - .5 * duck

def rms_db(x, m): return 10 * np.log10(np.mean(np.asarray(x)[m] ** 2) + 1e-12)
# set the music so that, while speaking, it sits 10 dB under the voice
m_s = score.mean(1) * g_m
gain = 10 ** ((rms_db(v, speaking) - 7 - rms_db(m_s, speaking)) / 20)   # 7 dB: the music must stay audible on a phone
score *= gain
fx *= 10 ** ((-34 - meter.integrated_loudness(fx)) / 20)          # the room: just there

mix = score * g_m[:, None] + fx + v[:, None]
mix *= 10 ** ((-14 - meter.integrated_loudness(mix)) / 20)
# true-peak limiter: 4x oversampled peak estimate, smooth gain reduction (5 ms attack, 120 ms release)
def tp(x): return np.abs(resample_poly(x, 4, 1, axis=0)).max()
ceil = 10 ** (-1.4 / 20)
for _ in range(4):
    over = np.abs(resample_poly(mix, 4, 1, axis=0)).reshape(-1, 4, 2).max(axis=(1, 2))[:N]
    need = np.minimum(1, ceil / np.maximum(over, 1e-9))
    gr = np.minimum.accumulate(np.r_[need[::-1]])[::-1] if False else need
    # smooth: release-limited envelope that never exceeds the needed gain
    g = np.ones(N); cur = 1.0; rel = np.exp(-1 / (.12 * SR)); att_n = int(.005 * SR)
    mins = np.minimum.reduceat(need, np.arange(0, N, 32)); gg = np.ones(len(mins))
    for i, m in enumerate(mins):
        cur = m if m < cur else 1 - (1 - cur) * rel ** 32; gg[i] = cur
    g = np.repeat(gg, 32)[:N]
    g = np.convolve(np.r_[np.ones(att_n), g], np.ones(att_n) / att_n, 'valid')[:N]
    g = np.minimum(g, need)
    mix *= g[:, None]
    L = meter.integrated_loudness(mix); mix *= 10 ** ((-14 - L) / 20)
    if tp(mix) <= 10 ** (-1.2 / 20): break
sf.write(os.path.join(ROOT, 'audio', 'mix.wav'), mix.astype(np.float32), SR, subtype='FLOAT')

L = meter.integrated_loudness(mix); TP = 20 * np.log10(tp(mix))
print(f'mix: {L:.2f} LUFS, true peak {TP:.2f} dBTP, {N / SR:.2f} s')
mus = score * g_m[:, None] + fx
print(f'while speaking: voice over music {rms_db(v, speaking) - rms_db(mus.mean(1), speaking):+.1f} dB (target +7)')
hpf = lambda x: sosfilt(sos('highpass', 300, 4), x)
print(f'phone band (>300 Hz) while speaking: voice over music {rms_db(hpf(v), speaking) - rms_db(hpf(mus.mean(1)), speaking):+.1f} dB')
w = int(.4 * SR); r = 10 * np.log10(np.convolve((mus ** 2).mean(1), np.ones(w) / w, 'same') + 1e-12)
order = np.argsort(r)[::-1]; picks = []
for i in order:
    if all(abs(i - j) > SR for j in picks): picks.append(i)
    if len(picks) == 4: break
print('loudest music moments (400 ms):', ', '.join(f'{i / SR:.2f}s {r[i] - r[picks[0]]:+.1f} dB' for i in picks))
T = TL['t']; a, b = int(T['lightsup'] * SR + .3 * SR), int(T['lamp'] * SR - .3 * SR)
print(f"the silence {T['lightsup']}–{T['lamp']} s: music {10 * np.log10(np.mean(mus[a:b] ** 2) + 1e-12) - np.median(r):+.1f} dB vs median program")
