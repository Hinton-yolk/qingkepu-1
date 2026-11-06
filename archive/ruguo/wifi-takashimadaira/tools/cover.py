"""Covers from a clean final-quality frame: out/cover_9x16.png (Douyin), out/cover_3x4.png (Xiaohongshu), out/poster.jpg.
The title sits top-left over the dark room (never centred on a gradient); one UI face (Noto Sans Mono CJK SC), one accent."""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def face(path, size):
    for i in range(10):
        f = ImageFont.truetype(path, size, index=i)
        if f.getname()[0] == 'Noto Sans Mono CJK SC': return f
    raise SystemExit('font not found')
BOLD, REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
ACC = (255, 106, 26)
base = Image.open(os.path.join(ROOT, 'review', 'cover', 'clean_37.2.png')).convert('RGB')

def title(img, x, y, s=1.0):
    # a legibility scrim: the dark room deepened behind the block (top-down, fades out under the last line)
    sc = Image.new('L', (1, 1000)); sc.putdata([int(150 * max(0, min(1, (1 - k / 1000) * 1.6))) for k in range(1000)])
    h = int(y + 600 * s); img.paste(Image.new('RGB', (img.width, h), (4, 5, 6)), (0, 0), sc.resize((img.width, h)))
    d = ImageDraw.Draw(img)
    d.text((x, y), '如果……会怎样 · 01', font=face(REG, int(34 * s)), fill=(236, 231, 222))
    d.text((x, y + 70 * s), '如果眼睛', font=face(BOLD, int(124 * s)), fill=(247, 242, 232))
    d.text((x, y + 210 * s), '能看见 Wi-Fi', font=face(BOLD, int(124 * s)), fill=(247, 242, 232))
    d.rectangle((x, y + 392 * s, x + 84 * s, y + 400 * s), fill=ACC)
    d.text((x, y + 428 * s), '一栋楼 200 多台路由器', font=face(REG, int(44 * s)), fill=(255, 210, 168))
    d.text((x, y + 490 * s), '每秒都在喊「我在这儿」', font=face(REG, int(44 * s)), fill=(255, 210, 168))

c916 = base.copy(); title(c916, 72, 64)
os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
c916.save(os.path.join(ROOT, 'out', 'cover_9x16.png'))
c916.save(os.path.join(ROOT, 'out', 'poster.jpg'), quality=92)
c34 = base.crop((0, 0, 1080, 1440)); title(c34, 64, 56, .92)
c34.save(os.path.join(ROOT, 'out', 'cover_3x4.png'))
S = Image.new('RGB', (540 + 540 + 20, 960), (20, 20, 20)); S.paste(c916.resize((540, 960)), (0, 0)); S.paste(c34.resize((540, 720)), (560, 0))
S.save(os.path.join(ROOT, 'review', 'covers.jpg'), quality=88); print('covers written')
