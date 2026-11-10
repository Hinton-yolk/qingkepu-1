# 内容关卡 2 草稿 v2：原稿 14 句，每句一帧（背景 = Blender 草稿静帧；叠加 = 沿走线透视画的刻度、鼓点、计数）
# 按审核 11-10 必改：演示长在走线上（用 Blender 导出的走线位置和每一位的边界）；鼓点只在跳变处；y11 用「每个比特的耗电」；
# y9 按 1 : 2 : 4；五站条常驻（y ≈ 200/1920）；字幕按原稿分段一次一行；字和条都避开抖音右侧按钮区。
import os, json
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); BO = os.path.join(HERE, '..', 'blender', 'out')
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'; W, H = 540, 960; SAFE_R = int(W * 0.84)
SC = {x['id']: x for x in json.load(open(os.path.join(HERE, '..', '..', '抖音版_上下集', '配音', 'script_x.json')))}
GOLD = (255, 170, 40); RED = (235, 70, 60); WHITE = (245, 245, 240); GREY = (170, 170, 170)
def f(n): return ImageFont.truetype(FONT, n)
def bg(name):
    im = Image.open(os.path.join(BO, name + '.png')).convert('RGB'); s = W / im.width
    js = os.path.join(BO, name + '.json'); band = None
    if os.path.exists(js):
        band = json.load(open(js))
        for p in band['pts']:
            for k in ('x', 'yy', 'lx', 'ly'): p[k] *= s
    return im.resize((W, H), Image.LANCZOS), band
def text(d, xy, s, size, fill=WHITE, anchor='mm', stroke=4):
    d.text(xy, s, font=f(size), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
def tag(d, s):
    d.rounded_rectangle([12, 52, 12 + 15 * len(s) + 20, 84], 8, fill=(200, 40, 40)); d.text((22, 68), s, font=f(16), fill=WHITE, anchor='lm')
def route(d, x=24, y=100, here=True):                 # 五站条（快递叫法），第一站亮；常驻在 y ≈ 200/1920
    names = ['打包出发', '路上', '中转', '干线', '签收']; step = 74
    d.rounded_rectangle([x - 12, y - 18, x + step * 4 + 46, y + 34], 12, fill=(16, 16, 18))
    d.line([(x + 18, y), (x + 18 + step * 4, y)], fill=(80, 80, 80), width=2)
    for i, n in enumerate(names):
        cx = x + 18 + i * step; d.ellipse([cx - 7, y - 7, cx + 7, y + 7], fill=GOLD if i == 0 else (90, 90, 90))
        d.text((cx, y + 20), n, font=f(15), fill=WHITE if i == 0 else (150, 150, 150), anchor='mm')
    return x + 18                                     # 第一站的 x（「你在这里」对准它）
def norm(p):                                          # 走线在这一点的「横向」方向（画刻度用）
    vx, vy = p['lx'] - p['x'], p['ly'] - p['yy']; L = max(1e-6, (vx * vx + vy * vy) ** 0.5); return vx / L, vy / L
def on_screen(p, m=6): return m < p['x'] < SAFE_R and 150 < p['yy'] < H * 0.70
def ticks(d, band, col=WHITE, every=1, scale=1.0, shift=None, width=3):
    pts = [p for p in band['pts'] if on_screen(p)]
    for i, p in enumerate(pts):
        if i % every: continue
        q = pts[min(i + 1, len(pts) - 1)] if i + 1 < len(pts) else pts[max(i - 1, 0)]
        sp = ((q['x'] - p['x']) ** 2 + (q['yy'] - p['yy']) ** 2) ** 0.5   # 相邻两位在画面上的距离：越远越短（跟着透视）
        nx, ny = norm(p); L = max(3, min(22, sp * 0.9)) * scale
        x, y = p['x'], p['yy']
        if shift: x, y = x + shift(i)[0], y + shift(i)[1]
        d.line([(x - nx * L, y - ny * L), (x + nx * L, y + ny * L)], fill=col, width=width)
def transitions(band):
    pts = band['pts']; return [pts[i] for i in range(1, len(pts)) if pts[i]['bit'] != pts[i - 1]['bit'] and on_screen(pts[i])]
def runs(band, n=5):
    pts = band['pts']; out = []; i = 0
    while i < len(pts):
        j = i
        while j + 1 < len(pts) and pts[j + 1]['bit'] == 1 and pts[i]['bit'] == 1: j += 1
        if pts[i]['bit'] == 1 and j - i + 1 == n: out.append(pts[i:j + 2] if j + 1 < len(pts) else pts[i:j + 1])
        i = j + 1
    return out
def subtitle_frames(k, im, draw):
    """一句拆成原稿的字幕分段，每段一帧（一次一行，y ≈ 1400/1920）"""
    outs = []
    for seg in SC[k]['sub']:
        fr = im.copy(); d = ImageDraw.Draw(fr); draw(d); route(d)
        text(d, (W // 2, int(H * 0.73)), seg, 25 if len(seg) <= 18 else 22, stroke=3); text(d, (W - 30, 22), k, 16, fill=(255, 220, 120), stroke=2)
        outs.append((seg, fr))
    return outs
BEATS = []
def beat(k, im, draw): BEATS.append((k, subtitle_frames(k, im, draw)))

im, _ = bg('A_f0040')
beat('y1', im, lambda d: (text(d, (W // 2, 205), '芯片是怎么数清', 44), text(d, (W // 2, 258), '0 和 1 的？', 44, fill=GOLD)))
im, _ = bg('B_f0110')
beat('y2', im, lambda d: (text(d, (W // 2, 190), '机房 · AI 服务器主板', 22), text(d, (W // 2, 640), '示意：金色光带 = 两根线之间的电压差，亮 = 1、暗 = 0', 14, fill=GOLD, stroke=2)))
im, band3 = bg('B_side_A_normal')
def y3(d):
    hx, hy = band3['host_head']; hx *= W / band3['W']; hy *= H / band3['H']
    d.rounded_rectangle([hx - 175, hy + 10, hx - 55, hy + 58], 16, fill=(250, 250, 245)); d.text((hx - 115, hy + 34), '4？5？', font=f(28), fill=(30, 30, 30), anchor='mm')
    for r in runs(band3)[:1]:
        a, b = r[0], r[-1]; nx, ny = norm(a); o = 14
        d.line([(a['x'] - nx * o, a['yy'] - ny * o), (b['x'] - nx * o, b['yy'] - ny * o)], fill=GOLD, width=4)
        text(d, ((a['x'] + b['x']) / 2 + 10, (a['yy'] + b['yy']) / 2 - 34), '连成一片的高电平', 20, fill=GOLD)
beat('y3', im, y3)
im, band4 = bg('B_side_B_normal')
def y4(d):
    ticks(d, band4, col=WHITE); pts = [p for p in band4['pts'] if on_screen(p)]
    if pts:                                          # 「时钟线」：走线旁边虚线画一对，被划掉
        a, b = pts[0], pts[-1]; nx, ny = norm(a); o = 36
        for t in range(0, 20, 2):
            x0 = a['x'] + (b['x'] - a['x']) * t / 20 + nx * o; y0 = a['yy'] + (b['yy'] - a['yy']) * t / 20 + ny * o
            x1 = a['x'] + (b['x'] - a['x']) * (t + 1) / 20 + nx * o; y1 = a['yy'] + (b['yy'] - a['yy']) * (t + 1) / 20 + ny * o
            d.line([(x0, y0), (x1, y1)], fill=GREY, width=3)
        mx_, my_ = (a['x'] + b['x']) / 2 + nx * o, (a['yy'] + b['yy']) / 2 + ny * o
        d.line([(mx_ - 18, my_ - 18), (mx_ + 18, my_ + 18)], fill=RED, width=5); d.line([(mx_ - 18, my_ + 18), (mx_ + 18, my_ - 18)], fill=RED, width=5)
        text(d, (W // 2, 560), '不另外送节拍器（时钟线）', 20)
    text(d, (W // 2, 190), '每一位占的时间 = 一拍', 22)
beat('y4', im, y4)
im, band5 = bg('B_side_B_normal')
def y5(d):
    tag(d, '姿势 C：拍手（待生成）')
    for p in transitions(band5): d.ellipse([p['x'] - 6, p['yy'] - 6, p['x'] + 6, p['yy'] + 6], fill=GOLD)
    text(d, (W // 2, 190), '♪  跟着鼓点拍手', 24, fill=GOLD)
beat('y5', im, y5)
im, band6 = bg('B_count_B_normal')
def y6(d):
    for p in transitions(band6): d.ellipse([p['x'] - 13, p['yy'] - 13, p['x'] + 13, p['yy'] + 13], outline=GOLD, width=4)
    ticks(d, band6, col=WHITE, width=2)
    for r in runs(band6)[:1]:
        for n in range(5):
            a, b = r[n], r[min(n + 1, len(r) - 1)]; text(d, ((a['x'] + b['x']) / 2, (a['yy'] + b['yy']) / 2 - 22), str(5 - n), 20, fill=GOLD)   # 信号往左跑向芯片：先到的在左边，从左往右数
    text(d, (W // 2, 190), '五个，不是四个', 30, fill=GOLD)
beat('y6', im, y6)
im, band7 = bg('B_count_B_long')
def y7(d):
    tag(d, '姿势 D：惊讶（待生成）')
    ticks(d, band7, col=GREY, width=2)                                       # 真实的节拍
    ticks(d, band7, col=RED, width=3, shift=lambda i: (0.35 * i * i ** 0.5, 0.0))     # 没有鼓点校准：拍子越走越偏
    text(d, (W // 2, 190), '没有鼓点，拍子跑偏', 26, fill=RED); text(d, (W // 2, 225), '灰 = 真实节拍  红 = 芯片数的拍', 16, stroke=2)
beat('y7', im, y7)
im, band8 = bg('B_count_B_normal')
def y8(d):
    for p in transitions(band8): d.ellipse([p['x'] - 9, p['yy'] - 9, p['x'] + 9, p['yy'] + 9], outline=GOLD, width=3)
    text(d, (W // 2, 190), '打乱以后：鼓点一直都在', 24, fill=GOLD); text(d, (W // 2, 225), '到对面：按同样的规则还原 ↺', 20)
beat('y8', im, y8)
im, band9 = bg('B_close_B_normal')
def y9(d):
    pts = [p for p in band9['pts'] if on_screen(p)]
    if len(pts) > 6:                                  # 同一段走线上，每一代一拍的长度减半（1 : 2 : 4）
        a, b = pts[0], pts[4]
        for row, (lab, sub) in enumerate((('1×', 1), ('2×', 2), ('4×', 4))):
            o = -30 + row * 30; nx, ny = norm(a)
            for t in range(4 * sub + 1):
                x = a['x'] + (b['x'] - a['x']) * t / (4 * sub) + nx * o * 2.2; y = a['yy'] + (b['yy'] - a['yy']) * t / (4 * sub) + ny * o * 2.2
                d.line([(x - 6, y - 6), (x + 6, y + 6)], fill=GOLD, width=2)
            text(d, (a['x'] + nx * o * 2.2 - 30, a['yy'] + ny * o * 2.2), lab, 18, fill=GOLD, stroke=2)
    text(d, (W // 2, 190), '速度翻倍：一拍的时间减半', 22)
beat('y9', im, y9)
im, _ = bg('B_rx_B_normal_xray')
def y10(d):
    text(d, (W // 2, 190), '修信号的电路（示意）', 24, fill=GOLD); text(d, (W // 2, 225), '要耗电、占面积', 20)
beat('y10', im, y10)
im, _ = bg('B_wide_B_normal')
def y11(d):
    for x0, lab, lvl, col in ((300, '速度', 0.85, WHITE), (400, '每个比特的耗电', 0.35, GOLD)):
        d.rectangle([x0, 230, x0 + 34, 520], outline=WHITE, width=2); d.rectangle([x0 + 3, 517 - int(284 * lvl), x0 + 31, 517], fill=col)
        text(d, (x0 + 17, 545), lab, 16, stroke=2)
    text(d, (x0 - 70, 200), '↑ 速度　↓ 每比特耗电', 20, fill=GOLD)
beat('y11', im, y11)
im, _ = bg('A_f0020_g0')
beat('y12', im, lambda d: text(d, (W // 2, 205), '每秒上千亿个比特', 34, fill=GOLD))
card = Image.new('RGB', (W, H), (18, 18, 20))
def y13(d):
    text(d, (W // 2, 300), '一句话带走', 42, fill=GOLD); text(d, (W // 2, 390), '发出去：排成一列', 30); text(d, (W // 2, 445), '收进来：听准节拍、拆回一排', 30)
    fx = route(d, 120, 560); text(d, (fx, 612), '你在这里', 16, fill=GOLD, stroke=2)
beat('y13', card, y13)
im, _ = bg('B_close_B_blur')
beat('y14', im, lambda d: (tag(d, '姿势 E：站起来（待生成）'), text(d, (W // 2, 190), '下一篇：信号为什么越跑越模糊？', 22)))

os.makedirs(os.path.join(HERE, 'beats'), exist_ok=True); man = []
for k, segs in BEATS:
    for n, (seg, fr) in enumerate(segs): fn = f'{k}_{n}.png'; fr.save(os.path.join(HERE, 'beats', fn)); man.append(dict(id=k, n=n, seg=seg, file=fn))
json.dump(man, open(os.path.join(HERE, 'beats', 'manifest.json'), 'w'), ensure_ascii=False)
tw, th = W // 2, H // 2; sheet = Image.new('RGB', (tw * 7, th * 2))
for i, (k, segs) in enumerate(BEATS): sheet.paste(segs[min(1, len(segs) - 1)][1].resize((tw, th), Image.LANCZOS), ((i % 7) * tw, (i // 7) * th))
sheet.save(os.path.join(HERE, '下集_草稿接触表_v2.jpg'), quality=86); print('ok', len(BEATS), len(man))
