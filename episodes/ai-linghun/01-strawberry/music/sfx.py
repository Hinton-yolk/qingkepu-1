#!/usr/bin/env python3
"""音效 + 配乐混音。
音效全部用代码合成，时间点来自 cues.json（film/render.mjs --cues 从画面代码里导出，改时间轴后重导即可），
音高放在 F 大调里（A1 配乐是 F 大调）。音乐用 prep.py 对齐过的 wav。整片响度 -14 LUFS，限幅到约 -1 dBTP。

  python3 sfx.py <对齐后的音乐.wav> <输出.wav> [--cues cues.json] [--fx-db 0] [--music-db 0] [--stems]
本集终版（用户 2026-11-22「音乐有点大，盖住音效了」）：--music-db -6
"""
import json, os, sys
import numpy as np, soundfile as sf
from scipy.signal import butter, lfilter

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from prep import loud

SR = 48000
rs = np.random.default_rng(7)


# ---------- building blocks ----------
def T(d): return np.arange(int(d * SR)) / SR
def env(n, a, d): e = np.exp(-np.arange(n) / (d * SR)); k = max(1, int(a * SR)); e[:k] *= np.linspace(0, 1, k); return e
def bp(x, lo, hi, o=2): b, a = butter(o, [lo / (SR / 2), min(hi, SR / 2 - 200) / (SR / 2)], 'band'); return lfilter(b, a, x)
def lp(x, fc, o=2): b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def noise(n): return rs.standard_normal(n)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def norm(x, pk=1.0): return x * (pk / (np.max(np.abs(x)) + 1e-12))


# ---------- the sounds (each returns mono, peak about 1 before gain) ----------
def s_pop(f=500, **_):
    t = T(0.12); return norm(np.sin(2 * np.pi * np.cumsum(f * (1 + 1.6 * np.exp(-t * 55))) / SR) * np.exp(-t / 0.035))
def s_tick(f=2800, **_):
    n = int(0.02 * SR); t = T(0.02); return norm(0.7 * bp(noise(n), f * 0.7, f * 1.4) * env(n, 0.0004, 0.004) + 0.3 * np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006))
def s_chime(m=77, **_):     # glockenspiel-ish mallet: partials 1, 2.76, 5.4
    f = hz(m); t = T(1.4); x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) for r, a, d in ((1, 1, 0.55), (2.76, 0.3, 0.18), (5.4, 0.12, 0.07)))
    return norm(x * env(len(t), 0.002, 10))
def s_blip(m=84, **_):
    f = hz(m); t = T(0.11); ph = 2 * np.pi * np.cumsum(f * (1 + 0.04 * (1 - np.exp(-t * 40)))) / SR
    return norm((np.sin(ph) + 0.2 * np.sin(2 * ph)) * env(len(t), 0.003, 0.035))
def s_boop(**_):            # two falling notes: "wrong"
    out = []
    for f0, d in ((hz(65), 0.11), (hz(60), 0.17)):
        t = T(d); x = np.sign(np.sin(2 * np.pi * f0 * t)) * 0.5 + np.sin(2 * np.pi * f0 * t); out.append(lp(x, 1800) * env(len(t), 0.004, d * 0.6))
    return norm(np.concatenate(out))
def s_flip(**_):
    n = int(0.14 * SR); x = noise(n); y = np.concatenate([bp(x[i:i + 960], 800 + 4000 * i / n, 1600 + 6000 * i / n) for i in range(0, n, 960)])[:n]
    return norm(y * np.sin(np.pi * np.arange(n) / n) ** 2)
def s_scan(d=1.0, **_):     # a thin rising shimmer over the x-ray
    t = T(d); f = 1800 * (2.2 ** (t / d)); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 18 * t))
    x = x * 0.6 + 0.4 * bp(noise(len(t)), 3000, 9000); return norm(x * np.sin(np.pi * t / d) ** 1.5)
def s_whoosh(d=0.6, **_):
    n = int(d * SR); x = noise(n); y = np.concatenate([bp(x[i:i + 960], 300 + 1800 * i / n, 900 + 3600 * i / n) for i in range(0, n, 960)])[:n]
    return norm(y * np.sin(np.pi * np.arange(n) / n) ** 2)
def s_chop(**_):
    t = T(0.18); n = len(t)
    x = 0.8 * hp(noise(n), 2500) * np.exp(-t / 0.008) + 0.9 * np.sin(2 * np.pi * 95 * t) * np.exp(-t / 0.045) + 0.25 * np.sin(2 * np.pi * 3600 * t) * np.exp(-t / 0.05)
    return norm(x)
def s_thud(f=140, **_):
    t = T(0.14); return norm(lp(noise(len(t)), 1500) * np.exp(-t / 0.02) + 0.7 * np.sin(2 * np.pi * f * t) * np.exp(-t / 0.045))
def s_clack(f=1.0, **_):    # wooden block handed out
    t = T(0.09); n = len(t); return norm(bp(noise(n), 900 * f, 2600 * f) * np.exp(-t / 0.012) + 0.5 * np.sin(2 * np.pi * 760 * f * t) * np.exp(-t / 0.02))
def s_click(**_):
    a = s_tick(f=1500); gap = np.zeros(int(0.045 * SR)); return norm(np.concatenate([a, gap, 0.7 * s_tick(f=1200)]))
def s_coin(f=1.0, **_):
    t = T(0.35); x = sum(a * np.sin(2 * np.pi * fr * f * t) * np.exp(-t / d) for fr, a, d in ((2350, 1, 0.12), (3720, 0.6, 0.08), (6050, 0.3, 0.04)))
    return norm(x * env(len(t), 0.0008, 10))
def s_zip(d=1.5, **_):      # ratchet of the unrolling tape
    out = np.zeros(int(d * SR) + int(0.03 * SR)); t = 0.0; k = 0
    while t < d:
        f = 2200 + 1400 * t / d; tk = s_tick(f=f) * (0.6 + 0.4 * np.sin(np.pi * t / d)); i = int(t * SR); out[i:i + len(tk)] += tk[:len(out) - i]; t += 1 / 26; k += 1
    return norm(out)
def s_count(d=2.0, rate=10, up=0, **_):
    out = np.zeros(int(d * SR) + int(0.03 * SR)); t = 0.0
    while t < d:
        u = t / d; f = 2600 + (1400 * u if up else 300 * np.sin(7 * t)); tk = s_tick(f=f); i = int(t * SR); out[i:i + len(tk)] += tk[:len(out) - i]
        t += 1 / (rate * (1 + 1.2 * u) if up else rate)
    return norm(out * np.minimum(1, np.minimum(np.arange(len(out)) / (0.15 * SR), (len(out) - np.arange(len(out))) / (0.25 * SR))))

SOUNDS = dict(pop=s_pop, tick=s_tick, chime=s_chime, blip=s_blip, boop=s_boop, flip=s_flip, scan=s_scan, whoosh=s_whoosh,
              chop=s_chop, thud=s_thud, clack=s_clack, click=s_click, coin=s_coin, zip=s_zip, count=s_count)
LEVEL = dict(pop=0.30, tick=0.22, chime=0.26, blip=0.26, boop=0.12, flip=0.18, scan=0.30, whoosh=0.32, chop=0.36, thud=0.36,
             clack=0.21, click=0.25, coin=0.16, zip=0.14, count=0.36)     # base peak per kind (× the cue's g); tuned so each sits
# about -9 to +6 dB (peak) against the music's local RMS: transients audible, beds (whoosh / scan / count) faint but there


def main():
    a = sys.argv[1:]; music, out = a[0], a[1]
    cues = json.load(open(a[a.index('--cues') + 1] if '--cues' in a else os.path.join(HERE, 'cues.json')))
    fx_db = float(a[a.index('--fx-db') + 1]) if '--fx-db' in a else 0.0
    music_db = float(a[a.index('--music-db') + 1]) if '--music-db' in a else 0.0   # user 11-22: the music covered the effects -> run it with --music-db -6
    m, sr = sf.read(music, always_2d=True); assert sr == SR, sr; m = m.T
    N = m.shape[1]; fx = np.zeros((2, N)); prng = np.random.default_rng(3)
    for c in cues['cues']:
        x = SOUNDS[c['k']](**{k: v for k, v in c.items() if k not in ('k', 't', 'g', 'pan')}) * LEVEL[c['k']] * c.get('g', 1.0)
        pan = c.get('pan', float(prng.uniform(-0.15, 0.15))); L, R = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        i = int(round(c['t'] * SR)); n = min(len(x), N - i)
        if n > 0: fx[0, i:i + n] += x[:n] * L * 1.414; fx[1, i:i + n] += x[:n] * R * 1.414
    fx *= 10 ** (fx_db / 20)
    from prep import PAUSE                     # the half-beat stop before the reveal is silent for the effects too (review: a chime tail leaked in)
    t = np.arange(N) / SR; fx *= np.clip(np.maximum((PAUSE[0] - t) / 0.025, (t - PAUSE[1]) / 0.025), 0, 1)
    if '--stems' in a: sf.write(out.replace('.wav', '_fx.wav'), np.clip(fx, -1, 1).T, SR, subtype='PCM_24')
    mix = m * 10 ** (music_db / 20) + fx
    pre = out[:-4]; y = loud(mix, SR, -14.0, pre)
    print(f'{len(cues["cues"])} cues; fx peak {20 * np.log10(np.max(np.abs(fx)) + 1e-12):.1f} dBFS (before loudness); -> {out}')


if __name__ == '__main__':
    main()
