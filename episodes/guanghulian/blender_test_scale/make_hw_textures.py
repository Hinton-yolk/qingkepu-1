# 生成交换机 / 光模块段的硬件贴图（示例，不对应任何真实产品）。输出到 assets/（gitignore）：
#   pcb_module.png  光模块电路板顶面：R = 阻焊下的铜（走线、铺铜）、G = 裸露金焊盘、B = 丝印、A = 过孔（凸起）
#   perf_hex.png    六边形排列的圆孔冲孔板（可平铺）：白 = 孔
#   rack_holes.png  机柜立柱方孔（EIA-310，一个 U 一块，可沿竖直平铺）：白 = 孔
# 坐标和 shot_scale.py 一致（单位 µm）：模块电路板中心 (0, −1000)，尺寸 17150 × 76000。
import math, random, sys, os
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
HERE = os.path.dirname(os.path.abspath(__file__))
rnd = random.Random(20261110)

# ---------- 1) 光模块电路板 ----------
PW, PL, PY0 = 17150.0, 76000.0, -1000.0
NX = 1200; NY = round(NX * PL / PW)
S = NX / PW
def px(x, y): return ((x + PW / 2) * S, (PY0 + PL / 2 - y) * S)        # 图片 y 向下 = 模块 +y 在上（金手指在图片顶部）
R = Image.new('L', (NX, NY), 0); G = Image.new('L', (NX, NY), 0); B = Image.new('L', (NX, NY), 0); A = Image.new('L', (NX, NY), 0)
dR, dG, dB, dA = (ImageDraw.Draw(i) for i in (R, G, B, A))
def rect(d, x0, y0, x1, y1, v=255, outline=None, w=1):
    (a0, b0), (a1, b1) = px(x0, y1), px(x1, y0)
    if outline is None: d.rectangle([a0, b0, a1, b1], fill=v)
    else: d.rectangle([a0, b0, a1, b1], outline=v, width=w)
def line(d, pts, w_um, v=255): d.line([px(*p) for p in pts], fill=v, width=max(1, round(w_um * S)), joint='curve')
def dot(d, x, y, r_um, v=255):
    cx, cy = px(x, y); r = max(1.0, r_um * S); d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=v)
# 铺铜（大面积，阻焊下稍亮），四周留边
rect(dR, -PW / 2 + 500, PY0 - PL / 2 + 500, PW / 2 - 500, PY0 + PL / 2 - 500, 70)
# 元件区挖空铺铜（走线周围的隔离带画成暗）
def clear(x0, y0, x1, y1): rect(dR, x0, y0, x1, y1, 0)
clear(-6500, 11500, 6500, 24500)                               # DSP 下面
clear(-7400, 24500, 7000, 33300)                                # DSP → 金手指 的高速走线区
clear(-7000, -1500, 7000, 11500)                                # DSP → 驱动 / 芯片
# 高速差分对：DSP 上边 → 金手指（每对两根，间距 150 µm，线宽 100 µm），45° 扇出
FINGER_X = [-7000 + k * 760 + 250 for k in range(19)]
for k, fx in enumerate(FINGER_X):
    if k % 3 == 0: continue                                     # 每 3 根里 1 根是地，不走线
    sx = -5000 + k * (10000 / 18)
    for dx in (-75, 75):
        line(dR, [(sx + dx, 24000), (sx + dx, 26000), (fx + dx * 0.6, 30000), (fx + dx * 0.6, 33500)], 100, 255)
# DSP 下边 → 驱动（8 对）和 → 芯片附近的打线焊盘
for k in range(8):
    sx = -4500 + k * 600
    for dx in (-75, 75):
        if k < 4: line(dR, [(sx + dx, 12000), (sx + dx, 9000), (-5200 + (k - 1.5) * 500 + dx, 5500), (-5200 + (k - 1.5) * 500 + dx, 3500)], 100)
        else: line(dR, [(sx + dx, 12000), (sx + dx, 8500), ((k - 5.5) * 700 + dx, 5200), ((k - 5.5) * 700 + dx, 3300)], 100)
# 激光器供电（较宽的线）
line(dR, [(5800, 12000), (5800, 6000), (4200, 3600), (4200, 2400)], 300)
# 低速 / 电源走线：DSP 左右两侧到金手指边缘
for k in range(5):
    line(dR, [(-6500, 14000 + k * 1600), (-7600, 15000 + k * 1600), (-7600, 33300)], 120, 180)
    line(dR, [(6500, 14000 + k * 1600), (7400, 15000 + k * 1600), (7400, 33300)], 120, 180)
# 金焊盘：芯片两侧打线焊盘、驱动焊盘、电容焊盘（电容几何放在上面）、测试点
for k in range(12): rect(dG, -2700 + k * 450, 2800, -2500 + k * 450, 3200)
for k in range(8): rect(dG, -6900 + k * 450, 3700, -6750 + k * 450, 3950)
for k in range(6): dot(dG, -6000 + k * 2400, -12000, 350)
for k in range(4): dot(dG, -6000 + k * 4000, 28500 if k % 2 else 29000, 300)
# 过孔：DSP 周围的地过孔栅格、走线旁的回流过孔
for y in range(-34000, 33000, 900):
    for x in (-7900, 7900): dot(dA, x, y, 130)
for k in range(60):
    x, y = rnd.uniform(-7500, 7500), rnd.uniform(-30000, 30000)
    if -6500 < x < 6500 and 11500 < y < 24500: continue
    dot(dA, x, y, 130)
for y in range(12500, 24000, 700):
    for x in (-6200, 6200): dot(dA, x, y, 110)
# 丝印：元件框、位号、一脚标记（白色）
for x0, y0, x1, y1, ref in ((-6300, 11800, 6300, 24200, 'U1'), (-6900, 300, -3500, 3700, 'U2'), (3500, 0, 4900, 2400, 'LD1'),
                            (-4800, -39000 + 500, 4800, -33500, 'J1')):
    rect(dB, x0, y0, x1, y1, 255, outline=True, w=max(1, round(120 * S)))
try: fnt = ImageFont.truetype('DejaVuSans.ttf', max(10, round(900 * S)))   # 丝印位号只用拉丁字母（项目里的标签字体是子集，没有这些字）
except Exception: fnt = ImageFont.load_default()
for x, y, t in ((-6000, 25800, 'U1'), (-6800, 5200, 'U2'), (3600, 4000, 'LD1'), (-4600, -32600, 'J1'), (5200, 25800, '1'), (-7600, -20000, 'C17'),
                (6100, -14000, 'C23'), (-7600, -4000, 'R8'), (5900, 30800, 'TP4')):
    dB.text(px(x, y), t, fill=255, font=fnt)
dot(dB, -6600, 24600, 220)                                      # 一脚标记
# 模块前半段（芯片 → MPO 之间，光纤带走这里）：几根低速线、电源铺铜的过孔、电容丝印框
for k in range(4): line(dR, [(-7200 + k * 300, -2000), (-7200 + k * 300, -30000)], 120, 180)
for k in range(3): line(dR, [(6400 + k * 300, -2000), (6400 + k * 300, -30000)], 120, 180)
for y in range(-30000, -3000, 1500):
    for x in (-4500, 4500): dot(dA, x, y, 120)
for x0, y0 in ((-6900, -9000), (-6900, -16000), (5600, -11000), (5600, -21000)): rect(dB, x0, y0, x0 + 1300, y0 + 700, 255, outline=True, w=1)
out = Image.merge('RGBA', (R, G, B, A)); out.save(os.path.join(OUT, 'pcb_module.png'), optimize=True)

# ---------- 2) 冲孔板（六边形排列圆孔，可平铺）：一块 = 10 列 × 12 行，孔距 p，行距 p·√3/2 ----------
P = 64; Wp = 10 * P; Hp = round(12 * P * math.sqrt(3) / 2)
perf = Image.new('L', (Wp * 2, Hp * 2), 0); d = ImageDraw.Draw(perf); r = P * 0.36 * 2
for j in range(-1, 13):
    for i in range(-1, 12):
        cx = (i * P + (P / 2 if j % 2 else 0)) * 2; cy = j * P * math.sqrt(3) / 2 * 2
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
perf.resize((Wp, Hp), Image.LANCZOS).save(os.path.join(OUT, 'perf_hex.png'), optimize=True)

# ---------- 3) 机柜立柱方孔（EIA-310）：一个 U = 44.45 mm，孔中心在 6.35 / 22.225 / 38.1 mm，方孔 9.5 mm ----------
RW, RH = 256, 455                                              # 立柱正面 25 mm 宽 × 一个 U
rk = Image.new('L', (RW, RH), 0); d = ImageDraw.Draw(rk); s = RH / 44.45
for c in (6.35, 22.225, 38.1):
    cy = RH - c * s; h = 9.5 * s / 2; d.rectangle([RW / 2 - h, cy - h, RW / 2 + h, cy + h], fill=255)
rk.save(os.path.join(OUT, 'rack_holes.png'), optimize=True)
print('ok', (NX, NY), (Wp, Hp), (RW, RH))
