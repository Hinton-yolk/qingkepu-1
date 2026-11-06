"""Covers from a clean frame (no subtitles): out/cover_9x16.png (Douyin), out/cover_3x4.png (Xiaohongshu).
Title top-left over the dark sheet, never centred on a gradient; one accent (orange = what moved)."""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def face(path, size, name='Noto Sans CJK SC'):
    for i in range(12):
        f = ImageFont.truetype(path, size, index=i)
        if f.getname()[0] == name: return f
BOLD, REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
ACC, WHITE, SOFT, BLUE = (255, 106, 26), (247, 244, 238), (255, 217, 184), (140, 185, 240)
base = Image.open(os.path.join(ROOT, 'review', 'cover', 't77.95.png')).convert('RGB')
def title(img, x, y, s=1.0):
    sc = Image.new('L', (1, 1000)); sc.putdata([int(190 * max(0, min(1, (1 - k / 1000) * 1.5))) for k in range(1000)])
    h = int(y + 660 * s); img.paste(Image.new('RGB', (img.width, h), (6, 12, 30)), (0, 0), sc.resize((img.width, h)))
    d = ImageDraw.Draw(img)
    d.text((x, y), '如果……会怎样 · 02', font=face(REG, int(36 * s)), fill=(220, 235, 250))
    f = face(BOLD, int(124 * s))
    d.text((x, y + 70 * s), '如果地球', font=f, fill=WHITE)
    d.text((x, y + 212 * s), '突然停止', font=f, fill=WHITE); w = d.textlength('突然停止', font=f)
    d.text((x + w, y + 212 * s), '自转', font=f, fill=ACC); w2 = d.textlength('自转', font=f); d.text((x + w + w2, y + 212 * s), '？', font=f, fill=WHITE)
    d.rectangle((x, y + 385 * s, x + 84 * s, y + 393 * s), fill=ACC)
    f3 = face(BOLD, int(52 * s))
    d.text((x, y + 420 * s), '哈尔滨沉进一公里深的海，', font=f3, fill=BLUE, stroke_width=5, stroke_fill=(6, 12, 30))
    d.text((x, y + 492 * s), '南海却露出了海底', font=f3, fill=SOFT, stroke_width=5, stroke_fill=(6, 12, 30))
c916 = Image.new('RGB', (1080, 1920), base.getpixel((10, 10))); c916.paste(base.crop((0, 0, 1080, 1600)), (0, 300)); title(c916, 72, 90)
c916.save(os.path.join(ROOT, 'out', 'cover_9x16.png')); c916.save(os.path.join(ROOT, 'out', 'poster.jpg'), quality=92)
c34 = Image.new('RGB', (1080, 1440), base.getpixel((10, 10))); c34.paste(base.crop((0, 300, 1080, 1440)), (0, 380)); title(c34, 64, 40, .86); c34.save(os.path.join(ROOT, 'out', 'cover_3x4.png'))
S = Image.new('RGB', (1100, 960), (20, 20, 20)); S.paste(c916.resize((540, 960)), (0, 0)); S.paste(c34.resize((540, 720)), (560, 0)); S.save(os.path.join(ROOT, 'review', 'covers.jpg'), quality=88)
print('covers written')
