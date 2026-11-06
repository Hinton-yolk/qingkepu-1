"""Tile frames/<tag>/f_*.jpg into a contact sheet with time labels: python3 tools/sheet_frames.py <dir> <out.jpg> <fps> [cols] [width]"""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont
d, out, fps = sys.argv[1], sys.argv[2], float(sys.argv[3])
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 12; w = int(sys.argv[5]) if len(sys.argv) > 5 else 180
fs = sorted(f for f in os.listdir(d) if re.match(r'f_\d+\.jpg$', f))
h = w * 16 // 9; rows = (len(fs) + cols - 1) // cols
S = Image.new('RGB', (cols * (w + 6) + 6, rows * (h + 26) + 6), (20, 20, 22)); D = ImageDraw.Draw(S)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
for i, f in enumerate(fs):
    t = int(f[2:7]) / fps; x, y = 6 + (i % cols) * (w + 6), 6 + (i // cols) * (h + 26)
    S.paste(Image.open(os.path.join(d, f)).resize((w, h), Image.LANCZOS), (x, y + 22)); D.text((x, y + 2), f'{t:.1f}', font=F, fill=(240, 200, 160))
S.save(out, quality=88); print(out, S.size, len(fs), 'frames')
