# 2D 层：手机屏幕贴图、大字问题、字幕。字留在 2D 层，保证手机上可读；3D 层由 scene.py 出。
# 用法：python3 overlay.py ui <out.png>
#       python3 overlay.py comp <3d.png> <out.png> <shot>
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
NOTO_R = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
SMILEY = '/usr/share/fonts/truetype/smiley-sans/SmileySans-Oblique.ttf'
SC = 2  # Noto CJK 集合里 SC 的序号

def f(path, size, idx=SC):
    return ImageFont.truetype(path, size, index=idx if path.endswith('.ttc') else 0)

INK = (27, 33, 64)
YEL = (255, 201, 60)

def ui(out):
    W, H = 1060, 2260
    im = Image.new('RGB', (W, H), (247, 248, 252)); d = ImageDraw.Draw(im)
    d.text((W / 2, 150), 'AI 助手', font=f(NOTO, 64), fill=(60, 66, 96), anchor='mm')
    d.line((60, 230, W - 60, 230), fill=(225, 228, 238), width=3)
    # 上一轮对话（淡）
    d.rounded_rectangle((W - 60 - 520, 290, W - 60, 400), 50, fill=(205, 222, 255))
    d.text((W - 100, 345), '今天天气怎么样？', font=f(NOTO, 56), fill=(70, 100, 170), anchor='rm')
    d.rounded_rectangle((40, 440, 820, 640), 50, fill=(236, 238, 246))
    d.text((90, 500), '晴，25 度，', font=f(NOTO, 56), fill=(120, 126, 150), anchor='lm')
    d.text((90, 580), '适合出门走走。', font=f(NOTO, 56), fill=(120, 126, 150), anchor='lm')
    OFF = 420
    # 用户气泡（右）
    t = '帮我写一句周末计划'; ft = f(NOTO, 74)
    tw = d.textlength(t, font=ft)
    d.rounded_rectangle((W - 60 - tw - 80, 320 + OFF, W - 60, 470 + OFF), 60, fill=(74, 141, 255))
    d.text((W - 60 - 40, 395 + OFF), t, font=ft, fill='white', anchor='rm')
    # AI 回复（左）：已写出的字 + 空出来的位置（「去」刚浮出屏幕）+ 黄色虚线「?」
    d.rounded_rectangle((40, 560 + OFF, 1020, 840 + OFF), 60, fill='white', outline=(225, 228, 238), width=4)
    ft2 = f(NOTO, 150); x = 80; cy = 700 + OFF; b = 76
    d.text((x, cy), '周末我想', font=ft2, fill=INK, anchor='lm'); x += d.textlength('周末我想', font=ft2) + 16
    d.rounded_rectangle((x, cy - b, x + 2 * b, cy + b), 18, outline=(200, 205, 220), width=6)  # 空位：「去」飞出去了
    x += 2 * b + 22
    L = 2 * b
    for k in range(0, L, 30):  # 黄色虚线框：下一个要写的位置
        e = min(k + 16, L)
        d.line((x + k, cy - b, x + e, cy - b), fill=YEL, width=9); d.line((x + k, cy + b, x + e, cy + b), fill=YEL, width=9)
        d.line((x, cy - b + k, x, cy - b + e), fill=YEL, width=9); d.line((x + L, cy - b + k, x + L, cy - b + e), fill=YEL, width=9)
    # 输入栏
    d.rounded_rectangle((80, H - 220, W - 80, H - 110), 55, fill=(232, 235, 244))
    im.save(out)

def comp(src, out, shot):
    im = Image.open(src).convert('RGB').resize((1080, 1920), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    # 大字问题（顶部两行，得意黑，深墨色；关键词下面垫一条黄色马克笔色块）
    l1, l2 = 'AI 为什么', '一个字一个字往外蹦？'
    size = 132
    while d.textlength(l2, font=f(SMILEY, size)) > 800: size -= 2
    ft = f(SMILEY, size)
    if shot == 1:
        w2 = d.textlength(l2, font=ft)
        x0 = 540 - w2 / 2
        kw = d.textlength('一个字一个字', font=ft)
        d.rounded_rectangle((x0 - 8, 340, x0 + kw + 8, 400), 14, fill=YEL)
        d.text((540, 225), l1, font=ft, fill=INK, anchor='mm')
        d.text((540, 365), l2, font=ft, fill=INK, anchor='mm')
    # 字幕：深色圆角条 + 白字，关键词黄色（沿用系列规格：中心 y 1480，60 px，≤ 13 字 / 行）
    caps = {1: [[('它不是在打字给你看', 'w')]],
            2: [[('每写一个字，', 'w')], [('都要把模型', 'w'), ('从头到尾', 'y'), ('过一遍', 'w')]],
            3: [[('这里选了「', 'w'), ('海', 'y'), ('」，', 'w')], [('后面是「边看日落」', 'w')]]}[shot]
    fc = f(NOTO, 60); lh = 80
    widths = [sum(d.textlength(s, font=fc) for s, _ in line) for line in caps]
    bw = max(widths) + 80; bh = lh * len(caps) + 40; cy = 1480
    bar = Image.new('RGBA', im.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(bar)
    bd.rounded_rectangle((540 - bw / 2, cy - bh / 2, 540 + bw / 2, cy + bh / 2), 26, fill=(20, 24, 48, 200))
    im.paste(bar, (0, 0), bar); d = ImageDraw.Draw(im)
    for i, line in enumerate(caps):
        x = 540 - widths[i] / 2; y = cy - (len(caps) - 1) * lh / 2 + i * lh
        for s, c in line:
            d.text((x, y), s, font=fc, fill=YEL if c == 'y' else (255, 255, 255), anchor='lm'); x += d.textlength(s, font=fc)
    # 小字注释（示意）
    note = {1: '一个「字」严格说是一个 token', 2: '模型的层数、格子数为示意', 3: '示意：前一个字不同，后面整句都不同'}[shot]
    fn = f(NOTO_R, 32); nw = d.textlength(note, font=fn); ny = cy - bh / 2 - 44
    bar = Image.new('RGBA', im.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(bar)
    bd.rounded_rectangle((540 - nw / 2 - 22, ny - 26, 540 + nw / 2 + 22, ny + 26), 18, fill=(20, 24, 48, 150))
    im.paste(bar, (0, 0), bar); d = ImageDraw.Draw(im)
    d.text((540, ny), note, font=fn, fill=(222, 226, 245), anchor='mm')
    im.save(out)

if __name__ == '__main__':
    if sys.argv[1] == 'ui': ui(sys.argv[2])
    else: comp(sys.argv[2], sys.argv[3], int(sys.argv[4]))
