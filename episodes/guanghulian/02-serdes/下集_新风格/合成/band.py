# 光带：按 Blender 导出的走线位置求板面的透视（单应），在板面坐标里画金色光带、节拍刻度，再投到画面上。
# 板面坐标：x = 横向（mm，线对中心为 0），y = 沿走线（mm，往芯片方向为正）。和 shot_open.py 的 signal_band 同一套：
#   每一位 0.7 mm（示意）、光带宽 0.32 mm；高电平亮、低电平暗，相邻同电平连成一片。
import json, os, numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__)); ST = os.path.join(HERE, 'in', 'stills')
BIT = 0.7; BAND_W = 0.42; SW, SH = 1188, 2112
BITS = [1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0] * 4     # = make_assets.py 的 BITS（第 2–6 位是连续五个 1）
VIEW_FILE = {'side': 'B_side_normal_noband', 'count': 'B_count_normal_noband', 'close': 'B_close_normal_noband', 'rx': 'B_rx_normal_xray_noband', 'wide': 'B_wide_normal_noband'}
# 相机（shot_open.py 的 VIEWS）：位置、对焦点；用来估景深（离对焦距离越远越虚）
CAM = {'side': ((-3.6, 2.6, 0.95), (0.3, 8.0, 0.35)), 'close': ((-0.55, 10.0, 0.55), (0.05, 16.0, 0.03)), 'rx': ((-9.0, 50.0, 14.0), (0.0, 78.0, 2.0)),
       'wide': ((-22.0, -28.0, 22.0), (0.0, 40.0, 2.0)), 'count': ((-4.2, 13.6, 1.5), (0.0, 14.2, 0.05))}
DOF_K = {'side': 6.0, 'count': 6.0, 'close': 6.0, 'rx': 3.0, 'wide': 3.0}     # 弥散圆（静帧像素）= K × |d − d_f| / d；按 B 段末帧校准，见 calib()

def load_view(v):
    j = json.load(open(os.path.join(ST, VIEW_FILE[v] + '.json'))); P = j['pts']
    src = np.array([[0.0, p['y']] for p in P] + [[-0.4, p['y']] for p in P], np.float64)
    dst = np.array([[p['x'], p['yy']] for p in P] + [[p['lx'], p['ly']] for p in P], np.float64)
    H, _ = cv2.findHomography(src, dst, 0)
    err = np.abs(cv2.perspectiveTransform(src[None], H)[0] - dst).max()
    ym = float(np.median([p['y'] for p in P]))
    if H[2, 1] * ym + H[2, 2] < 0: H = -H                                          # 约定：看得见的点分母为正（两个机位之间插值时才不会翻面）
    return dict(name=v, H=H, err=err, y0=min(p['y'] for p in P), y1=max(p['y'] for p in P), img=None)

def proj(G, x, y):
    """板面 (x, y) → 画面像素"""
    v = G @ np.array([x, y, 1.0]); return v[0] / v[2], v[1] / v[2]

def wave_table(bits, sub=32):
    """把比特串做成一张查找表：行 = 模糊程度（0、0.06、0.12 … 位，逐行加倍），列 = 沿走线的位置。画面上远处一位不到一个像素时取平均，不闪。"""
    n = len(bits); w = np.repeat(np.array(bits, np.float32), sub); rows = []
    sig = [0.0] + [0.06 * 2 ** k for k in range(8)]
    for s in sig:
        if s == 0: rows.append(w); continue
        k = np.arange(-int(4 * s * sub) - 1, int(4 * s * sub) + 2); g = np.exp(-0.5 * (k / (s * sub)) ** 2); g /= g.sum()
        rows.append(np.convolve(np.tile(w, 3), g, 'same')[len(w):2 * len(w)].astype(np.float32))
    T = np.stack(rows); return np.concatenate([T, T[:, :2]], 1), sig, sub, n

class Band:
    def __init__(self, bits=BITS):
        self.set_bits(bits)
    def set_bits(self, bits):
        self.T, self.sig, self.sub, self.n = wave_table(bits); self.bits = list(bits)
    def level_rows(self, s_bits):
        """模糊量（位）→ 查找表的行坐标（行间线性插值）"""
        s = np.maximum(s_bits, 1e-4); r = np.log2(s / 0.06) + 1.0
        return np.clip(np.where(s < 0.06, s / 0.06, r), 0, len(self.sig) - 1).astype(np.float32)
    def world(self, G, W, H):
        """每个画面像素对应的板面坐标，和一个像素在板面上有多大（mm）"""
        Gi = np.linalg.inv(G); u, v = np.meshgrid(np.arange(W, dtype=np.float32) + 0.5, np.arange(H, dtype=np.float32) + 0.5)
        d = Gi[2, 0] * u + Gi[2, 1] * v + Gi[2, 2]
        X = (Gi[0, 0] * u + Gi[0, 1] * v + Gi[0, 2]) / d; Y = (Gi[1, 0] * u + Gi[1, 1] * v + Gi[1, 2]) / d
        ok = (G[2, 0] * X + G[2, 1] * Y + G[2, 2]) > 0
        return X, Y, ok
    def render(self, G, W, H, phase, cam=None, dofk=0.0, px=1.0, blur_bits=0.0, bit_scale=1.0, ylo=-1e9, yhi=1e9, width=BAND_W,
               ticks=None, hi_boost=None, xoff=0.0, fade_edge=1.5):
        """返回 (level, alpha, tick) 三张图。
           phase：比特串沿 +y 移动了多少 mm；bit_scale：一位的长度倍数（速度翻倍 = 0.5）；blur_bits：信号变糊的程度（位）；
           ylo / yhi：只亮这一段（铺开用）；ticks = dict(phase=mm, scale=位长倍数, half=横向半长 mm, thick=mm)；
           hi_boost = (y_a, y_b, 强度)：这一段额外提亮（数拍用）。"""
        X, Y, ok = self.world(G, W, H)
        # 一个像素在板面上的大小（横向、纵向），用相邻像素的差近似
        fy = np.abs(np.gradient(Y, axis=0)) + np.abs(np.gradient(Y, axis=1)); fx = np.abs(np.gradient(X, axis=0)) + np.abs(np.gradient(X, axis=1))
        box = ok & (np.abs(X - xoff) < 2.5) & (Y > ylo - 3) & (Y < yhi + 3) & (fy < 20)
        ys, xs = np.where(box)
        lvl = np.zeros((H, W), np.float32); al = np.zeros((H, W), np.float32); tk = np.zeros((H, W), np.float32)
        if len(ys) == 0: return lvl, al, tk
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        Xc, Yc, fxc, fyc, okc = X[y0:y1, x0:x1] - xoff, Y[y0:y1, x0:x1], fx[y0:y1, x0:x1], fy[y0:y1, x0:x1], box[y0:y1, x0:x1]
        coc = np.zeros_like(Xc)
        if cam is not None and dofk:
            (cx, cy, cz), (tx, ty, tz) = cam; d = np.sqrt((Xc - cx) ** 2 + (Yc - cy) ** 2 + cz ** 2); df = np.sqrt((tx - cx) ** 2 + (ty - cy) ** 2 + (tz - cz) ** 2)
            coc = dofk * px * np.abs(d - df) / d                                   # 弥散圆半径（输出像素）
        sx = np.maximum(fxc * (0.7 + coc), 1e-4); sy = fyc * (0.7 + coc)           # 板面上的模糊量（mm）
        bl = BIT * bit_scale
        # 横向：两边软边
        a_lat = np.clip((width / 2 - np.abs(Xc)) / sx + 0.5, 0, 1)
        thin = np.clip(width / (2.0 * sx), 0, 1)                                    # 光带比模糊圈还细时整体变淡
        a_lat = a_lat * np.maximum(thin, 0.25) if dofk else a_lat
        # 纵向：查表
        pos = ((Yc - phase) / bl) % self.n
        row = self.level_rows(np.sqrt((sy / bl) ** 2 + blur_bits ** 2) * 0.6)
        L = cv2.remap(self.T, (pos * self.sub).astype(np.float32), row, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        vis = np.clip((Yc - ylo) / np.maximum(sy, 0.02) + 0.5, 0, 1) * np.clip((yhi - Yc) / np.maximum(sy, 0.02) + 0.5, 0, 1) * okc
        if hi_boost is not None:
            ya, yb, g = hi_boost; L = L + g * np.clip((Yc - ya) / np.maximum(sy, 0.02) + 0.5, 0, 1) * np.clip((yb - Yc) / np.maximum(sy, 0.02) + 0.5, 0, 1)
        lvl[y0:y1, x0:x1] = L; al[y0:y1, x0:x1] = a_lat * vis
        if ticks:
            c = (Yc - ticks['phase']) / (BIT * ticks.get('scale', 1.0)); f = np.abs(c - np.round(c)) * BIT * ticks.get('scale', 1.0)
            th = ticks.get('thick', 0.035); t_along = np.clip((th - f) / np.maximum(sy, 1e-4) + 0.5, 0, 1) * np.clip(th * 2 / np.maximum(sy, 1e-4), 0.3, 1)
            hx = ticks.get('half', 0.42); t_lat = np.clip((hx - np.abs(Xc)) / sx + 0.5, 0, 1)
            ta, tb = ticks.get('ylo', ylo), ticks.get('yhi', yhi)
            tv = np.clip((Yc - ta) / np.maximum(sy, 0.02) + 0.5, 0, 1) * np.clip((tb - Yc) / np.maximum(sy, 0.02) + 0.5, 0, 1) * okc
            tk[y0:y1, x0:x1] = t_along * t_lat * tv
        return lvl, al, tk

# 颜色（按 B 段末帧量的，显示色）：低电平 = 暗琥珀，半透明；高电平 = 亮奶油金
E_LO = np.array([2, 63, 118], np.float32) / 255; E_HI = np.array([176, 208, 240], np.float32) / 255      # BGR
A_LO, A_HI = 0.35, 0.80

E_LO_DIM = np.array([8, 24, 40], np.float32) / 255; A_LO_DIM = 0.55     # 「暗的 0」压成深色（观众反馈：暗的 0 也是橙色，和底下的线分不清）
def comp_band(img, lvl, al, glow=0.55, gain=1.0, lo_dim=0.0):
    """把光带叠到画面上（img：float32 BGR 0–1）。高电平带一圈不大的金色辉光。"""
    elo = E_LO + (E_LO_DIM - E_LO) * lo_dim; alo = A_LO + (A_LO_DIM - A_LO) * lo_dim
    L = np.clip(lvl, 0, 1.6)[..., None]; a = (alo + (A_HI - alo) * np.clip(L, 0, 1)) * al[..., None]
    E = (elo + (E_HI - elo) * np.clip(L, 0, 1)) * (1 + 0.35 * np.clip(L - 1, 0, 1)) * gain
    out = img * (1 - a) + E * al[..., None]
    if glow:
        h, w = img.shape[:2]; src = (np.clip(L[..., 0], 0, 1.4) ** 1.5 * al)
        sm = cv2.resize(src, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
        g = cv2.GaussianBlur(sm, (0, 0), w / 4 * 0.012) * 0.6 + cv2.GaussianBlur(sm, (0, 0), w / 4 * 0.05) * 0.4
        g = cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR)[..., None]
        out = out + g * np.array([0.25, 0.62, 1.0], np.float32) * glow * gain
    return out

def calib():
    """校准：在 side 背景上画光带，和 B 段第 120 帧（3D 光带，同一个机位）比。B 段末尾 offset = −0.48 圈 → phase = 0.48 × 120 × 0.7 = 40.32 mm"""
    v = load_view('side'); k = 1080 / SW; A = np.diag([k, k, 1.0]); G = A @ v['H']
    bg = cv2.resize(cv2.imread(os.path.join(ST, VIEW_FILE['side'] + '.png')), (1080, 1920), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    ref = cv2.imread(os.path.join(HERE, 'in', 'B', '00120.png')).astype(np.float32) / 255
    b = Band(); best = None
    for K in (2, 4, 6, 9):
        lvl, al, _ = b.render(G, 1080, 1920, 40.32, cam=CAM['side'], dofk=K, px=k)
        out = comp_band(bg, lvl, al); m = (cv2.GaussianBlur(al, (0, 0), 25) > 0.02)
        e = np.abs(out - ref)[m].mean() * 255; print('K', K, 'err', round(float(e), 2))
        if best is None or e < best[0]: best = (e, K, out)
    print('view err px', v['err'], 'best K', best[1])
    cv2.imwrite(os.path.join(HERE, 'out', 'calib_side.jpg'), (np.clip(np.vstack([best[2][900:1400], ref[900:1400]]), 0, 1) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88])

if __name__ == '__main__': calib()
