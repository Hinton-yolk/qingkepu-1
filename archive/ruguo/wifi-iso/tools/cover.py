"""Covers from a clean frame (no subtitles): out/cover_9x16.png (Douyin), out/cover_3x4.png (Xiaohongshu).
Title top-left over the dark sheet, never centred on a gradient; one accent (orange = Wi-Fi)."""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def face(path, size, name='Noto Sans CJK SC'):
    for i in range(12):
        f = ImageFont.truetype(path, size, index=i)
        if f.getname()[0] == name: return f
BOLD, REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
ACC, WHITE, SOFT = (255, 106, 26), (247, 244, 238), (255, 217, 184)
base = Image.open(os.path.join(ROOT, 'review', 'cover', 't12.90.png')).convert('RGB')
def title(img, x, y, s=1.0):
    sc = Image.new('L', (1, 1000)); sc.putdata([int(170 * max(0, min(1, (1 - k / 1000) * 1.5))) for k in range(1000)])
    h = int(y + 640 * s); img.paste(Image.new('RGB', (img.width, h), (6, 12, 30)), (0, 0), sc.resize((img.width, h)))
    d = ImageDraw.Draw(img)
    d.text((x, y), '如果……会怎样 · 01', font=face(REG, int(36 * s)), fill=(220, 235, 250))
    d.text((x, y + 70 * s), '如果你的眼睛', font=face(BOLD, int(118 * s)), fill=WHITE)
    f2 = face(BOLD, int(118 * s)); d.text((x, y + 205 * s), '突然能看见 ', font=f2, fill=WHITE)
    w = d.textlength('突然能看见 ', font=f2); d.text((x + w, y + 205 * s), 'Wi-Fi', font=f2, fill=ACC); w2 = d.textlength('Wi-Fi', font=f2); d.text((x + w + w2, y + 205 * s), '？', font=f2, fill=WHITE)
    d.rectangle((x, y + 372 * s, x + 84 * s, y + 380 * s), fill=ACC)
    d.text((x, y + 410 * s), '整栋楼都在发光——', font=face(BOLD, int(50 * s)), fill=SOFT, stroke_width=5, stroke_fill=(6, 12, 30))
    d.text((x, y + 478 * s), '可你一个也看不见', font=face(BOLD, int(50 * s)), fill=SOFT, stroke_width=5, stroke_fill=(6, 12, 30))
c916 = base.copy(); title(c916, 72, 90)
os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
c916.save(os.path.join(ROOT, 'out', 'cover_9x16.png')); c916.save(os.path.join(ROOT, 'out', 'poster.jpg'), quality=92)
c34 = base.crop((0, 120, 1080, 1560)); title(c34, 64, 50, .92); c34.save(os.path.join(ROOT, 'out', 'cover_3x4.png'))
S = Image.new('RGB', (1100, 960), (20, 20, 20)); S.paste(c916.resize((540, 960)), (0, 0)); S.paste(c34.resize((540, 720)), (560, 0)); S.save(os.path.join(ROOT, 'review', 'covers.jpg'), quality=88)
print('covers written')
