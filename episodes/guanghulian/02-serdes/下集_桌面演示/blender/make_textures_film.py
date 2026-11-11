"""全片用的小贴图（在 make_textures.py 之外）：盒子上的字、挡片、桌沿签、表上的小签、路线图小卡、手机屏幕的逐帧图。
用法：python3 make_textures_film.py <字体目录> <输出目录>
手机屏幕：phone/y1_0000.png …（消息从「七」字起变乱码）、phone/y12_0000.png …（从「七」字起一个个变回来）、phone/clean.png。"""
import sys, os, random
from PIL import Image, ImageDraw, ImageFont

FONTS, OUT = sys.argv[1], sys.argv[2]
os.makedirs(f"{OUT}/phone", exist_ok=True)
BOLD = f"{FONTS}/NotoSansSC-Bold.otf"
PAPER, INK = (236, 229, 212), (24, 22, 20)


def fit(d, text, w, h, size=400):
    while True:
        f = ImageFont.truetype(BOLD, size)
        l, t, r, b = d.textbbox((0, 0), text, font=f)
        if r - l <= w and b - t <= h: return f, (l, t, r, b)
        size -= 4


def label(name, text, w, h, bg=PAPER, fg=INK, border=True):
    im = Image.new("RGB", (w, h), bg); d = ImageDraw.Draw(im)
    f, (l, t, r, b) = fit(d, text, w * 0.86, h * 0.70)
    d.text(((w - (r - l)) / 2 - l, (h - (b - t)) / 2 - t), text, font=f, fill=fg)
    if border: d.rectangle([5, 5, w - 6, h - 6], outline=(120, 112, 98), width=3)
    im.save(f"{OUT}/{name}.png")


label("box_scr", "打乱", 640, 320)
label("box_des", "还原", 640, 320)
label("box_fix", "修信号", 560, 240, bg=(22, 22, 24), fg=(232, 226, 210), border=False)
label("gate", "不随货送", 900, 420)
label("tag_serdes", "整套 = SerDes", 1200, 360)
label("tag_power", "总耗电", 520, 220)
label("tag_bit", "每个比特", 520, 220)

# 路线图小卡：五站（快递叫法），亮「打包出发」，下一站「路上」
W, H = 900, 520
im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
f1 = ImageFont.truetype(BOLD, 84); f2 = ImageFont.truetype(BOLD, 40)
d.text((50, 40), "你在这里：打包出发", font=f1, fill=INK)
names = ["打包出发", "路上", "中转", "干线", "签收"]
xs = [90 + i * 180 for i in range(5)]
d.line([(xs[0], 270), (xs[-1], 270)], fill=(150, 60, 50), width=8)
for i, (x, n) in enumerate(zip(xs, names)):
    r = 30 if i == 0 else 20
    d.ellipse([x - r, 270 - r, x + r, 270 + r], fill=(196, 72, 56) if i == 0 else PAPER, outline=(150, 60, 50), width=7)
    l, t, r_, b = d.textbbox((0, 0), n, font=f2)
    d.text((x - (r_ - l) / 2 - l, 340), n, font=f2, fill=INK if i < 2 else (120, 112, 98))
d.rectangle([5, 5, W - 6, H - 6], outline=(120, 112, 98), width=3)
im.save(f"{OUT}/route.png")

# ---- 手机屏幕（540×1170）：一条收到的消息，字很大 ----
SW, SH = 540, 1170
MSG = "今晚七点，老地方见"
JUNK = list("锟斤拷烫屯葺#%&?")
fm = ImageFont.truetype(BOLD, 96); fs = ImageFont.truetype(BOLD, 34)


def screen(chars):
    """深色界面：屏幕不过曝，字是屏幕上最亮的东西。乱码用珊瑚色。"""
    im = Image.new("RGB", (SW, SH), (14, 15, 18)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, SW, 150], fill=(24, 26, 30)); d.line([(0, 150), (SW, 150)], fill=(52, 54, 60), width=2)
    d.ellipse([28, 62, 98, 132], fill=(96, 128, 170)); d.text((116, 76), "老周", font=fs, fill=(214, 214, 220))
    d.text((SW - 110, 20), "15:42", font=fs, fill=(150, 150, 158))
    d.rounded_rectangle([22, 226, SW - 22, 566], radius=34, fill=(44, 47, 54))
    rows = [chars[:5], chars[5:]]
    for r, row in enumerate(rows):
        for c, (ch, bad) in enumerate(row):
            d.text((44 + c * 94, 250 + r * 146), ch, font=fm, fill=(255, 112, 84) if bad else (244, 242, 236))
    for k in range(2): d.rounded_rectangle([22, 640 + k * 150, 300 + k * 90, 740 + k * 150], radius=30, fill=(30, 32, 37))   # 更早的两条消息（看不清内容）
    d.rounded_rectangle([22, SH - 150, SW - 22, SH - 60], radius=40, fill=(30, 32, 37))
    return im


def frames(prefix, n, bad_from):
    """bad_from(i, f) → 第 i 个字在第 f 帧是不是乱码。乱码每 3 帧换一个字。"""
    for f in range(n):
        rnd = random.Random(1000 + f // 3)
        chars = [(rnd.choice(JUNK), True) if bad_from(i, f) else (ch, False) for i, ch in enumerate(MSG)]
        screen(chars).save(f"{OUT}/phone/{prefix}_{f:04d}.png")


frames("y1", 60, lambda i, f: i >= 2 and f >= (i - 2) * 4.5)          # 第 0 帧「七」已在变，1.2 秒时后半句全乱
frames("y12", 76, lambda i, f: i >= 2 and f < 8 + (i - 2) * 7)        # 从「七」起一个个变回来，约 2.1 秒时整句回来
screen([(ch, False) for ch in MSG]).save(f"{OUT}/phone/clean.png")
print("ok", len(os.listdir(f"{OUT}/phone")), "phone frames")
