# trace.py — outlines of the four reference images (user's GPT images, 2026-11-14) → assets/people/outlines.json
# The film no longer shows the photos; it draws the arm and hands itself, using these outlines as the model
# (user 11-14: 「手尽可能还是按照图片的建模来修改」, like the feet of EP.05).
import json, sys, numpy as np
from PIL import Image
from skimage import measure
src = sys.argv[1] if len(sys.argv) > 1 else "assets/people"
out = {}
def simplify(P, tol):
    return measure.approximate_polygon(P, tolerance=tol)
for key, f in [("top", "arm-top.webp"), ("open", "arm-side-open-ring.webp"), ("fist", "arm-side-fist.webp"), ("pinch", "hand-pinch.webp")]:
    im = np.array(Image.open(f"{src}/{f}"))
    a = im[:, :, 3].astype(float) / 255
    a = np.pad(a, 2)
    cs = measure.find_contours(a, 0.5)
    c = max(cs, key=len)
    P = simplify(c, 1.2)
    out[key] = {"w": im.shape[1], "h": im.shape[0], "pts": [[round(float(x) - 2, 1), round(float(y) - 2, 1)] for y, x in P]}
    # per-column extent (for the forearm tube)
    m = im[:, :, 3] > 128
    cols = {}
    for x in range(0, im.shape[1], 10):
        ys = np.where(m[:, x])[0]
        if len(ys): cols[x] = [int(ys[0]), int(ys[-1])]
    out[key]["cols"] = cols
    print(key, len(c), "->", len(P), "points")
json.dump(out, open(f"{src}/outlines.json", "w"))
