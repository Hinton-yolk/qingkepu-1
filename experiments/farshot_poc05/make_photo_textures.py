"""照片对标版（build_aisle_photo.py）用的两张贴图，写到 assets_dl/：
- door_perf_mask.png：机柜前门的冲孔网（白 = 孔，透明；黑 = 钢板）。铺满 0.56 m × 1.9 m 的门，孔径约 4 mm、孔距约 6 mm（示意，常见的高开孔率网门）。
- floor_perf_col.png / floor_perf_rough.png：通风地板（600 mm 方砖，圆孔阵列，浅灰金属）。孔径约 12 mm、孔距约 24 mm（示意）。
用法：python3 make_photo_textures.py
"""
import os

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets_dl')
os.makedirs(OUT, exist_ok=True)


def door_mask():
    # 门 0.56 m × 1.90 m，按 1 px = 1 mm 的一半（0.5 mm/px）会太大；用 1 px ≈ 1 mm：560 × 1900
    w, h = 560, 1900
    im = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(im)
    pitch, r = 6, 2
    for j, y in enumerate(range(30, h - 30, pitch)):      # 上下、左右各留 30 mm 实心边框
        off = pitch / 2 if j % 2 else 0                   # 错位排列（六角网）
        x = 30 + off
        while x < w - 30:
            d.ellipse((x - r, y - r, x + r, y + r), fill=255)
            x += pitch
    im.save(os.path.join(OUT, 'door_perf_mask.png'))


def floor_perf():
    s = 600                                               # 1 px = 1 mm，一块 600 mm 地板
    col = Image.new('RGB', (s, s), (150, 153, 158))
    rough = Image.new('L', (s, s), 70)                    # 金属面偏亮，粗糙度约 0.27
    dc, dr = ImageDraw.Draw(col), ImageDraw.Draw(rough)
    # 板边一圈压条
    for k in range(6):
        dc.rectangle((k, k, s - 1 - k, s - 1 - k), outline=(120, 123, 128))
    pitch, r = 24, 6
    for y in range(36, s - 30, pitch):
        for x in range(36, s - 30, pitch):
            dc.ellipse((x - r, y - r, x + r, y + r), fill=(18, 19, 21))     # 孔：下面是暗的地板下空间
            dr.ellipse((x - r, y - r, x + r, y + r), fill=230)
    col = col.filter(ImageFilter.GaussianBlur(0.6))
    col.save(os.path.join(OUT, 'floor_perf_col.png'))
    rough.save(os.path.join(OUT, 'floor_perf_rough.png'))


door_mask()
floor_perf()
print('ok')
