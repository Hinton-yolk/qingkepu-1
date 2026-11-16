"""Comparison package for the S04 LTX test.
  python3 compare.py out/ltx/s04_ltx_3keys.mp4
Writes deliver/: synchronized 3-panel video (V1.1 blockout | clay layout | LTX), keyframe grid, frame grid,
metrics.txt (keyframe fidelity, frame-to-frame change, edge agreement with the clay layout)."""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
LTX = sys.argv[1]
D = os.path.join(HERE, 'deliver')
T = os.path.join(HERE, 'out', 'cmp')
os.makedirs(D, exist_ok=True)
for sub in ('ltx', 'blk'):
    os.makedirs(os.path.join(T, sub), exist_ok=True)
BLK = os.path.join(HERE, '..', 'lightpath_blockout_v1.1', 'out', 'frames')       # V1.1 30 fps frames (global)
CLAY = os.path.join(HERE, 'out', 'clay_png')


def ff(args):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + args, check=True)


ff(['-i', LTX, '-vsync', '0', os.path.join(T, 'ltx', 'l%03d.png')])
n = len(os.listdir(os.path.join(T, 'ltx')))
print('LTX frames', n)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
    fsm = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
except OSError:
    font = fsm = ImageFont.load_default()
W, H = 360, 636


def blk_frame(k):        # V1.1 blockout frame nearest to LTX frame k (S04 local 1 + k*149/120)
    g = 451 + round(k * 149 / 120)
    return os.path.join(BLK, f'f{g:04d}.png')


def g(p):
    return np.asarray(Image.open(p).convert('L').resize((272, 480)), np.float32)


def edges(a):
    im = Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.FIND_EDGES)
    e = np.asarray(im, np.float32)
    return e > np.percentile(e, 90)


diffs, agree = [], []
prev = None
for k in range(n):
    l = os.path.join(T, 'ltx', f'l{k + 1:03d}.png')
    c = os.path.join(CLAY, f'c{k:03d}.png')
    panels = [(blk_frame(k), 'V1.1 blockout'), (c, 'clay (LTX layout input)'), (l, 'LTX output')]
    row = Image.new('RGB', (W * 3 + 20, H + 50), (15, 15, 15))
    dr = ImageDraw.Draw(row)
    for i, (p, nm) in enumerate(panels):
        row.paste(Image.open(p).convert('RGB').resize((W, H), Image.LANCZOS), (i * (W + 10), 50))
        dr.text((i * (W + 10) + 6, 12), nm, fill=(235, 235, 235), font=fsm)
    dr.text((W * 3 - 120, 12), f'{k / 24:4.2f}s', fill=(235, 235, 235), font=fsm)
    row.save(os.path.join(T, 'blk', f'r{k:03d}.png'))
    a = g(l)
    if prev is not None:
        diffs.append(np.abs(a - prev).mean())
    prev = a
    ea, ec = edges(a), edges(g(c))
    # tolerant edge agreement: an LTX edge pixel counts if a clay edge lies within 3 px
    ecd = np.asarray(Image.fromarray((ec * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 0
    agree.append((ea & ecd).sum() / max(ea.sum(), 1))
ff(['-framerate', '24', '-i', os.path.join(T, 'blk', 'r%03d.png'), '-frames:v', str(n), '-vf',
    'pad=ceil(iw/2)*2:ceil(ih/2)*2', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-an',
    os.path.join(D, 'S04_compare_blockout_clay_ltx.mp4')])

# keyframe fidelity: LTX frame vs the GPT keyframe it was conditioned on
kf = {0: 'kf_first.png', 72: 'kf_mid.png', 120: 'kf_last.png'}
kfd = {}
G = Image.new('RGB', (W * 3 + 20, (H + 50) * 2), (15, 15, 15))
dg = ImageDraw.Draw(G)
for i, (k, f) in enumerate(kf.items()):
    a = g(os.path.join(HERE, 'in', f))
    b = g(os.path.join(T, 'ltx', f'l{k + 1:03d}.png'))
    kfd[k] = np.abs(a - b).mean()
    G.paste(Image.open(os.path.join(HERE, 'in', f)).convert('RGB').resize((W, H)), (i * (W + 10), 50))
    G.paste(Image.open(os.path.join(T, 'ltx', f'l{k + 1:03d}.png')).convert('RGB').resize((W, H)),
            (i * (W + 10), H + 100))
    dg.text((i * (W + 10) + 6, 12), f'GPT keyframe @ LTX frame {k}', fill=(235, 235, 235), font=fsm)
    dg.text((i * (W + 10) + 6, H + 62), f'LTX frame {k} ({k / 24:.2f}s)', fill=(235, 235, 235), font=fsm)
G.save(os.path.join(D, 'S04_keyframes_vs_ltx.jpg'), quality=88)

# representative frames: beginning / middle / end and the in-betweens
ks = [0, 24, 48, 72, 96, 120]
R = Image.new('RGB', (len(ks) * (W // 1.5 + 6).__int__(), int(H / 1.5) * 2 + 80), (15, 15, 15))
w2, h2 = int(W / 1.5), int(H / 1.5)
dr = ImageDraw.Draw(R)
for i, k in enumerate(ks):
    R.paste(Image.open(os.path.join(CLAY, f'c{k:03d}.png')).convert('RGB').resize((w2, h2)), (i * (w2 + 6), 40))
    R.paste(Image.open(os.path.join(T, 'ltx', f'l{k + 1:03d}.png')).convert('RGB').resize((w2, h2)),
            (i * (w2 + 6), h2 + 80))
    dr.text((i * (w2 + 6) + 4, 10), f'clay {k / 24:.2f}s', fill=(235, 235, 235), font=fsm)
    dr.text((i * (w2 + 6) + 4, h2 + 50), f'LTX {k / 24:.2f}s', fill=(235, 235, 235), font=fsm)
R.save(os.path.join(D, 'S04_frames_clay_vs_ltx.jpg'), quality=88)

d = np.array(diffs)
with open(os.path.join(D, 'metrics.txt'), 'w') as fh:
    fh.write(f'LTX frames {n}\n')
    fh.write('mean |LTX - GPT keyframe| (0-255 grey, 272x480): ' +
             ', '.join(f'frame {k}: {v:.1f}' for k, v in kfd.items()) + '\n')
    fh.write(f'frame-to-frame change: median {np.median(d):.2f}, p95 {np.percentile(d, 95):.2f}, max {d.max():.2f} '
             f'at frame {int(d.argmax()) + 1}\n')
    big = [i + 1 for i, x in enumerate(d) if x > 3 * np.median(d) and x > 4]
    fh.write(f'frames with change > 3x median (possible jumps/flicker): {big}\n')
    ag = np.array(agree)
    fh.write(f'edge agreement with clay (share of LTX edges within 3 px of a clay edge): mean {ag.mean():.2f}, '
             f'min {ag.min():.2f} at frame {int(ag.argmin())}; per 0.5 s: '
             + ', '.join(f'{ag[i:i + 12].mean():.2f}' for i in range(0, n, 12)) + '\n')
print(open(os.path.join(D, 'metrics.txt')).read())
