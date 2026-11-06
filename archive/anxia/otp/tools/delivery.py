"""How a line is delivered: pace (chars per voiced second, trimmed), pitch level and range (Praat), the ending (last 30% vs the rest),
and how abruptly it stops. Impatient = fast, low range, falling clipped ending."""
import sys, numpy as np, parselmouth
def trim(s):
    i = s.to_intensity(); v = i.values[0]; t = i.xs(); on = t[v > v.max() - 30]; return on[0], on[-1]
for f, n in [(a.split(':')[0], int(a.split(':')[1])) for a in sys.argv[1:]]:
    s = parselmouth.Sound(f); t0, t1 = trim(s); dur = t1 - t0
    p = s.to_pitch_ac(pitch_floor=65, pitch_ceiling=300); hz = p.selected_array['frequency']; ts = p.xs(); ok = hz > 0
    h, tt = hz[ok], ts[ok]; cut = t0 + .7 * dur
    body, end = h[tt < cut], h[tt >= cut]
    st = lambda a, b: 12 * np.log2(a / b)
    inten = s.to_intensity(); iv = inten.values[0]; it = inten.xs(); last = iv[(it > t1 - .25) & (it <= t1)]
    print(f"{f.split('/')[-1]:18s} pace {n / dur:4.2f} 字/s  dur {dur:4.2f}s  f0 med {np.median(h):5.1f} Hz  range p10–p90 {st(np.percentile(h, 90), np.percentile(h, 10)):4.1f} st  ending {st(np.median(end), np.median(body)) if len(end) and len(body) else float('nan'):+5.1f} st  tail drop {iv.max() - last.mean():4.1f} dB")
