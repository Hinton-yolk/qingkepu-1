#!/usr/bin/env python3
"""把 out/stills/ 里的单帧拼成一张接触表（每张约 270×480，角上标时间）。
用法：python3 scripts/contact_sheet.py <输出.jpg> [--cols 7] [--dir out/stills]
先用 `npm run still -- 1s 10s …` 出好单帧，再运行本脚本。需要 Pillow。"""
import argparse, glob, os, re
from PIL import Image, ImageDraw, ImageFont

p = argparse.ArgumentParser()
p.add_argument('out'); p.add_argument('--cols', type=int, default=7)
p.add_argument('--dir', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out', 'stills'))
a = p.parse_args()

files = sorted(glob.glob(os.path.join(a.dir, 't*_f*.png')))
if not files: raise SystemExit('没有单帧：先运行 npm run still -- <帧号…>')
TW, TH, GAP, CAP = 270, 480, 8, 26
cols = min(a.cols, len(files)); rows = (len(files) + cols - 1) // cols
sheet = Image.new('RGB', (cols * TW + (cols + 1) * GAP, rows * (TH + CAP) + (rows + 1) * GAP), (38, 39, 44))
d = ImageDraw.Draw(sheet)
try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
except Exception: font = ImageFont.load_default()
for i, f in enumerate(files):
    m = re.search(r't([\d.]+)_f(\d+)', os.path.basename(f))
    x = GAP + (i % cols) * (TW + GAP); y = GAP + (i // cols) * (TH + CAP + GAP)
    sheet.paste(Image.open(f).convert('RGB').resize((TW, TH), Image.LANCZOS), (x, y + CAP))
    d.text((x + 2, y + 3), f'{float(m.group(1)):.1f} s   f{int(m.group(2))}', fill=(243, 235, 221), font=font)
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
sheet.save(a.out, quality=90)
print('已写', a.out, sheet.size, f'{len(files)} 帧')
