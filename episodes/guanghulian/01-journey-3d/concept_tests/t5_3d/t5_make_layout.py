# T5 第 2、3 拍：硅光芯片表面版图贴图（示意，稀疏：波导、微环、光栅耦合器、焊盘；不对应真实产品）。
# 覆盖 x ∈ [-50,50]，y ∈ [-55,45]（单位 u，和 t5_shot23.py 一致）。主波导（x=0）和电极由几何体画，这里留出中央走廊。
# 通道：R = 硅器件（淡），G = 金属，B = 表面起伏。
import sys, random, math
from PIL import Image, ImageDraw, ImageFilter
N = 2048; X0, X1, Y0, Y1 = -50.0, 50.0, -55.0, 45.0
SX = N / (X1 - X0); SY = N / (Y1 - Y0)
px = lambda x, y: ((x - X0) * SX, (Y1 - y) * SY)
R = Image.new('L', (N, N), 0); G = Image.new('L', (N, N), 0)
dr, dg = ImageDraw.Draw(R), ImageDraw.Draw(G)
rnd = random.Random(7)
def wg(pts, w=0.5, d=dr): d.line([px(*p) for p in pts], fill=255, width=max(2, round(w * SX)), joint='curve')
def rect(x0, y0, x1, y1, d=dg):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); d.rectangle([px(x0, y1), px(x1, y0)], fill=255)
def ring(cx, cy, r, w=0.4):
    a, b = px(cx - r, cy + r), px(cx + r, cy - r); dr.ellipse([a, b], outline=255, width=max(2, round(w * SX)))
# 平行的旁路波导（淡，避开中央走廊 |x|<9）
for x in (-44, -38, -31, -24, -17, 17, 24, 31, 38, 44):
    y0 = rnd.uniform(-45, -20); y1 = rnd.uniform(15, 38)
    wg([(x, y0), (x, y1)], 0.45)
    # 微环 + 总线
    if rnd.random() < 0.7:
        yy = rnd.uniform(-10, 25); ring(x + (3 if x < 0 else -3), yy, 2.2); 
    wg([(x, y1), (x + (6 if x < 0 else -6), y1 + 4), (x + (6 if x < 0 else -6), 44)], 0.45)
# 光栅耦合器（小条纹）
for x in (-44, -31, 31, 44):
    for k in range(10): rect(x - 2.0, -52 + k * 0.5, x + 2.0, -52 + k * 0.5 + 0.25, dr)
# 焊盘排：左右两侧
for k in range(14):
    y = -48 + k * 6.6
    rect(-49, y, -46, y + 3.2); rect(46, y, 49, y + 3.2)
# 加热器蛇形
for s in (-1, 1):
    for k in range(6): rect(s * 20 - 2, 4 + k * 0.9, s * 20 + 2, 4 + k * 0.9 + 0.35)
# 对准标记
for (x, y) in ((-47, 42), (47, 42), (-47, -52), (47, -52)):
    rect(x - 1.2, y - 0.15, x + 1.2, y + 0.15); rect(x - 0.15, y - 1.2, x + 0.15, y + 1.2)
B = Image.effect_noise((N // 8, N // 8), 40).resize((N, N), Image.BICUBIC).filter(ImageFilter.GaussianBlur(4))
Image.merge('RGB', (R.filter(ImageFilter.GaussianBlur(0.6)), G.filter(ImageFilter.GaussianBlur(0.6)), B)).save(sys.argv[1], optimize=True)
print('ok')
