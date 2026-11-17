# 接触表：python3 scripts/sheet.py <目录> <输出.jpg> [每行张数]
import sys, glob, os
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
fs = sorted(glob.glob(os.path.join(d, 't*.png'))); ims = [Image.open(f).convert('RGB') for f in fs]
w, h = ims[0].size; rows = (len(ims) + cols - 1) // cols
S = Image.new('RGB', (cols * (w + 6), rows * (h + 30)), (40, 40, 40)); D = ImageDraw.Draw(S)
for i, (f, im) in enumerate(zip(fs, ims)):
    x, y = (i % cols) * (w + 6), (i // cols) * (h + 30); S.paste(im, (x, y + 26)); D.text((x + 4, y + 6), os.path.basename(f)[1:-4] + 's', fill=(255, 255, 0))
S.save(out, quality=82); print(out, S.size)
