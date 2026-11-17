"""S04 V2 comparison package.
  python3 compare_v2.py <V2 LTX mp4>
Writes deliver/: synchronized 3-panel (V1 LTX | V2 clay | V2 LTX), defect strips for A / B / C, keyframe check,
metrics_v2.txt (same metrics as V1's compare.py, for V1 and V2 side by side)."""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = sys.argv[1]
V1_FR = os.path.join(HERE, '..', 'lightpath_ltx_s04_poc', 'out', 'cmp', 'ltx')       # l001.png … (V1 LTX)
V1_CLAY = os.path.join(HERE, '..', 'lightpath_ltx_s04_poc', 'out', 'clay_png_run1')
CLAY = os.path.join(HERE, 'out', 'clay_png')
D = os.path.join(HERE, 'deliver')
T = os.path.join(HERE, 'out', 'cmp')
for sub in ('v2', 'row'):
    os.makedirs(os.path.join(T, sub), exist_ok=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', V2, '-vsync', '0', os.path.join(T, 'v2', 'l%03d.png')],
               check=True)
n = len(os.listdir(os.path.join(T, 'v2')))
f22 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
f18 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
W, H = 360, 636
v1 = lambda k: os.path.join(V1_FR, f'l{k + 1:03d}.png')
v2 = lambda k: os.path.join(T, 'v2', f'l{k + 1:03d}.png')
cl = lambda k: os.path.join(CLAY, f'c{k:03d}.png')

for k in range(n):
    row = Image.new('RGB', (W * 3 + 20, H + 50), (15, 15, 15))
    dr = ImageDraw.Draw(row)
    for i, (p, nm) in enumerate(((v1(k), 'V1 LTX (3 keys)'), (cl(k), 'V2 clay (layout)'), (v2(k), 'V2 LTX (4 keys)'))):
        row.paste(Image.open(p).convert('RGB').resize((W, H), Image.LANCZOS), (i * (W + 10), 50))
        dr.text((i * (W + 10) + 6, 12), nm, fill=(235, 235, 235), font=f22)
    dr.text((W * 3 - 90, 12), f'{k / 24:4.2f}s', fill=(255, 210, 120), font=f22)
    row.save(os.path.join(T, 'row', f'r{k:03d}.png'))
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(T, 'row', 'r%03d.png'),
                '-frames:v', str(n), '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2', '-c:v', 'libx264', '-crf', '18',
                '-pix_fmt', 'yuv420p', '-an', os.path.join(D, 'S04_compare_V1ltx_V2clay_V2ltx.mp4')], check=True)

# defect strips: rows V1 LTX / V2 clay / V2 LTX at the same timestamps
defects = {'A_0.8-1.1s_cable_into_tray': [19, 21, 23, 25, 27],
           'B_3.7-4.3s_server_panels': [89, 92, 95, 98, 101, 103],
           'C_4.3-4.7s_cable_near_receiver': [104, 106, 108, 110, 112]}
w2, h2 = 240, 424
for name, ks in defects.items():
    S = Image.new('RGB', (len(ks) * (w2 + 6) + 120, 3 * (h2 + 30) + 10), (15, 15, 15))
    d = ImageDraw.Draw(S)
    for r, (fn, lab) in enumerate(((v1, 'V1 LTX'), (cl, 'V2 clay'), (v2, 'V2 LTX'))):
        d.text((6, r * (h2 + 30) + h2 // 2), lab, fill=(255, 210, 120), font=f18)
        for i, k in enumerate(ks):
            x = 120 + i * (w2 + 6)
            S.paste(Image.open(fn(k)).convert('RGB').resize((w2, h2), Image.LANCZOS), (x, r * (h2 + 30) + 28))
            d.text((x + 4, r * (h2 + 30) + 4), f'{k / 24:.2f}s', fill=(235, 235, 235), font=f18)
    S.save(os.path.join(D, f'defect_{name}.jpg'), quality=88)

# keyframes vs V2 LTX
kf = {0: 'kf_first.png', 72: 'kf_mid.png', 96: 'kf_96.png', 120: 'kf_last.png'}
G = Image.new('RGB', (4 * (w2 + 6), 2 * (h2 + 30)), (15, 15, 15))
dg = ImageDraw.Draw(G)
for i, (k, f) in enumerate(kf.items()):
    G.paste(Image.open(os.path.join(HERE, 'in', f)).convert('RGB').resize((w2, h2)), (i * (w2 + 6), 28))
    G.paste(Image.open(v2(k)).convert('RGB').resize((w2, h2)), (i * (w2 + 6), h2 + 58))
    dg.text((i * (w2 + 6) + 4, 4), f'photo @ {k}', fill=(235, 235, 235), font=f18)
    dg.text((i * (w2 + 6) + 4, h2 + 34), f'V2 LTX {k / 24:.2f}s', fill=(235, 235, 235), font=f18)
G.save(os.path.join(D, 'S04_V2_keyframes_vs_ltx.jpg'), quality=88)


def g(p):
    return np.asarray(Image.open(p).convert('L').resize((272, 480)), np.float32)


def edges(a):
    e = np.asarray(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.FIND_EDGES), np.float32)
    return e > np.percentile(e, 90)


def stats(fr, clay):
    diffs, agree, prev = [], [], None
    for k in range(n):
        a = g(fr(k))
        if prev is not None:
            diffs.append(np.abs(a - prev).mean())
        prev = a
        ea, ec = edges(a), edges(g(clay(k)))
        ecd = np.asarray(Image.fromarray((ec * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 0
        agree.append((ea & ecd).sum() / max(ea.sum(), 1))
    return np.array(diffs), np.array(agree)


with open(os.path.join(D, 'metrics_v2.txt'), 'w') as fh:
    for lab, fr, clay in (('V1', v1, lambda k: os.path.join(V1_CLAY, f'c{k:03d}.png')), ('V2', v2, cl)):
        d, ag = stats(fr, clay)
        big = [i + 1 for i, x in enumerate(d) if x > 3 * np.median(d) and x > 4]
        fh.write(f'{lab}: frame-to-frame change median {np.median(d):.2f}, p95 {np.percentile(d, 95):.2f}, '
                 f'max {d.max():.2f} at frame {int(d.argmax()) + 1}; jumps >3x median: {big}\n')
        fh.write(f'{lab}: edge agreement with its own clay: mean {ag.mean():.2f}, min {ag.min():.2f} at frame '
                 f'{int(ag.argmin())}; windows A(19-27) {ag[19:28].mean():.2f}, B(89-103) {ag[89:104].mean():.2f}, '
                 f'C(104-113) {ag[104:114].mean():.2f}\n')
    kd = {k: np.abs(g(os.path.join(HERE, 'in', f)) - g(v2(k))).mean() for k, f in kf.items()}
    fh.write('V2 |LTX - photo| at keyframes: ' + ', '.join(f'{k}: {v:.1f}' for k, v in kd.items()) + '\n')
print(open(os.path.join(D, 'metrics_v2.txt')).read())
