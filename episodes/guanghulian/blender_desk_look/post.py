"""后期：只加高光晕（halation）、轻微暗角、细颗粒。不提饱和度、不加雾、不加辉光。
用法：python3 post.py <in.png 16bit> <out.png> [out_small.jpg]"""
import sys, numpy as np
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert("RGB") if Image.open(src).mode != "I;16" else Image.open(src))
a = np.asarray(Image.open(src))
a = a[..., :3].astype(np.float32) / (65535.0 if a.dtype == np.uint16 else 255.0)
H, W, _ = a.shape
lin = a ** 2.2


def blur(x, sigma):
    r = int(sigma * 3) | 1
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2); k /= k.sum()
    for ax in (0, 1):
        pad = [(0, 0)] * x.ndim; pad[ax] = (r, r)
        xp = np.pad(x, pad, mode="edge"); out = np.zeros_like(x)
        for i, w in enumerate(k):
            sl = [slice(None)] * x.ndim; sl[ax] = slice(i, i + x.shape[ax])
            out += w * xp[tuple(sl)]
        x = out
    return x


# 高光晕：只取最亮的部分，散开一圈偏红橙的光（胶片底片反光的样子）
lum = lin @ np.array([0.2126, 0.7152, 0.0722], np.float32)
hi = np.clip((lum - 0.62) / 0.38, 0, 1)[..., None] * lin
hal = blur(hi, W * 0.006) * np.array([1.0, 0.42, 0.18], np.float32)
lin = lin + 0.22 * hal
# 暗角：四角最多压暗约 14%
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r2 = ((xx - W / 2) / (W / 2)) ** 2 * 0.55 + ((yy - H / 2) / (H / 2)) ** 2 * 0.75
lin *= (1 - 0.14 * np.clip(r2 / 1.3, 0, 1) ** 1.5)[..., None]
out = np.clip(lin, 0, 1) ** (1 / 2.2)
# 细颗粒：亮度颗粒，中间调最明显
rng = np.random.default_rng(7)
g = blur(rng.normal(0, 1, (H, W)).astype(np.float32), 0.6)
g /= g.std()
l2 = out @ np.array([0.2126, 0.7152, 0.0722], np.float32)
out += (0.012 * g * (0.35 + 1.3 * l2 * (1 - l2) * 2))[..., None]
res = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))
res.save(dst)
if len(sys.argv) > 3:
    s = res.copy(); s.thumbnail((540, 960)); s.save(sys.argv[3], quality=88)
