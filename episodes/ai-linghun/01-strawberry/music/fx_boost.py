#!/usr/bin/env python3
"""把音效抬高几 dB，不需要配乐原文件（A1 的 wav 随上一个会话丢了，成片里只有混好的一条音轨）。
做法：音效是 sfx.py 用代码合成的，按同一份 cues.json 重新合成出来和原来逐样本相同；先在成片音轨里找到它的
对齐位置和混音时的增益 k（最小二乘），再在原音轨上叠加 (10^(dB/20) − 1) × k × 音效，最后整体响度回到 -14 LUFS
（和 sfx.py 同一个 loud()：增益 + 限幅，约 -1 dBTP）。音乐本身不动，只是整体响度回归时略降。

  python3 fx_boost.py <成片.mp4 或 .wav> <输出前缀> [--db 6] [--cues cues.json]   → <前缀>.wav
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sfx                                   # same sounds, same seeded noise (module-level rng), same levels
from prep import loud, PAUSE

SR = sfx.SR


def fx_stem(cues, N):
    """exactly what sfx.main() adds to the music (before loudness): same order, same pans, same pause gate"""
    fx = np.zeros((2, N)); prng = np.random.default_rng(3)
    for c in cues['cues']:
        x = sfx.SOUNDS[c['k']](**{k: v for k, v in c.items() if k not in ('k', 't', 'g', 'pan')}) * sfx.LEVEL[c['k']] * c.get('g', 1.0)
        pan = c.get('pan', float(prng.uniform(-0.15, 0.15))); L, R = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        i = int(round(c['t'] * SR)); n = min(len(x), N - i)
        if n > 0: fx[0, i:i + n] += x[:n] * L * 1.414; fx[1, i:i + n] += x[:n] * R * 1.414
    t = np.arange(N) / SR
    return fx * np.clip(np.maximum((PAUSE[0] - t) / 0.025, (t - PAUSE[1]) / 0.025), 0, 1)


def main():
    a = sys.argv[1:]; src, pre = a[0], a[1]
    db = float(a[a.index('--db') + 1]) if '--db' in a else 6.0
    cues = json.load(open(a[a.index('--cues') + 1] if '--cues' in a else os.path.join(HERE, 'cues.json')))
    if not src.endswith('.wav'):
        wav = pre + '.src.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_f32le', wav], check=True); src = wav
    up, sr = sf.read(src, always_2d=True); assert sr == SR, sr; up = up.T.astype(np.float64); N = up.shape[1]
    fx = fx_stem(cues, N)
    # 1) alignment: cross-correlate (mono, high-passed so the music matters less) over ±0.1 s
    from scipy.signal import correlate
    um, fm = sfx.hp(up.mean(0), 1500), sfx.hp(fx.mean(0), 1500)
    W = int(0.1 * SR); c = correlate(um, fm, mode='full', method='fft'); mid = len(fm) - 1
    lag = int(np.argmax(c[mid - W: mid + W + 1])) - W
    fx = np.roll(fx, lag, axis=1)
    if lag > 0: fx[:, :lag] = 0
    elif lag < 0: fx[:, lag:] = 0
    # 2) the gain the effects got in the mix (the music is uncorrelated with them, so least squares finds it)
    m = np.abs(fx).max(0) > 1e-4
    k = float(np.sum(up[:, m] * fx[:, m]) / np.sum(fx[:, m] ** 2))
    before = np.sum(up[:, m] ** 2); after = np.sum((up[:, m] - k * fx[:, m]) ** 2)
    print(f'alignment lag {lag} samples ({lag / SR * 1000:.1f} ms); effects gain in the mix k = {k:.3f} ({20 * np.log10(abs(k)):.1f} dB); '
          f'removing k·fx takes {10 * np.log10(before / after):.1f} dB off the audio under the effects (a large number = the stem matches)')
    # 3) add more of the same, then back to -14 LUFS
    y = up + (10 ** (db / 20) - 1) * k * fx
    y = loud(y, SR, -14.0, pre)
    import pyloudnorm as pyln
    mus = up - k * fx                                       # the music alone (estimate), to report the new balance
    def r(x, sel): return 10 * np.log10(np.mean(x[:, sel] ** 2) + 1e-12)
    hit = np.abs(fx).max(0) > 0.05 * np.abs(fx).max()
    print(f'+{db:g} dB effects -> {pre}.wav ; LUFS {pyln.Meter(SR).integrated_loudness(y.T):.1f} ; '
          f'effects vs music where effects sound: before {r(k * fx, hit) - r(mus, hit):+.1f} dB, after ≈ {r(k * fx, hit) + db - r(mus, hit):+.1f} dB')


if __name__ == '__main__':
    main()
