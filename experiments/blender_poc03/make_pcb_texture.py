"""生成网卡 PCB 表面的贴图（程序生成，非真实版图）。

输出三张 4096×4096 灰度图，覆盖板面 120 mm × 120 mm（1 像素约 0.03 mm）：
  assets_dl/pcb_trace_mask.png  走线（阻焊层下的铜，画面上是略浅的绿色凸起）
  assets_dl/pcb_pad_mask.png    裸露焊盘和过孔环（沉金，金色）
  assets_dl/pcb_silk_mask.png   白色丝印（元件框和位号示意）
用法：python3 make_pcb_texture.py
"""
import os
import random

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
N = 4096
SIZE_MM = 120.0
PX = N / SIZE_MM
random.seed(7)

trace = Image.new('L', (N, N), 0)
pad = Image.new('L', (N, N), 0)
silk = Image.new('L', (N, N), 0)
dt, dp, ds = ImageDraw.Draw(trace), ImageDraw.Draw(pad), ImageDraw.Draw(silk)


def p(xmm, ymm):
    return (xmm * PX, ymm * PX)


# 差分走线束：多条平行线，45° 折角，像高速信号线
for _ in range(26):
    x, y = random.uniform(5, 115), random.uniform(5, 115)
    n = random.choice([2, 4, 6, 8])
    gap = random.choice([0.35, 0.45, 0.6])
    w = random.choice([0.12, 0.15, 0.2])
    segs = []
    for _ in range(random.randint(2, 4)):
        d = random.choice([(1, 0), (0, 1), (1, 1), (1, -1), (-1, 0), (0, -1)])
        L = random.uniform(6, 30)
        segs.append((d, L))
    for k in range(n):
        off = k * gap
        cx, cy = x + off, y
        pts = [p(cx, cy)]
        for (dx, dy), L in segs:
            cx, cy = cx + dx * L, cy + dy * L
            pts.append(p(cx, cy))
        dt.line(pts, fill=255, width=max(1, int(w * PX)), joint='curve')

# 散布的单根细线
for _ in range(160):
    x, y = random.uniform(0, 120), random.uniform(0, 120)
    L = random.uniform(2, 12)
    d = random.choice([(1, 0), (0, 1), (0.707, 0.707)])
    dt.line([p(x, y), p(x + d[0] * L, y + d[1] * L)], fill=200, width=max(1, int(0.1 * PX)))

# 过孔：金色小环
for _ in range(700):
    x, y = random.uniform(1, 119), random.uniform(1, 119)
    r = random.choice([0.25, 0.3, 0.35])
    dp.ellipse([p(x - r, y - r), p(x + r, y + r)], fill=255)
    dp.ellipse([p(x - r * 0.45, y - r * 0.45), p(x + r * 0.45, y + r * 0.45)], fill=40)

# 裸露焊盘阵列（没有放元件的位置）
for _ in range(60):
    x, y = random.uniform(3, 117), random.uniform(3, 117)
    for k in range(random.choice([2, 4, 6])):
        dp.rectangle([p(x + k * 0.8, y), p(x + k * 0.8 + 0.45, y + 0.9)], fill=255)

# 丝印：元件框和位号一类的白色小标记（示意，不是真实文字）
for _ in range(220):
    x, y = random.uniform(2, 118), random.uniform(2, 118)
    w, h = random.choice([(2.2, 1.4), (1.6, 1.0), (5.5, 5.5), (3.2, 2.0)])
    ds.rectangle([p(x, y), p(x + w, y + h)], outline=255, width=max(1, int(0.12 * PX)))
    for k in range(random.randint(2, 4)):          # 位号：几个小笔画
        xx = x + k * 0.55
        ds.rectangle([p(xx, y - 0.9), p(xx + 0.35, y - 0.35)], outline=230, width=max(1, int(0.08 * PX)))
silk.save(os.path.join(HERE, 'assets_dl', 'pcb_silk_mask.png'))
trace.save(os.path.join(HERE, 'assets_dl', 'pcb_trace_mask.png'))
pad.save(os.path.join(HERE, 'assets_dl', 'pcb_pad_mask.png'))
print('ok')
