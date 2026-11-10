import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
src, out = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
mn = im.min(2); mx = im.max(2)
white = ((mn > 228) & (mx - mn < 18)).astype(np.uint8) * 255
m = Image.fromarray(white, 'L'); h, w = white.shape
# 背景 = 和边框连通的白区 + 面积大的封闭白区（手臂和腿之间）；衬衫领子是浅蓝，不在白区里
k = 1
while True:
    arr = np.asarray(m)
    ys, xs = np.nonzero(arr == 255)
    if len(ys) == 0: break
    y0, x0 = ys[0], xs[0]
    ImageDraw.floodfill(m, (int(x0), int(y0)), 1 if k > 250 else k)
    k += 1
    if k > 400: break
lab = np.asarray(m).astype(np.int32)
keep = np.zeros_like(white, bool)
for v in np.unique(lab):
    if v in (0,): continue
    reg = lab == v
    border = reg[0].any() or reg[-1].any() or reg[:, 0].any() or reg[:, -1].any()
    if border or reg.sum() > 3000: keep |= reg
bg = Image.fromarray(keep.astype(np.uint8) * 255).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
bgn = np.asarray(bg) > 0
band = (np.asarray(bg.filter(ImageFilter.MaxFilter(7))) > 0) & ~bgn
a = np.where(bgn, 0.0, 1.0)
a = np.where(band, np.clip((250 - mn) / 70.0, 0, 1), a)
a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 255
aa = np.clip(a, 1e-3, 1)[..., None]
rgb = np.clip((im - (1 - aa) * 255) / aa, 0, 255)
rgba = np.dstack([rgb, a * 255]).astype(np.uint8)
ys, xs = np.nonzero(a > 0.05); rgba = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
Image.fromarray(rgba, 'RGBA').save(out); print(out, rgba.shape, 'regions', k - 1)
