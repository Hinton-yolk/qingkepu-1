"""Direction B: the Wi-Fi field over the whole plate, as a texture the projector throws (static frame, t0).
Every building with routers is a source; rings of a stylised wavelength (shown as 示意 on screen) spread from it,
summed incoherently and attenuated by the buildings the signal must cross. Also finds 'the hole': the largest open
patch with no building (no building = no router = no light)."""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, gaussian_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
key = sys.argv[1] if len(sys.argv) > 1 else 'B'
M = json.load(open(os.path.join(ROOT, 'data', key, 'model.json')))
ST = json.load(open(os.path.join(ROOT, 'data', key, 'stats.json')))
PW = M['size'][0]                       # plate width in model metres
N = 2048
px = PW / N                             # model metres per pixel
real = lambda m: m * 1000.0

# footprint mask (for the hole and for attenuation)
mask = Image.new('L', (N, N), 0); d = ImageDraw.Draw(mask)
to_px = lambda x, z: ((x / PW + .5) * N, (z / PW + .5) * N)
cent = {}
for bi, h, rings in M['p']:
    d.polygon([to_px(x, z) for x, z in rings[0]], fill=255)
    r = np.array(rings[0]); cent.setdefault(bi, r.mean(0))
mask = np.array(mask) > 0

# sources: building centroids weighted by estimated routers
src = [(cent[bi], M['b'][bi][2]) for bi in cent if M['b'][bi][2] > 0]
F = np.zeros((N, N), np.float32)
R = int(110.0 / 1000 / px)              # each source reaches ~110 m
yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
rr = np.sqrt(xx * xx + yy * yy).astype(np.float32)
fall = 1.0 / (1.0 + rr / (18.0 / 1000 / px)) * (rr <= R)
rng = np.random.default_rng(7)
big = sorted(n for _, n in src)[-40]                     # only the ~40 biggest blocks throw visible rings
lam = 24.0 / 1000 / px
for (cx, cz), n in src:
    ph = rng.uniform(0, 2 * math.pi)
    crest = (0.5 + 0.5 * np.cos(2 * math.pi * rr / lam + ph)) ** 4
    if n >= big:
        K = math.sqrt(n) * 0.06 * fall * (0.04 + 0.96 * crest) * 1.6
    else:
        K = math.sqrt(n) * 0.05 * fall * 0.38          # houses: a low, steady glow
    i, j = int((cz / PW + .5) * N), int((cx / PW + .5) * N)
    y0, y1, x0, x1 = max(0, i - R), min(N, i + R + 1), max(0, j - R), min(N, j + R + 1)
    F[y0:y1, x0:x1] += K[y0 - (i - R):y1 - (i - R), x0 - (j - R):x1 - (j - R)]
F = 1 - np.exp(-F * 0.95)               # tone map 0..1
F = gaussian_filter(F, 0.8)
Image.fromarray((np.clip(F, 0, 1) * 255).astype(np.uint8)).save(os.path.join(ROOT, 'data', key, 'wifi.png'))

# the hole: the open point farthest from any building, away from the plate edge
dist = distance_transform_edt(~mask) * px * 1000      # metres
m = int(N * 0.18)
inner = np.zeros_like(dist); inner[m:-m, m:-m] = dist[m:-m, m:-m]
i, j = np.unravel_index(np.argmax(inner), inner.shape)
hole = dict(x=round((j / N - .5) * PW, 5), z=round((i / N - .5) * PW, 5), radius_m=round(float(inner[i, j]), 1))
ST['hole'] = hole
ST['field'] = dict(ring_m=24, reach_m=110, note='示意：环距与传播被放大')
json.dump(ST, open(os.path.join(ROOT, 'data', key, 'stats.json'), 'w'), ensure_ascii=False, indent=1)
print(key, 'field written; hole at', hole, '; sources', len(src))
