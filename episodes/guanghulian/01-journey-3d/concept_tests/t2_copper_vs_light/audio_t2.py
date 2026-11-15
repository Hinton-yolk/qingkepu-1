#!/usr/bin/env python3
"""T2 概念测试的临时声音（代码合成，不是配音）。用法：python3 audio_t2.py <输出.wav>
一组八拍的「嗒」，暗的那几拍轻。第一遍（0–4.5 秒）里随着条纹变虚，尾音越拖越长、越闷；
第二遍一直清脆。糊化的时间段和 t2.html 里条纹变虚的时间段对应（1.2–4.2 秒）。"""
import sys, wave
import numpy as np
SR, DUR, PASS, TBIT = 44100, 9.0, 4.5, 0.3
PATTERN = [1, 1, 0, 1, 0, 0, 1, 0]
DARK = 0.28
def smooth(x):
    x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def main():
    out = sys.argv[1]
    rng = np.random.default_rng(3)
    mixbuf = np.zeros(int(DUR * SR) + SR)
    n = 0
    while n * TBIT < DUR - 0.05:
        t0 = n * TBIT
        u = t0 % PASS if t0 < PASS else t0 - PASS
        m = float(smooth((t0 - 1.2) / 3.0)) if t0 < PASS else 0.0   # 糊化程度
        amp = (DARK + (1 - DARK) * PATTERN[n % 8]) * 0.55
        tau = 0.025 + 0.30 * m
        f = 1500 - 1000 * m
        L = int(min(1.2, tau * 7) * SR)
        tt = np.arange(L) / SR
        env = np.exp(-tt / tau)
        tone = np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.01 * tt)
        click = rng.standard_normal(L) * np.exp(-tt / 0.004) * (1 - m) * 0.8
        s = amp * (0.7 * tone * env + click)
        if m > 0.05:   # 越糊越闷：简单一阶低通
            a = 0.5 - 0.45 * m; y = np.zeros_like(s); acc = 0.0
            for i, v in enumerate(s): acc += a * (v - acc); y[i] = acc
            s = y * (1.0 + 0.8 * m)
        i0 = int(t0 * SR); mixbuf[i0:i0 + L] += s
        n += 1
    mixbuf = mixbuf[:int(DUR * SR)]
    t = np.arange(len(mixbuf)) / SR
    mixbuf *= smooth((DUR - t) / 0.3)
    mixbuf = mixbuf / max(1.0, np.abs(mixbuf).max() / 0.8)
    with wave.open(out, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mixbuf * 32767).astype('<i2').tobytes())
main()
