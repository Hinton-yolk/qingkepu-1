# python3 sheet2.py out_prefix t0 t1 [cols] —— stills/ 里 t0..t1 的帧拼成联系表
import sys, glob, os
from PIL import Image, ImageDraw
pre, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); cols = int(sys.argv[4]) if len(sys.argv) > 4 else 13
fs = [f for f in sorted(glob.glob('stills/t*.png'), key=lambda f: float(os.path.basename(f)[1:-4])) if a <= float(os.path.basename(f)[1:-4]) < b]
w, h = 162, 288; rows = (len(fs) + cols - 1) // cols
o = Image.new('RGB', (cols * w, rows * (h + 18)), 'white'); d = ImageDraw.Draw(o)
for i, f in enumerate(fs):
    x, y = (i % cols) * w, (i // cols) * (h + 18); o.paste(Image.open(f).convert('RGB').resize((w, h)), (x, y + 18)); d.text((x + 3, y + 3), os.path.basename(f)[1:-4], fill='black')
o.save(pre, quality=86); print(pre, o.size)
