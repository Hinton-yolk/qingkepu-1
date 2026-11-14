"""后期调色（Cycles 输出之后）：偏冷的暗部、轻微暗角、柔光晕和细颗粒。参数可调，原图不覆盖。
用法：python3 grade.py <输入.png> <输出.png> [--exposure -0.7] [--glow 0.18] [--seed 帧号]
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
EXP = float(sys.argv[sys.argv.index('--exposure') + 1]) if '--exposure' in sys.argv else 0.0
GLOW = float(sys.argv[sys.argv.index('--glow') + 1]) if '--glow' in sys.argv else 0.18
im = Image.open(src).convert('RGB')
a = np.asarray(im).astype(np.float32) / 255.0
# 曝光（在显示值上近似：线性化后乘 2^EXP 再回到 sRGB）
lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4) * (2.0 ** EXP)
a = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.clip(lin, 0, None) ** (1 / 2.4) - 0.055)
a = np.clip(a, 0, 1)
h, w, _ = a.shape
lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[..., None]
# 暗部偏青蓝、亮部略暖（分离色调）
shadow = np.clip(1.0 - lum * 2.2, 0, 1)
high = np.clip(lum * 1.6 - 0.6, 0, 1)
a = a + shadow * np.array([-0.010, 0.012, 0.030]) + high * np.array([0.015, 0.008, -0.010])
# 轻微 S 曲线加反差
a = np.clip(a, 0, 1)
a = a + 0.10 * (a - 0.5) * (1 - np.abs(2 * a - 1))
# 柔光晕：亮部模糊后叠加
glow = Image.fromarray((np.clip((a - 0.72) * 3.0, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(w / 60))
a = a + GLOW * np.asarray(glow).astype(np.float32) / 255.0
# 暗角
yy, xx = np.mgrid[0:h, 0:w]
r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
a = a * (1 - 0.28 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None]
# 细颗粒
SEED = int(sys.argv[sys.argv.index('--seed') + 1]) if '--seed' in sys.argv else 1
rng = np.random.default_rng(SEED)   # 动画每帧换种子，颗粒才会动
a = a + rng.normal(0, 0.012, a.shape) * (0.6 + 0.4 * (1 - lum))
Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(dst)
print('ok', dst)
