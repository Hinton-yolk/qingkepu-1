# python3 montage.py dir out.jpg [width] —— 把一组静帧按时间排成一排看
import sys, glob
from PIL import Image
d, out = sys.argv[1], sys.argv[2]; W = int(sys.argv[3]) if len(sys.argv) > 3 else 360; H = W * 16 // 9
fs = sorted(glob.glob(f'{d}/t*.png'), key=lambda f: float(f.split('/t')[-1][:-4])); S = Image.new('RGB', (W * len(fs), H))
for i, f in enumerate(fs): S.paste(Image.open(f).convert('RGB').resize((W, H)), (i * W, 0))
S.save(out, quality=88); print(len(fs))
