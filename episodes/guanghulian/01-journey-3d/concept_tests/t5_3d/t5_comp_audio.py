#!/usr/bin/env python3
"""T5 临时声音（numpy 合成，不是配音）。用法：python3 t5_comp_audio.py <输出.wav>
所有事件时间来自 t5_comp_timeline.audio_events()（常数从 Blender 脚本源码读），这里不写画面时间常数。"""
import sys, os, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t5_comp_timeline as TL
SR = 44100
rng = np.random.default_rng(11)
def smooth(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def tt(L): return np.arange(int(L * SR)) / SR
def lp(x, a):
    n = int(min(len(x), 6 / max(a, 1e-3))); h = a * (1 - a) ** np.arange(max(n, 2)); return np.convolve(x, h)[:len(x)]
def tick(f, amp, tau):
    t = tt(tau * 7 + 0.02); e = np.exp(-t / tau)
    return amp * ((np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.01 * t)) * e * 0.6 + rng.standard_normal(len(t)) * np.exp(-t / 0.003) * 0.25)
def hum(f, amp, L=0.2):
    t = tt(L); s = sum(np.sin(2 * np.pi * f * k * t) / k for k in (1, 2, 3, 4))
    return amp * s * np.minimum(1, t / 0.012) * np.exp(-t / 0.09)
def ding(f, amp, tau=0.16):
    t = tt(tau * 7); e = np.exp(-t / tau) * np.minimum(1, t / 0.002)
    return amp * e * (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) + 0.12 * np.sin(2 * np.pi * f * 5.4 * t))

def main():
    out = sys.argv[1]; ev = TL.audio_events(); DUR = [e['t'] for e in ev if e['kind'] == 'end'][0]
    n = int((DUR + 0.8) * SR); buf = np.zeros(n); t = np.arange(n) / SR
    def add(t0, s):
        i = int(round(t0 * SR))
        if i < 0 or i >= n: return
        s = s[:n - i]; buf[i:i + len(s)] += s
    seg1_end = TL.SEGS['shot1'][1] / TL.FPS
    # 第 1 拍：低沉的空间长音（两个很低的音 + 慢颤，到第 2 拍交叉溶解时收掉）
    d1 = (np.sin(2 * np.pi * 55 * t) + 0.7 * np.sin(2 * np.pi * 82.4 * t + 0.5 * np.sin(2 * np.pi * 0.35 * t)) + 0.3 * np.sin(2 * np.pi * 110.3 * t)) * smooth(t / 0.7) * smooth((seg1_end + 0.5 - t) / 0.6)
    buf += 0.16 * d1
    # 光的长音：进芯片后一直在；明暗跟消息、偏移时跟耦合（只改音量，不拖尾），回正时音高上扬
    on = [e for e in ev if e['kind'] == 'light_on'][0]['t']; off = [e for e in ev if e['kind'] == 'offset'][0]
    wh = [e for e in ev if e['kind'] == 'whoosh'][0]
    g = np.array([TL.light_gain_curve(x) for x in t[::441]]); g = np.interp(t, t[::441], g); g = lp(g, 0.02) if False else g
    k = int(0.02 * SR); g = np.convolve(np.pad(g, (k, 0), mode='edge'), np.ones(k) / k, 'valid')[:n]    # 20 ms 平滑，位与位之间不爆音
    f0 = 392.0
    rise = smooth((t - off['t2']) / (off['t3'] - off['t2']))                  # 回正时音高上扬
    f = f0 * (1 + 0.12 * rise * (1 - smooth((t - off['t3'] - 0.5) / 0.6)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    pad = np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)
    env = smooth((t - on) / 0.4) * smooth((wh['t'] + 0.5 - t) / 0.5)
    bright = 1 + 0.5 * rise * (1 - smooth((t - off['t3'] - 0.5) / 0.6))
    buf += 0.12 * pad * g * env * bright
    for e in ev:
        K = e['kind']; T = e.get('t')
        if K == 'tick1': add(T, tick(1900 if e['b'] else 1350, (0.30 if e['b'] else 0.12), 0.018))
        elif K == 'hum': add(T, hum(110, 0.34 if e['b'] else 0.10))
        elif K == 'whoosh':
            L = e['dur']; tl = tt(L); kk = tl / L; fc = 400 * (6000 / 400) ** kk
            nz = rng.standard_normal(len(tl)); sig = lp(nz, 0.5) - lp(nz, 0.03)                           # 带通噪声
            lo = lp(nz, 0.02); mix = lp(nz, 0.12) * (1 - kk) + (lp(nz, 0.5) - lp(nz, 0.08)) * kk
            add(T, 0.5 * mix * np.sin(np.pi * kk) ** 1.5 + 0.10 * np.sin(2 * np.pi * np.cumsum(fc) / SR * 0.5) * np.sin(np.pi * kk) ** 2)
        elif K == 'ding': add(T, ding(1320 if e['b'] else 880, 0.26 if e['b'] else 0.12))
        elif K == 'check':
            for fq, a in ((523.25, 1.0), (659.25, 0.8), (783.99, 0.8), (1046.5, 0.55)): add(T, ding(fq, 0.14 * a, tau=0.55))
    # 简单空间感：两个稀疏回声
    for dly, gn in ((0.19, 0.22), (0.37, 0.12)): buf[int(dly * SR):] += gn * buf[:-int(dly * SR)].copy()
    buf = np.tanh(buf * 1.2) / 1.2
    buf *= 0.5 / max(np.abs(buf).max(), 1e-6)
    st = np.stack([buf, buf], 1); wf = wave.open(out, 'wb'); wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((np.clip(st, -1, 1) * 32767).astype('<i2').tobytes()); wf.close(); print('WAV', out, round(len(buf) / SR, 2), 's')
if __name__ == '__main__': main()
