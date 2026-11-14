# parts.py — the sleeve (grey, unsaturated) of the side images and the ring (dark) → outlines in image px
import json, numpy as np
from PIL import Image
from skimage import measure, morphology
src = "assets/people"; O = json.load(open(f"{src}/outlines.json"))
for key, f in [("open", "arm-side-open-ring.webp"), ("fist", "arm-side-fist.webp")]:
    im = np.array(Image.open(f"{src}/{f}")).astype(float); R, G, B, A = [im[:, :, i] for i in range(4)]
    sl = (A > 128) & (np.abs(R - B) < 28) & (R > 90) & (R < 225)
    sl = morphology.binary_opening(sl, morphology.disk(4)); lab = measure.label(sl)
    reg = max(measure.regionprops(lab), key=lambda r: r.area)
    c = max(measure.find_contours(np.pad((lab == reg.label).astype(float), 1), 0.5), key=len)
    O[key]["sleeve"] = [[float(x - 1), float(y - 1)] for y, x in measure.approximate_polygon(c, 1.5)]
    if key == "open":
        rg = (A > 128) & (R < 90) & (G < 90) & (B < 90)
        rg = morphology.binary_opening(rg, morphology.disk(2)); lab = measure.label(rg)
        reg = max(measure.regionprops(lab), key=lambda r: r.area)
        c = max(measure.find_contours(np.pad((lab == reg.label).astype(float), 1), 0.5), key=len)
        O[key]["ring"] = [[float(x - 1), float(y - 1)] for y, x in measure.approximate_polygon(c, 1.0)]
        print("ring bbox", reg.bbox)
    print(key, "sleeve", len(O[key]["sleeve"]), "bbox", reg.bbox)
json.dump(O, open(f"{src}/outlines.json", "w"))
