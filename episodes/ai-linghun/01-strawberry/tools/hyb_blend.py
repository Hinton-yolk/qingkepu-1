#!/usr/bin/env python3
"""Blender 混合段贴回 three.js 帧时，在段落两头做交叉淡化（默认 12 帧 = 0.4 秒），避免硬切时质感一跳。
两边是同一时刻、同一机位、同一套字幕和标注，所以淡化只像光线轻轻变了一下，不会有重影。
  python3 hyb_blend.py <three.js 帧目录（就地写入）> <Blender 合成帧目录> <首帧:尾帧> [...] [--n 12]
段首在第 0 帧时不淡入（片子从 Blender 开始）。
"""
import os, sys
import numpy as np
from PIL import Image

a = sys.argv[1:]; N = int(a[a.index("--n") + 1]) if "--n" in a else 12
if "--n" in a: i = a.index("--n"); del a[i:i + 2]
FR, CO, segs = a[0], a[1], [tuple(map(int, s.split(":"))) for s in a[2:]]
P = lambda d, f: os.path.join(d, f"{f:05d}.png")
for s0, s1 in segs:
    for f in range(s0, s1 + 1):
        # weight of the Blender frame: ramps up over the first N frames (unless the segment starts the film) and down over the last N
        w_in = 1.0 if s0 == 0 else min(1.0, (f - s0 + 1) / (N + 1))
        w_out = min(1.0, (s1 - f + 1) / (N + 1))
        w = min(w_in, w_out)
        b = np.asarray(Image.open(P(CO, f)).convert("RGB"), dtype=np.float32)
        if w < 1.0:
            t = np.asarray(Image.open(P(FR, f)).convert("RGB"), dtype=np.float32)
            b = b * w + t * (1 - w)
        Image.fromarray(np.clip(b + 0.5, 0, 255).astype(np.uint8)).save(P(FR, f))
    print(f"segment {s0}–{s1}: {s1 - s0 + 1} frames, {N}-frame cross-fades at the ends")
