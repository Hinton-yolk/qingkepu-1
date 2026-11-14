"""封面：取一帧终版画面（y5 第 75 帧：节拍器 + 纸带 + 读带口），下半张桌面上压系列的封面字。
用法：python3 cover.py <终版帧目录> <字体目录> <输出目录>
出两张：封面_抖音_1080x1920.png、封面_小红书_1080x1440.png（3:4，从同一帧裁）。
字的样式跟系列以前的封面一致：红底系列签、深色撕边大字、关键词黄色荧光笔、一行副题。"""
import sys, os, random
from PIL import Image, ImageDraw, ImageFont
from overlay import grade

SRC, FONTS, OUT = sys.argv[1:4]
BOLD = f"{FONTS}/NotoSansSC-Bold.otf"
CREAM, DARK, PAPER, RED, YEL = (240, 236, 224), (22, 22, 24), (236, 229, 212), (196, 72, 56), (244, 214, 70)
TAG, L1, L2, KW, SUB = "一语道破 · 白话光互连 02", "芯片怎么数清", "0 和 1？", "0 和 1", "SerDes：没人打拍子，靠听鼓点"


def torn(d, box, fill, seed, j=9):
    x0, y0, x1, y1 = box; r = random.Random(seed); n = 7
    left = [(x0 + r.uniform(-j, j), y0 + (y1 - y0) * i / n) for i in range(n + 1)]
    right = [(x1 + r.uniform(-j, j), y1 - (y1 - y0) * i / n) for i in range(n + 1)]
    d.polygon(left + right, fill=fill)


def block(im, cx, y, text, size, bg, fg, seed, kw=None, pad=(34, 16)):
    """一行字压在撕边色块上，返回色块的下沿。kw：这几个字下面垫黄色荧光笔。"""
    f = ImageFont.truetype(BOLD, size); lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    l, t, r, b = d.textbbox((0, 0), text, font=f); w, h = r - l, b - t
    x = cx - w / 2
    torn(d, (x - pad[0] + 5, y + 7, x + w + pad[0] + 5, y + h + 2 * pad[1] + 7), (0, 0, 0, 90), seed)
    torn(d, (x - pad[0], y, x + w + pad[0], y + h + 2 * pad[1]), (*bg, 255), seed)
    if kw:
        k0 = d.textlength(text[:text.index(kw)], font=f); k1 = k0 + d.textlength(kw, font=f)
        d.rectangle([x + k0 - 8, y + pad[1] + h * 0.30, x + k1 + 8, y + pad[1] + h * 1.04], fill=(*YEL, 255))
    d.text((x - l, y + pad[1] - t), text, font=f, fill=(*fg, 255))
    im.alpha_composite(lay)
    return y + h + 2 * pad[1]


def cover(im, y, size, wide=True):
    """系列签在左上角，两行大字压在纸带下面的桌面上。wide=True（抖音 9:16）多一行副题，整组字收在 y 1680 以上（主页网格按 3:4 居中裁，底部还有界面）；小红书 3:4 不放副题。"""
    cx = im.size[0] / 2
    block(im, 300, 64, TAG, 40, RED, CREAM, 1, pad=(22, 12))       # 系列签在左上角：桌面留给大字
    y = block(im, cx, y, L1, size, DARK, CREAM, 2) + 14
    y = block(im, cx, y, L2, size, PAPER, DARK, 3, kw=KW) + 22
    if wide: block(im, cx, y, SUB, 46, DARK, CREAM, 4, pad=(26, 14))
    return im.convert("RGB")


base = grade(Image.open(os.path.join(SRC, "y5", "f_0075.png")), seed=75)
assert base.size == (1080, 1920), base.size
cover(base.copy(), 1240, 128).save(os.path.join(OUT, "封面_抖音_1080x1920.png"))
cover(base.crop((0, 160, 1080, 1600)), 1082, 124, wide=False).save(os.path.join(OUT, "封面_小红书_1080x1440.png"))
print("ok")
