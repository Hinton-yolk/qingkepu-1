#!/usr/bin/env python3
"""T1 概念测试的临时声音（代码合成，不是配音）。用法：python3 audio_t1.py <A|B> <输出.wav>
光是一个不变的长音；电到电极顶端时响一下低的「嗡」；随后长音跟着出口的光一起变轻。
时间和图样的常数和 t1.html 里的保持一致。"""
import sys, wave
import numpy as np

V, TBIT, T_ENTER = 220.0, 0.4, 0.6
PATTERN = [1, 1, 0, 1, 0, 0, 1, 0]
W, X_EL = 540, 230 + 66 + 40
Y_EL_BOT, Y_EL_TOP, Y_MERGE = 640, 380, 330
TRACE_LEN = (W - X_EL) + (Y_EL_BOT - Y_EL_TOP)
DIM, T_OPEN, DUR, SR = 0.12, 3.9, 8.0, 44100

def smooth(x):
    x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)

def src(tau):
    k = np.maximum(tau, 0) / TBIT; i = np.floor(k).astype(int); f = (k - i) * TBIT
    pat = np.array(PATTERN); cur = pat[i % 8]; prev = np.where(i == 0, 0, pat[(i - 1) % 8])
    return np.where(tau < 0, 0.0, prev + (cur - prev) * smooth(f / 0.07))

def main():
    variant, out = sys.argv[1], sys.argv[2]
    t = np.arange(int(DUR * SR)) / SR
    e_top = src(t - T_ENTER - TRACE_LEN / V)                       # 电到电极顶端
    light = 1 - (1 - DIM) * src(t - T_ENTER - TRACE_LEN / V - (Y_EL_TOP - Y_MERGE) / V)   # 出口的光
    tone = (np.sin(2 * np.pi * 392 * t) + 0.45 * np.sin(2 * np.pi * 784 * t) + 0.2 * np.sin(2 * np.pi * 1176 * t))
    tone *= 0.16 * smooth(t / 0.9) * (0.12 + 0.88 * light)
    saw = sum(np.sin(2 * np.pi * 98 * n * t) / n for n in range(1, 9))
    buzz = 0.11 * saw * e_top
    mix = tone + buzz
    if variant == 'B':                                             # 盒子打开时一声很轻的上行音
        d = t - T_OPEN; env = np.where((d > 0) & (d < 0.6), np.sin(np.pi * np.clip(d / 0.6, 0, 1)) ** 2, 0)
        mix += 0.05 * env * np.sin(2 * np.pi * (588 + 300 * np.clip(d, 0, 0.6)) * t)
    mix *= smooth((DUR - t) / 0.3)
    mix = np.clip(mix, -0.95, 0.95)
    with wave.open(out, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype('<i2').tobytes())

main()
