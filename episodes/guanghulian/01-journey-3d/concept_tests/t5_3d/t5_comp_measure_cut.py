#!/usr/bin/env python3
"""量出第 1 拍里「整帧平均亮度 < 0.12」的最长连续段（穿机箱侧壁的黑段），写 t5_comp_cut.json。
用法：python3 t5_comp_measure_cut.py <帧根> [阈值]   只看脚本内第 20–120 帧；这些帧不全时不改 json。
亮度 = 0.2126R+0.7152G+0.0722B（sRGB 编码值 0..1）整帧平均。"""
import sys, os, glob, re, json
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); JS = os.path.join(HERE, 't5_comp_cut.json')
root = sys.argv[1]; thr = float(sys.argv[2]) if len(sys.argv) > 2 else 0.12; XF = 4
files = {}
for p in glob.glob(os.path.join(root, 'shot1', '*.png')):
    m = re.search(r'(?:_|f)(\d{4,6})\.png$', p)
    if m: files[int(m.group(1))] = p
rng = range(20, 121)
if not all(f in files for f in rng): print('第 1 拍第 20–120 帧不全，json 不更新'); sys.exit(0)
lum = {f: float((lambda a: (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]).mean())(np.asarray(Image.open(files[f]).convert('RGB'), dtype=np.float32) / 255)) for f in rng}
runs = []; s = None
for f in rng:
    if lum[f] < thr and s is None: s = f
    if (lum[f] >= thr or f == 120) and s is not None: runs.append((s, f - 1 if lum[f] >= thr else f)); s = None
if not runs: print('没有暗段'); sys.exit(0)
a, b = max(runs, key=lambda r: r[1] - r[0])
j = {'说明': '第 1 拍（脚本内帧号，1 起）整帧平均亮度 < 阈值的最长连续段，合成时剪掉；前 xf 帧与段后 xf 帧交叉溶解。正式版请在 Blender 里重排镜头，别靠合成剪。',
     'threshold': thr, 'dark_first': a, 'dark_last': b, 'xf': XF, 'luma': {str(f): round(lum[f], 3) for f in range(a - 5, b + 6) if f in lum}}
json.dump(j, open(JS, 'w'), ensure_ascii=False, indent=1); print('剪掉暗段', a, '-', b, '帧', f'({(a-1)/30:.2f}–{b/30:.2f} s)')
