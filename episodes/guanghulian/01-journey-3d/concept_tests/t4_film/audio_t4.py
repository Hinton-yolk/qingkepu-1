#!/usr/bin/env python3
"""T4 临时声音（代码合成，不是配音）。用法：python3 audio_t4.py <events.json> <输出.wav>
所有声音的时间都来自 events.json（由 t4.html 的 window.t4Events() 导出）；这里不写画面时间常数。"""
import sys, json, wave
import numpy as np
SR = 44100
def smooth(x):
    x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def lp(x, a):                       # 一阶低通（卷积实现），a 越小越闷
    n = int(min(len(x), 6 / max(a, 1e-3)))
    h = a * (1 - a) ** np.arange(max(n, 2))
    return np.convolve(x, h)[:len(x)]
def tt(L): return np.arange(int(L * SR)) / SR
rng = np.random.default_rng(7)

def tick(f, amp, tau, click=0.6, smear=0.0, dur=None):
    L = dur or min(1.2, tau * 7 + 0.02); t = tt(L)
    env = np.exp(-t / tau)
    s = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t)) * env * 0.7
    s += rng.standard_normal(len(t)) * np.exp(-t / 0.004) * click * (1 - smear)
    if smear > 0.05: s = lp(s, 0.5 - 0.45 * smear) * (1 + 0.8 * smear)
    return s * amp
def bell(f, amp, tau, L=None):
    t = tt(L or tau * 6); e = np.exp(-t / tau) * np.minimum(1, t / 0.004)
    return amp * e * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t))
def sweep(f0, f1, dur, amp):
    t = tt(dur); k = t / dur; f = f0 * (f1 / f0) ** k
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.sin(np.pi * k) ** 2
    n = lp(rng.standard_normal(len(t)), 0.15) * 0.8
    return amp * env * (np.sin(ph) * 0.6 + n * 0.6)
def buzz(f, amp, tau, L):
    t = tt(L); saw = sum(np.sin(2 * np.pi * f * n * t) / n for n in range(1, 9))
    return amp * saw * np.exp(-t / tau) * np.minimum(1, t / 0.006)

def main():
    ev = json.load(open(sys.argv[1])); out = sys.argv[2]
    DUR = max(e['t'] for e in ev) + 1.1
    buf = np.zeros(int(DUR * SR) + 3 * SR)
    def add(t0, s):
        i = int(round(t0 * SR)); buf[i:i + len(s)] += s
    zaps = [e for e in ev if e['kind'] == 'zap']
    padOn = next(e['t'] for e in ev if e['kind'] == 'padOn'); padOff = next(e['t'] for e in ev if e['kind'] == 'padOff')
    firstD = min(e['t'] for e in ev if e.get('seg') == 'D' and e['kind'] == 'bit')
    t = np.arange(len(buf)) / SR
    # A：底下一层很轻的长音（到 B 开始前收掉）
    firstB = min(e['t'] for e in ev if e.get('seg') == 'B' and e['kind'] == 'bit')
    a_end = firstB - 0.5
    buf += 0.045 * (np.sin(2 * np.pi * 110 * t) + 0.6 * np.sin(2 * np.pi * 165 * t + 0.4 * np.sin(2 * np.pi * 0.5 * t))) * smooth(t / 0.8) * smooth((a_end - t) / 0.4)
    # C：光是一个不变的长音；电碰电极时音量下沉（不是全静），随暗段恢复
    duck = np.zeros_like(t)
    for z in zaps:
        g = smooth((t - z['t']) / z['rise']) - smooth((t - z['t'] - z['dur']) / z['rise'])
        duck = np.maximum(duck, np.clip(g, 0, 1))
    pad = (np.sin(2 * np.pi * 392 * t) + 0.45 * np.sin(2 * np.pi * 784 * t) + 0.2 * np.sin(2 * np.pi * 1176 * t))
    buf += 0.13 * pad * smooth((t - padOn) / 0.3) * smooth((padOff + 0.6 - t) / 0.5) * (1 - 0.8 * duck)
    # D / E：轻的和弦底
    end = max(e['t'] for e in ev)
    chordpad = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(131, 1), (196, 0.7), (262, 0.5), (330, 0.3)])
    buf += 0.035 * chordpad * smooth((t - firstD) / 0.8) * smooth((end + 0.9 - t) / 0.6)
    for e in ev:
        k, T = e['kind'], e['t']
        if k == 'glass':
            add(T, tick(2300 if not e.get('final') else 2300, 0.30 * e['amp'], 0.04 if not e.get('final') else 0.09, 0.5))
            if e.get('final'): add(T, bell(1150, 0.12, 0.5))
        elif k == 'whoosh':
            if e['dir'] == 'up': add(T, sweep(300, 2200, e['dur'], 0.20))
            else: add(T, sweep(1500, 250, e['dur'], 0.16))
        elif k == 'bit':
            lit = DARKAMP = 0.28 + 0.72 * e['b']
            if e['seg'] == 'B':
                s = e['smear']; add(T, tick(1500 - 1000 * s, 0.5 * lit, 0.025 + 0.30 * s, 0.8, s))
            else:
                add(T, tick(2100 if e['b'] else 1500, 0.42 * lit, 0.02, 0.8))
        elif k == 'panel':
            if e['seg'] == 'B':
                L = 0.9; tl = tt(L); env = np.sin(np.pi * tl / L) ** 2
                add(T, 0.2 * env * (np.sin(2 * np.pi * 110 * tl) + np.sin(2 * np.pi * 116.5 * tl) + 0.8 * np.sin(2 * np.pi * 155.6 * tl)) / 2.5)
            else: add(T, bell(659, 0.14, 0.25))
        elif k == 'cell':
            if e['seg'] == 'B':
                if e['wrong']: add(T, buzz(150, 0.05, 0.25, 0.5))
                else: add(T, tick(200, 0.10, 0.07, 0.2))
            else:
                f = [523, 587, 659, 784, 880, 1047, 1175, 1319][e['i']]
                add(T, bell(f, 0.07 * (0.35 + 0.65 * e['b']), 0.18))
        elif k == 'verdict':
            if not e['ok']:
                add(T, bell(220, 0.22, 0.35)); add(T + 0.18, bell(165, 0.22, 0.45))
            else:
                for f in (262, 330, 392, 523): add(T, bell(f, 0.10, 0.7, 2.0))
        elif k == 'zap':
            add(T, buzz(98, 0.07, 0.12, 0.4)); add(T, bell(196, 0.1, 0.2))
        elif k == 'cue': add(T, bell(880, 0.05, 0.12))
        elif k == 'shrink': add(T, sweep(900, 420, e['dur'], 0.07))
        elif k == 'chip':
            for f in (131, 262, 330, 392, 523): add(T, bell(f, 0.10, 0.9, 3.0))
    n = int(DUR * SR); m = buf[:n]
    tm = np.arange(n) / SR
    m = m * smooth((DUR - tm) / 0.15)
    m = m / max(1.0, np.abs(m).max() / 0.8)
    with wave.open(out, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((m * 32767).astype('<i2').tobytes())
main()
