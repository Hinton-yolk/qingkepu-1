"""Builds the delivery package from out/frames/f0001..f0900.png (run after `build_scene.py -- anim`).
   python3 package.py
Writes deliver/: master mp4, six shot mp4s, reference frames, contact sheet, sha256 list."""
import hashlib
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.join(HERE, 'out', 'frames')
D = os.path.join(HERE, 'deliver')
SHOTS = [('S01', 'departure'), ('S02', 'electrical'), ('S03', 'modulation'),
         ('S04', 'fiber'), ('S05', 'reception'), ('S06', 'arrival')]
HERO = {'S01': 110, 'S02': 75, 'S03': 80, 'S04': 100, 'S05': 70, 'S06': 100}   # principal-action local frames
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
   + [os.path.join(D, 'lightpath_blockout_30s.mp4')])
for i, (s, n) in enumerate(SHOTS):
    ff(['-framerate', '30', '-start_number', str(i * 150 + 1), '-i', os.path.join(FR, 'f%04d.png'),
        '-frames:v', '150'] + X264 + [os.path.join(D, 'shots', f'{s}_{n}.mp4')])
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
d.text((10, 10), 'PROJECT LIGHTPATH — 30 s Blender blockout V1.0 · contact sheet (local frame / global time)',
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
S.save(os.path.join(D, 'contact_sheet_30s.jpg'), quality=88)

with open(os.path.join(D, 'SHA256SUMS.txt'), 'w') as fh:
    for root, _, files in os.walk(D):
        for f in sorted(files):
            if f == 'SHA256SUMS.txt':
                continue
            p = os.path.join(root, f)
            fh.write(f'{hashlib.sha256(open(p, "rb").read()).hexdigest()}  {os.path.relpath(p, D)}\n')
print('done')
