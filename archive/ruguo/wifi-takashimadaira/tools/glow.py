"""The estate's Wi-Fi as a soft ground glow (no rings): every building with routers is a source, weighted by
sqrt(estimated routers), falling off over ~110 m. Thrown by the projector once the whole estate is on (main.js uGlow).
out: data/A/glow.png (plate-sized, 1024², R = glow 0..1)"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(ROOT, 'data', 'A', 'model.json')))
PW, N = M['size'][0], 1024
px = PW / N * 1000                       # real metres per pixel
cent = {}
for bi, h, rings in M['p']:
    cent.setdefault(bi, []).append(np.array(rings[0]).mean(0))
F = np.zeros((N, N), np.float32)
R = int(110 / px)
yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
rr = np.sqrt(xx * xx + yy * yy) * px
fall = (1 / (1 + rr / 18.0) * (rr <= 110)).astype(np.float32)
for bi, cs in cent.items():
    n = M['b'][bi][2]
    if n <= 0: continue
    cx, cz = np.mean(cs, 0)
    i, j = int((cz / PW + .5) * N), int((cx / PW + .5) * N)
    y0, y1, x0, x1 = max(0, i - R), min(N, i + R + 1), max(0, j - R), min(N, j + R + 1)
    F[y0:y1, x0:x1] += math.sqrt(n) * 0.05 * fall[y0 - (i - R):y1 - (i - R), x0 - (j - R):x1 - (j - R)]
F = 1 - np.exp(-F * 0.9)
F = gaussian_filter(F, 1.2)
Image.fromarray((np.clip(F, 0, 1) * 255).astype(np.uint8)).save(os.path.join(ROOT, 'data', 'A', 'glow.png'))
print('glow', F.min(), F.max(), F.mean())
