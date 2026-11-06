# python3 sheet.py s1 [每句取几帧=2] → review/s1_sheet.jpg：每句口播取帧拼成接触表（标注时间和句号）
import json, sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
N = sys.argv[1]; per = int(sys.argv[2]) if len(sys.argv) > 2 else 2
D = json.load(open(f'代码工程/split/{N}.json'))
ts = []
for l in D['lines']:
    for k in range(per): ts.append((round(l['t0'] + (l['t1'] - l['t0']) * (k + 0.6) / per, 2), l['id']))
ts = [(0.0, 'first')] + ts
out = f'review/{N}'; subprocess.run(['node', 'stills.mjs', out, '0', *[str(t) for t, _ in ts]], env={**os.environ, 'FILM': N}, check=True)
w, h = 270, 480; cols = 8; rows = (len(ts) + cols - 1) // cols
S = Image.new('RGB', (cols * w, rows * (h + 34)), '#111'); d = ImageDraw.Draw(S)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20) if os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf') else None
for i, (t, lid) in enumerate(ts):
    im = Image.open(f'{out}/t{t:.2f}.png').convert('RGB').resize((w, h), Image.LANCZOS); x, y = (i % cols) * w, (i // cols) * (h + 34)
    S.paste(im, (x, y + 34)); d.text((x + 6, y + 6), f'{t:.1f}s {lid}', fill='#eee', font=f)
S.save(f'review/{N}_sheet.jpg', quality=85); print('sheet', len(ts), 'frames')
