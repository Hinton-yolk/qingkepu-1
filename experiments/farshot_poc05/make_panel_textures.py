"""程序生成机柜里设备前面板的贴图（示意，不是某个真实型号）。

每种面板出两张图：颜色图（*_col.png）和指示灯发光遮罩（*_led.png，RGB = 灯的颜色，黑 = 不发光）。
19 英寸设备：面板宽 482.6 mm（含挂耳）；1U = 44.45 mm 高。按 4.4 px/mm 出图。
输出到 assets_dl/（不进仓库），用法：python3 make_panel_textures.py
"""
import os
import random

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assets_dl')
os.makedirs(OUT, exist_ok=True)
S = 4.4                       # px / mm
W_MM, U_MM = 482.6, 44.45
random.seed(11)

BASE = (38, 40, 44)           # 深灰喷涂面板
EAR = (52, 54, 58)
HOLE = (6, 6, 7)
CADDY = (88, 90, 96)          # 硬盘托架
GREEN, BLUE, AMBER, WHITE = (60, 255, 110), (70, 150, 255), (255, 170, 40), (230, 240, 255)


def px(v):
    return int(round(v * S))


def new(units):
    w, h = px(W_MM), px(U_MM * units)
    col = Image.new('RGB', (w, h), BASE)
    led = Image.new('RGB', (w, h), (0, 0, 0))
    dc, dl = ImageDraw.Draw(col), ImageDraw.Draw(led)
    for x0 in (0, W_MM - 18):                         # 挂耳和螺丝孔
        dc.rectangle([px(x0), 0, px(x0 + 18), h], fill=EAR)
        for k in range(units):
            cy = U_MM * k + U_MM / 2
            dc.ellipse([px(x0 + 6), px(cy - 3), px(x0 + 12), px(cy + 3)], fill=HOLE)
    return col, led, dc, dl, w, h


def vents(dc, x0, y0, x1, y1, pitch=3.2, r=1.0):
    """六角排列的圆形通风孔。"""
    row = 0
    y = y0 + r
    while y < y1 - r:
        x = x0 + r + (pitch / 2 if row % 2 else 0)
        while x < x1 - r:
            dc.ellipse([px(x - r), px(y - r), px(x + r), px(y + r)], fill=HOLE)
            x += pitch
        y += pitch * 0.866
        row += 1


def led_dot(dl, dc, x, y, c, on=True, r=1.1):
    dc.ellipse([px(x - r), px(y - r), px(x + r), px(y + r)], fill=(20, 22, 24))
    if on:
        dl.ellipse([px(x - r), px(y - r), px(x + r), px(y + r)], fill=c)


def server_1u(name):
    col, led, dc, dl, w, h = new(1)
    vents(dc, 22, 4, 150, U_MM - 4)
    for i in range(8):                               # 8 个 2.5 寸盘位（竖排托架）
        x = 160 + i * 25
        dc.rectangle([px(x), px(4), px(x + 22), px(U_MM - 4)], fill=CADDY)
        dc.rectangle([px(x + 2), px(6), px(x + 20), px(U_MM - 12)], fill=(70, 72, 78))
        led_dot(dl, dc, x + 6, U_MM - 7, GREEN, random.random() < 0.9)
        led_dot(dl, dc, x + 15, U_MM - 7, BLUE, random.random() < 0.3)
    vents(dc, 365, 4, 440, U_MM - 4)
    led_dot(dl, dc, 452, 12, BLUE)
    led_dot(dl, dc, 452, 22, GREEN)
    led_dot(dl, dc, 452, 32, AMBER, random.random() < 0.15)
    col.save(os.path.join(OUT, f'{name}_col.png'))
    led.save(os.path.join(OUT, f'{name}_led.png'))


def server_2u(name):
    col, led, dc, dl, w, h = new(2)
    for r in range(2):                                # 24 个 2.5 寸盘位，两排
        for i in range(12):
            x, y = 24 + i * 30, 5 + r * 42
            dc.rectangle([px(x), px(y), px(x + 27), px(y + 38)], fill=CADDY)
            dc.rectangle([px(x + 2), px(y + 2), px(x + 25), px(y + 28)], fill=(66, 68, 74))
            vents(dc, x + 3, y + 3, x + 24, y + 27, pitch=2.6, r=0.7)
            led_dot(dl, dc, x + 7, y + 33, GREEN, random.random() < 0.92)
            led_dot(dl, dc, x + 18, y + 33, BLUE, random.random() < 0.25)
    vents(dc, 392, 6, 440, U_MM * 2 - 6)
    for k, c in enumerate((BLUE, GREEN, GREEN, AMBER)):
        led_dot(dl, dc, 452, 14 + k * 16, c, c != AMBER or random.random() < 0.2)
    col.save(os.path.join(OUT, f'{name}_col.png'))
    led.save(os.path.join(OUT, f'{name}_led.png'))


def switch_1u(name, ports=32, tab=True):
    """1U 交换机：上下两排 OSFP 口（示意），口里插着带绿色拉环的模块，口旁边是链路灯。"""
    col, led, dc, dl, w, h = new(1)
    n = ports // 2
    pitch = (W_MM - 60) / n
    for r in range(2):
        for i in range(n):
            x = 24 + i * pitch
            y = 3 + r * 20
            dc.rectangle([px(x), px(y), px(x + pitch - 3), px(y + 17)], fill=(150, 152, 156))   # 笼口边框
            dc.rectangle([px(x + 1), px(y + 1.5), px(x + pitch - 4), px(y + 15.5)], fill=(18, 18, 20))
            if tab and random.random() < 0.8:                 # 插着的模块：银色前端 + 绿色拉环
                dc.rectangle([px(x + 2), px(y + 3), px(x + pitch - 5), px(y + 14)], fill=(170, 172, 176))
                dc.rectangle([px(x + 4), px(y + 5), px(x + pitch - 7), px(y + 12)], fill=(25, 26, 28))
                dc.rectangle([px(x + 1), px(y + 13), px(x + pitch - 4), px(y + 16)], fill=(130, 200, 30))
                led_dot(dl, dc, x + pitch - 2.2, y + 3, GREEN, random.random() < 0.85, r=0.7)
    led_dot(dl, dc, W_MM - 26, 10, BLUE)
    led_dot(dl, dc, W_MM - 26, 22, GREEN)
    col.save(os.path.join(OUT, f'{name}_col.png'))
    led.save(os.path.join(OUT, f'{name}_led.png'))


def blank_1u(name):
    col, led, dc, dl, w, h = new(1)
    vents(dc, 22, 6, W_MM - 22, U_MM - 6, pitch=5.0, r=1.4)
    col.save(os.path.join(OUT, f'{name}_col.png'))
    led.save(os.path.join(OUT, f'{name}_led.png'))


def floor_tile():
    """600 mm 活动地板：浅灰面层 + 接缝；另出一张开孔的通风地板。"""
    n = 1200
    for name, perf in (('tile', False), ('tile_perf', True)):
        im = Image.new('RGB', (n, n), (150, 152, 156))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, n - 1, n - 1], outline=(70, 72, 76), width=6)
        if perf:
            for y in range(60, n - 60, 22):
                for x in range(60, n - 60, 22):
                    d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(30, 32, 34))
        im.save(os.path.join(OUT, f'{name}_col.png'))


for i in range(3):
    server_1u(f'srv1u_{i}')
    server_2u(f'srv2u_{i}')
switch_1u('sw1u_osfp')
blank_1u('blank1u')
floor_tile()
print('ok', sorted(os.listdir(OUT)))
