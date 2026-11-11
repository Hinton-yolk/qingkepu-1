"""接触表：每拍一到三帧（film.py still=<帧> 渲的小图 + 同名 .json 锚点），贴上字幕、小签、五站条、系列名，拼成一张图。
用法：python3 sheet.py <小图目录> <字体目录> <输出.jpg> [列数 默认5]
字幕取 subs.json（配音对好的时间），小签的位置取锚点。"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
from overlay import Kit, grade

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, FONTS, DST = sys.argv[1:4]
COLS = int(sys.argv[4]) if len(sys.argv) > 4 else 5
FPS = 24
SUBS = json.load(open(os.path.join(HERE, "subs.json"), encoding="utf-8"))
# 镜头里的第 f 帧是全片的第几帧
OFF = dict(y1=0, y2=60, y3d=162, s34a=198, s34b=198, y4d=385, s34c=198, y5=456, y6g=576, y6c=576, y7=846, y8d=960, y8c=1031,
           y9e=1116, s9a=1210, s9b=1210, y12c=1584, y12g=1615, y12a=1670, y13=1746, y14=1866)
# (拍, 镜头, 帧, [(锚点, 文字, 签的哪个角对着锚点, (dx, dy), 大字?)], 角注)
FRAMES = [
    ("y1", "y1", 30, [("phone_top", "芯片怎么数清 0 和 1？", "mb", (0, -10), True)], None),
    ("y2", "y2", 8, [("tray", "一排", "mt", (0, 215), False)], None),
    ("y2", "y2", 85, [("tape_mid", "排成一列", "mt", (0, 50), False)], None),
    ("y3", "y3d", 14, [("prn_out", "黑 = 1　白 = 0", "lt", (-40, 60), False)], None),
    ("y3", "s34a", 75, [("dot1", "数一个", "mt", (0, 60), False)], "示意：只画两种电平"),
    ("y4", "s34b", 150, [("ruler", "一格多长 = 节拍", "mt", (0, 70), False)], None),
    ("y4", "y4d", 20, [], None),
    ("y4", "s34c", 245, [], None),
    ("y5", "y5", 75, [("lamp", "鼓点", "lt", (30, 60), False)], None),
    ("y6", "y6g", 50, [("pin", "信号跳一下", "rb", (-30, -70), False)], None),
    ("y6", "y6c", 236, [], None),
    ("y7", "y7", 104, [], None),
    ("y8", "y8d", 50, [], None),
    ("y8", "y8c", 60, [], None),
    ("y9", "y9e", 80, [], None),
    ("y9", "s9a", 40, [("dot", "每条通道：快一倍", "mt", (0, 70), False)], None),
    ("y10", "s9b", 130, [], None),
    ("y10", "s9b", 225, [], None),
    ("y11", "s9b", 355, [], None),
    ("y12", "y12c", 20, [], None),
    ("y12", "y12g", 40, [("pin", "一条通道 · 上千亿 / 秒", "rb", (-30, -70), False)], None),
    ("y12", "y12a", 60, [], None),
    ("y13", "y13", 45, [("tape_mid", "排成一列", "mt", (0, 50), False)], None),
    ("y13", "y13", 105, [("tray_r", "拆回一排", "mt", (0, 70), False)], None),
    ("y14", "y14", 40, [], None),
]


def sub_at(t):
    for a, b, txt in SUBS:
        if a <= t < b + 0.12: return txt
    return ""


cells = []
kit = None
for beat, shot, f, tags, note in FRAMES:
    p = os.path.join(SRC, f"{shot}_{f:03d}.png")
    if not os.path.exists(p): print("缺", p); continue
    im = grade(Image.open(p), seed=f)
    kit = kit or Kit(FONTS, im.size[0]); s = kit.s
    A = json.load(open(p + ".json"))
    t = (OFF[shot] + f) / FPS
    for anc, text, corner, (dx, dy), big in tags:
        ax, ay = A[anc][0] * kit.W, A[anc][1] * kit.H
        kit.tag(im, (ax + dx * s, ay + dy * s), text, anchor=corner, big=big, line_to=None if big else (ax, ay))
    if note: kit.note(im, note)
    kit.chrome(im, station=0, next_station=1 if beat == "y14" else None)
    kit.subtitle(im, sub_at(t))
    cells.append((f"{beat} · {t:.1f} 秒", im.convert("RGB")))

W, H = cells[0][1].size; LH = int(H * 0.055)
rows = (len(cells) + COLS - 1) // COLS
sheet = Image.new("RGB", (COLS * (W + 8) + 8, rows * (H + LH + 8) + 8), (18, 18, 18)); d = ImageDraw.Draw(sheet)
font = ImageFont.truetype(f"{FONTS}/NotoSansSC-Bold.otf", int(LH * 0.62))
for i, (label, im) in enumerate(cells):
    x, y = 8 + (i % COLS) * (W + 8), 8 + (i // COLS) * (H + LH + 8)
    d.text((x + 4, y + LH * 0.08), label, font=font, fill=(240, 236, 224)); sheet.paste(im, (x, y + LH))
sheet.save(DST, quality=88)
print("ok", DST, sheet.size)
