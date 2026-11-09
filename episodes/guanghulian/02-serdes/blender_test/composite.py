# 把 Blender 渲出的帧放大到 1080×1920，叠上 2D 字（大字问题、25 根 / 4 根、速度标签、字幕），配上正片开头那 8.25 秒的声音
# 用法：python3 composite.py <帧目录（含 anchors.json；或含显卡电脑渲出的 opening.mp4）> <正片 mp4> <输出 mp4>
import sys, json, os, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC, FILM, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__)); FONT = os.path.join(HERE, '..', '风格样片_等距', 'NotoSansSC-900.woff')
A = json.load(open(os.path.join(SRC, 'anchors.json')))
if 'frames' in A: FPS, NF, RW, A = A['fps'], A['nf'], A['w'], A['frames']
else: FPS, NF = 24, 198; RW = Image.open(os.path.join(SRC, 'f0001.png')).size[0]
if os.path.exists(os.path.join(SRC, 'opening.mp4')) and not os.path.exists(os.path.join(SRC, 'f0001.png')):   # 显卡电脑出的视频：先拆成帧
    subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', os.path.join(SRC, 'opening.mp4'), '-start_number', '1', os.path.join(SRC, 'f%04d.png')], check=True)
K = W / RW
RED, INK, CREAM = (229, 72, 63), (22, 22, 26), (246, 241, 230)
def f(size): return ImageFont.truetype(FONT, size)
def clamp(x): return max(0.0, min(1.0, x))
def back(k): s = 1.7; k -= 1; return k * k * ((s + 1) * k + s) + 1
def tag(base, text, x, y, size, bg, fg, t, t0, anchor=None):
    if t < t0: return
    k = clamp((t - t0) / 0.25); n = max(1, math.ceil(len(text) * k)); sc = 0.85 + 0.15 * back(clamp((t - t0) / 0.18))
    ft = f(size); tw = ft.getlength(text); pw, ph = int(tw + size * 0.9), int(size * 1.55)
    lay = Image.new('RGBA', (pw + 40, ph + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([20, 26, 20 + pw, 26 + ph], radius=size * 0.28, fill=(20, 12, 6, 110)); sh = sh.filter(ImageFilter.GaussianBlur(8))
    lay = Image.alpha_composite(sh, lay); d = ImageDraw.Draw(lay); d.rounded_rectangle([20, 20, 20 + pw, 20 + ph], radius=size * 0.28, fill=bg)
    d.text((20 + size * 0.45, 20 + ph / 2 + 1), text[:n], font=ft, fill=fg, anchor='lm')
    if sc != 1: lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.LANCZOS)
    x = min(max(x, lay.width / 2 + 24), W - lay.width / 2 - 24)   # 标签不出画面
    if anchor:   # 引线：标签 → 实物上的点
        dl = ImageDraw.Draw(base); kk = clamp((t - t0) / 0.3); ax, ay = anchor; ex, ey = ax + (x - ax) * kk, ay + (y - ay) * kk
        dl.line([ax, ay, ex, ey], fill=bg, width=6); dl.ellipse([ax - 9, ay - 9, ax + 9, ay + 9], fill=bg)
    base.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))
SUBS = [("25 根线，跑不过 4 根线", 0.095, 2.48), ("老打印机的并口线，每秒大约两兆字节", 2.48, 5.35), ("只有 4 根线的 USB，每秒几十兆", 5.35, 8.07)]
os.makedirs(os.path.join(SRC, 'comp'), exist_ok=True)
for i in range(1, NF + 1):
    t = (i - 1) / FPS; im = Image.open(os.path.join(SRC, f'f{i:04d}.png')).convert('RGBA').resize((W, H), Image.LANCZOS)
    a = {k: (v[0] * K, v[1] * K) for k, v in A[str(i)].items()}
    # 顶部压一点暗，让大字问题更跳
    g = Image.new('RGBA', (W, 520), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(520): gd.line([0, y, W, y], fill=(10, 6, 2, int(120 * (1 - y / 520) ** 1.6)))
    im.alpha_composite(g, (0, 0))
    tag(im, '线越多，反而越慢？', W / 2, 300, 68, RED + (255,), (255, 255, 255), t, 0)
    db, us = a['db25'], a['usb']
    tag(im, '25 根线', db[0] - 40, db[1] - 230, 56, CREAM + (255,), INK, t, 0.45, anchor=db)
    tag(im, '4 根线', us[0] - 60, us[1] - 400, 56, RED + (255,), (255, 255, 255), t, 1.35, anchor=us)
    ca, cb = a['cableA'], a['cableB']
    tag(im, '每秒约 2 MB', ca[0] - 120, ca[1] + 40, 44, CREAM + (255,), INK, t, 4.75, anchor=ca)
    tag(im, '每秒几十 MB', cb[0] + 60, cb[1] + 150, 44, RED + (255,), (255, 255, 255), t, 7.25, anchor=cb)
    s = next((x for x in SUBS if x[1] <= t < x[2]), None)
    if s:
        ft = f(50); tw = ft.getlength(s[0]); d = ImageDraw.Draw(im); d.rounded_rectangle([W / 2 - tw / 2 - 30, 1400 - 44, W / 2 + tw / 2 + 30, 1400 + 44], radius=10, fill=(22, 22, 26, 235))
        d.text((W / 2, 1402), s[0], font=ft, fill=CREAM, anchor='mm')
    im.convert('RGB').save(os.path.join(SRC, 'comp', f'{i:04d}.jpg'), quality=95)
subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(SRC, 'comp', '%04d.jpg'), '-ss', '0', '-t', str(NF / FPS), '-i', FILM,
                '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', OUT], check=True)
print('wrote', OUT)
