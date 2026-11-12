#!/usr/bin/env python3
"""把 dump 出来的每秒一帧拼成小图：python3 t5_comp_sheet.py <dump目录> <silent|sound> <输出.png> [列数]"""
import sys, glob
from PIL import Image
d, v, out = sys.argv[1:4]; cols = int(sys.argv[4]) if len(sys.argv) > 4 else 8
fs = sorted(glob.glob(f'{d}/{v}_*.png')); tw, th = 180, 320
rows = (len(fs) + cols - 1) // cols; im = Image.new('RGB', (cols * tw, rows * th), (0, 0, 0))
for i, f in enumerate(fs): im.paste(Image.open(f).resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
im.save(out); print(out, im.size, len(fs))
