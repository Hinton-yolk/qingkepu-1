# creases.py — the dark lines inside each reference image (finger gaps, knuckle folds, nail edges) → polylines in image px
import json, sys, numpy as np
from PIL import Image, ImageDraw
from skimage import filters, morphology, measure
src = "assets/people"; O = json.load(open(f"{src}/outlines.json"))
files = {"top": "arm-top.webp", "open": "arm-side-open-ring.webp", "fist": "arm-side-fist.webp", "pinch": "hand-pinch.webp"}
for key, f in files.items():
    im = np.array(Image.open(f"{src}/{f}")).astype(float)
    a = im[:, :, 3] / 255; L = (0.3 * im[:, :, 0] + 0.59 * im[:, :, 1] + 0.11 * im[:, :, 2]) / 255
    inner = morphology.binary_erosion(a > 0.5, morphology.disk(9))
    r = filters.sato(L, sigmas=[2, 3, 4], black_ridges=True)
    r[~inner] = 0
    thr = np.percentile(r[inner], 97.5)
    sk = morphology.skeletonize(morphology.remove_small_objects(r > thr, 60))
    lab = measure.label(sk, connectivity=2)
    lines = []
    for reg in measure.regionprops(lab):
        if reg.area < 35: continue
        ys, xs = reg.coords[:, 0], reg.coords[:, 1]
        # order the pixels along the main axis, then simplify
        d = np.array([xs - xs.mean(), ys - ys.mean()]); u, s_, vt = np.linalg.svd(d, full_matrices=False)
        o = np.argsort(u[:, 0] @ d); P = np.stack([ys[o], xs[o]], 1).astype(float)
        P = measure.approximate_polygon(P, 2.0)
        lines.append({"pts": [[float(x), float(y)] for y, x in P], "w": float(np.median(r[ys, xs]) / thr)})
    O[key]["creases"] = lines
    vis = Image.open(f"{src}/{f}").convert("RGBA"); bg = Image.new("RGBA", vis.size, (236, 235, 230, 255)); bg.alpha_composite(vis); dr = ImageDraw.Draw(bg)
    for l in lines: dr.line([tuple(p) for p in l["pts"]], fill=(255, 0, 80, 255), width=3)
    bg.convert("RGB").save(f"qa/creases-{key}.jpg", quality=80)
    print(key, len(lines), "lines")
json.dump(O, open(f"{src}/outlines.json", "w"))
