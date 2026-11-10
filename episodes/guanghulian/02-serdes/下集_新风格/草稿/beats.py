# 内容关卡 2 草稿：原稿 14 句，每句一帧（背景 = Blender 草稿静帧；字和示意 = 简单叠加，正式版在引擎里做动画）
import os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); BO = os.path.join(HERE, '..', 'blender', 'out')
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'; W, H = 540, 960
S = {x['id']: x['text'] for x in json.load(open(os.path.join(HERE, '..', '..', '抖音版_上下集', '配音', 'script_x.json')))}
GOLD = (255, 170, 40); RED = (235, 70, 60); WHITE = (245, 245, 240)
def f(n): return ImageFont.truetype(FONT, n)
def bg(name, blur=0):
    im = Image.open(os.path.join(BO, name + '.png')).convert('RGB').resize((W, H), Image.LANCZOS)
    return im.filter(ImageFilter.GaussianBlur(blur)) if blur else im
def text(d, xy, s, size, fill=WHITE, anchor='mm', stroke=4):
    d.text(xy, s, font=f(size), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
def subtitle(d, s):                                   # 抖音字幕位置：约 y = 1400 / 1920
    lines = [s[i:i + 16] for i in range(0, len(s), 16)]
    for k, ln in enumerate(lines): text(d, (W // 2, int(H * 0.73) + k * 34), ln, 26, stroke=3)
def tag(d, s):                                        # 待做的东西（姿势还没生成等）
    d.rounded_rectangle([12, 12, 12 + 15 * len(s) + 20, 46], 8, fill=(200, 40, 40)); d.text((22, 29), s, font=f(17), fill=WHITE, anchor='lm')
def route(d, x, y):                                   # 快递路线小图：五站，第一站亮
    names = ['打包出发', '路上', '中转', '干线', '签收']
    d.rounded_rectangle([x - 8, y - 22, x + 270, y + 30], 10, fill=(20, 20, 22))
    for i, n in enumerate(names):
        cx = x + 14 + i * 62; d.ellipse([cx - 7, y - 7, cx + 7, y + 7], fill=GOLD if i == 0 else (90, 90, 90))
        d.text((cx, y + 20), n, font=f(12), fill=WHITE if i == 0 else (150, 150, 150), anchor='mm')
def ticks(d, x0, x1, y, n, col=WHITE, skew=0):
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n + skew * i * i; d.line([(x, y - 14), (x, y + 14)], fill=col, width=3)
    d.line([(x0, y), (x1 + skew * n * n, y)], fill=col, width=2)
def wave(d, x0, y, bits, w, hgt, col):
    pts = []; x = x0
    for b in bits: yy = y - hgt if b else y; pts += [(x, yy), (x + w, yy)]; x += w
    d.line(pts, fill=col, width=4, joint='curve')
frames = []
def beat(k, im, draw):
    d = ImageDraw.Draw(im); draw(d); subtitle(d, S[k]); text(d, (W - 40, 30), k, 18, fill=(255, 220, 120)); frames.append(im)
beat('y1', bg('A_f0040'), lambda d: (text(d, (W // 2, 170), '芯片是怎么数清', 50), text(d, (W // 2, 232), '0 和 1 的？', 50, fill=GOLD)))
beat('y2', bg('B_f0110'), lambda d: route(d, 20, 120))
def y3(d):
    d.rounded_rectangle([170, 190, 300, 250], 18, fill=(250, 250, 245)); text(d, (235, 220), '4？5？', 34, fill=(30, 30, 30), stroke=0)
    d.line([(300, 640), (535, 700)], fill=GOLD, width=3); text(d, (420, 610), '连成一片的高电平', 22, fill=GOLD)
beat('y3', bg('B_side_A'), y3)
def y4(d):
    ticks(d, 60, 480, 330, 8)
    d.polygon([(70, 520), (120, 520), (95, 430)], outline=WHITE, width=3); d.line([(95, 505), (115, 445)], fill=WHITE, width=3)
    d.line([(60, 420), (130, 530)], fill=RED, width=6); d.line([(130, 420), (60, 530)], fill=RED, width=6); text(d, (200, 560), '不另外送节拍器', 22)
beat('y4', bg('B_side_B'), y4)
def y5(d):
    tag(d, '姿势 C：拍手（待生成）')
    for i in range(6): d.ellipse([90 + i * 70, 300, 106 + i * 70, 316], fill=GOLD)
    text(d, (W // 2, 360), '听着鼓点，自然就跟上了', 26)
beat('y5', bg('B_side_B'), y5)
def y6(d):
    for x in (215, 300, 360, 410): d.ellipse([x - 14, 600 - 14, x + 14, 600 + 14], outline=GOLD, width=4)
    ticks(d, 120, 470, 300, 5, col=GOLD); text(d, (W // 2, 250), '五个，不是四个', 32, fill=GOLD)
beat('y6', bg('B_close_B'), y6)
def y7(d):
    tag(d, '姿势 D：惊讶（待生成）'); ticks(d, 80, 420, 300, 6, col=RED, skew=0.9); text(d, (W // 2, 250), '没有鼓点，拍子跑偏', 28, fill=RED)
beat('y7', bg('B_close_B'), y7)
def y8(d):
    d.rounded_rectangle([40, 170, 500, 420], 14, fill=(15, 15, 18))
    wave(d, 70, 260, [1] * 12, 34, 40, (150, 150, 150)); text(d, (270, 200), '一长串 1：没有鼓点', 20)
    wave(d, 70, 380, [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1], 34, 40, GOLD); text(d, (270, 320), '打乱以后：鼓点一直都在', 20, fill=GOLD)
beat('y8', bg('B_close_B'), y8)
def y9(d):
    for i, (s, c) in enumerate((('1×', (150, 150, 150)), ('2×', (220, 180, 90)), ('4×', GOLD))):
        d.rounded_rectangle([60 + i * 150, 330 - i * 50, 190 + i * 150, 400], 8, fill=c); text(d, (125 + i * 150, 300 - i * 50), s, 30)
    text(d, (W // 2, 190), 'SerDes：串行收发电路', 22)
beat('y9', bg('B_wide_B'), y9)
def y10(d):
    d.rectangle([460, 220, 500, 520], outline=WHITE, width=3); d.rectangle([463, 300, 497, 517], fill=RED); text(d, (480, 195), '耗电', 22)
    text(d, (220, 260), '越快越糊', 30, fill=GOLD)
beat('y10', bg('B_wide_B', blur=1.5), y10)
def y11(d):
    d.rectangle([460, 220, 500, 520], outline=WHITE, width=3); d.rectangle([463, 420, 497, 517], fill=GOLD); text(d, (480, 195), '耗电', 22)
    text(d, (230, 260), '每个比特少花一点电', 26, fill=GOLD)
beat('y11', bg('B_wide_B'), y11)
def y12(d):
    tag(d, '姿势 E：站起来（待生成）'); text(d, (W // 2, 200), '一个都不能数错', 40, fill=GOLD)
beat('y12', bg('A_f0010'), y12)
def y13(d):
    d.rectangle([0, 0, W, H], fill=(18, 18, 20)); text(d, (W // 2, 260), '一句话带走', 44, fill=GOLD)
    text(d, (W // 2, 360), '发出去：排成一列', 32); text(d, (W // 2, 420), '收进来：听准节拍、拆回一排', 32); route(d, 130, 560)
    text(d, (162, 610), '你在这里', 16, fill=GOLD)
beat('y13', Image.new('RGB', (W, H)), y13)
beat('y14', bg('B_close_B', blur=3), lambda d: text(d, (W // 2, 230), '下一篇：信号为什么越跑越模糊？', 26))
sheet = Image.new('RGB', (W * 7 // 2, H * 2 // 2 * 2 // 2 * 2 // 2))
tw, th = W // 2, H // 2; sheet = Image.new('RGB', (tw * 7, th * 2), (0, 0, 0))
for i, im in enumerate(frames): sheet.paste(im.resize((tw, th), Image.LANCZOS), ((i % 7) * tw, (i // 7) * th))
sheet.save(os.path.join(HERE, '下集_草稿接触表_v1.jpg'), quality=86); print('ok', len(frames))
