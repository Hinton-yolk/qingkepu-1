"""Contact sheet: python3 tools/sheet.py <dir> <prefix> <out.jpg> [cols] [width]: tiles every <prefix><t>.jpg in time order, labelled."""
import sys, os, re
from PIL import Image, ImageDraw, ImageFont
d, pre, out = sys.argv[1:4]; cols = int(sys.argv[4]) if len(sys.argv) > 4 else 5; w = int(sys.argv[5]) if len(sys.argv) > 5 else 300
fs = sorted((float(re.match(re.escape(pre) + r'([\d.]+)\.jpg', f).group(1)), f) for f in os.listdir(d) if re.match(re.escape(pre) + r'[\d.]+\.jpg$', f))
h = w * 16 // 9; rows = (len(fs) + cols - 1) // cols
S = Image.new('RGB', (cols * (w + 8) + 8, rows * (h + 36) + 8), (20, 20, 22)); D = ImageDraw.Draw(S)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20) if os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf') else ImageFont.load_default()
for i, (t, f) in enumerate(fs):
    x, y = 8 + (i % cols) * (w + 8), 8 + (i // cols) * (h + 36)
    S.paste(Image.open(os.path.join(d, f)).resize((w, h), Image.LANCZOS), (x, y + 28)); D.text((x, y + 2), f'{t:.2f}s', font=F, fill=(240, 200, 160))
S.save(out, quality=88); print(out, S.size)
