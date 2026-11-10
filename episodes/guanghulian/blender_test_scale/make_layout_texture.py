# 生成 5 mm 硅光芯片表面的版图贴图（示例，不对应真实产品）：4096 px ≈ 1.22 µm/px。
# 通道：R = 硅器件（波导、光栅、探测器），G = 金属（电极、焊盘、加热器），B = 轻微的表面明暗变化，A = 亮着的光路（发射通道）。
# 坐标和 shot_scale.py 一致：芯片 x、y ∈ [−2500, 2500] µm，前边缘 y = −2500，光纤 x = 250·(i−3)。
import random, math, sys
from PIL import Image, ImageDraw, ImageFilter
N = 4096; S = N / 5000.0
def px(x, y): return ((x + 2500) * S, (2500 - y) * S)          # 图片 y 向下
R = Image.new('L', (N, N), 0); G = Image.new('L', (N, N), 0); A = Image.new('L', (N, N), 0)
dr, dg, da = ImageDraw.Draw(R), ImageDraw.Draw(G), ImageDraw.Draw(A)
rnd = random.Random(20261110)
def wg(points, w=1.0):                                           # 波导折线（最少 1 px）
    dr.line([px(*p) for p in points], fill=255, width=max(1, round(w * S)))
def rect(d, x0, y0, x1, y1, v=255):
    a, b = px(x0, y1), px(x1, y0); d.rectangle([a, b], fill=v)
FX = [250.0 * (i - 3) for i in range(8)]
EDGE = -2500.0
# 1) 8 路发射通道：边缘耦合 → 直波导 → MZM（金电极两侧）→ 弯到中部
for i, x in enumerate(FX):
    wg([(x, EDGE), (x, EDGE + 1600)]); da.line([px(x, EDGE), px(x, EDGE + 1600)], fill=255, width=2)
    rect(dg, x - 14, EDGE + 165, x - 4, EDGE + 1165); rect(dg, x + 4, EDGE + 165, x + 14, EDGE + 1165)   # MZM 电极（和几何一致）
    rect(dg, x - 40, EDGE + 1175, x + 40, EDGE + 1255)                                                   # 电极引线
    # 弯道：S 弯向中部合波区
    pts = []; tx = -600 + i * 60
    for k in range(41):
        u = k / 40; y = EDGE + 1600 + 900 * u; xx = x + (tx - x) * (0.5 - 0.5 * math.cos(math.pi * u)); pts.append((xx, y))
    wg(pts); da.line([px(*p) for p in pts], fill=200, width=2)
    wg([(tx, EDGE + 2500), (tx, 400)])
# 2) 中部：合波 / 复用区（一组平行波导 + 方形器件）、微加热器折线
for k in range(8): rect(dr, -700 + k * 60, 400, -680 + k * 60, 700)
rect(dr, -760, 700, -220, 760)
for k in range(6):
    yy = 900 + k * 120; dg.line([px(-1800, yy), px(-1200, yy), px(-1200, yy + 60), px(-1800, yy + 60)], fill=200, width=max(1, round(3 * S)))
# 3) 接收通道：光栅耦合器（小扇形）+ 探测器 + 焊盘，在右半边
for i in range(8):
    y = -1400 + i * 260
    rect(dr, 1200, y - 6, 1230, y + 6)                    # 光栅
    wg([(1230, y), (1700, y)]); rect(dr, 1700, y - 15, 1760, y + 15)   # 探测器
    rect(dg, 1800, y - 40, 1880, y + 40)                 # 焊盘
# 4) 四周焊盘
for k in range(30): rect(dg, -2300 + k * 150, 2310, -2220 + k * 150, 2390)
for k in range(28): rect(dg, 2310, -2100 + k * 150, 2390, -2020 + k * 150)
for k in range(28): rect(dg, -2390, -2100 + k * 150, -2310, -2020 + k * 150)
# 5) 零散器件：测试结构、对准标记、微环阵列（小圈）
for k in range(60):
    x, y = rnd.uniform(-2200, 2200), rnd.uniform(-1000, 2100)
    if -900 < x < 300 and y < 800: continue
    r = rnd.uniform(5, 20); a, b = px(x - r, y + r), px(x + r, y - r); dr.ellipse([a, b], outline=255, width=1)
    wg([(x - 60, y - r - 1), (x + 60, y - r - 1)])
for (x, y) in ((-2200, 2200), (2200, 2200), (-2200, -2200), (2200, -2200)):
    rect(dg, x - 40, y - 5, x + 40, y + 5); rect(dg, x - 5, y - 40, x + 5, y + 40)
# 6) 表面明暗：很淡的大尺度起伏（工艺不均匀）
B = Image.effect_noise((N // 8, N // 8), 40).resize((N, N), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))
out = Image.merge('RGBA', (R, G, B, A))
out.save(sys.argv[1] if len(sys.argv) > 1 else 'assets/chip_layout.png', optimize=True)
print('ok')
