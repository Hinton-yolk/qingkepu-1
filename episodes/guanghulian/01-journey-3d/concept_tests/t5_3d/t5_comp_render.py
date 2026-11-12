#!/usr/bin/env python3
"""T5 合成：PNG 序列 + 转场 + 叠加层 → 两份无损中间文件（静音版 / 试听版画面），再由 t5_comp_build.sh 压成最终 mp4。
用法：python3 t5_comp_render.py <帧根> <锚点目录> <输出目录> [--frames a-b] [--dump-dir DIR]
帧根下：shot1/T5S1_%06d.png（或 f%04d.png）、shot23/f%04d.png、arrive/T5ARR_%06d.png。缺帧用最近的已有帧补，并在 comp_log.txt 写出缺了哪些。"""
import sys, os, re, glob, subprocess, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t5_comp_timeline as TL
W, H, FPS = TL.W, TL.H, TL.FPS
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
_fc = {}
def font(sz):
    if sz not in _fc: _fc[sz] = ImageFont.truetype(FONT, sz)
    return _fc[sz]
CYAN = (60, 225, 240); INK = (8, 12, 22)

# ---------------- 帧源 ----------------
class Source:
    def __init__(self, root, seg, n_local, log):
        self.seg = seg; d = os.path.join(root, {'shot1': 'shot1', 'shot23': 'shot23', 'arrive': 'arrive'}[seg]); self.files = {}
        for p in glob.glob(os.path.join(d, '*.png')):
            m = re.search(r'(?:_|f)(\d{4,6})\.png$', os.path.basename(p))
            if m: self.files[int(m.group(1))] = p
        self.keys = sorted(self.files); self.n = n_local; self.cache = {}
        miss = [f for f in range(1, n_local + 1) if f not in self.files]
        if not self.keys: raise SystemExit(f'{seg} 一帧都没有：{d}')
        if miss:
            runs = []; s = miss[0]; p = miss[0]
            for f in miss[1:]:
                if f != p + 1: runs.append((s, p)); s = f
                p = f
            runs.append((s, p)); log.append(f'{seg}: 缺 {len(miss)}/{n_local} 帧（脚本内帧号 {", ".join(f"{a}-{b}" if a != b else str(a) for a, b in runs)}），用最近的已有帧补')
    def get(self, f):
        f = min(max(f, 1), self.n)
        k = f if f in self.files else min(self.keys, key=lambda x: (abs(x - f), x))
        if k not in self.cache:
            if len(self.cache) > 12: self.cache.clear()
            im = Image.open(self.files[k]).convert('RGB')
            if im.size != (W, H): im = im.resize((W, H), Image.LANCZOS)
            self.cache[k] = np.asarray(im, dtype=np.float32)
        return self.cache[k]

def base_frame(n, S):
    seg = TL.seg_of(n)
    if seg == 'shot1':                                         # 剪掉暗段：前 4 帧与段后 4 帧交叉溶解（像一次快甩）
        f, g = TL.shot1_src(n); img = S[seg].get(f)
        if g: k = (n - TL.CUT_A + 1) / (TL.CUT_XF + 1.0); img = img * (1 - k) + S[seg].get(g) * k
    else: img = S[seg].get(n - TL.OFF[seg])
    a, b = TL.SEGS['shot23']
    if a <= n < a + 6:                                           # 第 1 拍 → 第 2 拍：6 帧交叉溶解（第 1 拍末帧定格淡出，第 2 拍照常走，时间不错位）
        k = (n - a + 1) / 7.0; img = S['shot1'].get(TL.SHOT1_OLD) * (1 - k) + img * k
    a2, _ = TL.SEGS['arrive']
    if a2 <= n < a2 + 4:                                         # 第 3 拍 → 结尾：4 帧快速溶解 + 白闪
        k = (n - a2 + 1) / 5.0; img = S['shot23'].get(TL.SEGS['shot23'][1] - TL.OFF['shot23']) * (1 - k) + img * k
        w = [0.65, 0.45, 0.22, 0.08][n - a2]; img = img * (1 - w) + 255.0 * w
    return img

# ---------------- 叠加层 ----------------
def text_size(s, sz):
    l, t, r, b = font(sz).getbbox(s); return r - l, b - t
def draw_pill(frame, cx, cy, lines, sizes, colors, alpha, pad=(14, 8), bg=(8, 12, 22, 165), anchor='c', min_w=0, gap=6, radius=12, stroke=2):
    """多行文字居中放进半透明圆角底；返回 (x0,y0,x1,y1)。alpha 0..1 整体淡入淡出。"""
    if alpha <= 0.003: return None
    ws = [text_size(s, z)[0] for s, z in zip(lines, sizes)]; hs = [int(z * 1.18) for z in sizes]
    bw = max(max(ws) + 2 * pad[0], min_w); bh = sum(hs) + gap * (len(lines) - 1) + 2 * pad[1]
    x0 = int(round(cx - bw / 2)); y0 = int(round(cy - bh / 2)) if anchor == 'c' else int(round(cy))
    x0 = max(8, min(W - 8 - bw, x0)); layer = Image.new('RGBA', (bw, bh), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), radius, fill=(bg[0], bg[1], bg[2], int(bg[3] * alpha)))
    y = pad[1]
    for s, z, c, h in zip(lines, sizes, colors, hs):
        w = text_size(s, z)[0]; d.text(((bw - w) / 2 - font(z).getbbox(s)[0], y - 1), s, font=font(z), fill=(*c, int(255 * alpha)), stroke_width=stroke if stroke else 0, stroke_fill=(0, 0, 0, int(200 * alpha)))
        y += h + gap
    frame.alpha_composite(layer, (x0, y0)); return (x0, y0, x0 + bw, y0 + bh)

def glow_ring(frame, x, y, r, alpha, col=CYAN):
    if alpha <= 0.003: return
    pad = r + 24; layer = Image.new('RGBA', (pad * 2, pad * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for w, a in ((9, 40), (5, 70), (2, 190)): d.ellipse((pad - r, pad - r, pad + r, pad + r), outline=(*col, int(a * alpha)), width=w)
    frame.alpha_composite(layer, (int(x - pad), int(y - pad)))

def draw_check(d, cx, cy, s, col, w=5):
    d.line([(cx - s * 0.55, cy + s * 0.02), (cx - s * 0.15, cy + s * 0.42), (cx + s * 0.6, cy - s * 0.45)], fill=col, width=w, joint='curve')

def cells_panel(frame, t, sound):
    t0, t1 = TL.END_PANEL
    a = TL.alpha_win(t, t0, t1 + 5, 0.2)
    if a <= 0: return
    cell = 36; gap = 8; tot = 8 * cell + 7 * gap; pw = tot + 40; ph = 128 + (0 if True else 0)
    px = (W - pw) // 2; py = 205
    layer = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), 14, fill=(8, 12, 22, int(165 * a)))
    for k in range(8):
        x = 20 + k * (cell + gap); y = 18; ts = TL.CELLS_T0 + k * TL.CELLS_STEP; on = t >= ts; lit = TL.PATTERN[k]
        r = (x, y, x + cell, y + cell)
        if not on: d.rounded_rectangle(r, 6, outline=(90, 120, 140, int(120 * a)), width=2, fill=(20, 28, 40, int(150 * a))); continue
        flash = max(0.0, 1 - (t - ts) / 0.18)
        if lit:
            d.rounded_rectangle((x - 3, y - 3, x + cell + 3, y + cell + 3), 9, fill=(*CYAN, int((50 + 90 * flash) * a)))
            d.rounded_rectangle(r, 6, fill=(*CYAN, int(255 * a)), outline=(210, 255, 255, int(255 * a)), width=2)
        else:
            d.rounded_rectangle(r, 6, fill=(18, 38, 56, int(235 * a)), outline=(70, 130, 160, int((170 + 85 * flash) * a)), width=2)
    ca = TL.alpha_win(t, TL.CHECK_T, 99, 0.18)
    if ca > 0:
        label = '送到了'; fs = 34; tw = text_size(label, fs)[0]; cxm = pw / 2 - 4
        draw_check(d, cxm - tw / 2 - 20, 92, 26, (*CYAN, int(255 * ca)), w=6)
        d.text((cxm - tw / 2 + 18 - font(fs).getbbox(label)[0], 72), label, font=font(fs), fill=(255, 255, 255, int(255 * ca)), stroke_width=2, stroke_fill=(0, 0, 0, int(200 * ca)))
    frame.alpha_composite(layer, (px, py))

def overlay(img_f32, n, A, labels, sound):
    t = (n - 1) / FPS
    frame = Image.fromarray(np.clip(img_f32, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    # 角注
    for (a, b), s in TL.CORNER:
        al = TL.alpha_win(t, a + 0.1, b - 0.1, 0.3)
        if al > 0: draw_pill(frame, 16 + text_size(s, 18)[0] / 2 + 10, 58, [s], [18], [(225, 235, 240)], al, pad=(10, 4), bg=(8, 12, 22, 120), radius=8, stroke=1)
    # 开头大字
    al = TL.alpha_win(t, *TL.TITLE, 0.2, fade_in=False)
    if al > 0:
        draw_pill(frame, W / 2, 238, ['AI 芯片之间', '这串数据，', '怎么送到对面？'], [26, 46, 46], [(150, 235, 245), (255, 255, 255), (255, 255, 255)], al, pad=(22, 14), bg=(8, 12, 22, 170), anchor='t', min_w=480, gap=4, radius=16)
    # 标签
    for lb in labels:
        al = TL.alpha_win(t, lb['t0'], lb['t1'])
        if al <= 0: continue
        p = TL.anchor_at(A, lb['seg'], lb['key'], n)
        if p is None: continue
        x, y, z = p
        if lb['mode'] == 'edge':                       # 锚点不在屏幕上：贴屏幕边缘并加箭头指向它
            inside = TL.on_screen(p); ex = min(max(x, 80), W - 80); ey = min(max(y, 120), 770)
            if z <= 0: ex, ey = W / 2, 770
            ar = '▼' if (not inside and ey >= 760) else ('▲' if (not inside and ey <= 125) else '')
            r = draw_pill(frame, ex, ey - 22, [lb['text']], [22], [(255, 255, 255)], al, pad=(12, 6), anchor='c')
            if ar:
                lay = frame; d = ImageDraw.Draw(lay); cx = (r[0] + r[2]) / 2; ty = r[3] + 4 if ar == '▼' else r[1] - 4
                s = 10; pts = [(cx - s, ty), (cx + s, ty), (cx, ty + (s + 4) * (1 if ar == '▼' else -1))]
                d.polygon(pts, fill=(255, 255, 255, int(230 * al)))
            continue
        if not (TL.SAFE[0] - 10 <= x <= TL.SAFE[2] + 10 and TL.SAFE[1] - 40 <= y <= TL.SAFE[3] + 10 and z > 0): continue
        if lb['mode'] == 'ring': glow_ring(frame, x, y, 40, al)
        dy = -(52 if lb['mode'] == 'ring' else 40); lw = text_size(lb['text'], 22)[0]
        r = draw_pill(frame, x, max(110, y + dy), [lb['text']], [22], [(255, 255, 255)], al, pad=(12, 6))
        d = ImageDraw.Draw(frame); d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(*CYAN, int(255 * al)), outline=(255, 255, 255, int(255 * al)))
        if r and lb['mode'] != 'ring': d.line([(min(max(x, r[0] + 8), r[2] - 8), r[3]), (x, y - 4)], fill=(255, 255, 255, int(170 * al)), width=2)
    # 结尾八格 + ✓
    cells_panel(frame, t, sound)
    ca = TL.alpha_win(t, TL.CHECK_T, 99, 0.2)
    if ca > 0:
        p = TL.anchor_at(A, 'arrive', 'gpu_b', n)
        if p and p[2] > 0: glow_ring(frame, p[0], p[1], 46, ca * 0.9)
    # 字幕（试听版）
    if sound:
        for a, b, s in TL.SUBS:
            al = TL.alpha_win(t, a, b, 0.2)
            if al > 0:
                assert text_size(s, 24)[0] + 28 <= W - 16, s
                draw_pill(frame, W / 2, 836, [s], [24], [(255, 255, 255)], al, pad=(14, 8), bg=(0, 0, 0, 175), stroke=2)
    return np.asarray(frame.convert('RGB'))

def main():
    a = sys.argv[1:]; root, adir, out = a[0], a[1], a[2]; os.makedirs(out, exist_ok=True)
    rng = (1, TL.N_FRAMES)
    if '--frames' in a: lo, hi = a[a.index('--frames') + 1].split('-'); rng = (int(lo), int(hi))
    dump = a[a.index('--dump-dir') + 1] if '--dump-dir' in a else None
    log = []; S = {k: Source(root, k, TL.SHOT1_OLD if k == 'shot1' else TL.SEGS[k][1] - TL.SEGS[k][0] + 1, log) for k in TL.SEGS}
    A = TL.load_anchors(adir); labels = TL.resolve_labels(A)
    for lb in labels: log.append(f"标签 {lb['text']}: " + (f"{lb['t0']:.2f}–{lb['t1']:.2f} s" if lb['t0'] is not None else lb.get('note', '无')))
    procs = {}
    for name, snd in (('silent', False), ('sound', True)):
        if dump: continue
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'ultrafast', '-qp', '0', '-pix_fmt', 'yuv444p', os.path.join(out, f'lossless_{name}.mkv')]
        procs[name] = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(rng[0], rng[1] + 1):
        b = base_frame(n, S)
        for name, snd in (('silent', False), ('sound', True)):
            fr = overlay(b, n, A, labels, snd)
            if dump:
                if (n - 1) % FPS == 0 or n in dump_extra(): Image.fromarray(fr).save(os.path.join(dump, f'{name}_{n:04d}.png'))
            else: procs[name].stdin.write(fr.tobytes())
    for p in procs.values(): p.stdin.close(); p.wait()
    open(os.path.join(out, 'comp_log.txt'), 'w', encoding='utf-8').write('\n'.join(log) + '\n'); print('\n'.join(log))
def dump_extra(): return ()
if __name__ == '__main__': main()
