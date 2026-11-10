#!/usr/bin/env python3
"""测画面亮度和色度（「3D 镜头语法」里「微观世界的样子」「工序台的样子」两条用）。

用法：
  python3 tools/frame_stats.py <图片或视频> [秒 ...] [--crop 宽:高:x:y]
  - 图片：直接测；视频：在给定秒数抽帧测（不给秒数就测第 0 秒）。
  - --crop：先裁剪再测（测录屏时用它去掉浏览器界面）。
输出：
  - 平均亮度（Rec.709，0–1）、5% / 95% 分位亮度；
  - 平均色度 C = max(R,G,B) − min(R,G,B)（0–1）。规则里的阈值用这个；
    它不会像 HSV 的 S 那样在暗像素上被放大（近黑的深蓝 S 很高，C 很低）；
  - 仅作参考：V > 0.2 的像素的 HSV 饱和度（V 不是亮度，深蓝也可能算进去）；
  - 5 个主色。
"""
import sys, os, subprocess, tempfile, shutil
import numpy as np
from PIL import Image

def stats(im):
    a = np.asarray(im.convert('RGB'), dtype=np.float32) / 255
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    mx, mn = a.max(axis=2), a.min(axis=2); chroma = mx - mn
    bright = mx > 0.2; s_bright = float((chroma[bright] / mx[bright]).mean()) if bright.any() else 0.0
    cols = sorted(im.convert('RGB').quantize(5).convert('RGB').getcolors(), reverse=True)[:5]
    return lum.mean(), np.percentile(lum, 5), np.percentile(lum, 95), chroma.mean(), s_bright, ['#%02x%02x%02x' % c for _, c in cols]

def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print(__doc__); sys.exit(0 if args else 1)
    crop = None
    if '--crop' in args:
        i = args.index('--crop')
        try: w, h, x, y = map(int, args[i + 1].split(':'))
        except (IndexError, ValueError): sys.exit('--crop 要写成 宽:高:x:y，例如 --crop 640:360:0:20')
        if w <= 0 or h <= 0 or x < 0 or y < 0: sys.exit('--crop 的宽高要大于 0，x、y 不能为负')
        crop = (x, y, x + w, y + h); del args[i:i + 2]
        if not args: sys.exit('缺少图片或视频路径')
    src, ts = args[0], args[1:]
    if not os.path.exists(src): sys.exit(f'找不到文件：{src}')
    items = []
    if src.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        items.append((src, Image.open(src)))
    else:
        tmp = tempfile.mkdtemp()
        try:
            for t in ts or ['0']:
                p = os.path.join(tmp, f'{t}.png')
                r = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', t, '-i', src, '-frames:v', '1', p])
                if r.returncode != 0 or not os.path.exists(p): sys.exit(f'抽帧失败：{src} 第 {t} 秒')
                items.append((f'{src}@{t}s', Image.open(p).copy()))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    for name, im in items:
        if crop:
            if crop[0] < 0 or crop[1] < 0 or crop[2] > im.width or crop[3] > im.height:
                sys.exit(f'裁剪框 {crop} 超出画面 {im.width}×{im.height}')
            im = im.crop(crop)
        m, lo, hi, c, sb, cols = stats(im)
        print(f'{name}  平均亮度 {m:.2f}  暗部5% {lo:.2f}  亮部95% {hi:.2f}  平均色度 {c:.2f}  V>0.2 像素的饱和度（仅参考） {sb:.2f}  主色 {cols}')

if __name__ == '__main__':
    main()
