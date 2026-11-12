#!/usr/bin/env python3
"""把 out/stills/ 里的单帧拼成一张接触表（默认每张 270×480，角上标时间）。
用法：python3 scripts/contact_sheet.py <输出.jpg> [--cols 7] [--cell 360x640] [--title "说明"] [--dir out/stills]
先用 `npm run still -- 1s 10s …` 出好单帧，再运行本脚本。需要 Pillow。
文件名里 f<帧号> 后面的后缀（例如 still 的 --tag=xxx）会标在那一格的角上。"""
import argparse, glob, os, re
from PIL import Image, ImageDraw, ImageFont

p = argparse.ArgumentParser()
p.add_argument('out'); p.add_argument('--cols', type=int, default=7)
p.add_argument('--cell', default='270x480', help='每格的大小，宽x高')
p.add_argument('--title', default='', help='表头的一行说明')
p.add_argument('--dir', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out', 'stills'))
a = p.parse_args()

files = sorted(glob.glob(os.path.join(a.dir, 't*_f*.png')))
if not files: raise SystemExit('没有单帧：先运行 npm run still -- <帧号…>')
TW, TH = (int(v) for v in a.cell.lower().split('x')); GAP, CAP = 8, 26
HEAD = 34 if a.title else 0
cols = min(a.cols, len(files)); rows = (len(files) + cols - 1) // cols
sheet = Image.new('RGB', (cols * TW + (cols + 1) * GAP, HEAD + rows * (TH + CAP) + (rows + 1) * GAP), (38, 39, 44))
d = ImageDraw.Draw(sheet)
def load(size):
    # 表头和后缀可能有中文：先找中文字体
    for path in ('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        try: return ImageFont.truetype(path, size)
        except Exception: pass
    return ImageFont.load_default()
font = load(18)
if a.title: d.text((GAP + 2, 7), a.title, fill=(243, 235, 221), font=load(20))
for i, f in enumerate(files):
    m = re.search(r't([\d.]+)_f(\d+)(?:_(.+))?\.png$', os.path.basename(f))
    x = GAP + (i % cols) * (TW + GAP); y = HEAD + GAP + (i // cols) * (TH + CAP + GAP)
    sheet.paste(Image.open(f).convert('RGB').resize((TW, TH), Image.LANCZOS), (x, y + CAP))
    tag = f'   {m.group(3)}' if m.group(3) else ''
    d.text((x + 2, y + 3), f'{float(m.group(1)):.1f} s   f{int(m.group(2))}{tag}', fill=(243, 235, 221), font=font)
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
sheet.save(a.out, quality=90)
print('已写', a.out, sheet.size, f'{len(files)} 帧')
