# 光互连 02 下集 · 新画面版 · 云端合成
# 输入（in/，不进仓库）：A/、B/（用户电脑渲的 r2 + Cycles 序列，从 A.mp4、B.mp4 解出的 PNG）、stills/（5 张背景 + 走线位置 json）、voice/（原稿 14 句配音）
# 画面顺序：3D 背景 → 光带、刻度、鼓点闪光（长在板面上，跟着透视和景深）→ 灰尘 → 调色 → 标签、五站条、字幕
# 用法：python3 comp.py frames <输出目录> [scale=0.5] [t0 t1]   渲 PNG 序列（多进程在 render.sh 里分段）
#       python3 comp.py sheet <输出.jpg> t1 t2 …                 指定时刻各出一帧拼成接触表
import os, sys, json, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import band as B, timeline as TLm

HERE = os.path.dirname(os.path.abspath(__file__)); IN = os.path.join(HERE, 'in'); FPS = 30; W0, H0 = 1080, 1920
S = 1.0
FONT_B = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'; FONT_R = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
GOLD = (255, 186, 60); WHITE = (246, 244, 236); RED = (240, 84, 70); BLUE = (150, 210, 255); DARK = (20, 20, 22)
TL, PH = TLm.full(); T = TL['T']; VS = TL['vs']; B0 = TL['b0']; SUBS = TL['subs']
def sub0(k, n): return next(s['t0'] for s in SUBS if s['id'] == k and s['n'] == n)
ease = TLm.ease
def ramp(t, a, b): return min(1.0, max(0.0, (t - a) / (b - a))) if b > a else float(t >= a)
def pulse(t, t0, up=0.25, hold=1e9, down=0.3): return ramp(t, t0, t0 + up) * (1 - ramp(t, t0 + up + hold, t0 + up + hold + down))
def win(t, a, b, up=0.25, down=0.25): return ramp(t, a, a + up) * (1 - ramp(t, b - down, b))

# ---------- 背景 ----------
VIEWS = {v: B.load_view(v) for v in B.VIEW_FILE}
_img = {}
def still(v):
    if v not in _img: _img[v] = cv2.imread(os.path.join(B.ST, B.VIEW_FILE[v] + '.png')).astype(np.float32) / 255
    return _img[v]
def seq(shot, i):
    k = (shot, i)
    if k not in _img:
        if len(_img) > 40:
            for kk in [x for x in _img if isinstance(x, tuple)][:20]: _img.pop(kk)
        _img[k] = cv2.imread(os.path.join(IN, shot, f'{i:05d}.png')).astype(np.float32) / 255
    return _img[k]
def out_size(): return int(round(W0 * S)), int(round(H0 * S))
def fit(img):
    w, h = out_size(); return img if img.shape[1] == w else cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)

SEGS = [('side', T['side'], T['count']), ('count', T['count'], T['close']), ('close', T['close'], T['rx']), ('rx', T['rx'], T['wide']), ('wide', T['wide'], T['arev']), ('close', T['close2'], T['end'])]
PUSH = {'side': 0.15, 'count': 0.14, 'close': 0.10, 'rx': 0.10, 'wide': 0.10}
def cam_affine(v, a, b, t):
    """静帧上的慢推 + 缓慢的横移和很小的滚转（静帧比成片大 10%；推到 1.1 倍以内是原生像素，再往上略有放大）。返回 静帧像素 → 成片像素 的 3×3"""
    u = (t - a) / max(1e-6, b - a); join = (v == 'side' and a == T['side'])
    z = 1.0 + PUSH[v] * u * u * (1.6 - 0.6 * u) if join else 1.03 + PUSH[v] * (0.25 * u + 0.75 * ease(u, 'io'))
    k = W0 / B.SW * z; ph = sum(map(ord, v)) % 7; mx = B.SW * (1 - 1 / z) / 2; my = B.SH * (1 - 1 / z) / 2          # 两边可以挪的余量（静帧像素）
    dx = min(34, mx * 0.9 + 3) * math.sin(0.5 * (t - a) + ph) * min(1, (t - a) / 3.0); dy = min(30, my * 0.9 + 3) * math.cos(0.5 * (t - a) + ph) * min(1, (t - a) / 3.0)   # 走一个扁圆：任何时刻都在动
    r = math.radians(0.5) * math.sin(0.33 * (t - a) + ph) * min(1, (t - a) / 3.0)
    c, s_ = math.cos(r) * k, math.sin(r) * k; cx, cy = B.SW / 2 + dx, B.SH / 2 + dy
    return np.array([[c, -s_, W0 / 2 - c * cx + s_ * cy], [s_, c, H0 / 2 - s_ * cx - c * cy], [0, 0, 1.0]])
def warp(img, A):
    w, h = out_size(); M = (np.diag([S, S, 1.0]) @ A)[:2]; return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_AREA if M[0, 0] < 0.8 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
def view_at(t):
    for v, a, b in SEGS:
        if a <= t < b or (b == T['end'] and t >= a): return v, a, b
    return None
def mblur(img, dx, dy):
    L = int(max(abs(dx), abs(dy)))
    if L < 3: return img
    return cv2.blur(img, (L, 1)) if abs(dx) >= abs(dy) else cv2.blur(img, (1, L))
WHIP = 0.30
WHIPS = [(T['count'], 'side', 'count', (1, 0)), (T['close'], 'count', 'close', (0, 1)), (T['rx'], 'close', 'rx', (0, -1)), (T['wide'], 'rx', 'wide', 'zoom')]
def whip_at(t):
    for tc, a, b, d in WHIPS:
        if tc - WHIP / 2 <= t < tc + WHIP / 2: return tc, a, b, d
    return None
def seg_of(v, tc, before):
    for vv, a, b in SEGS:
        if vv == v and ((before and abs(b - tc) < 1e-6) or (not before and abs(a - tc) < 1e-6)): return a, b
def normG(G): return G / np.linalg.norm(G)

def a_rev_frame(u):
    """y12：A 段倒放。信号飞回手机那段原速；之后手机上的字还原那段放慢（两帧之间线性混合，画面本来就几乎不动）"""
    D = T['card'] - T['arev']; t_fly = 26 / 30
    if u < t_fly: return 72 - u * 30, 0
    keys = [(t_fly, 46.0), (VS['y12'] - T['arev'] + 2.7, 34.0), (VS['y12'] - T['arev'] + 3.5, 24.0), (D, 6.0)]
    for (a, fa), (b, fb) in zip(keys, keys[1:]):
        if u <= b: return fa + (fb - fa) * (u - a) / (b - a), 1
    return 6.0, 1

def background(t):
    """返回 (画面, 板面→成片像素的单应 或 None, 机位名)"""
    w, h = out_size()
    if t < T['B']:
        im = seq('A', min(72, 1 + int(t * FPS + 1e-6))); z = 1.0 + 0.045 * ease(t / 1.3, 'out') * (1 - ease((t - 1.45) / 0.5, 'io'))     # 开头轻轻推近（第一帧就在动），信号飞出去时回到原位
        if z > 1.0005: M = np.array([[z * S, 0, (W0 / 2 - z * W0 / 2) * S], [0, z * S, (H0 * 0.42 - z * H0 * 0.42) * S]]); return cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT), None, 'A'
        return fit(im), None, 'A'
    if t < T['side']: return fit(seq('B', min(120, 1 + int((t - T['B']) * FPS + 1e-6)))), None, 'B'
    if T['arev'] <= t < T['card']:
        u = t - T['arev']; f, slow = a_rev_frame(u); i = int(math.floor(f)); fr = f - i
        im = seq('A', max(1, min(72, i))) if fr < 1e-3 or not slow else seq('A', i) * (1 - fr) + seq('A', min(72, i + 1)) * fr
        if not slow and fr > 1e-3: im = seq('A', max(1, min(72, int(round(f)))))
        z = 1.0 + 0.2 * ramp(u, 0.9, T['card'] - T['arev']) + 0.9 * ease((t - (T['card'] - 0.45)) / 0.45, 'in')      # 最后推进屏幕
        cx, cy = 0.50 * W0, (0.50 - 0.04 * ease((t - (T['card'] - 0.45)) / 0.45, 'in')) * H0
        M = np.array([[z * S, 0, (W0 / 2 - z * cx) * S], [0, z * S, (H0 / 2 - z * cy) * S]])
        return cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT), None, 'Arev'
    if T['card'] <= t < T['close2']: return np.zeros((h, w, 3), np.float32) + np.array(DARK[::-1], np.float32) / 255, None, 'card'
    wp = whip_at(t)
    if wp:
        tc, va, vb, d = wp; p = (t - (tc - WHIP / 2)) / WHIP; e = ease(p, 'io'); de = 6 * p * (1 - p) / (WHIP * FPS)
        a0, a1 = seg_of(va, tc, True); b0_, b1 = seg_of(vb, tc, False)
        Aa = cam_affine(va, a0, a1, t); Ab = cam_affine(vb, b0_, b1, t); ia, ib = warp(still(va), Aa), warp(still(vb), Ab)
        if d == 'zoom':                                                       # 甩镜拉远：新画面从封装入口那一点放大着进来，很快缩回原位
            px, py = B.proj(Ab @ VIEWS[vb]['H'], 0, 60.0); z = 1 + 2.6 * (1 - ease(p, 'out'))
            M = np.array([[z, 0, (px - z * px) * S], [0, z, (py - z * py) * S]]); nb = cv2.warpAffine(ib, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            if z > 1.05: nb = sum(cv2.warpAffine(nb, np.array([[q, 0, (px - q * px) * S], [0, q, (py - q * py) * S]]), (w, h), borderMode=cv2.BORDER_REFLECT) for q in (1.0, 1 + (z - 1) * 0.04, 1 + (z - 1) * 0.08, 1 + (z - 1) * 0.12)) / 4
            k = ramp(p, 0.0, 0.3); im = ia * (1 - k) + nb * k
            Z = np.array([[z, 0, px - z * px], [0, z, py - z * py], [0, 0, 1.0]]); G = (1 - k) * normG(Aa @ VIEWS[va]['H']) + k * normG(Z @ Ab @ VIEWS[vb]['H'])
            return im, G, vb if k > 0.5 else va
        dx, dy = d; im = np.empty_like(ia)
        if dx:
            o = int(round(e * w)); im[:, :w - o] = ia[:, o:]; im[:, w - o:] = ib[:, :o]; im = mblur(im, de * w * 0.7, 0)
        else:
            o = int(round(e * h)); sgn = dy
            if sgn > 0: im[:h - o] = ia[o:]; im[h - o:] = ib[:o]
            else: im[o:] = ia[:h - o]; im[:o] = ib[h - o:]
            im = mblur(im, 0, de * h * 0.7)
        G = (1 - e) * normG(Aa @ VIEWS[va]['H']) + e * normG(Ab @ VIEWS[vb]['H'])
        return im, G, vb if e > 0.5 else va
    v, a, b = view_at(t); A = cam_affine(v, a, b, t)
    if v == 'close' and a == T['close2']:                                     # y14：卡片往上滑走，下面露出 close 背景
        pass
    im = warp(still(v), A)
    if v == 'rx':                                                             # 收货端：信号进了封装，修信号的电路从信号进来的一侧一块块亮起，之后轻轻起伏
        lum = im @ np.array([0.114, 0.587, 0.299], np.float32); m = np.clip((lum - 0.62) / 0.25, 0, 1)[..., None]; hh, ww = lum.shape
        xs = np.linspace(0, 1, ww, dtype=np.float32)[None, :, None]; ton = a + 0.45 + (1 - xs) * 1.1; on = np.clip((t - ton) / 0.18, 0, 1)
        pul = 0.82 + 0.18 * np.sin(5.0 * t - 9.0 * xs)
        im = im * (1 - m * (1 - (0.22 + 0.78 * on) * pul))
        gl = cv2.GaussianBlur(cv2.resize((m * on * pul)[..., 0], (ww // 4, hh // 4)), (0, 0), 6 * S + 1); im = im + cv2.resize(gl, (ww, hh))[..., None] * np.array([1.0, 0.85, 0.55], np.float32) * 0.35
    return im, A @ VIEWS[v]['H'], v

# ---------- 文字 ----------
_spr = {}
def sprite(text, size, col=WHITE, bold=True, stroke=None, bg=None, pad=0):
    k = (text, size, col, bold, stroke, bg, pad, S)
    if k in _spr: return _spr[k]
    px = max(8, int(round(size * S))); f = ImageFont.truetype(FONT_B if bold else FONT_R, px, index=2)
    sw = int(round((stroke if stroke is not None else size * 0.09) * S)); bb = f.getbbox(text, stroke_width=sw); m = int(px * 0.5) + int(pad * S)
    w, h = bb[2] - bb[0] + 2 * m, bb[3] - bb[1] + 2 * m; im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if bg: d.rounded_rectangle([m - pad * S, m - pad * S * 0.55, w - m + pad * S, h - m + pad * S * 0.55], radius=int(0.35 * px), fill=bg)
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh); ds.text((m - bb[0], m - bb[1] + px * 0.06), text, font=f, fill=(0, 0, 0, 200), stroke_width=sw + int(px * 0.06), stroke_fill=(0, 0, 0, 200))
    a = np.asarray(sh, np.float32) / 255; a[..., 3] = cv2.GaussianBlur(a[..., 3], (0, 0), px * 0.10); im2 = Image.fromarray((a * 255).astype(np.uint8), 'RGBA') if not bg else Image.new('RGBA', (w, h), (0, 0, 0, 0))
    im2.alpha_composite(im); d = ImageDraw.Draw(im2); d.text((m - bb[0], m - bb[1]), text, font=f, fill=col + (255,), stroke_width=sw, stroke_fill=(12, 12, 14, 255))
    arr = np.asarray(im2, np.float32) / 255; out = (arr[..., 2::-1] * arr[..., 3:4], arr[..., 3:4]); _spr[k] = out; return out
def put(img, spr, x, y, alpha=1.0, anchor='mm', scale=1.0):
    if alpha <= 0.003: return
    rgb, a = spr
    if abs(scale - 1) > 0.01: rgb = cv2.resize(rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR); a = cv2.resize(a, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)[..., None]
    h, w = a.shape[:2]; x = x * S; y = y * S
    x0 = int(round(x - (w / 2 if anchor[0] == 'm' else 0 if anchor[0] == 'l' else w))); y0 = int(round(y - (h / 2 if anchor[1] == 'm' else 0 if anchor[1] == 't' else h)))
    H_, W_ = img.shape[:2]; xa, ya, xb, yb = max(0, x0), max(0, y0), min(W_, x0 + w), min(H_, y0 + h)
    if xa >= xb or ya >= yb: return
    r = rgb[ya - y0:yb - y0, xa - x0:xb - x0]; al = a[ya - y0:yb - y0, xa - x0:xb - x0] * alpha
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - al) + r * alpha
def label(img, text, size, x, y, t, t0, t1, col=WHITE, anchor='mm', rise=14, **kw):
    a = win(t, t0, t1, 0.22, 0.22)
    if a > 0: put(img, sprite(text, size, col, **kw), x, y + rise * (1 - ease(ramp(t, t0, t0 + 0.3), 'out')), a, anchor)

def route_sprite(here=False, lit=1.0):
    k = ('route', here, round(lit, 2), S)
    if k in _spr: return _spr[k]
    w, h = int(900 * S), int((150 if here else 112) * S); im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, int(104 * S)], radius=int(26 * S), fill=(14, 15, 18, 178))
    names = ['打包出发', '路上', '中转', '干线', '签收']; x0, step, yy = 110 * S, 170 * S, 34 * S
    d.line([(x0, yy), (x0 + step * 4, yy)], fill=(96, 98, 104, 255), width=max(1, int(3 * S)))
    f = ImageFont.truetype(FONT_B, int(30 * S), index=2); fr = ImageFont.truetype(FONT_R, int(29 * S), index=2)
    for i, n in enumerate(names):
        cx = x0 + i * step; r = (12 if i == 0 else 8) * S
        if i == 0: d.ellipse([cx - r * (1.5 + 0.5 * lit), yy - r * (1.5 + 0.5 * lit), cx + r * (1.5 + 0.5 * lit), yy + r * (1.5 + 0.5 * lit)], fill=GOLD + (int(70 * lit),))
        d.ellipse([cx - r, yy - r, cx + r, yy + r], fill=GOLD + (255,) if i == 0 else (120, 122, 128, 255))
        d.text((cx, 72 * S), n, font=f if i == 0 else fr, fill=WHITE + (255,) if i == 0 else (168, 170, 176, 255), anchor='mm')
    if here: d.text((x0, 128 * S), '▲ 你在这里', font=f, fill=GOLD + (255,), anchor='mm')
    arr = np.asarray(im, np.float32) / 255; out = (arr[..., 2::-1] * arr[..., 3:4], arr[..., 3:4]); _spr[k] = out; return out

# ---------- 小元件 ----------
def glow_dot(img, x, y, r, col, amt):
    """加亮的圆光斑（鼓点闪光、飞出去的信号）"""
    if amt <= 0.003: return
    x, y, r = x * S, y * S, max(1.5, r * S); R = int(r * 3.2); H_, W_ = img.shape[:2]; xa, ya, xb, yb = max(0, int(x) - R), max(0, int(y) - R), min(W_, int(x) + R), min(H_, int(y) + R)
    if xa >= xb or ya >= yb: return
    uu, vv = np.meshgrid(np.arange(xa, xb) - x, np.arange(ya, yb) - y); d2 = (uu * uu + vv * vv) / (r * r)
    g = (np.exp(-d2 * 1.6) + 0.35 * np.exp(-d2 * 0.22))[..., None] * amt
    img[ya:yb, xa:xb] += g * (np.array(col[::-1], np.float32) / 255)
def line(img, p, q, col, width, alpha=1.0):
    if alpha <= 0.003: return
    ov = img.copy(); cv2.line(ov, (int(p[0] * S), int(p[1] * S)), (int(q[0] * S), int(q[1] * S)), tuple(c / 255 for c in col[::-1]), max(1, int(round(width * S))), cv2.LINE_AA); img[:] = img * (1 - alpha) + ov * alpha
def rect(img, x0, y0, x1, y1, col, alpha=1.0, outline=0):
    if alpha <= 0.003: return
    a, b = (int(round(x0 * S)), int(round(y0 * S))), (int(round(x1 * S)), int(round(y1 * S))); c = tuple(v / 255 for v in col[::-1])
    if outline: ov = img.copy(); cv2.rectangle(ov, a, b, c, max(1, int(round(outline * S))), cv2.LINE_AA); img[:] = img * (1 - alpha) + ov * alpha
    else: img[a[1]:b[1], a[0]:b[0]] = img[a[1]:b[1], a[0]:b[0]] * (1 - alpha) + np.array(c, np.float32) * alpha

# ---------- 灰尘（离镜头很近、虚成光斑；数量少、慢慢漂）----------
_rs = np.random.default_rng(3)
DUST = [dict(x=_rs.uniform(0, 1), y=_rs.uniform(0.15, 0.95), r=_rs.uniform(26, 84), a=_rs.uniform(0.035, 0.085), vx=_rs.uniform(-0.006, 0.010), vy=_rs.uniform(-0.012, -0.002), ph=_rs.uniform(0, 6.28), z=_rs.uniform(1.2, 2.2)) for _ in range(11)]
def whip_shift(t):
    """甩镜累计带走的位移（灰尘离镜头近，被甩得更远）"""
    sx = sy = 0.0
    for tc, a, b, d in WHIPS:
        if d == 'zoom': continue
        e = ease((t - (tc - WHIP / 2)) / WHIP, 'io'); sx -= d[0] * e; sy -= d[1] * e
    return sx, sy
def dust(img, t, amt=1.0):
    h, w = img.shape[:2]; sm = np.zeros((h // 4, w // 4), np.float32); sx, sy = whip_shift(t)
    for p in DUST:
        x = ((p['x'] + p['vx'] * t + 0.012 * math.sin(0.4 * t + p['ph']) + sx * p['z']) % 1.2 - 0.1) * w / 4; y = ((p['y'] + p['vy'] * t + 0.008 * math.cos(0.33 * t + p['ph']) + sy * p['z']) % 1.2 - 0.1) * h / 4
        r = p['r'] * S / 4; a = p['a'] * (0.75 + 0.25 * math.sin(0.9 * t + p['ph']))
        cv2.circle(sm, (int(x), int(y)), int(r), a, -1, cv2.LINE_AA); cv2.circle(sm, (int(x), int(y)), int(r), a * 1.5, max(1, int(r * 0.12)), cv2.LINE_AA)
    sm = cv2.GaussianBlur(sm, (0, 0), 2.2 * S + 0.5); g = cv2.resize(sm, (w, h), interpolation=cv2.INTER_LINEAR)[..., None]
    img += g * np.array([0.62, 0.86, 1.0], np.float32) * amt

# ---------- 调色 ----------
_vig = {}
def grade(img, t):
    """提色度、加一点对比和暗角。样张测得静帧平均色度只有 0.09–0.10（规则建议 ≥ 0.2）"""
    h, w = img.shape[:2]; x = np.clip(img, 0, 4)
    lum = (x @ np.array([0.114, 0.587, 0.299], np.float32))[..., None]
    ch = x.max(-1, keepdims=True) - x.min(-1, keepdims=True); neu = np.clip(1 - ch / 0.10, 0, 1)
    x = x + neu * np.clip(lum, 0, 0.8) * np.array(AIR, np.float32)                  # 接近灰色的地方（雾、金属、封装）偏冷青蓝：空气感，也和绿板、金色信号分开
    x = lum + (x - lum) * SAT                                                       # 饱和度
    x = x * (1 + CONTRAST * (np.clip(lum, 0, 1) - 0.42))                          # 对比（以中间调为轴）
    sh = np.clip(1 - lum * 2.2, 0, 1); hi = np.clip(lum * 1.6 - 0.6, 0, 1)
    x = x + sh * np.array(TINT_SH, np.float32) + hi * np.array(TINT_HI, np.float32)  # 暗部偏青、亮部偏暖
    if (h, w) not in _vig:
        u, v = np.meshgrid(np.linspace(-1, 1, w, dtype=np.float32), np.linspace(-1, 1, h, dtype=np.float32)); _vig[(h, w)] = (1 - 0.30 * np.clip((u * u * 0.8 + v * v) - 0.35, 0, 1))[..., None]
    return np.clip(x * _vig[(h, w)] * GAIN, 0, 1)
SAT, CONTRAST, GAIN = 1.7, 0.55, 1.06; AIR = (0.30, 0.10, -0.09); TINT_SH = (0.022, 0.010, -0.006); TINT_HI = (-0.012, 0.004, 0.018)   # BGR

# ---------- 光带上的演示 ----------
band_long = B.Band(TLm.SEQ_LONG); band_scr = B.Band(TLm.SEQ_SCR); band_clk = B.Band([1, 0] * 120); band_one = B.Band([1] * 240)
HITS, _yl = TLm.hits(TL, PH, [10.4, 15.9, 15.9]); YL = dict(zip(('side', 'count', 'count2'), _yl))     # 「听的位置」；自动微调到鼓点落在八分音符的格子上
def yl_at(t): return YL['side'] if t < T['count'] else YL['count'] if t < B0['y7'] else YL['count2']
LOCK_HITS = [h for h in HITS if sub0('y6', 1) - 0.4 <= h <= TL['marks']['count_park']][-4:]     # y6「跟着鼓点校准自己」：最后这几个鼓点，每个把刻度挪近一步
def run_span(phi, idx0, n=5):
    """比特串里第 idx0 … idx0+n−1 位现在在板面上的 y 区间"""
    ya = phi + idx0 * B.BIT; ya -= TLm.PERIOD * round((ya - 14) / TLm.PERIOD); return ya, ya + n * B.BIT
def tint(img, mask, col, amt):
    img += mask[..., None] * (np.array(col[::-1], np.float32) / 255) * amt

def scene_fx(img, G, v, t):
    """板面上的东西：光带、刻度、时钟线、鼓点闪光、还原后的那一行"""
    h, w = img.shape[:2]; Gs = np.diag([S, S, 1.0]) @ G; phi = PH(t); cam = B.CAM[v]; dk = B.DOF_K[v]; px = W0 / B.SW * S
    bs = TLm.bit_scale(t, TL); blur = 0.0; piv = 16.0
    if T['close'] <= t < T['wide']: blur = 0.55 * ease((t - VS['y10'] - 0.2) / 1.6, 'io') * (1 - 0.45 * ramp(t, T['rx'] - 0.15, T['rx'] + 0.15))
    if t >= T['close2']: blur = 0.75 * ease((t - VS['y14'] - 0.5) / 2.2, 'io')
    if v == 'wide': piv = 30.0
    ph_eff = phi if bs == 1.0 else None
    kw = dict(cam=cam, dofk=dk, px=px, blur_bits=blur, bit_scale=bs, yhi=62.0)
    # 相位：一位变短时以 piv 为中心缩（屏幕上不乱跑）
    def rend(bd, **k2):
        k = dict(kw); k.update(k2); s_ = k['bit_scale']
        phase = piv - (piv - phi) * s_ if s_ != 1.0 else phi
        return bd.render(Gs, w, h, phase, **k)
    ticks = None; tick_col = WHITE; tick_a = 0.0; ticks2 = None
    # y3：那段连成一片的高电平，分成 4 份还是 5 份？（淡刻度在两种分法之间来回）
    if VS['y3'] + 1.2 <= t < B0['y4'] + 0.2:
        ya, yb = run_span(phi, 182); k = int((t - VS['y3'] - 1.2) / 0.55) % 2; sc = 1.0 if k else 1.25
        ticks = dict(phase=ya, scale=sc, half=0.34, thick=0.03, ylo=ya - 0.05, yhi=yb + 0.05); tick_a = 0.75 * win(t, VS['y3'] + 1.2, B0['y4'] + 0.2, 0.3, 0.3)
    # y4：节拍刻度（每一位一格）
    if B0['y4'] + 0.2 <= t < B0['y5'] + 0.4:
        ticks = dict(phase=phi, half=0.52, thick=0.045); tick_a = 0.95 * win(t, VS['y4'] + 0.9, B0['y5'] + 0.4, 0.5, 0.4)
    # y6：刻度先是错开的，跟着鼓点对齐
    t_lock = sub0('y6', 1) + 0.3
    if t_lock - 0.6 <= t < B0['y7']:
        off = 0.42 * B.BIT * (1 - sum(ease((t - h) / 0.14, 'out') for h in LOCK_HITS) / max(1, len(LOCK_HITS))); ticks = dict(phase=phi + off, half=0.52, thick=0.045); tick_a = 0.95 * ramp(t, t_lock - 0.6, t_lock - 0.1)
    # y7：一长串 1，没有鼓点 → 芯片自己数的拍（红）慢慢跑偏；真实的节拍（深色）不动
    if B0['y7'] <= t < B0['y8'] + 0.7:
        d = 0.085 * ease((t - VS['y7'] - 1.0) / 2.6, 'in') * (1 - ease((t - B0['y8'] - 0.15) / 0.5, 'io')); red = ramp(t, VS['y7'] + 0.9, VS['y7'] + 1.5) * (1 - ramp(t, B0['y8'] + 0.2, B0['y8'] + 0.65))
        ticks = dict(phase=phi + (17.6 - phi) * (1 - (1 + d)) , scale=1 + d, half=0.52, thick=0.034); tick_col = tuple(int(WHITE[i] + (RED[i] - WHITE[i]) * red) for i in range(3)); tick_a = 0.95
        ticks2 = dict(phase=phi, half=0.30, thick=0.03)
    # y8：打乱以后刻度重新对齐
    if B0['y8'] + 0.7 <= t < T['close'] - 0.1: ticks = dict(phase=phi, half=0.52, thick=0.045); tick_a = 0.95 * (1 - ramp(t, T['close'] - 0.5, T['close'] - 0.1))
    # 光带本体
    m = ease((t - B0['y8'] - 0.15) / 0.6, 'io')                                   # 打乱：一长串 1 原地变成有起有伏
    hb = None
    if TL['marks']['count_park'] - 0.1 <= t < B0['y7']:                            # y6：五拍一拍一拍亮起（先到的在左边 = y 大的一头）
        ya, yb = run_span(phi, 152); n = min(5, int((t - (TL['marks']['count_park'] + 0.15)) / 0.25) + 1)
        if n > 0: hb = (yb - n * B.BIT, yb, 0.55)
    lvl, al, tk = rend(band_long if m < 1 else band_scr, ticks=ticks, hi_boost=hb)
    if 0 < m < 1: lvl2, _, _ = rend(band_scr); lvl = lvl * (1 - m) + lvl2 * m
    shimmer = 1.0 + 0.05 * math.sin(7.0 * t)
    img[:] = B.comp_band(img, lvl, al, gain=shimmer)
    if ticks is not None and tick_a > 0:
        if ticks2 is not None:
            _, _, tk2 = rend(band_one, ticks=ticks2); a2 = (tk2 * 0.85 * ramp(t, VS['y7'] + 0.9, VS['y7'] + 1.5) * (1 - ramp(t, B0['y8'] + 0.2, B0['y8'] + 0.65)))[..., None]; img[:] = img * (1 - a2) + a2 * 0.06
        a = (tk * tick_a)[..., None]; img[:] = img * (1 - a) + a * (np.array(tick_col[::-1], np.float32) / 255)
    # y4 第三段：旁边并没有另外一对「时钟线」（虚的一对，随后划掉）
    tk0 = sub0('y4', 2)
    if tk0 <= t < B0['y5'] + 0.3:
        a = win(t, tk0, B0['y5'] + 0.3, 0.35, 0.35) * (1 - 0.55 * ramp(t, tk0 + 1.3, tk0 + 1.6))
        l2, a2, _ = band_clk.render(Gs, w, h, phi * 1.0, cam=cam, dofk=dk, px=px, xoff=-0.95, width=0.34)
        aa = (a2 * (0.25 + 0.5 * np.clip(l2, 0, 1)) * a)[..., None]; img[:] = img * (1 - aa * 0.6) + aa * (np.array(BLUE[::-1], np.float32) / 255)
    # y8 第三段：到对面按同样的规则还原（旁边一行 = 还原后的数据，从芯片那头一格格亮出来）
    tr = sub0('y8', 2) - 0.2
    if tr <= t < T['close']:
        ylo = 17.6 - 7.5 * ease((t - tr) / 1.4, 'io'); l3, a3, _ = band_one.render(Gs, w, h, phi, cam=cam, dofk=dk, px=px, xoff=0.85, width=0.34, ylo=ylo, yhi=17.6)
        img[:] = B.comp_band(img, l3 * 0.9, a3 * (1 - ramp(t, T['close'] - 0.35, T['close'] - 0.1)), glow=0.35)
    if v == 'rx' and not whip_at(t):                                               # 进了封装以后：走到接收电路的路（示意，虚线上有小光点在走）
        p0 = B.proj(G, 0, 62.0); p1 = (W0 * 0.90, p0[1] - (p0[1] - H0 * 0.445) * 1.0); a = ramp(t, T['rx'] + 0.2, T['rx'] + 0.6) * (1 - ramp(t, T['wide'] - 0.3, T['wide'] - 0.1))
        for i in range(14):
            u0 = (i + (t * 1.6) % 1) / 14; glow_dot(img, p0[0] + (p1[0] - p0[0]) * u0, p0[1] + (p1[1] - p0[1]) * u0, 9, (255, 196, 96), 0.75 * a * min(1, u0 * 6) * min(1, (1 - u0) * 6))
    # 鼓点闪光：跳变经过「听的位置」的那一下
    yl = yl_at(t); gx, gy = B.proj(G, 0, yl)
    show_gate = win(t, TL['marks']['flow1'][0] - 0.3, TL['marks']['count_park'], 0.3, 0.3) + win(t, TL['marks']['flow2'][0] - 0.2, T['close'] - 0.2, 0.3, 0.2)
    if show_gate > 0 and not whip_at(t):
        p1, p2 = B.proj(G, -0.62, yl), B.proj(G, 0.62, yl); line(img, p1, p2, WHITE, 5, 0.8 * show_gate)
    for th in HITS:
        if 0 <= t - th < 0.42 and not whip_at(t):
            k = math.exp(-(t - th) / 0.11); glow_dot(img, gx, gy, 46 + 60 * (t - th), (255, 214, 140), 0.95 * k)

def bars(img, t, t0, t1, items, x0, y0, hmax=300, bw=64, gap=150):
    """竖条（速度、每比特耗电）：items = [(名字, 颜色, 高度函数)]"""
    a = win(t, t0, t1, 0.3, 0.3)
    if a <= 0: return
    for i, (name, col, f) in enumerate(items):
        x = x0 + i * gap; v = f(t); rect(img, x - 6, y0 - hmax - 6, x + bw + 6, y0 + 6, (14, 15, 18), 0.6 * a)
        rect(img, x, y0 - hmax, x + bw, y0, WHITE, 0.9 * a, outline=3); rect(img, x + 5, y0 - 5 - (hmax - 10) * v, x + bw - 5, y0 - 5, col, 0.95 * a)
        put(img, sprite(name, 38, WHITE), x + bw / 2, y0 + 50, a)

def overlays(img, v, t, G):
    """贴在画面里的字和小图（原稿的大字、标签照留）"""
    cx = W0 / 2
    # y1：大字问题（五站条下面）
    a = win(t, 0.0, T['B'] - 0.05, 0.001, 0.2)
    if a > 0:
        put(img, sprite('芯片是怎么数清', 92, WHITE), cx, 400, a); put(img, sprite('0 和 1 的？', 100, GOLD), cx, 512, a)
    label(img, '机房 · AI 服务器主板', 54, cx, 372, t, T['B'] + 1.5, T['side'] + 0.6)
    label(img, '示意：金色光带 = 两线间的电压差（亮 1 暗 0）', 38, cx, 1240, t, T['B'] + 2.3, VS['y3'] + 1.0, GOLD, bold=False)
    if G is not None and v in ('side', 'count') and not whip_at(t):
        phi = PH(t)
        # y3：连成一片的高电平；4？5？
        if VS['y3'] + 0.9 <= t < B0['y4'] + 0.25:
            ya, yb = run_span(phi, 182); pa, pb = B.proj(G, 0, ya), B.proj(G, 0, yb); mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
            a = win(t, VS['y3'] + 0.9, B0['y4'] + 0.25, 0.3, 0.25); e = ease(ramp(t, VS['y3'] + 0.9, VS['y3'] + 1.5), 'out')
            q0 = B.proj(G, 0.42, ya); q1 = B.proj(G, 0.42, yb); line(img, q0, (q0[0] + (q1[0] - q0[0]) * e, q0[1] + (q1[1] - q0[1]) * e), GOLD, 6, a)
            put(img, sprite('连成一片的高电平', 50, GOLD), mx + 30, my - 96, a)
            a2 = win(t, sub0('y3', 1) + 1.9, B0['y4'] + 0.25, 0.2, 0.25); k = ease(ramp(t, sub0('y3', 1) + 1.9, sub0('y3', 1) + 2.2), 'out')
            put(img, sprite('4？5？', 76, DARK, stroke=0, bg=(250, 248, 240, 255), pad=22), mx - 40, my + 150, a2, scale=0.8 + 0.2 * k)
        # y6：数五拍
        cp = TL['marks']['count_park']
        if cp <= t < B0['y7']:
            ya, yb = run_span(phi, 152)
            for i in range(5):
                ti = cp + 0.15 + 0.25 * i; yy = yb - (i + 0.5) * B.BIT; p = B.proj(G, 0.0, yy); q = B.proj(G, 0.9, yy)
                a = ramp(t, ti, ti + 0.12) * (1 - ramp(t, B0['y7'] - 0.25, B0['y7'])); k = 1 + 0.35 * (1 - ease(ramp(t, ti, ti + 0.25), 'out'))
                put(img, sprite(str(i + 1), 76, GOLD), q[0], q[1] - 36, a, scale=k)
    label(img, '每一位占的时间 = 一拍', 60, cx, 372, t, VS['y4'] + 1.0, sub0('y4', 2) - 0.1)
    tk0 = sub0('y4', 2)
    if G is not None and tk0 <= t < B0['y5'] + 0.3 and v == 'side':
        p = B.proj(G, -0.95, 7.3); a = win(t, tk0 + 1.3, B0['y5'] + 0.3, 0.12, 0.3); e = ease(ramp(t, tk0 + 1.3, tk0 + 1.55), 'out'); r = 44
        line(img, (p[0] - r, p[1] - r), (p[0] - r + 2 * r * e, p[1] - r + 2 * r * e), RED, 11, a); line(img, (p[0] - r, p[1] + r), (p[0] - r + 2 * r * e, p[1] + r - 2 * r * e), RED, 11, a)
        label(img, '时钟线：不另外送', 50, min(780, max(300, p[0] + 10)), p[1] + 104, t, tk0 + 0.3, B0['y5'] + 0.3)
    label(img, '♪  跟着鼓点拍手', 66, cx, 372, t, VS['y5'] + 0.2, B0['y6'] - 0.1, GOLD)
    label(img, '信号每跳一下 = 一个鼓点', 58, cx, 372, t, VS['y6'] + 0.9, sub0('y6', 1) - 0.1, GOLD)
    label(img, '五个，不是四个', 84, cx, 380, t, sub0('y6', 2) - 0.05, B0['y7'] - 0.05, GOLD)
    label(img, '没有鼓点，拍子跑偏', 68, cx, 366, t, VS['y7'] + 1.3, B0['y8'] - 0.05, RED)
    label(img, '深色 = 真实节拍　红 = 芯片数的拍', 38, cx, 452, t, VS['y7'] + 1.7, B0['y8'] - 0.05, bold=False)
    label(img, '打乱以后：鼓点一直都在', 62, cx, 372, t, VS['y8'] + 1.6, sub0('y8', 2) - 0.25, GOLD)
    label(img, '到对面：按同样的规则还原', 58, cx, 372, t, sub0('y8', 2) - 0.2, T['close'] - 0.2)
    # y9：速度翻倍，一拍的时间减半（三级台阶）
    t9 = VS['y9']; a = win(t, t9 + 0.5, VS['y10'] - 0.1, 0.3, 0.3)
    if a > 0:
        label(img, '速度翻倍：一拍的时间减半', 58, cx, 372, t, t9 + 0.5, VS['y10'] - 0.1)
        for row, (lab, n, ts) in enumerate((('1×', 4, t9 + 0.6), ('2×', 8, t9 + 1.15), ('4×', 16, t9 + 2.35))):
            ar = a * ramp(t, ts, ts + 0.25); y0 = 490 + row * 100; x0, x1 = 250, 880
            if ar <= 0: continue
            rect(img, x0 - 8, y0 - 8, x1 + 8, y0 + 56, (14, 15, 18), 0.55 * ar); rect(img, x0, y0, x1, y0 + 48, WHITE, 0.9 * ar, outline=3)
            for k in range(0, n, 2): rect(img, x0 + (x1 - x0) * k / n + 3, y0 + 4, x0 + (x1 - x0) * (k + 1) / n - 1, y0 + 44, GOLD, 0.95 * ar)
            put(img, sprite(lab, 42, GOLD), x0 - 64, y0 + 24, ar)
    label(img, '越快，越糊', 88, cx, 380, t, VS['y10'] + 0.3, T['rx'] - 0.2, GOLD)
    label(img, '修信号的电路（示意）', 60, cx, 366, t, T['rx'] + 0.35, T['wide'] - 0.2, BLUE)
    label(img, '散热器已移开（示意）', 36, cx, 448, t, T['rx'] + 0.6, T['wide'] - 0.2, bold=False)
    t10 = sub0('y10', 2)
    bars(img, t, t10 - 0.2, T['wide'] - 0.2, [('耗电', GOLD, lambda tt: 0.25 + 0.6 * ease((tt - t10) / 1.3, 'io')), ('面积', BLUE, lambda tt: 0.25 + 0.5 * ease((tt - t10 - 0.5) / 1.3, 'io'))], 690, 1180, hmax=260)
    t11 = VS['y11']; s11 = sub0('y11', 1)
    bars(img, t, t11 + 0.5, T['arev'] - 0.15, [('速度', WHITE, lambda tt: 0.35 + 0.55 * ease((tt - t11 - 1.2) / 1.2, 'io')), ('每比特耗电', GOLD, lambda tt: 0.8 - 0.5 * ease((tt - s11 - 0.3) / 1.4, 'io'))], 610, 820, hmax=300, gap=200)
    label(img, '更快，每个比特还要更省电', 58, cx, 372, t, t11 + 0.5, T['arev'] - 0.15, GOLD)
    label(img, '每秒上千亿个比特', 80, cx, 380, t, VS['y12'] + 1.5, T['card'] - 0.5, GOLD)
    # y12：金色光点从光带上弹起来往上飞（接 A 段倒放）
    if G is not None and T['arev'] - 0.5 <= t < T['arev']:
        u = ramp(t, T['arev'] - 0.5, T['arev']); p = B.proj(G, 0, 30.0); glow_dot(img, p[0] + (cx - p[0]) * u, p[1] - (p[1] + 200) * ease(u, 'in'), 26 + 30 * u, (255, 206, 120), 1.3)
    # y13：一句话带走
    if v == 'card' or (T['close2'] <= t < T['close2'] + 0.6):
        tc = T['card']; slide = -H0 * ease((t - T['close2']) / 0.5, 'in'); a = ramp(t, tc, tc + 0.3)
        put(img, sprite('一句话带走', 104, GOLD), cx, 650 + slide, a * ramp(t, tc + 0.1, tc + 0.4))
        x0, x1 = 150, 930; xr = x0 + (x1 - x0) * ease(ramp(t, tc + 0.2, tc + 1.0), 'io'); bw_ = 52; off = (t * 300) % (bw_ * 240)      # 一列比特从左往右流（排成一列）
        if 0 <= 752 + slide < H0 - 30:
            k0 = int((x0 - off) // bw_)
            for k in range(k0, k0 + int((x1 - x0) / bw_) + 3):
                xa, xb = max(x0, k * bw_ + off), min(xr, (k + 1) * bw_ + off)
                if xb > xa: rect(img, xa, 738 + slide, xb, 766 + slide, (255, 236, 196) if TLm.BITS[k % 120] else (150, 96, 22), 0.95)
        put(img, sprite('发出去：排成一列', 70, WHITE), cx, 860 + slide, ramp(t, VS['y13'] + 0.9, VS['y13'] + 1.2))
        put(img, sprite('收进来：听准节拍、拆回一排', 70, WHITE), cx, 980 + slide, ramp(t, sub0('y13', 1), sub0('y13', 1) + 0.3))
    label(img, '下一篇：信号为什么越跑越模糊？', 58, cx, 380, t, VS['y14'] + 0.2, T['end'] + 1, GOLD)

BREAK = {'可高速连接通常不另外送一个节拍器过去': 7, 'SerDes 的速度大约每过几年就要翻一倍': 11}     # 没有标点的长句：折行不拆词
def ui(img, v, t):
    """五站条常驻（第一站「打包出发」亮）、系列名、字幕"""
    lit = 0.6 + 0.4 * math.sin(2.4 * t) ** 2; here = win(t, T['card'] + 0.5, T['close2'] + 0.1, 0.3, 0.3)
    put(img, route_sprite(False, lit), W0 / 2 - 30, 164, 1.0, 'mt')
    if here > 0: put(img, route_sprite(True, 1.0), W0 / 2 - 30, 164, here, 'mt')
    put(img, sprite('一语道破 · 白话光互连 02', 26, (214, 212, 204), bold=False, stroke=2), 62, 300 + 40 * (here > 0), 0.85 * (1 - here), 'lm')
    for s in SUBS:
        if s['t0'] - 0.04 <= t < s['t1']:
            txt = s['text']; f = ImageFont.truetype(FONT_B, 50, index=2)
            if f.getlength(txt) <= W0 * 0.80: lines = [txt]
            elif txt in BREAK: lines = [txt[:BREAK[txt]], txt[BREAK[txt]:]]
            else:
                cuts = [i + 1 for i, ch in enumerate(txt[:-1]) if ch in '，：；、']; c = min(cuts, key=lambda i: abs(i - len(txt) / 2)) if cuts else (len(txt) + 1) // 2; lines = [txt[:c], txt[c:]]
            for i, ln in enumerate(lines): put(img, sprite(ln, 50, WHITE, stroke=5), W0 * 0.47, 1400 + i * 70 - (35 if len(lines) > 1 else 0), ramp(t, s['t0'] - 0.04, s['t0'] + 0.06))

def frame(t):
    img, G, v = background(t); img = img.copy()
    if G is not None: scene_fx(img, G, v, t)
    if v == 'card':                                                              # 卡片：屏幕的深色底铺满画面；底上有很淡的流动光，不是死黑
        h, w = img.shape[:2]; glow_dot(img, W0 * (0.5 + 0.32 * math.sin(1.1 * t)), H0 * 0.42, 420, (70, 50, 22), 0.6); glow_dot(img, W0 * (0.5 - 0.34 * math.sin(0.9 * t + 1)), H0 * 0.72, 380, (18, 46, 60), 0.6)
    dust(img, t, 0.6 if v in ('A', 'Arev') else 1.0)
    img = grade(img, t) if v != 'card' else np.clip(img, 0, 1)
    if T['card'] - 0.2 <= t < T['card']: k = ramp(t, T['card'] - 0.2, T['card']); img = img * (1 - k) + (np.array(DARK[::-1], np.float32) / 255) * k
    if T['close2'] <= t < T['close2'] + 0.5:                                      # 卡片往上滑走，露出下面的 close 背景
        h, w = img.shape[:2]; o = int(h * (1 - ease((t - T['close2']) / 0.5, 'in'))); img[:o] = np.array(DARK[::-1], np.float32) / 255
    overlays(img, v, t, G); ui(img, v, t)
    if t > T['end'] - 0.4: img = img * (1 - ease((t - (T['end'] - 0.4)) / 0.4, 'io'))          # 片尾淡出
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)

if __name__ == '__main__':
    mode = sys.argv[1]; opt = dict(a.split('=') for a in sys.argv[2:] if '=' in a); pos = [a for a in sys.argv[2:] if '=' not in a]
    S = float(opt.get('scale', 1.0))
    if mode == 'sheet':
        ts = [float(x) for x in pos[1:]]; fr = [cv2.resize(frame(t), (270, 480), interpolation=cv2.INTER_AREA) for t in ts]
        for f_, t in zip(fr, ts): cv2.putText(f_, f'{t:.1f}', (8, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 255, 255), 2)
        n = int(opt.get('cols', 8)); rows = [np.hstack(fr[i:i + n] + [np.zeros_like(fr[0])] * (n - len(fr[i:i + n]))) for i in range(0, len(fr), n)]
        cv2.imwrite(pos[0], np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 86]); print('sheet', pos[0])
    elif mode == 'one':
        cv2.imwrite(pos[0], frame(float(pos[1])), [cv2.IMWRITE_JPEG_QUALITY, 90])
    elif mode == 'frames':
        out = pos[0]; os.makedirs(out, exist_ok=True); n = int(round(T['end'] * FPS)); i0 = int(opt.get('i0', 0)); i1 = int(opt.get('i1', n))
        for i in range(i0, min(i1, n)): cv2.imwrite(os.path.join(out, f'{i:05d}.png'), frame(i / FPS), [cv2.IMWRITE_PNG_COMPRESSION, 1])
        print('frames', i0, i1)
    elif mode == 'info':
        json.dump(dict(T=T, vs=VS, b0=B0, subs=SUBS, hits=HITS, end=T['end'], marks=TL['marks'], dur=TL['dur']), open(pos[0], 'w'), ensure_ascii=False, indent=1); print('hits', len(HITS), [round(h, 2) for h in HITS])
