"""T5 合成：同一份时间表（叠加层、声音、转场都从这里取时间）。
常数不另抄一份：消息流速、位长、偏移时刻、第 1 拍流速表、到达时刻，都用正则从 Blender 脚本源码里读出来
（t5_shot1.py / t5_shot23.py / t5_arrive.py）；屏幕锚点从 --anchors 写出的 anchors.json 读。
全片时间 T（秒）= 帧号 (n-1)/30，n = 1..645。"""
import re, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30; N_FRAMES = 645; W, H = 540, 960
SEGS = {'shot1': (1, 195), 'shot23': (196, 570), 'arrive': (571, 645)}     # 全片帧号范围（含）
OFF = {k: v[0] - 1 for k, v in SEGS.items()}                                # 脚本内帧号 = 全片帧号 - OFF
def seg_of(n): return next(k for k, (a, b) in SEGS.items() if a <= n <= b)
def T_of(seg, t_local): return OFF[seg] / FPS + t_local                    # 脚本内秒 → 全片秒
def src(name): return open(os.path.join(HERE, name), encoding='utf-8').read()

# ---------- 从脚本源码读常数 ----------
_s23 = src('t5_shot23.py'); _s1 = src('t5_shot1.py'); _ar = src('t5_arrive.py')
VSPEED = float(re.search(r'^VSPEED = ([\d.]+)', _s23, re.M).group(1))
BITLEN = float(re.search(r'^BITLEN = ([\d.]+)', _s23, re.M).group(1))
PATTERN = eval(re.search(r'^PATTERN = (\[[\d, ]+\])', _s23, re.M).group(1))
_m = re.search(r'def fiber_dx\(t\):\s*return ([\d.]+) \* \(sstep\(([\d.]+), ([\d.]+), t\) - sstep\(([\d.]+), ([\d.]+), t\)\)', _s23)
DX, OFF_A, OFF_B, BACK_A, BACK_B = [float(v) for v in _m.groups()]           # 脚本内秒：9.0 开始滑开，9.7 到位，10.3 开始滑回，11.1 回正
RATE = eval(re.search(r'^RATE = (\[.*\])', _s1, re.M).group(1))              # 第 1 拍：(秒, 位/秒)
HEAD_T = float(re.search(r'^HEAD_T = ([\d.]+)', _ar, re.M).group(1))        # 结尾：消息头到达 B 的脚本内秒
T_ARR = HEAD_T + 0.05
BIT_P = BITLEN / VSPEED                                                      # 第 2、3 拍一位的时长（秒）

def sstep(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0); return u * u * (3 - 2 * u)
def fiber_dx(t): return DX * (sstep(OFF_A, OFF_B, t) - sstep(BACK_A, BACK_B, t))
def coupling(dx): return max(0.08, math.exp(-(dx / 1.3) ** 2))

# ---------- 第 1 拍：消息位时刻（积分流速，每过一整位一声） ----------
def _hermite_s(keys, t):   # 同 t5_s1_scene.hermite_s（端点单边差分）
    n = len(keys); t = max(keys[0][0], min(keys[-1][0], t))
    def tan(i):
        if i == 0: return (keys[1][1] - keys[0][1]) / (keys[1][0] - keys[0][0])
        if i == n - 1: return (keys[-1][1] - keys[-2][1]) / (keys[-1][0] - keys[-2][0])
        return (keys[i + 1][1] - keys[i - 1][1]) / (keys[i + 1][0] - keys[i - 1][0])
    i = max(k for k in range(n - 1) if keys[k][0] <= t); (t0, p0), (t1, p1) = keys[i], keys[i + 1]; h = t1 - t0; s = (t - t0) / h
    return (2*s**3 - 3*s**2 + 1)*p0 + (s**3 - 2*s**2 + s)*h*tan(i) + (-2*s**3 + 3*s**2)*p1 + (s**3 - s**2)*h*tan(i + 1)
def shot1_bits(dur=6.5):
    """[(全片秒, 该位亮=1/暗=0)]。与脚本一样每 0.25 s 一步累计位数（脚本里的 msg_offset）。"""
    out = []; acc = 0.0; tt = 0.0; k_prev = 0
    while tt <= dur + 1e-6:
        r = _hermite_s(RATE, tt + 0.125); nxt = acc + r * 0.25
        while int(nxt) > k_prev:                                    # 本步内跨过整位
            k_prev += 1; frac = (k_prev - acc) / (nxt - acc); out.append((tt + 0.25 * frac, PATTERN[(k_prev - 1) % 8]))
        acc = nxt; tt += 0.25
    return [(t, b) for t, b in out if t <= dur]

# ---------- 第 2、3 拍的位（电极「嗡」/ 光的明暗） ----------
ELEC_WIN = (0.5, 7.6)       # 脚本内秒：相机看着电极和焊线的时间
LIGHT_WIN = (1.0, 11.1)     # 光带明暗同步的时间（到飞走为止）
def shot23_bits(win):
    k0 = 0; out = []
    t = win[0]
    while t < win[1]: out.append((T_of('shot23', t), PATTERN[k0 % 8])); t += BIT_P; k0 += 1
    return out
def light_gain_curve(t_full, bit_lo=0.38):
    """试听版光的长音增益：明暗跟消息一位一位走；偏移时跟耦合系数走。返回 0..1。"""
    tl = t_full - OFF['shot23'] / FPS
    if tl < LIGHT_WIN[0] or tl > LIGHT_WIN[1]: g = 1.0
    else:
        k = int((tl - LIGHT_WIN[0]) / BIT_P); g = 1.0 if PATTERN[k % 8] else bit_lo
    return g * (coupling(fiber_dx(tl)) if tl >= OFF_A - 0.2 else 1.0)

# ---------- 文字 / 标签 / 字幕（全片秒） ----------
TITLE = (0.2, 2.6)
CORNER = [((0.0, 6.5), '外壳透明化 · 结构为示意'), ((6.5, 19.0), '红外光，颜色为示意 · 结构为示意')]
LABEL_REQ = [   # 文字、锚点来源(段, 键)、请求窗口（全片秒）、最长显示秒数、可提前秒数（锚点不在屏幕上时会自动挑在屏幕上的那一段）
    ('GPU A', 'shot1', 'gpu_a', (2.8, 5.2), 2.4, 0.0, 'edge'),
    ('GPU B', 'shot1', 'gpu_b', (2.8, 5.2), 2.4, 0.0, 'ring'),
    ('激光：一直亮着', 'shot23', 'laser_label', (7.6, 9.6), 1.4, 0.5, None),
    ('电信号', 'shot23', 'electric_label', (8.8, 10.8), 1.6, 0.0, None),
    ('偏一点，就进不去', 'shot23', 'offset_label', (T_of('shot23', OFF_B) - 0.1, T_of('shot23', BACK_A) + 0.5), 2.0, 0.0, None),
]
SUBS = [(3.0, 5.6, '对面那台机器，在几十米外'), (9.0, 12.0, '光一直亮着，电让它照着电的样子一亮一暗'), (14.5, 17.5, '要对准一根比头发还细的芯，光才进得去')]
CELLS_T0 = 19.7; CELLS_STEP = 0.09           # 八格依次点亮
CHECK_T = T_of('arrive', T_ARR)               # ✓：消息头到达 B、标记亮起的那一刻
END_PANEL = (19.6, 21.5)
FADE = 0.15

def load_anchors(adir):
    d = {}
    for seg, name in (('shot1', 'shot1'), ('shot23', 'shot23'), ('arrive', 'arrive')):
        p = os.path.join(adir, name + '.json'); j = json.load(open(p)); d[seg] = {int(k): v for k, v in j['frames'].items()}
    return d
def anchor_at(A, seg, key, n):
    """全片帧 n 在 seg 里的锚点 (x, y, z) 或 None"""
    f = n - OFF[seg]; fr = A[seg].get(f)
    return None if fr is None else fr[key]
SAFE = (30, 120, 510, 880)    # 锚点在这个框里才算「看得见」
def on_screen(p): return p is not None and p[2] > 0 and SAFE[0] <= p[0] <= SAFE[2] and SAFE[1] <= p[1] <= SAFE[3]
def resolve_labels(A):
    """每个标签返回 dict(text, t0, t1, seg, key, mode)。start 取请求窗口里第一个看得见的帧（可提前），最长 dur。"""
    out = []
    for text, seg, key, (a, b), dur, early, mode in LABEL_REQ:
        n0 = max(1, int(round((a - early) * FPS)) + 1); n1 = int(round(b * FPS)) + 1
        vis = [n for n in range(n0, n1 + 1) if mode == 'edge' or on_screen(anchor_at(A, seg, key, n))]
        if not vis: out.append(dict(text=text, t0=None, t1=None, seg=seg, key=key, mode=mode, note='锚点始终不在屏幕上')); continue
        start = vis[0]; end = min(vis[-1], start + int(dur * FPS)); out.append(dict(text=text, t0=(start - 1) / FPS, t1=(end - 1) / FPS, seg=seg, key=key, mode=mode))
    return out
def alpha_win(t, t0, t1, fade=FADE):
    if t0 is None or t < t0 or t > t1: return 0.0
    return min(1.0, (t - t0) / fade, (t1 - t) / fade)

# ---------- 声音事件 ----------
def audio_events(A=None):
    ev = []
    for t, b in shot1_bits(): ev.append(dict(kind='tick1', t=t, b=b))
    for t, b in shot23_bits(ELEC_WIN): ev.append(dict(kind='hum', t=t, b=b))
    ev.append(dict(kind='light_on', t=T_of('shot23', 0.1)))
    ev.append(dict(kind='offset', t0=T_of('shot23', OFF_A), t1=T_of('shot23', OFF_B), t2=T_of('shot23', BACK_A), t3=T_of('shot23', BACK_B)))
    ev.append(dict(kind='whoosh', t=T_of('shot23', BACK_B), dur=OFF['arrive'] / FPS - T_of('shot23', BACK_B) + 0.15))
    for k in range(8): ev.append(dict(kind='ding', t=CELLS_T0 + k * CELLS_STEP, b=PATTERN[k]))
    ev.append(dict(kind='check', t=CHECK_T))
    ev.append(dict(kind='end', t=N_FRAMES / FPS))
    return ev

if __name__ == '__main__':
    print('VSPEED', VSPEED, 'BITLEN', BITLEN, 'BIT_P', round(BIT_P, 4), 'PATTERN', PATTERN)
    print('偏移 全片秒', [round(T_of('shot23', x), 2) for x in (OFF_A, OFF_B, BACK_A, BACK_B)], 'dx', DX)
    print('第1拍位数', len(shot1_bits()), '| ✓ 全片秒', round(CHECK_T, 2))
