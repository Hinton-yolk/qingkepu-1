"""V1.1 delivery package from out/frames/f0001..f0900.png (run after `build_scene_v11.py -- anim`).
   python3 package_v11.py
Writes deliver_v1.1/: master + six shot mp4s, 18 reference frames, full-film contact sheet,
one contact sheet per shot, five transition comparisons, sha256 list."""
import hashlib
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.join(HERE, 'out', 'frames')
D = os.path.join(HERE, 'deliver_v1.1')
SHOTS = [('S01', 'departure'), ('S02', 'electrical'), ('S03', 'modulation'),
         ('S04', 'fiber'), ('S05', 'reception'), ('S06', 'arrival')]
HERO = {'S01': 55, 'S02': 75, 'S03': 75, 'S04': 90, 'S05': 70, 'S06': 100}   # principal-action local frames
os.makedirs(os.path.join(D, 'shots'), exist_ok=True)
os.makedirs(os.path.join(D, 'reference_frames'), exist_ok=True)
missing = [f for f in range(1, 901) if not os.path.exists(os.path.join(FR, f'f{f:04d}.png'))]
if missing:
    sys.exit(f'missing frames: {missing[:10]}… ({len(missing)})')

X264 = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-an', '-r', '30',
        '-movflags', '+faststart']


def ff(args):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + args, check=True)


ff(['-framerate', '30', '-start_number', '1', '-i', os.path.join(FR, 'f%04d.png'), '-frames:v', '900'] + X264
   + [os.path.join(D, 'lightpath_blockout_30s_v1.1.mp4')])
for i, (s, n) in enumerate(SHOTS):
    ff(['-framerate', '30', '-start_number', str(i * 150 + 1), '-i', os.path.join(FR, 'f%04d.png'),
        '-frames:v', '150'] + X264 + [os.path.join(D, 'shots', f'{s}_{n}_v1.1.mp4')])
    for lf in (1, HERO[s], 150):
        src = os.path.join(FR, f'f{i * 150 + lf:04d}.png')
        tag = 'first' if lf == 1 else ('last' if lf == 150 else 'hero')
        Image.open(src).save(os.path.join(D, 'reference_frames', f'{s}_F{lf:03d}_{tag}.png'))

# contact sheet: one row per shot, local frames 1, 30, 60, 90, 120, 150 (+ hero marked)
cols = [1, 30, 60, 90, 120, 150]
tw, th = 200, 356
pad, head = 6, 22
W = 120 + len(cols) * (tw + pad)
H = 40 + len(SHOTS) * (th + head + pad)
S = Image.new('RGB', (W, H), (245, 245, 245))
d = ImageDraw.Draw(S)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    fontb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
except OSError:
    font = fontb = ImageFont.load_default()
d.text((10, 10), 'PROJECT LIGHTPATH — 30 s Blender blockout V1.1 · contact sheet (local frame / global time)',
       fill=(0, 0, 0), font=fontb)
for r, (s, n) in enumerate(SHOTS):
    y = 40 + r * (th + head + pad)
    d.text((10, y + head + th // 2 - 20), f'{s}\n{n}', fill=(0, 0, 0), font=fontb)
    for c, lf in enumerate(cols):
        g = r * 150 + lf
        im = Image.open(os.path.join(FR, f'f{g:04d}.png')).convert('RGB').resize((tw, th), Image.LANCZOS)
        x = 120 + c * (tw + pad)
        S.paste(im, (x, y + head))
        d.text((x + 2, y + 3), f'F{lf:03d}  {(g - 1) / 30:05.2f}s', fill=(0, 0, 0), font=font)
S.save(os.path.join(D, 'contact_sheet_30s_v1.1.jpg'), quality=88)

# one contact sheet per shot: every 15 frames (F001, F015 … F150), 2 rows
os.makedirs(os.path.join(D, 'contact_sheets_per_shot'), exist_ok=True)
for r, (s, n) in enumerate(SHOTS):
    lfs = [1] + list(range(15, 151, 15))
    tw2, th2 = 180, 320
    cols2 = 6
    rows2 = (len(lfs) + cols2 - 1) // cols2
    S2 = Image.new('RGB', (cols2 * (tw2 + pad) + pad, 36 + rows2 * (th2 + head + pad)), (245, 245, 245))
    d2 = ImageDraw.Draw(S2)
    d2.text((8, 8), f'{s} {n} · V1.1 · every 15 frames (hero F{HERO[s]:03d} marked *)', fill=(0, 0, 0), font=fontb)
    for k, lf in enumerate(lfs):
        g = r * 150 + lf
        im = Image.open(os.path.join(FR, f'f{g:04d}.png')).convert('RGB').resize((tw2, th2), Image.LANCZOS)
        x = pad + (k % cols2) * (tw2 + pad)
        y = 36 + (k // cols2) * (th2 + head + pad)
        S2.paste(im, (x, y + head))
        d2.text((x + 2, y + 3), f'F{lf:03d}  {(g - 1) / 30:05.2f}s', fill=(0, 0, 0), font=font)
    S2.save(os.path.join(D, 'contact_sheets_per_shot', f'{s}_{n}_v1.1.jpg'), quality=88)

# five transition comparisons: outgoing F150 | incoming F001, full camera frames side by side
os.makedirs(os.path.join(D, 'transitions'), exist_ok=True)
for r in range(5):
    a, b = SHOTS[r], SHOTS[r + 1]
    ia = Image.open(os.path.join(FR, f'f{r * 150 + 150:04d}.png')).convert('RGB')
    ib = Image.open(os.path.join(FR, f'f{(r + 1) * 150 + 1:04d}.png')).convert('RGB')
    T = Image.new('RGB', (ia.width * 2 + 3 * pad, ia.height + 40), (245, 245, 245))
    T.paste(ia, (pad, 40))
    T.paste(ib, (2 * pad + ia.width, 40))
    dt = ImageDraw.Draw(T)
    dt.text((pad, 10), f'{a[0]} {a[1]} F150 (out)', fill=(0, 0, 0), font=fontb)
    dt.text((2 * pad + ia.width, 10), f'{b[0]} {b[1]} F001 (in)', fill=(0, 0, 0), font=fontb)
    T.save(os.path.join(D, 'transitions', f'T{r + 1}_{a[0]}_to_{b[0]}.jpg'), quality=88)

with open(os.path.join(D, 'SHA256SUMS.txt'), 'w') as fh:
    for root, _, files in os.walk(D):
        for f in sorted(files):
            if f == 'SHA256SUMS.txt':
                continue
            p = os.path.join(root, f)
            fh.write(f'{hashlib.sha256(open(p, "rb").read()).hexdigest()}  {os.path.relpath(p, D)}\n')
print('done')
