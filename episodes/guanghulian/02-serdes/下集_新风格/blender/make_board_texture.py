# 生成 AI 服务器主板这一块的贴图（示意，不对应任何真实产品），给「去塑料感」的新材质用。输出 assets/board_*.png
#   board_rgba.png：R = 阻焊下的铜（走线、铺铜）、G = 裸露的金焊盘、B = 白色丝印、A = 过孔
# 坐标（mm，和 shot_open.py 一致）：x ∈ [−60, 60]，y ∈ [−50, 70]；芯片封装基板前沿在 y = 62，主差分对在 x = 0（几何另画）。
import os, random, math
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'assets'); os.makedirs(OUT, exist_ok=True)
X0, X1, Y0, Y1 = -60.0, 60.0, -50.0, 70.0; PPM = 34          # 每毫米 34 像素（0.09 mm 的线约 3 像素）
NX, NY = int((X1 - X0) * PPM), int((Y1 - Y0) * PPM)
rnd = random.Random(20261110)
def px(x, y): return ((x - X0) * PPM, (Y1 - y) * PPM)
R = Image.new('L', (NX, NY), 0); G = Image.new('L', (NX, NY), 0); B = Image.new('L', (NX, NY), 0); A = Image.new('L', (NX, NY), 0)
dR, dG, dB, dA = (ImageDraw.Draw(i) for i in (R, G, B, A))
def line(d, pts, w, v=255): d.line([px(*p) for p in pts], fill=v, width=max(1, round(w * PPM)), joint='curve')
def rect(d, x0, y0, x1, y1, v=255):
    (a, b), (c, e) = px(x0, y1), px(x1, y0); d.rectangle([a, b, c, e], fill=v)
def dot(d, x, y, r, v=255):
    cx, cy = px(x, y); rr = max(1.0, r * PPM); d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=v)
# 1) 大面积铺铜（地平面在阻焊下略亮），高速走线区挖出隔离带
rect(dR, X0 + 1, Y0 + 1, X1 - 1, Y1 - 1, 60)
rect(dR, -12.5, Y0, 12.5, 62, 0)
# 2) 高速差分对：从画外来，平行走，靠近封装时 45° 扇出到 BGA 焊球区；每对线宽 0.09、间距 0.12；中间偶尔有等长绕线（蛇形）
PAIRS = [0.0] + [s * d for d in (1.3, 2.6, 3.9, 5.2, 7.5, 9.8) for s in (-1, 1)]
for px_ in PAIRS:
    fan = px_ * 0.55
    for dx in (-0.105, 0.105):
        pts = [(px_ + dx, Y0), (px_ + dx, 50), (fan + dx, 57), (fan + dx, 66)]
        if abs(px_) in (3.9, 7.5):                          # 等长绕线：一小段蛇形
            mid = [(px_ + dx + (0.25 if k % 2 else 0), 20 + k * 0.6) for k in range(10)]
            pts = [pts[0], (px_ + dx, 20)] + mid + [(px_ + dx, 26)] + pts[1:]
        line(dR, pts, 0.09, 255)
    for k in range(0, 3):                                    # 回流地过孔（成对走线旁边）
        dot(dA, px_ + 0.55, -30 + k * 30, 0.15)
# 3) 走线区两边：低速信号、电源走线（宽一点、会拐弯）
for side in (-1, 1):
    for k in range(9):
        x = side * (14 + k * 1.1)
        line(dR, [(x, Y0), (x, 10 + k), (x + side * 3, 14 + k), (x + side * 3, 52)], 0.15, 200)
    for k in range(4):
        line(dR, [(side * 26, -40 + k * 6), (side * 40, -40 + k * 6), (side * 44, -36 + k * 6)], 0.6, 230)
# 4) 去耦电容的焊盘（金，ENIG）和丝印框；位置和 shot_open.py 里的电容一致
CAPS = []
for side in (-1, 1):
    for row in range(3):
        for k in range(8): CAPS.append((side * (13.0 + k * 1.9), 53.5 + row * 2.4, True))
    for k in range(14): CAPS.append((side * 33.5, 64 + k * 3.8, False))
for x, y, along_x in CAPS:
    for sg in (-1, 1):
        if along_x: rect(dG, x + sg * 0.42 - 0.17, y - 0.3, x + sg * 0.42 + 0.17, y + 0.3)
        else: rect(dG, x - 0.3, y + sg * 0.42 - 0.17, x + 0.3, y + sg * 0.42 + 0.17)
# 5) 测试点、基准点（圆形金焊盘）
for k in range(10): dot(dG, rnd.uniform(-55, -16) * rnd.choice([1, -1]), rnd.uniform(-45, 45), 0.4)
for x, y in ((-55, -45), (55, -45), (-55, 48)): dot(dG, x, y, 0.5); dot(dB, x, y, 1.0)
# 6) 白色丝印：元件位号、框线、极性点、板名
try: F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', int(0.9 * PPM))
except Exception: F = ImageFont.load_default()
FS = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', int(0.6 * PPM)) if F else F
for i, (x, y, along_x) in enumerate(CAPS):
    if i % 2 == 0: dB.text(px(x, y + 0.9 if along_x else y), f'C{301 + i}', font=FS, fill=255, anchor='mm')
for side in (-1, 1):
    for k in range(3):
        for r in range(3):
            cx, cy = side * (45 + k * 11), 70 + r * 13
            if cy < Y1: (a, b), (c, e) = px(cx - 5.2, cy + 5.2), px(cx + 5.2, cy - 5.2); dB.rectangle([a, b, c, e], outline=255, width=3); dB.text(px(cx, cy - 6.2), f'L{10 + k * 3 + r}', font=F, fill=255, anchor='mm')
(a, b), (c, e) = px(-31, 62.6), px(31, 61.4); dB.rectangle([a, b, c, e], outline=255, width=3)
dB.text(px(-24, -46), 'AIX-SRV-MB  REV C', font=F, fill=255, anchor='lm'); dB.text(px(24, -46), '94V-0', font=F, fill=255, anchor='mm')
dB.text(px(-8, 40), 'SERDES_TX0', font=FS, fill=255, anchor='mm')
# 7) 过孔：电源区栅格 + 随机散布
for x in range(-56, 57, 3):
    for y in range(-44, 50, 3):
        if abs(x) > 13 and rnd.random() < 0.35: dot(dA, x + rnd.uniform(-0.3, 0.3), y + rnd.uniform(-0.3, 0.3), 0.15)
img = Image.merge('RGBA', (R, G, B, A)); img.save(os.path.join(OUT, 'board_rgba.png')); print('board_rgba', img.size)
