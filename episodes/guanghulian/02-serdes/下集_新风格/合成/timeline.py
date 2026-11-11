# 时间轴：按 14 句原稿配音的实际时长排（口播一字不改），算出每句的起点、字幕分段、换机位的时刻、光带的流动和鼓点。
# 画面（comp.py）和配乐（score.py）都读这一份，声音和画面用同一组时间。
import json, os, wave, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
SC = {x['id']: x for x in json.load(open(os.path.join(HERE, '..', '..', '抖音版_上下集', '配音', 'script_x.json'))) if x['id'].startswith('y')}
IDS = [f'y{i}' for i in range(1, 15)]
BIT = 0.7; BEAT = 0.5                                   # 120 BPM；光带流动时每个八分音符（0.25 秒）过一位

def rd(k):
    w = wave.open(os.path.join(HERE, 'in', 'voice', k + '.wav')); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32768; return x, w.getframerate()

def pauses(x, sr):
    """一句配音里的停顿（> 0.1 秒）：字幕分段的切点往最近的停顿上靠"""
    hop = sr // 100; e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)]); thr = max(0.012, np.percentile(e, 95) * 0.06)
    q = e < thr; out = []; i = 0
    while i < len(q):
        if q[i]:
            j = i
            while j < len(q) and q[j]: j += 1
            if j - i >= 10 and i > 5 and j < len(q) - 5: out.append(((i + j) / 2 / 100, (j - i) / 100))
            i = j
        else: i += 1
    return out

def build():
    dur = {}; ps = {}
    for k in IDS: x, sr = rd(k); dur[k] = len(x) / sr; ps[k] = pauses(x, sr)
    gap = {k: 0.30 for k in IDS}; gap['y8'] = 0.45; gap['y11'] = 0.45; gap['y12'] = 0.40; gap['y13'] = 0.35
    vs = {'y1': 0.12, 'y2': 2.52, 'y3': 6.55}
    for a, b in zip(IDS[2:], IDS[3:]): vs[b] = round((vs[a] + dur[a] + gap[a]) * FPS) / FPS
    b0 = {k: vs[k] - 0.12 for k in IDS}; b0['y1'] = 0.0; b0['y2'] = 2.4; b0['y3'] = 6.4
    end = round((vs['y14'] + dur['y14'] + 1.4) * FPS) / FPS
    subs = []
    for k in IDS:
        segs = SC[k]['sub']; wts = [len(s) + 1.5 for s in segs]; tot = sum(wts); t = 0.0; cuts = []
        for w_ in wts[:-1]:
            t += w_ / tot * dur[k]; c = min(ps[k], key=lambda p: abs(p[0] - t), default=None)
            cuts.append(c[0] if c and abs(c[0] - t) < 0.6 else t)
        ed = [0.0] + cuts + [dur[k]]
        for i, s in enumerate(segs): subs.append(dict(id=k, n=i, text=s, t0=round(vs[k] + ed[i], 3), t1=round(vs[k] + ed[i + 1] + (0.12 if i == len(segs) - 1 else 0), 3)))
    sub0 = lambda k, n: next(s['t0'] for s in subs if s['id'] == k and s['n'] == n)
    T = dict(A=0.0, B=2.4, side=6.4, count=b0['y6'], close=b0['y9'], rx=sub0('y10', 1) - 0.1, wide=b0['y11'], arev=b0['y12'], card=b0['y13'], close2=b0['y14'], end=end)
    return dict(dur=dur, vs=vs, b0=b0, subs=subs, T=T, end=end)

# ---------- 比特串（一整条，240 位一圈）----------
BITS = [1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0] * 4
def scr(n, seed):
    r = np.random.default_rng(seed); out = []
    while len(out) < n:
        b = int(r.integers(0, 2)); L = int(r.choice([1, 1, 1, 2, 2, 3]))
        if out and out[-1] == b: b = 1 - b
        out += [b] * L
    return out[:n]
# 同一位置上先到的在高位：120–239 = 和 3D 光带一样的普通数据；116–119 过渡；76–115 = 一长串 1（y7）；0–75 = 打乱后的数据
SEQ_LONG = scr(76, 5) + [1] * 40 + [0, 1, 0, 0] + BITS
SEQ_SCR = scr(76, 5) + scr(40, 9) + [0, 1, 0, 0] + BITS
N = 240; PERIOD = N * BIT

def ease(p, kind):
    p = min(1.0, max(0.0, p))
    return p if kind == 'lin' else 1 - (1 - p) ** 2 if kind == 'out' else p * p if kind == 'in' else p * p * (3 - 2 * p)

def phase_fn(TL):
    """光带的相位 φ(t)（mm，比特串沿 +y 走了多远）。分段：接 B 段末尾 → 减速到慢慢滑（数 4 还是 5）→ 流动（听鼓点）→ 慢下来数五拍 → 冲到一长串 1 → 打乱后继续流 → 越来越快。
       每段写 (起, 止, 起始速度, 结束速度)，速度线性变化，位置连续；慢的时候也不完全停，画面一直是活的。"""
    b0, vs, T = TL['b0'], TL['vs'], TL['T']; v = BIT / 0.25                      # 2.8 mm/s = 每秒 4 位
    ta = g8(b0['y5'] + 0.5); c1 = 0.26; c2 = 0.2
    seg = [(6.4, 7.6, 10.08, c1), (7.6, b0['y5'], c1, c1), (b0['y5'], ta, c1, v)]
    def end_phi(sg, p0=40.32):
        for a, b, va, vb in sg: p0 += (va + vb) / 2 * (b - a)
        return p0
    # 第二次慢下来：连续五个 1 那一段的中心停在 count 机位的画面中间（y ≈ 13.9）
    target = 10.75 + 21 * 3; pa = end_phi(seg); tb = ta + (target - (v + c2) / 2 * 0.5 - pa) / v
    seg += [(ta, tb, v, v), (tb, tb + 0.5, v, c2), (tb + 0.5, b0['y7'], c2, c2)]
    # y7：冲到一长串 1（第 96 位在 y ≈ 13.8）
    p7 = end_phi(seg); vb_ = (114.6 - p7) / 0.7 * 2 - c2; seg += [(b0['y7'], b0['y7'] + 0.35, c2, vb_ * 0.5 + c2 * 0.5 + (114.6 - p7) / 0.7 * 0), ]
    seg.pop(); vm = ((114.6 - p7) - c2 * 0.7) / 0.35 + c2                          # 三角形速度：0.35 秒加速到 vm，再 0.35 秒减回来
    seg += [(b0['y7'], b0['y7'] + 0.35, c2, vm), (b0['y7'] + 0.35, b0['y7'] + 0.7, vm, c2), (b0['y7'] + 0.7, b0['y8'] + 0.55, c2, c2)]
    tc = g8(b0['y8'] + 0.95); seg += [(b0['y8'] + 0.55, tc, c2, v), (tc, T['close'], v, v)]
    starts = []; p = 40.32
    for a, b, va, vb in seg: starts.append(p); p += (va + vb) / 2 * (b - a)
    pc = p; marks = dict(count_park=tb + 0.5, flow1=(ta, tb), flow2=(tc, T['close']))
    # 之后：屏幕上的流速不变（信号在线上的速度没变），一位越来越短 → 每秒过去的位数翻倍
    dt = 1 / 300; ts = np.arange(T['close'], TL['end'] + 0.1, dt); ph = np.zeros(len(ts)); ph[0] = pc
    for i in range(1, len(ts)): ph[i] = ph[i - 1] + scr_speed(ts[i], TL) / bit_scale(ts[i], TL) * dt
    def f(t):
        if t <= 6.4: return 40.32 - 10.08 * (6.4 - t)
        if t >= T['close']: return float(np.interp(t, ts, ph))
        for (a, b, va, vb), p0 in zip(seg, starts):
            if a <= t <= b: u = t - a; return p0 + va * u + 0.5 * (vb - va) / (b - a) * u * u
        return pc
    return f, marks

def g8(t): return round(t / 0.25) * 0.25                 # 靠到八分音符的格子上
def bit_scale(t, TL):
    """一位在线上的长度倍数：y9 三级台阶 1 → 1/2 → 1/4；到整块板时回到 1/2（太密就成一条线了）"""
    v9 = TL['vs']['y9']; s = 1.0
    for t0, a, b in ((v9 + 1.15, 1.0, 0.5), (v9 + 2.35, 0.5, 0.25)):
        if t >= t0: s = a + (b - a) * ease((t - t0) / 0.3, 'io')
    if t >= TL['T']['wide'] - 0.15: s = 0.25 + 0.25 * ease((t - TL['T']['wide'] + 0.15) / 0.3, 'io')
    return s
def scr_speed(t, TL):
    return 2.8 + 2.2 * ease((t - TL['T']['close']) / 0.6, 'io')

def hits(TL, phase, yls):
    """鼓点：光带流动时，每个跳变经过「听的位置」的时刻。y7（一长串 1）没有跳变，自然没有鼓点。
       yls = 三个流动段各自「听的位置」（mm）；自动微调（不到半位）让鼓点落在八分音符的格子上。返回 (时刻表, 调好的位置)"""
    T = TL['T']; (a1, b1), (a2, b2) = TL['marks']['flow1'], TL['marks']['flow2']
    wins = [(a1 + 0.1, T['count'] - 0.2, SEQ_LONG), (T['count'] + 0.2, b1 + 0.2, SEQ_LONG), (a2 + 0.02, T['close'] - 0.25, SEQ_SCR)]
    def scan(a, b, seq, yl):
        out = []; dt = 1 / 600; t = a; c0 = (yl - phase(t)) / BIT
        while t < b:
            t += dt; c1 = (yl - phase(t)) / BIT
            if np.floor(c1) < np.floor(c0):
                k = int(np.floor(c0)) % N
                if seq[k] != seq[(k - 1) % N]: out.append(round(t, 3))
            c0 = c1
        return out
    allh = []; yl2 = []
    for (a, b, seq), yl in zip(wins, yls):
        h = scan(a + 0.3, b, seq, yl)
        if h:
            d = (0.25 - h[0] % 0.25) % 0.25 * (BIT / 0.25)
            if d > BIT / 2: d -= BIT
            yl += d
        yl2.append(round(yl, 3)); allh += scan(a, b, seq, yl)
    return allh, yl2

def full():
    TL = build(); ph, marks = phase_fn(TL); TL['marks'] = marks; return TL, ph

if __name__ == '__main__':
    TL, ph = full()
    for k in IDS: print(k, 'voice', round(TL['vs'][k], 2), '→', round(TL['vs'][k] + TL['dur'][k], 2), '|', ' / '.join(f"{s['text']}@{s['t0']:.2f}" for s in TL['subs'] if s['id'] == k))
    print({k: round(v, 2) for k, v in TL['T'].items()}); print('marks', TL['marks'])
