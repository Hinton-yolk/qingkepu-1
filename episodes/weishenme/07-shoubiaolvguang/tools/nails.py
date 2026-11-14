# nails.py — nail plates in the reference images (pinkish, bluer than skin) → outlines in image px, added to outlines.json
import json, numpy as np
from PIL import Image, ImageDraw
from skimage import measure, morphology
src = "assets/people"; O = json.load(open(f"{src}/outlines.json"))
files = {"top": "arm-top.webp", "open": "arm-side-open-ring.webp", "fist": "arm-side-fist.webp", "pinch": "hand-pinch.webp"}
for key, f in files.items():
    im = np.array(Image.open(f"{src}/{f}")).astype(float); R, G, B, A = [im[:, :, i] for i in range(4)]
    m = (A > 200) & (B / np.maximum(R, 1) > 0.66) & (R > 195) & (G / np.maximum(R, 1) > 0.72)
    m = morphology.binary_opening(m, morphology.disk(3)); m = morphology.remove_small_objects(m, 250)
    nails = []
    for reg in measure.regionprops(measure.label(m)):
        if reg.area > 12000: continue
        c = max(measure.find_contours(np.pad(reg.image, 1).astype(float), 0.5), key=len)
        P = measure.approximate_polygon(c, 1.5); y0, x0 = reg.bbox[:2]
        pts = [[float(x + x0 - 1), float(y + y0 - 1)] for y, x in P]
        cy, cx = reg.centroid; d = min(np.hypot(ox - cx, oy - cy) for ox, oy in O[key]["pts"])
        if d < {"pinch": 70, "fist": 45}.get(key, 34) and 300 < reg.area < 9000: nails.append(pts)          # only plates at the outline (fingertips), not highlights inside the hand
    O[key]["nails"] = nails
    vis = Image.open(f"{src}/{f}").convert("RGBA"); bg = Image.new("RGBA", vis.size, (236, 235, 230, 255)); bg.alpha_composite(vis); dr = ImageDraw.Draw(bg)
    for n in nails: dr.polygon([tuple(p) for p in n], outline=(0, 120, 255, 255), width=3)
    bg.convert("RGB").save(f"qa/nails-{key}.jpg", quality=80); print(key, len(nails), [len(n) for n in nails])
json.dump(O, open(f"{src}/outlines.json", "w"))
# hand-checked: keep only the real nail plates (the rest are highlights on knuckles / the thumb side)
KEEP = {"open": [0, 4, 5, 6, 7], "fist": [0], "pinch": [4, 5]}
for k, idx in KEEP.items(): O[k]["nails"] = [O[k]["nails"][i] for i in idx]
json.dump(O, open(f"{src}/outlines.json", "w"))
