# python3 sheet_from_mp4.py film.mp4 out.jpg [step=0.5] [cols=13] —— 从成片按拍抽帧，拼成联系表（每拍一帧）
import sys, subprocess, os, glob, tempfile
from PIL import Image, ImageDraw
mp4, out = sys.argv[1], sys.argv[2]; step = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5; cols = int(sys.argv[4]) if len(sys.argv) > 4 else 13
d = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(out)))
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', mp4, '-vf', f'fps=1/{step},scale=162:288', f'{d}/%04d.png'], check=True)
fs = sorted(glob.glob(f'{d}/*.png')); w, h = 162, 288; rows = (len(fs) + cols - 1) // cols
o = Image.new('RGB', (cols * w, rows * (h + 18)), 'white'); dr = ImageDraw.Draw(o)
for i, f in enumerate(fs):
    x, y = (i % cols) * w, (i // cols) * (h + 18); o.paste(Image.open(f).convert('RGB'), (x, y + 18)); dr.text((x + 3, y + 3), f'{i * step:.1f}s', fill='black'); os.remove(f)
os.rmdir(d); o.save(out, quality=86); print(out, o.size, len(fs), 'frames')
