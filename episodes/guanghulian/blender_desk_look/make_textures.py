"""定妆静帧用的 2D 贴图：平板屏幕内容 + 三条纸条。
用法：python3 make_textures.py <字体目录> <输出目录>
字体目录里要有 NotoSerifSC.otf（纸条）和 NotoSansSC-Bold.otf（屏幕）。
"""
import sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

FD, OUT = sys.argv[1], sys.argv[2]
SERIF = f"{FD}/NotoSerifSC.otf"
SANS = f"{FD}/NotoSansSC-Bold.otf"
GOLD = (255, 196, 84)      # 系列色板：金色只给电
INK_NIGHT = (18, 19, 24)   # 墨夜 #121318


def screen():
    # 平板正面 248.6 x 179.5 mm，整面一张图（含黑边框）
    W, H = 2488, 1796               # 10 px / mm
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    bz = 90                          # 边框 9 mm
    d.rounded_rectangle([bz, bz, W - bz, H - bz], 60, fill=INK_NIGHT)
    # 方波：低 → 一段平平的高电平 → 低
    x0, x1 = bz + 170, W - bz - 170
    yl, yh = 800, 400
    xa, xb = x0 + 330, x1 - 330
    pts = [(x0, yl), (xa, yl), (xa, yh), (xb, yh), (xb, yl), (x1, yl)]
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).line(pts, fill=(120, 80, 20), width=46, joint="curve")
    glow = glow.filter(ImageFilter.GaussianBlur(26))
    # 辉光只留在屏幕玻璃范围内
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle([bz, bz, W - bz, H - bz], 60, fill=255)
    im = Image.composite(ImageChops.add(im, glow), im, m)
    d = ImageDraw.Draw(im)
    d.line(pts, fill=GOLD, width=22, joint="curve")
    for p in pts[1:-1]:
        d.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=GOLD)
    # 0 / 1 电平小标
    f_s = ImageFont.truetype(SANS, 84)
    d.text((x0 - 90, yl - 52), "0", font=f_s, fill=(150, 152, 160))
    d.text((x0 - 90, yh - 52), "1", font=f_s, fill=(150, 152, 160))
    # 高电平下面的双箭头
    ya = yl + 110
    d.line([(xa + 20, ya), (xb - 20, ya)], fill=(235, 235, 240), width=8)
    for xx, s in ((xa + 20, 1), (xb - 20, -1)):
        d.polygon([(xx, ya), (xx + s * 44, ya - 26), (xx + s * 44, ya + 26)], fill=(235, 235, 240))
    d.line([(xa, yl + 40), (xa, ya + 40)], fill=(235, 235, 240), width=5)
    d.line([(xb, yl + 40), (xb, ya + 40)], fill=(235, 235, 240), width=5)
    # 大字问题
    f_b = ImageFont.truetype(SANS, 250)
    t = "四个？还是五个？"
    tw = d.textlength(t, font=f_b)
    d.text(((W - tw) / 2, 1120), t, font=f_b, fill=(245, 245, 248))
    im.save(f"{OUT}/screen.png")


def paper_base(W, H, seed):
    rnd = random.Random(seed)
    im = Image.new("RGB", (W, H), (242, 238, 228))
    # 纸的纤维斑驳：低频 + 高频噪声
    n = Image.effect_noise((W // 6, H // 6), 22).resize((W, H), Image.BICUBIC)
    n2 = Image.effect_noise((W, H), 9)
    n = ImageChops.add(n, n2, scale=2.0)
    im = ImageChops.multiply(im, Image.merge("RGB", [n.point(lambda v: 232 + (v - 128) // 5)] * 3))
    return im, rnd


def highlighter(im, box, seed):
    """荧光笔：两三道略有重叠、边缘不齐的笔画，正片叠底。"""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    lay = Image.new("RGB", im.size, (255, 255, 255))
    d = ImageDraw.Draw(lay)
    col = (255, 236, 60)
    top, bot = [], []
    n = 14
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        top.append((x + rnd.uniform(-4, 4), y0 + rnd.uniform(-7, 7) - 6 * i / n))
        bot.append((x + rnd.uniform(-4, 4), y1 + rnd.uniform(-7, 7) - 6 * i / n))
    d.polygon(top + bot[::-1], fill=col)
    # 起笔、收笔处颜色更深一点
    d.ellipse([x0 - 16, y0 + 6, x0 + 30, y1 - 6], fill=(250, 222, 40))
    d.ellipse([x1 - 26, y0 - 4, x1 + 18, y1 - 14], fill=(250, 226, 46))
    lay = lay.filter(ImageFilter.GaussianBlur(2.2))
    return ImageChops.multiply(im, lay)


def strip(name, lines, hl=None, seed=1, size=150, pad=(120, 105), lead=1.45):
    f = ImageFont.truetype(SERIF, size)
    tmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    tw = max(tmp.textlength(s, font=f) for s in lines)
    W = int(tw + pad[0] * 2)
    H = int(pad[1] * 2 + size * lead * (len(lines) - 1) + size * 1.25)
    im, rnd = paper_base(W, H, seed)
    d = ImageDraw.Draw(im)
    if hl:
        li, a, b = hl                                # 第 li 行里从 a 到 b 的子串
        s = lines[li]
        xa = pad[0] + tmp.textlength(s[:a], font=f)
        xb = pad[0] + tmp.textlength(s[:b], font=f)
        y = pad[1] + size * lead * li
        im = highlighter(im, (xa - 14, y + size * 0.16, xb + 14, y + size * 1.22), seed)
        d = ImageDraw.Draw(im)
    for i, s in enumerate(lines):
        d.text((pad[0], pad[1] + size * lead * i), s, font=f, fill=(28, 26, 26))
    # 打印的墨不是纯黑、边缘略糊
    im = im.filter(ImageFilter.GaussianBlur(0.8))
    im.save(f"{OUT}/{name}.png")
    print(name, W, H, "px  → 宽高比", round(W / H, 3))


screen()
# 主纸条：用户确认过的原文（抖音版下集 y3），「五个 1」上荧光笔
strip("strip_main", ["连续五个 1，就是一段连在一起、", "没有缝隙的高电平。"], hl=(0, 2, 6), seed=3)
strip("strip_b", ["芯片之间的数据排成一列跑，", "到了对面，要一个一个数清楚。"], seed=5)
strip("strip_c", ["收货端要数清这里有几个 1，", "就得知道每个比特占多长时间。"], seed=8)
