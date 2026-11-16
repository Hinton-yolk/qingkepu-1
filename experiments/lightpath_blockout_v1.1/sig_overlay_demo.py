"""Signal-only overlay test (V1.1, task 4B). Builds a straight-alpha RGBA signal layer from two Workbench passes,
composites it over a hardware-only plate, and shows what happens when the plate geometry drifts (as an LTX render will).

Render the passes first (global frames a..b), from this directory:
  blender -b --factory-startup --python-exit-code 1 --python build_scene_v11.py -- sig_color 341 380
  blender -b --factory-startup --python-exit-code 1 --python build_scene_v11.py -- sig_cov   341 380
  blender -b --factory-startup --python-exit-code 1 --python build_scene_v11.py -- plate     341 380
then:
  python3 sig_overlay_demo.py 341 380 S03
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
a, b, tag = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
O = os.path.join(HERE, 'out')
D = os.path.join(HERE, 'deliver_v1.1', 'signal_overlay_demo')
os.makedirs(os.path.join(D, 'rgba'), exist_ok=True)
os.makedirs(os.path.join(O, 'demo_panels'), exist_ok=True)


def lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), np.float32) / 255.0


try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
except OSError:
    font = ImageFont.load_default()
H, W = 1280, 720
yy, xx = np.mgrid[0:H, 0:W]
checker = np.where(((yy // 24 + xx // 24) % 2) == 0, 0.32, 0.22)[..., None].repeat(3, 2)
errs, errs_drift = [], []
for f in range(a, b + 1):
    col = lin(load(os.path.join(O, 'sig_color', f'f{f:04d}.png')))      # premultiplied signal colour, linear
    cov = lin(load(os.path.join(O, 'sig_cov', f'f{f:04d}.png')))[..., :1]  # coverage (alpha), linear
    alpha = np.clip(cov, 0, 1)
    straight = np.where(alpha > 1e-4, col / np.maximum(alpha, 1e-4), 0)
    rgba = np.concatenate([srgb(straight), alpha], 2)
    Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), 'RGBA').save(
        os.path.join(D, 'rgba', f'{tag}_F{f - (int(tag[1:]) - 1) * 150:03d}_signals_rgba.png'))
    plate = lin(load(os.path.join(O, 'plate', f'f{f:04d}.png')))
    comp = col + plate * (1 - alpha)                                     # premultiplied "over", in linear light
    ref = lin(load(os.path.join(HERE, 'out', 'frames', f'f{f:04d}.png')))   # the normal V1.1 render (with signals)
    errs.append(np.abs(srgb(comp) - srgb(ref)).mean() * 255)
    # simulated LTX drift: plate scaled up 1.5 % about the centre and shifted 6 px right, 4 px down
    pim = Image.fromarray((srgb(plate) * 255 + .5).astype(np.uint8))
    s = 1.015
    pim = pim.resize((int(W * s), int(H * s)), Image.BICUBIC)
    ox, oy = (pim.width - W) // 2 - 6, (pim.height - H) // 2 - 4
    drift = lin(np.asarray(pim.crop((ox, oy, ox + W, oy + H)), np.float32) / 255)
    comp_d = col + drift * (1 - alpha)
    errs_drift.append(np.abs(srgb(comp_d) - srgb(ref)).mean() * 255)
    panels = [srgb(plate), srgb(straight) * alpha + checker * (1 - alpha), srgb(comp), srgb(comp_d)]
    names = ['1 plate (hardware only)', '2 signal layer (RGBA)', '3 plate + signals', '4 drifted plate + signals']
    row = Image.new('RGB', (W * 4 + 30, H + 44), (20, 20, 20))
    dr = ImageDraw.Draw(row)
    for k, (im, nm) in enumerate(zip(panels, names)):
        row.paste(Image.fromarray((np.clip(im, 0, 1) * 255 + .5).astype(np.uint8)), (k * (W + 10), 44))
        dr.text((k * (W + 10) + 8, 10), nm, fill=(235, 235, 235), font=font)
    row = row.resize((row.width // 2, row.height // 2), Image.LANCZOS)
    row.save(os.path.join(O, 'demo_panels', f'p{f:04d}.png'))
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-start_number', str(a), '-i',
                os.path.join(O, 'demo_panels', 'p%04d.png'), '-frames:v', str(b - a + 1), '-vf',
                'pad=ceil(iw/2)*2:ceil(ih/2)*2', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-an',
                os.path.join(D, f'{tag}_overlay_demo_4panel.mp4')], check=True)
Image.open(os.path.join(O, 'demo_panels', f'p{(a + b) // 2:04d}.png')).save(
    os.path.join(D, f'{tag}_overlay_demo_4panel_mid.jpg'), quality=88)
with open(os.path.join(D, 'metrics.txt'), 'w') as fh:
    fh.write(f'{tag} global frames {a}-{b}\n')
    fh.write(f'plate+signals vs normal render: mean |diff| {np.mean(errs):.2f} / 255 (max per frame {np.max(errs):.2f})\n')
    fh.write(f'drifted plate (1.5% scale, 6/4 px shift)+signals vs normal render: mean |diff| {np.mean(errs_drift):.2f} / 255\n')
print(open(os.path.join(D, 'metrics.txt')).read())
