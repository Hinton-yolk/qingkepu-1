#!/usr/bin/env python3
"""测画面亮度和饱和度（「3D 镜头语法」第 9、10 条用）。
用法：python3 tools/frame_stats.py <图片或视频> [秒 ...]
  - 图片：直接测；视频：在给定秒数抽帧测（不给秒数就测第 0 秒）。
输出：平均亮度（Rec.709 亮度，0–1）、5% / 95% 分位亮度、平均饱和度（全帧 HSV 的 S 取平均，0–1）、5 个主色。
"""
import sys, os, subprocess, tempfile
import numpy as np
from PIL import Image

def stats(im):
    a = np.asarray(im.convert('RGB'), dtype=np.float32) / 255
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)          # HSV 的 S
    cols = sorted(im.convert('RGB').quantize(5).convert('RGB').getcolors(), reverse=True)[:5]
    return lum.mean(), np.percentile(lum, 5), np.percentile(lum, 95), sat.mean(), ['#%02x%02x%02x' % c for _, c in cols]

def main():
    src = sys.argv[1]; ts = sys.argv[2:]
    if src.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        items = [(src, Image.open(src))]
    else:
        items = []
        for t in ts or ['0']:
            p = os.path.join(tempfile.mkdtemp(), 'f.png')
            subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', t, '-i', src, '-frames:v', '1', p], check=True)
            items.append((f'{src}@{t}s', Image.open(p)))
    for name, im in items:
        m, lo, hi, s, c = stats(im)
        print(f'{name}  平均亮度 {m:.2f}  暗部5% {lo:.2f}  亮部95% {hi:.2f}  平均饱和度 {s:.2f}  主色 {c}')

if __name__ == '__main__':
    main()
