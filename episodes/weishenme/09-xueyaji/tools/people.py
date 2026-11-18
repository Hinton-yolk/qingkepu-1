# people.py — the user's reference images (2026-11-18, assets/people/*.webp, GPT-generated) → assets/people/model.js.
# The film draws the people itself from these outlines (no photo is shown), like EP.05's feet and EP.07/08's hands.
#   ARM : arm-flat-palmup.webp — one whole arm lying flat, shoulder at the left edge, palm up (outline + a few creases)
#   SIDE: side-arm-{heart,raised,down}.webp — a woman sitting, profile facing right; per pose: polygons per colour class
#         (pants, shirt, skin, hair) + small face features, registered to the heart pose (same body; only the arm changes).
import json, sys, numpy as np
from PIL import Image, ImageDraw
from skimage import measure, morphology, filters

def load(src):
    im = Image.open(src)
    rgba = np.array(im.convert("RGBA")).astype(float)
    R, G, B, A = [rgba[:, :, i] for i in range(4)]
    if im.mode != "RGBA":   # a checkerboard painted in: the background is neutral grey / white
        chroma = rgba[:, :, :3].max(2) - rgba[:, :, :3].min(2); L = (0.3 * R + 0.59 * G + 0.11 * B)
        fg = (chroma > 14) | (L < 150)
        fg = morphology.remove_small_objects(morphology.binary_closing(fg, morphology.disk(3)), 5000)
        fg = morphology.remove_small_holes(fg, 4000)
        A = fg * 255.0
    return R, G, B, A

def poly(mask, tol=1.4, pad=2):
    out = []
    lab = measure.label(mask)
    for rg in measure.regionprops(lab):
        if rg.area < 200: continue
        m = lab == rg.label
        c = max(measure.find_contours(np.pad(m.astype(float), pad), 0.5), key=len)
        P = measure.approximate_polygon(c, tol)
        out.append({"area": int(rg.area), "c": [round(float(rg.centroid[1]), 1), round(float(rg.centroid[0]), 1)],
                    "pts": [[round(float(x) - pad, 1), round(float(y) - pad, 1)] for y, x in P]})
    return sorted(out, key=lambda r: -r["area"])

def creases(L, m, pct=97.5, minlen=40, keep=10):
    inner = morphology.binary_erosion(m, morphology.disk(10))
    r = filters.sato(L, sigmas=[2, 3, 4], black_ridges=True); r[~inner] = 0
    thr = np.percentile(r[inner], pct)
    sk = morphology.skeletonize(morphology.remove_small_objects(r > thr, 60))
    cl = measure.label(sk, connectivity=2); out = []
    for rg in measure.regionprops(cl):
        if rg.area < minlen: continue
        ys, xs = rg.coords[:, 0], rg.coords[:, 1]
        d = np.array([xs - xs.mean(), ys - ys.mean()]); u, s_, vt = np.linalg.svd(d, full_matrices=False)
        o = np.argsort(u[:, 0] @ d); Q = measure.approximate_polygon(np.stack([ys[o], xs[o]], 1).astype(float), 2.0)
        out.append((rg.area, [[float(x), float(y)] for y, x in Q]))
    return [q for _, q in sorted(out, key=lambda z: -z[0])[:keep]]

model = {}
# ---------------- ARM
R, G, B, A = load("assets/people/arm-flat-palmup.webp")
m = A > 128; L = (0.3 * R + 0.59 * G + 0.11 * B) / 255
P = poly(m, 1.2)[0]
model["ARM"] = {"w": m.shape[1], "h": m.shape[0], "pts": P["pts"], "creases": creases(L, m, 98.0, 50, 12)}

# ---------------- SIDE poses
CLS = {"hair": (45, 33, 28), "skin": (236, 203, 172), "shirt": (138, 147, 124), "pants": (214, 200, 184)}
names = list(CLS); cols = np.array([CLS[k] for k in names], float)
side = {}
for pose in ["heart", "raised", "down"]:
    R, G, B, A = load(f"assets/people/side-arm-{pose}.webp")
    fg = A > 128
    L = (0.3 * R + 0.59 * G + 0.11 * B) / 255
    # classes by hue (shading must stay in its class): hair = dark; shirt = greenish (G >= R); skin = warm (R−B large); pants = the rest
    k = np.full(fg.shape, -1)
    k[fg] = 3
    k[fg & (R - B > 44)] = 1
    k[fg & (G - R > -11) & (R - B < 44)] = 2
    k[fg & (L < 0.30)] = 0
    regs = {}
    for i, nm in enumerate(names):
        mk = morphology.binary_opening(k == i, morphology.disk(2))
        mk = morphology.remove_small_holes(mk, 1500)
        if nm == "hair":   # one head of hair: the largest piece, its highlights filled
            lab_ = measure.label(mk); big = max(measure.regionprops(lab_), key=lambda r: r.area).label
            mk = morphology.remove_small_holes(lab_ == big, 20000)
        regs[nm] = poly(mk, 1.4)
    skin = (k == 1)
    feats = {"dark": [], "lips": []}
    ys, xs = np.nonzero(fg); top = ys.min()
    hb = regs["hair"][0]; hx = max(p[0] for p in hb["pts"])
    face = np.zeros_like(fg); face[top: top + int(0.27 * (ys.max() - top)), :] = True
    fx0 = int(np.percentile([p[0] for p in hb["pts"]], 60))
    face[:, :fx0] = False                                   # the face: right of most of the hair
    dk = face & fg & (L < 0.42)
    lab = measure.label(dk)
    hair_lab = set(np.unique(lab[morphology.binary_erosion(k == 0, morphology.disk(6))])) - {0}
    dk2 = dk & ~np.isin(lab, list(hair_lab))
    feats["dark"] = [p for p in poly(dk2, 0.8) if 20 < p["area"] < 5000]
    lips = face & fg & (R - G > 50) & (R > 150) & (R - B > 60)
    lp = poly(lips, 0.8)
    feats["lips"] = sorted(lp, key=lambda p: -p["c"][0])[:1]
    hy, hx_ = np.nonzero(morphology.remove_small_holes(measure.label(k == 0) == max(measure.regionprops(measure.label(k == 0)), key=lambda r: r.area).label, 20000))
    shirt = k == 2
    sy, sx = np.nonzero(shirt)
    side[pose] = {"w": fg.shape[1], "h": fg.shape[0], "regs": regs, "feats": feats,
                  "shirtBox": [int(sx.min()), int(sy.min()), int(sx.max()), int(sy.max())], "hairBox": [int(hx_.min()), int(hy.min()), int(hx_.max()), int(hy.max())],
                  "earCreases": creases(L, skin & face, 98.5, 25, 4)}
    vis = Image.new("RGB", (fg.shape[1], fg.shape[0]), (236, 235, 230)); dr = ImageDraw.Draw(vis)
    for nm, colr in zip(["pants", "shirt", "skin", "hair"], [(214, 200, 184), (138, 147, 124), (236, 203, 172), (45, 33, 28)]):
        for r in regs[nm]: dr.polygon([tuple(p) for p in r["pts"]], fill=colr, outline=(20, 20, 20))
    for r in feats["dark"] + feats["lips"]: dr.polygon([tuple(p) for p in r["pts"]], fill=(200, 40, 40))
    vis.save(f"qa/trace-{pose}.png")
    print(pose, {nm: [(r["area"], r["c"]) for r in regs[nm][:4]] for nm in names}, "feats", len(feats["dark"]), len(feats["lips"]), "shirtBox", side[pose]["shirtBox"])
# register every pose to the heart pose by the shirt's top-left and height (the body is the same)
ref = side["heart"]["hairBox"]
for pose, s in side.items():
    b = s["hairBox"]; sc = (ref[2] - ref[0]) / (b[2] - b[0])
    s["reg"] = [sc, ref[0] - sc * b[0], ref[1] - sc * b[1]]   # x' = sc*x + tx
    print(pose, "reg", [round(v, 3) for v in s["reg"]])
model["SIDE"] = side
open("assets/people/model.js", "w").write("window.PEOPLE = " + json.dumps(model, separators=(",", ":")) + ";\n")
print("model.js", round(len(json.dumps(model)) / 1024), "KB")
