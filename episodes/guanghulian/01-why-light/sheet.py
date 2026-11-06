# python3 sheet.py out.jpg [cols] —— stills/ 里的帧拼成一张联系表（文件名标时间）
import sys, glob, os
from PIL import Image, ImageDraw
fs = sorted(glob.glob('stills/t*.png'), key=lambda f: float(os.path.basename(f)[1:-4]))
cols = int(sys.argv[2]) if len(sys.argv) > 2 else 9; w, h = 216, 384; rows = (len(fs) + cols - 1) // cols
o = Image.new('RGB', (cols * w, rows * (h + 20)), 'white'); d = ImageDraw.Draw(o)
for i, f in enumerate(fs):
    x, y = (i % cols) * w, (i // cols) * (h + 20); o.paste(Image.open(f).convert('RGB').resize((w, h)), (x, y + 20)); d.text((x + 4, y + 4), os.path.basename(f)[1:-4] + 's', fill='black')
o.save(sys.argv[1], quality=88); print(o.size)
