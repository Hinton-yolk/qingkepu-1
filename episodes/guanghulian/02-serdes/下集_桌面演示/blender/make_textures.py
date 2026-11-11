"""演示装置用的小贴图：翻面纸签、计数轮数字、节拍器刻度牌。
用法：python3 make_textures.py <字体目录> <输出目录>"""
import sys, os
from PIL import Image, ImageDraw, ImageFont

FONTS, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
BOLD = f"{FONTS}/NotoSansSC-Bold.otf"
PAPER, INK = (236, 229, 212), (24, 22, 20)


def sign(name, text, w=960, h=352):
    im = Image.new("RGB", (w, h), PAPER); d = ImageDraw.Draw(im)
    size = 230
    while True:
        f = ImageFont.truetype(BOLD, size)
        l, t, r, b = d.textbbox((0, 0), text, font=f)
        if r - l <= w * 0.86 and b - t <= h * 0.74: break
        size -= 6
    d.text(((w - (r - l)) / 2 - l, (h - (b - t)) / 2 - t), text, font=f, fill=INK)
    d.rectangle([6, 6, w - 7, h - 7], outline=(120, 112, 98), width=3)
    im.save(f"{OUT}/{name}.png")


sign("sign_reader", "读带口")
sign("sign_chip", "收货的芯片")

# 计数轮：0–9 从上到下排成一条，卷在轮子上。黑底白字（机械计数器的样子）
W, CH = 264, 226
im = Image.new("RGB", (W, CH * 10), (14, 14, 15)); d = ImageDraw.Draw(im)
f = ImageFont.truetype(BOLD, 200)
for n in range(10):
    l, t, r, b = d.textbbox((0, 0), str(n), font=f)
    d.text(((W - (r - l)) / 2 - l, n * CH + (CH - (b - t)) / 2 - t), str(n), font=f, fill=(236, 232, 220))
im.save(f"{OUT}/digits.png")

# 节拍器刻度牌：竖条，刻度 + 速度数字（40–208，常见机械节拍器的范围）
W, H = 200, 1500
im = Image.new("RGB", (W, H), (226, 216, 190)); d = ImageDraw.Draw(im)
f = ImageFont.truetype(BOLD, 34)
marks = [40, 44, 48, 52, 56, 60, 66, 72, 80, 88, 96, 104, 112, 120, 132, 144, 160, 176, 192, 208]
for i, m in enumerate(marks):
    y = 60 + i * (H - 120) / (len(marks) - 1)
    d.line([(W / 2 - 22, y), (W / 2 + 22, y)], fill=INK, width=5)
    s = str(m); l, t, r, b = d.textbbox((0, 0), s, font=f)
    x = 12 if i % 2 == 0 else W - 12 - (r - l)
    d.text((x - l, y - (b - t) / 2 - t), s, font=f, fill=INK)
im.save(f"{OUT}/scale.png")
print("ok", os.listdir(OUT))
