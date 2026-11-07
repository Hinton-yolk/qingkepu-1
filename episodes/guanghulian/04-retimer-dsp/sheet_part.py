# 每句旁白一帧（句中间）的接触表：python3 sheet_x.py → review/x_sheet.jpg（从草稿 mp4 里抽帧）
import json, subprocess, os, sys
V = sys.argv[1]; NAME = '上' if V == 'u' else '下'
from PIL import Image, ImageDraw
D = json.load(open(f'代码工程/ep4/desk_{V}.json', encoding='utf-8')); A = json.load(open('配音/align_x.json', encoding='utf-8'))
mp4 = f'review/光互连04_小红书_{NAME}集_草稿.mp4'; os.makedirs(f'review/{V}s', exist_ok=True)
ts = [(0.0, 'first')] + [(round(v['t'] + A[v['id']]['dur'] * 0.6, 2), v['id']) for v in D['voice']]
w, h, cols = 216, 384, 9; rows = (len(ts) + cols - 1) // cols
S = Image.new('RGB', (cols * w, rows * (h + 22)), '#111'); d = ImageDraw.Draw(S)
for i, (t, lid) in enumerate(ts):
    f = f'review/{V}s/{i:02d}.png'; subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-ss', str(t), '-i', mp4, '-frames:v', '1', f], check=True)
    x, y = (i % cols) * w, (i // cols) * (h + 22); S.paste(Image.open(f).convert('RGB').resize((w, h)), (x, y + 22)); d.text((x + 4, y + 4), f'{t:.1f}s {lid}', fill='#eee')
S.save(f'review/{V}_sheet.jpg', quality=85); print(len(ts), 'frames')
